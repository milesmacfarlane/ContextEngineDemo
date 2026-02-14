# 🚀 GitHub + Streamlit Deployment Guide

## Complete Step-by-Step Setup

This guide will walk you through creating a Streamlit app connected to your GitHub repository.

---

## 📋 Prerequisites

- GitHub account (free): https://github.com/signup
- Files ready to upload (I've created them for you!)

---

## PART 1️⃣: Create GitHub Repository

### Step 1: Create New Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `ContextEngineDemo` (or your choice)
   - **Description:** `Statistics Question Generator with Rich Narrative Context Engine`
   - **Visibility:** ✅ **Public** (required for free Streamlit hosting)
   - **Initialize:** ✅ Check "Add a README file"
3. Click **"Create repository"**

✅ **You now have:** `https://github.com/YourUsername/ContextEngineDemo`

---

### Step 2: Create Folder Structure

On the GitHub website, you'll create this structure:

```
ContextEngineDemo/
├── app.py                                  ← Main app
├── requirements.txt                        ← Dependencies
├── README.md                              ← Already created
├── .gitignore                             ← Ignore files
├── data/
│   ├── ContextBanks.xlsx                  ← Your 50 contexts
│   └── WorksheetMergeMasterSourceFile.xlsx ← Lookup data
└── src/
    ├── context_engine.py                  ← Context engine
    ├── data_manager.py                    ← Data manager
    ├── statistics_calculator.py           ← Calculator
    ├── question_models.py                 ← Question models
    └── generators/
        └── mean_generator_v2.py           ← Mean generator
```

---

### Step 3: Upload Files (GitHub Web Interface)

I'll give you the exact steps for each file:

#### **A. Root Files**

1. Click **"Add file"** → **"Upload files"**
2. Upload these files to root:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
3. Commit: "Add root files"

#### **B. Create `data` folder**

1. Click **"Add file"** → **"Create new file"**
2. Type in filename: `data/.gitkeep` (this creates the folder)
3. Click **"Commit changes"**
4. Now click into `data` folder
5. Click **"Add file"** → **"Upload files"**
6. Upload:
   - `ContextBanks.xlsx`
   - `WorksheetMergeMasterSourceFile.xlsx`
7. Commit: "Add data files"

#### **C. Create `src` folder**

1. Back to root, click **"Add file"** → **"Create new file"**
2. Type: `src/.gitkeep`
3. Commit changes
4. Click into `src` folder
5. Upload:
   - `context_engine.py`
   - `data_manager.py`
   - `statistics_calculator.py`
   - `question_models.py`
6. Commit: "Add src files"

#### **D. Create `src/generators` folder**

1. Inside `src`, click **"Add file"** → **"Create new file"**
2. Type: `generators/.gitkeep`
3. Commit changes
4. Click into `generators` folder
5. Upload:
   - `mean_generator_v2.py`
6. Commit: "Add generators"

✅ **All files uploaded!**

---

## PART 2️⃣: Connect to Streamlit

### Step 1: Create Streamlit Account

1. Go to https://streamlit.io/cloud
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub
5. Complete profile setup

✅ **Streamlit can now see your GitHub repos**

---

### Step 2: Deploy Your App

1. On Streamlit Cloud dashboard, click **"New app"**
2. Fill in:
   - **Repository:** Select `YourUsername/ContextEngineDemo`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Choose a custom URL (e.g., `yourname-context-engine`)
3. Click **"Deploy!"**

🎉 **Streamlit starts building your app!**

---

### Step 3: Wait for Deployment

You'll see:
- ⏳ Installing dependencies...
- ⏳ Building app...
- ✅ **App is live!**

Takes ~2-3 minutes on first deploy.

---

### Step 4: Test Your App

1. Once deployed, you'll get a URL like:
   ```
   https://yourname-context-engine.streamlit.app
   ```

2. Click the URL to open your app

3. Test it:
   - Select a context (e.g., "heart_rate")
   - Choose narrative level ("standard")
   - Click **"Generate Question"**
   - See the magic! ✨

---

## 🔄 Making Updates

Whenever you update files on GitHub:

1. Edit file on GitHub (or push from local)
2. Commit changes
3. Streamlit **automatically redeploys** in ~1 minute!

No manual deployment needed! 🚀

---

## 📂 Where to Get the Files

I've created these files for you:

### **Files I Created:**
1. `app.py` - Main Streamlit app (interactive demo)
2. `requirements.txt` - Python dependencies
3. `README.md` - Repository description
4. `.gitignore` - Files to ignore

### **Files You Already Have:**
5. `ContextBanks.xlsx` - Your 50 contexts (you filled this in!)
6. `context_engine.py` - Context engine (I built this)
7. `mean_generator_v2.py` - Mean generator (I built this)

### **Files from Previous Work:**
8. `data_manager.py` - From your TestGenerator repo
9. `statistics_calculator.py` - From your TestGenerator repo
10. `question_models.py` - From your TestGenerator repo
11. `WorksheetMergeMasterSourceFile.xlsx` - Your lookup data

---

## 🎯 Quick Checklist

Before deploying, make sure you have:

- [ ] GitHub account created
- [ ] New repository created (`ContextEngineDemo`)
- [ ] All files uploaded to correct folders
- [ ] Streamlit account created
- [ ] Connected Streamlit to GitHub
- [ ] App deployed
- [ ] App tested and working

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Fix:** Add missing module to `requirements.txt`

Example:
```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
```

Commit the change, Streamlit will redeploy.

---

### "File not found: data/ContextBanks.xlsx"

**Fix:** Check folder structure matches exactly:
```
data/
  ContextBanks.xlsx  ← Must be here
  WorksheetMergeMasterSourceFile.xlsx
```

---

### "Import Error: context_engine"

**Fix:** Check `src/` folder has all files:
```
src/
  context_engine.py  ← Must be here
  data_manager.py
  statistics_calculator.py
  question_models.py
  generators/
    mean_generator_v2.py
```

---

### App loads slowly

**Normal!** First load can take 10-20 seconds as it:
- Loads Excel files
- Parses 50 contexts
- Creates cache

Subsequent loads are faster (cached).

---

## 🎨 Customization

### Change App Title
In `app.py`, line ~15:
```python
st.set_page_config(
    page_title="Your Custom Title",  # Change this
    page_icon="🎨",
```

### Change URL
On Streamlit Cloud:
1. Go to app settings
2. Click "Edit URL"
3. Choose new URL
4. Save

### Add Features
Edit `app.py` on GitHub:
1. Make changes
2. Commit
3. Auto-deploys!

---

## 📊 App Features

Your deployed app will have:

✅ **Interactive UI**
- Dropdown to select contexts
- Sliders for difficulty
- Radio buttons for narrative level
- Generate button

✅ **Live Preview**
- See generated questions
- Show/hide answers
- View solution steps

✅ **Context Info**
- Shows context metadata
- Displays value ranges
- Lists compatible variations

✅ **Examples**
- Sample questions for different contexts
- Category browsing
- System statistics

---

## 🚀 Next Steps

After deployment:

1. **Share your URL!**
   - Tweet it
   - Share with colleagues
   - Demo to students

2. **Gather Feedback**
   - What contexts do students like?
   - Which narrative level works best?
   - Any missing contexts?

3. **Iterate**
   - Add contexts to Excel
   - Push to GitHub
   - Auto-deploys with updates!

4. **Expand**
   - Add more variations
   - Integrate other generators
   - Build out full test creator

---

## 💡 Pro Tips

### Tip 1: Use .streamlit/secrets.toml for API Keys

If you add features that need API keys:

1. In Streamlit Cloud, go to app settings
2. Click "Secrets"
3. Add secrets in TOML format
4. Access in code: `st.secrets["key_name"]`

### Tip 2: Enable Analytics

Streamlit Cloud shows you:
- Number of visitors
- Most popular features
- Error logs

Check "Analytics" tab in app settings.

### Tip 3: Custom Domain (Paid)

Want `questions.yourschool.com` instead of `.streamlit.app`?

Upgrade to Streamlit Teams plan ($250/month).

### Tip 4: Pin Versions

In `requirements.txt`, pin exact versions for stability:
```
streamlit==1.29.0
pandas==2.1.0
openpyxl==3.1.2
```

---

## 🎉 You're Ready!

Follow this guide step-by-step and you'll have:

1. ✅ GitHub repository with all files
2. ✅ Streamlit app deployed
3. ✅ Live URL to share
4. ✅ Auto-deployment on updates

**Let's make this happen!** 🚀

---

## 📞 Need Help?

If you get stuck:
1. Check the Troubleshooting section above
2. Look at Streamlit docs: https://docs.streamlit.io
3. Check GitHub file structure matches exactly
4. Verify all files are in correct locations

**Most common issue:** Files in wrong folders. Double-check the folder structure!

---

**Ready to deploy? Let me know when you've created your GitHub repo and I'll help with the next steps!** 🎯
