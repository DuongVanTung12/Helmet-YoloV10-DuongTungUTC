import cv2
import time
from safety_detection import load_models, process_video_stream

def webcam_safety_detection(camera_id=0):
    """
    Standalone webcam application for safety detection
    """
    print("Starting webcam safety detection...")
    print("Press 'q' to exit")

    # Load models directly
    best_model, person_model = load_models()
    print("Models loaded successfully")

    # Initialize webcam
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_id}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create window
    cv2.namedWindow('Safety Detection Webcam', cv2.WINDOW_NORMAL)
    
    # Calculate FPS
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
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
        for box in person_boxes_from_best:
            x1, y1, x2, y2, _ = box
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(processed_frame, "Person", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Determine safety status
        safety_status = None
        if head_boxes and not helmet_boxes:
            safety_status = "UNSAFE"
            color = (0, 0, 255)  # Red
        elif helmet_boxes:
            safety_status = "SAFE"
            color = (0, 255, 0)  # Green
        elif not head_boxes and not helmet_boxes:
            safety_status = "NONE"
            color = (255, 165, 0)  # Orange
        
        # Show safety status on frame
        if safety_status:
            text_size = cv2.getTextSize(safety_status, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            cv2.rectangle(processed_frame, 
                        (10, 30 - text_size[1] - 10), 
                        (10 + text_size[0] + 10, 30 + 10), 
                        color, 
                        -1)
            cv2.putText(processed_frame, safety_status, (15, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # Display FPS
        cv2.putText(processed_frame, f"FPS: {fps}", (10, processed_frame.shape[0] - 10),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display the frame
        cv2.imshow('Safety Detection Webcam', processed_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam_safety_detection()
