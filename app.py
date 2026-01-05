# app.py (using Flask)
from flask import Flask, request, jsonify, send_file
import os
from your_stego_script import (
    encode_image, decode_image,
    encode_audio, decode_audio,
    encode_video, decode_video,
    # You'll need to adapt your existing functions to take file paths/objects
    # and return results/paths to new files
)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'stego_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html') # Serve your HTML

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

@app.route('/script.js')
def serve_js():
    return send_file('script.js')

@app.route('/api/stego-process', methods=['POST'])
def stego_process():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    file_type = request.form.get('type')
    action = request.form.get('action')
    message = request.form.get('message')
    output_name = request.form.get('output_name')

    if file:
        # Save the uploaded file temporarily
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            if action == 'encode':
                output_path = os.path.join(OUTPUT_FOLDER, output_name)
                # Call your encode function here. You'll need to modify it
                # to accept input/output paths and the message directly.
                # Example: encode_image(filepath, message, output_path)
                # For now, let's just simulate:
                return jsonify({'status': 'success', 'message': 'Encoding simulated.', 'download_url': f'/download/{output_name}'})
            elif action == 'decode':
                # Call your decode function here. You'll need to modify it
                # to accept input path and return the decoded message.
                # Example: decoded_message = decode_image(filepath)
                # For now, let's just simulate:
                decoded_message = "This is a simulated decoded message."
                return jsonify({'status': 'success', 'message': 'Decoding simulated.', 'decoded_text': decoded_message})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid action'}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            os.remove(filepath) # Clean up the uploaded file

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)