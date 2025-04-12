from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, Response
from werkzeug.utils import secure_filename
import os
import uuid
import threading
from safety_detection import process_video_stream, get_latest_frame
import time
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safety_detection_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'wmv', 'flv'}
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max upload size

# Global variables
processing_filename = None
output_filename = None
processing_thread = None

# Create the upload and processed folders if they don't exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

def process_video_thread(input_path, output_path, is_camera=False, camera_id=0):
    global processing_filename, output_filename

    if is_camera:
        # Fix: Pass the camera_id integer instead of the VideoCapture object
        success, result = process_video_stream(camera_id, output_path, is_camera=True)
    else:
        success, result = process_video_stream(input_path, output_path)

    if not success:
        print(f"Error processing video: {result}")

    processing_filename = None
    output_filename = result if success else None

# Add support for selecting input from camera or video file
@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_filename, output_filename, processing_thread

    input_type = request.form.get('input_type')

    if input_type == 'camera':
        # Handle camera input
        camera_id = int(request.form.get('camera_id', 0))  # Default to camera 0
        unique_id = str(uuid.uuid4())
        output_filename = f"camera_{unique_id}.mp4"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

        processing_filename = f"camera_{unique_id}"

        # Start processing in a separate thread
        processing_thread = threading.Thread(target=process_video_thread, args=(None, output_path), kwargs={'is_camera': True, 'camera_id': camera_id})
        processing_thread.daemon = True
        processing_thread.start()

        return redirect(url_for('processing_page', filename=processing_filename))

    elif 'video' in request.files:
        # Handle video file upload
        file = request.files['video']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            unique_filename = f"{unique_id}_{filename}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            file.save(input_path)

            output_filename = f"processed_{unique_filename}"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

            processing_filename = unique_filename

            processing_thread = threading.Thread(target=process_video_thread, args=(input_path, output_path))
            processing_thread.daemon = True
            processing_thread.start()

            return redirect(url_for('processing_page', filename=unique_filename))

    flash('Invalid input type or file type. Please select a valid input.')
    return redirect(url_for('index'))

@app.route('/processing/<filename>')
def processing_page(filename):
    return render_template('processing.html', filename=filename)

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generator function for video streaming."""
    while processing_filename is not None:
        frame = get_latest_frame()
        if frame is not None:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            # Convert to bytes and yield
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Small sleep to not overload the CPU
        time.sleep(0.03)
    
    # If processing is done but there's an output file, redirect to download page
    if output_filename is not None:
        message = 'Processing complete, redirecting to download...'.encode()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + message + b'\r\n')

@app.route('/check_processing_status')
def check_processing_status():
    """Check if processing is complete."""
    if processing_filename is None and output_filename is not None:
        return {"status": "complete", "redirect": url_for('download_page', filename=output_filename)}
    elif processing_filename is not None:
        return {"status": "processing"}
    else:
        return {"status": "error"}

@app.route('/download/<filename>')
def download_page(filename):
    return render_template('download.html', filename=filename)

@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
