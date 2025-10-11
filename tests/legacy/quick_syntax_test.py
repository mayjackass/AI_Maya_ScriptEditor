"""
Quick test for syntax error detection
"""

# Test code with syntax errors
test_code = '''
print("unterminated string

if True
    pass

def bad():
print("bad indent")

x == = 5
'''

# Direct syntax check using compile
try:
    compile(test_code, '<test>', 'exec')
    print("No syntax errors found by compile()")
except SyntaxError as e:
    print(f"compile() found ONE error: Line {e.lineno}: {e.msg}")

# Now test line by line
lines = test_code.strip().split('\n')
errors = []

for i, line in enumerate(lines, 1):
    if not line.strip() or line.strip().startswith('#'):
        continue
    
    # Check common issues
    if '"' in line and line.count('"') % 2 != 0:
        errors.append(f"Line {i}: Unterminated string")
    
    if line.strip().endswith(':') is False and any(line.strip().startswith(kw) for kw in ['if ', 'def ', 'for ', 'while ']):
        if ':' not in line:
            errors.append(f"Line {i}: Missing colon")
    
    if line.startswith(' ') and 'def ' in lines[max(0, i-2):i]:
        if not line.startswith('    '):
            errors.append(f"Line {i}: Bad indentation")

print(f"\nLine-by-line analysis found {len(errors)} errors:")
for error in errors:
    print(f"  - {error}")

print(f"\nThis demonstrates that compile() only finds the FIRST error, but line analysis can find multiple.")