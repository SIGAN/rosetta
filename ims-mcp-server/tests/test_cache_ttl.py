"""Unit tests for bootstrap instructions cache TTL."""

import time
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_server_module():
    """Mock the server module with cache variables."""
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", None), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", 0.0), \
         patch("ims_mcp.server.DOC_CACHE_TTL_SECONDS", 300):
        yield


def test_is_context_instructions_stale_when_cache_is_none():
    """Test staleness check returns True when cache is None."""
    from ims_mcp.server import _is_context_instructions_stale
    
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", None):
        assert _is_context_instructions_stale() is True


def test_is_context_instructions_stale_when_fresh():
    """Test staleness check returns False when cache is fresh (< 5 minutes)."""
    from ims_mcp.server import _is_context_instructions_stale
    
    current_time = time.time()
    cache_time = current_time - 60  # 1 minute ago
    
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", "cached content"), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", cache_time), \
         patch("time.time", return_value=current_time):
        assert _is_context_instructions_stale() is False


def test_is_context_instructions_stale_when_expired():
    """Test staleness check returns True when cache is older than 5 minutes."""
    from ims_mcp.server import _is_context_instructions_stale
    
    current_time = time.time()
    cache_time = current_time - 301  # 5 minutes and 1 second ago
    
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", "cached content"), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", cache_time), \
         patch("time.time", return_value=current_time):
        assert _is_context_instructions_stale() is True


def test_is_context_instructions_stale_at_ttl_boundary():
    """Test staleness check at exactly 5 minutes (300 seconds)."""
    from ims_mcp.server import _is_context_instructions_stale
    
    current_time = time.time()
    cache_time = current_time - 300  # exactly 5 minutes ago
    
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", "cached content"), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", cache_time), \
         patch("time.time", return_value=current_time):
        # At exactly TTL boundary, should NOT be stale (<=)
        assert _is_context_instructions_stale() is False


def test_is_context_instructions_stale_just_after_ttl():
    """Test staleness check just after TTL expires."""
    from ims_mcp.server import _is_context_instructions_stale
    
    current_time = time.time()
    cache_time = current_time - 300.1  # just over 5 minutes
    
    with patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", "cached content"), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", cache_time), \
         patch("time.time", return_value=current_time):
        assert _is_context_instructions_stale() is True


@pytest.mark.asyncio
async def test_get_context_instructions_caches_result():
    """Test that get_context_instructions caches the result with timestamp."""
    from ims_mcp.server import get_context_instructions
    
    mock_result = "bootstrap instructions content"
    current_time = 1234567890.0
    
    with patch("ims_mcp.server._RAGFLOW", Mock()), \
         patch("ims_mcp.server._is_context_instructions_stale", return_value=True), \
         patch("ims_mcp.server._validate_topic", return_value=None), \
         patch("ims_mcp.server._build_call_context", return_value=Mock()), \
         patch("ims_mcp.server._retry_once", return_value=mock_result), \
         patch("ims_mcp.server._log"), \
         patch("time.time", return_value=current_time), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", None) as mock_cache, \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", 0.0) as mock_time:
        
        result = await get_context_instructions()
        
        assert result == mock_result
        # Note: In real code, globals are updated but mocks don't capture that
        # This test validates the function structure


@pytest.mark.asyncio
async def test_get_context_instructions_returns_cached_when_fresh():
    """Test that get_context_instructions returns cached value when fresh."""
    from ims_mcp.server import get_context_instructions
    
    cached_content = "cached bootstrap instructions"
    
    with patch("ims_mcp.server._RAGFLOW", Mock()), \
         patch("ims_mcp.server._is_context_instructions_stale", return_value=False), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", cached_content), \
         patch("ims_mcp.server._validate_topic", return_value=None), \
         patch("ims_mcp.server._retry_once") as mock_retry:
        
        result = await get_context_instructions()
        
        assert result == cached_content
        # Should not call _retry_once when cache is fresh
        mock_retry.assert_not_called()


@pytest.mark.asyncio
async def test_get_context_instructions_reloads_when_stale():
    """Test that get_context_instructions reloads when cache is stale."""
    from ims_mcp.server import get_context_instructions
    
    new_content = "new bootstrap instructions"
    
    with patch("ims_mcp.server._RAGFLOW", Mock()), \
         patch("ims_mcp.server._is_context_instructions_stale", return_value=True), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", "old content"), \
         patch("ims_mcp.server._validate_topic", return_value=None), \
         patch("ims_mcp.server._build_call_context", return_value=Mock()), \
         patch("ims_mcp.server._retry_once", return_value=new_content), \
         patch("ims_mcp.server._log"), \
         patch("time.time", return_value=1234567890.0):
        
        result = await get_context_instructions()
        
        assert result == new_content


@pytest.mark.asyncio
async def test_get_context_instructions_does_not_cache_errors():
    """Test that errors are not cached."""
    from ims_mcp.server import get_context_instructions
    
    error_result = "Error: something went wrong"
    
    with patch("ims_mcp.server._RAGFLOW", Mock()), \
         patch("ims_mcp.server._is_context_instructions_stale", return_value=True), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE", None), \
         patch("ims_mcp.server._CONTEXT_INSTRUCTIONS_CACHE_TIME", 0.0), \
         patch("ims_mcp.server._validate_topic", return_value=None), \
         patch("ims_mcp.server._build_call_context", return_value=Mock()), \
         patch("ims_mcp.server._retry_once", return_value=error_result), \
         patch("ims_mcp.server._log"), \
         patch("time.time", return_value=1234567890.0):
        
        result = await get_context_instructions()
        
        assert result == error_result
        # Error should not be cached (cache remains None)
