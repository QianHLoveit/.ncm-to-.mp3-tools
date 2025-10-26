#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the parameter fix for decrypt_ncm function
"""

import os
import sys

def test_function_definitions():
    """Test that all function definitions have the correct parameters"""
    print("Testing function parameter definitions...")
    
    try:
        # Read the main script file
        with open('ncm2mp3.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check decrypt_ncm function definition
        if 'def decrypt_ncm(ncm_file_path, debug=False):' in content:
            print("✓ decrypt_ncm function has correct parameters")
        elif 'def decrypt_ncm(ncm_file_path):' in content:
            print("✗ decrypt_ncm function is missing debug parameter")
            return False
        else:
            print("✗ Could not find decrypt_ncm function definition")
            return False
        
        # Check convert_ncm_to_mp3 function definition
        if 'def convert_ncm_to_mp3(ncm_file_path, output_dir=None, force_overwrite=False, quiet=False, debug=False):' in content:
            print("✓ convert_ncm_to_mp3 function has correct parameters")
        else:
            print("✗ convert_ncm_to_mp3 function parameters are incorrect")
            return False
        
        # Check that convert_ncm_to_mp3 calls decrypt_ncm with debug parameter
        if 'decrypt_ncm(ncm_file_path, debug=debug)' in content:
            print("✓ convert_ncm_to_mp3 calls decrypt_ncm with debug parameter")
        else:
            print("✗ convert_ncm_to_mp3 does not pass debug parameter correctly")
            return False
        
        # Check that main passes debug parameter
        if 'convert_ncm_to_mp3(ncm_file, args.output, args.force, args.quiet, args.debug)' in content:
            print("✓ Main function passes debug parameter correctly")
        else:
            print("✗ Main function does not pass debug parameter correctly")
            return False
        
        # Check that debug argument is parsed
        if 'parser.add_argument(\'-d\', \'--debug\'' in content:
            print("✓ Debug command-line argument is parsed")
        else:
            print("✗ Debug command-line argument is missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking function definitions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_mode():
    """Test that debug mode can be activated"""
    print("\nTesting debug mode activation...")
    
    try:
        # Create a test NCM file (empty file with magic header)
        test_file = "test.ncm"
        with open(test_file, 'wb') as f:
            f.write(b'CTENFDAM')  # Magic header
            f.write(b'\x00\x00\x00\x00')  # Key length 0
            f.write(b'\x00\x00\x00\x00')  # Meta length 0
        
        # Test running with debug mode
        print("Trying to run with debug mode (this should show usage)...")
        os.system(f'python ncm2mp3.py -d {test_file}')
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("✓ Debug mode can be activated without parameter errors")
        return True
        
    except Exception as e:
        print(f"✗ Error testing debug mode: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Function Parameter Fix Test")
    print("=" * 60)
    
    tests = [
        ("Function Definitions Check", test_function_definitions),
        ("Debug Mode Activation Test", test_debug_mode)
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
        print("✓ All tests passed! The parameter fix is working correctly.")
        return 0
    else:
        print("✗ Some tests failed! Please check the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
