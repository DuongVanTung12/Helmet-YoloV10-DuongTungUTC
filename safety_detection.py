import cv2
import torch
from ultralytics import YOLO
import time
import numpy as np
import os

def load_models():
    # Load YOLO models
    best_model = YOLO("best.pt")  # Contains classes: head, helmet, person
    person_model = YOLO("model.pt")  # Specialized for person detection
    return best_model, person_model

# Function to check if a helmet is properly worn on a head
def is_helmet_properly_worn(helmet_box, head_box):
    # Extract coordinates
    head_x1, head_y1, head_x2, head_y2 = head_box
    helmet_x1, helmet_y1, helmet_x2, helmet_y2 = helmet_box
    
    # Calculate overlap
    x_overlap = max(0, min(helmet_x2, head_x2) - max(helmet_x1, head_x1))
    y_overlap = max(0, min(helmet_y2, head_y2) - max(helmet_y1, head_y1))
    
    overlap_area = x_overlap * y_overlap
    head_area = (head_x2 - head_x1) * (head_y2 - head_y1)
    helmet_area = (helmet_x2 - helmet_x1) * (helmet_y2 - helmet_y1)
    
    # If head area is very small, it could be false detection
    if head_area < 100:
        return False
    
    # Calculate overlap ratio with head
    if head_area > 0:
        head_overlap_ratio = overlap_area / head_area
    else:
        head_overlap_ratio = 0
    
    # Calculate overlap ratio with helmet
    if helmet_area > 0:
        helmet_overlap_ratio = overlap_area / helmet_area
    else:
        helmet_overlap_ratio = 0
    
    # Helmet is properly worn if it significantly overlaps with the head
    return head_overlap_ratio > 0.5 or helmet_overlap_ratio > 0.5

# New function to filter out false person detections
def filter_person_detections(person_boxes):
    filtered_boxes = []
    
    for box in person_boxes:
        x1, y1, x2, y2, confidence = box
        
        # Get box dimensions
        width = x2 - x1
        height = y2 - y1
        
        # Calculate aspect ratio (height/width)
        aspect_ratio = height / width if width > 0 else 0
        
        # People typically have aspect ratios between 1.5 and 3.5
        # (height is usually 1.5 to 3.5 times the width)
        is_person_ratio = 1.5 <= aspect_ratio <= 3.5
        
        # People are usually taller than they are wide
        is_tall = height > width
        
        # Higher confidence threshold for unusual aspect ratios
        confidence_threshold = 0.4 if not is_person_ratio else 0.25
        
        # Apply stricter filtering
        if confidence > confidence_threshold and is_tall:
            filtered_boxes.append(box)
    
    return filtered_boxes

# Global variable for the current frame
current_frame = None

# Function to process video with streaming capability
def process_video_stream(input_path, output_path, frame_callback=None, is_camera=False):
    global current_frame

    # Load models
    best_model, person_model = load_models()

    # Add debug prints to track detections
    print("Models loaded successfully")

    # Open the video file or camera
    if is_camera:
        cap = cv2.VideoCapture(input_path if input_path is not None else 0)
    else:
        cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        return False, "Could not open video source"

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) if not is_camera else 30  # Default to 30 FPS for camera

    # Create video writer if not using camera
    if not is_camera:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Initialize variables
    frame_count = 0

    while cap.isOpened():
        # Read frame
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Process with both models
        best_results = best_model(frame)  # Get head, helmet, person from best.pt
        person_results = person_model(frame)  # Get only person detections from model.pt

        # Create a clean copy for drawing
        processed_frame = frame.copy()

        # Extract class indices from best.pt model
        best_classes = best_results[0].names
        head_class_id = -1
        helmet_class_id = -1
        person_class_id = -1

        # Find the class IDs from best.pt
        for class_id, class_name in best_classes.items():
            class_name = class_name.lower()
            if class_name == 'head':
                head_class_id = int(class_id)
            elif class_name == 'helmet':
                helmet_class_id = int(class_id)
            elif class_name == 'person':
                person_class_id = int(class_id)

        # Extract detections from best model (all three classes)
        head_boxes = []
        helmet_boxes = []
        person_boxes_from_best = []

        for box in best_results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            if class_id == head_class_id and confidence > 0.3:
                head_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence))
            elif class_id == helmet_class_id and confidence > 0.2:
                helmet_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence))
            elif class_id == person_class_id and confidence > 0.3:
                person_boxes_from_best.append((int(x1), int(y1), int(x2), int(y2), confidence))

        # Combine person detections from both models
        all_person_boxes = person_boxes_from_best

        # Draw head boxes in yellow
        for box in head_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(processed_frame, "Head", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Draw helmet boxes in green
        for box in helmet_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(processed_frame, "Helmet", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Draw person boxes in blue
        for box in all_person_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(processed_frame, "Person", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Save current frame for streaming
        current_frame = processed_frame.copy()

        # Write to output video if not using camera
        if not is_camera:
            out.write(processed_frame)

        # Break loop if camera and 'q' is pressed
        if is_camera and cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    if not is_camera:
        out.release()

    return True, output_path if not is_camera else "Camera stream processed"

# Function to get the latest processed frame
def get_latest_frame():
    global current_frame
    return current_frame

# For backward compatibility 
def process_video(input_path, output_path):
    return process_video_stream(input_path, output_path)

def main():
    # Load models
    best_model, person_model = load_models()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Calculate FPS
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # FPS calculation
        fps_frame_count += 1
        if time.time() - fps_start_time >= 1:
            fps = fps_frame_count
            fps_frame_count = 0
            fps_start_time = time.time()
        
        # Process with both models
        best_results = best_model(frame)  # Get head, helmet, person from best.pt
        person_results = person_model(frame)  # Get only person detections from model.pt
        
        # Extract class indices from best.pt model
        best_classes = best_results[0].names
        head_class_id = -1
        helmet_class_id = -1
        person_class_id = -1
        
        # Find the class IDs from best.pt
        for class_id, class_name in best_classes.items():
            if class_name.lower() == 'head':
                head_class_id = int(class_id)
            elif class_name.lower() == 'helmet':
                helmet_class_id = int(class_id)
            elif class_name.lower() == 'person':
                person_class_id = int(class_id)
        
        # Extract detections from best model (all three classes)
        head_boxes = []
        helmet_boxes = []
        person_boxes_from_best = []
        
        for box in best_results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            
            if class_id == head_class_id:
                head_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence))
            elif class_id == helmet_class_id:
                helmet_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence))
            elif class_id == person_class_id:
                # Use a higher confidence threshold for person detection from best.pt
                if confidence > 0.3:
                    person_boxes_from_best.append((int(x1), int(y1), int(x2), int(y2), confidence))
        
        # Extract only person detections from person_model with higher threshold
        person_boxes_from_model = []
        for box in person_results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0].item())
            # Use a higher confidence threshold for model.pt
            if confidence > 0.4:  # Stricter threshold for model.pt
                person_boxes_from_model.append((int(x1), int(y1), int(x2), int(y2), confidence))
        
        # Apply aspect ratio and dimensional filtering to remove false person detections
        person_boxes_from_best = filter_person_detections(person_boxes_from_best)
        person_boxes_from_model = filter_person_detections(person_boxes_from_model)
        
        # Combine person detections from both models
        all_person_boxes = person_boxes_from_best + person_boxes_from_model
        
        # Remove duplicate person detections using non-maximum suppression
        if all_person_boxes:
            # Convert to numpy arrays for NMS
            boxes = np.array([box[:4] for box in all_person_boxes])
            scores = np.array([box[4] for box in all_person_boxes])
            
            # Apply NMS
            nms_threshold = 0.45
            indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), 0.25, nms_threshold)
            
            # Keep only the boxes that survived NMS
            filtered_person_boxes = [all_person_boxes[i] for i in indices.flatten()] if len(indices) > 0 else []
            all_person_boxes = filtered_person_boxes
        
        # Draw head boxes in yellow
        for box in head_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, "Head", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Draw helmet boxes in green
        for box in helmet_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Helmet", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw person boxes in blue
        for box in all_person_boxes:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, "Person", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Determine safety status
        safety_status = ""
        color = (0, 0, 0)
        
        if all_person_boxes:
            # Check if there's a head with helmet for any person
            safe_person_found = False
            
            for person_box in all_person_boxes:
                person_x1, person_y1, person_x2, person_y2, _ = person_box
                
                # Check if any head is inside this person
                for head_box in head_boxes:
                    head_x1, head_y1, head_x2, head_y2, _ = head_box
                    
                    # Check if head is inside person
                    if (head_x1 >= person_x1 and head_x2 <= person_x2 and 
                        head_y1 >= person_y1 and head_y2 <= person_y2):
                        
                        # Check if any helmet is properly worn on this head
                        for helmet_box in helmet_boxes:
                            helmet_x1, helmet_y1, helmet_x2, helmet_y2, _ = helmet_box
                            
                            if is_helmet_properly_worn(
                                (helmet_x1, helmet_y1, helmet_x2, helmet_y2),
                                (head_x1, head_y1, head_x2, head_y2)
                            ):
                                safe_person_found = True
                                break
            
            if safe_person_found:
                safety_status = "SAFE"
                color = (0, 255, 0)  # Green
            else:
                safety_status = "DANGEROUS"
                color = (0, 0, 255)  # Red
        elif helmet_boxes:
            safety_status = "NONE"
            color = (255, 165, 0)  # Orange
        
        # Show safety status on frame
        if safety_status:
            text_size = cv2.getTextSize(safety_status, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            cv2.rectangle(frame, 
                         (10, 30 - text_size[1] - 10), 
                         (10 + text_size[0] + 10, 30 + 10), 
                         color, 
                         -1)
            cv2.putText(frame, safety_status, (15, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # Display FPS
        cv2.putText(frame, f"FPS: {fps}", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display the frame
        cv2.imshow('Safety Detection', frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
