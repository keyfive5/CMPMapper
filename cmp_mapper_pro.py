#!/usr/bin/env python3
"""
CMP Mapper Pro - Professional Web Interface
Beautiful, comprehensive prototype with Excel upload, mass testing, and rules management
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import json
from werkzeug.utils import secure_filename
import glob

# Try to import pandas (optional for Excel upload)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. Excel upload functionality will be limited.")

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store the last generated rule
current_rule = None
current_test_results = []

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_rules_from_directory():
    """Load all JSON rules from the rules directories."""
    rules = []
    
    # Load from custom-consent-o-matic-rules/rules
    rules_dir = 'custom-consent-o-matic-rules/rules'
    if os.path.exists(rules_dir):
        for rule_file in glob.glob(os.path.join(rules_dir, '*.json')):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)
                    rule_data['filename'] = os.path.basename(rule_file)
                    rule_data['path'] = rule_file
                    rules.append(rule_data)
            except Exception as e:
                print(f"Error loading rule {rule_file}: {e}")
    
    # Load from data/rules
    data_rules_dir = 'data/rules'
    if os.path.exists(data_rules_dir):
        for rule_file in glob.glob(os.path.join(data_rules_dir, '*_consent_o_matic.json')):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)
                    rule_data['filename'] = os.path.basename(rule_file)
                    rule_data['path'] = rule_file
                    rules.append(rule_data)
            except Exception as e:
                print(f"Error loading rule {rule_file}: {e}")
    
    return rules

@app.route('/')
def index():
    """Main page with beautiful UI."""
    rules = load_rules_from_directory()
    # Create safe JSON for JavaScript - json.dumps produces valid JavaScript
    rules_data = []
    for r in rules:
        rules_data.append({
            'filename': str(r.get('filename', 'unknown')),
            'site': str(r.get('site', 'unknown'))
        })
        # json.dumps produces valid JavaScript object notation
    rules_json_str = json.dumps(rules_data, ensure_ascii=False)
    # Escape </script> to prevent breaking the script tag
    rules_json_str = rules_json_str.replace('</script>', '<\\/script>').replace('</SCRIPT>', '<\\/SCRIPT>')
    rules_html = generate_rules_html(rules)
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CMP Mapper Pro - Consent Banner Detection & Rule Generation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .tabs {{
                display: flex;
                background: #f8f9fa;
                border-bottom: 2px solid #e9ecef;
                overflow-x: auto;
            }}
            
            .tab {{
                padding: 20px 30px;
                cursor: pointer;
                border: none;
                background: transparent;
                font-size: 16px;
                font-weight: 600;
                color: #666;
                transition: all 0.3s;
                border-bottom: 3px solid transparent;
                white-space: nowrap;
            }}
            
            .tab:hover {{
                background: #e9ecef;
                color: #667eea;
            }}
            
            .tab.active {{
                color: #667eea;
                border-bottom-color: #667eea;
                background: white;
            }}
            
            .tab-content {{
                display: none;
                padding: 40px;
            }}
            
            .tab-content.active {{
                display: block;
            }}
            
            .input-group {{
                margin-bottom: 25px;
            }}
            
            .input-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #495057;
                font-size: 14px;
            }}
            
            .input-group input, .input-group textarea {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s;
            }}
            
            .input-group input:focus, .input-group textarea:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .btn {{
                padding: 14px 28px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: inline-block;
                text-align: center;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            
            .btn-success {{
                background: #28a745;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #218838;
                transform: translateY(-2px);
            }}
            
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            
            .btn-secondary:hover {{
                background: #5a6268;
            }}
            
            .btn-group {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin: 20px 0;
            }}
            
            .quick-links {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 12px;
                margin: 25px 0;
            }}
            
            .quick-links h3 {{
                margin-bottom: 15px;
                color: #495057;
            }}
            
            .group-section {{
                margin-bottom: 20px;
            }}
            
            .group-title {{
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
                color: #495057;
            }}
            
            .quick-link-btn {{
                padding: 8px 16px;
                margin: 5px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .quick-link-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            
            .progress-container {{
                display: none;
                margin: 25px 0;
            }}
            
            .progress-bar {{
                background: #e9ecef;
                height: 40px;
                border-radius: 20px;
                overflow: hidden;
                position: relative;
                margin-bottom: 10px;
            }}
            
            .progress-fill {{
                background: linear-gradient(90deg, #28a745, #20c997);
                height: 100%;
                width: 0%;
                transition: width 0.3s ease;
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
            }}
            
            .result-container {{
                display: none;
                margin-top: 30px;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 12px;
                border-left: 4px solid #667eea;
            }}
            
            .result-success {{
                border-left-color: #28a745;
            }}
            
            .result-error {{
                border-left-color: #dc3545;
            }}
            
            .result-warning {{
                border-left-color: #ffc107;
            }}
            
            .code-block {{
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                margin: 15px 0;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
            }}
            
            .stat-card h3 {{
                font-size: 2.5em;
                margin-bottom: 5px;
            }}
            
            .stat-card p {{
                opacity: 0.9;
                font-size: 14px;
            }}
            
            .rules-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            
            .rule-card {{
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s;
            }}
            
            .rule-card:hover {{
                border-color: #667eea;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
                transform: translateY(-2px);
            }}
            
            .rule-card h4 {{
                color: #667eea;
                margin-bottom: 10px;
            }}
            
            .file-upload-area {{
                border: 3px dashed #667eea;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                background: #f8f9fa;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .file-upload-area:hover {{
                background: #e9ecef;
                border-color: #764ba2;
            }}
            
            .file-upload-area.dragover {{
                background: #e7f3ff;
                border-color: #667eea;
            }}
            
            .test-results-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            .test-results-table th, .test-results-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }}
            
            .test-results-table th {{
                background: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }}
            
            .status-badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            
            .status-success {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-error {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .status-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            
            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 1.8em;
                }}
                
                .tabs {{
                    flex-direction: column;
                }}
                
                .tab {{
                    width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍪 CMP Mapper Pro</h1>
                <p>Automated Consent Banner Detection & Consent O Matic Rule Generation</p>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('analyze', this)">🔍 Analyze Banner</button>
                <button class="tab" onclick="switchTab('pharmacy-test', this)">🏥 Pharmacy Sites CMP Detection</button>
                <button class="tab" onclick="switchTab('upload', this)">📊 Excel/CSV Upload</button>
                <button class="tab" onclick="switchTab('mass-test', this)">🚀 Mass Testing</button>
                <button class="tab" onclick="switchTab('rules', this)">📋 Rules Manager</button>
                <button class="tab" onclick="switchTab('about', this)">ℹ️ About</button>
            </div>
            
            <!-- Analyze Tab -->
            <div id="analyze" class="tab-content active">
                <h2>Single URL Analysis</h2>
                <p style="color: #666; margin-bottom: 25px;">Enter a website URL to detect consent banners and generate Consent O Matic rules</p>
                
                <div class="input-group">
                    <label for="url">Website URL</label>
                    <input type="text" id="url" placeholder="https://www.example.com/" />
                </div>
                
                <button class="btn btn-primary" onclick="analyzeBanner()">🔍 Analyze Consent Banner</button>
                
                <div class="quick-links">
                    <h3>📋 Quick Test Links</h3>
                    
                    <div class="group-section">
                        <div class="group-title">🟢 GoDaddy Group (8 sites)</div>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://pendalepharmacy.ca/')">Pendale Pharmacy</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://northmedafixcompoundingpharmacy.ca/')">North Medafix</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://centerpharm.ca/')">CenterPharm</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://riverviewpharmacy.ca/')">Riverview Pharmacy</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://nadiasmedicalcentre.ca/')">Nadia's Medical</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://www.midtowncompoundingpharmacy.ca/')">Midtown Pharmacy</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://abundancespecialtyrx.com/')">Abundance Specialty</button>
                        <button class="quick-link-btn" style="background: #17a2b8; color: white;" onclick="loadUrl('https://rxottawa.ca/')">Rx Ottawa</button>
                    </div>
                    
                    <div class="group-section">
                        <div class="group-title">🟡 CookieYes Group (4 sites)</div>
                        <button class="quick-link-btn" style="background: #ffc107; color: #333;" onclick="loadUrl('https://eramosapharmacy.ca/')">Eramosa Pharmacy</button>
                        <button class="quick-link-btn" style="background: #ffc107; color: #333;" onclick="loadUrl('https://www.westmountmedicalpharmacy.ca/')">Westmount Medical</button>
                        <button class="quick-link-btn" style="background: #ffc107; color: #333;" onclick="loadUrl('https://primecarepharmacy.ca/')">Prime Care</button>
                        <button class="quick-link-btn" style="background: #ffc107; color: #333;" onclick="loadUrl('https://www.arkellmedical.ca/')">Arkell Medical</button>
                    </div>
                    
                    <div class="group-section">
                        <div class="group-title">🟣 Other Sites</div>
                        <button class="quick-link-btn" style="background: #6f42c1; color: white;" onclick="loadUrl('https://www.margispharmacy.com/')">Margis Pharmacy</button>
                        <button class="quick-link-btn" style="background: #6f42c1; color: white;" onclick="loadUrl('https://blendrx.ca/')">BlendRx</button>
                        <button class="quick-link-btn" style="background: #6f42c1; color: white;" onclick="loadUrl('https://www.fresenius-kabi.com/en-ca/')">Fresenius Kabi</button>
                    </div>
                    
                    <div class="btn-group" style="margin-top: 20px;">
                        <button class="btn btn-success" onclick="testAllGoDaddy()">🚀 Test All GoDaddy Sites (8)</button>
                        <button class="btn btn-success" onclick="testAllCookieYes()">🚀 Test All CookieYes Sites (4)</button>
                    </div>
                </div>
                
                <div class="progress-container" id="progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill">0%</div>
                    </div>
                    <p id="progress-text" style="text-align: center; color: #666;">Starting analysis...</p>
                </div>
                
                <div class="result-container" id="result"></div>
            </div>
            
            <!-- Pharmacy Sites CMP Detection Tab -->
            <div id="pharmacy-test" class="tab-content">
                <h2>🏥 Pharmacy Sites CMP Detection</h2>
                <p style="color: #666; margin-bottom: 25px;">Test all 15 pharmacy websites to identify their CMP groups (GoDaddy, CookieYes, OneTrust, Cookiebot, etc.)</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                    <h3 style="margin-top: 0;">All Pharmacy Sites (15 total)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; margin-top: 15px;">
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">1. Pendale Pharmacy</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">2. North Medafix</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">3. CenterPharm</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">4. Riverview Pharmacy</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">5. Nadia's Medical</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">6. Midtown Pharmacy</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">7. Abundance Specialty</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #17a2b8;">8. Rx Ottawa</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #ffc107;">9. Eramosa Pharmacy</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #ffc107;">10. Westmount Medical</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #ffc107;">11. Prime Care</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #ffc107;">12. Arkell Medical</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #6f42c1;">13. Margis Pharmacy</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #6f42c1;">14. BlendRx</div>
                        <div style="padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #6f42c1;">15. Fresenius Kabi</div>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="testAllPharmacySites()" style="width: 100%; padding: 15px; font-size: 18px;">🚀 Test All 15 Pharmacy Sites & Detect CMP Groups</button>
                
                <div class="progress-container" id="pharmacy-progress" style="display: none; margin-top: 25px;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="pharmacy-progress-fill">0%</div>
                    </div>
                    <p id="pharmacy-progress-text" style="text-align: center; color: #666;">Starting tests...</p>
                    <p id="pharmacy-progress-status" style="text-align: center; color: #999; font-size: 14px; margin-top: 10px;">Preparing to test 15 sites...</p>
                </div>
                
                <div id="pharmacy-results" style="margin-top: 30px;"></div>
            </div>
            
            <!-- Excel Upload Tab -->
            <div id="upload" class="tab-content">
                <h2>📊 Excel/CSV Upload</h2>
                <p style="color: #666; margin-bottom: 25px;">Upload an Excel (.xlsx, .xls) or CSV file with URLs to extract and test</p>
                
                <div class="file-upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" accept=".xlsx,.xls,.csv" style="display: none;" onchange="handleFileSelect(event)">
                    <h3>📁 Click to Upload or Drag & Drop</h3>
                    <p>Supported formats: .xlsx, .xls, .csv</p>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">The file should have URLs in the first column or a column named "URL"</p>
                </div>
                
                <div id="upload-result" style="margin-top: 20px;"></div>
                
                <div id="extracted-urls" style="display: none; margin-top: 30px;">
                    <h3>Extracted URLs</h3>
                    <div id="urls-list" style="max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0;"></div>
                    <button class="btn btn-primary" onclick="useUrlsForMassTest()">🚀 Use These URLs for Mass Testing</button>
                </div>
            </div>
            
            <!-- Mass Testing Tab -->
            <div id="mass-test" class="tab-content">
                <h2>🚀 Mass Testing</h2>
                <p style="color: #666; margin-bottom: 25px;">Test multiple URLs against your Consent O Matic rules</p>
                
                <div class="input-group">
                    <label for="mass-urls">URLs (one per line)</label>
                    <textarea id="mass-urls" rows="10" placeholder="https://example1.com/&#10;https://example2.com/&#10;https://example3.com/"></textarea>
                </div>
                
                <div class="input-group">
                    <label>Select Rules to Test</label>
                    <div id="rules-checkboxes" style="max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                        <label style="display: block; margin: 10px 0;">
                            <input type="checkbox" id="test-all-rules" checked onchange="toggleAllRules()"> 
                            <strong>Test All Rules</strong>
                        </label>
                        <div id="rules-list-checkboxes"></div>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="startMassTest()">🚀 Start Mass Testing</button>
                
                <div id="mass-test-results" style="margin-top: 30px;"></div>
            </div>
            
            <!-- Rules Manager Tab -->
            <div id="rules" class="tab-content">
                <h2>📋 Rules Manager</h2>
                <p style="color: #666; margin-bottom: 25px;">View and manage your Consent O Matic rules</p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{len(rules)}</h3>
                        <p>Total Rules</p>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        <h3>5</h3>
                        <p>CMP Groups</p>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        <h3>12+</h3>
                        <p>Tested Sites</p>
                    </div>
                </div>
                
                <div class="rules-list" id="rules-list">
                    {rules_html}
                </div>
            </div>
            
            <!-- About Tab -->
            <div id="about" class="tab-content">
                <h2>ℹ️ About CMP Mapper Pro</h2>
                <div style="line-height: 1.8; color: #666;">
                    <h3 style="color: #667eea; margin: 20px 0 10px 0;">What is CMP Mapper?</h3>
                    <p>CMP Mapper Pro is an automated tool for detecting cookie consent banners and generating Consent O Matic compatible rules. It helps researchers and developers quickly identify and handle consent management platforms (CMPs) across multiple websites.</p>
                    
                    <h3 style="color: #667eea; margin: 20px 0 10px 0;">Features</h3>
                    <ul style="margin-left: 20px; margin-bottom: 20px;">
                        <li>🔍 Automated banner detection using advanced pattern recognition</li>
                        <li>📊 Excel/CSV upload for batch processing</li>
                        <li>🚀 Mass testing against multiple URLs</li>
                        <li>📋 Rules management and organization</li>
                        <li>🍪 Support for 5+ CMP groups (GoDaddy, CookieYes, OneTrust, etc.)</li>
                        <li>☁️ Cloud-ready deployment</li>
                    </ul>
                    
                    <h3 style="color: #667eea; margin: 20px 0 10px 0;">CMP Groups Identified</h3>
                    <ul style="margin-left: 20px; margin-bottom: 20px;">
                        <li><strong>GoDaddy Website Builder</strong> - 8 pharmacy websites</li>
                        <li><strong>CookieYes</strong> - 4 pharmacy websites</li>
                        <li><strong>OneTrust</strong> - Enterprise CMP</li>
                        <li><strong>Shopify Privacy Center</strong> - E-commerce sites</li>
                        <li><strong>Custom WordPress</strong> - Custom implementations</li>
                    </ul>
                    
                    <h3 style="color: #667eea; margin: 20px 0 10px 0;">How It Works</h3>
                    <ol style="margin-left: 20px; margin-bottom: 20px;">
                        <li>Enter a website URL or upload an Excel file with URLs</li>
                        <li>CMP Mapper scrapes the website and analyzes the HTML</li>
                        <li>It detects consent banners using pattern recognition</li>
                        <li>Generates Consent O Matic compatible JSON rules</li>
                        <li>You can download and import rules into Consent O Matic</li>
                    </ol>
                </div>
            </div>
        </div>
        
        <script id="rules-data" type="application/json">{rules_json_str}</script>
        <script>
            // Rules data loaded above
            let extractedUrls = [];
            let allRules = [];
            try {{
                const rulesDataElement = document.getElementById('rules-data');
                if (rulesDataElement) {{
                    allRules = JSON.parse(rulesDataElement.textContent);
                }}
            }} catch (e) {{
                console.error('Error parsing rules:', e);
                allRules = [];
            }}
            
            function switchTab(tabName, clickedButton) {{
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(function(tab) {{
                    tab.classList.remove('active');
                }});
                document.querySelectorAll('.tab').forEach(function(tab) {{
                    tab.classList.remove('active');
                }});
                
                // Show selected tab
                const tabContent = document.getElementById(tabName);
                if (tabContent) {{
                    tabContent.classList.add('active');
                }}
                
                // Activate clicked button
                if (clickedButton) {{
                    clickedButton.classList.add('active');
                }} else {{
                    // Fallback: find button by tab name
                    document.querySelectorAll('.tab').forEach(function(btn) {{
                        var onclickAttr = btn.getAttribute('onclick');
                        if (onclickAttr && onclickAttr.indexOf(tabName) !== -1) {{
                            btn.classList.add('active');
                        }}
                    }});
                }}
                
                // Load rules checkboxes if mass-test tab
                if (tabName === 'mass-test') {{
                    loadRulesCheckboxes();
                }}
            }}
            
            function loadUrl(url) {{
                document.getElementById('url').value = url;
            }}
            
            async function analyzeBanner() {{
                const url = document.getElementById('url').value;
                if (!url) {{
                    alert('Please enter a URL');
                    return;
                }}
                
                const progress = document.getElementById('progress');
                const result = document.getElementById('result');
                const progressFill = document.getElementById('progress-fill');
                const progressText = document.getElementById('progress-text');
                
                progress.style.display = 'block';
                result.style.display = 'none';
                progressFill.style.width = '10%';
                progressFill.textContent = '10%';
                progressText.textContent = 'Starting analysis...';
                
                const steps = [
                    {{progress: 20, text: 'Scraping website...'}},
                    {{progress: 40, text: 'Analyzing HTML content...'}},
                    {{progress: 60, text: 'Detecting consent banner...'}},
                    {{progress: 80, text: 'Generating rule...'}}
                ];
                
                let stepIndex = 0;
                const progressInterval = setInterval(() => {{
                    if (stepIndex < steps.length) {{
                        const step = steps[stepIndex];
                        progressFill.style.width = step.progress + '%';
                        progressFill.textContent = step.progress + '%';
                        progressText.textContent = step.text;
                        stepIndex++;
                    }}
                }}, 1500);
                
                try {{
                    const response = await fetch('/api/test', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    
                    clearInterval(progressInterval);
                    progressFill.style.width = '100%';
                    progressFill.textContent = '100%';
                    progressText.textContent = 'Analysis complete!';
                    
                    const data = await response.json();
                    
                    setTimeout(() => {{
                        progress.style.display = 'none';
                        result.style.display = 'block';
                        
                        if (data.success && data.banner_detected && data.rule) {{
                            result.className = 'result-container result-success';
                            const confidencePercent = (data.confidence * 100).toFixed(1);
                            const ruleJson = JSON.stringify(data.rule, null, 2);
                            result.innerHTML = 
                                '<h3>✅ Consent Banner Detected!</h3>' +
                                '<div class="stats-grid">' +
                                    '<div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">' +
                                        '<h3>' + confidencePercent + '%</h3>' +
                                        '<p>Confidence</p>' +
                                    '</div>' +
                                    '<div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">' +
                                        '<h3>' + data.buttons_count + '</h3>' +
                                        '<p>Buttons Found</p>' +
                                    '</div>' +
                                '</div>' +
                                '<p><strong>Banner Type:</strong> ' + data.banner_type + '</p>' +
                                '<p><strong>Container:</strong> ' + data.container_selector + '</p>' +
                                '<p><strong>URL:</strong> ' + data.url + '</p>' +
                                '<button class="btn btn-success" onclick="downloadRule()" style="margin: 15px 0;">⬇️ Download rules.json</button>' +
                                '<details>' +
                                    '<summary style="cursor: pointer; color: #667eea; font-weight: bold; margin: 15px 0;">📋 View Generated Rule JSON</summary>' +
                                    '<div class="code-block">' + ruleJson + '</div>' +
                                '</details>';
                        }} else if (data.success && data.banner_detected) {{
                            result.className = 'result-container result-warning';
                            const confidencePercent = (data.confidence * 100).toFixed(1);
                            result.innerHTML = 
                                '<h3>⚠️ Banner Detected but Rule Generation Failed</h3>' +
                                '<p><strong>Confidence:</strong> ' + confidencePercent + '%</p>' +
                                '<p><strong>Banner Type:</strong> ' + data.banner_type + '</p>';
                        }} else if (data.success) {{
                            result.className = 'result-container result-warning';
                            const message = data.message || 'No consent banner found on this page';
                            result.innerHTML = 
                                '<h3>❌ No Consent Banner Detected</h3>' +
                                '<p>' + message + '</p>' +
                                '<p><strong>URL:</strong> ' + data.url + '</p>';
                        }} else {{
                            result.className = 'result-container result-error';
                            result.innerHTML = 
                                '<h3>❌ Analysis Failed</h3>' +
                                '<p>' + data.error + '</p>';
                        }}
                    }}, 500);
                }} catch (error) {{
                    clearInterval(progressInterval);
                    progress.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result-container result-error';
                    result.innerHTML = '<h3>❌ Error</h3><p>' + error.message + '</p>';
                }}
            }}
            
            function downloadRule() {{
                window.open('/api/download-rule', '_blank');
            }}
            
            async function testAllGoDaddy() {{
                const sites = [
                    'https://pendalepharmacy.ca/',
                    'https://northmedafixcompoundingpharmacy.ca/',
                    'https://centerpharm.ca/',
                    'https://riverviewpharmacy.ca/',
                    'https://nadiasmedicalcentre.ca/',
                    'https://www.midtowncompoundingpharmacy.ca/',
                    'https://abundancespecialtyrx.com/',
                    'https://rxottawa.ca/'
                ];
                await testSiteGroup(sites, 'GoDaddy Group');
            }}
            
            async function testAllCookieYes() {{
                const sites = [
                    'https://eramosapharmacy.ca/',
                    'https://www.westmountmedicalpharmacy.ca/',
                    'https://primecarepharmacy.ca/',
                    'https://www.arkellmedical.ca/'
                ];
                await testSiteGroup(sites, 'CookieYes Group');
            }}
            
            async function testSiteGroup(sites, groupName) {{
                const result = document.getElementById('result');
                result.style.display = 'block';
                result.className = 'result-container';
                result.innerHTML = `<h3>Testing ${{groupName}} (${{sites.length}} sites)</h3><p>Starting tests...</p>`;
                
                let resultsHTML = `<h3>Test Results for ${{groupName}} (${{sites.length}} sites)</h3>`;
                let successCount = 0;
                let failCount = 0;
                
                for (let i = 0; i < sites.length; i++) {{
                    const site = sites[i];
                    resultsHTML += `<hr><h4>${{i + 1}}. ${{site}}</h4>`;
                    resultsHTML += `<div id="site-result-${{i}}">Analyzing...</div>`;
                    result.innerHTML = resultsHTML;
                    
                    try {{
                        const response = await fetch('/api/test', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ url: site }})
                        }});
                        
                        const data = await response.json();
                        const siteDiv = document.getElementById(`site-result-${{i}}`);
                        
                        if (data.success && data.banner_detected && data.rule) {{
                            successCount++;
                            siteDiv.innerHTML = `<p style="color: green;">✅ Banner Detected (Confidence: ${{(data.confidence * 100).toFixed(1)}}%)</p>`;
                        }} else {{
                            failCount++;
                            siteDiv.innerHTML = `<p style="color: red;">❌ ${{data.banner_detected ? 'Banner detected but rule generation failed' : 'No banner detected'}}</p>`;
                        }}
                    }} catch (error) {{
                        failCount++;
                        const siteDiv = document.getElementById(`site-result-${{i}}`);
                        siteDiv.innerHTML = `<p style="color: red;">❌ Error: ${{error.message}}</p>`;
                    }}
                    
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }}
                
                resultsHTML += `<hr><h3>Summary: ${{successCount}} successful, ${{failCount}} failed</h3>`;
                result.innerHTML = resultsHTML;
            }}
            
            function handleFileSelect(event) {{
                const file = event.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('file', file);
                
                const uploadResult = document.getElementById('upload-result');
                uploadResult.innerHTML = '<p>Uploading and processing file...</p>';
                
                fetch('/api/upload', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        extractedUrls = data.urls;
                        const urlCount = extractedUrls.length;
                        uploadResult.innerHTML = '<p style="color: green;">✅ File processed successfully! Found ' + urlCount + ' URLs.</p>';
                        
                        const urlsList = document.getElementById('urls-list');
                        urlsList.innerHTML = extractedUrls.map(function(url, i) {{
                            return '<div style="padding: 8px; border-bottom: 1px solid #e9ecef;">' + (i + 1) + '. ' + url + '</div>';
                        }}).join('');
                        
                        document.getElementById('extracted-urls').style.display = 'block';
                    }} else {{
                        uploadResult.innerHTML = '<p style="color: red;">❌ Error: ' + data.error + '</p>';
                    }}
                }})
                .catch(error => {{
                    uploadResult.innerHTML = '<p style="color: red;">❌ Error: ' + error.message + '</p>';
                }});
            }}
            
            function useUrlsForMassTest() {{
                document.getElementById('mass-urls').value = extractedUrls.join('\\n');
                const massTestTab = document.querySelector('button.tab[onclick*="mass-test"]');
                if (massTestTab) {{
                    switchTab('mass-test', massTestTab);
                }}
            }}
            
            function loadRulesCheckboxes() {{
                const container = document.getElementById('rules-list-checkboxes');
                container.innerHTML = allRules.map(function(rule, i) {{
                    return '<label style="display: block; margin: 10px 0;">' +
                           '<input type="checkbox" class="rule-checkbox" value="' + i + '" checked> ' +
                           rule.filename + ' - ' + rule.site +
                           '</label>';
                }}).join('');
            }}
            
            function toggleAllRules() {{
                const checkAll = document.getElementById('test-all-rules').checked;
                document.querySelectorAll('.rule-checkbox').forEach(function(cb) {{
                    cb.checked = checkAll;
                }});
            }}
            
            async function startMassTest() {{
                const urlsText = document.getElementById('mass-urls').value;
                const urls = urlsText.split('\\n').filter(function(url) {{ return url.trim(); }});
                
                if (urls.length === 0) {{
                    alert('Please enter at least one URL');
                    return;
                }}
                
                const selectedRules = Array.from(document.querySelectorAll('.rule-checkbox:checked')).map(function(cb) {{ return parseInt(cb.value); }});
                
                if (selectedRules.length === 0) {{
                    alert('Please select at least one rule to test');
                    return;
                }}
                
                const resultsDiv = document.getElementById('mass-test-results');
                resultsDiv.innerHTML = '<h3>Starting mass test...</h3><p>This may take a while...</p>';
                
                // Implementation would go here - for now just show a message
                const urlCount = urls.length;
                const ruleCount = selectedRules.length;
                resultsDiv.innerHTML = 
                    '<h3>Mass Testing Results</h3>' +
                    '<p>Testing ' + urlCount + ' URLs against ' + ruleCount + ' rules...</p>' +
                    '<p style="color: #666;">Mass testing functionality is being implemented. For now, use the "Analyze Banner" tab for individual testing.</p>';
            }}
            
            async function testAllPharmacySites() {{
                const pharmacySites = [
                    {{name: 'Pendale Pharmacy', url: 'https://pendalepharmacy.ca/'}},
                    {{name: 'North Medafix', url: 'https://northmedafixcompoundingpharmacy.ca/'}},
                    {{name: 'CenterPharm', url: 'https://centerpharm.ca/'}},
                    {{name: 'Riverview Pharmacy', url: 'https://riverviewpharmacy.ca/'}},
                    {{name: 'Nadia\'s Medical', url: 'https://nadiasmedicalcentre.ca/'}},
                    {{name: 'Midtown Pharmacy', url: 'https://www.midtowncompoundingpharmacy.ca/'}},
                    {{name: 'Abundance Specialty', url: 'https://abundancespecialtyrx.com/'}},
                    {{name: 'Rx Ottawa', url: 'https://rxottawa.ca/'}},
                    {{name: 'Eramosa Pharmacy', url: 'https://eramosapharmacy.ca/'}},
                    {{name: 'Westmount Medical', url: 'https://www.westmountmedicalpharmacy.ca/'}},
                    {{name: 'Prime Care', url: 'https://primecarepharmacy.ca/'}},
                    {{name: 'Arkell Medical', url: 'https://www.arkellmedical.ca/'}},
                    {{name: 'Margis Pharmacy', url: 'https://www.margispharmacy.com/'}},
                    {{name: 'BlendRx', url: 'https://blendrx.ca/'}},
                    {{name: 'Fresenius Kabi', url: 'https://www.fresenius-kabi.com/en-ca/'}}
                ];
                
                const progressDiv = document.getElementById('pharmacy-progress');
                const progressFill = document.getElementById('pharmacy-progress-fill');
                const progressText = document.getElementById('pharmacy-progress-text');
                const progressStatus = document.getElementById('pharmacy-progress-status');
                const resultsDiv = document.getElementById('pharmacy-results');
                
                progressDiv.style.display = 'block';
                resultsDiv.innerHTML = '';
                
                let results = [];
                let cmpGroups = {{}};
                
                for (let i = 0; i < pharmacySites.length; i++) {{
                    const site = pharmacySites[i];
                    const progress = Math.round(((i + 1) / pharmacySites.length) * 100);
                    
                    progressFill.style.width = progress + '%';
                    progressFill.textContent = progress + '%';
                    progressText.textContent = 'Testing site ' + (i + 1) + ' of ' + pharmacySites.length;
                    progressStatus.textContent = 'Analyzing: ' + site.name + '...';
                    
                    try {{
                        const response = await fetch('/api/test', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ url: site.url }})
                        }});
                        
                        const data = await response.json();
                        
                        const cmpType = data.cmp_type || 'Unknown';
                        const cmpDisplayName = formatCMPName(cmpType);
                        
                        if (!cmpGroups[cmpType]) {{
                            cmpGroups[cmpType] = [];
                        }}
                        
                        cmpGroups[cmpType].push({{
                            name: site.name,
                            url: site.url,
                            banner_detected: data.banner_detected || false,
                            confidence: data.confidence || 0,
                            cmp_type: cmpType,
                            cmp_display_name: cmpDisplayName,
                            error: data.error || null
                        }});
                        
                        results.push({{
                            name: site.name,
                            url: site.url,
                            banner_detected: data.banner_detected || false,
                            confidence: data.confidence || 0,
                            cmp_type: cmpType,
                            cmp_display_name: cmpDisplayName,
                            error: data.error || null
                        }});
                    }} catch (error) {{
                        if (!cmpGroups['Error']) {{
                            cmpGroups['Error'] = [];
                        }}
                        cmpGroups['Error'].push({{
                            name: site.name,
                            url: site.url,
                            banner_detected: false,
                            confidence: 0,
                            cmp_type: 'Error',
                            cmp_display_name: 'Error',
                            error: error.message
                        }});
                        results.push({{
                            name: site.name,
                            url: site.url,
                            banner_detected: false,
                            confidence: 0,
                            cmp_type: 'Error',
                            cmp_display_name: 'Error',
                            error: error.message
                        }});
                    }}
                    
                    // Small delay between requests
                    await new Promise(resolve => setTimeout(resolve, 500));
                }}
                
                progressFill.style.width = '100%';
                progressFill.textContent = '100%';
                progressText.textContent = 'Complete!';
                progressStatus.textContent = 'All sites tested';
                
                // Display results grouped by CMP type
                displayPharmacyResults(results, cmpGroups);
            }}
            
            function formatCMPName(cmpType) {{
                const cmpNames = {{
                    'godaddy': 'GoDaddy Website Builder',
                    'cookieyes': 'CookieYes',
                    'onetrust': 'OneTrust',
                    'cookiebot': 'Cookiebot',
                    'consentmanager': 'ConsentManager',
                    'tarteaucitron': 'TarteAuCitron',
                    'cookieinformation': 'Cookie Information',
                    'custom_wordpress': 'Custom WordPress',
                    'shopify': 'Shopify',
                    'custom_generic': 'Custom Generic',
                    'Unknown': 'Unknown',
                    'Error': 'Error'
                }};
                return cmpNames[cmpType] || cmpType;
            }}
            
            function displayPharmacyResults(results, cmpGroups) {{
                const resultsDiv = document.getElementById('pharmacy-results');
                
                let html = '<h2>📊 CMP Detection Results</h2>';
                html += '<p style="color: #666; margin-bottom: 20px;">Tested ' + results.length + ' pharmacy sites</p>';
                
                // Summary statistics
                const totalSites = results.length;
                const sitesWithBanners = results.filter(function(r) {{ return r.banner_detected; }}).length;
                const uniqueCMPs = Object.keys(cmpGroups).length;
                
                html += 
                    '<div class="stats-grid" style="margin-bottom: 30px;">' +
                        '<div class="stat-card">' +
                            '<h3>' + totalSites + '</h3>' +
                            '<p>Total Sites</p>' +
                        '</div>' +
                        '<div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">' +
                            '<h3>' + sitesWithBanners + '</h3>' +
                            '<p>Sites with Banners</p>' +
                        '</div>' +
                        '<div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">' +
                            '<h3>' + uniqueCMPs + '</h3>' +
                            '<p>CMP Groups Found</p>' +
                        '</div>' +
                    '</div>';
                
                // Group results by CMP type
                html += '<h3 style="margin-top: 30px; margin-bottom: 20px;">Results by CMP Group</h3>';
                
                // Sort CMP groups by number of sites
                const sortedGroups = Object.entries(cmpGroups).sort(function(a, b) {{ return b[1].length - a[1].length; }});
                
                for (const [cmpType, sites] of sortedGroups) {{
                    const cmpDisplayName = formatCMPName(cmpType);
                    const cmpColor = getCMPColor(cmpType);
                    
                    const cmpIcon = getCMPIcon(cmpType);
                    html += '<div style="margin-bottom: 30px; border: 2px solid ' + cmpColor + '; border-radius: 12px; padding: 20px; background: #f8f9fa;">' +
                            '<h4 style="color: ' + cmpColor + '; margin-top: 0; font-size: 20px;">' +
                                cmpIcon + ' ' + cmpDisplayName + ' (' + sites.length + ' sites)' +
                            '</h4>' +
                            '<table class="test-results-table" style="width: 100%; margin-top: 15px;">' +
                                '<thead>' +
                                    '<tr>' +
                                        '<th>Site Name</th>' +
                                        '<th>URL</th>' +
                                        '<th>Banner Detected</th>' +
                                        '<th>Confidence</th>' +
                                        '<th>Status</th>' +
                                    '</tr>' +
                                '</thead>' +
                                '<tbody>';
                    
                    for (const site of sites) {{
                        const statusBadge = site.banner_detected 
                            ? '<span class="status-badge status-success">✅ Detected</span>'
                            : site.error
                            ? '<span class="status-badge status-error">❌ Error</span>'
                            : '<span class="status-badge status-warning">⚠️ No Banner</span>';
                        
                        const confidenceText = site.confidence > 0 
                            ? (site.confidence * 100).toFixed(1) + '%'
                            : 'N/A';
                        
                        const bannerText = site.banner_detected ? 'Yes' : 'No';
                        
                        html += '<tr>' +
                                '<td><strong>' + site.name + '</strong></td>' +
                                '<td><a href="' + site.url + '" target="_blank" style="color: #667eea;">' + site.url + '</a></td>' +
                                '<td>' + bannerText + '</td>' +
                                '<td>' + confidenceText + '</td>' +
                                '<td>' + statusBadge + '</td>' +
                            '</tr>';
                    }}
                    
                    html += '</tbody>' +
                            '</table>' +
                        '</div>';
                }}
                
                resultsDiv.innerHTML = html;
            }}
            
            function getCMPColor(cmpType) {{
                const colors = {{
                    'godaddy': '#17a2b8',
                    'cookieyes': '#ffc107',
                    'onetrust': '#007bff',
                    'cookiebot': '#28a745',
                    'consentmanager': '#6f42c1',
                    'tarteaucitron': '#fd7e14',
                    'cookieinformation': '#20c997',
                    'custom_wordpress': '#6c757d',
                    'shopify': '#95bf47',
                    'custom_generic': '#dc3545',
                    'Unknown': '#6c757d',
                    'Error': '#dc3545'
                }};
                return colors[cmpType] || '#667eea';
            }}
            
            function getCMPIcon(cmpType) {{
                const icons = {{
                    'godaddy': '🟢',
                    'cookieyes': '🟡',
                    'onetrust': '🔵',
                    'cookiebot': '🟢',
                    'consentmanager': '🟣',
                    'tarteaucitron': '🟠',
                    'cookieinformation': '🟢',
                    'custom_wordpress': '⚫',
                    'shopify': '🟢',
                    'custom_generic': '🔴',
                    'Unknown': '⚪',
                    'Error': '❌'
                }};
                return icons[cmpType] || '❓';
            }}
        </script>
    </body>
    </html>
    '''

def generate_rules_html(rules):
    """Generate HTML for rules list."""
    if not rules:
        return '<p>No rules found. Generate some rules first!</p>'
    
    html = ''
    for rule in rules:
        site = rule.get('site', 'Unknown Site')
        filename = rule.get('filename', 'unknown.json')
        detectors = rule.get('detectors', [])
        methods = rule.get('methods', [])
        
        html += f'''
        <div class="rule-card">
            <h4>{site}</h4>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Detectors:</strong> {len(detectors) if isinstance(detectors, list) else 'N/A'}</p>
            <p><strong>Methods:</strong> {len(methods) if isinstance(methods, list) else 'N/A'}</p>
            <button class="btn btn-secondary" onclick="viewRule('{filename}')" style="margin-top: 10px; width: 100%;">View Rule</button>
        </div>
        '''
    
    return html

@app.route('/api/test', methods=['POST'])
def test():
    """Test a single URL for consent banners."""
    data = request.get_json()
    url = data.get('url', '')
    
    try:
        from src.collectors.web_scraper import WebScraper
        from src.detectors.banner_detector import BannerDetector
        from src.generators.rule_generator import RuleGenerator
        
        with WebScraper(headless=True, timeout=30) as scraper:
            page_data = scraper.collect_page(url)
        
        if not page_data or not page_data.html_content:
            return jsonify({
                'success': False,
                'error': 'Failed to collect page data',
                'url': url
            })
        
        detector = BannerDetector()
        banner_info = detector.detect_banner(page_data)
        
        # Get CMP type from banner info or detect it separately
        cmp_type = 'Unknown'
        if banner_info:
            cmp_type = getattr(banner_info, 'cmp_type', 'Unknown')
            if cmp_type == 'Unknown' or not cmp_type:
                # Try to detect CMP type even if banner not detected
                from src.detectors.cmp_fingerprinter import CMPFingerprinter
                fingerprinter = CMPFingerprinter()
                cmp_type, cmp_confidence, cmp_indicators = fingerprinter.identify_cmp_type(page_data)
        
        # If no banner detected, still try to identify CMP type
        if not banner_info:
            from src.detectors.cmp_fingerprinter import CMPFingerprinter
            fingerprinter = CMPFingerprinter()
            cmp_type, cmp_confidence, cmp_indicators = fingerprinter.identify_cmp_type(page_data)
        
        if banner_info:
            generator = RuleGenerator()
            rule = generator.generate_consent_o_matic_json(banner_info)
            
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
                'cmp_type': cmp_type,
                'url': url
            })
        else:
            return jsonify({
                'success': True,
                'banner_detected': False,
                'message': 'No consent banner detected',
                'cmp_type': cmp_type,
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
    
    site_name = current_rule.get('site', 'consent_rule')
    filename = site_name.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '_')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(current_rule, f, indent=2)
        temp_path = f.name
    
    return send_file(
        temp_path,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{filename}_rule.json'
    )

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle Excel/CSV file upload and extract URLs."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload .xlsx, .xls, or .csv'}), 400
    
    try:
        if not PANDAS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'pandas is not installed. Please install it with: pip install pandas openpyxl'
            }), 500
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read the file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Extract URLs - try different column names
        urls = []
        for col in df.columns:
            if 'url' in col.lower() or col.lower() == 'url':
                urls = df[col].dropna().astype(str).tolist()
                break
        
        # If no URL column found, use first column
        if not urls:
            urls = df.iloc[:, 0].dropna().astype(str).tolist()
        
        # Filter to valid URLs
        urls = [url for url in urls if url.startswith('http://') or url.startswith('https://')]
        
        # Clean up file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'urls': urls,
            'count': len(urls)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rules')
def get_rules():
    """Get all available rules."""
    rules = load_rules_from_directory()
    return jsonify({'success': True, 'rules': rules})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Use 127.0.0.1 for local development, 0.0.0.0 for cloud deployment
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"Starting CMP Mapper Pro on {host}:{port}...")
    print(f"Open: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        app.run(debug=False, port=port, host=host)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

