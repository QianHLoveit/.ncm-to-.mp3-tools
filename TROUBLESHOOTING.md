# Troubleshooting Guide

## Common Error Messages and Solutions

### 1. "Data must be aligned to block boundary in ECB mode"

**Solution**: This error occurs when the encrypted data length is not a multiple of AES block size (16 bytes). The latest version of the tool includes a fix for this issue.

**How to fix**:
- Ensure you're using the latest version of the script
- If the error persists, try re-downloading the NCM file

### 2. "Invalid key header"

**Solution**: This error occurs when the decrypted key doesn't contain the expected header "neteasecloudmusic".

**Possible causes and fixes**:

#### 1. **File Corruption**
- **Fix**: Try re-downloading the NCM file from NetEase Cloud Music
- Verify the file plays correctly in the NetEase Cloud Music client

#### 2. **Newer NCM Format**
- **Fix**: The latest version of the tool includes improved header detection
- Run with debug mode to get more information:
  ```bash
  python ncm2mp3.py -d your_file.ncm
  ```

#### 3. **Encryption Key Changes**
- **Fix**: The tool uses the standard AES key for NCM decryption
- If you're using an older version, update to the latest release
- Try the debug tool to analyze the file structure:
  ```bash
  python debug_ncm.py your_file.ncm
  ```

#### 4. **Partial File Download**
- **Fix**: Check if the file size seems reasonable
- Incomplete downloads often cause decryption failures
- Compare file sizes with other working NCM files

#### 5. **Alternative Decryption Methods**
If the standard method fails, try these alternatives:

1. **Use the debug mode with detailed analysis**:
   ```bash
   python ncm2mp3.py -d your_file.ncm
   ```

2. **Run the dedicated debug tool**:
   ```bash
   python debug_ncm.py your_file.ncm
   ```

3. **Try manual header search**:
   The tool now automatically searches for the header at different offsets, but you can also:
   - Check if the header appears later in the decrypted key
   - Look for the string "neteasecloudmusic" in the debug output

4. **Verify the AES key**:
   Ensure the tool is using the correct AES key for decryption
   The standard key is built into the tool

If none of these solutions work, please provide the debug output when reporting the issue.

### 3. "Failed to decrypt NCM file"

**Solution**: General decryption failure.

**Troubleshooting steps**:
1. Verify the file is a valid NCM file
2. Check if the file is not corrupted (try playing it in NetEase Cloud Music)
3. Try re-downloading the file
4. Update to the latest version of the converter

### 4. "FFmpeg not found"

**Solution**: FFmpeg is required for audio processing.

**Installation instructions**:
- **Windows**: Download from [FFmpeg官网](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora)

### 5. "Permission denied"

**Solution**: The tool doesn't have permission to read the input file or write to the output directory.

**How to fix**:
- Check file permissions: `ls -l /path/to/file.ncm`
- Run the tool with appropriate permissions: `sudo python ncm2mp3.py /path/to/file.ncm`
- Choose a different output directory with write permissions

### 6. "No NCM files found"

**Solution**: The input path doesn't contain any valid NCM files.

**Check these**:
- Verify the file path is correct
- Ensure the files have the .ncm extension
- Check if the files are actually NCM files (not renamed MP3 files)

## General Troubleshooting Steps

### 1. Update the Tool

```bash
# If using git
git pull

# If downloaded manually, re-download the latest version
```

### 2. Verify Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### 3. Check File Integrity

```bash
# Check if the file is a valid NCM file
python -c "
with open('your_file.ncm', 'rb') as f:
    header = f.read(8)
    print(f'File header: {header}')
    print(f'Expected header: b\'CTENFDAM\'')
    print(f'Valid NCM file: {header == b\'CTENFDAM\'}')
"
```

### 4. Try with a Different File

Sometimes the issue is specific to a particular file. Try converting a different NCM file to see if the problem persists.

### 5. Use Debug Tools

The project includes two debug tools to help diagnose issues:

#### Debug Mode
Run the converter with debug mode enabled to get detailed information:
```bash
python ncm2mp3.py -d your_file.ncm
```

#### NCM Analyzer Tool
Use the dedicated debug tool to analyze NCM file structure:
```bash
python debug_ncm.py your_file.ncm
```

This tool provides comprehensive analysis of:
- File header and structure
- Key section analysis
- AES decryption process
- Metadata section validation
- Version detection

### 6. Check for Newer NCM Formats

NetEase occasionally updates the NCM encryption format. If you're getting "Invalid key header" errors with all files:

1. Check if the files are from the latest version of NetEase Cloud Music
2. Look for updates to the converter tool
3. The debug tool can help identify newer formats:
   ```bash
   python debug_ncm.py your_file.ncm
   ```

### 5. Run in Verbose Mode

```bash
python -v ncm2mp3.py your_file.ncm
```

This will show more detailed output that can help diagnose the problem.

## Advanced Solutions

### 1. Manually Check File Structure

```bash
# Install hexdump (if not already installed)
sudo apt-get install bsdmainutils  # Debian/Ubuntu
# or
sudo dnf install util-linux-user   # Fedora

# Check the first 16 bytes of the file
hexdump -C -n 16 your_file.ncm
```

The output should start with `43 54 45 4E 46 44 41 4D` (which is "CTENFDAM" in ASCII).

### 2. Check Python Version

```bash
python --version
```

Ensure you're using Python 3.6 or higher.

### 3. Create a Test Environment

```bash
# Create a virtual environment
python -m venv test_env

# Activate it
source test_env/bin/activate  # Linux/macOS
# or
test_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the tool
python ncm2mp3.py your_file.ncm
```

## If All Else Fails

If you've tried all these solutions and are still having problems:

1. Create a detailed bug report including:
   - The exact error message
   - The command you ran
   - The output of `python --version`
   - The output of `pip list`
   - The first 16 bytes of your NCM file (using hexdump)

2. Contact the developer with this information for further assistance.
