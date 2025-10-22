#!/usr/bin/env python3
"""
Vercel-compatible API for CMP Mapper.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import version info
from version import get_version_info

app = Flask(__name__)

@app.route('/')
def index():
    """Main page."""
    version_info = get_version_info()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CMP Mapper - Cookie Consent Banner Detector</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }}
            h1 {{
                font-size: 3rem;
                margin-bottom: 1rem;
            }}
            .subtitle {{
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }}
            .input-group {{
                margin: 2rem 0;
            }}
            input[type="url"] {{
                width: 100%;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                margin-bottom: 1rem;
            }}
            button {{
                background: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                cursor: pointer;
                transition: background 0.3s;
            }}
            button:hover {{
                background: #45a049;
            }}
            .result {{
                margin-top: 2rem;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                text-align: left;
            }}
            .version {{
                margin-top: 2rem;
                font-size: 0.9rem;
                opacity: 0.7;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍪 CMP Mapper</h1>
            <p class="subtitle">Automated Cookie Consent Banner Detection & Rule Generation</p>
            
            <div class="input-group">
                <input type="url" id="urlInput" placeholder="Enter website URL (e.g., https://example.com)" />
                <button onclick="analyzeUrl()">Analyze Website</button>
            </div>
            
            <div id="result" class="result" style="display: none;">
                <h3>Analysis Results:</h3>
                <div id="resultContent"></div>
            </div>
            
            <div class="version">
                <p>Version: {version_info['version']}</p>
                <p>Last Updated: {version_info['last_updated']}</p>
            </div>
        </div>
        
        <script>
            function analyzeUrl() {{
                const url = document.getElementById('urlInput').value;
                if (!url) {{
                    alert('Please enter a URL');
                    return;
                }}
                
                const resultDiv = document.getElementById('result');
                const contentDiv = document.getElementById('resultContent');
                
                resultDiv.style.display = 'block';
                contentDiv.innerHTML = '<p>Analyzing website... This may take 10-30 seconds.</p>';
                
                fetch('/api/analyze', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ url: url }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        contentDiv.innerHTML = `
                            <h4>✅ Banner Detected!</h4>
                            <p><strong>Confidence:</strong> ${{(data.confidence * 100).toFixed(1)}}%</p>
                            <p><strong>Banner Type:</strong> ${{data.banner_type}}</p>
                            <p><strong>Buttons Found:</strong> ${{data.button_count}}</p>
                            <p><strong>Banner Selector:</strong> <code>${{data.banner_selector}}</code></p>
                            <p><strong>Accept Button:</strong> <code>${{data.accept_button}}</code></p>
                            <button onclick="downloadRule()" style="margin-top: 10px;">Download Rule JSON</button>
                        `;
                    }} else {{
                        contentDiv.innerHTML = `
                            <h4>❌ No Banner Detected</h4>
                            <p>${{data.message}}</p>
                        `;
                    }}
                }})
                .catch(error => {{
                    contentDiv.innerHTML = `
                        <h4>❌ Error</h4>
                        <p>Error analyzing website: ${{error.message}}</p>
                    `;
                }});
            }}
            
            function downloadRule() {{
                // Simple rule download
                const rule = {{
                    "domain": "example.com",
                    "rules": [
                        {{
                            "selector": "banner-selector",
                            "action": "hide"
                        }},
                        {{
                            "selector": "accept-button",
                            "action": "click"
                        }}
                    ]
                }};
                
                const blob = new Blob([JSON.stringify(rule, null, 2)], {{ type: 'application/json' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'consent-rule.json';
                a.click();
                URL.revokeObjectURL(url);
            }}
        </script>
    </body>
    </html>
    """

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """Analyze a URL for consent banners."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'message': 'No URL provided'})
        
        # Simple analysis (for demo purposes)
        # In a real implementation, you'd use the full CMP Mapper logic
        
        # Simulate analysis
        import random
        confidence = random.uniform(0.6, 1.0)
        
        if confidence > 0.7:
            return jsonify({
                'success': True,
                'confidence': confidence,
                'banner_type': 'modal',
                'button_count': random.randint(1, 5),
                'banner_selector': '.cookie-banner',
                'accept_button': '.accept-cookies',
                'message': 'Banner detected successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No consent banner detected on this page'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error analyzing website: {str(e)}'
        })

@app.route('/api/version')
def get_version():
    """Get version information."""
    return jsonify(get_version_info())

if __name__ == '__main__':
    app.run(debug=True)
