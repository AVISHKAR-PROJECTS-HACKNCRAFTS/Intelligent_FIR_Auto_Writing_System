"""
Classification Service for FIR Generation System.
Uses transformer-based models for offence type classification.
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Data class for classification results."""
    label: str
    confidence: float
    all_scores: Dict[str, float]


# Offence categories with descriptions for zero-shot classification
OFFENCE_CATEGORIES = {
    "Theft": [
        "theft", "robbery", "burglary", "stealing", "larceny",
        "snatching", "pickpocket", "shoplifting", "vehicle theft",
        "property stolen", "belongings taken", "valuables missing"
    ],
    "Assault": [
        "assault", "physical attack", "beating", "violence", "fight",
        "bodily harm", "injury", "hit", "punch", "kick", "attack",
        "murder", "attempted murder", "grievous hurt", "manslaughter"
    ],
    "Cyber Crime": [
        "cyber crime", "online fraud", "hacking", "phishing", "identity theft",
        "social media fraud", "facebook scam", "instagram fraud", "online scam",
        "data breach", "ransomware", "cyber stalking", "online harassment",
        "bank account hacked", "upi fraud", "credit card fraud", "otp fraud"
    ],
    "Cheating": [
        "cheating", "fraud", "deception", "scam", "con",
        "financial fraud", "money fraud", "fake documents", "forgery",
        "embezzlement", "misappropriation", "breach of trust", "ponzi scheme"
    ],
    "Harassment": [
        "harassment", "stalking", "threatening", "intimidation", "bullying",
        "sexual harassment", "workplace harassment", "domestic violence",
        "eve teasing", "dowry harassment", "mental torture", "abuse"
    ],
    "Other": [
        "other crime", "miscellaneous", "general complaint", "unknown offence"
    ]
}

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
    """
    
    def __init__(self):
        """Initialize the classification service."""
        self.classifier = None
        self.sentence_model = None
        self.use_zero_shot = True
        self._load_models()
    
    def _load_models(self):
        """Load classification models."""
        # Try zero-shot classification first (most versatile)
        try:
            self._load_zero_shot_classifier()
        except Exception as e:
            logger.warning(f"Zero-shot classifier failed: {e}")
            try:
                self._load_sentence_transformer()
            except Exception as e2:
                logger.warning(f"Sentence transformer failed: {e2}")
                logger.info("Using fallback keyword-based classification")
                self.use_zero_shot = False
    
    def _load_zero_shot_classifier(self):
        """Load zero-shot classification pipeline."""
        from transformers import pipeline
        
        logger.info("Loading zero-shot classification model...")
        
        # Use a smaller, efficient model for zero-shot
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # CPU, use 0 for GPU
        )
        
        logger.info("Zero-shot classifier loaded successfully")
    
    def _load_sentence_transformer(self):
        """Load sentence transformer for similarity-based classification."""
        from sentence_transformers import SentenceTransformer
        
        logger.info("Loading sentence transformer model...")
        
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.use_zero_shot = False
        
        # Pre-compute embeddings for category descriptions
        self._compute_category_embeddings()
        
        logger.info("Sentence transformer loaded successfully")
    
    def _compute_category_embeddings(self):
        """Pre-compute embeddings for offence categories."""
        self.category_embeddings = {}
        
        for category, keywords in OFFENCE_CATEGORIES.items():
            # Create a representative text for each category
            category_text = " ".join(keywords)
            embedding = self.sentence_model.encode(category_text)
            self.category_embeddings[category] = embedding
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify the offence type from complaint text.
        
        Args:
            text: Complaint description text
            
        Returns:
            ClassificationResult with label, confidence, and all scores
        """
        if self.classifier is not None:
            return self._classify_zero_shot(text)
        elif self.sentence_model is not None:
            return self._classify_similarity(text)
        else:
            return self._classify_fallback(text)
    
    def _classify_zero_shot(self, text: str) -> ClassificationResult:
        """Classify using zero-shot classification."""
        try:
            # Run zero-shot classification
            result = self.classifier(
                text,
                candidate_labels=ZERO_SHOT_LABELS,
                multi_label=False
            )
            
            # Map results to our categories
            scores = {}
            for label, score in zip(result['labels'], result['scores']):
                mapped_label = LABEL_MAPPING.get(label, "Other")
                scores[mapped_label] = score
            
            # Get top prediction
            top_label = LABEL_MAPPING.get(result['labels'][0], "Other")
            top_confidence = result['scores'][0]
            
            return ClassificationResult(
                label=top_label,
                confidence=float(top_confidence),
                all_scores=scores
            )
            
        except Exception as e:
            logger.error(f"Zero-shot classification error: {e}")
            return self._classify_fallback(text)
    
    def _classify_similarity(self, text: str) -> ClassificationResult:
        """Classify using sentence similarity."""
        try:
            # Encode input text
            text_embedding = self.sentence_model.encode(text)
            
            # Calculate similarity with each category
            scores = {}
            for category, cat_embedding in self.category_embeddings.items():
                # Cosine similarity
                similarity = np.dot(text_embedding, cat_embedding) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(cat_embedding)
                )
                scores[category] = float(similarity)
            
            # Normalize scores to probabilities using softmax
            score_values = np.array(list(scores.values()))
            exp_scores = np.exp(score_values - np.max(score_values))
            probabilities = exp_scores / exp_scores.sum()
            
            for i, category in enumerate(scores.keys()):
                scores[category] = float(probabilities[i])
            
            # Get top prediction
            top_category = max(scores, key=scores.get)
            top_confidence = scores[top_category]
            
            return ClassificationResult(
                label=top_category,
                confidence=top_confidence,
                all_scores=scores
            )
            
        except Exception as e:
            logger.error(f"Similarity classification error: {e}")
            return self._classify_fallback(text)
    
    def _classify_fallback(self, text: str) -> ClassificationResult:
        """Fallback keyword-based classification with scoring."""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in OFFENCE_CATEGORIES.items():
            # Count keyword matches
            match_count = sum(1 for kw in keywords if kw.lower() in text_lower)
            # Weight by keyword specificity
            score = match_count / len(keywords) if keywords else 0
            scores[category] = score
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            for category in scores:
                scores[category] /= total_score
        else:
            # Default to "Other" if no matches
            scores["Other"] = 1.0
        
        # Get top prediction
        top_category = max(scores, key=scores.get)
        top_confidence = scores[top_category]
        
        # Ensure minimum confidence for "Other"
        if top_confidence < 0.2:
            top_category = "Other"
            top_confidence = 0.5
        
        return ClassificationResult(
            label=top_category,
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
_classification_service: Optional[ClassificationService] = None


def get_classification_service() -> ClassificationService:
    """
    Get or create classification service singleton.
    
    Returns:
        ClassificationService instance
    """
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService()
    return _classification_service
