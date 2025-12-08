# 🚀 CMP Mapper Pro - Deployment Guide

## Cloud Deployment Options

CMP Mapper Pro is ready for cloud deployment on multiple platforms. All configurations are already set up!

### Option 1: Railway (Recommended - Free Tier Available)

1. **Sign up** at [railway.app](https://railway.app)
2. **Create a new project** and connect your GitHub repository
3. Railway will automatically detect the `railway.json` configuration
4. Your app will be live at `https://your-app-name.railway.app`

**Benefits:**
- Free tier with $5 credit/month
- Automatic HTTPS
- Easy GitHub integration
- No credit card required for free tier

### Option 2: Render (Free Tier Available)

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. Connect your GitHub repository
4. Render will use the `render.yaml` configuration automatically
5. Your app will be live at `https://your-app-name.onrender.com`

**Benefits:**
- Free tier available
- Automatic HTTPS
- Auto-deploy on git push
- Free tier spins down after 15 minutes of inactivity (wakes up on first request)

### Option 3: Heroku (Paid)

1. **Sign up** at [heroku.com](https://heroku.com)
2. **Create a new app**
3. Connect your GitHub repository
4. Deploy using the `Procfile`
5. Your app will be live at `https://your-app-name.herokuapp.com`

**Note:** Heroku no longer offers a free tier, but provides reliable hosting.

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python cmp_mapper_pro.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

## Environment Variables

The application uses the following environment variables (optional):

- `PORT` - Port to run on (default: 5000)
- `HOST` - Host to bind to (default: 0.0.0.0)

These are automatically set by cloud platforms.

## Features Available

✅ **Single URL Analysis** - Analyze individual websites for consent banners
✅ **Excel/CSV Upload** - Upload files with URLs for batch processing
✅ **Mass Testing** - Test multiple URLs against your rules
✅ **Rules Manager** - View and manage all Consent O Matic rules
✅ **Quick Links** - Pre-configured links for GoDaddy and CookieYes groups
✅ **Beautiful UI** - Modern, responsive design

## Sample Files

- `pharmacy_sites.csv` - Sample CSV file with all 15 pharmacy websites
- Upload this file in the "Excel/CSV Upload" tab to test all sites at once

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, set a different port:
```bash
export PORT=5001
python cmp_mapper_pro.py
```

### Missing Dependencies
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Selenium Issues
If you encounter Selenium errors, make sure you have Chrome/Chromium installed. The application uses headless Chrome for web scraping.

## Support

For issues or questions, please check the main README.md or open an issue on GitHub.

