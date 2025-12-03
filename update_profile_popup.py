# Script to update mobile profile popup to slide from top with all options
import re

# Read the current base.html
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change 1: Update CSS for profile popup to slide from top instead of bottom
old_css = r'''        /\* Profile popup from bottom \*/
        \.profile-popup \{
            transform: translateY\(100%\);
            transition: transform 0\.3s ease-out;
        \}
        \.profile-popup\.active \{
            transform: translateY\(0\);
        \}'''

new_css = '''        /* Profile popup from top */
        .profile-popup {
            transform: translateY(-100%);
            transition: transform 0.3s ease-out;
        }
        .profile-popup.active {
            transform: translateY(0);
        }'''

content = re.sub(old_css, new_css, content, flags=re.DOTALL)

# Change 2: Update mobile profile popup position and add all menu options
old_popup = r'''    <!-- Mobile Profile Popup -->
    <div id="mobile-profile-popup" class="profile-popup md:hidden fixed bottom-0 left-0 right-0 z-40 bg-gray-900 border-t border-gray-700 rounded-t-2xl no-print">'''

new_popup = '''    <!-- Mobile Profile Popup -->
    <div id="mobile-profile-popup" class="profile-popup md:hidden fixed top-[72px] left-0 right-0 z-40 bg-gray-900 border-b border-gray-700 rounded-b-2xl no-print shadow-2xl">'''

content = content.replace(old_popup, new_popup)

# Change 3: Add all profile menu options (Banking, Security, Notifications, Billing)
old_menu_options = r'''                <a href="/settings/shop" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                        </svg>
                        <span>Shop Settings</span>
                    </div>
                </a>
                <a href="/invoices/new" class="block px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-center font-medium">
                    New Invoice
                </a>'''

new_menu_options = '''                <a href="/settings/shop" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                        </svg>
                        <span>Shop Settings</span>
                    </div>
                </a>
                <a href="/settings/bank" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                        </svg>
                        <span>Banking & Payments</span>
                    </div>
                </a>
                <a href="/settings/security" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                        <span>Security</span>
                    </div>
                </a>
                <a href="/settings/notifications" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                        </svg>
                        <span>Notifications</span>
                    </div>
                </a>
                <a href="/settings/billing" class="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">
                    <div class="flex items-center gap-3">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                        </svg>
                        <span>Billing & Subscription</span>
                    </div>
                </a>
                <div class="border-t border-gray-800 mt-2 pt-2">
                    <a href="/invoices/new" class="block px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-center font-medium">
                        New Invoice
                    </a>
                </div>'''

content = content.replace(old_menu_options, new_menu_options)

# Write the updated content
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Mobile profile popup updated successfully!")
print("Changes made:")
print("1. Profile popup now slides from TOP (not bottom)")
print("2. Added all profile menu options:")
print("   - Profile Settings")
print("   - Shop Settings")
print("   - Banking & Payments")
print("   - Security")
print("   - Notifications")
print("   - Billing & Subscription")
print("   - New Invoice")
print("   - Logout")
