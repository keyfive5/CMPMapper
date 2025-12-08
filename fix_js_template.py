#!/usr/bin/env python3
"""
Script to fix JavaScript template literals in cmp_mapper_pro.py
Replace all template literals with string concatenation to avoid f-string escaping issues
"""

import re

# Read the file
with open('cmp_mapper_pro.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all JavaScript template literals with ${{}} pattern
# We need to replace them with string concatenation

# Pattern to find template literals: `...${{...}}...`
pattern = r'`([^`]*)\$\{\{([^}]+)\}\}([^`]*)`'

def replace_template_literal(match):
    before = match.group(1)
    expr = match.group(2)
    after = match.group(3)
    # Convert to string concatenation
    return "'" + before + "' + " + expr + " + '" + after + "'"

# Replace template literals
new_content = re.sub(pattern, replace_template_literal, content)

print("Fixed template literals")
print(f"Original length: {len(content)}")
print(f"New length: {len(new_content)}")

