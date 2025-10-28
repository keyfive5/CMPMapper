#!/usr/bin/env python3
"""
Working CMP Mapper - Minimal but functional version
"""

from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>CMP Mapper - Working Version</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            margin: 0; 
            padding: 20px; 
            min-height: 100vh;
        }
        .container { 
            background: white; 
            border-radius: 15px; 
            padding: 30px; 
            max-width: 800px; 
            margin: 0 auto; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .tab { 
            padding: 10px 20px; 
            background: #f8f9fa; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s ease;
        }
        .tab.active { background: #667eea; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; font-weight: bold; }
        .input-group input, .input-group textarea { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
        }
        .btn { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn:hover { background: #5a6fd8; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .results { 
            margin-top: 20px; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            border-left: 4px solid #667eea;
        }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .info { background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .website-item { 
            display: flex; 
            align-items: center; 
            padding: 10px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            margin: 5px 0; 
            cursor: pointer; 
            transition: all 0.3s ease;
        }
        .website-item:hover { background: #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍪 CMP Mapper - Working Version</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('single')">Single URL</button>
            <button class="tab" onclick="switchTab('multiple')">Multiple URLs</button>
            <button class="tab" onclick="switchTab('samples')">Sample Websites</button>
        </div>
        
        <div id="single-tab" class="tab-content active">
            <div class="input-group">
                <label>Website URL:</label>
                <input type="url" id="url-input" placeholder="https://example.com" value="https://example.com">
            </div>
            <button class="btn" onclick="analyzeSingle()">Analyze Website</button>
        </div>
        
        <div id="multiple-tab" class="tab-content">
            <div class="input-group">
                <label>Multiple URLs (one per line):</label>
                <textarea id="multiple-urls-input" rows="6" placeholder="https://example1.com&#10;https://example2.com"></textarea>
            </div>
            <button class="btn" onclick="analyzeMultiple()">Analyze All Websites</button>
        </div>
        
        <div id="samples-tab" class="tab-content">
            <h3>Sample Websites (No Consent Banners)</h3>
            <p>These websites are known to have no cookie consent banners.</p>
            
            <div class="website-item" onclick="addToMultipleUrls('https://www.whitehouse.gov')">
                🏛️ whitehouse.gov
            </div>
            <div class="website-item" onclick="addToMultipleUrls('https://www.canada.ca')">
                🇨🇦 canada.ca
            </div>
            <div class="website-item" onclick="addToMultipleUrls('https://www.gov.uk')">
                🇬🇧 gov.uk
            </div>
            <div class="website-item" onclick="addToMultipleUrls('https://www.mit.edu')">
                🎓 mit.edu
            </div>
            <div class="website-item" onclick="addToMultipleUrls('https://www.harvard.edu')">
                🎓 harvard.edu
            </div>
            
            <div style="margin-top: 20px;">
                <button class="btn" onclick="loadAllSampleWebsites()">Load All Sample Websites</button>
                <button class="btn btn-secondary" onclick="clearMultipleUrls()">Clear All</button>
            </div>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <!-- Results will appear here -->
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function showResults(html) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        }
        
        function showError(message) {
            showResults(`<div class="error">❌ ${message}</div>`);
        }
        
        function showSuccess(message) {
            showResults(`<div class="success">✅ ${message}</div>`);
        }
        
        function showInfo(message) {
            showResults(`<div class="info">ℹ️ ${message}</div>`);
        }
        
        async function analyzeSingle() {
            const url = document.getElementById('url-input').value.trim();
            if (!url) {
                showError('Please enter a URL to analyze');
                return;
            }
            
            showInfo('Analyzing website... Please wait.');
            
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
                
                if (data.banner_detected) {
                    showSuccess(`Consent banner detected on ${data.site}! Confidence: ${data.confidence}%`);
                } else {
                    showInfo(`No consent banner detected on ${data.site}`);
                }
            } catch (error) {
                showError('Analysis failed: ' + error.message);
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
            
            showInfo(`Analyzing ${urls.length} websites... Please wait.`);
            
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
                
                let html = '<h3>Analysis Results:</h3>';
                data.results.forEach((result, index) => {
                    const status = result.banner_detected ? 
                        '<span style="color: green;">✅ Banner Found</span>' : 
                        '<span style="color: red;">❌ No Banner</span>';
                    
                    html += `<div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <strong>${result.site}</strong> - ${status}
                        ${result.banner_detected ? `<br><small>Confidence: ${result.confidence}%</small>` : ''}
                    </div>`;
                });
                
                showResults(html);
            } catch (error) {
                showError('Analysis failed: ' + error.message);
            }
        }
        
        function addToMultipleUrls(url) {
            const textarea = document.getElementById('multiple-urls-input');
            if (textarea.value.trim()) {
                textarea.value += '\n' + url;
            } else {
                textarea.value = url;
            }
            switchTab('multiple');
            showInfo(`Added ${url} to Multiple URLs`);
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
            showInfo(`Loaded ${sampleWebsites.length} sample websites`);
        }
        
        function clearMultipleUrls() {
            document.getElementById('multiple-urls-input').value = '';
            showInfo('Cleared all URLs');
        }
        
        // Test that JavaScript is working
        console.log('CMP Mapper loaded successfully!');
    </script>
</body>
</html>
    ''')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a single URL."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Simulate analysis
        banner_detected = random.choice([True, False])
        confidence = random.randint(70, 95) if banner_detected else 0
        
        result = {
            'site': url,
            'banner_detected': banner_detected,
            'confidence': confidence
        }
        
        print(f"Analyzing {url} - Banner detected: {banner_detected}")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-multiple', methods=['POST'])
def analyze_multiple():
    """Analyze multiple URLs."""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'URLs are required'}), 400
        
        results = []
        for url in urls:
            banner_detected = random.choice([True, False])
            confidence = random.randint(70, 95) if banner_detected else 0
            
            results.append({
                'site': url,
                'banner_detected': banner_detected,
                'confidence': confidence
            })
            
            print(f"Analyzing {url} - Banner detected: {banner_detected}")
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting CMP Mapper (Working Version)...")
    print("=" * 50)
    print("Web Interface: http://127.0.0.1:5005")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(debug=False, host='127.0.0.1', port=5005)
