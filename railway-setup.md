# Railway Hosting Setup for CMP Mapper

## Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

## Step 2: Login to Railway
```bash
railway login
```

## Step 3: Initialize Project
```bash
railway init
```

## Step 4: Deploy
```bash
railway up
```

## Step 5: Set Environment Variables
In Railway dashboard, add:
- `PORT=5000`
- `PYTHON_VERSION=3.11`

## Step 6: Install Chrome Dependencies
Add to your `requirements.txt`:
```
selenium
beautifulsoup4
flask
requests
pydantic
```

## Step 7: Add Chrome Installation
Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python web_ui.py"
  }
}
```

## Step 8: Deploy
```bash
git add .
git commit -m "Add Railway deployment config"
git push origin main
railway up
```

Your app will be available at: `https://your-app-name.railway.app`
