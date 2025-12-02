import os

path = r'c:\Users\Md Sahimuzzaman\Desktop\GST_DEMO\app\templates\invoices\print.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the split point
split_index = -1
for i, line in enumerate(lines):
    if '<!-- ACTION & SHARE SCRIPTS -->' in line:
        split_index = i
        break

if split_index == -1:
    print("Could not find split point! Searching for alternative...")
    # Fallback: look for the closing div of page-container or similar
    # In the corrupted file, we might have multiple copies or garbage.
    # Let's look for the line "    <div class=\"page-container\">" and find its closing div? No too hard.
    # Let's look for the LAST occurrence of "    </div>" before the script?
    # Actually, let's just look for the line index 630 roughly?
    # Let's look for the line that says "    <!-- ACTION & SHARE SCRIPTS -->" - if it's missing, we are in trouble.
    # But I saw it in the file view in Step 1346.
    # In Step 1392, it was missing?
    # Step 1392 showed lines 430-658.
    # Line 632 was "        }".
    # It seems the marker might be gone.
    
    # Let's look for the line "            </div>" followed by "        </div>" followed by "    </div>"
    # This corresponds to the closing of invoice-box, invoice-container, page-container.
    # Let's find the index of "    <div class=\"computer-generated-note\">"
    for i, line in enumerate(lines):
        if 'class="computer-generated-note"' in line:
            # The note is 3 lines long.
            # 625: <div...
            # 626: content
            # 627: </div>
            # Then 3 closing divs.
            split_index = i + 6 # Skip note + 3 closing divs
            break

if split_index == -1:
    print("CRITICAL: Could not find split point. Aborting.")
    exit(1)

print(f"Truncating at line {split_index}")

# Safe content (top part)
content = "".join(lines[:split_index])

# New script content
new_script = """
    <!-- ACTION & SHARE SCRIPTS -->
    <script>
        // Basic invoice variables from backend
        const invoiceId = {{ invoice.id }};
        const invoiceNo = "{{ invoice.invoice_no }}";
        const totalAmount = {{ "%.2f"|format(total_amount) }};

        function printInvoice() {
            window.print();
        }

        function downloadPDF() {
            // Add timestamp to prevent caching of previous 401/JSON responses
            window.location.href = `/invoices/${invoiceId}/pdf?t=${new Date().getTime()}`;
        }

        function toggleSharePopup() {
            const popup = document.getElementById('sharePopup');
            popup.classList.toggle('active');
        }

        function closeSharePopup(event) {
            if (event) {
                event.stopPropagation();
            }
            const popup = document.getElementById('sharePopup');
            popup.classList.remove('active');
        }

        function copyInvoiceLink() {
            const invoiceUrl = window.location.href;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(invoiceUrl)
                    .then(() => {
                        alert('Invoice link copied to clipboard!');
                        toggleSharePopup();
                    })
                    .catch(err => {
                        console.error('Failed to copy:', err);
                        alert('Failed to copy link. Please copy manually: ' + invoiceUrl);
                    });
            } else {
                alert('Clipboard not supported. Please copy manually: ' + invoiceUrl);
            }
        }

        function shareViaWhatsApp() {
            const invoiceUrl = window.location.href;
            const message = `Invoice ${invoiceNo} – Amount ₹${totalAmount} – ${invoiceUrl}`;
            const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
            window.open(whatsappUrl, '_blank');
            toggleSharePopup();
        }

        // Close popup on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const popup = document.getElementById('sharePopup');
                if (popup.classList.contains('active')) {
                    popup.classList.remove('active');
                }
            }
        });
    </script>
</body>
</html>"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content + new_script)

print("File repaired successfully.")
