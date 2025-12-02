# Project Architecture: GST Invoice Manager

## 1. Executive Summary

The **GST Invoice Manager** is a lightweight, web-based application designed to streamline the creation, management, and printing of GST-compliant invoices. Its primary goal is to produce pixel-perfect, A4-printable PDF invoices that strictly adhere to Indian GST layout standards. The system is built for simplicity, supporting local offline deployment while offering a professional, responsive web interface for data entry and preview. Key constraints include accurate PDF rendering (matching the browser preview exactly) and minimal deployment dependencies.

## 2. Technology Stack

*   **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python) - High-performance, async web framework.
*   **Templating Engine**: [Jinja2](https://jinja.palletsprojects.com/) - Server-side rendering for both HTML previews and PDF generation.
*   **PDF Generation**: `xhtml2pdf` - Converts HTML/CSS templates directly to PDF.
    *   *Note*: Used for its ability to handle inline styles and simple layouts effectively without a headless browser.
*   **Database**: [SQLite](https://www.sqlite.org/) (via [SQLAlchemy](https://www.sqlalchemy.org/) ORM) - Zero-config, file-based storage ideal for local/single-tenant use.
*   **Frontend**: Server-side rendered HTML with [Vanilla CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) (custom `invoice_print.css` for print layouts).
*   **Storage**: Local file system:
    *   `app/static/img/`: Application assets (placeholders).
    *   `uploads/`: User-uploaded content (shop logos, QR codes).
*   **Dev Tools**: Python `venv` for isolation. `uvicorn` for the ASGI server.

## 3. Repository Layout

```text
/GST_DEMO
├── app/
│   ├── routers/
│   │   ├── invoices.py       # Core logic: CRUD, PDF generation, Preview
│   │   ├── auth.py           # User authentication routes
│   │   ├── dashboard.py      # Main dashboard stats
│   │   ├── masters.py        # Product/Customer management
│   │   └── settings.py       # Shop profile & config
│   ├── templates/
│   │   ├── invoices/
│   │   │   ├── print_pdf.html # [AUTHORITATIVE] Template for PDF generation
│   │   │   ├── print.html     # [AUTHORITATIVE] Template for Browser Preview
│   │   │   ├── list.html      # Invoice listing
│   │   │   └── create.html    # Invoice creation form
│   │   └── ...
│   ├── static/
│   │   ├── css/
│   │   │   └── invoice_print.css # Shared styles for Print & PDF
│   │   └── img/
│   │       ├── logo-w-gradient-new.png
│   │       └── qr_placeholder.png
│   ├── models.py             # SQLAlchemy Database Models
│   ├── main.py               # App entry point & configuration
│   └── database.py           # DB connection & session handling
├── docs/
│   └── project-architecture.md
├── requirements.txt          # Python dependencies
└── README.md
```

**Key Note**: `print.html` and `print_pdf.html` are kept in sync to ensure "What You See Is What You Get" (WYSIWYG). `invoice_print.css` drives the styling for both.

## 4. High-Level Architecture

```mermaid
graph LR
    User[User / Browser] -->|HTTP Request| FastAPI[FastAPI Server]
    
    subgraph "Application Layer"
        FastAPI -->|Read/Write| DB[(SQLite Database)]
        FastAPI -->|Load| Templates[Jinja2 Templates]
        FastAPI -->|Serve| Static[Static Assets (CSS/Img)]
    end
    
    subgraph "PDF Generation Flow"
        Templates -->|Render HTML| HTML_String[HTML String]
        HTML_String -->|Input| PISA[xhtml2pdf (PISA)]
        Static -->|Embed Images| PISA
        PISA -->|Generate| PDF_File[PDF Document]
    end
    
    PISA -->|Stream Bytes| User
```

## 5. Detailed Component Descriptions

### API / Routers (`app/routers/invoices.py`)

*   **`GET /invoices/{id}`**: Renders the invoice preview.
    *   **Input**: Invoice ID.
    *   **Output**: HTML page (`print.html`) populated with invoice, shop, and customer data.
*   **`GET /invoices/{id}/pdf`**: Generates and downloads the PDF.
    *   **Input**: Invoice ID.
    *   **Output**: `application/pdf` stream with `Content-Disposition: attachment`.
*   **`POST /invoices/new`**: Creates a new invoice.
    *   **Payload**: Form data including `customer_id`, `date`, `items_json` (JSON string of line items).

### Templates

*   **`print_pdf.html`**: The strict XHTML template for PDF generation. It uses a robust **table-based layout** (instead of divs) to ensure pixel-perfect rendering in `xhtml2pdf`. It includes embedded CSS (from `invoice_print.css`) and inline styles for precise alignment.
    *   **Sections**: Header (Logo/Address), Metadata Table (Invoice No, Dates), Items Table, Totals (Tax breakdown), Bottom Row (Bank Details + QR), Signatures.
*   **`print.html`**: The browser-friendly version. It has been **synchronized** with `print_pdf.html` to use the same table-based structure and CSS, ensuring the web preview matches the PDF exactly. Includes a JavaScript toolbar for "Print" and "Download PDF" actions.

### CSS (`invoice_print.css`)

Contains the print-specific layout rules, designed to match "Sample 1".
*   **No `@page`**: Removed to avoid conflicts with `xhtml2pdf`'s internal paging.
*   **Tables**: Used extensively for layout (Header, Items, Signatures) to guarantee structure in the PDF engine.
*   **Classes**: `.col-qty`, `.col-price`, etc., define precise percentage widths to prevent wrapping.
*   **Consistency**: Used by both `print_pdf.html` and `print.html` to ensure WYSIWYG.

### Database Models (`app/models.py`)

*   **`Shop`**: Stores business profile (`name`, `gstin`, `logo_path`, `qr_code_path`).
*   **`Customer`**: Client details (`name`, `address`, `gstin`, `state`).
*   **`Invoice`**: Header info (`invoice_no`, `date`, `grand_total`).
*   **`InvoiceItem`**: Line items linked to an invoice.
    *   *Schema*: `id`, `invoice_id`, `description`, `hsn_code`, `qty`, `rate`, `taxable_value`, `cgst_amount`, `sgst_amount`, `igst_amount`, `total_amount`.

## 6. Data Flow for PDF Generation

1.  **Request**: User clicks "Download PDF" (`GET /invoices/123/pdf`).
2.  **Data Fetch**: `download_invoice_pdf` function fetches `Invoice`, `Shop`, and `Customer` from SQLite.
3.  **Context Prep**: Data is organized into a safe dictionary (`shop_data`) using `getattr` defaults to prevent errors. Totals are calculated, and absolute file paths are resolved for images.
4.  **Rendering**: `print_pdf.html` is rendered with Jinja2 into a pure HTML string.
5.  **Conversion**: `pisa.CreatePDF` converts the HTML string to PDF bytes.
    *   *Callback*: A `link_callback` function intercepts image URLs (e.g., `/static/logo.png`) and converts them to absolute system paths (`C:\Users\...\static\logo.png`).
6.  **Response**: The PDF bytes are streamed back to the browser.

## 7. Security & Input Validation

*   **Authentication**: Basic session/cookie-based auth (via `auth.py`).
*   **Input Sanitization**: Jinja2 auto-escapes HTML variables to prevent XSS.
*   **File Paths**: The `link_callback` in PDF generation strictly maps `/static/` URLs to the app's static directory to prevent arbitrary file access.

## 8. Deployment & Hosting

*   **Requirements**: Python 3.9+, `pip`.
*   **Environment Variables**:
    *   `DATABASE_URL`: Connection string (default: `sqlite:///./gst_billing.db`).
    *   `SECRET_KEY`: For session security.
*   **Run Command**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
*   **Recommendation**: For production, run behind Nginx or use a Docker container.

## 9. Testing & QA

### Manual Verification Steps
1.  **Preview Accuracy**: Open an invoice in the browser. Verify alignment of "Price" and "Amount" columns (should be right-aligned).
2.  **PDF Parity**: Click "Download PDF". Open the file and compare side-by-side with the browser view. Ensure the QR code is in the bottom-right and the Signature section has 4 columns.
3.  **Data Integrity**: Verify that CGST, SGST, and IGST rows are **always visible** in the totals section. If a tax is not applicable (e.g., IGST for local sales), it should show as `0.00`.

## 10. Operational Notes

*   **Missing QR Code**: If the QR code is missing, check `app/static/img/qr_placeholder.png`. Ensure the `Shop` record has a valid `qr_code_path` if a custom one is desired.
*   **PDF Errors**: If PDF generation fails, check the server logs for `link_callback` errors (usually "Missing file"). Ensure image paths are correct.
*   **Restart**: To restart the service, kill the `uvicorn` process and run the start command again.

## 11. Maintenance & Extension

*   **New Fields**: To add a field (e.g., "PO Number"):
    1.  Add column to `Invoice` model in `models.py`.
    2.  Update `create_invoice` in `routers/invoices.py` to save it.
    3.  Add `{{ invoice.po_number }}` to `print.html` and `print_pdf.html`.
*   **Localization**: `amount_in_words` is currently generated in English. Modify `invoice_service.num_to_words` to support other languages.

## 12. Appendices

### Sample Invoice Context (JSON)
```json
{
  "invoice_no": "INV-001",
  "date": "2023-10-27",
  "customer": {
    "name": "Acme Corp",
    "address": "123 Business Rd, Mumbai",
    "gstin": "27ABCDE1234F1Z5"
  },
  "items": [
    {
      "description": "Office Chair",
      "hsn_code": "9403",
      "qty": 2,
      "rate": 5000.00,
      "taxable_value": 10000.00,
      "total_amount": 11800.00
    }
  ],
  "totals": {
    "taxable": 10000.00,
    "cgst": 900.00,
    "sgst": 900.00,
    "grand_total": 11800.00
  }
}
```
