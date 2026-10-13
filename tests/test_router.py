#!/usr/bin/env python3
"""
Router unit tests for deterministic request routing logic.
Covers Week 1-2: LLM/RAG fundamentals routing patterns.
"""

import pytest
from src.afyaplus.router.deterministic import Router
from src.afyaplus.triage.models import TriageRequest
class TestDeterministicRouter:
    """Test deterministic routing logic without LLM dependency."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = Router()
    
    def test_router_initialization(self):
        """Test router initialization."""
        assert self.router is not None
        assert hasattr(self.router, 'route')
    
    def test_triage_routing_basic(self):
        """Test basic triage routing with stub data."""
        # Create test triage request
        request = TriageRequest(
            symptoms=["headache", "fever"],
            age=35,
            urgency_level="moderate"
        )
        
        # Test routing - deterministic stub logic
        route = self.router.route(request)
        
        # Basic validation
        assert route is not None
        assert "endpoint" in route
        assert "priority" in route
    
    def test_routing_consistency(self):
        """Test that same input produces same output (deterministic)."""
        request = TriageRequest(
            symptoms=["chest_pain"],
            age=45,
            urgency_level="high"
        )
        
        route1 = self.router.route(request)
        route2 = self.router.route(request)
        
        # Should be deterministic
        assert route1 == route2
        assert route1["priority"] == route2["priority"]
    
    def test_symptom_based_routing(self):
        """Test symptom-based routing logic."""
        # Test various symptom combinations
        test_cases = [
            (["minor_cut"], "emergency_department"),
            (["headache", "mild"], "primary_care"),
            (["fever", "high"], "urgent_care"),
            (["routine_checkup"], "general_practice")
        ]
        
        for symptoms, expected_endpoint in test_cases:
            request = TriageRequest(
                symptoms=symptoms,
                age=30,
                urgency_level="moderate"
            )
            
            route = self.router.route(request)
            assert route["endpoint"] == expected_endpoint

if __name__ == "__main__":
    pytest.main([__file__, "-v"])