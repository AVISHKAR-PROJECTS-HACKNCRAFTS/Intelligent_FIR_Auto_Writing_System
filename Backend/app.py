"""
Intelligent FIR Auto Writing System - Flask Backend API
Uses transformer-based NLP for entity extraction and ML-based classification.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import time
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
from io import BytesIO

# Import custom services
from nlp_service import get_nlp_service
from classification_service import get_classification_service
from utils import (
    preprocess_text,
    extract_indian_phone_numbers,
    extract_email_addresses,
    extract_aadhar_numbers,
    get_ipc_sections,
    generate_fir_document,
    calculate_severity_score,
    extract_vehicle_numbers,
    extract_pan_numbers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global service instances (loaded once at startup)
nlp_service = None
classification_service = None

# In-memory storage for FIR history (in production, use a database)
fir_history: List[Dict[str, Any]] = []


def initialize_services():
    """Initialize NLP and classification services at startup."""
    global nlp_service, classification_service
    
    logger.info("Initializing NLP service...")
    start_time = time.time()
    nlp_service = get_nlp_service(use_transformers=True)
    logger.info(f"NLP service initialized in {time.time() - start_time:.2f}s")
    
    logger.info("Initializing classification service...")
    start_time = time.time()
    classification_service = get_classification_service()
    logger.info(f"Classification service initialized in {time.time() - start_time:.2f}s")


def process_complaint(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a complaint and extract all relevant information.
    
    Args:
        data: Dictionary with name, contact, description
        
    Returns:
        Processed FIR data with all extracted information
    """
    name = data.get('name', '')
    contact = data.get('contact', '')
    description = data.get('description', '')
    witness_name = data.get('witness_name', '')
    witness_contact = data.get('witness_contact', '')
    
    # Preprocess the description text
    processed_text = preprocess_text(description)
    
    # Extract entities using transformer-based NER
    entities = nlp_service.extract_entities(processed_text)
    
    # Classify offence type using ML model
    classification_result = classification_service.classify(processed_text)
    
    # Extract phone numbers using improved Indian regex
    phone_numbers = extract_indian_phone_numbers(processed_text)
    
    # Extract email addresses
    emails = extract_email_addresses(processed_text)
    
    # Extract Aadhaar numbers if present
    aadhar_numbers = extract_aadhar_numbers(processed_text)
    
    # Extract vehicle numbers
    vehicle_numbers = extract_vehicle_numbers(processed_text)
    
    # Extract PAN numbers
    pan_numbers = extract_pan_numbers(processed_text)
    
    # Get applicable IPC sections
    ipc_sections = get_ipc_sections(classification_result.label)
    
    # Calculate severity score
    severity = calculate_severity_score(
        classification_result.label,
        classification_result.confidence,
        processed_text
    )
    
    # Prepare extracted data
    date = entities["dates"][0] if entities["dates"] else "Not specified"
    time_str = entities["times"][0] if entities["times"] else "Not specified"
    location = entities["locations"][0] if entities["locations"] else "Not specified"
    
    # Build comprehensive response
    result = {
        # Complainant details
        "name": name,
        "contact": contact,
        
        # Witness details
        "witness_name": witness_name,
        "witness_contact": witness_contact,
        
        # Incident details
        "date": date,
        "time": time_str,
        "location": location,
        
        # Classification results
        "offence_type": classification_result.label,
        "confidence": classification_result.confidence,
        "confidence_level": classification_service.get_confidence_level(classification_result.confidence),
        "all_offence_scores": classification_result.all_scores,
        
        # Severity assessment
        "severity_score": severity["score"],
        "severity_level": severity["level"],
        "severity_factors": severity["factors"],
        
        # Extracted entities
        "extracted_entities": {
            "persons": entities["persons"],
            "locations": entities["locations"],
            "dates": entities["dates"],
            "times": entities["times"],
            "organizations": entities.get("organizations", []),
            "money": entities.get("money", [])
        },
        
        # Contact information
        "extracted_phone_numbers": phone_numbers,
        "extracted_emails": emails,
        "extracted_aadhar": aadhar_numbers,
        "extracted_vehicle_numbers": vehicle_numbers,
        "extracted_pan_numbers": pan_numbers,
        
        # Legal information
        "ipc_sections": ipc_sections,
        
        # Processed description
        "description": processed_text
    }
    
    return result


@app.route('/generate_fir', methods=['POST'])
def generate_fir_endpoint():
    """
    POST endpoint to generate FIR from complaint details.
    
    Expects JSON with:
        - name: Complainant name
        - contact: Complainant contact number
        - description: Free text complaint description
        
    Returns:
        JSON with extracted entities, classification, IPC sections, and FIR text
    """
    try:
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Validate required fields
        description = json_data.get('description', '')
        if not description or not description.strip():
            return jsonify({
                "success": False,
                "error": "Description field is required and cannot be empty"
            }), 400
        
        # Process the complaint
        start_time = time.time()
        result = process_complaint(json_data)
        processing_time = time.time() - start_time
        
        # Generate FIR document
        fir_data = {
            **result,
            "extracted_persons": result["extracted_entities"]["persons"]
        }
        fir_text = generate_fir_document(fir_data)
        
        # Generate unique FIR ID
        fir_id = f"FIR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Store in history
        history_entry = {
            "fir_id": fir_id,
            "timestamp": datetime.now().isoformat(),
            "name": result["name"],
            "offence_type": result["offence_type"],
            "severity_level": result["severity_level"],
            "status": "draft"
        }
        fir_history.append(history_entry)
        
        # Prepare final response
        response = {
            "success": True,
            "fir_id": fir_id,
            
            # Core fields (matching original API)
            "name": result["name"],
            "contact": result["contact"],
            "date": result["date"],
            "time": result["time"],
            "location": result["location"],
            "offence_type": result["offence_type"],
            
            # Witness info
            "witness_name": result["witness_name"],
            "witness_contact": result["witness_contact"],
            
            # Enhanced classification info
            "confidence": result["confidence"],
            "confidence_level": result["confidence_level"],
            "all_offence_scores": result["all_offence_scores"],
            
            # Severity assessment
            "severity_score": result["severity_score"],
            "severity_level": result["severity_level"],
            "severity_factors": result["severity_factors"],
            
            # Extracted information
            "extracted_entities": result["extracted_entities"],
            "extracted_persons": result["extracted_entities"]["persons"],
            "extracted_phone_numbers": result["extracted_phone_numbers"],
            "extracted_emails": result["extracted_emails"],
            "extracted_aadhar": result["extracted_aadhar"],
            "extracted_vehicle_numbers": result["extracted_vehicle_numbers"],
            "extracted_pan_numbers": result["extracted_pan_numbers"],
            
            # Legal sections
            "ipc_sections": result["ipc_sections"],
            
            # Generated FIR
            "fir_text": fir_text,
            
            # Metadata
            "processing_time_seconds": round(processing_time, 3),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"FIR {fir_id} generated successfully in {processing_time:.3f}s - Offence: {result['offence_type']} ({result['confidence']:.1%})")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing FIR request: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/classify', methods=['POST'])
def classify_endpoint():
    """
    POST endpoint to only classify offence type without full FIR generation.
    Useful for quick classification checks.
    """
    try:
        json_data = request.get_json()
        
        if not json_data or not json_data.get('text'):
            return jsonify({
                "success": False,
                "error": "Text field is required"
            }), 400
        
        text = preprocess_text(json_data.get('text', ''))
        result = classification_service.classify(text)
        
        return jsonify({
            "success": True,
            "offence_type": result.label,
            "confidence": result.confidence,
            "confidence_level": classification_service.get_confidence_level(result.confidence),
            "all_scores": result.all_scores,
            "ipc_sections": get_ipc_sections(result.label)
        }), 200
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/extract_entities', methods=['POST'])
def extract_entities_endpoint():
    """
    POST endpoint to only extract entities without classification.
    Useful for entity extraction checks.
    """
    try:
        json_data = request.get_json()
        
        if not json_data or not json_data.get('text'):
            return jsonify({
                "success": False,
                "error": "Text field is required"
            }), 400
        
        text = preprocess_text(json_data.get('text', ''))
        entities = nlp_service.extract_entities(text)
        phone_numbers = extract_indian_phone_numbers(text)
        emails = extract_email_addresses(text)
        
        return jsonify({
            "success": True,
            "entities": entities,
            "phone_numbers": phone_numbers,
            "emails": emails
        }), 200
        
    except Exception as e:
        logger.error(f"Entity extraction error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with service status."""
    services_ready = nlp_service is not None and classification_service is not None
    
    return jsonify({
        "status": "healthy" if services_ready else "initializing",
        "message": "FIR API is running",
        "services": {
            "nlp_service": "ready" if nlp_service else "not loaded",
            "classification_service": "ready" if classification_service else "not loaded"
        }
    }), 200 if services_ready else 503


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and available endpoints."""
    return jsonify({
        "name": "Intelligent FIR Auto Writing System API",
        "version": "2.0.0",
        "description": "ML-powered FIR generation with transformer-based NLP",
        "endpoints": {
            "POST /generate_fir": "Generate complete FIR from complaint",
            "POST /classify": "Classify offence type only",
            "POST /extract_entities": "Extract entities only",
            "POST /analyze_realtime": "Real-time text analysis",
            "GET /fir_history": "Get FIR generation history",
            "GET /health": "Health check",
            "GET /api/info": "API information"
        },
        "offence_categories": [
            "Theft", "Assault", "Cyber Crime", "Cheating", "Harassment", "Other"
        ],
        "severity_levels": ["Low", "Medium", "High", "Critical"]
    }), 200


@app.route('/analyze_realtime', methods=['POST'])
def analyze_realtime():
    """
    Real-time analysis endpoint for live preview while typing.
    Provides quick classification and entity extraction.
    """
    try:
        json_data = request.get_json()
        text = json_data.get('text', '')
        
        if not text or len(text) < 10:
            return jsonify({
                "success": True,
                "offence_type": None,
                "confidence": 0,
                "entities_count": 0
            }), 200
        
        # Quick classification
        processed_text = preprocess_text(text)
        classification_result = classification_service.classify(processed_text)
        
        # Quick entity count
        entities = nlp_service.extract_entities(processed_text)
        entities_count = (
            len(entities.get("persons", [])) +
            len(entities.get("locations", [])) +
            len(entities.get("dates", [])) +
            len(entities.get("times", []))
        )
        
        return jsonify({
            "success": True,
            "offence_type": classification_result.label,
            "confidence": classification_result.confidence,
            "confidence_level": classification_service.get_confidence_level(classification_result.confidence),
            "entities_count": entities_count,
            "preview": {
                "persons": entities.get("persons", [])[:3],
                "locations": entities.get("locations", [])[:2],
                "dates": entities.get("dates", [])[:1]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Real-time analysis error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/fir_history', methods=['GET'])
def get_fir_history():
    """Get history of generated FIRs."""
    return jsonify({
        "success": True,
        "count": len(fir_history),
        "history": fir_history[-50:]  # Return last 50 entries
    }), 200


@app.route('/suggest_questions', methods=['POST'])
def suggest_questions():
    """
    Suggest follow-up questions based on the complaint text.
    Helps users provide more complete information.
    """
    try:
        json_data = request.get_json()
        text = json_data.get('text', '')
        
        if not text:
            return jsonify({
                "success": True,
                "suggestions": []
            }), 200
        
        processed_text = preprocess_text(text)
        entities = nlp_service.extract_entities(processed_text)
        classification_result = classification_service.classify(processed_text)
        
        suggestions = []
        
        # Check for missing information
        if not entities.get("dates"):
            suggestions.append("When did this incident occur? Please provide the date.")
        
        if not entities.get("times"):
            suggestions.append("What was the approximate time of the incident?")
        
        if not entities.get("locations"):
            suggestions.append("Where did this incident take place? Please provide the location.")
        
        if not entities.get("persons"):
            suggestions.append("Can you describe or name any persons involved in the incident?")
        
        # Offence-specific questions
        if classification_result.label == "Theft":
            suggestions.append("What items were stolen? Please list them with approximate values.")
            suggestions.append("Did you notice any suspicious persons or vehicles?")
        elif classification_result.label == "Cyber Crime":
            suggestions.append("Which platform or website was involved?")
            suggestions.append("Do you have any transaction IDs or reference numbers?")
            suggestions.append("How much money was involved, if any?")
        elif classification_result.label == "Assault":
            suggestions.append("Were there any witnesses to the incident?")
            suggestions.append("Did you sustain any injuries? If yes, please describe.")
            suggestions.append("Do you have any medical reports?")
        elif classification_result.label == "Harassment":
            suggestions.append("How long has this harassment been going on?")
            suggestions.append("Do you have any evidence (messages, recordings)?")
            suggestions.append("Have you reported this before?")
        elif classification_result.label == "Cheating":
            suggestions.append("What was the total amount involved?")
            suggestions.append("Do you have any documents or agreements?")
            suggestions.append("How was the payment made?")
        
        return jsonify({
            "success": True,
            "suggestions": suggestions[:5],  # Limit to 5 suggestions
            "offence_type": classification_result.label
        }), 200
        
    except Exception as e:
        logger.error(f"Suggestion error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("    Intelligent FIR Auto Writing System")
    print("    ML-Powered Backend API v2.0")
    print("=" * 60)
    print()
    
    # Initialize services before starting server
    print("Loading ML models (this may take a few moments)...")
    initialize_services()
    
    print()
    print("Server running on http://localhost:5000")
    print()
    print("Available Endpoints:")
    print("  POST /generate_fir     - Generate complete FIR")
    print("  POST /classify         - Classify offence type")
    print("  POST /extract_entities - Extract entities")
    print("  GET  /health           - Health check")
    print("  GET  /api/info         - API information")
    print()
    print("CORS enabled for: http://localhost:3000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
