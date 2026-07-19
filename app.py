from flask import Flask, Response, render_template_string, request
import cv2
import numpy as np
from threading import Lock

app = Flask(__name__)

latest_frame = None
lock = Lock()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Partage Écran</title>
    <style>
        body { background: #000; margin:0; padding:0; overflow:hidden; }
        img { width: 100vw; height: 100vh; object-fit: contain; display:block; }
    </style>
</head>
<body>
    <img src="/video_feed" />
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/stream', methods=['POST'])
def receive_stream():
    global latest_frame
    try:
        data = request.get_data()
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            with lock:
                latest_frame = frame.copy()
    except:
        pass
    return "OK", 200

def gen_frames():
    global latest_frame
    while True:
        with lock:
            frame = latest_frame.copy() if latest_frame is not None else np.zeros((720, 1280, 3), dtype=np.uint8)
        
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        time.sleep(0.025)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
