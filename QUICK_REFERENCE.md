# ⚡ Quick Reference - GitHub + Streamlit Setup

## 📦 Files You Need

### From Me (New Files):
- [ ] `app.py` - Streamlit app
- [ ] `requirements.txt` - Dependencies
- [ ] `README.md` - Repository description
- [ ] `.gitignore` - Git ignore file
- [ ] `context_engine.py` - Context engine
- [ ] `mean_generator_v2.py` - Mean generator

### From You (Existing Files):
- [ ] `ContextBanks.xlsx` - Your 50 contexts
- [ ] `WorksheetMergeMasterSourceFile.xlsx` - Lookup data
- [ ] `data_manager.py` - From TestGenerator
- [ ] `statistics_calculator.py` - From TestGenerator
- [ ] `question_models.py` - From TestGenerator

---

## 🎯 5-Minute Deploy Checklist

### GitHub Setup (3 minutes)
1. [ ] Create repository: https://github.com/new
   - Name: `ContextEngineDemo`
   - Public ✅
   - Initialize with README ✅

2. [ ] Upload root files:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`

3. [ ] Create `data/` folder, upload:
   - `ContextBanks.xlsx`
   - `WorksheetMergeMasterSourceFile.xlsx`

4. [ ] Create `src/` folder, upload:
   - `context_engine.py`
   - `data_manager.py`
   - `statistics_calculator.py`
   - `question_models.py`

5. [ ] Create `src/generators/` folder, upload:
   - `mean_generator_v2.py`

### Streamlit Deploy (2 minutes)
1. [ ] Go to: https://streamlit.io/cloud
2. [ ] Sign up with GitHub
3. [ ] Click "New app"
4. [ ] Select your repo: `ContextEngineDemo`
5. [ ] Main file: `app.py`
6. [ ] Click "Deploy"
7. [ ] Wait ~2 minutes
8. [ ] ✅ App is live!

---

## 📂 Folder Structure (Must Match Exactly!)

```
ContextEngineDemo/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── ContextBanks.xlsx
│   └── WorksheetMergeMasterSourceFile.xlsx
└── src/
    ├── context_engine.py
    ├── data_manager.py
    ├── statistics_calculator.py
    ├── question_models.py
    └── generators/
        └── mean_generator_v2.py
```

---

## 🔗 URLs You'll Need

| Service | URL |
|---------|-----|
| Create GitHub repo | https://github.com/new |
| Streamlit Cloud signup | https://streamlit.io/cloud |
| Your GitHub repo | https://github.com/YourUsername/ContextEngineDemo |
| Your deployed app | https://yourname-context-engine.streamlit.app |

---

## ⚠️ Common Mistakes

❌ **Don't:**
- Make repository private (Streamlit free tier needs public)
- Upload files to wrong folders
- Forget to create folders (data/, src/, src/generators/)
- Miss any files

✅ **Do:**
- Double-check folder structure
- Verify all files uploaded
- Test after deployment
- Share your URL!

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| "Module not found" | Check `requirements.txt` has all packages |
| "File not found" | Check file is in correct folder |
| "Import error" | Check `src/` folder structure |
| App won't load | Check logs in Streamlit Cloud dashboard |

---

## 🎉 Success Checklist

After deployment, you should be able to:
- [ ] Visit your app URL
- [ ] See the Context Engine interface
- [ ] Select a context from dropdown
- [ ] Click "Generate Question"
- [ ] See a formatted question appear
- [ ] Toggle "Show Answer" to see solution
- [ ] Generate multiple questions

---

## 📞 Help Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Deployment:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **GitHub Guide:** https://docs.github.com/en/get-started

---

**You've got this! 🚀**

Follow the checklist, double-check the folder structure, and you'll have a live app in minutes!
