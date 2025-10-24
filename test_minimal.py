#!/usr/bin/env python3
"""
Minimal Flask app to test if the issue is with the main web_ui.py
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>CMP Mapper - Minimal Test</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f0f0; }
        .container { background: white; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 CMP Mapper - Minimal Test</h1>
        <p>If you can see this page, Flask is working!</p>
        <p>This is a minimal test to check if the main app has issues.</p>
        <button class="btn" onclick="alert('JavaScript is working!')">Test Button</button>
        <p><strong>Status:</strong> ✅ Flask app is running</p>
        <p><strong>Time:</strong> <span id="time"></span></p>
    </div>
    
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
        console.log('Page loaded successfully!');
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("Starting minimal test server...")
    app.run(debug=True, host='127.0.0.1', port=5002)
