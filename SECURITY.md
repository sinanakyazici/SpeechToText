# Security Policy

## 🔒 Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:
- Opening a GitHub issue with the label "security"
- Or contacting the maintainers directly

We take security seriously and will respond to valid reports as quickly as possible.

---

## ⚠️ Known Security Issues

### Critical: API Token Exposure (FIXED)

**Issue**: Previous versions of this project contained hardcoded HuggingFace API tokens in the source code.

**Status**: This has been addressed in the latest version.

**Action Required**:
1. If you cloned this repository before December 2, 2025, ensure you:
   - Update to the latest version
   - Never commit `.env` files containing tokens
   - Rotate any exposed API tokens immediately

---

## 🛡️ Security Best Practices

### 1. Environment Variables
**NEVER** commit sensitive information like API tokens to version control.

**✅ DO:**
```python
import os
HF_TOKEN = os.getenv("HF_TOKEN")
```

**❌ DON'T:**
```python
HF_TOKEN = "hf_xxxxxxxxxxxxx"  # Never do this!
```

### 2. .env File Protection
- Always add `.env` to `.gitignore` (already done in this project)
- Use `.env.example` as a template without real credentials
- Never share your `.env` file with others

### 3. Token Management
- Generate new tokens regularly
- Use tokens with minimal required permissions
- Revoke tokens immediately if exposed
- Don't share tokens via email, chat, or screenshots

### 4. HuggingFace Tokens
To get a HuggingFace token:
1. Visit https://huggingface.co/settings/tokens
2. Create a new token with read-only access
3. Request access to: https://huggingface.co/pyannote/speaker-diarization-3.1
4. Store in `.env` file: `HF_TOKEN=your_token_here`

---

## 🔍 Security Checklist for Contributors

Before committing code:
- [ ] No hardcoded credentials or tokens
- [ ] No sensitive file paths or personal information
- [ ] All secrets use environment variables
- [ ] `.env` file is in `.gitignore`
- [ ] Dependencies are up to date
- [ ] No unnecessary permissions requested

---

## 📦 Dependency Security

This project uses:
- `openai-whisper` - AI model for speech recognition
- `pyannote.audio` - Speaker diarization
- `torch` - Deep learning framework

**Recommendations:**
1. Keep dependencies updated:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. Check for vulnerabilities:
   ```bash
   pip install safety
   safety check
   ```

3. Use virtual environments:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

---

## 🚨 What to Do If Token is Exposed

If you accidentally commit a token:

1. **Immediately revoke the token**
   - HuggingFace: https://huggingface.co/settings/tokens

2. **Remove from Git history**
   ```bash
   # Remove file from history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (CAUTION!)
   git push origin --force --all
   ```

3. **Generate new credentials**
   - Create new token
   - Update your local `.env` file

4. **Notify maintainers**
   - Open a GitHub issue
   - Explain what was exposed

---

## 🔐 Data Privacy

### Audio Files
- This application processes audio files locally
- No audio data is sent to third parties (except for model downloads)
- Transcription results are stored locally

### Models
- Whisper models are downloaded from OpenAI
- Pyannote models are downloaded from HuggingFace
- Models are cached locally for reuse

### Telemetry
- This project does NOT collect any telemetry or usage data
- No analytics or tracking

---

## 📞 Contact

For security-related questions or concerns:
- Open a GitHub issue
- Label it with "security"
- Provide details (without exposing sensitive information)

---

## 🔄 Security Updates

**Last Updated**: December 2, 2025

### Version History
- **v1.1** (Dec 2, 2025): Added environment variable support, fixed token exposure
- **v1.0** (Dec 2, 2025): Initial release (security issues present)

---

**Remember**: Security is everyone's responsibility. Thank you for helping keep this project secure!
