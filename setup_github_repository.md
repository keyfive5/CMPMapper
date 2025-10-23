# Setting Up Your Own Consent O Matic Rules Repository

## 🎯 Goal
Create your own GitHub repository to host Consent O Matic rules, similar to the official repository.

## 📋 Steps

### 1. Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name it: `consent-o-matic-rules` (or your preferred name)
4. Make it **Public** (so raw.githubusercontent.com works)
5. Add description: "Custom Consent O Matic rules for various websites"
6. Click "Create repository"

### 2. Repository Structure
Create this folder structure:
```
consent-o-matic-rules/
├── rules/
│   ├── margispharmacy.json
│   ├── midtowncompoundingpharmacy.json
│   ├── beyondrx.json
│   ├── westmountmedicalpharmacy.json
│   └── [your-custom-rules].json
├── README.md
└── rules.schema.json
```

### 3. Upload Your Rules
1. Go to your repository
2. Click "Add file" → "Upload files"
3. Upload all your generated JSON rules
4. Commit with message: "Add custom Consent O Matic rules"

### 4. Create Raw URLs
Your rules will be accessible at:
- `https://raw.githubusercontent.com/[your-username]/consent-o-matic-rules/master/rules/margispharmacy.json`
- `https://raw.githubusercontent.com/[your-username]/consent-o-matic-rules/master/rules/westmountmedicalpharmacy.json`
- etc.

### 5. Update Your CMP Mapper
Modify your CMP Mapper to use your repository URLs instead of the official ones.

## 🎉 Benefits
- **Your own rules**: Host custom rules for specific websites
- **Easy sharing**: Share rules with others via raw URLs
- **Version control**: Track changes to your rules
- **Collaboration**: Others can contribute rules
- **Custom schema**: Create your own validation schema

## 📝 Example Repository
Your repository could look like:
```
https://github.com/[your-username]/consent-o-matic-rules
```

With rules accessible at:
```
https://raw.githubusercontent.com/[your-username]/consent-o-matic-rules/master/rules/[rule-name].json
```
