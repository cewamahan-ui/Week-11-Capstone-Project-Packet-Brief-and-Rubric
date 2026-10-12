#!/usr/bin/env python3
"""
Domain twin logic unit tests.
Covers Week 1-5: Core domain logic without external dependencies.
"""

import pytest
from src.afyaplus.triage.domain_twin import DomainTwin
from src.afyaplus.triage.models import TriageRequest, TriageResponse


class TestDomainTwin:
    """Test domain twin logic for healthcare triage decisions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.twin = DomainTwin()
    
    def test_twin_initialization(self):
        """Test domain twin initialization."""
        assert self.twin is not None
        assert hasattr(self.twin, 'assess')
        assert hasattr(self.twin, 'recommend')
    
    def test_assessment_basic(self):
        """Test basic triage assessment."""
        request = TriageRequest(
            symptoms=["fever", "cough"],
            age=28,
            urgency_level="moderate",
            vitals={"temperature": 38.5, "heart_rate": 95}
        )
        
        response = self.twin.assess(request)
        
        assert response is not None
        assert isinstance(response, TriageResponse)
        assert response.confidence_score > 0
        assert response.recommendation is not None
    
    def test_recommendation_urgency_mapping(self):
        """Test urgency level mapping to recommendations."""
        test_cases = [
            ("high", "immediate_attention"),
            ("moderate", "within_24_hours"),
            ("low", "routine_follow_up"),
        ]
        
        for urgency, expected_recommendation in test_cases:
            request = TriageRequest(
                symptoms=["moderate_symptoms"],
                age=40,
                urgency_level=urgency
            )
            
            response = self.twin.assess(request)
            assert expected_recommendation in response.recommendation.lower()
    
    def test_age_based_adjustment(self):
        """Test age-based triage adjustments."""
        # Elderly patient with same symptoms
        elderly_request = TriageRequest(
            symptoms=["mild_fatigue"],
            age=70,
            urgency_level="low"
        )
        
        young_request = TriageRequest(
            symptoms=["mild_fatigue"],
            age=25,
            urgency_level="low"
        )
        
        elderly_response = self.twin.assess(elderly_request)
        young_response = self.twin.assess(young_request)
        
        # Elderly should have higher priority for same symptoms
        assert elderly_response.priority >= young_response.priority
    
    def test_confidence_scoring(self):
        """Test confidence scoring logic."""
        # Well-defined symptoms
        clear_request = TriageRequest(
            symptoms=["severe_chest_pain"],
            age=55,
            urgency_level="high"
        )
        
        # Vague symptoms
        vague_request = TriageRequest(
            symptoms=["feeling_off"],
            age=30,
            urgency_level="low"
        )
        
        clear_response = self.twin.assess(clear_request)
        vague_response = self.twin.assess(vague_request)
        
        # Clear symptoms should have higher confidence
        assert clear_response.confidence_score >= vague_response.confidence_score

if __name__ == "__main__":
    pytest.main([__file__, "-v"])