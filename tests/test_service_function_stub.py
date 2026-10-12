#!/usr/bin/env python3
"""
Service function stub tests.
Tests stubbed service functions that would normally call external APIs.
"""

import pytest
from unittest.mock import Mock, patch
from src.afyaplus.mcp.tools import MCPTools
from src.afyaplus.rag.retriever import RAGRetriever


class TestServiceFunctionStubs:
    """Test stubbed service functions with mocked external dependencies."""
    
    def test_mcp_tool_stub_response(self):
        """Test MCP tool stub returns expected structure."""
        mcp = MCPTools()
        result = mcp.execute("test_operation", {"param": "value"})
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "stub"
        assert "data" in result
    
    def test_mcp_tool_stub_consistency(self):
        """Test MCP tool stub returns consistent results."""
        mcp = MCPTools()
        
        result1 = mcp.execute("operation1", {"key": "value1"})
        result2 = mcp.execute("operation1", {"key": "value1"})
        
        # Stub should return consistent results
        assert result1 == result2
    
    def test_rag_retriever_stub(self):
        """Test RAG retriever stub functionality."""
        retriever = RAGRetriever()
        results = retriever.search("test query")
        
        assert results is not None
        assert isinstance(results, list)
        assert len(results) > 0
        # Stub should return at least one result
        assert "content" in results[0]
    
    def test_rag_retriever_stub_with_context(self):
        """Test RAG retriever with context."""
        retriever = RAGRetriever()
        results = retriever.search("medical query", context={"department": "cardiology"})
        
        assert results is not None
        assert isinstance(results, list)
        # Context should be reflected in stub response
        assert any("cardiology" in str(r).lower() for r in results)
    
    def test_external_call_fallback(self):
        """Test fallback when external service unavailable."""
        mcp = MCPTools()
        
        # Simulate external service failure
        with patch.object(mcp, '_call_external_service', side_effect=Exception("Service unavailable")):
            result = mcp.execute("fallback_test", {})
            
            # Should fall back to stub
            assert result is not None
            assert result["status"] == "stub"
            assert "fallback" in result.get("reason", "").lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])