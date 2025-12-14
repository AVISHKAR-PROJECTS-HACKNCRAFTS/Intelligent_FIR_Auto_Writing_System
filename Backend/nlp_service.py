"""
NLP Service for FIR Generation System.
Uses transformer-based models for Named Entity Recognition.
"""

# IMPORTANT: Patch TensorFlow BEFORE any other imports
import tf_patch  # This patches TensorFlow imports

import os
from typing import Dict, List, Any, Optional
import logging

# Disable TensorFlow imports - we only use PyTorch models
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPService:
    """
    NLP Service using transformer-based models for entity extraction.
    Uses dslim/bert-base-NER for Named Entity Recognition.
    """
    
    def __init__(self):
        """Initialize NLP Service."""
        logger.info("Loading dslim/bert-base-NER...")
        
        # Use direct model loading to avoid TensorFlow import issues with pipeline
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        import torch
        
        model_name = "dslim/bert-base-NER"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.model.eval()  # Set to evaluation mode
        
        logger.info("Transformer NER model loaded successfully")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text for entity extraction
            
        Returns:
            Dictionary containing extracted entities by category
            
        Raises:
            Exception: If entity extraction fails
        """
        entities = {
            "persons": [],
            "locations": [],
            "organizations": []
        }
        
        # Direct model inference (avoiding pipeline to prevent TensorFlow imports)
        import torch
        
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predictions = torch.argmax(predictions, dim=-1)
        
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        labels = [self.model.config.id2label[pred.item()] for pred in predictions[0]]
        scores = [torch.max(probs).item() for probs in torch.nn.functional.softmax(outputs.logits, dim=-1)[0]]
        
        # Aggregate entities
        current_entity = None
        current_text = []
        current_scores = []
        
        for token, label, score in zip(tokens, labels, scores):
            # Skip special tokens
            if token in ['[CLS]', '[SEP]', '[PAD]']:
                continue
            
            # Clean token (remove ## prefix from wordpiece tokens)
            clean_token = token.replace('##', '')
            
            if label.startswith("B-"):
                # Save previous entity if exists
                if current_entity and current_text:
                    entity_text = self.tokenizer.convert_tokens_to_string(current_text).strip().replace(' ##', '')
                    avg_score = sum(current_scores) / len(current_scores) if current_scores else 0
                    
                    if entity_text and avg_score >= 0.5:
                        entity_type = current_entity.replace("B-", "").replace("I-", "")
                        if entity_type == "PER" and len(entity_text) > 1:
                            entities["persons"].append(entity_text)
                        elif entity_type == "LOC" and len(entity_text) > 1:
                            entities["locations"].append(entity_text)
                        elif entity_type == "ORG" and len(entity_text) > 1:
                            entities["organizations"].append(entity_text)
                
                # Start new entity
                current_entity = label
                current_text = [token]
                current_scores = [score]
            elif label.startswith("I-") and current_entity:
                entity_type_current = label.replace("I-", "")
                entity_type_prev = current_entity.replace("B-", "").replace("I-", "")
                if entity_type_current == entity_type_prev:
                    current_text.append(token)
                    current_scores.append(score)
                else:
                    # Entity type changed, save previous and start new
                    if current_text:
                        entity_text = self.tokenizer.convert_tokens_to_string(current_text).strip().replace(' ##', '')
                        avg_score = sum(current_scores) / len(current_scores) if current_scores else 0
                        if entity_text and avg_score >= 0.5:
                            if entity_type_prev == "PER" and len(entity_text) > 1:
                                entities["persons"].append(entity_text)
                            elif entity_type_prev == "LOC" and len(entity_text) > 1:
                                entities["locations"].append(entity_text)
                            elif entity_type_prev == "ORG" and len(entity_text) > 1:
                                entities["organizations"].append(entity_text)
                    current_entity = label
                    current_text = [token]
                    current_scores = [score]
            else:
                # O label or different entity type - save previous if exists
                if current_entity and current_text:
                    entity_text = self.tokenizer.convert_tokens_to_string(current_text).strip().replace(' ##', '')
                    avg_score = sum(current_scores) / len(current_scores) if current_scores else 0
                    if entity_text and avg_score >= 0.5:
                        entity_type = current_entity.replace("B-", "").replace("I-", "")
                        if entity_type == "PER" and len(entity_text) > 1:
                            entities["persons"].append(entity_text)
                        elif entity_type == "LOC" and len(entity_text) > 1:
                            entities["locations"].append(entity_text)
                        elif entity_type == "ORG" and len(entity_text) > 1:
                            entities["organizations"].append(entity_text)
                current_entity = None
                current_text = []
                current_scores = []
        
        # Don't forget the last entity
        if current_entity and current_text:
            entity_text = self.tokenizer.convert_tokens_to_string(current_text).strip().replace(' ##', '')
            avg_score = sum(current_scores) / len(current_scores) if current_scores else 0
            if entity_text and avg_score >= 0.5:
                entity_type = current_entity.replace("B-", "").replace("I-", "")
                if entity_type == "PER" and len(entity_text) > 1:
                    entities["persons"].append(entity_text)
                elif entity_type == "LOC" and len(entity_text) > 1:
                    entities["locations"].append(entity_text)
                elif entity_type == "ORG" and len(entity_text) > 1:
                    entities["organizations"].append(entity_text)
        
        # Deduplicate
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))
        
        return entities


# Singleton instance
_nlp_service: Optional[NLPService] = None


def get_nlp_service() -> NLPService:
    """
    Get or create NLP service singleton.
    
    Returns:
        NLPService instance
    """
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService()
    return _nlp_service
