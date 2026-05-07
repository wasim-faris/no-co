import re

def validate_name_field(value):
    """
    Strict name validation:
    - Allow ONLY letters (A-Z, a-z) and single normal spaces.
    - Block numbers, special characters, symbols, etc.
    - Must be 2-100 characters.
    """
    if not value:
        return False, "This field is required."
    trimmed = value.strip()
    if len(trimmed) < 2:
        return False, "Must be at least 2 characters."
    if len(trimmed) > 100:
        return False, "Must be 100 characters or fewer."
    if not re.fullmatch(r"[a-zA-Z ]+", trimmed):
        return False, "Only letters are allowed."
    if "  " in trimmed:
        return False, "Multiple consecutive spaces are not allowed."
    return True, ""

def validate_address_field(value, required=True):
    """
    Strict address line validation:
    - Allow ONLY letters (A-Z, a-z), digits (0-9), and single normal spaces.
    - Block special characters (@, -, ., *, etc.).
    - Must be 3-200 characters if provided.
    """
    if not value:
        if required:
            return False, "This field is required."
        return True, ""
    trimmed = value.strip()
    if len(trimmed) < 3:
        return False, "Must be at least 3 characters."
    if len(trimmed) > 200:
        return False, "Must be 200 characters or fewer."
    if not re.fullmatch(r"[a-zA-Z0-9 ]+", trimmed):
        return False, "Only letters, numbers, and spaces are allowed."
    if "  " in trimmed:
        return False, "Multiple consecutive spaces are not allowed."
    return True, ""

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

def validate_color_name(value):
    """
    Special validation for Variant Colors:
    - Allow letters, spaces, and single '/'.
    - Block numbers and other special chars.
    - Must be 3-100 characters.
    """
    if not value:
        return False
    
    trimmed = value.strip()
    if len(trimmed) < 3 or len(trimmed) > 100:
        return False
    
    # Allow letters, spaces, and /
    if not re.fullmatch(r"[a-zA-Z /]+", trimmed):
        return False
        
    # Prevent multiple consecutive spaces or slashes
    if "  " in trimmed or "//" in trimmed:
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
