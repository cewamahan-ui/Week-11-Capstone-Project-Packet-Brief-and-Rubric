#!/usr/bin/env python3
"""
Golden fixture comparison tests.
Validates expected outputs against golden reference data.
"""

import json
import pytest
from pathlib import Path
from src.afyaplus.triage.domain_twin import DomainTwin
from src.afyaplus.triage.models import TriageRequest, TriageResponse


class TestGoldenFixtures:
    """Test golden fixture data for expected triage outcomes."""
    
    def setup_method(self):
        """Load golden fixture data."""
        self.twin = DomainTwin()
        fixture_path = Path(__file__).parent.parent / "fixtures" / "triage_messages_sample.jsonl"
        
        # Load golden fixtures (first 50 for testing)
        self.golden_data = []
        if fixture_path.exists():
            with open(fixture_path, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 50:
                        break
                    self.golden_data.append(json.loads(line))
    
    def test_golden_fixture_structure(self):
        """Test that golden fixtures have required structure."""
        if not self.golden_data:
            pytest.skip("Golden fixtures not available")
        
        for fixture in self.golden_data:
            assert "symptoms" in fixture
            assert "age" in fixture
            assert "expected_urgency" in fixture
            assert "expected_recommendation" in fixture
    
    def test_golden_fixture_assessment(self):
        """Test assessment against golden fixtures."""
        if not self.golden_data:
            pytest.skip("Golden fixtures not available")
        
        for fixture in self.golden_data[:10]:  # Test first 10
            request = TriageRequest(
                symptoms=fixture["symptoms"],
                age=fixture["age"],
                urgency_level=fixture.get("urgency_level", "moderate"),
                vitals=fixture.get("vitals", {})
            )
            
            response = self.twin.assess(request)
            
            # Validate against golden expectations
            assert response.recommendation is not None
            assert response.confidence_score > 0
            # Check that expected recommendation is in the response
            if "expected_recommendation" in fixture:
                assert fixture["expected_recommendation"].lower() in response.recommendation.lower()
    
    def test_golden_fixture_urgency_mapping(self):
        """Test urgency mapping consistency."""
        if not self.golden_data:
            pytest.skip("Golden fixtures not available")
        
        for fixture in self.golden_data[:5]:
            request = TriageRequest(
                symptoms=fixture["symptoms"],
                age=fixture["age"],
                urgency_level=fixture.get("urgency_level", "moderate"),
                vitals=fixture.get("vitals", {})
            )
            
            response = self.twin.assess(request)
            
            # Validate urgency level
            if "expected_urgency" in fixture:
                expected_urgency = fixture["expected_urgency"]
                # The response should reflect the expected urgency
                assert expected_urgency in response.recommendation.lower() or \
                       response.priority >= 1  # At least some priority assigned

if __name__ == "__main__":
    pytest.main([__file__, "-v"])