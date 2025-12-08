# HCHC Family Health Cookie Banner Rule

## 🎯 **Generated Rule for hchcfamilyhealth.org**

**Website**: https://hchcfamilyhealth.org/on-site-services.php  
**Detection Confidence**: 95%  
**Banner Type**: Modal/Bottom Bar

## ✅ **Consent O Matic Setup Instructions**

### **Step 1: Create New Rule**
1. Open Consent O Matic → Settings → Rules → Custom Rules
2. Click "Add New Rule"
3. **Domain**: `hchcfamilyhealth.org`
4. **Rule Name**: `HCHC Family Health Cookie Banner`

### **Step 2: Configure Detectors**

#### **presentMatcher:**
- **Drag `CssMatcher`** into presentMatcher area
- **Target selector**: `.cookies-notification.cookies-notification--visible`
- **Parent**: (leave empty)

#### **showingMatcher:**
- **Drag `CssMatcher`** into showingMatcher area  
- **Target selector**: `.cookies-notification.cookies-notification--visible`
- **Parent**: (leave empty)

### **Step 3: Configure Actions**

#### **HIDE_CMP Method:**
- **Selector**: `.cookies-notification.cookies-notification--visible`
- **Action**: Hide the cookie banner

#### **DO_CONSENT Method:**
- **Drag `ClickAction`** into DO_CONSENT area
- **Target selector**: `.cookies-notification-button`
- **Action**: Click the Accept button

## 🎯 **Summary of Selectors**

| Element | Selector | Purpose |
|---------|----------|---------|
| **Banner** | `.cookies-notification.cookies-notification--visible` | Detect and hide the cookie banner |
| **Accept Button** | `.cookies-notification-button` | Click to accept cookies |

## 🧪 **Testing**

1. **Visit**: https://hchcfamilyhealth.org/on-site-services.php
2. **Expected Result**: Cookie banner should disappear automatically
3. **If not working**: Check browser console for errors

## 📊 **Detection Details**

- **Confidence Score**: 95%
- **Buttons Found**: 3 accept buttons
- **Banner Type**: Modal/notification style
- **Location**: Bottom of page
- **Generated**: 2025-10-17 by CMP Mapper

## 🔧 **Alternative Selectors (if needed)**

If the main selectors don't work, try these alternatives:

### **Banner Alternatives:**
- `.cookies-notification`
- `[class*='cookie-notification']`
- `.cookie-banner`

### **Button Alternatives:**
- `.cookies-notification button`
- `button[class*='cookie']`
- `.cookie-accept-button`

## 💡 **Notes**

- This rule was automatically generated using CMP Mapper
- High confidence score indicates reliable detection
- Banner appears as a bottom notification bar
- Uses standard cookie consent patterns
