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
                <div style="margin-bottom: 15px;">
                    <h4 style="margin: 10px 0 5px 0; font-size: 14px; color: #28a745;">🟢 GoDaddy Group (8 sites):</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
                        <button onclick="loadUrl('https://pendalepharmacy.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Pendale Pharmacy</button>
                        <button onclick="loadUrl('https://northmedafixcompoundingpharmacy.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">North Medafix</button>
                        <button onclick="loadUrl('https://centerpharm.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">CenterPharm</button>
                        <button onclick="loadUrl('https://riverviewpharmacy.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Riverview Pharmacy</button>
                        <button onclick="loadUrl('https://nadiasmedicalcentre.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Nadia's Medical</button>
                        <button onclick="loadUrl('https://www.midtowncompoundingpharmacy.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Midtown Pharmacy</button>
                        <button onclick="loadUrl('https://abundancespecialtyrx.com/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Abundance Specialty</button>
                        <button onclick="loadUrl('https://rxottawa.ca/')" style="background: #17a2b8; padding: 8px 15px; font-size: 12px;">Rx Ottawa</button>
                    </div>
                    <h4 style="margin: 15px 0 5px 0; font-size: 14px; color: #ffc107;">🟡 CookieYes Group (4 sites):</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
                        <button onclick="loadUrl('https://eramosapharmacy.ca/')" style="background: #ffc107; padding: 8px 15px; font-size: 12px;">Eramosa Pharmacy</button>
                        <button onclick="loadUrl('https://www.westmountmedicalpharmacy.ca/')" style="background: #ffc107; padding: 8px 15px; font-size: 12px;">Westmount Medical</button>
                        <button onclick="loadUrl('https://primecarepharmacy.ca/')" style="background: #ffc107; padding: 8px 15px; font-size: 12px;">Prime Care</button>
                        <button onclick="loadUrl('https://www.arkellmedical.ca/')" style="background: #ffc107; padding: 8px 15px; font-size: 12px;">Arkell Medical</button>
                    </div>
                    <h4 style="margin: 15px 0 5px 0; font-size: 14px; color: #6f42c1;">🟣 Other Sites:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                        <button onclick="loadUrl('https://www.margispharmacy.com/')" style="background: #6f42c1; padding: 8px 15px; font-size: 12px;">Margis Pharmacy</button>
                        <button onclick="loadUrl('https://blendrx.ca/')" style="background: #6f42c1; padding: 8px 15px; font-size: 12px;">BlendRx</button>
                        <button onclick="loadUrl('https://www.fresenius-kabi.com/en-ca/')" style="background: #6f42c1; padding: 8px 15px; font-size: 12px;">Fresenius Kabi</button>
                    </div>
                </div>
                <button onclick="testAllSites()" style="background: #ffc107; color: #333; padding: 10px 20px; font-size: 14px; font-weight: bold; width: 100%;">🚀 Test All GoDaddy Sites (8)</button>
                <button onclick="testAllCookieYesSites()" style="background: #28a745; color: #fff; padding: 10px 20px; font-size: 14px; font-weight: bold; width: 100%; margin-top: 8px;">🚀 Test All CookieYes Sites (4)</button>
                <button onclick="generateBlendRxFreseniusRule()" style="background: #6f42c1; color: #fff; padding: 10px 20px; font-size: 14px; font-weight: bold; width: 100%; margin-top: 8px;">🧩 Generate Multi‑Site Rule (BlendRx + Fresenius)</button>
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
            
            async function generateBlendRxFreseniusRule() {
                const result = document.getElementById('result');
                const loading = document.getElementById('loading');
                const progressBar = document.getElementById('progress-bar');
                const loadingText = document.getElementById('loading-text');
                
                result.style.display = 'none';
                loading.style.display = 'block';
                progressBar.style.width = '20%';
                loadingText.textContent = 'Analyzing BlendRx...';
                
                try {
                    const response = await fetch('/api/multi-rule', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ urls: ['https://blendrx.ca/', 'https://www.fresenius-kabi.com/en-ca/'] })
                    });
                    
                    progressBar.style.width = '70%';
                    loadingText.textContent = 'Merging rules...';
                    const data = await response.json();
                    progressBar.style.width = '100%';
                    loadingText.textContent = 'Complete!';
                    
                    setTimeout(() => {
                        loading.style.display = 'none';
                        result.style.display = 'block';
                        if (data.success) {
                            result.innerHTML = `
                                <h3>✅ Multi‑Site Rule Generated</h3>
                                <p><strong>Sites:</strong> ${data.summary.join(', ')}</p>
                                <p><strong>Detectors:</strong> ${data.rule.detectors ? data.rule.detectors.length : 0}</p>
                                <p><strong>Methods:</strong> ${data.rule.methods ? data.rule.methods.length : 0}</p>
                                <button onclick="downloadRule()" style="background: #28a745; margin: 10px 0;">⬇️ Download rules.json</button>
                                <details style="margin-top: 10px;">
  <summary style="cursor: pointer; color: #007bff; font-weight: bold;">📋 View Combined Rule JSON</summary>
  <pre style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px;">${JSON.stringify(data.rule, null, 2)}</pre>
</details>
                            `;
                        } else {
                            result.innerHTML = `<h3>❌ Failed</h3><p>${data.error || 'Could not generate multi‑site rule'}</p>`;
                        }
                    }, 400);
                } catch (err) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = `<h3>❌ Error</h3><p>${err.message}</p>`;
                }
            }
            
            async function testAllSites() {
                const sites = [
                    { url: 'https://pendalepharmacy.ca/', name: 'Pendale Pharmacy' },
                    { url: 'https://northmedafixcompoundingpharmacy.ca/', name: 'North Medafix' },
                    { url: 'https://centerpharm.ca/', name: 'CenterPharm' },
                    { url: 'https://riverviewpharmacy.ca/', name: 'Riverview Pharmacy' },
                    { url: 'https://nadiasmedicalcentre.ca/', name: 'Nadia\'s Medical' },
                    { url: 'https://www.midtowncompoundingpharmacy.ca/', name: 'Midtown Pharmacy' },
                    { url: 'https://abundancespecialtyrx.com/', name: 'Abundance Specialty' },
                    { url: 'https://rxottawa.ca/', name: 'Rx Ottawa' }
                ];
                
                await testSiteGroup(sites, 'GoDaddy Group');
            }
            
            async function testAllCookieYesSites() {
                const sites = [
                    { url: 'https://eramosapharmacy.ca/', name: 'Eramosa Pharmacy' },
                    { url: 'https://www.westmountmedicalpharmacy.ca/', name: 'Westmount Medical' },
                    { url: 'https://primecarepharmacy.ca/', name: 'Prime Care' },
                    { url: 'https://www.arkellmedical.ca/', name: 'Arkell Medical' }
                ];
                
                await testSiteGroup(sites, 'CookieYes Group');
            }
            
            async function testSiteGroup(sites, groupName) {
                const result = document.getElementById('result');
                const loading = document.getElementById('loading');
                
                loading.style.display = 'block';
                result.style.display = 'block';
                
                let resultsHTML = `<h3>Test Results for ${groupName} (${sites.length} sites)</h3>`;
                
                for (let i = 0; i < sites.length; i++) {
                    const site = sites[i];
                    
                    // Add site header
                    resultsHTML += `<hr><h4>${i + 1}. ${site.name}</h4>`;
                    resultsHTML += `<p>URL: ${site.url}</p>`;
                    resultsHTML += `<div id="site-${i}">`;
                    resultsHTML += `
                        <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                            <div id="progress-${i}" style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: 0%; transition: width 0.3s ease; border-radius: 12px;"></div>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold;">Loading...</div>
                        </div>
                        <p id="eta-${i}" style="text-align: center; color: #666; font-size: 12px;">Analyzing... ETA: ~10s</p>
                    `;
                    resultsHTML += '</div>';
                    
                    result.innerHTML = resultsHTML;
                    result.style.display = 'block';
                    
                    // Simulate progress
                    const progressSteps = [
                        { progress: 25, text: 'Scraping website...', eta: 8 },
                        { progress: 50, text: 'Analyzing HTML...', eta: 6 },
                        { progress: 75, text: 'Detecting banner...', eta: 3 },
                        { progress: 95, text: 'Generating rule...', eta: 1 }
                    ];
                    
                    let stepIndex = 0;
                    const progressInterval = setInterval(() => {
                        if (stepIndex < progressSteps.length) {
                            const step = progressSteps[stepIndex];
                            const progressBar = document.getElementById(`progress-${i}`);
                            const etaText = document.getElementById(`eta-${i}`);
                            if (progressBar && etaText) {
                                progressBar.style.width = step.progress + '%';
                                etaText.textContent = `${step.text} ETA: ~${step.eta}s`;
                            }
                            stepIndex++;
                        }
                    }, 2000);
                    
                    try {
                        const response = await fetch('/api/test', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ url: site.url })
                        });
                        
                        clearInterval(progressInterval);
                        
                        const progressBar = document.getElementById(`progress-${i}`);
                        const etaText = document.getElementById(`eta-${i}`);
                        if (progressBar) progressBar.style.width = '100%';
                        if (etaText) etaText.textContent = 'Analysis complete!';
                        
                        const data = await response.json();
                        
                        // Update the specific site's content
                        const siteDiv = document.getElementById(`site-${i}`);
                        
                        if (data.success && data.banner_detected && data.rule) {
                            siteDiv.innerHTML = `
                                <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                                    <div style="background: #28a745; height: 100%; width: 100%; border-radius: 12px;"></div>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold; color: white;">Complete!</div>
                                </div>
                                <p style="color: green; font-weight: bold;">✅ Banner Detected (Confidence: ${(data.confidence * 100).toFixed(1)}%)</p>
                                <p>Banner Type: ${data.banner_type}</p>
                                <p>Buttons Found: ${data.buttons_count}</p>
                                <button onclick="downloadRule()" style="background: #28a745; margin: 10px 0; padding: 8px 15px; color: white; border: none; border-radius: 5px; cursor: pointer;">⬇️ Download rules.json</button>
                                <details style="margin-top: 10px;">
                                    <summary style="cursor: pointer; color: #007bff; font-weight: bold;">📋 View Rule JSON</summary>
                                    <pre style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px;">${JSON.stringify(data.rule, null, 2)}</pre>
                                </details>
                            `;
                        } else if (data.success && data.banner_detected) {
                            siteDiv.innerHTML = `
                                <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                                    <div style="background: #ffc107; height: 100%; width: 100%; border-radius: 12px;"></div>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold; color: #333;">Warning!</div>
                                </div>
                                <p style="color: orange;">⚠️ Banner Detected but Rule Generation Failed</p>
                                <p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
                            `;
                        } else if (data.success) {
                            siteDiv.innerHTML = `
                                <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                                    <div style="background: #dc3545; height: 100%; width: 100%; border-radius: 12px;"></div>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold; color: white;">No Banner</div>
                                </div>
                                <p style="color: red;">❌ No Banner Detected</p>
                                <p>${data.message || 'No consent banner found on this page'}</p>
                            `;
                        } else {
                            siteDiv.innerHTML = `
                                <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                                    <div style="background: #dc3545; height: 100%; width: 100%; border-radius: 12px;"></div>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold; color: white;">Failed</div>
                                </div>
                                <p style="color: red;">❌ Analysis Failed</p>
                                <p>${data.error || 'Unknown error'}</p>
                            `;
                        }
                        
                    } catch (error) {
                        clearInterval(progressInterval);
                        const siteDiv = document.getElementById(`site-${i}`);
                        siteDiv.innerHTML = `
                            <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; position: relative; margin: 10px 0;">
                                <div style="background: #dc3545; height: 100%; width: 100%; border-radius: 12px;"></div>
                                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: bold; color: white;">Error</div>
                            </div>
                            <p style="color: red;">❌ Network Error</p>
                            <p>${error.message}</p>
                        `;
                    }
                    
                    // Wait 1 second before testing next site
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
                loading.style.display = 'none';
                result.innerHTML = resultsHTML;
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

@app.route('/api/multi-rule', methods=['POST'])
def multi_rule():
    """Generate a combined Consent O Matic rule from multiple URLs."""
    data = request.get_json(silent=True) or {}
    urls = data.get('urls', [])
    if not urls:
        return jsonify({'success': False, 'error': 'No URLs provided'}), 400
    
    try:
        from src.collectors.web_scraper import WebScraper
        from src.detectors.banner_detector import BannerDetector
        from src.generators.rule_generator import RuleGenerator
        
        rules = []
        summaries = []
        
        with WebScraper(headless=True, timeout=35) as scraper:
            detector = BannerDetector()
            generator = RuleGenerator()
            
            for url in urls:
                page_data = scraper.collect_page(url)
                if not page_data or not page_data.html_content:
                    continue
                banner_info = detector.detect_banner(page_data)
                if not banner_info:
                    continue
                rule = generator.generate_consent_o_matic_json(banner_info)
                if rule:
                    rules.append(rule)
                    summaries.append(url)
        
        if not rules:
            return jsonify({'success': False, 'error': 'No rules could be generated'}), 200
        
        # Merge rules (array-based format expected)
        def dedup_list(items):
            seen = set()
            out = []
            for it in items:
                key = json.dumps(it, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    out.append(it)
            return out
        
        combined_detectors = []
        combined_methods = []
        for r in rules:
            ds = r.get('detectors', [])
            ms = r.get('methods', [])
            # Support object-based fallback
            if isinstance(ds, dict):
                ds = list(ds.values())
            if isinstance(ms, dict):
                ms = list(ms.values())
            combined_detectors.extend(ds)
            combined_methods.extend(ms)
        
        # Ensure non-empty detectors/methods
        merged_detectors = dedup_list(combined_detectors)
        if not merged_detectors:
            merged_detectors = [{ 'preset': 'always', 'showing': 'body' }]
        merged_methods = dedup_list(combined_methods)

        combined_rule = {
            'site': 'multi: blendrx.ca + fresenius-kabi.com',
            'detectors': merged_detectors,
            'methods': merged_methods
        }
        
        # Store for download
        global current_rule
        current_rule = combined_rule
        
        return jsonify({'success': True, 'rule': combined_rule, 'summary': summaries}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 200

if __name__ == '__main__':
    print("Starting CMP Mapper on port 5002...")
    print("Open: http://localhost:5002")
    app.run(debug=False, port=5002, host='127.0.0.1')
