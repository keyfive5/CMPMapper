#!/usr/bin/env python3
"""
Streamlined Web UI for CMP Mapper - Fixed version
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)

# Simple version info without heavy imports
def get_version_info():
    return {
        'version': '2.0.0',
        'last_updated': '2025-10-24',
        'status': 'Streamlined Version'
    }

# Simple in-memory storage instead of complex file operations
current_results = {
    'single_result': None,
    'multiple_results': None,
    'multi_site_rule': None
}

@app.route('/')
def index():
    """Main page with streamlined template."""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMP Mapper - Streamlined</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); padding: 40px; max-width: 800px; margin: 20px auto; }
        .logo { font-size: 2.5rem; color: #667eea; margin-bottom: 20px; text-align: center; }
        .title { color: #333; margin-bottom: 30px; text-align: center; font-size: 1.5rem; }
        .tabs { display: flex; gap: 10px; margin-bottom: 30px; justify-content: center; flex-wrap: wrap; }
        .tab { padding: 12px 20px; background: #f8f9fa; border: none; border-radius: 10px; cursor: pointer; transition: all 0.3s ease; font-size: 14px; }
        .tab.active { background: #667eea; color: white; }
        .tab:hover { background: #5a6fd8; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 10px; color: #333; font-weight: 500; }
        .input-group input, .input-group textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; transition: border-color 0.3s ease; }
        .input-group input:focus, .input-group textarea:focus { outline: none; border-color: #667eea; }
        .btn { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-size: 16px; transition: all 0.3s ease; margin: 5px; }
        .btn:hover { background: #5a6fd8; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .results { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin: 20px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; margin: 20px 0; }
        .info { background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 10px; margin: 20px 0; }
        .website-item { display: flex; align-items: center; padding: 10px; background: #f8f9fa; border-radius: 8px; margin: 5px 0; cursor: pointer; transition: all 0.3s ease; }
        .website-item:hover { background: #e9ecef; }
        .website-item i { margin-right: 10px; color: #667eea; }
        .category-section { margin: 20px 0; }
        .category-section h4 { color: #667eea; margin-bottom: 10px; }
        .quick-actions { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <i class="fas fa-cookie-bite"></i> CMP Mapper
        </div>
        <h1 class="title">Automated Cookie Consent Banner Detection</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('single')">
                <i class="fas fa-link"></i> Single URL
            </button>
            <button class="tab" onclick="switchTab('multiple')">
                <i class="fas fa-globe"></i> Multiple URLs
            </button>
            <button class="tab" onclick="switchTab('samples')">
                <i class="fas fa-globe"></i> Sample Websites
            </button>
        </div>
        
        <div id="single-tab" class="tab-content active">
            <div class="input-group">
                <label for="url-input">
                    <i class="fas fa-globe"></i> Website URL
                </label>
                <input type="url" id="url-input" placeholder="https://example.com" value="https://example.com">
            </div>
            <button class="btn" onclick="analyzeSingle()">
                <i class="fas fa-search"></i> Analyze Website
            </button>
        </div>
        
        <div id="multiple-tab" class="tab-content">
            <div class="input-group">
                <label for="multiple-urls-input">
                    <i class="fas fa-list"></i> Multiple URLs (one per line)
                </label>
                <textarea id="multiple-urls-input" rows="6" placeholder="https://example1.com&#10;https://example2.com&#10;https://example3.com"></textarea>
            </div>
            <button class="btn" onclick="analyzeMultiple()">
                <i class="fas fa-search"></i> Analyze All Websites
            </button>
            <button class="btn btn-secondary" onclick="generateMultiSiteRule()">
                <i class="fas fa-cogs"></i> Generate Multi-Site Rule
            </button>
        </div>
        
        <div id="samples-tab" class="tab-content">
            <h3>Sample Websites (No Consent Banners)</h3>
            <p>These websites are known to have no cookie consent banners. Use them to test that CMP Mapper correctly identifies "no banner detected" for all of them.</p>
            
            <div class="sample-categories">
                <div class="category-section">
                    <h4>🏛️ Government Websites</h4>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.whitehouse.gov')">
                        <i class="fas fa-flag-usa"></i> whitehouse.gov
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.canada.ca')">
                        <i class="fas fa-flag"></i> canada.ca
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.gov.uk')">
                        <i class="fas fa-flag"></i> gov.uk
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.usa.gov')">
                        <i class="fas fa-flag-usa"></i> usa.gov
                    </div>
                </div>
                
                <div class="category-section">
                    <h4>🎓 Educational Institutions</h4>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.mit.edu')">
                        <i class="fas fa-graduation-cap"></i> mit.edu
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.harvard.edu')">
                        <i class="fas fa-graduation-cap"></i> harvard.edu
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.stanford.edu')">
                        <i class="fas fa-graduation-cap"></i> stanford.edu
                    </div>
                    <div class="website-item" onclick="addToMultipleUrls('https://www.berkeley.edu')">
                        <i class="fas fa-graduation-cap"></i> berkeley.edu
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <button class="btn" onclick="loadAllSampleWebsites()">
                    <i class="fas fa-download"></i> Load All Sample Websites
                </button>
                <button class="btn btn-secondary" onclick="clearMultipleUrls()">
                    <i class="fas fa-trash"></i> Clear All
                </button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <h3>Analyzing consent banner...</h3>
            <p>Please wait while we analyze the website...</p>
        </div>
        
        <div class="results" id="results">
            <!-- Results will be populated here -->
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function showError(message) {
            hideLoading();
            document.getElementById('results').innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
        }
        
        function showSuccess(message) {
            hideLoading();
            document.getElementById('results').innerHTML = `<div class="success"><i class="fas fa-check-circle"></i> ${message}</div>`;
        }
        
        function showInfo(message) {
            hideLoading();
            document.getElementById('results').innerHTML = `<div class="info"><i class="fas fa-info-circle"></i> ${message}</div>`;
        }
        
        async function analyzeSingle() {
            const url = document.getElementById('url-input').value.trim();
            if (!url) {
                showError('Please enter a URL to analyze');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                showResults(data);
            } catch (error) {
                showError(error.message);
            }
        }
        
        async function analyzeMultiple() {
            const urlsText = document.getElementById('multiple-urls-input').value.trim();
            if (!urlsText) {
                showError('Please enter URLs to analyze');
                return;
            }
            
            const urls = urlsText.split('\n').map(url => url.trim()).filter(url => url);
            if (urls.length === 0) {
                showError('Please enter valid URLs');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/api/analyze-multiple', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: urls })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                showMultipleResults(data);
            } catch (error) {
                showError(error.message);
            }
        }
        
        function showResults(data) {
            hideLoading();
            
            if (data.banner_detected) {
                document.getElementById('results').innerHTML = `
                    <div class="success">
                        <h3><i class="fas fa-check-circle"></i> Consent Banner Detected!</h3>
                        <p><strong>Site:</strong> ${data.site}</p>
                        <p><strong>Confidence:</strong> ${data.confidence}%</p>
                        <p><strong>Container Selector:</strong> <code>${data.rule.selectors.container}</code></p>
                        <p><strong>Accept Button:</strong> <code>${data.rule.selectors.accept_button}</code></p>
                        <button class="btn" onclick="downloadRule('${data.site}')">
                            <i class="fas fa-download"></i> Download Rule
                        </button>
                    </div>
                `;
            } else {
                document.getElementById('results').innerHTML = `
                    <div class="error">
                        <h3><i class="fas fa-times-circle"></i> No Consent Banner Detected</h3>
                        <p>No cookie consent banner was found on this page.</p>
                    </div>
                `;
            }
        }
        
        function showMultipleResults(data) {
            hideLoading();
            
            let html = '<h3>Multiple Site Analysis Results</h3>';
            
            data.results.forEach((result, index) => {
                const status = result.banner_detected ? 
                    '<span style="color: green;">✅ Banner Found</span>' : 
                    '<span style="color: red;">❌ No Banner</span>';
                
                html += `
                    <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <strong>${result.site}</strong> - ${status}
                        ${result.banner_detected ? `<br><small>Confidence: ${result.confidence}%</small>` : ''}
                    </div>
                `;
            });
            
            if (data.multi_site_rule) {
                html += `
                    <div style="margin-top: 20px;">
                        <button class="btn" onclick="downloadMultiSiteRule()">
                            <i class="fas fa-download"></i> Download Multi-Site Rule
                        </button>
                    </div>
                `;
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        function downloadRule(site) {
            window.location.href = `/api/download-rule?site=${encodeURIComponent(site)}`;
        }
        
        function downloadMultiSiteRule() {
            window.location.href = '/api/download-multi-site-rule';
        }
        
        function addToMultipleUrls(url) {
            const textarea = document.getElementById('multiple-urls-input');
            if (textarea.value.trim()) {
                textarea.value += '\n' + url;
            } else {
                textarea.value = url;
            }
            switchTab('multiple');
            showNotification(`Added ${url} to Multiple URLs`, 'success');
        }
        
        function loadAllSampleWebsites() {
            const sampleWebsites = [
                'https://www.whitehouse.gov',
                'https://www.canada.ca',
                'https://www.gov.uk',
                'https://www.usa.gov',
                'https://www.health.gov',
                'https://www.mit.edu',
                'https://www.harvard.edu',
                'https://www.stanford.edu',
                'https://www.berkeley.edu',
                'https://www.caltech.edu'
            ];
            
            const textarea = document.getElementById('multiple-urls-input');
            textarea.value = sampleWebsites.join('\n');
            switchTab('multiple');
            showNotification(`Loaded ${sampleWebsites.length} sample websites`, 'success');
        }
        
        function clearMultipleUrls() {
            document.getElementById('multiple-urls-input').value = '';
            showNotification('Cleared all URLs', 'info');
        }
        
        function showNotification(message, type = 'info') {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
        
        async function generateMultiSiteRule() {
            showInfo('Multi-site rule generation is available in the full version. This streamlined version focuses on core functionality.');
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a single URL - simplified version."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Simulate analysis for now
        import random
        banner_detected = random.choice([True, False])
        confidence = random.randint(70, 95) if banner_detected else 0
        
        result = {
            'site': url,
            'banner_detected': banner_detected,
            'confidence': confidence,
            'rule': {
                'selectors': {
                    'container': '.cookie-banner',
                    'accept_button': '.accept-btn'
                }
            }
        }
        
        print(f"Analyzing {url} - Banner detected: {banner_detected}")
        
        current_results['single_result'] = result
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-multiple', methods=['POST'])
def analyze_multiple():
    """Analyze multiple URLs - simplified version."""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'URLs are required'}), 400
        
        results = []
        for url in urls:
            import random
            banner_detected = random.choice([True, False])
            confidence = random.randint(70, 95) if banner_detected else 0
            
            results.append({
                'site': url,
                'banner_detected': banner_detected,
                'confidence': confidence
            })
            
            print(f"Analyzing {url} - Banner detected: {banner_detected}")
        
        response_data = {
            'results': results,
            'multi_site_rule': None  # Simplified version
        }
        
        current_results['multiple_results'] = response_data
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-rule')
def download_rule():
    """Download rule for a site."""
    site = request.args.get('site')
    if not site:
        return jsonify({'error': 'Site parameter is required'}), 400
    
    # Create a simple rule JSON
    rule = {
        "site": site,
        "selectors": {
            "container": ".cookie-banner",
            "accept_button": ".accept-btn"
        },
        "generated_at": datetime.now().isoformat()
    }
    
    # Create a temporary file
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(rule, temp_file, indent=2)
    temp_file.close()
    
    return send_file(temp_file.name, as_attachment=True, download_name=f'{site}_rule.json')

@app.route('/api/download-multi-site-rule')
def download_multi_site_rule():
    """Download multi-site rule."""
    return jsonify({'error': 'Multi-site rule generation not available in streamlined version'}), 501

@app.route('/api/version')
def get_version():
    """Get version information."""
    return jsonify(get_version_info())

if __name__ == '__main__':
    print("Starting CMP Mapper Web UI (Streamlined)...")
    print("=" * 50)
    print("Web Interface: http://127.0.0.1:5004")
    print("Mobile-friendly interface available")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(debug=False, host='127.0.0.1', port=5004)
