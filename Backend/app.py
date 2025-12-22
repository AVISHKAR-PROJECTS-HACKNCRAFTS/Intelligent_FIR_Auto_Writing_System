"""
Intelligent FIR Auto Writing System - Flask Backend API
Uses transformer-based NLP for entity extraction and ML-based classification.
"""

# IMPORTANT: Patch TensorFlow BEFORE any other imports
import tf_patch  # This patches TensorFlow imports

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
import uuid
import os
import tempfile
from datetime import datetime
from typing import Dict, Any
from werkzeug.utils import secure_filename

# Import custom services
from nlp_service import get_nlp_service
from classification_service import get_classification_service
from utils import (
    preprocess_text,
    get_ipc_sections,
    generate_fir_document,
    transcribe_audio
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


def initialize_services():
    """Initialize NLP and classification services at startup."""
    global nlp_service, classification_service
    
    logger.info("Initializing NLP service...")
    start_time = time.time()
    nlp_service = get_nlp_service()
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
    
    entities = nlp_service.extract_entities(processed_text)
    classification_result = classification_service.classify(processed_text)
    ipc_sections = get_ipc_sections(classification_result.label)
    location = entities["locations"][0] if entities["locations"] else "Not specified"
    result = {
        "name": name,
        "contact": contact,
        "witness_name": witness_name,
        "witness_contact": witness_contact,
        "location": location,
        "offence_type": classification_result.label,
        "confidence": classification_result.confidence,
        "confidence_level": classification_service.get_confidence_level(classification_result.confidence),
        "all_offence_scores": classification_result.all_scores,
        "extracted_entities": {
            "persons": entities["persons"],
            "locations": entities["locations"],
            "organizations": entities.get("organizations", [])
        },
        "ipc_sections": ipc_sections,
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
        - language: Language for FIR document ('en' or 'te', default: 'en')
        
    Returns:
        JSON with extracted entities, classification, IPC sections, and FIR text
    """
    try:
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        description = json_data.get('description', '')
        if not description or not description.strip():
            return jsonify({
                "success": False,
                "error": "Description field is required and cannot be empty"
            }), 400
        
        # Get language parameter (default to English)
        language = json_data.get('language', 'en')
        if language not in ['en', 'te']:
            language = 'en'
        
        start_time = time.time()
        result = process_complaint(json_data)
        processing_time = time.time() - start_time
        
        # Generate FIR ID first
        fir_id = f"FIR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Generate FIR document in requested language with FIR ID
        fir_text = generate_fir_document({
            **result,
            "extracted_persons": result["extracted_entities"]["persons"],
            "fir_id": fir_id
        }, language=language)
        
        response = {
            "success": True,
            "fir_id": fir_id,
            "name": result["name"],
            "contact": result["contact"],
            "location": result["location"],
            "offence_type": result["offence_type"],
            "witness_name": result["witness_name"],
            "witness_contact": result["witness_contact"],
            "confidence": result["confidence"],
            "confidence_level": result["confidence_level"],
            "all_offence_scores": result["all_offence_scores"],
            "extracted_entities": result["extracted_entities"],
            "extracted_persons": result["extracted_entities"]["persons"],
            "ipc_sections": result["ipc_sections"],
            "fir_text": fir_text,
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
    """Classify offence type without full FIR generation."""
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
    """Extract entities without classification."""
    try:
        json_data = request.get_json()
        
        if not json_data or not json_data.get('text'):
            return jsonify({
                "success": False,
                "error": "Text field is required"
            }), 400
        
        text = preprocess_text(json_data.get('text', ''))
        entities = nlp_service.extract_entities(text)
        
        return jsonify({
            "success": True,
            "entities": entities
        }), 200
        
    except Exception as e:
        logger.error(f"Entity extraction error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio_endpoint():
    """
    POST endpoint to transcribe audio to text.
    
    Expects:
        - audio file in request.files with key 'audio'
        
    Returns:
        JSON with transcribed text
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                "success": False,
                "error": "No audio file selected"
            }), 400
        
        # Save the audio file temporarily
        filename = secure_filename(audio_file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{filename}")
        
        try:
            audio_file.save(temp_path)
            
            # Transcribe the audio
            logger.info(f"Transcribing audio file: {filename}")
            start_time = time.time()
            transcribed_text = transcribe_audio(temp_path)
            processing_time = time.time() - start_time
            
            logger.info(f"Audio transcribed in {processing_time:.2f}s")
            
            return jsonify({
                "success": True,
                "text": transcribed_text,
                "processing_time_seconds": round(processing_time, 3)
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
    
    except Exception as e:
        logger.error(f"Audio transcription error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Error transcribing audio: {str(e)}"
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


@app.route('/analyze_realtime', methods=['POST'])
def analyze_realtime():
    """Real-time analysis endpoint for live preview while typing."""
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
        
        processed_text = preprocess_text(text)
        classification_result = classification_service.classify(processed_text)
        entities = nlp_service.extract_entities(processed_text)
        entities_count = (
            len(entities.get("persons", [])) +
            len(entities.get("locations", [])) +
            len(entities.get("organizations", []))
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
                "organizations": entities.get("organizations", [])[:2]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Real-time analysis error: {str(e)}")
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
    print("  POST /analyze_realtime - Real-time analysis")
    print("  GET  /health           - Health check")
    print()
    print("CORS enabled for: http://localhost:3000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
