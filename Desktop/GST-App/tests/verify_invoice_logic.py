import sys
import os
sys.path.append(os.getcwd())
from app.services import invoice_service

def test_intra_state():
    print("Testing Intra-state Calculation...")
    taxable = 1000
    rate = 18
    is_inter_state = False
    taxes = invoice_service.calculate_taxes(taxable, rate, is_inter_state)
    
    assert taxes['cgst_amount'] == 90.0, f"Expected CGST 90, got {taxes['cgst_amount']}"
    assert taxes['sgst_amount'] == 90.0, f"Expected SGST 90, got {taxes['sgst_amount']}"
    assert taxes['igst_amount'] == 0.0, f"Expected IGST 0, got {taxes['igst_amount']}"
    assert taxes['total_tax'] == 180.0, f"Expected Total Tax 180, got {taxes['total_tax']}"
    print("✅ Intra-state Passed")

def test_inter_state():
    print("Testing Inter-state Calculation...")
    taxable = 1000
    rate = 18
    is_inter_state = True
    taxes = invoice_service.calculate_taxes(taxable, rate, is_inter_state)
    
    assert taxes['cgst_amount'] == 0.0, f"Expected CGST 0, got {taxes['cgst_amount']}"
    assert taxes['sgst_amount'] == 0.0, f"Expected SGST 0, got {taxes['sgst_amount']}"
    assert taxes['igst_amount'] == 180.0, f"Expected IGST 180, got {taxes['igst_amount']}"
    assert taxes['total_tax'] == 180.0, f"Expected Total Tax 180, got {taxes['total_tax']}"
    print("✅ Inter-state Passed")

def test_rounding_and_words():
    print("Testing Rounding and Words...")
    # Case 1: 12345.67 -> 12346
    amount = 12345.67
    rounded = round(amount)
    assert rounded == 12346, f"Expected 12346, got {rounded}"
    
    words = invoice_service.num_to_words(rounded)
    print(f"12346 -> {words}")
    assert "Twelve Thousand Three Hundred Forty Six" in words or "Twelve Thousand Three Hundred Forty-Six" in words, "Words mismatch"
    print("✅ Rounding & Words Passed")

if __name__ == "__main__":
    try:
        test_intra_state()
        test_inter_state()
        test_rounding_and_words()
        print("\n🎉 All Logic Tests Passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
