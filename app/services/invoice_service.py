from app import models
from sqlalchemy.orm import Session
import math

def num_to_words(num):
    if num == 0:
        return "Zero"
    
    words = {
        0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
        10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen",
        17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty", 40: "Forty", 50: "Fifty",
        60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety"
    }
    
    def get_words(n):
        if n < 20:
            return words[n]
        elif n < 100:
            return words[n // 10 * 10] + (" " + words[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return words[n // 100] + " Hundred" + (" " + get_words(n % 100) if n % 100 != 0 else "")
        elif n < 100000:
            return get_words(n // 1000) + " Thousand" + (" " + get_words(n % 1000) if n % 1000 != 0 else "")
        elif n < 10000000:
            return get_words(n // 100000) + " Lakh" + (" " + get_words(n % 100000) if n % 100000 != 0 else "")
        else:
            return get_words(n // 10000000) + " Crore" + (" " + get_words(n % 10000000) if n % 10000000 != 0 else "")

    num_int = int(num)
    num_dec = int(round((num - num_int) * 100))
    
    result = "Rupees " + get_words(num_int)
    if num_dec > 0:
        result += " and " + get_words(num_dec) + " Paise"
    
    return result + " Only"

def calculate_taxes(item_total, tax_rate, is_inter_state):
    # item_total is taxable value
    tax_amount = item_total * (tax_rate / 100)
    
    if is_inter_state:
        return {
            "cgst_rate": 0,
            "cgst_amount": 0,
            "sgst_rate": 0,
            "sgst_amount": 0,
            "igst_rate": tax_rate,
            "igst_amount": tax_amount,
            "total_tax": tax_amount
        }
    else:
        half_tax = tax_amount / 2
        half_rate = tax_rate / 2
        return {
            "cgst_rate": half_rate,
            "cgst_amount": half_tax,
            "sgst_rate": half_rate,
            "sgst_amount": half_tax,
            "igst_rate": 0,
            "igst_amount": 0,
            "total_tax": tax_amount
        }

def generate_invoice_number(shop_id: int, db: Session):
    # Simple auto-increment logic for now. 
    # In real app, might want to check last invoice number pattern.
    count = db.query(models.Invoice).filter(models.Invoice.shop_id == shop_id).count()
    return f"INV-{count + 1:04d}"
