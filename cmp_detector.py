#!/usr/bin/env python3
"""
Simple CMP Detector - Clean prototype for detecting cookie banner/CMP types
"""

from flask import Flask, render_template_string, request, jsonify
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.detectors.cmp_fingerprinter import CMPFingerprinter
from src.collectors.web_scraper import WebScraper

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMP Detector - Find Cookie Banner Types</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result {
            margin-top: 30px;
            padding: 25px;
            border-radius: 12px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
        }
        
        .result.error {
            background: #f8d7da;
            border: 2px solid #dc3545;
            color: #721c24;
        }
        
        .result.warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            color: #856404;
        }
        
        .cmp-name {
            font-size: 2em;
            font-weight: bold;
            margin: 15px 0;
            color: #667eea;
        }
        
        .confidence {
            font-size: 1.2em;
            margin: 10px 0;
        }
        
        .indicators {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        
        .indicator {
            padding: 8px 12px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 6px;
            margin: 5px 0;
            font-size: 0.9em;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-size: 1.1em;
        }
        
        .quick-links {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #e9ecef;
        }
        
        .quick-links h3 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .quick-link {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            color: #495057;
        }
        
        .quick-link:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍪 CMP Detector</h1>
        <p class="subtitle">Detect Cookie Banner / Consent Management Platform Types</p>
        
        <div class="input-group">
            <label for="url">Website URL</label>
            <input type="text" id="url" placeholder="https://www.example.com" value="">
        </div>
        
        <button class="btn" onclick="detectCMP()">🔍 Detect CMP Type</button>
        
        <div class="loading" id="loading">Analyzing website...</div>
        
        <div class="result" id="result"></div>
        
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 12px;">
            <h3>🚀 Test All Sites & Group by CMP</h3>
            <p style="color: #666; margin-bottom: 15px;">Test all websites and automatically group them by CMP type</p>
            <button class="btn" onclick="testAllSites()" style="width: 100%; margin-bottom: 15px;">🔍 Test All Sites & Group by CMP</button>
            <div id="all-sites-progress" style="display: none; margin-top: 20px;">
                <div style="background: #e9ecef; height: 30px; border-radius: 15px; overflow: hidden; position: relative;">
                    <div id="progress-bar" style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: 0%; transition: width 0.3s; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;"></div>
                </div>
                <p id="progress-text" style="text-align: center; margin-top: 10px; color: #666;"></p>
            </div>
            <div id="all-sites-results" style="margin-top: 30px;"></div>
        </div>
        
        <div class="quick-links" style="margin-top: 30px;">
            <h3>Quick Test Individual Sites</h3>
            <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">{{total_sites}} total sites available. Use "Test All Sites" button above to group them by CMP type.</p>
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                <p style="color: #666; margin: 0;">💡 Tip: Use the "Test All Sites & Group by CMP" button to automatically test and group all {{total_sites}} sites by their CMP type.</p>
            </div>
        </div>
    </div>
    
    <script>
        function loadUrl(url) {
            document.getElementById('url').value = url;
        }
        
        async function detectCMP() {
            const url = document.getElementById('url').value.trim();
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/api/detect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.success) {
                    const cmpName = data.cmp_type || 'Unknown';
                    const confidence = (data.confidence * 100).toFixed(1);
                    const indicators = data.indicators || [];
                    
                    let indicatorsHtml = '';
                    if (indicators.length > 0) {
                        indicatorsHtml = '<div class="indicators"><strong>Detection Indicators:</strong>';
                        indicators.forEach(function(ind) {
                            indicatorsHtml += '<div class="indicator">' + ind + '</div>';
                        });
                        indicatorsHtml += '</div>';
                    }
                    
                    result.className = 'result success';
                    result.innerHTML = 
                        '<h2>✅ CMP Detected!</h2>' +
                        '<div class="cmp-name">' + cmpName + '</div>' +
                        '<div class="confidence">Confidence: ' + confidence + '%</div>' +
                        '<p><strong>URL:</strong> ' + data.url + '</p>' +
                        indicatorsHtml;
                } else {
                    result.className = 'result warning';
                    result.innerHTML = 
                        '<h2>⚠️ No CMP Detected</h2>' +
                        '<p>' + (data.message || 'No cookie consent banner or CMP detected on this website.') + '</p>' +
                        '<p><strong>URL:</strong> ' + data.url + '</p>';
                }
            } catch (error) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.className = 'result error';
                result.innerHTML = 
                    '<h2>❌ Error</h2>' +
                    '<p>Failed to analyze website: ' + error.message + '</p>';
            }
        }
        
        // All sites to test - loaded from API
        let allSites = [];
        
        // Load sites on page load
        async function loadSites() {
            try {
                const response = await fetch('/api/sites');
                const data = await response.json();
                allSites = data.sites || [];
                console.log('Loaded', allSites.length, 'sites');
            } catch (error) {
                console.error('Failed to load sites:', error);
                alert('Failed to load sites list. Please refresh the page.');
            }
        }
        
        // Load sites when page loads
        window.addEventListener('DOMContentLoaded', loadSites);
        
        async function testAllSites() {
            const progressDiv = document.getElementById('all-sites-progress');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const resultsDiv = document.getElementById('all-sites-results');
            
            // Load sites if not already loaded
            if (!allSites || allSites.length === 0) {
                await loadSites();
            }
            
            if (!allSites || allSites.length === 0) {
                alert('Sites list not loaded. Please refresh the page.');
                return;
            }
            
            progressDiv.style.display = 'block';
            resultsDiv.innerHTML = '';
            
            const results = [];
            const cmpGroups = {};
            
            for (let i = 0; i < allSites.length; i++) {
                const url = allSites[i];
                const progress = Math.round(((i + 1) / allSites.length) * 100);
                
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';
                progressText.textContent = 'Testing site ' + (i + 1) + ' of ' + allSites.length + ': ' + url;
                
                try {
                    const response = await fetch('/api/detect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    const cmpType = data.cmp_type_key || 'Unknown';
                    const cmpName = data.cmp_type || 'Unknown';
                    
                    if (!cmpGroups[cmpType]) {
                        cmpGroups[cmpType] = [];
                    }
                    
                    cmpGroups[cmpType].push({
                        url: url,
                        cmp_name: cmpName,
                        confidence: data.confidence || 0,
                        success: data.success || false
                    });
                    
                    results.push({
                        url: url,
                        cmp_type: cmpType,
                        cmp_name: cmpName,
                        confidence: data.confidence || 0,
                        success: data.success || false
                    });
                } catch (error) {
                    if (!cmpGroups['Error']) {
                        cmpGroups['Error'] = [];
                    }
                    cmpGroups['Error'].push({
                        url: url,
                        cmp_name: 'Error',
                        confidence: 0,
                        success: false,
                        error: error.message
                    });
                }
                
                // Small delay between requests
                await new Promise(function(resolve) { setTimeout(resolve, 500); });
            }
            
            progressBar.style.width = '100%';
            progressBar.textContent = '100%';
            progressText.textContent = 'Complete!';
            
            // Display grouped results
            displayGroupedResults(cmpGroups, results);
        }
        
        function displayGroupedResults(cmpGroups, results) {
            const resultsDiv = document.getElementById('all-sites-results');
            
            let html = '<h2 style="margin-bottom: 20px;">📊 CMP Grouping Results</h2>';
            html += '<p style="color: #666; margin-bottom: 20px;">Total sites tested: ' + results.length + '</p>';
            
            // Summary stats
            const totalSites = results.length;
            const sitesWithCMP = results.filter(function(r) { return r.success && r.cmp_type !== 'Unknown'; }).length;
            const uniqueCMPs = Object.keys(cmpGroups).filter(function(k) { return k !== 'Error' && k !== 'Unknown'; }).length;
            
            html += '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">';
            html += '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;"><h3 style="margin: 0; color: #667eea;">' + totalSites + '</h3><p style="margin: 5px 0 0 0; color: #666;">Total Sites</p></div>';
            html += '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;"><h3 style="margin: 0; color: #28a745;">' + sitesWithCMP + '</h3><p style="margin: 5px 0 0 0; color: #666;">Sites with CMP</p></div>';
            html += '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;"><h3 style="margin: 0; color: #ffc107;">' + uniqueCMPs + '</h3><p style="margin: 5px 0 0 0; color: #666;">CMP Groups</p></div>';
            html += '</div>';
            
            // Group by CMP type
            html += '<h3 style="margin-top: 30px; margin-bottom: 20px;">Results by CMP Group</h3>';
            
            // Sort groups by size
            const sortedGroups = Object.entries(cmpGroups).sort(function(a, b) {
                return b[1].length - a[1].length;
            });
            
            sortedGroups.forEach(function(entry) {
                const cmpType = entry[0];
                const sites = entry[1];
                
                const cmpColors = {
                    'godaddy': '#17a2b8',
                    'cookieyes': '#ffc107',
                    'onetrust': '#007bff',
                    'cookiebot': '#28a745',
                    'Unknown': '#6c757d',
                    'Error': '#dc3545'
                };
                
                const color = cmpColors[cmpType] || '#667eea';
                
                html += '<div style="margin-bottom: 30px; border: 2px solid ' + color + '; border-radius: 12px; padding: 20px; background: #f8f9fa;">';
                html += '<h4 style="color: ' + color + '; margin-top: 0; font-size: 20px;">' + sites[0].cmp_name + ' (' + sites.length + ' sites)</h4>';
                html += '<div style="max-height: 300px; overflow-y: auto;">';
                html += '<table style="width: 100%; border-collapse: collapse;">';
                html += '<thead><tr style="background: white;"><th style="padding: 10px; text-align: left; border-bottom: 2px solid #e9ecef;">URL</th><th style="padding: 10px; text-align: left; border-bottom: 2px solid #e9ecef;">Confidence</th><th style="padding: 10px; text-align: left; border-bottom: 2px solid #e9ecef;">Status</th></tr></thead>';
                html += '<tbody>';
                
                sites.forEach(function(site) {
                    const confidenceText = site.confidence > 0 ? (site.confidence * 100).toFixed(1) + '%' : 'N/A';
                    const statusBadge = site.success ? '<span style="background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-size: 12px;">✅ Detected</span>' : '<span style="background: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-size: 12px;">❌ Error</span>';
                    html += '<tr><td style="padding: 8px; border-bottom: 1px solid #e9ecef;"><a href="' + site.url + '" target="_blank" style="color: #667eea;">' + site.url + '</a></td><td style="padding: 8px; border-bottom: 1px solid #e9ecef;">' + confidenceText + '</td><td style="padding: 8px; border-bottom: 1px solid #e9ecef;">' + statusBadge + '</td></tr>';
                });
                
                html += '</tbody></table>';
                html += '</div>';
                html += '</div>';
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
'''

# All pharmacy websites to test
ALL_SITES = [
    'https://pharmasavebarriedowntown.com',
    'https://www.loblaws.ca/pharmacy',
    'https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/big-bay-point-guardian-pharmacy-7015555',
    'https://barriewalkinclinic.ca/pharmacy/',
    'https://www.carerx.ca/welcome/',
    'https://canatp.ca/catp-barrie/',
    'https://costcopharmacy.ca/',
    'https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/craighurst-pharmacy-7044700',
    'https://pharmasave.com/barrie-cundles/',
    'https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/dunlop-pharmacy-7056000',
    'https://ferndalepharmacy.ca/',
    'https://www.foodbasics.ca/services/pharmacy',
    'https://grovestpharmacy.ca/',
    'https://www.innomar-strategies.com/',
    'https://www.letitiapharmacy.com/',
    'https://www.pharmachoice.com/locations/little-avenue-pharmacy/',
    'https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/little-lake-pharmacy-7016243',
    'https://www.lmc.ca/locations/lmc-barrie/',
    'https://www.mapleviewpharmacy.com/',
    'https://pharmasave.com/barrie-marsellus-drive/',
    'https://www.medisystempharmacy.com/',
    'https://newlifefamilypharm.wixsite.com/newlife',
    'https://www.peritusmedical.ca/',
    'https://pharmarightbarrie.ca/',
    'https://pharmasave.com/store/pharmasave-allandale/',
    'https://pharmasavesimcoe.com/',
    'https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/primary-care-pharmacy-7022839',
    'https://pharmasave.com/barrie-prince-william/',
    'https://www.procarepharmacy.ca/',
    'https://prohealthbarrie.com/7057921414',
    'https://purehealthpharmacy.com/',
    'https://www.rexall.ca/storelocator/store/1388/',
    'https://pharmasave.com/store/pharmasave-royal-medical/',
    'https://www.rvh.on.ca/',
    'https://shoppersdrugmart.ca',
    'https://sobeyspharmacy.com/stores/barriemolson-park/',
    'https://truemedica.ca/',
    'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183',
    'https://www.1clinic.ca/index.php',
    'https://beyondrx.ca/',
    'https://afiyapainclinictoronto.com/',
    'https://sunnybrook.ca/content/?page=care-serv-ambul-pharm',
    'https://www.pharmachoice.com/locations/apex-compounding-pharmacy/',
    'https://apollonpharmacy.com/',
    'https://apothecapharmacy.ca/',
    'https://www.ascendpharmacy.ca/',
    'https://avapharmacy.ca/',
    'https://pharmasave.com/store/pharmasave-balmoral/',
    'https://bathurstpharmacy.ca/',
    'https://pharmasave.com/toronto-beaches/',
    'https://www.blaircourtpharmacy.com/',
    'https://www.bookmypharmacy.com/4169770970',
    'https://www.bloorstpharmacy.com/',
    'https://bloordale.pharmabest.ca/',
    'https://blueskypharmacy.ca/',
    'https://brimleymedical.ca/brmc-ida-pharmacy/',
    'https://www.cabbagetownpharmacy.com/',
    'https://www.camh.ca/',
    'https://pharmasave.com/toronto-leslieville/',
    'https://caseyhouse.ca/',
    'https://pharmacy.ca/?v=3e8d115eb4b3',
    'https://www.citylifepharmacy.com/',
    'https://citypharmacy.ca/',
    'https://pharmasave.com/toronto-fort-york/',
    'https://cloudpharmacy.ca/',
    'https://pharmasave.com/toronto-community-choice/',
    'https://www.cwhealth.ca/pharmacy',
    'https://dalespharmacy.ca/',
    'https://www.thedanforthpharmacy.com/',
    'https://davisvilleguardianpharmacy.ca/',
    'https://www.deerparkcompound.com.au/',
    'https://demarcopharmacy.com/',
    'https://www.discoverypharmacy.utoronto.ca/',
    'https://www.donrusselldrugmart.ca/',
    'https://donvalleypharma.com/',
    'https://www.villageofislington.com/business/dunbloor-medical-pharmacy-and-walk-in-clinic/',
    'https://eastlibertyvillagepharmacy.ca/',
    'https://www.dynastypharmacy.ca/',
    'https://eglintonbathurstpharmacy.ca/4167878281',
    'https://emergepharmacy.com/',
    'https://emeryvillagepharmacy.com/',
    'https://everestpharmacy.ca/',
    'https://www.familycareonking.com/',
    'https://fortyorkmedical.com/pharmacy/',
    'https://freshco.com/pharmacy/',
    'https://westkingpharmacy.com/4162484485',
    'https://geriatrx.com/',
    'https://www.getwellrx.ca/',
    'https://www.glengrovepharmacy.com/',
    'https://medcab.ca/',
    'https://hcmpharmacy.pharmabest.ca/',
    'https://www.healthshield.ca/compounding/',
    'https://www.medspharmacy.ca/high-park-pharmacy',
    'https://hoopershealth.com/',
    'https://www.remedyrxjamestownpharmacy.com/',
    'https://www.jarvis-st-apothecary.com/',
    'https://johnjackpharmacy.ca/',
    'https://www.junctionchemist.com/',
    'https://www.kasselspharmacy.com/',
    'https://kingswaydrugs.weebly.com/contact-us.html',
    'https://libertymarketpharmacy.com/contact/',
    'https://www.lmc.ca/',
    'https://lordspharmacy.net/',
    'https://mapleleafmedicalpharmacy.com/',
    'https://www.margispharmacy.com/',
    'https://www.markiepharmacy.com/',
    'https://www.mediplacepharmacy.com/',
    'https://medicaredrugmart.ca/',
    'https://www.medionerx.com/pharmacy/',
    'https://medishop.ca/',
    'https://mednow.ca/',
    'https://www.medsexpert.ca/',
    'https://metropolitanpharmacy.ca/',
    'https://www.midtowncompoundingpharmacy.ca/',
    'https://misterpharmacist.com/',
    'https://morellispharmacy.ca/',
    'https://mortarpestle.ca/',
    'https://mountsinaifertility.com/',
    'http://www.multicarepharmacy.ca/',
    'https://onemedicalpharmacy.weebly.com/',
    'https://www.prepclinic.ca/',
    'https://pacepharmacy.com/',
    'http://parkdalepharmacy.ca/',
    'https://pharmacaredrugmart.square.site/',
    'https://pharmacygo.com/',
    'https://unityhealth.to/locations/st-michaels-hospital/',
    'https://www.uhn.ca/PrincessMargaret/',
    'https://www.procare-pharmacy.ca/',
    'https://www.prohealthpharmacy.ca/',
    'https://unityhealth.to/locations/providence-healthcare/',
    'https://queeneastpharmacy.ca/',
    'https://www.radiantpharmacy.ca/',
    'http://www.raxlenpharmacy.com/',
    'https://regalhpharmacy.com/',
    'https://rosedalefamilydentalcare.com/',
    'https://runnymedehc.ca/',
    'https://rxcrew.ca/',
    'https://www.sagepharmacyrx.ca/',
    'https://www.torontograce.org/',
    'https://www.seatonpharmacy.ca/',
    'https://unityhealth.to/locations/st-josephs-health-centre/',
    'https://sunnysidepharmacy.ca/contact-us/',
    'https://www.symingtonpharmacy.ca/',
    'https://new.healingsourcepharmacy.ca/',
    'https://www.sickkids.ca/',
    'https://www.medicineshoppe.ca/',
    'https://www.thepharmacylab.ca/',
    'https://www.thevillagepharmacy.ca/',
    'https://timspharmacy.ca/contact/',
    'https://torontowellnessrx.com/',
    'https://treasuryhealth.ca/',
    'https://www.trinitydrugstore.ca/contact.html',
    'https://twigfertility.com/',
    'https://urbancarepharmacy.ca/',
    'https://victorpharmacy.com/',
    'https://myvivapharmacy.com/',
    'https://www.wellmedica.ca/',
    'https://www.westpark.org/',
    'https://whitespharmacy.ca/',
    'https://mywhpharmacy.ca/',
    'https://www.womenscollegehospital.ca/',
    'http://apothesospharmacy.ca/',
    'https://beechwoodpharmacy.com/',
    'https://bellpharmacy.ca/',
    'https://www.cheo.on.ca/en/index.aspx',
    'https://frangian.com/donald-st-pharmacy/',
    'https://www.bruyere.org/en/s-elisabeth-bruyere-hospital',
    'https://extendpharmacy.com/',
    'http://www.findlaycreekpharmacy.ca/contact-us.html',
    'https://www.firstcarepharmacy.ca/',
    'https://www.gvpharmacy.com/',
    'https://hopitalmontfort.com/en/corp/hospital-contact-information',
    'https://huntclubpharmacy.ca/index.php/contact-us',
    'https://www.idameadowlands.ca/',
    'https://medical-arts.ca/',
    'https://www.nkshealth.ca/',
    'https://nutrichem.com/',
    'https://rxottawa.ca/',
    'https://pharmaciebrisson.ca/',
    'https://campuspharmacy.com/6135634000',
    'https://prestonmed.ca/',
    'https://pharmacypromed.com/',
    'https://www.respectrx.ca/',
    'https://www.restorepharmacy.ca/',
    'https://www.theroyal.ca/',
    'https://www.bruyere.org/en/s-saint-vincent-hospital',
    'https://www.shaspharmacy.com/',
    'https://stlaurentpharmacy.ca/',
    'https://www.ottawahospital.on.ca/en/',
    'http://www.prescriptionshop.ca/rxshop/',
    'https://www.ottawaheart.ca/',
    'https://www.trinityrx.ca/',
    'https://www.victoriaparkpharmacy.com/',
    'https://www.watsonspharma.com/',
    'https://wellingtondrugstore.wixsite.com/website',
    'https://whitecrossdispensary.com/',
    'https://wholehealthglebe.com/',
    'https://www.woodroffepharmacy.ca/',
    'https://www.arkellmedical.ca/',
    'https://chancellorswaypharmacy.com/',
    'https://www.chironcompounding.com/',
    'https://www.eramosapharmacy.ca/',
    'https://pharmasavegordonpharmacy.com/',
    'https://greengatemedical.ca/pharmacy/',
    'https://guelphchc.ca/',
    'https://www.gghorg.ca/',
    'https://guelphmedicalplacepharmacy.com/',
    'https://homewoodhealthcentre.com/',
    'https://norfolkpharmacyandsurgical.ca/',
    'https://primecarepharmacy.ca/',
    'https://royalcitypharmacy.com/',
    'https://www.sjhcg.ca/',
    'https://surreystreetmedical.com/',
    'https://ucpharmacy.ca/5197637773',
    'https://www.westmountmedicalpharmacy.ca/',
    'https://www.willowpharmacy.ca/',
    'https://www.woodlawnpharmacy.com/contact',
    'https://wyndhammedicalpharmacy.com/contact.html',
    'https://abundancespecialtyrx.ca/',
    'https://bartonmedicalcenter.ca/',
    'https://www.calea.ca/en/',
    'https://www.hamiltonhealthsciences.ca/about-us/our-organization/our-locations/juravinski-cancer-centre/',
    'https://centennial.princerx.ca/',
    'http://charltonhealthcare.com/contact/',
    'https://eastsidemedicalclinic.com/',
    'https://www.glenviewpharmacy.ca/',
    'https://www.hamiltoncommunityhealthcentre.ca/on-site-services.php',
    'https://www.hausershealthcare.com/',
    'https://www.huntermedicalclinic.com/pharmacy.html',
    'https://healingrx.princerx.ca/',
    'https://www.hamiltonfht.ca/en/index.aspx',
    'https://hessvillagepharmacy.wixsite.com/mysite',
    'https://joyofheartspharmacy.com/',
    'https://kingmedicalpharmacy.com/',
    'https://www.kingwestpharmacy.com/',
    'https://kohlerdrugstore.ca/about.html',
    'https://www.lifecaremedicalpharmacy.com/',
    'https://pharmacyhamilton.com/',
    'https://loprestipharmacy.com/',
    'https://m-linepharmacy.ca/',
    'https://www.mainmedicalpharmacy.com/',
    'https://marchesehealthcare.ca/',
    'https://mcknightsdrugs.com/',
    'https://www.doctr.ca/app/clinics/744319/McMaster-Drugstore/fr',
    'https://www.mediservepharmacy.ca/',
    'https://midtownpharmacy.ca/',
    'https://montgomerypharmacy.ca/',
    'https://mountainclinic.princerx.ca/',
    'https://nadiasmedicalcentre.ca/',
    'https://primaryclinic.ca/',
    'https://www.gibsonspharmacy.ca/',
    'https://www.parkdalemedicalpharmacy.com/',
    'https://pharmacenterhamilton.com/',
    'https://queensdale.princerx.ca/',
    'https://queenstonpharmacy.com/',
    'https://riverviewpharmacy.ca/',
    'https://www.samysdrugmart.ca/',
    'https://www.stjoes.ca/',
    'https://stm.grcgroup.ca/',
    'https://www.stonechurchpharmacy.com/',
    'https://www.thehamiltonpharmacy.com/',
    'https://www.queenspharmacy.ca/home',
    'https://thpharmacy.com/',
    'https://canatc.ca/company/locations/trc-hamilton-john-street/',
    'https://wellkare.ca/',
    'https://www.westendpharmacy.net/',
    'https://whitneymedicalclinic.com/index.html',
    'https://www.affirmingcare.ca/',
    'https://allwellpharmacy.ca/',
    'https://www.applehillspharmacy.com/',
    'https://www.applewoodmedical.ca/pharmacy',
    'https://arcpharmacy.ca/',
    'https://www.baxter.ca/',
    'https://bioscript.ca/',
    'https://blendrx.ca/',
    'https://brightwaterpharmacy.com/',
    'https://www.myrxhealth.ca/bp/',
    'https://britanniamedicalpharmacy.ca/contact/',
    'https://centerpharm.ca/',
    'https://aymandongol.wixsite.com/website',
    'https://thecompoundingspecialty.com/',
    'https://createcompounding.ca/',
    'https://www.crosslakepharmacy.com/contact',
    'https://danton.ca/',
    'https://derryurgentcare.ca/',
    'https://dhaliwalpharmacy.com/',
    'https://bedrugsmart.ca/',
    'https://400dundasmedical.com/',
    'https://www.dundasclinicalpharmacy.com/',
    'http://www.dunwinpharmacy.ca/',
    'https://www.earthyapothecary.com/',
    'http://emichael.ca/',
    'https://www.express-scripts.ca/',
    'https://fairviewmedicalpharmacy.com/',
    'https://faithhopeandlovepharmacy.ca/',
    'https://www.felixforyou.ca/',
    'https://www.fresenius-kabi.com/en-ca/',
    'https://glenerinpharmacy.com/',
    'https://www.healthplus2clinic.ca/',
    'https://www.premierehealthgroup.com/heartlandhealth/',
    'https://janespharmacy.ca/',
    'https://www.kennedypharmacy.ca/',
    'https://www.lakewestpharmacy.ca/',
    'https://www.lifewatchpharmacy.ca/contact-us',
    'https://www.lighthousemedicalclinic.com/',
    'https://www.lisgarwoodspharmacy.ca/',
    'https://www.mcitypharmacy.ca/',
    'https://www.medicare-clinic-maindrugmart.ca/',
    'https://www.marketplacemedical.ca/',
    'https://matthewsgatemedica.wixsite.com/website',
    'https://www.mckesson.ca/',
    'https://mdmpharmacy.ca/',
    'https://www.meadowvalepharmacy.com/compounding-',
    'https://www.medilifefamily.ca/',
    'https://www.dundas427.com/',
    'https://medixpro.wordpress.com/',
    'https://www.miclinicpharmacy.ca/',
    'https://northmedafixcompoundingpharmacy.ca/contact-us',
    'https://www.phoenixpharmacyoakville.com/',
    'https://www.pocketpills.com/',
    'https://proximahealth.ca/',
    'https://reflexmedical.net/pharmacy/',
    'https://www.renewmedicalclinics.com/home',
    'https://revepharma.ca/',
    'https://www.rxconnect.ca/',
    'https://sandalwooddrugs.ca/',
    'https://www.sdmshn.ca/',
    'https://www.sheridanpharmacy.ca/',
    'https://www.skymarkpharmacy.com/',
    'https://smartcarepharmacy.ca/',
    'https://www.sq1healthgroup.com/#',
    'https://swiderskipharmacy.ca/',
    'https://www.trimdpharmacy.com/contact-us',
    'https://triolab.ca/',
    'https://www.urbanrx.ca/pharmacy-services',
    'https://well.ca/pharmacy-welcome?affid=CJ&utm_source=Sovrn+Inc&utm_medium=affiliate&cjevent=a87de90f229b11ef804300d50a82b820',
    'https://www.windwoodpharmacy.com/',
    'https://winstondundaspharm.wixsite.com/website',
    'https://woodlawn.clinic/',
    'https://medcab.ca/',
    'https://zcanpharmacy.com/',
    'https://canapo.ca/',
    'https://careandcurepharmacies.com/',
    'https://commissionerspharmacy.com/',
    'https://universitypharmacy.ca/',
    'https://farnhampharmacy.com/',
    'https://www.greenshield.ca/en-ca/health/pharmacy',
    'https://hamilton-pharmacy.com/',
    'https://hydeparkcarepharmacy.com/',
    'https://knighthillpharmacy.wixsite.com/knighthillpharmacy',
    'https://www.lambethdrugs.ca/',
    'https://lmprx.ca/contact.html',
    'https://www.cancercareontario.ca/en',
    'https://nlmpharmacy.com/',
    'https://www.procare-pharmacy.ca/locations/london-procare-pharmacy-and-compounding',
    'https://richmondrxpharmacy.ca/',
    'https://www.riverbend-pharmacy.com/',
    'https://silverfoxrx.pharmacy.ca/',
    'https://srxhealth.ca/',
    'https://thamesvalleyfht.ca/',
    'https://tmcpharmacy.ca/',
    'https://www.uccpharmacy.com/',
    'https://www.lhsc.on.ca/about-lhsc/victoria-hospital-childrens-hospital-0',
    'https://www.saffronhealth.ca/services/pharmacy/',
    'https://yurekpharmacy.com/',
    'https://apexcare.ca/',
    'https://www.williamoslerhs.ca/en/index.aspx',
    'https://cornerstonepharmacy.ca/',
    'https://pulseucc.com/',
    'https://flowercitypharmacy.com/',
    'https://www.gillinghampharmacy.ca/',
    'https://wexfordmed.com/our-pharmacy/',
    'https://intrepidhealthgroup.com/',
    'https://mcqueenpharmacy.com/',
    'https://medboxpharmacy.ca/',
    'https://medrosemedical.ca/',
    'https://vantagemedical.ca/',
    'https://nexuspharmaherbs.com/',
    'https://www.otbramptonclinic.com/',
    'https://pendalepharmacy.ca/',
    'https://www.pillway.com/',
    'https://springdalepharmacy.ca/',
    'https://www.qhpharmacy.ca/',
    'https://www.queenlynch.com/',
    'https://myrocky.ca/',
    'https://sandalwoodpharmacy.ca/',
    'https://howdenmedicalclinic.com/',
    'https://www.springvalleypharmacy.com/',
    'https://storybrookmedical.com/',
    'https://sunnyvalemed.com/',
    'https://www.ultramedpharmacy.com/',
    'https://vanrosemedical.ca/Contactus',
    'https://vitalrx.ca/contact-us/',
    'https://wanlesspharmacy.ca/',
    'https://activapharmacy.ca/',
    'https://www.bayshore.ca/',
    'https://belgagepharmacy.com/5195762900',
    'https://www.belmontdrugspharmacy.com/',
    'https://bentonmedicalclinic.com/',
    'https://cooksrx.ca/'
]

@app.route('/')
def index():
    """Main page."""
    html = HTML_TEMPLATE.replace('{{total_sites}}', str(len(ALL_SITES)))
    return render_template_string(html)

@app.route('/api/sites')
def get_sites():
    """Get all sites list."""
    import json
    return jsonify({
        'sites': ALL_SITES,
        'count': len(ALL_SITES)
    })

@app.route('/api/detect', methods=['POST'])
def detect():
    """Detect CMP type for a given URL."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Scrape the website
        scraper = WebScraper()
        page_data = scraper.scrape(url)
        
        if not page_data or not page_data.html:
            return jsonify({
                'success': False,
                'url': url,
                'message': 'Failed to load website content'
            })
        
        # Detect CMP type
        fingerprinter = CMPFingerprinter()
        cmp_type, confidence, indicators = fingerprinter.identify_cmp_type(page_data)
        
        # Format CMP name
        cmp_display_names = {
            'godaddy': 'GoDaddy Website Builder',
            'cookieyes': 'CookieYes',
            'onetrust': 'OneTrust',
            'cookiebot': 'Cookiebot',
            'consentmanager': 'ConsentManager',
            'tarteaucitron': 'TarteAuCitron',
            'cookieinformation': 'Cookie Information',
            'custom_wordpress': 'Custom WordPress',
            'shopify': 'Shopify Privacy Center',
            'custom_generic': 'Custom Generic',
            'Unknown': 'Unknown / No CMP Detected'
        }
        
        cmp_display_name = cmp_display_names.get(cmp_type, cmp_type)
        
        return jsonify({
            'success': True,
            'url': url,
            'cmp_type': cmp_display_name,
            'cmp_type_key': cmp_type,
            'confidence': confidence,
            'indicators': indicators
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"Starting CMP Detector on {host}:{port}...")
    print(f"Open: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        app.run(debug=False, port=port, host=host)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

