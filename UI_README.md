# CMP Mapper Web UI

A beautiful, modern web interface for the CMP Mapper cookie consent banner detection system.

## 🚀 Quick Start

### Option 1: Double-click launcher (Windows)
```
start_ui.bat
```

### Option 2: Command line
```bash
python web_ui.py
```

### Option 3: Demo test
```bash
python demo_ui.py
```

## 🌐 Access the Interface

Once started, the web UI will be available at:
**http://127.0.0.1:5000**

The browser should open automatically. If not, manually navigate to the URL above.

## 🎯 Features

### 📱 Modern, Responsive Design
- Beautiful gradient backgrounds
- Card-based layout
- Mobile-friendly responsive design
- Smooth animations and transitions

### 🔍 Two Analysis Modes

#### 1. URL Analysis
- Enter any website URL
- Automatic web scraping and banner detection
- Real-time analysis results

#### 2. HTML Analysis
- Paste HTML content directly
- Perfect for testing custom banners
- Instant analysis and rule generation

### 📊 Comprehensive Results

#### Page Information
- URL and metadata
- HTML size and collection time
- Analysis timestamp

#### Banner Detection
- Banner type (modal, bottom bar, etc.)
- Confidence score (0-100%)
- Detected buttons with selectors
- Container and overlay selectors

#### Generated Rule
- Consent O Matic compatible JSON
- Optimized CSS selectors
- Action recommendations
- Download functionality

### 🎨 Visual Elements

#### Status Badges
- ✅ Success indicators
- ⚠️ Warning messages
- ❌ Error notifications

#### Interactive Elements
- Tabbed interface
- Loading animations
- Real-time updates
- Download buttons

#### Code Display
- Syntax highlighting for selectors
- Monospace fonts for code
- Copy-friendly formatting

## 🛠️ Technical Details

### Built With
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with gradients and animations
- **Icons**: Font Awesome
- **API**: RESTful JSON API

### API Endpoints
- `GET /` - Main interface
- `POST /api/analyze` - Analyze URL
- `POST /api/analyze-html` - Analyze HTML content
- `GET /api/download-rule` - Download generated rule
- `GET /api/results` - Get current results

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## 📱 Mobile Support

The interface is fully responsive and works great on:
- Smartphones
- Tablets
- Desktop computers
- All screen sizes

## 🎯 Usage Examples

### Example 1: Analyze a Website
1. Go to "URL Analysis" tab
2. Enter: `https://example.com`
3. Click "Analyze Website"
4. View results and download rule

### Example 2: Test Custom HTML
1. Go to "HTML Analysis" tab
2. Paste your HTML content
3. Click "Analyze HTML"
4. Review detected elements

### Example 3: Download Rules
1. After analysis, click "Download Rule JSON"
2. Save the Consent O Matic compatible rule
3. Import into Consent O Matic extension

## 🔧 Troubleshooting

### Server Won't Start
- Make sure Python is installed
- Install Flask: `pip install flask`
- Check if port 5000 is available

### Browser Won't Open
- Manually navigate to: http://127.0.0.1:5000
- Try a different browser
- Check firewall settings

### Analysis Fails
- Check your internet connection
- Verify the URL is accessible
- Try the HTML analysis mode instead

## 🎨 Customization

The UI is built with modern CSS and can be easily customized:
- Colors and gradients
- Fonts and typography
- Layout and spacing
- Animations and transitions

## 📈 Performance

- Fast analysis (typically 2-5 seconds)
- Responsive interface
- Efficient data handling
- Minimal resource usage

## 🔒 Security

- Local server only (127.0.0.1)
- No external data transmission
- Secure API endpoints
- Input validation and sanitization

## 🎉 Enjoy!

The CMP Mapper Web UI provides a beautiful, intuitive way to analyze cookie consent banners and generate Consent O Matic rules. No more command-line interfaces - everything is visual and interactive!

---

**Happy banner detecting!** 🍪✨

