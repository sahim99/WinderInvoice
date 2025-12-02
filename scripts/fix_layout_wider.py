import re
import os

# Define the replacement - use even wider containers
old_pattern = 'class="w-full max-w-6xl xl:max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'
new_pattern = 'class="w-full max-w-screen-xl 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8'

# List of ALL files to update
files_to_update = [
    'app/templates/home.html',
    'app/templates/base.html',
    'app/templates/dashboard_ultimate.html',
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
            print(f"- No changes needed: {file_path}")
    else:
        print(f"✗ Not found: {file_path}")

print(f"\n✅ Updated {updated_count} files to use max-w-screen-xl (1280px) and 2xl:max-w-screen-2xl (1536px)")
print("This will utilize much more screen width on large displays!")
