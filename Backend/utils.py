"""
Utility functions for FIR generation system.
Includes text preprocessing, IPC section mapping, and FIR document generation.
"""

import re
import os
import tempfile
from typing import List, Dict, Any
from datetime import datetime


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
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation needed for NER
    text = re.sub(r'[^\w\s.,!?;:\'"@#$%&*()\-/]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


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


def generate_fir_document(data: Dict[str, Any], language: str = 'en') -> str:
    """
    Generate formatted FIR document from extracted data.
    
    Args:
        data: Dictionary containing all FIR fields
        language: Language for FIR document ('en' or 'te')
        
    Returns:
        Formatted FIR text document
    """
    if language == 'te':
        return generate_fir_document_telugu(data)
    
    # Get IPC sections
    ipc_sections = data.get('ipc_sections', [])
    ipc_text = "\n".join([f"  - Section {s['section']}: {s['description']}" for s in ipc_sections])
    
    # Format extracted persons (from NER model)
    persons = data.get('extracted_persons', [])
    persons_text = ", ".join(persons) if persons else "Not identified"
    
    # Format extracted locations (from NER model)
    locations = data.get('extracted_entities', {}).get('locations', [])
    locations_text = ", ".join(locations) if locations else "Not specified"
    
    # Format extracted organizations (from NER model)
    organizations = data.get('extracted_entities', {}).get('organizations', [])
    organizations_text = ", ".join(organizations) if organizations else "None"
    
    # Witness info
    witness_name = data.get('witness_name', '')
    witness_contact = data.get('witness_contact', '')
    witness_text = f"{witness_name} ({witness_contact})" if witness_name else "None provided"
    
    # FIR ID
    fir_id = data.get('fir_id', 'PENDING')
    
    fir_template = f"""
================================================================================
                        FIRST INFORMATION REPORT (FIR)
================================================================================
FIR Reference: {fir_id}
Generated On:  {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
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
Place of Incident: {locations_text}
Type of Offence:   {data.get('offence_type', 'Unknown')}
Classification Confidence: {data.get('confidence', 0):.1%}

SECTION D: PERSONS INVOLVED / ACCUSED
--------------------------------------
{persons_text}

SECTION E: EXTRACTED INFORMATION (ML Models)
----------------------------------------------
Locations:       {locations_text}
Organizations:   {organizations_text}

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


def generate_fir_document_telugu(data: Dict[str, Any]) -> str:
    """
    Generate formatted FIR document in Telugu language.
    
    Args:
        data: Dictionary containing all FIR fields
        
    Returns:
        Formatted FIR text document in Telugu
    """
    # Get IPC sections
    ipc_sections = data.get('ipc_sections', [])
    ipc_text = "\n".join([f"  - సెక్షన్ {s['section']}: {s['description']}" for s in ipc_sections])
    
    # Format extracted persons (from NER model)
    persons = data.get('extracted_persons', [])
    persons_text = ", ".join(persons) if persons else "గుర్తించబడలేదు"
    
    # Format extracted locations (from NER model)
    locations = data.get('extracted_entities', {}).get('locations', [])
    locations_text = ", ".join(locations) if locations else "పేర్కొనబడలేదు"
    
    # Format extracted organizations (from NER model)
    organizations = data.get('extracted_entities', {}).get('organizations', [])
    organizations_text = ", ".join(organizations) if organizations else "ఏదీ లేదు"
    
    # Witness info
    witness_name = data.get('witness_name', '')
    witness_contact = data.get('witness_contact', '')
    witness_text = f"{witness_name} ({witness_contact})" if witness_name else "అందించబడలేదు"
    
    # FIR ID
    fir_id = data.get('fir_id', 'పెండింగ్')
    
    # Offence type translations
    offence_translations = {
        "Theft": "దొంగతనం",
        "Assault": "దాడి",
        "Cyber Crime": "సైబర్ నేరం",
        "Cheating": "మోసం",
        "Fraud": "మోసపూరిత",
        "Harassment": "వేధింపు",
        "Other": "ఇతర"
    }
    offence_type_te = offence_translations.get(data.get('offence_type', 'Unknown'), data.get('offence_type', 'తెలియదు'))
    
    fir_template = f"""
================================================================================
                    మొదటి సమాచార నివేదిక (ఎఫ్‌ఐఆర్)
================================================================================
ఎఫ్‌ఐఆర్ సూచన: {fir_id}
సృష్టించిన తేదీ: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
================================================================================

విభాగం A: ఫిర్యాదుదారు వివరాలు
--------------------------------
పేరు:    {data.get('name', 'N/A')}
సంప్రదింపు: {data.get('contact', 'N/A')}

విభాగం B: సాక్షి వివరాలు
---------------------------
{witness_text}

విభాగం C: సంఘటన వివరాలు
---------------------------
సంఘటన స్థలం: {locations_text}
నేర రకం:   {offence_type_te}
వర్గీకరణ విశ్వసనీయత: {data.get('confidence', 0):.1%}

విభాగం D: పాల్గొన్న వ్యక్తులు / నిందితులు
--------------------------------------------
{persons_text}

విభాగం E: సేకరించిన సమాచారం (ML మోడల్స్)
--------------------------------------------
స్థలాలు:       {locations_text}
సంస్థలు:   {organizations_text}

విభాగం F: వర్తించే చట్టపరమైన విభాగాలు
-----------------------------------------
{ipc_text if ipc_text else "  దర్యాప్తు అధికారిచే నిర్ణయించబడుతుంది"}

విభాగం G: వివరణాత్మక వర్ణన
-------------------------------
{data.get('description', 'వివరణ అందించబడలేదు')}

విభాగం H: ఫిర్యాదుదారు అభ్యర్థన
------------------------------------
నేను, {data.get('name', 'ఫిర్యాదుదారు')}, సంబంధిత అధికారులను దయతో ఈ మొదటి 
సమాచార నివేదికను నమోదు చేయమని మరియు భారతీయ శిక్షాస్మృతి మరియు ఇతర సంబంధిత 
చట్టాల వర్తించే విభాగాల క్రింద నిందితుల పై అవసరమైన చట్టపరమైన చర్య తీసుకోవాలని 
అభ్యర్థిస్తున్నాను.

పైన అందించిన సమాచారం నా జ్ఞానం మరియు విశ్వాసం ప్రకారం నిజమైనది మరియు 
సరైనదని నేను ధృవీకరిస్తున్నాను.


ఫిర్యాదుదారు సంతకం: _______________________

తేదీ: _______________________

================================================================================
                        అధికారిక ఉపయోగం కోసం మాత్రమే
================================================================================
ఎఫ్‌ఐఆర్ నంబర్:           ________________________
పోలీస్ స్టేషన్:       ________________________
జిల్లా:             ________________________
నమోదు తేదీ: ________________________
నమోదు సమయం: ________________________
దర్యాప్తు అధికారి: ________________________
అధికారి హోదా/బ్యాడ్జ్:   ________________________
================================================================================
                    మొదటి సమాచార నివేదిక ముగింపు
================================================================================
"""
    return fir_template


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file to text using speech recognition.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Transcribed text from the audio
    """
    import speech_recognition as sr
    from pydub import AudioSegment
    
    recognizer = sr.Recognizer()
    
    try:
        # Convert audio to WAV format if needed
        audio = AudioSegment.from_file(audio_file_path)
        
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            audio.export(temp_wav.name, format="wav")
            temp_wav_path = temp_wav.name
        
        # Transcribe the audio
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = recognizer.record(source)
            
            # Try Google Speech Recognition first
            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Audio could not be understood"
            except sr.RequestError as e:
                # Fallback to Sphinx if Google API fails
                try:
                    text = recognizer.recognize_sphinx(audio_data)
                    return text
                except:
                    return f"Speech recognition service error: {str(e)}"
    
    except Exception as e:
        return f"Error processing audio: {str(e)}"
    
    finally:
        # Clean up temporary file
        if 'temp_wav_path' in locals():
            try:
                os.unlink(temp_wav_path)
            except:
                pass


