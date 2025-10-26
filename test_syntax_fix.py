#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the syntax fix for f-string issue
"""

import os
import sys
import ast

def check_syntax():
    """Check if the main script has valid Python syntax"""
    print("Checking Python syntax...")
    
    try:
        # Read the main script file
        with open('ncm2mp3.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the code to check for syntax errors
        ast.parse(content)
        
        print("✓ No syntax errors found")
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error found: {e}")
        print(f"  Line {e.lineno}, Column {e.offset}: {e.text.strip()}")
        return False
    except Exception as e:
        print(f"✗ Error checking syntax: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_fstring_lines():
    """Check specific lines that had f-string issues"""
    print("\nChecking f-string lines...")
    
    try:
        # Read the main script file
        with open('ncm2mp3.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check line 309 (where the issue was)
        line_number = 309
        if line_number <= len(lines):
            line = lines[line_number - 1]
            if 'print(f"' in line and line.strip().endswith('")'):
                print(f"✓ Line {line_number} has properly closed f-string")
            else:
                print(f"✗ Line {line_number} may have f-string issues: {line.strip()}")
                return False
        
        # Check other f-strings for similar issues
        problematic_lines = []
        for i, line in enumerate(lines, 1):
            if 'print(f"' in line and not line.strip().endswith(('")', '")\n')):
                # Check if the next line continues the string
                if i < len(lines) and lines[i].strip().startswith(('"', "'")):
                    continue  # This is intentional multi-line string
                problematic_lines.append((i, line.strip()))
        
        if problematic_lines:
            print(f"✗ Found potential f-string issues in {len(problematic_lines)} lines:")
            for line_num, line_content in problematic_lines:
                print(f"  Line {line_num}: {line_content}")
            return False
        else:
            print("✓ All f-strings appear to be properly formatted")
            return True
            
    except Exception as e:
        print(f"✗ Error checking f-strings: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_run_simple():
    """Test running a simple command to catch runtime errors"""
    print("\nTesting simple script execution...")
    
    try:
        # Create a minimal test NCM file
        test_file = "test_syntax.ncm"
        with open(test_file, 'wb') as f:
            f.write(b'CTENFDAM')  # Magic header
            f.write(b'\x00\x00\x00\x00')  # Key length 0
            f.write(b'\x00\x00\x00\x00')  # Meta length 0
        
        # Run the script with help option to check if it can start
        result = os.system('python ncm2mp3.py -h >nul 2>&1')
        
        if result == 0:
            print("✓ Script can be executed without syntax errors")
        else:
            print("✗ Script execution failed (may indicate syntax error)")
            return False
            
    except Exception as e:
        print(f"✗ Error during test execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("Syntax Fix Verification Test")
    print("=" * 60)
    
    tests = [
        ("Syntax Check", check_syntax),
        ("F-string Validation", check_fstring_lines),
        ("Script Execution Test", test_run_simple)
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
        print("✓ All tests passed! The syntax fix is working correctly.")
        return 0
    else:
        print("✗ Some tests failed! Please check the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
