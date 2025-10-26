#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for NCM to MP3 conversion
"""

import os
import sys
import tempfile
import shutil
from ncm2mp3 import decrypt_ncm, convert_ncm_to_mp3, get_ncm_files

def test_decryption():
    """Test NCM decryption function"""
    print("Testing NCM decryption...")
    
    # Check if there are NCM files in the current directory
    ncm_files = get_ncm_files('.')
    
    if not ncm_files:
        print("No NCM files found in current directory. Skipping decryption test.")
        return False
    
    # Test decryption with the first NCM file
    test_file = ncm_files[0]
    print(f"Testing with file: {test_file}")
    
    try:
        decrypted_audio, meta = decrypt_ncm(test_file)
        print(f"✓ Decryption successful")
        print(f"  Audio length: {len(decrypted_audio)} bytes")
        print(f"  Metadata extracted: {json.dumps(meta, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"✗ Decryption failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion():
    """Test full conversion process"""
    print("\nTesting full conversion...")
    
    # Check if there are NCM files in the current directory
    ncm_files = get_ncm_files('.')
    
    if not ncm_files:
        print("No NCM files found in current directory. Skipping conversion test.")
        return False
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary output directory: {temp_dir}")
        
        # Test conversion with the first NCM file
        test_file = ncm_files[0]
        print(f"Converting file: {test_file}")
        
        try:
            success = convert_ncm_to_mp3(test_file, temp_dir, force_overwrite=True, quiet=False)
            
            if success:
                print("✓ Conversion successful")
                
                # Check output file
                output_file = os.path.join(temp_dir, os.path.splitext(os.path.basename(test_file))[0] + '.mp3')
                if os.path.exists(output_file):
                    print(f"✓ Output file created: {output_file}")
                    print(f"  File size: {os.path.getsize(output_file)} bytes")
                    
                    # Try to read metadata with mutagen
                    try:
                        from mutagen.mp3 import MP3
                        from mutagen.id3 import ID3, TIT2, TPE1, TALB
                        
                        audio = MP3(output_file, ID3=ID3)
                        print(f"✓ Metadata read successfully")
                        
                        if 'TIT2' in audio.tags:
                            print(f"  Title: {audio.tags['TIT2'].text[0]}")
                        if 'TPE1' in audio.tags:
                            print(f"  Artist: {audio.tags['TPE1'].text[0]}")
                        if 'TALB' in audio.tags:
                            print(f"  Album: {audio.tags['TALB'].text[0]}")
                            
                    except Exception as e:
                        print(f"✗ Failed to read metadata: {str(e)}")
                
                return True
            else:
                print("✗ Conversion failed")
                return False
                
        except Exception as e:
            print(f"✗ Conversion error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_batch_conversion():
    """Test batch conversion"""
    print("\nTesting batch conversion...")
    
    # Check if there are NCM files in the current directory
    ncm_files = get_ncm_files('.')
    
    if len(ncm_files) < 2:
        print(f"Found only {len(ncm_files)} NCM file(s). Skipping batch test.")
        return False
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary output directory: {temp_dir}")
        print(f"Converting {len(ncm_files)} files...")
        
        success_count = 0
        error_count = 0
        
        for i, ncm_file in enumerate(ncm_files[:3]):  # Test first 3 files
            print(f"\nFile {i+1}/{len(ncm_files[:3])}: {os.path.basename(ncm_file)}")
            
            try:
                success = convert_ncm_to_mp3(ncm_file, temp_dir, force_overwrite=True, quiet=True)
                
                if success:
                    print("✓ Success")
                    success_count += 1
                else:
                    print("✗ Failed")
                    error_count += 1
                    
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                error_count += 1
        
        print(f"\nBatch conversion results:")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        
        return success_count > 0

def main():
    """Main test function"""
    print("=" * 60)
    print("NCM to MP3 Converter Test Suite")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Decryption Test", test_decryption),
        ("Conversion Test", test_conversion),
        ("Batch Conversion Test", test_batch_conversion)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Running {test_name}")
        print('=' * 60)
        
        try:
            result = test_func()
            if result:
                print(f"\n{test_name}: ✓ PASSED")
            else:
                print(f"\n{test_name}: ✗ FAILED")
                all_passed = False
        except Exception as e:
            print(f"\n{test_name}: ✗ ERROR - {str(e)}")
            all_passed = False
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print("=" * 60)
    
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    import json
    sys.exit(main())
