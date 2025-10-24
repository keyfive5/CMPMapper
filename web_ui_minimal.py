#!/usr/bin/env python3
"""
Minimal version of web_ui.py to test if the issue is with specific routes or imports
"""

from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>CMP Mapper - Minimal</title>
    <style>
        body { font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; }
        .container { background: white; padding: 30px; border-radius: 15px; max-width: 600px; margin: 50px auto; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; margin: 10px; }
        .btn:hover { background: #5a6fd8; }
        .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍪 CMP Mapper - Minimal Version</h1>
        <div class="status">
            <strong>✅ Status:</strong> Flask app is running successfully!
        </div>
        <p>This is a minimal version to test if the main app has issues.</p>
        <button class="btn" onclick="testFunction()">Test JavaScript</button>
        <button class="btn" onclick="testAPI()">Test API</button>
        <div id="result"></div>
    </div>
    
    <script>
        function testFunction() {
            document.getElementById('result').innerHTML = '<p style="color: green;">✅ JavaScript is working!</p>';
        }
        
        async function testAPI() {
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                document.getElementById('result').innerHTML = '<p style="color: green;">✅ API is working: ' + data.message + '</p>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">❌ API Error: ' + error.message + '</p>';
            }
        }
        
        console.log('Page loaded successfully!');
    </script>
</body>
</html>
    ''')

@app.route('/api/test')
def test_api():
    return jsonify({'message': 'API is working!', 'status': 'success'})

if __name__ == '__main__':
    print("Starting minimal CMP Mapper...")
    app.run(debug=True, host='127.0.0.1', port=5003)
