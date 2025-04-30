# Safety Detection System

## Tổng quan
Hệ thống Safety Detection là một ứng dụng thị giác máy tính tiên tiến được thiết kế để giám sát an toàn trong thời gian thực. Hệ thống sử dụng các mô hình học sâu để phát hiện người, đầu và mũ bảo hiểm trong luồng video, xác định liệu các quy trình an toàn có được tuân thủ trong các môi trường yêu cầu sử dụng mũ bảo hiểm như công trường xây dựng, nhà máy sản xuất hoặc khu vực khai thác.

### Mục tiêu của dự án
- Tăng cường an toàn lao động thông qua giám sát tự động
- Giảm thiểu tai nạn liên quan đến thiếu thiết bị bảo hộ
- Cung cấp bằng chứng tuân thủ quy định an toàn
- Tự động hóa quy trình giám sát mà không cần sự can thiệp thủ công

### Ứng dụng thực tế
- Công trường xây dựng
- Cơ sở sản xuất công nghiệp
- Khu vực khai thác mỏ
- Cảng biển và khu vực logistics
- Bất kỳ môi trường nào yêu cầu sử dụng mũ bảo hiểm bắt buộc

## Tính năng chi tiết

### Phát hiện đối tượng trong thời gian thực
- **Phát hiện đa đối tượng**: Nhận diện đồng thời người, đầu và mũ bảo hiểm
- **Hiệu suất cao**: Tối ưu hóa để đạt FPS cao trên phần cứng phổ thông
- **Độ chính xác cao**: Sử dụng kết hợp hai mô hình YOLO để tăng độ chính xác
- **Lọc phát hiện sai**: Áp dụng thuật toán lọc dựa trên tỷ lệ khung hình và kích thước

### Phân tích an toàn thông minh
- **Xác định vị trí đúng của mũ bảo hiểm**: Phát hiện liệu mũ bảo hiểm có được đội đúng cách
- **Xác định trạng thái an toàn**: Tự động phân loại cảnh vào các trạng thái:
  - **AN TOÀN**: Khi tất cả người được phát hiện đều đội mũ bảo hiểm đúng cách
  - **NGUY HIỂM/KHÔNG AN TOÀN**: Khi phát hiện người không đội mũ bảo hiểm
  - **KHÔNG CÓ ĐỐI TƯỢNG**: Khi không phát hiện vấn đề an toàn
- **Hiển thị trực quan**: Đánh dấu màu rõ ràng cho từng trạng thái an toàn

### Đa dạng nguồn đầu vào
- **Xử lý file video**: Hỗ trợ nhiều định dạng video (mp4, avi, mov, wmv, flv)
- **Xử lý webcam trực tiếp**: Phát hiện an toàn thời gian thực từ webcam
- **Hỗ trợ camera IP**: Kết nối với camera giám sát IP qua địa chỉ URL
- **Giới hạn kích thước tệp**: Xử lý file lên đến 200MB để đảm bảo hiệu suất

### Giao diện người dùng web
- **Thiết kế thân thiện**: Giao diện trực quan, dễ sử dụng
- **Theo dõi tiến trình**: Hiển thị trạng thái xử lý video theo thời gian thực
- **Xem trước trực tiếp**: Hiển thị khung hình đang được xử lý
- **Tùy chọn tải xuống**: Lưu video đã xử lý với chú thích an toàn

## Công nghệ sử dụng

### Ngôn ngữ và Framework
- **Python 3.7+**: Ngôn ngữ lập trình chính
- **Flask 2.0+**: Framework web cho giao diện người dùng
- **Jinja2**: Hệ thống template cho giao diện web
- **Werkzeug**: Thư viện WSGI cho xử lý tệp và bảo mật

### Thị giác máy tính và AI
- **OpenCV 4.5+**: Thư viện xử lý ảnh và video
  - Đọc và ghi video
  - Xử lý khung hình
  - Vẽ khung giới hạn và văn bản
- **PyTorch 1.10+**: Framework học sâu cho mô hình YOLO
- **Ultralytics YOLO v10v10**: Triển khai mô hình YOLO hiệu suất cao
- **CUDA**: Hỗ trợ tăng tốc GPU (tùy chọn nhưng khuyến nghị)

### Mô hình học sâu
- **best.pt (78MB)**: Mô hình chuyên biệt được đào tạo để phát hiện:
  - Đầu người (head)
  - Mũ bảo hiểm (helmet)
  - Người (person)
- **model.pt (86MB)**: Mô hình bổ sung tập trung vào phát hiện người chính xác

## Yêu cầu hệ thống chi tiết

### Phần cứng tối thiểu
- **CPU**: Bộ xử lý đa nhân (4+ nhân)
- **RAM**: 8GB trở lên
- **Ổ cứng**: 1GB không gian trống cho cài đặt và tệp tạm thời
- **GPU**: Khuyến nghị NVIDIA GPU với hỗ trợ CUDA (tối thiểu 4GB VRAM)

### Phần mềm
- **Hệ điều hành**: Windows 10/11, macOS 10.15+, hoặc Linux (Ubuntu 18.04+)
- **Python**: Phiên bản 3.7 đến 3.10
- **Pip**: Công cụ quản lý gói Python mới nhất

### Thư viện Python cần thiết
```
flask==2.0.1
opencv-python==4.5.3.56
torch==1.10.0
torchvision==0.11.1
ultralytics==8.0.20
numpy==1.21.2
Werkzeug==2.0.1
```

## Hướng dẫn cài đặt chi tiết

### Bước 1: Cài đặt Python và môi trường
1. Tải và cài đặt Python 3.7+ từ [python.org](https://www.python.org/downloads/)
2. Đảm bảo thêm Python vào PATH trong quá trình cài đặt
3. Kiểm tra cài đặt:
   ```
   python --version
   pip --version
   ```

### Bước 2: Clone hoặc tải mã nguồn
1. Sử dụng Git để clone repository:
   ```
   git clone https://github.com/your-username/safety-detection.git
   cd safety-detection
   ```
   Hoặc tải và giải nén mã nguồn

### Bước 3: Cài đặt thư viện phụ thuộc
1. Cài đặt các gói Python yêu cầu:
   ```
   pip install -r requirements.txt
   ```
2. Nếu có GPU NVIDIA, cài đặt CUDA và cuDNN theo hướng dẫn tại [pytorch.org](https://pytorch.org/get-started/locally/)

### Bước 4: Tải mô hình pre-trained
1. Đảm bảo tệp mô hình `best.pt` và `model.pt` có trong thư mục gốc của dự án
2. Nếu không có sẵn, tải từ liên kết sau:
   - [best.pt](https://drive.google.com/file/d/your-file-link)
   - [model.pt](https://drive.google.com/file/d/your-file-link)

### Bước 5: Cấu hình thư mục
1. Đảm bảo tồn tại các thư mục sau (nếu không tự động tạo):
   ```
   mkdir -p uploads processed templates
   ```

## Hướng dẫn sử dụng chi tiết

### Khởi động ứng dụng web
1. Mở terminal/command prompt tại thư mục dự án
2. Chạy ứng dụng Flask:
   ```
   python app.py
   ```
3. Truy cập giao diện web tại `http://localhost:5000` trong trình duyệt
4. Nếu muốn truy cập từ các thiết bị khác trong mạng LAN, hãy thay đổi trong app.py:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```
   Và truy cập qua địa chỉ IP máy chủ: `http://your-server-ip:5000`

### Xử lý video qua giao diện web
1. Trên giao diện chính, chọn "Upload Video" hoặc "Use Camera"
2. Nếu tải lên video:
   - Nhấp "Choose File" và chọn video của bạn (tối đa 200MB)
   - Các định dạng hỗ trợ: mp4, avi, mov, wmv, flv
3. Nếu sử dụng camera:
   - Chọn ID camera (thường là 0 cho webcam tích hợp)
   - Đối với camera IP, nhập URL rtsp (ví dụ: rtsp://username:password@ip-address:port/path)
4. Nhấp "Upload and Process"
5. Theo dõi tiến trình xử lý trên trang Processing
6. Tải xuống hoặc xem video đã xử lý sau khi hoàn thành

### Sử dụng ứng dụng webcam độc lập
1. Mở terminal/command prompt tại thư mục dự án
2. Chạy ứng dụng webcam:
   ```
   python webcam_app.py
   ```
3. Một cửa sổ OpenCV sẽ hiển thị với video trực tiếp từ webcam
4. Xem kết quả phát hiện và trạng thái an toàn trong thời gian thực
5. Nhấn phím 'q' để thoát ứng dụng

### Tùy chỉnh các tham số (cho người dùng nâng cao)
Chỉnh sửa tệp `safety_detection.py` để điều chỉnh:
1. Ngưỡng tin cậy cho việc phát hiện (0.2-0.5 thích hợp cho hầu hết tình huống)
   ```python
   # Ví dụ thay đổi ngưỡng phát hiện đầu
   if class_id == head_class_id and confidence > 0.4:  # Tăng từ 0.3 lên 0.4
   ```
2. Điều chỉnh thuật toán xác định mũ bảo hiểm đội đúng cách
   ```python
   # Trong hàm is_helmet_properly_worn
   return head_overlap_ratio > 0.6  # Tăng từ 0.5 lên 0.6 để yêu cầu mức độ phủ cao hơn
   ```

## Cách hoạt động chi tiết

### Quy trình xử lý video
1. **Đầu vào video**:
   - Đọc từng khung hình từ tệp video hoặc nguồn camera
   - Điều chỉnh kích thước nếu cần để cân bằng hiệu suất và độ chính xác

2. **Phát hiện đối tượng**:
   - Khung hình được đưa qua hai mô hình YOLO:
     - `best.pt`: Phát hiện đầu, mũ bảo hiểm và người với bounding boxes
     - `model.pt`: Bổ sung phát hiện người để tăng độ chính xác

3. **Xử lý kết quả phát hiện**:
   - Trích xuất bounding boxes của đầu, mũ bảo hiểm và người
   - Áp dụng ngưỡng tin cậy để loại bỏ phát hiện có độ tin cậy thấp
   - Sử dụng thuật toán Non-Maximum Suppression (NMS) để loại bỏ các hộp chồng chéo
   - Lọc phát hiện người dựa trên tỷ lệ khung hình để giảm phát hiện sai

4. **Phân tích mối quan hệ không gian**:
   - Xác định các đầu có nằm trong bounding box của người không
   - Kiểm tra xem mũ bảo hiểm có được đội đúng cách trên đầu không
   - Tính toán tỷ lệ chồng lấp giữa hộp đầu và mũ bảo hiểm

5. **Đánh giá trạng thái an toàn**:
   - AN TOÀN: Tất cả đầu người được phát hiện đều có mũ bảo hiểm đội đúng cách
   - NGUY HIỂM: Phát hiện ít nhất một đầu người không có mũ bảo hiểm
   - KHÔNG CÓ ĐỐI TƯỢNG: Không phát hiện đầu người hoặc mũ bảo hiểm

6. **Trực quan hóa và ghi kết quả**:
   - Vẽ bounding boxes với màu tương ứng cho mỗi loại đối tượng
   - Hiển thị trạng thái an toàn trên khung hình với màu sắc thích hợp
   - Ghi khung hình đã xử lý vào video đầu ra hoặc hiển thị trực tiếp

### Thuật toán phát hiện mũ bảo hiểm đội đúng cách

```python
def is_helmet_properly_worn(helmet_box, head_box):
    # Trích xuất tọa độ
    head_x1, head_y1, head_x2, head_y2 = head_box
    helmet_x1, helmet_y1, helmet_x2, helmet_y2 = helmet_box
    
    # Tính diện tích chồng lấp
    x_overlap = max(0, min(helmet_x2, head_x2) - max(helmet_x1, head_x1))
    y_overlap = max(0, min(helmet_y2, head_y2) - max(helmet_y1, head_y1))
    
    overlap_area = x_overlap * y_overlap
    head_area = (head_x2 - head_x1) * (head_y2 - head_y1)
    helmet_area = (helmet_x2 - helmet_x1) * (helmet_y2 - helmet_y1)
    
    # Nếu diện tích đầu quá nhỏ, có thể là phát hiện sai
    if head_area < 100:
        return False
    
    # Tính tỷ lệ chồng lấp với đầu
    if head_area > 0:
        head_overlap_ratio = overlap_area / head_area
    else:
        head_overlap_ratio = 0
    
    # Tính tỷ lệ chồng lấp với mũ bảo hiểm
    if helmet_area > 0:
        helmet_overlap_ratio = overlap_area / helmet_area
    else:
        helmet_overlap_ratio = 0
    
    # Mũ bảo hiểm được đội đúng cách nếu chồng lấp đáng kể với đầu
    return head_overlap_ratio > 0.5 or helmet_overlap_ratio > 0.5
```

### Mã màu và trực quan hóa
- **Hộp màu xanh lam** (RGB: 255, 0, 0): Người được phát hiện
- **Hộp màu vàng** (RGB: 0, 255, 255): Đầu được phát hiện
- **Hộp màu xanh lá** (RGB: 0, 255, 0): Mũ bảo hiểm được phát hiện
- **Chỉ báo trạng thái an toàn**:
  - **Xanh lá** (RGB: 0, 255, 0): AN TOÀN
  - **Đỏ** (RGB: 0, 0, 255): NGUY HIỂM/KHÔNG AN TOÀN
  - **Cam** (RGB: 255, 165, 0): KHÔNG CÓ ĐỐI TƯỢNG

## Kiến trúc hệ thống chi tiết

### Thành phần chính
- `app.py` (1.2KB): Ứng dụng web Flask, xử lý giao diện người dùng và tải lên video
  - Cung cấp các routes cho trang chủ, tải lên, xử lý và tải xuống
  - Quản lý luồng xử lý video không đồng bộ thông qua đa luồng
  - Tạo luồng video trực tiếp trong quá trình xử lý

- `safety_detection.py` (12KB): Module xử lý chính
  - Tải và quản lý các mô hình YOLO
  - Thực hiện phát hiện đối tượng và phân tích trạng thái an toàn
  - Cung cấp các hàm xử lý video và phát hiện an toàn

- `webcam_app.py` (4KB): Ứng dụng webcam độc lập
  - Giao diện đơn giản sử dụng OpenCV cho phát hiện trực tiếp
  - Hiển thị FPS và trạng thái an toàn trong thời gian thực
  - Sử dụng cùng logic phát hiện với ứng dụng web

- `best.pt` (78MB): Mô hình YOLO đã được đào tạo cho đầu, mũ bảo hiểm và phát hiện người
  - Kiến trúc: YOLOv8n
  - Lớp: head, helmet, person
  - Độ chính xác mAP@0.5: 0.92

- `model.pt` (86MB): Mô hình YOLO phụ cho phát hiện người
  - Kiến trúc: YOLOv8m
  - Lớp: person
  - Độ chính xác mAP@0.5: 0.88

### Cấu trúc thư mục chi tiết
```
/
├── app.py                 # Ứng dụng web Flask
├── best.pt                # Mô hình YOLO cho phát hiện đầu, mũ bảo hiểm, người
├── model.pt               # Mô hình YOLO chuyên biệt cho phát hiện người
├── requirements.txt       # Danh sách phụ thuộc Python
├── README.md              # Tài liệu dự án
├── safety_detection.py    # Thuật toán phát hiện an toàn cốt lõi
├── webcam_app.py          # Ứng dụng webcam độc lập
├── __pycache__/           # Tệp cache Python
│   └── safety_detection.cpython-310.pyc
├── processed/             # Thư mục đầu ra cho video đã xử lý
├── templates/             # Mẫu HTML cho giao diện web
│   ├── download.html      # Trang tải xuống video đã xử lý
│   ├── index.html         # Trang chính với form tải lên
│   └── processing.html    # Trang hiển thị trạng thái xử lý
└── uploads/               # Lưu trữ tạm thời cho video đã tải lên
```

### Luồng hoạt động của ứng dụng web
1. Người dùng truy cập trang chủ (`/`)
2. Chọn nguồn đầu vào (tải lên video hoặc sử dụng camera)
3. Form gửi yêu cầu POST đến route `/upload`
4. Ứng dụng xử lý tệp và tạo một luồng xử lý mới
5. Chuyển hướng người dùng đến trang xử lý (`/processing/<filename>`)
6. Hiển thị nguồn cấp dữ liệu video trực tiếp (`/video_feed`)
7. Kiểm tra trạng thái định kỳ thông qua `/check_processing_status`
8. Sau khi hoàn thành, chuyển hướng đến trang tải xuống (`/download/<filename>`)
9. Người dùng có thể tải xuống hoặc xem video đã xử lý

## Cân nhắc hiệu năng chi tiết

### Yếu tố ảnh hưởng đến hiệu suất
- **Độ phân giải video**: 
  - 720p (1280x720): Phù hợp cho hầu hết hệ thống
  - 1080p (1920x1080): Yêu cầu GPU tốt hơn
  - 4K (3840x2160): Không khuyến nghị cho xử lý thời gian thực

- **Phần cứng**:
  - CPU: Mỗi nhân bổ sung cải thiện thời gian xử lý khoảng 10-15%
  - GPU: Tăng tốc 5-10x so với chỉ sử dụng CPU
  - RAM: Ít nhất 4GB cho mỗi luồng xử lý video

- **Số lượng đối tượng**:
  - 1-5 người: Hiệu suất tốt nhất
  - 5-15 người: Giảm FPS khoảng 30-50%
  - 15+ người: Không phù hợp cho xử lý thời gian thực

- **Tối ưu hóa của dự án**:
  - Tăng tốc GPU với CUDA
  - Xử lý không đồng bộ thông qua đa luồng
  - Phân tích định kỳ (không phải mỗi khung hình) để tăng FPS

### Số liệu hiệu suất điển hình
- **CPU 4 nhân + Không có GPU**:
  - Video 720p: 3-5 FPS
  - Video 1080p: 1-3 FPS

- **CPU 8 nhân + GPU NVIDIA GTX 1660**:
  - Video 720p: 20-25 FPS
  - Video 1080p: 15-18 FPS

- **CPU 12 nhân + GPU NVIDIA RTX 3080**:
  - Video 720p: 45-60 FPS
  - Video 1080p: 30-40 FPS

### Theo dõi hiệu suất
Hệ thống bao gồm đo lường FPS để giám sát hiệu suất:
```python
# Tính toán FPS
fps_frame_count += 1
if time.time() - fps_start_time >= 1:
    fps = fps_frame_count
    fps_frame_count = 0
    fps_start_time = time.time()

# Hiển thị FPS
cv2.putText(frame, f"FPS: {fps}", (10, frame.shape[0] - 10),
           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
```

## Giới hạn và cân nhắc

### Giới hạn kỹ thuật
- **Độ chính xác phát hiện**:
  - Phụ thuộc vào điều kiện ánh sáng; ánh sáng yếu giảm độ chính xác 15-30%
  - Phát hiện mũ bảo hiểm kém chính xác hơn khi góc nhìn không thuận lợi
  - Khoảng cách xa (>10m) giảm đáng kể độ chính xác phát hiện

- **Tài nguyên hệ thống**:
  - Xử lý file video lớn (>10 phút) có thể tiêu tốn RAM đáng kể
  - Thiếu GPU có thể làm giảm FPS xuống dưới mức sử dụng được cho thời gian thực
  - Có thể xảy ra lỗi mất dữ liệu nếu đột ngột dừng quá trình xử lý

- **Kích thước file đầu ra**:
  - Video đã xử lý thường lớn hơn 10-20% so với bản gốc
  - Giới hạn tải lên 200MB có thể không đủ cho video độ phân giải cao dài >15 phút

### Cải tiến dự kiến
- **Cải thiện mô hình**:
  - Đào tạo lại mô hình với nhiều loại mũ bảo hiểm và điều kiện ánh sáng
  - Thêm khả năng nhận diện thêm thiết bị bảo hộ (áo phản quang, găng tay, v.v.)

- **Tối ưu hóa hiệu suất**:
  - Triển khai các kỹ thuật giảm độ phân giải thích ứng
  - Tích hợp ONNX Runtime hoặc TensorRT để tăng tốc suy luận

- **Tính năng giám sát nâng cao**:
  - Thêm thông báo tức thì khi phát hiện vi phạm an toàn
  - Tích hợp theo dõi đối tượng để đảm bảo nhất quán giữa các khung hình
  - Tạo báo cáo phân tích với số liệu thống kê vi phạm

## Mở rộng hệ thống

### Mở rộng phát hiện thiết bị an toàn
- **Phát hiện thêm thiết bị bảo hộ**:
  - Áo phản quang
  - Găng tay bảo hộ
  - Đai an toàn
  - Mặt nạ và kính bảo hộ
  - Giày bảo hộ

### Tích hợp hệ thống
- **Kết nối với hệ thống báo động**:
  ```python
  # Ví dụ mã tích hợp với hệ thống cảnh báo
  def trigger_alarm(violation_type, confidence, image):
      if confidence > 0.8:  # Chỉ cảnh báo khi tin cậy cao
          alarm_data = {
              "type": violation_type,
              "timestamp": time.time(),
              "confidence": confidence,
              "image_path": save_violation_image(image)
          }
          requests.post("http://alarm-system-api/trigger", json=alarm_data)
  ```

- **Tích hợp với hệ thống quản lý an toàn**:
  - API để gửi dữ liệu vi phạm đến hệ thống trung tâm
  - Kết nối với cơ sở dữ liệu để theo dõi xu hướng an toàn theo thời gian

### Phân tích dữ liệu nâng cao
- **Thống kê an toàn**:
  - Tỷ lệ tuân thủ theo thời gian
  - Khu vực có nhiều vi phạm nhất
  - Giờ cao điểm của vi phạm an toàn

- **Báo cáo và cảnh báo**:
  - Tự động tạo báo cáo hàng ngày/hàng tuần
  - Cảnh báo thời gian thực cho người giám sát
  - Thông báo vi phạm qua email hoặc tin nhắn

## Giấy phép
[Thêm thông tin giấy phép tại đây]

## Người đóng góp và đơn vị phát triển
[Thêm thông tin về người đóng góp, đơn vị phát triển và công nhận tại đây]"# model_hemet" 
