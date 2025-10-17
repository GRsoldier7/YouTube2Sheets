# 🛡️ YouTube2Sheets - Modern YouTube to Google Sheets Automation

A secure, enterprise-grade YouTube to Google Sheets automation tool with a **stunning modern GUI**, comprehensive credential protection, and advanced security features, now enhanced with the **PolyChronos Ω v5.0** AI development framework and **MCP tool integration**.

## 🎨 Modern GUI Features

The application now features a **stunning modern interface** built with CustomTkinter:

- **🌟 Glassmorphism Design**: Floating cards with translucent backgrounds
- **⚡ Smooth Animations**: Fluid transitions and hover effects
- **🎯 Responsive Layout**: Adapts to different screen sizes
- **🌙 Dark/Light Themes**: Automatic theme switching
- **⌨️ Keyboard Shortcuts**: 50+ shortcuts for power users
- **♿ Accessibility**: Screen reader support and keyboard navigation
- **📊 Real-time Progress**: Live status updates and progress tracking
- **🔧 Performance Optimized**: Async operations and smooth scrolling

## 🚀 PolyChronos Ω Integration

This project now includes the **PolyChronos Ω v5.0** framework, providing:
- **AI Personas**: Specialized AI experts for different development aspects
- **Structured Planning**: Comprehensive planning templates and documentation
- **Quality Assurance**: Built-in quality gates and testing strategies
- **Context Engineering**: Rich context for AI-powered development
- **MCP Tool Integration**: Enhanced development with Model Context Protocol tools

### Available AI Personas
- **🎯 Project Manager**: Orchestrates development and manages risks
- **🏛️ Savant Architect**: Designs system architecture
- **🎨 Front End Architect**: Creates modern user interfaces
- **⚙️ Back End Architect**: Builds core functionality
- **🛡️ Security Engineer**: Ensures security and compliance
- **🧪 QA Director**: Manages testing and quality assurance

## 🔧 MCP Tool Integration

This project leverages **Model Context Protocol (MCP) tools** for enhanced development:

- **📚 Context7**: Enhanced documentation and library support
- **🐙 GitHub Integration**: Version control and collaboration
- **🗂️ File System Tools**: Advanced file operations and organization
- **🧠 Sequential Thinking**: AI-powered analysis and planning
- **🌐 Web Scraping**: Data collection and research capabilities
- **🗺️ Google Maps**: Location-based features and geocoding

## 🔐 Security Features

- **Zero Credential Exposure**: All API keys and credentials are stored in environment variables
- **Comprehensive .gitignore**: Protects sensitive files from accidental commits
- **Environment Template**: `env_example.txt` provides secure setup guidance
- **Security Verification**: Built-in tools to verify no sensitive data is exposed
- **Production Ready**: Designed with security-first principles

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/GRsoldier7/YouTube2Sheets.git
cd YouTube2Sheets
```

### 2. Set Up Environment

```bash
# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Modern GUI

**Option A: Using the Launcher (Recommended)**
```bash
python LAUNCH_GUI.pyw
```

**Option B: Direct Launch**
```bash
python -c "from src.gui.modern_app import ModernYouTube2SheetsGUI; ModernYouTube2SheetsGUI().run()"
```

**Option C: Batch File (Windows)**
```bash
LAUNCH_YouTube2Sheets.bat
```

### 4. Configure Cursor IDE

1. **Open Cursor IDE** and open the project folder
2. **Set up PolyChronos Ω system prompt**:
   - Go to Cursor Settings > System Prompt
   - Copy contents of `.cursor/prompts/PolyChronos-Omega.md`
   - Paste as your system prompt
3. **Configure .cursorrules**: Already configured for the project

### 4. Set Up Environment

```bash
# Run the secure setup script
python setup_secure_environment.py

# This creates:
# - .env file with your API keys (protected by .gitignore)
# - credentials.json for Google Sheets (protected by .gitignore)
# - .env.example template for others
```

### 5. Configure Your Credentials

Edit the `.env` file with your actual API keys:

```bash
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
YOUTUBE_API_KEY_BACKUP=your_backup_youtube_api_key_here
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

### 6. Run the Application

```bash
python -m src.gui.main_app
```

### 7. Scheduler CLI (Optional)

```bash
python -m src.backend.scheduler_runner --status
python -m src.backend.scheduler_runner --dry-run
python -m src.backend.scheduler_runner
```

Enable the intelligent scheduler add-on:

```bash
set ENABLE_INTELLIGENT_SCHEDULER=true  # PowerShell: $env:ENABLE_INTELLIGENT_SCHEDULER="true"
python -m src.backend.scheduler_runner
```

## 🎭 Using PolyChronos Ω Framework

### AI Personas
To use a specific AI persona, start your request with:
```
As the [Persona Name], I need to [describe your request]
```

**Examples:**
```
As the Savant Architect, I need to design the data flow for video processing.
As the Front End Architect, I need to create a modern progress indicator.
As the Security Engineer, I need to validate our credential management.
```

### Planning Templates
The framework includes comprehensive planning documents:
- **Discovery.md**: Market research and opportunity analysis
- **PRD.md**: Product requirements and user stories
- **Architecture.md**: Technical architecture and design
- **TestPlan.md**: Testing strategy and test cases
- **QualityMandate.md**: Quality standards and processes

### Quality Gates
Each development phase has defined quality gates:
1. **Discovery & Planning**: Requirements validation
2. **Design & Architecture**: Technical design approval
3. **Implementation**: Code quality validation
4. **Testing & Validation**: Quality assurance complete
5. **Deployment & Release**: Production readiness

## 🔒 Security Verification

Before pushing any changes, run the security verification:

```bash
python verify_security.py
```

This ensures no sensitive data will be committed to the repository.

## 📁 Project Structure

```
YouTube2Sheets/
├── src/
│   ├── backend/
│   │   ├── api_optimizer.py
│   │   ├── data_processor.py
│   │   ├── exceptions.py
│   │   ├── filters.py
│   │   ├── intelligent_scheduler/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── engine.py
│   │   ├── scheduler_runner.py
│   │   ├── scheduler_sheet_manager.py
│   │   └── youtube2sheets.py
│   ├── config/
│   │   ├── gui.json
│   │   ├── loader.py
│   │   └── logging.json
│   └── gui/
│       ├── __init__.py
│       └── main_app.py
├── scripts/
│   └── create_shortcut.py            # Optional Windows desktop shortcut helper
├── youtube_to_sheets.py              # Compatibility shim exporting backend APIs
├── youtube_to_sheets_gui.py          # Thin launcher calling src.gui.main_app
├── launch_youtube2sheets.bat         # Updated Windows launcher
├── launch_youtube2sheets.py
├── launch_youtube2sheets.sh
├── CURRENT_SYSTEM_STATE.md
├── docs/
│   ├── living/
│   │   ├── Architecture.md
│   │   ├── PRD.md
│   │   └── …
│   └── archives/
│       └── *.md (historical reports)
```

### Quick Start (Updated)
1. `pip install -r requirements.txt`
2. `python -m src.gui.main_app`
3. Windows shortcut: double-click `launch_youtube2sheets.bat` or run `python scripts/create_shortcut.py`

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
- **AI Insight Engine**: Engagement scoring, sentiment analysis, and actionable recommendations

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