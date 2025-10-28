#!/usr/bin/env python3
"""
Simple Flask test to check if the issue is with the HTML file
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>CMP Mapper Test</title>
</head>
<body>
    <h1>CMP Mapper Test Page</h1>
    <p>If you can see this, the Flask app is working!</p>
    <p>Time: {{ time }}</p>
</body>
</html>
    ''', time="Test successful")

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(debug=True, host='127.0.0.1', port=5001)
