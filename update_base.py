# Script to update base.html with mobile navigation changes
import re

# Read the current base.html
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change 1: Replace Profile button with Products in bottom nav (lines 223-233)
old_profile_section = r'''            <!-- Profile -->
            <button onclick="toggleMobileProfile\(\)" class="bottom-nav-item flex flex-col items-center justify-center text-gray-400 hover:text-blue-400">
                {% if user\.avatar_path %}
                <img class="w-6 h-6 rounded-full object-cover mb-1" src="{{ user\.avatar_path }}" alt="profile">
                {% else %}
                <div class="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold flex items-center justify-center text-xs mb-1">
                    {{ \(user\.full_name or user\.name or user\.email\)\[0\] \| upper }}
                </div>
                {% endif %}
                <span class="text-xs">Profile</span>
            </button>'''

new_products_section = '''            <!-- Products -->
            <a href="/products" class="bottom-nav-item flex flex-col items-center justify-center text-gray-400 hover:text-blue-400 {% if '/products' in request.url.path %}active{% endif %}">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
                <span class="text-xs">Products</span>
            </a>'''

content = re.sub(old_profile_section, new_products_section, content, flags=re.DOTALL)

# Change 2: Add profile icon to top-right on mobile (after line 114, in the user section)
# Find the position after the "New Invoice" button and before the desktop profile menu
old_desktop_profile = r'''                        <div class="relative ml-3 hidden md:block">'''
new_mobile_and_desktop_profile = '''                        <!-- Mobile Profile Icon (top-right) -->
                        <button onclick="toggleMobileProfile()" class="md:hidden relative ml-3">
                            {% if user.avatar_path %}
                            <img class="w-9 h-9 rounded-full object-cover border-2 border-gray-700" src="{{ user.avatar_path }}" alt="profile">
                            {% else %}
                            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold flex items-center justify-center text-sm border-2 border-gray-700">
                                {{ (user.full_name or user.name or user.email)[0] | upper }}
                            </div>
                            {% endif %}
                        </button>
                        
                        <div class="relative ml-3 hidden md:block">'''

content = content.replace(old_desktop_profile, new_mobile_and_desktop_profile)

# Change 3: Add Login/Signup buttons to mobile landing page (after line 155, in the else section)
old_landing_buttons = r'''                    <div class="hidden md:flex items-center gap-3">
                        <a href="/auth/login" class="text-gray-300 hover:text-white font-medium px-3 py-2 transition-colors">Log in</a>
                        <a href="/auth/signup" class="bg-white text-black hover:bg-gray-100 font-semibold px-4 py-2 rounded-lg transition-colors">Get Started</a>
                    </div>'''

new_landing_buttons = '''                    <!-- Desktop Login/Signup -->
                    <div class="hidden md:flex items-center gap-3">
                        <a href="/auth/login" class="text-gray-300 hover:text-white font-medium px-3 py-2 transition-colors">Log in</a>
                        <a href="/auth/signup" class="bg-white text-black hover:bg-gray-100 font-semibold px-4 py-2 rounded-lg transition-colors">Get Started</a>
                    </div>
                    
                    <!-- Mobile Login/Signup -->
                    <div class="md:hidden flex items-center gap-2">
                        <a href="/auth/login" class="text-gray-300 hover:text-white font-medium px-3 py-2 text-sm transition-colors">Log in</a>
                        <a href="/auth/signup" class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-lg text-sm transition-colors">Sign up</a>
                    </div>'''

content = content.replace(old_landing_buttons, new_landing_buttons)

# Write the updated content
with open(r'c:\Users\Md Sahimuzzaman\Desktop\GST-App\app\templates\base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ base.html updated successfully!")
print("Changes made:")
print("1. Replaced Profile with Products in bottom navigation")
print("2. Added profile icon to top-right corner on mobile")
print("3. Added Login/Signup buttons for mobile landing page")
