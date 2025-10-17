# Getting Started with Modern YouTube2Sheets GUI

## Quick Start

### 1. Launch the Application

**Option A: Using the Launcher**
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

### 2. First Time Setup

1. **API Configuration**: Enter your YouTube API key and Google Sheets credentials
2. **Theme Selection**: Choose between light and dark themes
3. **Preferences**: Configure your preferred settings

## Interface Overview

### Main Window Layout

The modern GUI features a clean, organized layout with:

- **Header**: Application title and theme toggle
- **Tab Navigation**: Sync, Scheduler, Analytics, and Logs tabs
- **Main Content**: Context-specific content for each tab
- **Status Bar**: Real-time status and progress information

### Tab Structure

#### 🔄 Sync Tab
- **Configuration Section**: API keys, spreadsheet settings
- **Filter Configuration**: Video filters and search criteria
- **Progress Section**: Real-time sync progress and status
- **Control Buttons**: Start/stop sync operations

#### ⏰ Scheduler Tab
- **Scheduler Configuration**: Sheet ID and tab settings
- **Scheduler Controls**: Run once or enable continuous scheduling
- **Status Display**: Current scheduler status and history

#### 📊 Analytics Tab
- **Data Visualization**: Charts and graphs
- **Statistics**: Sync statistics and performance metrics
- **Export Options**: Data export and reporting

#### 📝 Logs Tab
- **Log Console**: Real-time log display with filtering
- **Search and Filter**: Find specific log entries
- **Export Logs**: Save logs to file

## Basic Operations

### Starting a Sync

1. **Configure APIs**: Enter your YouTube API key and Google Sheets URL
2. **Set Filters**: Configure video filters (duration, keywords, etc.)
3. **Click Start**: Press the "Start Sync" button or use `Ctrl+Enter`
4. **Monitor Progress**: Watch the progress bar and status indicators

### Using Keyboard Shortcuts

The application supports extensive keyboard shortcuts:

#### Essential Shortcuts
- `Ctrl+Enter`: Start sync
- `Ctrl+Shift+Enter`: Stop sync
- `F5`: Refresh data
- `Ctrl+?`: Show all shortcuts
- `F11`: Toggle fullscreen

#### Navigation Shortcuts
- `Tab`: Move to next field
- `Shift+Tab`: Move to previous field
- `Ctrl+Home`: Go to first field
- `Ctrl+End`: Go to last field

#### File Operations
- `Ctrl+N`: New configuration
- `Ctrl+O`: Open configuration
- `Ctrl+S`: Save configuration
- `Ctrl+Q`: Quit application

### Customizing the Interface

#### Theme Selection
- **Dark Theme**: Modern dark interface (default)
- **Light Theme**: Clean light interface
- **Auto Theme**: Follows system theme

#### Layout Options
- **Window Size**: Resizable window with memory
- **Tab Order**: Customizable tab arrangement
- **Component Visibility**: Show/hide specific components

## Advanced Features

### Glassmorphism Effects

The interface features modern glassmorphism effects:
- **Floating Cards**: Elevated content containers
- **Translucent Backgrounds**: Subtle transparency effects
- **Smooth Animations**: Fluid transitions and hover effects

### Enhanced Scrolling

- **Momentum Scrolling**: Natural scroll behavior
- **Auto-scroll**: Automatic scrolling to new content
- **Smooth Transitions**: Fluid scroll animations

### Accessibility Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: Compatible with assistive technologies
- **High Contrast Mode**: Enhanced visibility options
- **Large Text Mode**: Increased text size for readability

### Performance Monitoring

- **Real-time Metrics**: CPU and memory usage
- **Progress Tracking**: Detailed operation progress
- **Performance Alerts**: Notifications for performance issues

## Configuration

### API Setup

#### YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Copy the API key to the application

#### Google Sheets Setup
1. Create a new Google Sheet
2. Copy the sheet ID from the URL
3. Ensure the sheet is accessible
4. Enter the sheet URL in the application

### Filter Configuration

#### Duration Filters
- **Minimum Duration**: Set minimum video length
- **Maximum Duration**: Set maximum video length
- **Use Sliders**: Interactive duration selection

#### Keyword Filters
- **Include Keywords**: Videos must contain these keywords
- **Exclude Keywords**: Videos must not contain these keywords
- **Case Sensitivity**: Toggle case-sensitive matching

#### Advanced Filters
- **Channel Filters**: Specific YouTube channels
- **Date Range**: Video publication date range
- **View Count**: Minimum/maximum view counts

## Troubleshooting

### Common Issues

#### Application Won't Start
1. **Check Python Installation**: Ensure Python 3.8+ is installed
2. **Install Dependencies**: Run `pip install -r requirements.txt`
3. **Check Permissions**: Ensure write permissions for logs directory
4. **Verify CustomTkinter**: Install with `pip install customtkinter`

#### API Errors
1. **Invalid API Key**: Verify YouTube API key is correct
2. **Quota Exceeded**: Check API quota limits
3. **Sheet Access**: Ensure Google Sheet is accessible
4. **Network Issues**: Check internet connection

#### Performance Issues
1. **Memory Usage**: Close other applications
2. **Large Datasets**: Use filters to reduce data size
3. **Background Tasks**: Check for running background processes
4. **System Resources**: Monitor CPU and memory usage

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Logs are stored in the `logs/` directory:
- `youtube2sheets.log`: Main application log
- `error.log`: Error-specific logs
- `performance.log`: Performance metrics

## Tips and Best Practices

### Performance Optimization
1. **Use Filters**: Apply filters to reduce data processing
2. **Batch Operations**: Process videos in batches
3. **Monitor Resources**: Keep an eye on memory usage
4. **Regular Cleanup**: Clear logs and temporary files

### Data Management
1. **Backup Configurations**: Save your settings regularly
2. **Export Data**: Export important data periodically
3. **Version Control**: Keep track of configuration changes
4. **Documentation**: Document your setup and processes

### Security
1. **Secure API Keys**: Don't share API keys
2. **Regular Updates**: Keep the application updated
3. **Access Control**: Limit sheet access appropriately
4. **Audit Logs**: Review logs regularly

## Getting Help

### Documentation
- **User Guide**: This comprehensive guide
- **API Reference**: Technical documentation
- **FAQ**: Frequently asked questions
- **Troubleshooting**: Common issues and solutions

### Support
- **Log Files**: Check logs for error details
- **Debug Mode**: Enable debug logging
- **Community**: Join the user community
- **Issues**: Report bugs and feature requests

### Updates
- **Version Check**: Check for updates regularly
- **Changelog**: Review new features and fixes
- **Migration Guide**: Upgrade instructions
- **Compatibility**: System requirements

## Next Steps

1. **Explore Features**: Try different tabs and options
2. **Customize Settings**: Adjust preferences to your needs
3. **Learn Shortcuts**: Master keyboard shortcuts for efficiency
4. **Advanced Usage**: Explore advanced features and configurations
5. **Contribute**: Share feedback and suggestions

## Additional Resources

- **Video Tutorials**: Step-by-step video guides
- **Sample Configurations**: Pre-configured setups
- **Templates**: Ready-to-use templates
- **Community Examples**: User-contributed examples

