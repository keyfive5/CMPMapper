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

# Store the last generated rule
current_rule = None

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
            
            <input type="text" id="url" placeholder="Enter website URL (e.g., https://www.margispharmacy.com/)" />
            <button onclick="test()">Analyze for Consent Banner</button>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <h3 style="margin-top: 0; font-size: 16px; color: #495057;">📋 Quick Test Links:</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <button onclick="loadUrl('https://www.margispharmacy.com/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Margis Pharmacy</button>
                    <button onclick="loadUrl('https://primecarepharmacy.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Prime Care Pharmacy</button>
                    <button onclick="loadUrl('https://blendrx.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">BlendRx</button>
                    <button onclick="loadUrl('https://www.fresenius-kabi.com/en-ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Fresenius Kabi</button>
                </div>
            </div>
            
            <div id="loading" style="display:none; margin-top: 20px;">
                <div style="background: #e0e0e0; height: 30px; border-radius: 15px; overflow: hidden; position: relative;">
                    <div id="progress-bar" style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: 0%; transition: width 0.3s ease; border-radius: 15px;"></div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 14px; font-weight: bold;">Loading...</div>
                </div>
                <p id="loading-text" style="text-align: center; margin-top: 10px; color: #666;">Starting analysis...</p>
            </div>
            
            <div id="result" class="result" style="display:none;"></div>
        </div>
        
        <script>
            async function test() {
                const url = document.getElementById('url').value;
                const result = document.getElementById('result');
                const loading = document.getElementById('loading');
                const progressBar = document.getElementById('progress-bar');
                const loadingText = document.getElementById('loading-text');
                
                // Hide previous results and show loading
                result.style.display = 'none';
                loading.style.display = 'block';
                progressBar.style.width = '10%';
                loadingText.textContent = 'Starting analysis...';
                
                // Simulate progress
                const progressSteps = [
                    { progress: 20, text: 'Scraping website...' },
                    { progress: 40, text: 'Analyzing HTML content...' },
                    { progress: 60, text: 'Detecting consent banner...' },
                    { progress: 80, text: 'Generating rule...' }
                ];
                
                let stepIndex = 0;
                const progressInterval = setInterval(() => {
                    if (stepIndex < progressSteps.length) {
                        const step = progressSteps[stepIndex];
                        progressBar.style.width = step.progress + '%';
                        loadingText.textContent = step.text;
                        stepIndex++;
                    }
                }, 1500);
                
                try {
                    const response = await fetch('/api/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    // Clear progress interval and complete loading
                    clearInterval(progressInterval);
                    progressBar.style.width = '100%';
                    loadingText.textContent = 'Analysis complete!';
                    
                    // Wait a moment, then show results
                    setTimeout(() => {
                        loading.style.display = 'none';
                        result.style.display = 'block';
                        
                        if (data.success) {
                            if (data.banner_detected && data.rule) {
                                result.innerHTML = `
                                    <h3>✅ Consent Banner Detected!</h3>
                                    <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                                    <p><strong>Banner Type:</strong> ${data.banner_type}</p>
                                    <p><strong>Buttons Found:</strong> ${data.buttons_count}</p>
                                    <p><strong>Container:</strong> ${data.container_selector}</p>
                                    <p><strong>URL:</strong> ${data.url}</p>
                                    <hr>
                                    <h4>Generated Consent O Matic Rule:</h4>
                                    <button onclick="downloadRule()" style="background: #28a745; margin: 10px 0;">⬇️ Download rules.json</button>
                                    <pre style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(data.rule, null, 2)}</pre>
                                `;
                            } else if (data.banner_detected) {
                                result.innerHTML = `
                                    <h3>✅ Consent Banner Detected!</h3>
                                    <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                                    <p><strong>Banner Type:</strong> ${data.banner_type}</p>
                                    <p><strong>URL:</strong> ${data.url}</p>
                                    <p style="color: red;">⚠️ Rule generation failed</p>
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
                    }, 500);  // Half second delay
                } catch (error) {
                    clearInterval(progressInterval);
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
                }
            }
            
            function downloadRule() {
                window.open('/api/download-rule', '_blank');
            }
            
            function loadUrl(url) {
                document.getElementById('url').value = url;
                // Optional: Auto-analyze when clicking a quick link
                // test();
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
            
            # Store the rule globally for download
            global current_rule
            current_rule = rule
            
            return jsonify({
                'success': True,
                'banner_detected': True,
                'confidence': banner_info.detection_confidence,
                'banner_type': banner_info.banner_type.value,
                'buttons_count': len(banner_info.buttons),
                'container_selector': banner_info.container_selector,
                'rule_generated': rule is not None,
                'rule': rule,
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

@app.route('/api/download-rule')
def download_rule():
    """Download the generated rule as JSON file."""
    global current_rule
    
    if not current_rule:
        return jsonify({'error': 'No rule generated yet'}), 400
    
    # Get the site name from the rule to create filename
    site_name = current_rule.get('site', 'consent_rule')
    # Clean the site name for filename
    filename = site_name.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '_')
    
    # Create a temporary file with the JSON rule
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(current_rule, f, indent=2)
        temp_path = f.name
    
    return send_file(
        temp_path,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{filename}_rule.json'
    )

if __name__ == '__main__':
    print("Starting CMP Mapper on port 5001...")
    print("Open: http://localhost:5001")
    app.run(debug=True, port=5001, host='127.0.0.1')
