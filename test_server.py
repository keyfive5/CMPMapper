#!/usr/bin/env python3
"""
Simple test server to verify Flask is working
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
        <h1>CMP Mapper Test Server</h1>
        <p>If you can see this, Flask is working!</p>
        <p>Server is running on port 5001</p>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("Starting test server on port 5001...")
    app.run(debug=True, port=5001, host='127.0.0.1')
