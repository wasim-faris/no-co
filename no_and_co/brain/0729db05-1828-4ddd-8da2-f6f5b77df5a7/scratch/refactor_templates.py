import os
import re

files = [
    r'd:\first-ecom\no-co\no_and_co\products\templates\variant\admin-variants.html',
    r'd:\first-ecom\no-co\no_and_co\products\templates\product\admin-product-details.html',
    r'd:\first-ecom\no-co\no_and_co\products\templates\product\product-form.html',
    r'd:\first-ecom\no-co\no_and_co\products\templates\product\admin-products.html',
    r'd:\first-ecom\no-co\no_and_co\order_management\templates\order_management\inventory_list.html',
    r'd:\first-ecom\no-co\no_and_co\coupon\templates\coupon\admin_coupons.html',
    r'd:\first-ecom\no-co\no_and_co\admin_dashboard\templates\admin-user-management.html'
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if '{% extends' in content[:100]:
        print(f'Already refactored {f}')
        continue

    # Extract Title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else 'Admin Panel - NØ & CO'

    # Extract Style
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    style = style_match.group(1) if style_match else ''
    style_block = f"<style>{style}</style>" if style else ''

    # Find where <aside> ends
    aside_start = content.find('<aside')
    if aside_start == -1:
        print(f'No aside found in {f}')
        continue
        
    # The aside end can be tricky if there are nested asides, but usually there's only one or we want the first closing tag.
    # Actually admin-product-details has multiple <aside> tags
    # Let's find the first <aside ...> and its closing </aside>
    def find_closing_tag(text, start_idx, tag_name):
        # Very simple tag matcher
        count = 1
        idx = start_idx
        while count > 0 and idx < len(text):
            next_open = text.find(f'<{tag_name}', idx)
            next_close = text.find(f'</{tag_name}>', idx)
            
            if next_close == -1:
                return -1
                
            if next_open != -1 and next_open < next_close:
                count += 1
                idx = next_open + len(f'<{tag_name}')
            else:
                count -= 1
                idx = next_close + len(f'</{tag_name}>')
        return idx
    
    aside_end = find_closing_tag(content, aside_start + 6, 'aside')
    
    if aside_end != -1:
        after_aside = content[aside_end:]
        # Find the main div wrapper
        wrapper_match = re.search(r'<div class="[^"]*flex-1[^"]*flex-col[^"]*">', after_aside)
        if wrapper_match:
            content_part = after_aside[wrapper_match.end():]
        else:
            content_part = after_aside
            
        # Optional: check if there's a Toast Container before aside
        toast_start = content.find('<!-- Toast Container -->')
        toast_str = ''
        if toast_start != -1 and toast_start < aside_start:
            # find end of toast container
            sidebar_start = content.find('<aside', toast_start)
            if sidebar_start != -1:
                toast_str = content[toast_start:sidebar_start]

        # Fix bottom part: remove </body></html> and wrap scripts in extra_scripts
        content_part = content_part.replace('</body>', '').replace('</html>', '').strip()
        
        # We need to split scripts at the bottom
        script_match = re.search(r'(<script>.*?</script>.*?)$', content_part, re.DOTALL)
        if script_match:
            scripts_part = script_match.group(1)
            main_content = content_part[:script_match.start()]
        else:
            scripts_part = ''
            main_content = content_part
            
        new_content = f"""{{% extends 'admin_base/base.html' %}}

{{% block title %}}{title}{{% endblock %}}

{{% block extra_head %}}
{style_block}
{{% endblock %}}

{{% block content %}}
{toast_str}
{main_content}
{{% endblock %}}

{{% block extra_scripts %}}
{scripts_part}
{{% endblock %}}
"""
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Refactored {f}')
