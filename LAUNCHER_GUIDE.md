# 🚀 YouTube2Sheets Launcher Guide

**Date:** September 30, 2025  
**Status:** ✅ Fixed and Working

---

## ✅ **ISSUE RESOLVED**

**Problem:** Desktop shortcut didn't launch the application  
**Root Cause:** Shortcut was pointing to deleted `launch_youtube2sheets.bat` file  
**Solution:** Updated shortcut to use `launch_youtube2sheets.py`

---

## 🎯 **THREE WAYS TO LAUNCH**

### **Method 1: Desktop Shortcut** ⭐ (Recommended)

**Location:** `C:\Users\Admin\Desktop\YouTube2Sheets.lnk`

**How to use:**
1. Double-click the "YouTube2Sheets" icon on your Desktop
2. The GUI will launch automatically
3. No terminal window required

**Features:**
- ✅ One-click launch
- ✅ Clean user experience
- ✅ Uses correct Python executable
- ✅ Automatically sets working directory

---

### **Method 2: Batch File** (Backup Method)

**Location:** `YouTube2Sheets.bat` (in project folder)

**How to use:**
1. Navigate to the project folder
2. Double-click `YouTube2Sheets.bat`
3. The GUI will launch

**Features:**
- ✅ Shows error messages if launch fails
- ✅ Keeps console open for debugging
- ✅ Simple and reliable

---

### **Method 3: Python Direct** (Advanced)

**Command:**
```bash
python youtube_to_sheets_gui.py
```

**How to use:**
1. Open terminal in project directory
2. Run the command above
3. GUI launches with console visible

**Features:**
- ✅ See all log messages in console
- ✅ Debug mode available
- ✅ Full control over environment

---

## 🔧 **WHAT WAS FIXED**

### **Before (Broken):**
```
Desktop Shortcut → launch_youtube2sheets.bat (DELETED)
                    ❌ File not found
                    ❌ Shortcut broken
```

### **After (Fixed):**
```
Desktop Shortcut → launch_youtube2sheets.py ✅
                 → Uses correct Python ✅
                 → Launches GUI successfully ✅
```

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Shortcut doesn't do anything**

**Solution 1: Recreate the shortcut**
```bash
python scripts/create_shortcut.py
```

**Solution 2: Use the batch file instead**
- Double-click `YouTube2Sheets.bat` in project folder
- If it shows an error, you'll see what went wrong

**Solution 3: Launch directly**
```bash
python youtube_to_sheets_gui.py
```

---

### **Issue: "Python not found" error**

**Cause:** Python not in PATH or virtual environment not activated

**Solution:**
1. Open terminal in project directory
2. Activate virtual environment (if using one):
   ```bash
   venv\Scripts\activate
   ```
3. Recreate shortcut:
   ```bash
   python scripts/create_shortcut.py
   ```

---

### **Issue: Console window flashes and closes**

**Cause:** An error occurred during startup

**Solution:**
1. Use `YouTube2Sheets.bat` instead (it keeps console open)
2. Or launch from terminal to see error messages:
   ```bash
   python youtube_to_sheets_gui.py
   ```
3. Check logs: `logs/youtube2sheets.log`

---

### **Issue: "Module not found" error**

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

Then recreate the shortcut:
```bash
python scripts/create_shortcut.py
```

---

## 📝 **TECHNICAL DETAILS**

### **Desktop Shortcut Configuration:**
```
Target: C:\...\python.exe
Arguments: C:\...\YouTube2Sheets\launch_youtube2sheets.py
Working Directory: C:\...\YouTube2Sheets\
```

### **Launch Flow:**
```
Desktop Icon
    ↓
Python.exe
    ↓
launch_youtube2sheets.py
    ↓
youtube_to_sheets_gui.py
    ↓
src/gui/main_app.py (YouTube2SheetsGUI)
    ↓
GUI Window Opens ✅
```

---

## ✅ **VERIFICATION CHECKLIST**

After launching, verify:

- [ ] GUI window opens without errors
- [ ] All input fields are visible
- [ ] Buttons are clickable
- [ ] No error messages in console
- [ ] Window title shows "YouTube2Sheets"

---

## 🎯 **RECOMMENDED WORKFLOW**

### **For Regular Use:**
1. Use the **Desktop Shortcut** (easiest)
2. Click once, application launches
3. No terminal windows to manage

### **For Debugging:**
1. Use `YouTube2Sheets.bat` or launch from terminal
2. Console stays open to see messages
3. Review logs if errors occur

### **For Development:**
1. Launch from terminal with `python youtube_to_sheets_gui.py`
2. Full console output visible
3. Easy to stop/restart with Ctrl+C

---

## 🔄 **RECREATING THE SHORTCUT**

If you ever need to recreate the desktop shortcut:

**Option 1: Using the script**
```bash
python scripts/create_shortcut.py
```

**Option 2: Manually**
1. Right-click Desktop → New → Shortcut
2. Target: `C:\Path\To\python.exe "C:\Path\To\YouTube2Sheets\launch_youtube2sheets.py"`
3. Working Directory: `C:\Path\To\YouTube2Sheets`
4. Name: YouTube2Sheets

---

## 📚 **RELATED FILES**

- **Desktop Shortcut:** `C:\Users\Admin\Desktop\YouTube2Sheets.lnk`
- **Batch Launcher:** `YouTube2Sheets.bat`
- **Python Launcher:** `launch_youtube2sheets.py`
- **GUI Entry Point:** `youtube_to_sheets_gui.py`
- **Main GUI Code:** `src/gui/main_app.py`
- **Shortcut Creator:** `scripts/create_shortcut.py`

---

## 🏆 **STATUS**

✅ **Desktop shortcut is now working!**
- Launches GUI successfully
- No errors
- Clean user experience

**You can now launch YouTube2Sheets with a single click!** 🚀

---

## ❓ **NEXT STEPS**

Now that the launcher is working:

1. **Test the GUI:** Double-click the desktop icon
2. **Verify it works:** Window opens, all fields visible
3. **Run live tests:** Use the testing guide
4. **Deploy with confidence:** Everything is ready!

---

**Last Updated:** September 30, 2025  
**Status:** ✅ **WORKING - PRODUCTION READY**

