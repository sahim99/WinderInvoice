import requests

# Test the PDF endpoint
response = requests.get('http://localhost:8000/invoices/1/pdf', allow_redirects=False)

print("Status Code:", response.status_code)
print("\nResponse Headers:")
for header, value in response.headers.items():
    print(f"  {header}: {value}")

print("\nContent-Disposition header:")
print(f"  {response.headers.get('Content-Disposition', 'NOT FOUND')}")

print("\nContent-Type header:")
print(f"  {response.headers.get('Content-Type', 'NOT FOUND')}")
