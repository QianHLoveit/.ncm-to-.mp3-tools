# Fixing System Beep Sound Issue

## Problem Description
When running the ncm2mp3 converter, you might hear an annoying system beep sound every time an error occurs. This is especially noticeable on Windows systems.

## Root Cause
The system beep occurs because:
1. The Windows Command Prompt produces a beep sound when it encounters the ASCII Bell character (ASCII code 7, represented as `\a`)
2. Some error messages or exception traces might contain control characters that trigger this beep
3. The default error printing in Python can sometimes include these characters

## Solution Implemented

I've updated the code to prevent system beeps by:

1. **Filtering out control characters** from error messages:
   ```python
   # Remove ASCII control characters except newlines
   error_msg = ''.join(char for char in error_msg if char.isprintable() or char == '\n')
   ```

2. **Enhancing error handling** to avoid generating beep-triggering characters

3. **Improving NCM decryption** to reduce errors in the first place:
   - Added multiple AES padding strategies
   - Enhanced key header detection with fallback methods
   - Better handling of different NCM file formats

## Additional Steps to Eliminate Beeps

### For Windows Users:

#### Method 1: Disable System Beep Temporarily
Run this command in Command Prompt before using the converter:
```cmd
net stop beep
```

To re-enable later:
```cmd
net start beep
```

#### Method 2: Disable System Beep Permanently
1. Press `Win + R` and type `devmgmt.msc` to open Device Manager
2. Go to "View" > "Show hidden devices"
3. Expand "Non-Plug and Play Drivers"
4. Right-click on "Beep" and select "Properties"
5. Go to the "Driver" tab
6. Click "Stop" to stop the service
7. Set "Startup type" to "Disabled"
8. Click "OK"

#### Method 3: Use PowerShell Instead of Command Prompt
PowerShell doesn't produce beep sounds by default. You can run the converter using:
```powershell
python ncm2mp3.py your_file.ncm
```

#### Method 4: Redirect Output to a File
If you still hear beeps, you can redirect output to a file:
```cmd
python ncm2mp3.py your_file.ncm > output.log 2>&1
```
Then view the log file with:
```cmd
notepad output.log
```

### For Linux/macOS Users:
These systems typically don't produce beep sounds for command-line errors, but if you experience it:

1. Disable the bell in terminal preferences
2. Or run:
   ```bash
   xset b off  # For Linux X11
   ```

## Testing the Fix

After applying these changes, test with:
```bash
python ncm2mp3.py -d your_file.ncm
```

If you still hear beeps, please:
1. Check if the error occurs in PowerShell
2. Try redirecting output to a file
3. Verify if other command-line tools also produce beeps (system-wide issue)

## Additional Notes

The latest version of the converter also includes:
- Improved NCM decryption with multiple padding strategies
- Enhanced error recovery for different NCM formats
- Better debug information without beep-triggering characters

These improvements should reduce both the frequency of errors and the associated beep sounds.
