# Script to make FAB only show on main pages (not sub-pages)
import re

# Read the current base.html
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the FAB HTML to only show on main pages
old_fab = '''    <!-- Floating Action Button (New Invoice) - Only for logged in users -->
    {% if user %}
    <a href="/invoices/new" class="fab md:hidden fixed bottom-20 right-6 z-40 w-14 h-14 rounded-full flex items-center justify-center text-blue-400 hover:text-blue-300 no-print" title="New Invoice">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
        </svg>
    </a>
    {% endif %}'''

new_fab = '''    <!-- Floating Action Button (New Invoice) - Only on main pages -->
    {% if user %}
    {% set main_pages = ['/dashboard', '/invoices', '/customers', '/products', '/reports/gst-summary'] %}
    {% set is_main_page = request.url.path in main_pages or request.url.path == '/' %}
    {% if is_main_page %}
    <a href="/invoices/new" class="fab md:hidden fixed bottom-20 right-6 z-40 w-14 h-14 rounded-full flex items-center justify-center text-blue-400 hover:text-blue-300 no-print" title="New Invoice">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
        </svg>
    </a>
    {% endif %}
    {% endif %}'''

content = content.replace(old_fab, new_fab)

# Write the updated content
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ FAB visibility updated successfully!")
print("FAB will now only show on main pages:")
print("  - Dashboard (/dashboard)")
print("  - Invoices List (/invoices)")
print("  - Customers List (/customers)")
print("  - Products List (/products)")
print("  - Reports (/reports/gst-summary)")
print("")
print("FAB will NOT show on:")
print("  - New Invoice (/invoices/new)")
print("  - New Customer (/customers/new)")
print("  - New Product (/products/new)")
print("  - Settings pages (/settings/*)")
print("  - Any other sub-pages")
