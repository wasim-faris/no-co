import re

def validate_meaningful_content(value):
    """
    Validates that the input is not just special characters, spaces, or repeated symbols.
    Must contain at least one alphanumeric character.
    """
    if not value:
        return False
    
    trimmed = value.strip()
    if not trimmed:
        return False
    
    # Reject if it contains ONLY symbols, underscores, dashes, dots, spaces
    if re.fullmatch(r"[\s._\-!@#$%^&*()=+\[\]{};':\",.<>/?|\\`~]+", trimmed):
        return False
    
    # Must contain at least one alphanumeric character
    if not re.search(r"[a-zA-Z0-9]", trimmed):
        return False
        
    # Prevent consecutive unnecessary special characters (e.g., "---", "...")
    # Allow up to 2 consecutive special chars if they are between alphanumeric ones, 
    # but reject if they are the only content or repeated excessively.
    if re.search(r"([._\-!@#$%^&*()=+\[\]{};':\",.<>/?|\\`~])\1{2,}", trimmed):
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
