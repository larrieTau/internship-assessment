# 🚀 Deployment to Hugging Face Spaces

This guide walks you through deploying the Sunbird AI GenAI Application to Hugging Face Spaces (free hosting).

## Prerequisites

- GitHub account with your forked repository
- Hugging Face account (free at https://huggingface.co/join)
- Sunbird AI API token (from https://sunbird.ai)

---

## Step 1: Create a Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Fill in the form:
   - **Owner:** Select your username
   - **Space name:** `sunbird-ai-genai-app` (or your preferred name)
   - **SDK:** Select "Gradio"
   - **Visibility:** Select "Public"
3. Click **"Create Space"**

**Your Space URL will be:** `https://huggingface.co/spaces/<your-username>/<space-name>`

---

## Step 2: Add Sunbird API Token as a Secret

Hugging Face Spaces securely stores secrets as environment variables.

1. Go to your Space page
2. Click **Settings** (gear icon, top right)
3. Go to the **"Variables and secrets"** tab
4. Click **"New secret"**
5. Fill in:
   - **Name:** `SUNBIRD_API_TOKEN`
   - **Value:** Paste your actual Sunbird AI API token
6. Click **"Add secret"**

✅ The token is now encrypted and only accessible to your Space's code.

---

## Step 3: Connect Your GitHub Repository

You have two options:

### Option A: Push from Command Line (Recommended)

```bash
# Navigate to your local repository
cd /path/to/internship-assessment

# Add Hugging Face as a remote
git remote add space https://huggingface.co/spaces/<your-username>/<space-name>

# Ensure you're on the main branch
git branch -M main

# Push your code
git push -u space main
```

Hugging Face will automatically:
- Clone your code
- Install `requirements.txt`
- Run `app.py` as the entry point
- Make it publicly accessible

### Option B: Push via GitHub Connection (Alternative)

1. In your Space Settings, connect your GitHub account
2. Select your repository
3. Connect the Space to auto-sync with your GitHub `main` branch

---

## Step 4: Verify Deployment

After pushing, Hugging Face will start building:

1. You'll see a **"Building"** status in the Space
2. Watch the build logs (takes 2-5 minutes typically)
3. Once complete, you'll see **"Running"** and a green checkmark
4. Click the Space URL or the **"View" button** to test the app

### Test Checklist

- ✅ Page loads without errors
- ✅ Can toggle between "text" and "audio" input
- ✅ Can select target languages
- ✅ UI displays all 4 output sections

---

## Step 5: Test with Real Input

### Test with Text Input

1. Select **"text"** input type
2. Enter: *"Uganda is a beautiful country in East Africa with diverse wildlife."*
3. Select target language: **"Luganda"**
4. Click **"🚀 Process"**
5. Verify you get:
   - Original text
   - Summary
   - Translation in Luganda
   - Playable audio

### Test with Audio (Optional)

1. Record a short audio file (under 5 minutes)
2. Upload it
3. Select target language
4. Process and verify all outputs

---

## Troubleshooting Deployment

### App shows "Error: API token not configured"
- **Cause:** `SUNBIRD_API_TOKEN` secret not set
- **Fix:** Go to Space Settings → Variables and secrets → Add the secret

### "Build failed" during deployment
1. Check the build logs for specific errors
2. Verify `requirements.txt` has all dependencies
3. Ensure `app.py` is in the root directory
4. Try deleting the Space and recreating it

### App runs but API calls fail
- **Cause 1:** API token invalid or expired
  - **Fix:** Regenerate token at https://sunbird.ai/api-dashboard and update the secret
- **Cause 2:** Sunbird API endpoint changed
  - **Fix:** Check https://docs.sunbird.ai and update URLs in `backend/sunbird_client.py`

### "Can't find Python dependencies"
- **Cause:** `requirements.txt` missing or incomplete
- **Fix:** Ensure `requirements.txt` in root includes: gradio, requests, python-dotenv, soundfile, numpy, scipy

---

## Updating Your Deployment

### After Making Changes Locally

```bash
# Make your changes, then:
git add .
git commit -m "Your change description"
git push space main
```

Hugging Face will automatically rebuild and redeploy.

### Rollback to Previous Version

If something breaks:
1. Go to your Space's **"Files and versions"** tab
2. See your commit history
3. Revert to a previous commit or modify `app.py` directly in the Hugging Face editor

---

## Sharing Your Deployed App

Once live, share the URL:
- **Direct link:** `https://huggingface.co/spaces/<your-username>/<space-name>`
- **Embedded iframe:** Include in your portfolio or resume
- **Social media:** Link to show reviewers your work

---

## Performance Considerations

**Free Tier Limits:**
- CPU: Shared compute
- Memory: Generous but not unlimited
- Uptime: App stays on if accessed regularly; might sleep if unused for long periods

**For Production/Heavy Use:**
- Upgrade to a paid Space compute tier
- Or deploy to Vercel (for Next.js) or another provider

---

## Next: Submission

Once deployed:

1. ✅ Copy your Space URL: `https://huggingface.co/spaces/<username>/<space-name>`
2. ✅ Verify the app works with test input
3. ✅ Update PROJECT_README.md with the deployed link
4. ✅ Create a GitHub PR or provide your repository link
5. ✅ Submit all three components:
   - GitHub repo with code
   - Updated README with deployment link
   - Live working app at the Space URL

---

## Support

- **Hugging Face Spaces Docs:** https://huggingface.co/docs/hub/spaces
- **Gradio Docs:** https://www.gradio.app/docs
- **Sunbird AI Docs:** https://docs.sunbird.ai
