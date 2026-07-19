from flask import Flask, Response, render_template_string
import cv2
import numpy as np
import time

app = Flask(__name__)

# Variable globale pour stocker la dernière frame
latest_frame = None

@app.route('/')
def index():
    """Page web principale"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Screenshare Live</title>
        <style>
            body { margin: 0; background: #000; }
            img { width: 100%; height: auto; display: block; }
        </style>
    </head>
    <body>
        <img src="/stream" alt="Live Stream">
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/stream')
def stream():
    def generate():
        global latest_frame
        while True:
            if latest_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n\r\n')
            else:
                # Envoie une petite image noire au démarrage pour éviter le blocage
                black = np.zeros((720, 1280, 3), dtype=np.uint8)
                _, black_jpg = cv2.imencode('.jpg', black)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + black_jpg.tobytes() + b'\r\n\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update', methods=['POST'])
def update_frame():
    """Reçoit les frames du client"""
    global latest_frame
    try:
        latest_frame = request.data
        return "OK", 200
    except:
        return "Error", 400

if __name__ == '__main__':
    print("🚀 Serveur Screenshare démarré sur http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
