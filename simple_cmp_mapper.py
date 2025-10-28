#!/usr/bin/env python3
"""
Simple working CMP Mapper server
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CMP Mapper - Working Version</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #333; text-align: center; }
            input, button { padding: 10px; margin: 10px 0; width: 100%; }
            button { background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍪 CMP Mapper - Working Version</h1>
            <p>Server is running on port 5001</p>
            
            <input type="text" id="url" placeholder="Enter website URL" />
            <button onclick="test()">Analyze for Consent Banner</button>
            
            <div id="result" class="result" style="display:none;"></div>
        </div>
        
        <script>
            async function test() {
                const url = document.getElementById('url').value;
                const result = document.getElementById('result');
                
                result.innerHTML = 'Testing...';
                result.style.display = 'block';
                
                try {
                    const response = await fetch('/api/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.banner_detected) {
                            result.innerHTML = `
                                <h3>✅ Consent Banner Detected!</h3>
                                <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                                <p><strong>Banner Type:</strong> ${data.banner_type}</p>
                                <p><strong>Buttons Found:</strong> ${data.buttons_count}</p>
                                <p><strong>Container:</strong> ${data.container_selector}</p>
                                <p><strong>Rule Generated:</strong> ${data.rule_generated ? 'Yes' : 'No'}</p>
                                <p><strong>URL:</strong> ${data.url}</p>
                            `;
                        } else {
                            result.innerHTML = `
                                <h3>❌ No Consent Banner Detected</h3>
                                <p>${data.message}</p>
                                <p><strong>URL:</strong> ${data.url}</p>
                            `;
                        }
                    } else {
                        result.innerHTML = `
                            <h3>❌ Analysis Failed</h3>
                            <p>${data.error}</p>
                            <p><strong>URL:</strong> ${data.url}</p>
                        `;
                    }
                } catch (error) {
                    result.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/test', methods=['POST'])
def test():
    data = request.get_json()
    url = data.get('url', '')
    
    try:
        # Import the detection modules
        from src.collectors.web_scraper import WebScraper
        from src.detectors.banner_detector import BannerDetector
        from src.generators.rule_generator import RuleGenerator
        
        # Collect page data
        with WebScraper(headless=True, timeout=30) as scraper:
            page_data = scraper.collect_page(url)
        
        if not page_data or not page_data.html_content:
            return jsonify({
                'success': False,
                'error': 'Failed to collect page data',
                'url': url
            })
        
        # Detect banner
        detector = BannerDetector()
        banner_info = detector.detect_banner(page_data)
        
        if banner_info:
            # Generate rule
            generator = RuleGenerator()
            rule = generator.generate_consent_o_matic_json(banner_info)
            
            return jsonify({
                'success': True,
                'banner_detected': True,
                'confidence': banner_info.detection_confidence,
                'banner_type': banner_info.banner_type.value,
                'buttons_count': len(banner_info.buttons),
                'container_selector': banner_info.container_selector,
                'rule_generated': rule is not None,
                'url': url
            })
        else:
            return jsonify({
                'success': True,
                'banner_detected': False,
                'message': 'No consent banner detected',
                'url': url
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}',
            'url': url
        })

if __name__ == '__main__':
    print("Starting CMP Mapper on port 5001...")
    print("Open: http://localhost:5001")
    app.run(debug=True, port=5001, host='127.0.0.1')
