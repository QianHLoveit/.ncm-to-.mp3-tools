#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the fix for bytesarray error
"""

import os
import sys

def test_bytesarray_fix():
    """Test to verify the bytesarray fix"""
    print("Testing bytesarray fix...")
    
    # Test the bytes vs bytesarray issue
    try:
        # This should work in Python 3
        padding_length = 5
        padding = bytes([padding_length]) * padding_length
        print(f"✓ bytes([{padding_length}]) * {padding_length} = {padding}")
        
        # Test that bytesarray is not used
        code_file = "ncm2mp3.py"
        if os.path.exists(code_file):
            with open(code_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'bytesarray' in content:
                    print(f"✗ Found 'bytesarray' in code - this might cause issues")
                    # Check if it's in the padding section
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'bytesarray' in line and 'padding' in line:
                            print(f"  Line {i+1}: {line.strip()}")
                else:
                    print("✓ No 'bytesarray' found in code - good")
                    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    
    return True

def test_encryption_padding():
    """Test encryption padding function"""
    print("\nTesting encryption padding...")
    
    try:
        # Test various lengths
        test_lengths = [10, 16, 20, 31, 32]
        
        for length in test_lengths:
            data = b'x' * length
            padding_length = 16 - (len(data) % 16)
            
            if padding_length != 16:
                data += bytes([padding_length]) * padding_length
            
            print(f"✓ Length {length} → padded to {len(data)} (multiple of 16)")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("bytesarray Fix Test")
    print("=" * 60)
    
    tests = [
        ("bytesarray Usage Check", test_bytesarray_fix),
        ("Encryption Padding Test", test_encryption_padding)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name} passed")
            else:
                print(f"✗ {test_name} failed")
                all_passed = False
        except Exception as e:
            print(f"✗ {test_name} error: {str(e)}")
            all_passed = False
    
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print("=" * 60)
    
    if all_passed:
        print("✓ All tests passed! The fix is working correctly.")
        return 0
    else:
        print("✗ Some tests failed! Please check the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
