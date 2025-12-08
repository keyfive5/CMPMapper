# CMP Mapper - Deployment Guide

## Cloud Deployment Options

CMP Mapper can be deployed to various cloud platforms. Here are the supported platforms:

### 1. Railway (Recommended - Free Tier Available)

1. **Sign up** at [railway.app](https://railway.app)
2. **Create a new project** and connect your GitHub repository
3. Railway will automatically detect the `railway.json` configuration
4. The app will deploy automatically on push to main branch
5. Your app will be available at `https://your-app-name.railway.app`

**Environment Variables (Optional):**
- `PORT` - Automatically set by Railway
- `FLASK_DEBUG` - Set to `False` for production

### 2. Render

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service** and connect your GitHub repository
3. Use the following settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_ui.py`
   - **Environment:** Python 3
4. Render will use the `render.yaml` configuration automatically
5. Your app will be available at `https://your-app-name.onrender.com`

**Note:** Free tier on Render spins down after 15 minutes of inactivity.

### 3. Vercel (Serverless)

1. **Sign up** at [vercel.com](https://vercel.com)
2. **Import your project** from GitHub
3. Vercel will use the `vercel.json` configuration
4. Note: Vercel uses serverless functions, so long-running operations may timeout

### 4. Heroku

1. **Sign up** at [heroku.com](https://heroku.com)
2. **Create a new app** and connect your GitHub repository
3. Heroku will use the `Procfile` automatically
4. Your app will be available at `https://your-app-name.herokuapp.com`

**Note:** Heroku no longer offers a free tier.

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python web_ui.py
   ```

3. **Access the web interface:**
   Open your browser to `http://127.0.0.1:5000`

## Features

### Excel/CSV Upload
- Upload Excel (.xlsx, .xls) or CSV files containing URLs
- The file should have URLs in the first column or a column named "URL" or "url"
- Maximum 100 URLs per batch

### Rules Management
- View all Consent O Matic rules in the `custom-consent-o-matic-rules/rules/` directory
- Rules are automatically loaded and available for batch testing

### Batch Testing
- Test multiple URLs against your Consent O Matic rules
- See which rules match which websites
- Get detailed statistics and results

## Requirements

- Python 3.11+
- All dependencies listed in `requirements.txt`
- For cloud deployment: A cloud platform account (Railway, Render, etc.)

## Troubleshooting

### Port Issues
If you encounter port binding errors, ensure the `PORT` environment variable is set correctly for your platform.

### Selenium/Chrome Issues
For cloud deployment, you may need to install Chrome/Chromium. Some platforms require additional buildpacks or configuration.

### File Upload Issues
Ensure the `uploads/` directory exists and has write permissions (if using file storage).

## Support

For issues or questions, please check the main README.md or open an issue on GitHub.
