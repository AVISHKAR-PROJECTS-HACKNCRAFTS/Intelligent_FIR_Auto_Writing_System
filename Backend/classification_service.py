"""
Classification Service for FIR Generation System.
Uses transformer-based models for offence type classification.
"""

# IMPORTANT: Patch TensorFlow BEFORE any other imports
import tf_patch  # This patches TensorFlow imports

import os
import logging
from typing import Dict
from dataclasses import dataclass

# Disable TensorFlow imports - we only use PyTorch models
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Data class for classification results."""
    label: str
    confidence: float
    all_scores: Dict[str, float]


# Mapping for zero-shot classification labels
ZERO_SHOT_LABELS = [
    "theft or robbery or stealing",
    "physical assault or violence or attack",
    "cyber crime or online fraud or hacking",
    "cheating or fraud or scam",
    "harassment or stalking or threatening",
    "other criminal activity"
]

LABEL_MAPPING = {
    "theft or robbery or stealing": "Theft",
    "physical assault or violence or attack": "Assault",
    "cyber crime or online fraud or hacking": "Cyber Crime",
    "cheating or fraud or scam": "Cheating",
    "harassment or stalking or threatening": "Harassment",
    "other criminal activity": "Other"
}


class ClassificationService:
    """
    Classification service using transformer models for offence detection.
    Uses facebook/bart-large-mnli for zero-shot classification.
    """
    
    def __init__(self):
        """Initialize the classification service."""
        logger.info("Loading facebook/bart-large-mnli...")
        
        # Use direct model loading to avoid TensorFlow import issues with pipeline
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        model_name = "facebook/bart-large-mnli"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = -1  # CPU, use 0 for GPU
        self.model.eval()  # Set to evaluation mode
        
        if self.device >= 0:
            self.model = self.model.to(f"cuda:{self.device}")
        
        logger.info("Zero-shot classifier loaded successfully")
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify the offence type from complaint text.
        
        Args:
            text: Complaint description text
            
        Returns:
            ClassificationResult with label, confidence, and all scores
            
        Raises:
            Exception: If classification fails
        """
        import torch
        
        # Prepare inputs for each candidate label
        inputs_list = []
        for label in ZERO_SHOT_LABELS:
            inputs = self.tokenizer(text, label, return_tensors="pt", truncation=True, max_length=512)
            if self.device >= 0:
                inputs = {k: v.to(f"cuda:{self.device}") for k, v in inputs.items()}
            inputs_list.append(inputs)
        
        # Get scores for each label
        scores_dict = {}
        with torch.no_grad():
            for label, inputs in zip(ZERO_SHOT_LABELS, inputs_list):
                outputs = self.model(**inputs)
                logits = outputs.logits
                # BART MNLI outputs [entailment, neutral, contradiction]
                # We use entailment (index 0) as the score
                score = torch.softmax(logits, dim=-1)[0][0].item()
                scores_dict[label] = score
        
        # Sort by score
        sorted_labels = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Map results to our categories
        scores = {}
        for label, score in sorted_labels:
            mapped_label = LABEL_MAPPING.get(label, "Other")
            scores[mapped_label] = float(score)
        
        # Get top prediction
        top_label_key = sorted_labels[0][0]
        top_label = LABEL_MAPPING.get(top_label_key, "Other")
        top_confidence = float(sorted_labels[0][1])
        
        return ClassificationResult(
            label=top_label,
            confidence=top_confidence,
            all_scores=scores
        )
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get human-readable confidence level.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.5:
            return "Medium"
        else:
            return "Low"


# Singleton instance
_classification_service = None


def get_classification_service():
    """
    Get or create classification service singleton.
    
    Returns:
        ClassificationService instance
    """
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService()
    return _classification_service
