# Deployment Guide 🚀

## Quick Deployment to Render.com

### Step 1: Prepare Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (e.g., `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Deploy to Render

1. **Sign up** at [Render.com](https://render.com) (free account)

2. **Connect GitHub**:
   - Push this code to your GitHub repository
   - Connect Render to your GitHub account

3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Select your repository
   - Service name: `engineers-babu-bot`
   - Environment: `Python 3`

4. **Configure Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_bot.py`
   
5. **Add Environment Variable**:
   - Go to "Environment" tab
   - Add variable:
     - Key: `BOT_TOKEN`
     - Value: Your bot token from BotFather

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - ✅ Done! Your bot is live!

### Step 3: Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Upload a `.txt` file
5. Receive your personalized HTML! 🎉

## Alternative Deployment Options

### Deploy to Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create engineers-babu-bot

# Set environment variable
heroku config:set BOT_TOKEN=your_bot_token_here

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variable:
   - `BOT_TOKEN` = your token
5. Deploy automatically

### Deploy to PythonAnywhere

1. Upload files to PythonAnywhere
2. Create virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.8 myenv
   pip install -r requirements.txt
   ```
3. Set environment variable in `.bashrc`:
   ```bash
   export BOT_TOKEN="your_token_here"
   ```
4. Create always-on task:
   ```bash
   python telegram_bot.py
   ```

## Troubleshooting

### Bot Not Responding

**Problem**: Bot doesn't reply to messages

**Solutions**:
1. Check logs for errors
2. Verify `BOT_TOKEN` is correct
3. Ensure bot is running
4. Check Telegram bot settings with @BotFather

**Render Logs**:
```bash
# View in Render dashboard → Logs tab
```

### Port Error Fixed

**Previous Issue**: `app.run()` port error

**Fix Applied**: 
- Removed Flask dependency
- Bot now runs with `application.run_polling()`
- No port configuration needed

### File Processing Errors

**Problem**: Bot can't process files

**Solutions**:
1. Check file format (must be `.txt`)
2. Verify file content matches format: `(Category)Title:URL`
3. Check for special characters in file
4. Ensure URLs are valid

### Deployment Failed

**Problem**: Render deployment fails

**Solutions**:
1. Check `requirements.txt` is present
2. Verify Python version compatibility
3. Check build logs for specific errors
4. Ensure `render.yaml` is configured correctly

## Environment Variables

### Required Variables

- `BOT_TOKEN`: Your Telegram bot token from @BotFather

### Optional Variables

None required for basic operation.

## File Structure for Deployment

```
your-project/
├── telegram_bot.py       # Main bot code ✓
├── test_parser.py       # Testing script ✓
├── requirements.txt     # Dependencies ✓
├── render.yaml         # Render config ✓
├── README.md          # Documentation ✓
└── DEPLOYMENT.md      # This file ✓
```

## Testing Before Deployment

### Local Test

```bash
# Set token
export BOT_TOKEN="your_token_here"

# Run bot
python telegram_bot.py

# You should see:
# 🤖 Bot started! Send /start to begin.
```

### Test HTML Generation

```bash
# Run test script
python test_parser.py

# Check output in /mnt/user-data/outputs/test_output.html
```

## Post-Deployment Checklist

- [ ] Bot token configured
- [ ] Bot responds to `/start`
- [ ] Can upload `.txt` files
- [ ] HTML files generated correctly
- [ ] Videos play properly
- [ ] PDFs open in fullscreen
- [ ] Watermark appears on videos
- [ ] Right-click disabled
- [ ] Mobile responsive

## Monitoring

### Check Bot Status

**Render Dashboard**:
- Go to your service
- Check "Logs" tab
- Monitor for errors

**Telegram**:
- Send `/start` to bot
- If no response, check deployment

### View Logs

**Render**:
```
Dashboard → Your Service → Logs
```

**Heroku**:
```bash
heroku logs --tail
```

**Railway**:
```
Project → Deployments → View Logs
```

## Updating Your Bot

### Update Code

```bash
# Make changes to code
git add .
git commit -m "Update bot features"
git push origin main

# Render will auto-deploy
# Or trigger manual deploy in dashboard
```

### Update Dependencies

```bash
# Edit requirements.txt
# Push changes
# Render will rebuild automatically
```

## Security Best Practices

1. **Never commit** `BOT_TOKEN` to GitHub
2. **Use environment variables** for sensitive data
3. **Regularly update** dependencies
4. **Monitor logs** for suspicious activity
5. **Keep backup** of bot configuration

## Cost Considerations

### Render.com (Free Tier)
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Spins down after inactivity

### Heroku (Free Tier)
- ✅ 550-1000 hours/month free
- ✅ Easy deployment
- ⚠️ Deprecated free tier (check current status)

### Railway (Free Tier)
- ✅ $5 free credit/month
- ✅ Simple deployment
- ✅ Good performance

## Support

Need help? Check:
1. Render documentation: https://render.com/docs
2. python-telegram-bot docs: https://docs.python-telegram-bot.org
3. GitHub issues in repository

## Success Metrics

After deployment, verify:
- ✅ Bot uptime > 99%
- ✅ Response time < 2s
- ✅ HTML generation < 5s
- ✅ No error logs
- ✅ All features working

---

**Deployment Complete! 🎉**

Your bot is now live and ready to generate HTML files!
