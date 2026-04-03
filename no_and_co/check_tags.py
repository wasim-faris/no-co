import re
import sys

def check_tags(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all django tags
    tags = re.findall(r'\{%\s*(.*?)\s*%\}', content)
    
    stack = []
    line_nums = []
    
    # We need to track line numbers for better reporting
    lines = content.splitlines()
    all_tags_with_lines = []
    for i, line in enumerate(lines):
        found = re.findall(r'\{%\s*(.*?)\s*%\}', line)
        for t in found:
            all_tags_with_lines.append((t.strip(), i + 1))

    for tag_full, line_num in all_tags_with_lines:
        tag_parts = tag_full.split()
        if not tag_parts:
            continue
        tag_name = tag_parts[0]
        
        if tag_name in ['if', 'for', 'with', 'block', 'comment', 'filter', 'spaceless']:
            stack.append((tag_name, line_num))
        elif tag_name == 'elif' or tag_name == 'else':
            if not stack or stack[-1][0] not in ['if', 'for']: # else can be in for too (for-else)
                print(f"Error: {tag_name} at line {line_num} without matching if/for")
        elif tag_name.startswith('end'):
            expected = tag_name[3:]
            if not stack:
                print(f"Error: {tag_name} at line {line_num} without opening tag")
                continue
            
            actual_name, actual_line = stack.pop()
            if actual_name != expected:
                print(f"Mismatch: Found {tag_name} at line {line_num}, but expected end{actual_name} (from line {actual_line})")
                # Put it back to try to keep going? No, usually one error cascades.
    
    if stack:
        for name, line in stack:
            print(f"Error: Unclosed {name} from line {line}")

if __name__ == "__main__":
    check_tags(sys.argv[1])
