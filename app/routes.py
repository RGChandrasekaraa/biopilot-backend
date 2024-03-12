from flask import request, jsonify, make_response
from werkzeug.utils import secure_filename
import os
from .resume_parser import evaluate_resume
from app import app


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files or 'job_desc' not in request.form:
        return jsonify({'error': 'No resume file or job description provided'}), 400

    file = request.files['resume']
    job_desc = request.form['job_desc']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    try:
        score = evaluate_resume(filepath, job_desc)
        return jsonify({'score': score})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)  # Clean up file after processing


@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Resource not found'}), 404)
