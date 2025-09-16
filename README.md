# 🛡️ YouTube2Sheets-Secure

A secure, enterprise-grade YouTube to Google Sheets automation tool with comprehensive credential protection and advanced security features.

## 🔐 Security Features

- **Zero Credential Exposure**: All API keys and credentials are stored in environment variables
- **Comprehensive .gitignore**: Protects sensitive files from accidental commits
- **Environment Template**: `.env.example` provides secure setup guidance
- **Security Verification**: Built-in tools to verify no sensitive data is exposed
- **Production Ready**: Designed with security-first principles

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/GRsoldier7/YouTube2Sheets-Secure.git
cd YouTube2Sheets-Secure
```

### 2. Set Up Environment
```bash
# Run the secure setup script
python setup_secure_environment.py

# This creates:
# - .env file with your API keys (protected by .gitignore)
# - credentials.json for Google Sheets (protected by .gitignore)
# - .env.example template for others
```

### 3. Configure Your Credentials
Edit the `.env` file with your actual API keys:
```env
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
YOUTUBE_API_KEY_BACKUP=your_backup_youtube_api_key_here
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

### 4. Run the Application
```bash
python youtube_to_sheets_gui.py
```

## 🔒 Security Verification

Before pushing any changes, run the security verification:
```bash
python verify_security.py
```

This ensures no sensitive data will be committed to the repository.

## 📁 Project Structure

```
YouTube2Sheets-Secure/
├── .env                    # Your API keys (IGNORED by git)
├── credentials.json        # Google Sheets credentials (IGNORED by git)
├── .env.example           # Template for others
├── .gitignore             # Comprehensive security protection
├── setup_secure_environment.py  # Secure setup script
├── verify_security.py     # Security verification tool
├── src/                   # Source code
├── docs/                  # Documentation
└── tests/                 # Test files
```

## 🛡️ Security Best Practices

1. **Never commit `.env` or `credentials.json`** - These are protected by `.gitignore`
2. **Use environment variables** - All sensitive data is loaded from environment
3. **Rotate credentials regularly** - Update API keys periodically
4. **Verify before pushing** - Always run `verify_security.py` before commits
5. **Use the template** - Share `.env.example` instead of actual credentials

## 🔧 Features

- **YouTube Data API Integration**: Fetch video data from YouTube channels
- **Google Sheets Automation**: Write data directly to Google Sheets
- **Advanced Filtering**: Filter videos by duration, keywords, and more
- **GUI Interface**: Modern, user-friendly graphical interface
- **Scheduler**: Automated job scheduling and execution
- **API Optimization**: Efficient API usage with quota management
- **Error Handling**: Comprehensive error handling and logging

## 📊 Supported Data

- Video Title
- Video URL
- View Count
- Like Count
- Comment Count
- Duration
- Published Date
- Channel Information
- Thumbnail URLs

## 🚨 Security Notice

This repository is designed with security-first principles. All sensitive credentials are:
- Stored in environment variables
- Protected by comprehensive `.gitignore`
- Never committed to version control
- Verified before any push operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `python verify_security.py` to ensure security
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For security concerns or questions, please open an issue in the repository.

---

**Remember**: Security is everyone's responsibility. Always verify your changes before pushing to ensure no sensitive data is exposed.