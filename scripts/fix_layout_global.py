import re
import os

# Define the replacement pattern
old_pattern = r'class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'
new_pattern = 'class="w-full max-w-6xl xl:max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'

# List of files to update (authenticated pages only, not alternative home pages)
files_to_update = [
    'app/templates/base.html',
    'app/templates/customers/list.html',
    'app/templates/products/list.html',
    'app/templates/products/create.html',
    'app/templates/products/edit.html',
    'app/templates/invoices/list.html',
    'app/templates/invoices/create.html',
    'app/templates/reports/gst_summary.html',
    'app/templates/reports/customer_ledger.html',
]

updated_count = 0
for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the pattern
        new_content = content.replace(old_pattern, new_pattern)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_count += 1
            print(f"✓ Updated: {file_path}")
        else:
            print(f"- No changes: {file_path}")
    else:
        print(f"✗ Not found: {file_path}")

print(f"\n✅ Updated {updated_count} files with full-width responsive layout")
