
import cv2
import time
import torch
import os
from datetime import datetime
# Đảm bảo bạn có file safety_detection.py với hàm load_models phù hợp
# Hàm load_models() cần trả về (model_cho_head_helmet, model_cho_person)
# Ví dụ: return YOLO('best.pt'), YOLO('model.pt')
from safety_detection import load_models

# --- Cấu hình ---
# Ngưỡng để ổn định trạng thái hiển thị (số khung hình liên tiếp)
STATUS_CONSISTENCY_THRESHOLD = 5
# Thời gian (giây) trạng thái UNSAFE phải duy trì để chụp ảnh
UNSAFE_DURATION_THRESHOLD = 2.0
# Thư mục lưu ảnh chụp khi không an toàn
CAPTURE_FOLDER = "unsafe_captures"

# --- Ngưỡng phát hiện và IoU ---
# Ngưỡng tin cậy tối thiểu để chấp nhận phát hiện người
PERSON_CONFIDENCE_THRESHOLD = 0.4
# Ngưỡng tin cậy tối thiểu để chấp nhận phát hiện đầu (chỉ để vẽ nếu muốn)
HEAD_CONFIDENCE_THRESHOLD = 0.3
# Ngưỡng tin cậy tối thiểu để chấp nhận phát hiện mũ
HELMET_CONFIDENCE_THRESHOLD = 0.2 # Có thể giảm nếu mũ bị mất phát hiện (vd: 0.15)
# Ngưỡng IoU tối thiểu giữa MŨ và NGƯỜI để coi là người đó đang đội mũ
HELMET_PERSON_IOU_THRESHOLD = 0.2 # Đã giảm! Thử nghiệm với 0.15, 0.2, 0.25, 0.3

# --- Kết thúc cấu hình ---

def calculate_iou(box1, box2):
    """
    Tính Intersection over Union (IoU) giữa hai bounding box.
    Mỗi box có dạng (x1, y1, x2, y2).
    """
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)
    if intersection_area == 0:
        return 0.0 # Không giao nhau

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - intersection_area
    if union_area == 0:
        return 0.0 # Tránh chia cho 0

    iou = intersection_area / union_area
    return iou

def webcam_safety_detection(camera_id=0):
    """
    Ứng dụng webcam phát hiện an toàn sử dụng logic chồng chéo Mũ-Người,
    với GPU (nếu có), lọc nhiễu trạng thái và chụp ảnh tự động.
    """
    print("--- Bắt đầu Webcam Safety Detection ---")
    print(f"Ngưỡng IoU Mũ-Người (SAFE): > {HELMET_PERSON_IOU_THRESHOLD}")
    print(f"Ngưỡng tin cậy: Person > {PERSON_CONFIDENCE_THRESHOLD}, Helmet > {HELMET_CONFIDENCE_THRESHOLD}")
    print(f"Trạng thái ổn định sau: {STATUS_CONSISTENCY_THRESHOLD} khung hình")
    print(f"Chụp ảnh UNSAFE sau: {UNSAFE_DURATION_THRESHOLD} giây vào thư mục '{CAPTURE_FOLDER}'")
    print("Nhấn 'q' để thoát.")

    # --- 1. Chọn thiết bị (GPU/CPU) ---
    if torch.cuda.is_available():
        device = 'cuda'
        print(f"Thiết bị: CUDA (GPU) - {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("Thiết bị: CPU")
    # ------------------------------------

    # --- 2. Tải mô hình ---
    try:
        # Hàm load_models cần trả về (model head/helmet, model person)
        best_model, person_model = load_models()
        print("Tải mô hình thành công.")
        # Gợi ý: Có thể thêm best_model.to(device), person_model.to(device) ở đây nếu cần
    except Exception as e:
        print(f"LỖI TẢI MÔ HÌNH: {e}")
        print("Vui lòng kiểm tra file 'safety_detection.py' và các file model (.pt).")
        return
    # --------------------------

    # --- 3. Khởi tạo Webcam ---
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"LỖI: Không thể mở camera ID {camera_id}")
        return
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Độ phân giải Camera: {width}x{height}")
    # ---------------------------

    # --- 4. Tạo cửa sổ & Khởi tạo biến ---
    cv2.namedWindow('Safety Detection Webcam', cv2.WINDOW_NORMAL)
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    # Biến cho lọc nhiễu trạng thái
    displayed_status = None
    last_detected_status = None
    status_consistent_count = 0
    # Biến cho chụp ảnh tự động
    unsafe_start_time = None
    unsafe_capture_taken = False
    os.makedirs(CAPTURE_FOLDER, exist_ok=True) # Tạo thư mục nếu chưa có
    # ---------------------------------------

    # --- 5. Vòng lặp xử lý chính ---
    while True:
        current_time = time.time() # Lấy thời gian hiện tại

        # --- Đọc khung hình ---
        ret, frame = cap.read()
        if not ret:
            print("LỖI: Không thể đọc khung hình từ camera.")
            time.sleep(0.5) # Đợi chút trước khi thử lại hoặc thoát
            continue # Hoặc break nếu muốn dừng hẳn

        # --- Tính FPS ---
        fps_frame_count += 1
        if current_time - fps_start_time >= 1.0:
            fps = fps_frame_count
            fps_frame_count = 0
            fps_start_time = current_time
        # ---------------

        # --- Chạy suy luận trên cả 2 model ---
        try:
            # Model 1: Phát hiện Head và Helmet
            best_results = best_model(frame, device=device, verbose=False, conf=HELMET_CONFIDENCE_THRESHOLD) # Có thể đặt conf ở đây
            # Model 2: Phát hiện Person (từ model.pt)
            person_results = person_model(frame, device=device, verbose=False, conf=PERSON_CONFIDENCE_THRESHOLD) # Có thể đặt conf ở đây
        except Exception as e:
            print(f"LỖI SUY LUẬN: {e}")
            # Hiển thị lỗi trên khung hình
            error_frame = frame.copy()
            cv2.putText(error_frame, "Inference Error", (int(width*0.1), height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(error_frame, "Inference Error", (int(width*0.1), height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow('Safety Detection Webcam', error_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        # --------------------------------------

        # --- Chuẩn bị xử lý kết quả ---
        processed_frame = frame.copy() # Khung hình để vẽ lên
        head_boxes = []     # Chỉ để vẽ (tùy chọn)
        helmet_boxes = []   # Dùng cho logic IoU
        person_boxes = []   # Dùng cho logic IoU
        current_frame_status = None # Trạng thái gốc của khung hình này
        color = (128, 128, 128) # Màu trạng thái mặc định (Xám)
        # -------------------------------

        # --- Trích xuất Head (tùy chọn) và Helmet từ best_results ---
        if best_results and hasattr(best_results[0], 'names') and hasattr(best_results[0], 'boxes'):
            best_classes = best_results[0].names
            head_class_id = next((int(k) for k, v in best_classes.items() if v.lower() == 'head'), -1)
            helmet_class_id = next((int(k) for k, v in best_classes.items() if v.lower() == 'helmet'), -1)

            for box in best_results[0].boxes:
                 # Có thể thêm kiểm tra box.conf[0] > threshold ở đây nếu chưa đặt ở model()
                try:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    class_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    box_coords = (x1, y1, x2, y2)

                    # Bỏ qua nếu không đủ tin cậy (nếu chưa lọc bằng conf= trong model())
                    # if class_id == head_class_id and confidence < HEAD_CONFIDENCE_THRESHOLD: continue
                    # if class_id == helmet_class_id and confidence < HELMET_CONFIDENCE_THRESHOLD: continue

                    if class_id == head_class_id: # Chỉ vẽ nếu muốn
                        head_boxes.append(box_coords)
                        # cv2.rectangle(processed_frame, box_coords, (0, 255, 255), 1)
                        # cv2.putText(processed_frame, f"H {confidence:.1f}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                    elif class_id == helmet_class_id:
                        helmet_boxes.append(box_coords)
                        cv2.rectangle(processed_frame, box_coords, (0, 255, 0), 2) # Xanh lá
                        cv2.putText(processed_frame, f"Helmet {confidence:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                except Exception as e:
                    print(f"Lỗi xử lý hộp head/helmet: {e}")
        # --- Kết thúc trích xuất head/helmet ---

        # --- Trích xuất Person từ person_results ---
        if person_results and hasattr(person_results[0], 'names') and hasattr(person_results[0], 'boxes'):
             person_classes = person_results[0].names
             person_class_id_in_person_model = next((int(k) for k, v in person_classes.items() if v.lower() == 'person'), -1)
             if person_class_id_in_person_model != -1:
                 for box in person_results[0].boxes:
                     # Có thể thêm kiểm tra box.conf[0] > PERSON_CONFIDENCE_THRESHOLD ở đây
                     try:
                         x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                         class_id = int(box.cls[0].item())
                         confidence = float(box.conf[0].item())
                         box_coords = (x1, y1, x2, y2)

                         if class_id == person_class_id_in_person_model:
                              person_boxes.append(box_coords)
                              cv2.rectangle(processed_frame, box_coords, (255, 0, 0), 2) # Xanh dương
                              cv2.putText(processed_frame, f"Person {confidence:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                     except Exception as e:
                          print(f"Lỗi xử lý hộp person: {e}")
        # --- Kết thúc trích xuất person ---


        # --- Xác định trạng thái gốc DỰA TRÊN HELMET-PERSON IoU ---
        num_persons = len(person_boxes)
        if num_persons > 0:
            uncovered_person_found = False # Cờ kiểm tra có người nào không đội mũ không

            for i, person_box in enumerate(person_boxes):
                person_has_helmet = False # Cờ kiểm tra người thứ i này có mũ không
                max_iou_for_person = 0 # Lưu IoU lớn nhất tìm được cho người này (để debug)

                for helmet_box in helmet_boxes:
                    iou = calculate_iou(person_box, helmet_box)
                    max_iou_for_person = max(max_iou_for_person, iou) # Cập nhật IoU lớn nhất

                    if iou >= HELMET_PERSON_IOU_THRESHOLD:
                        person_has_helmet = True
                        # Đánh dấu người này là an toàn (tùy chọn)
                        # cv2.rectangle(processed_frame, person_box, (0, 255, 0), 2) # Đè viền xanh lá
                        break # Đã tìm thấy mũ cho người này, không cần kiểm tra mũ khác

                # === DEBUG PRINT (Bỏ comment nếu cần kiểm tra IoU) ===
                # print(f"  Person {i}: Max IoU = {max_iou_for_person:.3f}, Has Helmet = {person_has_helmet}")
                # ====================================================

                if not person_has_helmet:
                    uncovered_person_found = True
                    # Đánh dấu người không an toàn (viền đỏ dày)
                    cv2.rectangle(processed_frame, person_box, (0, 0, 255), 3)
                    # break # Bỏ comment nếu muốn xác định UNSAFE ngay khi tìm thấy 1 người vi phạm

            # Xác định trạng thái cuối cùng cho khung hình
            if uncovered_person_found:
                current_frame_status = "UNSAFE"
            else: # Không tìm thấy người nào không đội mũ => An toàn
                current_frame_status = "SAFE"

        else: # Không có người nào được phát hiện
            current_frame_status = None # Sẽ hiển thị là NO DETECTION
        # --- Kết thúc xác định trạng thái gốc ---


        # --- Lọc nhiễu (Debouncing) Trạng thái ---
        if current_frame_status == last_detected_status:
            status_consistent_count += 1
        else:
            last_detected_status = current_frame_status
            status_consistent_count = 1 # Reset bộ đếm

        if status_consistent_count >= STATUS_CONSISTENCY_THRESHOLD or status_consistent_count == 1 : # Cập nhật ngay lần đầu hoặc khi đủ ổn định
             if status_consistent_count == 1 and displayed_status is not None and current_frame_status is None:
                  pass # Tránh chuyển từ trạng thái có nghĩa sang NO DETECTION ngay lập tức
             elif status_consistent_count >= STATUS_CONSISTENCY_THRESHOLD or displayed_status is None:
                  displayed_status = last_detected_status

        # === DEBUG PRINT (Bỏ comment nếu cần kiểm tra debouncing) ===
        # print(f"Status: current={current_frame_status}, last={last_detected_status}, count={status_consistent_count}, displayed={displayed_status}")
        # =========================================================
        # ---------------------------------------------

        # --- Chụp ảnh nếu trạng thái UNSAFE kéo dài ---
        if displayed_status == "UNSAFE":
            if unsafe_start_time is None: # Bắt đầu đếm giờ UNSAFE
                unsafe_start_time = current_time
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Trạng thái UNSAFE bắt đầu.")
            # Kiểm tra thời gian và cờ đã chụp
            elif current_time - unsafe_start_time >= UNSAFE_DURATION_THRESHOLD and not unsafe_capture_taken:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # Thêm mili giây
                filename = os.path.join(CAPTURE_FOLDER, f"unsafe_{timestamp}.jpg")
                try:
                    cv2.imwrite(filename, frame) # Lưu khung hình gốc (không có vẽ vời)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ảnh UNSAFE đã lưu: {filename}")
                    unsafe_capture_taken = True # Đánh dấu đã chụp cho đợt này
                except Exception as e:
                    print(f"LỖI khi lưu ảnh: {e}")
        else: # Nếu trạng thái không còn là UNSAFE
            if unsafe_start_time is not None: # Reset nếu trước đó là UNSAFE
                 print(f"[{datetime.now().strftime('%H:%M:%S')}] Trạng thái UNSAFE kết thúc.")
                 unsafe_start_time = None
                 unsafe_capture_taken = False # Cho phép chụp lại nếu UNSAFE lần nữa
        # ---------------------------------------------

        # --- Hiển thị trạng thái lên màn hình ---
        status_text = displayed_status if displayed_status else "NO DETECTION"
        if displayed_status == "UNSAFE": color = (0, 0, 255)       # Đỏ
        elif displayed_status == "SAFE": color = (0, 255, 0)       # Xanh lá
        else: color = (128, 128, 128)                              # Xám (NO DETECTION)

        # Vẽ background cho chữ trạng thái
        (text_w, text_h), baseline = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
        cv2.rectangle(processed_frame, (10, 10), (10 + text_w + 10, 10 + text_h + 10), color, -1)
        # Vẽ chữ trạng thái
        cv2.putText(processed_frame, status_text, (15, 10 + text_h + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
        # ------------------------------------------

        # --- Hiển thị FPS ---
        fps_text = f"FPS: {fps:.1f} ({device.upper()})"
        (fps_w, fps_h), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        fps_color = (0, 255, 0) if device == 'cuda' else (255, 255, 255)
        cv2.putText(processed_frame, fps_text, (10, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 1, cv2.LINE_AA)
        # ------------------

        # --- Hiển thị khung hình cuối cùng ---
        cv2.imshow('Safety Detection Webcam', processed_frame)
        # ----------------------------------

        # --- Thoát nếu nhấn 'q' ---
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Đã nhấn 'q', đang thoát...")
            break
        # --------------------------

    # --- 6. Giải phóng tài nguyên ---
    print("Đang giải phóng tài nguyên...")
    cap.release()
    cv2.destroyAllWindows()
    print("--- Webcam Safety Detection đã dừng ---")
    # -----------------------------

if __name__ == "__main__":
    webcam_safety_detection()
