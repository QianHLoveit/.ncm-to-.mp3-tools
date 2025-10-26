#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM to MP3 Converter
Command-line tool to convert NetEase Cloud Music (NCM) files to MP3 format.
"""

import os
import sys
import struct
import base64
import json
import hashlib
import binascii
from Crypto.Cipher import AES, ARC4
from Crypto.Util.Padding import unpad
from tqdm import tqdm
import mutagen
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC
from mutagen.mp3 import MP3

__version__ = "1.0.0"
__author__ = "NCM2MP3 Converter"

# Constants for NCM decryption
MAGIC_HEADER = b'CTENFDAM'
AES_KEY = b'hzHRAmso5kInbaxW'
META_XOR_KEY = 0x63
KEY_XOR_KEY = 0x64
HEADER = b'neteasecloudmusic'

def print_banner():
    """Print program banner"""
    banner = f"""
NCM to MP3 Converter v{__version__}
====================================
A command-line tool to convert NetEase Cloud Music (NCM) files to MP3 format.
"""
    print(banner)

def print_help():
    """Print help information"""
    help_text = """
Usage: ncm2mp3.py [options] <input_file_or_dir>

Options:
  -h, --help            Show this help message and exit
  -v, --version         Show program version
  -o, --output <dir>    Specify output directory (default: same as input)
  -q, --quiet           Quiet mode (suppress output except errors)
  -f, --force           Overwrite existing files without prompt

Examples:
  Convert a single file:
    python ncm2mp3.py song.ncm
    
  Convert all NCM files in a directory:
    python ncm2mp3.py /path/to/music
    
  Convert with custom output directory:
    python ncm2mp3.py -o /path/to/output song.ncm
"""
    print(help_text)

def is_ncm_file(file_path):
    """Check if a file is a valid NCM file"""
    if not os.path.isfile(file_path) or not file_path.lower().endswith('.ncm'):
        return False
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(len(MAGIC_HEADER))
            return header == MAGIC_HEADER
    except:
        return False

def get_ncm_files(input_path):
    """Get all NCM files from input path (file or directory)"""
    ncm_files = []
    
    if os.path.isfile(input_path):
        if is_ncm_file(input_path):
            ncm_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_ncm_file(file_path):
                    ncm_files.append(file_path)
    
    return ncm_files

def decrypt_ncm(ncm_file_path, debug=False):
    """Decrypt NCM file and return audio data and metadata"""
    try:
        with open(ncm_file_path, 'rb') as f:
            data = f.read()
        
        # Check magic header
        if not data.startswith(MAGIC_HEADER):
            raise ValueError("Not a valid NCM file")
        
        offset = len(MAGIC_HEADER)
        
        # Read key length
        key_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Read encrypted key
        encrypted_key = data[offset:offset+key_len]
        offset += key_len
        
        # Decrypt key with XOR and AES
        encrypted_key = bytes([b ^ KEY_XOR_KEY for b in encrypted_key])
        
        # Try different padding strategies for AES decryption
        padding_strategies = [
            # Standard PKCS#7 padding
            lambda data: data + bytes([16 - (len(data) % 16)]) * (16 - (len(data) % 16)) if len(data) % 16 != 0 else data,
            # Null padding
            lambda data: data.ljust(((len(data) + 15) // 16) * 16, b'\x00'),
            # No padding (for testing)
            lambda data: data
        ]
        
        decrypted_key = None
        for i, pad_func in enumerate(padding_strategies):
            try:
                padded_key = pad_func(encrypted_key)
                if len(padded_key) % 16 != 0:
                    continue
                    
                cipher = AES.new(AES_KEY, AES.MODE_ECB)
                temp_key = cipher.decrypt(padded_key)
                
                # Check if this decryption produced a valid key
                if HEADER in temp_key or len(temp_key.strip(b'\x00')) >= 16:
                    decrypted_key = temp_key
                    if debug:
                        print(f"Debug: Successfully decrypted key using padding strategy {i+1}")
                    break
                    
            except Exception as e:
                if debug:
                    print(f"Debug: Padding strategy {i+1} failed: {str(e)}")
        
        if decrypted_key is None:
            # Fallback to standard padding
            padding_length = 16 - (len(encrypted_key) % 16)
            if padding_length != 16:
                encrypted_key += bytes([padding_length]) * padding_length
            
            cipher = AES.new(AES_KEY, AES.MODE_ECB)
            decrypted_key = cipher.decrypt(encrypted_key)
        
        key = decrypted_key
        
        # Check header in decrypted key with more detailed error information
        # First, remove any leading null bytes that might be padding
        key = key.lstrip(b'\x00')
        
        if not key.startswith(HEADER):
            # Try different offsets to find the header
            header_found = False
            for i in range(len(key) - len(HEADER) + 1):
                if key[i:i+len(HEADER)] == HEADER:
                    print(f"Warning: Header found at offset {i}, not at beginning")
                    key = key[i+len(HEADER):]
                    header_found = True
                    break
            
            if not header_found:
                # Try to find the header by searching for the string
                key_str = key.decode('latin-1', errors='ignore')
                header_pos = key_str.find(HEADER.decode('utf-8'))
                
                if header_pos != -1:
                    print(f"Warning: Header found at position {header_pos} in string representation")
                    key = key[header_pos+len(HEADER):]
                    header_found = True
            
            if not header_found:
                # Try alternative header search methods
                # Check if key contains null-terminated header
                null_terminated_header = HEADER + b'\x00'
                if null_terminated_header in key:
                    pos = key.find(null_terminated_header)
                    print(f"Warning: Null-terminated header found at position {pos}")
                    key = key[pos+len(null_terminated_header):]
                    header_found = True
                else:
                    # Try to find the header with possible padding
                    for padding in [0, 1, 2, 3, 4, 5, 6, 7]:
                        padded_header = b'\x00' * padding + HEADER
                        if padded_header in key:
                            pos = key.find(padded_header)
                            print(f"Warning: Header with {padding} null bytes padding found at position {pos}")
                            key = key[pos+len(padded_header):]
                            header_found = True
                            break
            
            if not header_found:
                # As a last resort, try to use the entire decrypted key (excluding possible padding)
                # This might work for some newer NCM formats
                key = key.lstrip(b'\x00')  # Remove leading null bytes
                if len(key) >= 16:  # Minimum RC4 key length
                    print(f"Warning: Using fallback key extraction method")
                    print(f"Warning: Header not found but key length is sufficient")
                    header_found = True
                else:
                    # Show debug information
                    if debug:
                        print(f"Debug: Key length: {len(key)}")
                        print(f"Debug: First 32 bytes: {key[:32].hex()}")
                        print(f"Debug: Key as string: {key[:64].decode('latin-1', errors='replace')}")
                    raise ValueError(f"Invalid key header. Expected '{HEADER.decode('utf-8')}' at start of decrypted key.")
        
        # Remove any null bytes or garbage from the end of the key
        key = key.rstrip(b'\x00')
        
        # Ensure key is not empty
        if not key:
            raise ValueError("Decrypted key is empty")
        
        # Read metadata length
        meta_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Read encrypted metadata
        encrypted_meta = data[offset:offset+meta_len]
        offset += meta_len
        
        # Decrypt metadata with XOR, Base64 and AES
        encrypted_meta = bytes([b ^ META_XOR_KEY for b in encrypted_meta])
        
        if debug:
            print(f"Debug: Encrypted meta length: {len(encrypted_meta)}")
            print(f"Debug: Encrypted meta first 32 bytes: {encrypted_meta[:32].hex()}")
        
        try:
            encrypted_meta = base64.b64decode(encrypted_meta)
        except Exception as e:
            print(f"Warning: Base64 decode failed, trying with padding: {str(e)}")
            # Try adding padding if needed
            padding_needed = len(encrypted_meta) % 4
            if padding_needed:
                encrypted_meta += b'=' * (4 - padding_needed)
            encrypted_meta = base64.b64decode(encrypted_meta)
        
        if debug:
            print(f"Debug: Base64 decoded meta length: {len(encrypted_meta)}")
            print(f"Debug: Base64 decoded meta first 32 bytes: {encrypted_meta[:32].hex()}")
        
        # Ensure the encrypted metadata length is a multiple of AES block size
        padding_length = 16 - (len(encrypted_meta) % 16)
        if padding_length != 16:
            if debug:
                print(f"Debug: Adding {padding_length} bytes of padding to meta")
            encrypted_meta += bytes([padding_length]) * padding_length
        
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        meta = cipher.decrypt(encrypted_meta)
        
        if debug:
            print(f"Debug: Decrypted meta length: {len(meta)}")
            print(f"Debug: Decrypted meta first 64 bytes: {meta[:64].hex()}")
            print(f"Debug: Decrypted meta as string: {meta[:128].decode('utf-8', errors='replace')}")
        
        # Remove padding
        try:
            meta = unpad(meta, AES.block_size)
        except ValueError:
            # If unpad fails, try to find the JSON end manually
            print("Warning: Standard unpad failed, trying manual method")
            meta_str = meta.decode('utf-8', errors='ignore')
            json_end = meta_str.rfind('}')
            if json_end != -1:
                meta_str = meta_str[:json_end+1]
                meta = meta_str.encode('utf-8')
                print(f"Warning: Manually truncated to JSON at position {json_end}")
            else:
                raise
        
        meta = json.loads(meta.decode('utf-8'))
        
        if debug:
            print(f"Debug: Successfully parsed metadata: {json.dumps(meta, indent=2, ensure_ascii=False)}")
        
        # Skip CRC32
        offset += 4
        
        # Skip album cover (we'll handle this later from metadata)
        image_size = struct.unpack('<I', data[offset+5:offset+9])[0]
        offset += 9 + image_size
        
        # Decrypt audio data with RC4
        audio_data = data[offset:]
        
        if debug:
            print(f"Debug: Audio data length: {len(audio_data)}")
            print(f"Debug: Audio data first 32 bytes: {audio_data[:32].hex()}")
        
        try:
            cipher = ARC4.new(key)
            decrypted_audio = cipher.decrypt(audio_data)
            
            if debug:
                print(f"Debug: Decrypted audio length: {len(decrypted_audio)}")
                print(f"Debug: Decrypted audio first 32 bytes: {decrypted_audio[:32].hex()}")
                
                # Check if the decrypted audio starts with a known header
                if decrypted_audio.startswith(b'ID3'):
                    print("Debug: Decrypted audio appears to be MP3 with ID3 tag")
                elif decrypted_audio.startswith(b'fLaC'):
                    print("Debug: Decrypted audio appears to be FLAC")
                elif decrypted_audio[:4] == b'\xff\xfb' or decrypted_audio[:3] == b'\xff\xf3' or decrypted_audio[:3] == b'\xff\xf2':
                    print("Debug: Decrypted audio appears to be MP3")
                else:
                    # Try to find audio header later in the file
                    mp3_header_pos = decrypted_audio.find(b'\xff\xe3')
                    if mp3_header_pos != -1 and mp3_header_pos < 1024:
                        print(f"Debug: MP3 header found at position {mp3_header_pos}")
                        # Extract audio from header position
                        decrypted_audio = decrypted_audio[mp3_header_pos:]
                    else:
                        print("Warning: Decrypted audio does not have a recognizable header")
                    
        except Exception as e:
            print(f"Error during RC4 decryption: {str(e)}")
            raise
        
        return decrypted_audio, meta
    
    except Exception as e:
        raise Exception(f"Failed to decrypt NCM file: {str(e)}")

def write_temp_audio(audio_data):
    """Write decrypted audio data to a temporary file"""
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name

def add_metadata(mp3_file_path, meta):
    """Add metadata to MP3 file"""
    try:
        audio = MP3(mp3_file_path, ID3=ID3)
        
        # Add ID3 tags if not present
        try:
            audio.add_tags()
        except mutagen.id3.error:
            pass
        
        # Set basic metadata
        if 'musicName' in meta:
            audio.tags.add(TIT2(encoding=3, text=meta['musicName']))
        
        if 'artist' in meta:
            artists = [artist['name'] for artist in meta['artist']]
            audio.tags.add(TPE1(encoding=3, text=', '.join(artists)))
        
        if 'album' in meta:
            audio.tags.add(TALB(encoding=3, text=meta['album']))
        
        if 'genre' in meta:
            audio.tags.add(TCON(encoding=3, text=meta['genre']))
        
        if 'year' in meta:
            audio.tags.add(TDRC(encoding=3, text=str(meta['year'])))
        
        # Add album cover if available
        if 'albumPic' in meta:
            try:
                cover_data = base64.b64decode(meta['albumPic'])
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc=u'Cover',
                    data=cover_data
                ))
            except:
                pass
        
        audio.save()
        return True
    
    except Exception as e:
        print(f"Warning: Failed to add metadata: {str(e)}")
        return False

def convert_ncm_to_mp3(ncm_file_path, output_dir=None, force_overwrite=False, quiet=False, debug=False):
    """Convert a single NCM file to MP3"""
    try:
        # Get output file path
        if output_dir is None:
            output_dir = os.path.dirname(ncm_file_path)
        
        file_name = os.path.basename(ncm_file_path)
        mp3_file_name = os.path.splitext(file_name)[0] + '.mp3'
        mp3_file_path = os.path.join(output_dir, mp3_file_name)
        
        # Check if output file exists
        if os.path.exists(mp3_file_path) and not force_overwrite:
            if not quiet:
                response = input(f"File '{mp3_file_path}' already exists. Overwrite? (y/N): ")
            else:
                response = 'n'
            
            if response.lower() != 'y':
                if not quiet:
                    print("Skipping file.")
                return False
        
        if not quiet:
            print(f"\nProcessing: {file_name}")
        
        # Decrypt NCM file
        if not quiet:
            print("Decrypting NCM file...", end='', flush=True)
        
        decrypted_audio, meta = decrypt_ncm(ncm_file_path, debug=debug)
        
        if not quiet:
            print(" Done")
        
        # Write decrypted audio to temporary file
        temp_file_path = write_temp_audio(decrypted_audio)
        
        try:
            # Add metadata and save to final location
            if not quiet:
                print("Adding metadata...", end='', flush=True)
            
            # Copy temporary file to final location
            with open(temp_file_path, 'rb') as temp_file:
                with open(mp3_file_path, 'wb') as mp3_file:
                    mp3_file.write(temp_file.read())
            
            # Add metadata
            add_metadata(mp3_file_path, meta)
            
            if not quiet:
                print(" Done")
            
            return True
        
        finally:
            # Clean up temporary file
            os.remove(os.path.exists(temp_file_path) and os.remove(temp_file_path))
    
    except Exception as e:
        if not quiet:
            print(f"\nError processing {ncm_file_path}: {str(e)}")
        return False

def main():
    """Main function"""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert NetEase Cloud Music (NCM) files to MP3 format.')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output directory (default: same as input)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (suppress output except errors)')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing files without prompt')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{__version__}')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode (show detailed information)')
    
    args = parser.parse_args()
    
    # Print banner if not quiet
    if not args.quiet:
        print_banner()
    
    # Get NCM files
    ncm_files = get_ncm_files(args.input)
    
    if not ncm_files:
        print(f"Error: No NCM files found in '{args.input}'")
        sys.exit(1)
    
    # Create output directory if specified
    if args.output and not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
        except Exception as e:
            print(f"Error: Failed to create output directory: {str(e)}")
            sys.exit(1)
    
    # Process files
    if not args.quiet:
        print(f"\nFound {len(ncm_files)} NCM file(s) to process.")
    
    success_count = 0
    error_count = 0
    
    for i, ncm_file in enumerate(ncm_files, 1):
        if not args.quiet:
            print(f"\nFile {i}/{len(ncm_files)}:")
        
        if convert_ncm_to_mp3(ncm_file, args.output, args.force, args.quiet, args.debug):
            success_count += 1
        else:
            error_count += 1
    
    # Summary
    if not args.quiet:
        print(f"\n{'='*50}")
        print(f"Conversion complete!")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Total: {len(ncm_files)}")
        print(f"{'='*50}")
    
    sys.exit(0 if error_count == 0 else 1)

if __name__ == '__main__':
    main()
