# Script to remove New Invoice from profile menu and add floating action button
import re

# Read the current base.html
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change 1: Remove "New Invoice" button from profile popup
old_new_invoice_section = '''                <div class="border-t border-gray-800 mt-2 pt-2">
                    <a href="/invoices/new" class="block px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-center font-medium">
                        New Invoice
                    </a>
                </div>'''

content = content.replace(old_new_invoice_section, '')

# Change 2: Add CSS for floating action button
# Find the closing of the mobile nav CSS section
css_insertion_point = '''        /* Add padding to main content on mobile to account for bottom nav */
        @media (max-width: 768px) {
            main {
                padding-bottom: 80px !important;
            }
        }
    </style>'''

new_css = '''        /* Add padding to main content on mobile to account for bottom nav */
        @media (max-width: 768px) {
            main {
                padding-bottom: 80px !important;
            }
        }
        
        /* Floating Action Button */
        .fab {
            background: rgba(59, 130, 246, 0.15);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(59, 130, 246, 0.3);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
            transition: all 0.3s ease;
        }
        .fab:hover {
            background: rgba(59, 130, 246, 0.25);
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 12px 40px rgba(59, 130, 246, 0.3);
            transform: translateY(-2px);
        }
        .fab:active {
            transform: translateY(0) scale(0.95);
        }
    </style>'''

content = content.replace(css_insertion_point, new_css)

# Change 3: Add floating action button HTML before the closing body tag
closing_body_marker = '</body>\n</html>'

fab_html = '''
    <!-- Floating Action Button (New Invoice) - Only for logged in users -->
    {% if user %}
    <a href="/invoices/new" class="fab md:hidden fixed bottom-20 right-6 z-40 w-14 h-14 rounded-full flex items-center justify-center text-blue-400 hover:text-blue-300 no-print" title="New Invoice">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
        </svg>
    </a>
    {% endif %}
</body>
</html>'''

content = content.replace(closing_body_marker, fab_html)

# Write the updated content
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Floating Action Button added successfully!")
print("Changes made:")
print("1. Removed 'New Invoice' button from profile dropdown")
print("2. Added floating transparent glass button in bottom-right")
print("3. Button positioned above bottom navigation bar")
print("4. Glassmorphism effect with blur and transparency")
