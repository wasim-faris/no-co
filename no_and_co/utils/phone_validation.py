import phonenumbers
import requests
import re
from django.conf import settings

def is_valid_phone(phone_str, region="IN"):
    """
    STRICT production-grade phone verification.
    1. Local pattern & entropy checks (quick reject fakes)
    2. Libphonenumber telecom structure check
    3. (Optional) External API check (AbstractAPI/Twilio) for existence/carrier
    """
    if not phone_str:
        return False, "Phone number is required"
    
    phone_str = str(phone_str).strip()
    clean_phone = re.sub(r'\D', '', phone_str)
    
    # ── 1. LOCAL DUMMY PATTERN REJECTION ──
    
    # Reject if less than 10 digits (for IN) or too short in general
    if len(clean_phone) < 10:
        return False, "Phone number is too short"

    # Entropy check: Real numbers usually have at least 4-5 unique digits
    if len(set(clean_phone)) < 4:
        return False, "This looks like a fake or generated number"

    # Sequential checks
    sequences = ["0123456789", "1234567890", "9876543210", "1122334455", "5544332211"]
    if any(seq in clean_phone for seq in sequences):
        return False, "Please enter a realistic active mobile number"

    # Repeated pattern (e.g., 9000000000, 9999999999)
    # Check if the last 7+ digits are identical
    if re.search(r'(\d)\1{6,}$', clean_phone):
        return False, "Fake or repeated digit pattern detected"

    # ── 2. LIBPHONENUMBER STRUCTURE CHECK ──
    try:
        if not phone_str.startswith('+'):
            # Basic sanity for India
            if region == "IN" and (not clean_phone.startswith(('6', '7', '8', '9'))):
                return False, "Invalid Indian mobile prefix"
            parsed = phonenumbers.parse(phone_str, region)
        else:
            parsed = phonenumbers.parse(phone_str, None)

        if not phonenumbers.is_possible_number(parsed):
            return False, "This phone number is not possible"
            
        if not phonenumbers.is_valid_number(parsed):
            return False, "This phone number is invalid for its region"

        num_type = phonenumbers.number_type(parsed)
        if num_type not in [phonenumbers.PhoneNumberType.MOBILE, phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE]:
            return False, "Only active mobile numbers are accepted"

        # ── 3. EXTERNAL API CHECK (Optional, if Key exists) ──
        api_key = getattr(settings, 'ABSTRACT_PHONE_API_KEY', None)
        if api_key:
            # Format to E.164 for API
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            try:
                url = f"https://phonevalidation.abstractapi.com/v1/?api_key={api_key}&number={e164}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # AbstractAPI 'valid' check includes telecom existence
                    if not data.get('valid', False):
                        return False, "This number does not exist or is inactive"
                    # Reject VOIP if possible (common for fakes)
                    if data.get('type') == 'VOIP':
                        return False, "VOIP/Virtual numbers are not allowed"
            except Exception as e:
                # Log but pass if API is down to avoid blocking real users
                print(f"Phone API Error: {e}")

        return True, ""
    except Exception:
        return False, "Invalid phone number format"
