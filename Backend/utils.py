"""
Utility functions for FIR generation system.
Includes text preprocessing and Indian phone number extraction.
"""

import re
from typing import List, Dict, Any


# IPC Section mappings for different offence types
IPC_SECTIONS = {
    "Theft": [
        {"section": "379", "description": "Punishment for theft"},
        {"section": "380", "description": "Theft in dwelling house"},
        {"section": "381", "description": "Theft by clerk or servant"},
        {"section": "382", "description": "Theft after preparation for causing death/hurt"}
    ],
    "Assault": [
        {"section": "323", "description": "Punishment for voluntarily causing hurt"},
        {"section": "324", "description": "Voluntarily causing hurt by dangerous weapons"},
        {"section": "325", "description": "Punishment for voluntarily causing grievous hurt"},
        {"section": "326", "description": "Voluntarily causing grievous hurt by dangerous weapons"},
        {"section": "352", "description": "Punishment for assault or criminal force"}
    ],
    "Cyber Crime": [
        {"section": "66", "description": "IT Act - Computer related offences"},
        {"section": "66C", "description": "IT Act - Identity theft"},
        {"section": "66D", "description": "IT Act - Cheating by personation using computer"},
        {"section": "67", "description": "IT Act - Publishing obscene information"},
        {"section": "420", "description": "IPC - Cheating and dishonestly inducing delivery of property"}
    ],
    "Cheating": [
        {"section": "415", "description": "Cheating"},
        {"section": "417", "description": "Punishment for cheating"},
        {"section": "418", "description": "Cheating with knowledge that wrongful loss may ensue"},
        {"section": "420", "description": "Cheating and dishonestly inducing delivery of property"}
    ],
    "Fraud": [
        {"section": "415", "description": "Cheating"},
        {"section": "420", "description": "Cheating and dishonestly inducing delivery of property"},
        {"section": "465", "description": "Punishment for forgery"},
        {"section": "468", "description": "Forgery for purpose of cheating"}
    ],
    "Harassment": [
        {"section": "354", "description": "Assault or criminal force to woman with intent to outrage modesty"},
        {"section": "354A", "description": "Sexual harassment"},
        {"section": "354D", "description": "Stalking"},
        {"section": "498A", "description": "Husband or relative subjecting woman to cruelty"},
        {"section": "509", "description": "Word, gesture or act intended to insult modesty of woman"}
    ],
    "Other": [
        {"section": "154", "description": "CrPC - Information in cognizable cases"},
        {"section": "200", "description": "CrPC - Examination of complainant"}
    ]
}


def preprocess_text(text: str) -> str:
    """
    Perform comprehensive text preprocessing.
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses (but keep for extraction separately)
    # text = re.sub(r'\S+@\S+', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation needed for NER
    text = re.sub(r'[^\w\s.,!?;:\'"@#$%&*()\-/]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_indian_phone_numbers(text: str) -> List[str]:
    """
    Extract Indian phone numbers from text using comprehensive regex patterns.
    Supports multiple Indian phone number formats.
    
    Args:
        text: Input text containing phone numbers
        
    Returns:
        List of extracted phone numbers
    """
    patterns = [
        # +91 followed by 10 digits with optional separators
        r'\+91[-.\s]?[6-9]\d{9}',
        # 91 followed by 10 digits (without plus)
        r'(?<!\d)91[-.\s]?[6-9]\d{9}',
        # 0 followed by 10 digits (STD format)
        r'(?<!\d)0[6-9]\d{9}',
        # Plain 10 digit Indian mobile (starting with 6-9)
        r'(?<!\d)[6-9]\d{9}(?!\d)',
        # Formatted: XXX-XXX-XXXX or XXX XXX XXXX or XXX.XXX.XXXX
        r'(?<!\d)[6-9]\d{2}[-.\s]\d{3}[-.\s]\d{4}(?!\d)',
        # With country code in parentheses: (+91) XXXXXXXXXX
        r'\(\+?91\)[-.\s]?[6-9]\d{9}',
        # Landline numbers: STD code + number (e.g., 011-12345678)
        r'(?<!\d)0\d{2,4}[-.\s]?\d{6,8}(?!\d)',
    ]
    
    phone_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    # Clean and normalize phone numbers
    cleaned_numbers = []
    for phone in phone_numbers:
        # Remove all non-digit characters for normalization
        digits = re.sub(r'\D', '', phone)
        
        # Ensure it's a valid length
        if len(digits) == 10 and digits[0] in '6789':
            cleaned_numbers.append(digits)
        elif len(digits) == 11 and digits[0] == '0' and digits[1] in '6789':
            cleaned_numbers.append(digits[1:])  # Remove leading 0
        elif len(digits) == 12 and digits[:2] == '91' and digits[2] in '6789':
            cleaned_numbers.append(digits[2:])  # Remove country code
        elif len(digits) == 13 and digits[:3] == '091' and digits[3] in '6789':
            cleaned_numbers.append(digits[3:])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_numbers = []
    for num in cleaned_numbers:
        if num not in seen:
            seen.add(num)
            unique_numbers.append(num)
    
    return unique_numbers


def extract_email_addresses(text: str) -> List[str]:
    """
    Extract email addresses from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted email addresses
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(pattern, text)))


def extract_aadhar_numbers(text: str) -> List[str]:
    """
    Extract Aadhaar numbers from text (12-digit Indian ID).
    
    Args:
        text: Input text
        
    Returns:
        List of extracted Aadhaar numbers
    """
    # Aadhaar format: XXXX XXXX XXXX or XXXX-XXXX-XXXX or XXXXXXXXXXXX
    patterns = [
        r'(?<!\d)\d{4}[-.\s]\d{4}[-.\s]\d{4}(?!\d)',
        r'(?<!\d)\d{12}(?!\d)'
    ]
    
    aadhar_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        aadhar_numbers.extend(matches)
    
    # Clean and validate
    cleaned = []
    for num in aadhar_numbers:
        digits = re.sub(r'\D', '', num)
        if len(digits) == 12 and digits[0] != '0' and digits[0] != '1':
            cleaned.append(digits)
    
    return list(set(cleaned))


def get_ipc_sections(offence_type: str) -> List[Dict[str, str]]:
    """
    Get relevant IPC sections for a given offence type.
    
    Args:
        offence_type: Type of offence detected
        
    Returns:
        List of relevant IPC sections with descriptions
    """
    # Normalize offence type
    offence_type = offence_type.strip().title()
    
    # Handle variations
    if "cyber" in offence_type.lower():
        offence_type = "Cyber Crime"
    elif "cheat" in offence_type.lower() or "fraud" in offence_type.lower():
        offence_type = "Cheating"
    
    return IPC_SECTIONS.get(offence_type, IPC_SECTIONS["Other"])


def format_phone_number(phone: str) -> str:
    """
    Format a 10-digit phone number in a readable format.
    
    Args:
        phone: 10-digit phone number
        
    Returns:
        Formatted phone number
    """
    if len(phone) == 10:
        return f"+91 {phone[:5]} {phone[5:]}"
    return phone


def generate_fir_document(data: Dict[str, Any]) -> str:
    """
    Generate formatted FIR document from extracted data.
    
    Args:
        data: Dictionary containing all FIR fields
        
    Returns:
        Formatted FIR text document
    """
    # Get IPC sections
    ipc_sections = data.get('ipc_sections', [])
    ipc_text = "\n".join([f"  - Section {s['section']}: {s['description']}" for s in ipc_sections])
    
    # Format extracted persons
    persons = data.get('extracted_persons', [])
    persons_text = ", ".join(persons) if persons else "Not identified"
    
    # Format phone numbers
    phones = data.get('extracted_phone_numbers', [])
    phones_text = ", ".join([format_phone_number(p) for p in phones]) if phones else "None extracted"
    
    # Format vehicle numbers
    vehicles = data.get('extracted_vehicle_numbers', [])
    vehicles_text = ", ".join(vehicles) if vehicles else "None"
    
    # Witness info
    witness_name = data.get('witness_name', '')
    witness_contact = data.get('witness_contact', '')
    witness_text = f"{witness_name} ({witness_contact})" if witness_name else "None provided"
    
    # Severity info
    severity_level = data.get('severity_level', 'Unknown')
    severity_score = data.get('severity_score', 0)
    
    # FIR ID
    fir_id = data.get('fir_id', 'PENDING')
    
    fir_template = f"""
================================================================================
                        FIRST INFORMATION REPORT (FIR)
================================================================================
FIR Reference: {fir_id}
Generated On:  {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
Severity:      {severity_level} (Score: {severity_score}/100)
================================================================================

SECTION A: COMPLAINANT DETAILS
------------------------------
Name:    {data.get('name', 'N/A')}
Contact: {data.get('contact', 'N/A')}

SECTION B: WITNESS DETAILS
--------------------------
{witness_text}

SECTION C: INCIDENT DETAILS
---------------------------
Date of Incident:  {data.get('date', 'Not specified')}
Time of Incident:  {data.get('time', 'Not specified')}
Place of Incident: {data.get('location', 'Not specified')}
Type of Offence:   {data.get('offence_type', 'Unknown')}
Classification Confidence: {data.get('confidence', 0):.1%}

SECTION D: PERSONS INVOLVED / ACCUSED
--------------------------------------
{persons_text}

SECTION E: EXTRACTED INFORMATION
---------------------------------
Phone Numbers:   {phones_text}
Vehicle Numbers: {vehicles_text}

SECTION F: APPLICABLE LEGAL SECTIONS
-------------------------------------
{ipc_text if ipc_text else "  To be determined by investigating officer"}

SECTION G: DETAILED NARRATIVE
------------------------------
{data.get('description', 'No description provided')}

SECTION H: COMPLAINANT'S REQUEST
---------------------------------
I, {data.get('name', 'the complainant')}, hereby request the concerned 
authorities to kindly register this First Information Report and take 
necessary legal action against the accused person(s) under the applicable 
sections of the Indian Penal Code and other relevant laws.

I affirm that the information provided above is true and correct to the 
best of my knowledge and belief.


Signature of Complainant: _______________________

Date: _______________________

================================================================================
                              FOR OFFICIAL USE ONLY
================================================================================
FIR Number:           ________________________
Police Station:       ________________________
District:             ________________________
Date of Registration: ________________________
Time of Registration: ________________________
Investigating Officer: ________________________
Officer Rank/Badge:   ________________________
================================================================================
                         END OF FIRST INFORMATION REPORT
================================================================================
"""
    return fir_template


def extract_vehicle_numbers(text: str) -> List[str]:
    """
    Extract Indian vehicle registration numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted vehicle numbers
    """
    # Indian vehicle number format: XX-00-XX-0000 or XX00XX0000
    patterns = [
        r'\b[A-Z]{2}[-.\s]?\d{1,2}[-.\s]?[A-Z]{1,3}[-.\s]?\d{4}\b',
        r'\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}\b'
    ]
    
    vehicle_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text.upper())
        vehicle_numbers.extend(matches)
    
    # Clean and normalize
    cleaned = []
    for num in vehicle_numbers:
        clean_num = re.sub(r'[-.\s]', '', num).upper()
        if len(clean_num) >= 9 and len(clean_num) <= 11:
            cleaned.append(clean_num)
    
    return list(set(cleaned))


def extract_pan_numbers(text: str) -> List[str]:
    """
    Extract PAN (Permanent Account Number) from text.
    Format: AAAAA0000A
    
    Args:
        text: Input text
        
    Returns:
        List of extracted PAN numbers
    """
    pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
    matches = re.findall(pattern, text.upper())
    return list(set(matches))


def calculate_severity_score(offence_type: str, confidence: float, text: str) -> Dict[str, Any]:
    """
    Calculate severity score based on offence type, confidence, and text analysis.
    
    Args:
        offence_type: Detected offence type
        confidence: Classification confidence
        text: Complaint text
        
    Returns:
        Dictionary with severity score, level, and contributing factors
    """
    base_scores = {
        "Assault": 70,
        "Cyber Crime": 50,
        "Theft": 45,
        "Cheating": 40,
        "Harassment": 55,
        "Other": 30
    }
    
    score = base_scores.get(offence_type, 30)
    factors = []
    
    # Severity keywords analysis
    high_severity_keywords = [
        "murder", "death", "killed", "weapon", "gun", "knife",
        "hospital", "critical", "serious injury", "blood",
        "threat to life", "kidnap", "abduct", "ransom"
    ]
    
    medium_severity_keywords = [
        "injured", "hurt", "attack", "force", "threat",
        "large amount", "lakh", "crore", "multiple victims"
    ]
    
    text_lower = text.lower()
    
    # Check for high severity indicators
    for keyword in high_severity_keywords:
        if keyword in text_lower:
            score += 15
            factors.append(f"High severity indicator: '{keyword}'")
            break
    
    # Check for medium severity indicators
    for keyword in medium_severity_keywords:
        if keyword in text_lower:
            score += 8
            factors.append(f"Medium severity indicator: '{keyword}'")
            break
    
    # Confidence factor
    if confidence > 0.8:
        score += 5
        factors.append("High classification confidence")
    elif confidence < 0.4:
        score -= 5
        factors.append("Low classification confidence")
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    # Determine level
    if score >= 75:
        level = "Critical"
    elif score >= 55:
        level = "High"
    elif score >= 35:
        level = "Medium"
    else:
        level = "Low"
    
    return {
        "score": score,
        "level": level,
        "factors": factors
    }


# Import datetime for FIR document
from datetime import datetime
