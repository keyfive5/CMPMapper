from flask import Flask, request, jsonify, send_file
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

app = Flask(__name__)
current_rule = None

@app.route('/')
def index():
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>CMP Mapper - Emergency Prototype</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        input { width: 70%; padding: 10px; border: 2px solid #007bff; border-radius: 5px; }
        button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        #loading { display: none; margin: 20px 0; }
        #result { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px; }
        #progress-bar { width: 0%; height: 30px; background: #28a745; border-radius: 5px; margin: 10px 0; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🔍 CMP Mapper - Emergency Prototype</h1>
    <p>Quick cookie banner detection and rule generation</p>
    
    <div style="margin: 30px 0;">
        <input type="text" id="url" placeholder="Enter website URL (e.g., https://www.margispharmacy.com/)">
        <button onclick="analyzeUrl()">Analyze Banner</button>
    </div>
    
    <div id="loading" style="text-align: center;">
        <div id="progress-bar"></div>
        <p id="loading-text">Analyzing...</p>
    </div>
    
    <div id="result"></div>
    
    <script>
        let currentRule = null;
        
        async function analyzeUrl() {
            const url = document.getElementById('url').value;
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const progressBar = document.getElementById('progress-bar');
            const loadingText = document.getElementById('loading-text');
            
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                if (progress <= 90) {
                    progressBar.style.width = progress + '%';
                    progressText = 'Scraping website...';
                    if (progress > 30) progressText = 'Detecting banner...';
                    if (progress > 60) progressText = 'Generating rule...';
                    loadingText.textContent = progressText;
                } else {
                    clearInterval(interval);
                }
            }, 500);
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                clearInterval(interval);
                progressBar.style.width = '100%';
                loadingText.textContent = 'Complete!';
                
                setTimeout(() => {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (data.success && data.banner_detected && data.rule) {
                        currentRule = data.rule;
                        result.innerHTML = 
                            '<h2 style="color: green;">✅ Banner Detected!</h2>' +
                            '<p><strong>Confidence:</strong> ' + (data.confidence * 100).toFixed(1) + '%</p>' +
                            '<p><strong>Banner Type:</strong> ' + data.banner_type + '</p>' +
                            '<button onclick="downloadRule()" style="background: #28a745; margin: 15px 0; padding: 12px 24px;">⬇️ Download rules.json</button>' +
                            '<details style="margin-top: 15px;">' +
                            '<summary style="cursor: pointer; color: #007bff; font-weight: bold;">📋 View Rule JSON</summary>' +
                            '<pre style="margin-top: 10px;">' + JSON.stringify(data.rule, null, 2) + '</pre>' +
                            '</details>';
                    } else {
                        result.innerHTML = '<h2 style="color: red;">❌ No Banner Detected</h2><p>' + (data.message || 'No consent banner found') + '</p>';
                    }
                }, 1000);
                
            } catch (error) {
                clearInterval(interval);
                loading.style.display = 'none';
                result.style.display = 'block';
                result.innerHTML = '<h2 style="color: red;">❌ Error</h2><p>' + error.message + '</p>';
            }
        }
        
        function downloadRule() {
            if (currentRule) {
                const blob = new Blob([JSON.stringify(currentRule, null, 2)], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'rules.json';
                a.click();
                window.URL.revokeObjectURL(url);
            }
        }
        
        // Allow Enter key to trigger analysis
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeUrl();
            }
        });
    </script>
</body>
</html>
'''
    return html

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global current_rule
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    try:
        scraper = WebScraper(headless=True, timeout=30)
        detector = BannerDetector()
        generator = RuleGenerator()
        
        page_data = scraper.collect_page(url)
        if not page_data or not page_data.html_content:
            return jsonify({'success': False, 'error': 'Failed to collect page data'})
        
        banner_info = detector.detect_banner(page_data)
        if not banner_info:
            return jsonify({
                'success': True,
                'banner_detected': False,
                'message': 'No consent banner detected on this page'
            })
        
        consent_o_matic_rule = generator.generate_consent_o_matic_json(banner_info)
        current_rule = consent_o_matic_rule
        
        return jsonify({
            'success': True,
            'banner_detected': True,
            'confidence': banner_info.detection_confidence,
            'banner_type': banner_info.banner_type.value,
            'rule': consent_o_matic_rule
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting Emergency CMP Mapper on port 5555...")
    print("Open: http://localhost:5555")
    app.run(debug=False, host='127.0.0.1', port=5555)

