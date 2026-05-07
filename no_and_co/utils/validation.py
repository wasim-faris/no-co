import re

def validate_meaningful_content(value):
    """
    STRICT ALPHABET-ONLY VALIDATION:
    - Allow ONLY letters (A-Z, a-z) and single normal spaces.
    - Block numbers, symbols, underscores, dashes, etc.
    - No multiple consecutive spaces.
    - Must be 3-100 characters.
    """
    if not value:
        return False
    
    trimmed = value.strip()
    if len(trimmed) < 3 or len(trimmed) > 100:
        return False
    
    # Allow ONLY letters and spaces
    if not re.fullmatch(r"[a-zA-Z ]+", trimmed):
        return False
        
    # Prevent multiple consecutive spaces
    if "  " in trimmed:
        return False
        
    return True

def validate_phone_number(phone):
    if not phone:
        return False, "Phone number is required"
    
    phone = str(phone).strip()
    
    if not phone.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(phone) != 10:
        return False, "Phone number must be exactly 10 digits"
    
    if phone[0] not in '6789':
        return False, "Phone number must start with 6, 7, 8, or 9"
    
    if len(set(phone)) == 1:
        return False, "Invalid phone number (repeated digits)"
    
    # Check for sequential patterns like 1234567890 or 0987654321
    if phone in "0123456789" or phone in "9876543210":
        return False, "Please enter a realistic phone number"
        
    return True, ""

def clean_input(value):
    """Trims the input."""
    if value:
        return value.strip()
    return value
