# Google Sheets Permissions Fix

## 🚨 CRITICAL: Google Sheets Access Denied

The service account needs to be granted access to your Google Spreadsheet.

## Service Account Email
```
n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com
```

## Spreadsheet URL
```
https://docs.google.com/spreadsheets/d/13WluwYBj5EPg5-zpvAtDVHtekAwPUnayNArKrMAOxAE/edit?gid=0#gid=0
```

## Steps to Fix (REQUIRED)

1. **Open the Google Spreadsheet** in your browser
2. **Click the "Share" button** (top right corner)
3. **Add the service account email**: `n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com`
4. **Set permissions to "Viewer"** (minimum required)
5. **Click "Send"**

## Verification

After granting permissions, run:
```bash
python test_api_connections.py
```

You should see:
```
✅ Google Sheets connection successful!
📋 Found X tabs: [tab names]
```

## Security Note

This service account is specifically created for this application and has limited permissions. It can only access spreadsheets you explicitly share with it.
