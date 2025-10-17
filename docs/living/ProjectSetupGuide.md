# Project Setup Guide - YouTube2Sheets with PolyChronos Ω
**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Active  

---

## Overview

This guide will help you set up the YouTube2Sheets project with the integrated PolyChronos Ω framework. The framework provides a comprehensive development environment with AI personas, structured planning templates, and quality assurance processes.

---

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space
- **Internet**: Required for API access and package installation

### Required Accounts
- **Google Account**: For Google Sheets API access
- **YouTube API Key**: For YouTube Data API v3 access
- **GitHub Account**: For version control (optional)

---

## Installation Steps

### Step 1: Clone the Repository
```bash
# Clone the repository
git clone https://github.com/your-username/YouTube2Sheets.git
cd YouTube2Sheets

# Verify the PolyChronos Ω framework structure
ls -la
# You should see: .cursor/, context/, docs/, .cursorrules
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import customtkinter; print('CustomTkinter installed successfully')"
python -c "import google.oauth2; print('Google API client installed successfully')"
```

### Step 4: Configure Environment Variables
1. Create `.env` using `setup_secure_environment.py` if not already done.
2. Edit `.env` with values for `YOUTUBE_API_KEY`, `YOUTUBE_API_KEY_BACKUP`, `GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON`, and `GOOGLE_SHEET_ID`.
3. Optional: Add `ENABLE_INTELLIGENT_SCHEDULER=true` when you want advanced scheduler features.

### Step 5: Launch the GUI
```bash
python -m src.gui.main_app
```

### Step 6: Scheduler Runner (Optional)
```bash
python -m src.backend.scheduler_runner --status
python -m src.backend.scheduler_runner --dry-run
python -m src.backend.scheduler_runner
```

The CLI reads logging configuration from `src/config/logging.json` and writes to `logs/youtube2sheets.log`.

### Step 7: Desktop Shortcut (Windows)
```bash
python scripts/create_shortcut.py
```
This creates `YouTube2Sheets.lnk` on the desktop launching `launch_youtube2sheets.bat`.

### Step 8: Set Up Google Sheets API
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a New Project** or select existing project
3. **Enable Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
5. **Download Credentials**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key" > "JSON"
   - Save as `credentials.json` in project root
6. **Share Google Sheet**:
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (from credentials.json)
   - Give "Editor" permissions

### Step 9: Set Up YouTube Data API
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select the same project** used for Google Sheets
3. **Enable YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. **Create API Key**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key to your `.env` file
5. **Restrict API Key** (Recommended):
   - Click on the API key
   - Under "API restrictions", select "Restrict key"
   - Select "YouTube Data API v3"
   - Save changes

### Step 10: Configure Cursor IDE
1. **Open Cursor IDE**
2. **Open the project folder**
3. **Set up PolyChronos Ω system prompt**:
   - Go to Cursor Settings
   - Find "System Prompt" or "Custom Instructions"
   - Copy the contents of `.cursor/prompts/PolyChronos-Omega.md`
   - Paste as your system prompt
4. **Configure .cursorrules**:
   - The `.cursorrules` file is already configured
   - Cursor will automatically use these rules

---

## PolyChronos Ω Framework Usage

### Understanding the Framework
The PolyChronos Ω framework provides:
- **AI Personas**: Specialized AI experts for different aspects of development
- **Planning Templates**: Structured documents for project planning
- **Quality Gates**: Defined checkpoints for quality assurance
- **Context Engineering**: Rich context for AI interactions

### Available AI Personas
#### Strategy & Leadership
- **🎯 Project Manager**: Orchestrates development, manages risks, and drives phase gates
- **📜 The Loremaster**: Maintains the living documentation corpus and ensures knowledge fidelity
- **🔭 Visionary Planner**: Maps the opportunity space, market forces, and Jobs-to-be-Done
- **🗺️ Product Strategist**: Shapes roadmap priorities and translates user value into actionable stories

#### Engineering & Delivery
- **🏛️ Savant Architect**: Owns holistic system architecture and technical cohesion
- **🧬 Data Engineer**: Crafts resilient data pipelines and enforces data quality
- **⚙️ Back End Architect**: Designs and scales the server-side foundation and APIs
- **🎨 Front End Architect**: Builds modern, accessible user interfaces in CustomTkinter
- **👷 Lead Engineer**: Leads implementation craftsmanship and mentors the engineering guild
- **🚀 DevOps Lead**: Automates delivery, observability, and environment reliability
- **🧠 Nexus Architect**: Designs autonomous agents, AI workflows, and cognitive services
- **🎨 UX Designer**: Ensures intuitive, inclusive, and delightful user experiences
- **⚡ Performance Engineer**: Optimizes system responsiveness, scalability, and efficiency

#### Quality, Security & Diagnostics
- **🛡️ Security Engineer (The Sentinel)**: Engineers defense-in-depth and governs credential safety
- **🧪 QA Director**: Architects multi-layer testing strategy and quality metrics
- **🩺 The Diagnostician**: Leads Δ-Protocol investigations, root cause analysis, and fix verification

### Using AI Personas
To use a specific persona, start your request with:
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
The framework includes several planning templates:
- **Discovery.md**: Market research and opportunity analysis
- **PRD.md**: Product requirements and user stories
- **Architecture.md**: Technical architecture, automation architecture, and AI enablement
- **TestPlan.md**: Testing strategy covering core, GUI, and AI modules
- **QualityMandate.md**: Quality standards, gates, and success metrics
- **FrameworkIntegrationSummary.md**: Overview of PolyChronos Ω activation and assets

### Quality Gates
Each phase has defined quality gates:
1. **Discovery & Planning**: Requirements validation
2. **Design & Architecture**: Technical design approval
3. **Implementation**: Code quality validation
4. **Testing & Validation**: Quality assurance complete
5. **Deployment & Release**: Production readiness

---

## Development Workflow

### Daily Development Process
1. **Start with Context**: Review relevant documentation
2. **Choose Persona**: Select appropriate AI persona for your task
3. **Follow Quality Gates**: Ensure quality standards are met
4. **Update Documentation**: Keep living documentation current
5. **Test Thoroughly**: Run all tests before committing

### Code Quality Process
1. **Write Code**: Follow project standards
2. **Run Tests**: Execute unit, integration, and AI insight tests
3. **Code Review**: Use AI personas for targeted reviews (Lead Engineer, QA Director, Security Engineer)
4. **Security Check**: Run security validation and credential audits
5. **Documentation**: Update relevant documentation with the Loremaster

### Testing Process
1. **Unit Tests**: Test individual components (core, GUI, AI modules)
2. **Integration Tests**: Test component interactions and AI ↔ Sheets orchestration
3. **System Tests**: Test complete workflows and autonomous runs
4. **Security Tests**: Validate security controls and API key handling
5. **Performance Tests**: Ensure performance and AI latency requirements
6. **Accessibility Tests**: Validate CustomTkinter UI accessibility guidelines

---

## Project Structure

```
YouTube2Sheets/
├── .cursor/                          # Cursor IDE configuration
│   └── prompts/
│       └── PolyChronos-Omega.md     # Main system prompt
├── context/                          # AI persona definitions
│   └── personas/
│       ├── BackEndArchitect.md
│       ├── DataEngineer.md
│       ├── DevOpsLead.md
│       ├── FrontEndArchitect.md
│       ├── LeadEngineer.md
│       ├── NexusArchitect.md
│       ├── PerformanceEngineer.md
│       ├── ProductManager.md
│       ├── ProductStrategist.md
│       ├── ProjectManager.md
│       ├── QADirector.md
│       ├── SecurityEngineer.md
│       ├── TheDiagnostician.md
│       ├── TheLoremaster.md
│       ├── UXDesigner.md
│       └── VisionaryPlanner.md
├── docs/                            # Project documentation
│   ├── living/                      # Active documentation
│   │   ├── Discovery.md
│   │   ├── PRD.md
│   │   ├── Architecture.md
│   │   ├── TestPlan.md
│   │   ├── QualityMandate.md
│   │   └── ProjectSetupGuide.md
│   └── archives/                    # Historical documentation
├── .cursorrules                     # Project quality rules
├── .env                            # Environment variables (not in git)
├── credentials.json                # Google service account (not in git)
├── requirements.txt                # Python dependencies
├── youtube_to_sheets.py            # Core business logic
├── youtube_to_sheets_gui.py        # GUI application
├── setup_secure_environment.py     # Security setup script
├── verify_security.py              # Security validation
└── README.md                       # Project overview
```

---

## Security Setup

### Credential Management
1. **Never commit credentials**: All sensitive data in `.env` file
2. **Use environment variables**: Load credentials from environment
3. **Rotate credentials regularly**: Update API keys periodically
4. **Verify security**: Run `python verify_security.py` before commits

### Security Validation
```bash
# Run security verification
python verify_security.py

# Expected output:
# ✅ Security verification passed
# ✅ No sensitive data found in code
# ✅ Environment variables properly configured
```

### Security Best Practices
- **Use strong API keys**: Generate secure, random API keys
- **Restrict API access**: Limit API keys to required services
- **Monitor usage**: Track API usage and costs
- **Regular audits**: Perform security audits regularly

---

## Testing Setup

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=youtube_to_sheets

# Run specific test file
pytest tests/test_youtube_api.py

# Run with verbose output
pytest -v
```

### Test Categories
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test API integrations
- **Security Tests**: Test security controls
- **Performance Tests**: Test performance requirements

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'customtkinter'
# Solution: Install missing package
pip install customtkinter
```

#### 2. API Key Issues
```bash
# Error: Invalid API key
# Solution: Check .env file and API key validity
python -c "import os; print(os.getenv('YOUTUBE_API_KEY'))"
```

#### 3. Google Sheets Access Issues
```bash
# Error: Permission denied
# Solution: Check service account permissions
# Ensure service account email has access to the sheet
```

#### 4. GUI Not Starting
```bash
# Error: GUI fails to start
# Solution: Check Python version and dependencies
python --version  # Should be 3.8+
pip list | grep customtkinter
```

### Getting Help
1. **Check Documentation**: Review relevant docs in `docs/living/`
2. **Use AI Personas**: Ask specific personas for help
3. **Check Logs**: Review log files for error details
4. **Run Diagnostics**: Use built-in diagnostic tools

---

## Advanced Configuration

### Customizing AI Personas
1. **Edit Persona Files**: Modify files in `context/personas/`
2. **Add New Personas**: Create new persona files with charter, principles, responsibilities, success metrics
3. **Update System Prompt**: Modify `.cursor/prompts/PolyChronos-Omega.md` to surface new roles and maxims

### Customizing Quality Rules
1. **Edit .cursorrules**: Modify project quality standards
2. **Add New Rules**: Define additional quality requirements
3. **Update Templates**: Modify planning templates as needed

### Integration with Other Tools
- **Git Hooks**: Add pre-commit hooks for quality checks
- **CI/CD**: Integrate with continuous integration systems
- **Monitoring**: Add application monitoring and alerting

---

## Maintenance

### Regular Maintenance Tasks
1. **Update Dependencies**: Keep packages up to date
2. **Security Updates**: Apply security patches
3. **Documentation Updates**: Keep documentation current
4. **Performance Monitoring**: Monitor system performance
5. **Backup**: Regular backup of important data

### Monitoring and Alerting
- **API Usage**: Monitor API quota usage
- **Error Rates**: Track application errors
- **Performance**: Monitor response times
- **Security**: Monitor security events

---

## Support and Resources

### Documentation
- **Project Docs**: `docs/living/` directory
- **API Documentation**: Google and YouTube API docs
- **Framework Docs**: PolyChronos Ω framework documentation

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community discussions and Q&A
- **Contributing**: Guidelines for contributing to the project

### Professional Support
- **Consulting**: Professional development consulting
- **Training**: Team training and workshops
- **Custom Development**: Custom feature development

---

## Next Steps

### After Setup
1. **Review Documentation**: Read through all planning documents
2. **Run Tests**: Execute the test suite to verify setup
3. **Try the GUI**: Launch the application and test basic functionality
4. **Explore Personas**: Try using different AI personas
5. **Customize**: Adapt the framework to your specific needs

### Development Workflow
1. **Start with Discovery**: Use Discovery.md for new features
2. **Plan with PRD**: Use PRD.md for requirements
3. **Design with Architecture**: Use Architecture.md for technical design
4. **Implement with Personas**: Use AI personas for development
5. **Test with TestPlan**: Use TestPlan.md for testing
6. **Deploy with Quality**: Use QualityMandate.md for quality assurance

---

**Document Owner:** Project Manager  
**Review Cycle:** Monthly  
**Next Review:** February 2025
