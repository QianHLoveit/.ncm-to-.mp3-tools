# NCM to MP3 Converter

A command-line tool to convert NetEase Cloud Music (NCM) files to MP3 format.

## Features

- **Batch Conversion**: Convert multiple NCM files at once
- **Metadata Preservation**: Keep all original metadata (title, artist, album, cover art)
- **Fast Processing**: Efficient decryption and conversion
- **User-Friendly**: Simple command-line interface with progress feedback
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Debug Tools**: Built-in debugging features to diagnose conversion issues
- **Robust Error Handling**: Improved error recovery and informative error messages
- **Silent Operation**: No annoying system beep sounds on errors (Windows)

## Installation

### Prerequisites

- Python 3.6 or higher
- FFmpeg (required for audio processing)

### Install FFmpeg

- **Windows**: Download from [FFmpeg官网](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python ncm2mp3.py input.ncm
```

### Command-Line Options

```bash
-h, --help            Show this help message and exit
-v, --version         Show program version
-o, --output <dir>    Specify output directory (default: same as input)
-q, --quiet           Quiet mode (suppress output except errors)
-f, --force           Overwrite existing files without prompt
-d, --debug           Debug mode (show detailed information for troubleshooting)
```

### Examples

1. **Convert a single file**:
   ```bash
   python ncm2mp3.py song.ncm
   ```

2. **Convert all NCM files in a directory**:
   ```bash
   python ncm2mp3.py /home/user/music/ncm
   ```

3. **Convert with custom output directory**:
   ```bash
   python ncm2mp3.py -o /home/user/music/mp3 song.ncm
   ```

4. **Force overwrite existing files**:
   ```bash
   python ncm2mp3.py -f song.ncm
   ```

5. **Run in debug mode (for troubleshooting)**:
   ```bash
   python ncm2mp3.py -d song.ncm
   ```

6. **Quiet mode with force overwrite**:
   ```bash
   python ncm2mp3.py -q -f /path/to/music/directory
   ```

## Examples

1. Convert a single file:
   ```bash
   python ncm2mp3.py song.ncm
   ```

2. Convert all NCM files in a directory:
   ```bash
   python ncm2mp3.py /home/user/music
   ```

3. Convert with custom output and force overwrite:
   ```bash
   python ncm2mp3.py -o ~/music/mp3 -f ~/music/ncm/*.ncm
   ```

## How It Works

1. **Decryption**: The tool decrypts NCM files using AES and RC4 algorithms
2. **Metadata Extraction**: Extracts and preserves all metadata (title, artist, album, etc.)
3. **Audio Conversion**: Converts the decrypted audio to MP3 format
4. **Tagging**: Adds ID3 tags and album cover to the output MP3 file

## Notes

- This tool is for personal use only. Make sure you have the right to convert the files.
- The quality of the output MP3 depends on the original NCM file quality.
- Album covers are automatically added to the MP3 files when available.

## Troubleshooting

Please refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for detailed error solutions and troubleshooting steps.

### System Beep Sound Issue

If you hear an annoying system beep when running the tool on Windows, please see [NOISE_FIX.md](NOISE_FIX.md) for solutions to eliminate this sound.

### Debug Tools

The project includes powerful debug tools to help diagnose conversion issues:

#### 1. Debug Mode
Run the converter with debug mode enabled to get detailed information about the conversion process:

```bash
python ncm2mp3.py -d your_file.ncm
```

This will show:
- File structure analysis
- Decryption process details
- Metadata extraction information
- Audio format verification

#### 2. NCM File Analyzer
Use the dedicated debug tool to perform a comprehensive analysis of NCM files:

```bash
python debug_ncm.py your_file.ncm
```

This tool provides:
- Detailed file structure analysis
- Key section validation
- AES decryption debugging
- Metadata format checking
- Version detection
- Known pattern recognition

### Common Issues

1. **FFmpeg not found**: Make sure FFmpeg is installed and added to your system PATH.
2. **Permission errors**: Ensure you have read/write permissions for input/output directories.
3. **Corrupted files**: Some files may fail to convert. Try to re-download them.
4. **Decryption errors**: Use the debug tools to diagnose issues with NCM file decryption.
5. **"Invalid key header"**: This usually indicates a newer NCM format or file corruption. See troubleshooting guide for solutions.

### Running Tests

To verify if the tool is working correctly on your system, you can run the test script:

```bash
python test_conversion.py
```

This will test the decryption and conversion functionality with NCM files in your current directory.

For testing the specific fix for bytesarray issue:

```bash
python test_fix.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
