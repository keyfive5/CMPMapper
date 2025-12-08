# 🚀 Quick Start Guide - CMP Mapper Pro

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python cmp_mapper_pro.py
```

### Step 3: Open in Browser
Navigate to: `http://localhost:5000`

## Using the Application

### 🔍 Analyze a Single Website

1. Go to the **"Analyze Banner"** tab
2. Enter a website URL (e.g., `https://www.example.com/`)
3. Click **"Analyze Consent Banner"**
4. Wait for analysis to complete
5. Download the generated rule JSON file

### 📊 Upload Excel/CSV File

1. Go to the **"Excel/CSV Upload"** tab
2. Click the upload area or drag & drop your file
3. Supported formats: `.xlsx`, `.xls`, `.csv`
4. The file should have URLs in the first column or a column named "URL"
5. Once uploaded, you'll see all extracted URLs
6. Click **"Use These URLs for Mass Testing"** to test them all

### 🚀 Mass Testing

1. Go to the **"Mass Testing"** tab
2. Enter URLs (one per line) or use URLs from Excel upload
3. Select which rules to test against
4. Click **"Start Mass Testing"**
5. View results for each URL

### 📋 Rules Manager

1. Go to the **"Rules Manager"** tab
2. View all your Consent O Matic rules
3. See statistics about your rules
4. Click on any rule to view details

## Sample Files

We've included a sample CSV file with all 15 pharmacy websites:
- `pharmacy_sites.csv` - Ready to upload and test!

## Quick Test Links

The application includes pre-configured quick links for:
- **GoDaddy Group** (8 sites)
- **CookieYes Group** (4 sites)
- **Other Sites** (3 sites)

Just click any button to load the URL and analyze it!

## Cloud Deployment

Want to deploy online? See `DEPLOYMENT_GUIDE.md` for instructions on deploying to:
- Railway (Free tier available)
- Render (Free tier available)
- Heroku

## Need Help?

- Check the **"About"** tab in the application
- Read the main `README.md`
- See `DEPLOYMENT_GUIDE.md` for cloud deployment

