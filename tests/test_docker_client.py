"""
Tests for Docker Client Utilities
=================================
"""

import pytest
from utils.docker_client import is_container_allowed, filter_containers


class TestDockerClient:
    """Test cases for Docker client utilities"""
    
    def test_is_container_allowed_no_filter(self, monkeypatch):
        """Test container allowed with no filtering"""
        monkeypatch.setattr('utils.docker_client.get_config', lambda: {
            'docker': {'filter': {'whitelist': [], 'blacklist': []}}
        })
        
        assert is_container_allowed("test-container") is True
    
    def test_is_container_allowed_whitelist(self, monkeypatch):
        """Test container allowed with whitelist"""
        monkeypatch.setattr('utils.docker_client.get_config', lambda: {
            'docker': {'filter': {'whitelist': ['allowed-container'], 'blacklist': []}}
        })
        
        assert is_container_allowed("allowed-container") is True
        assert is_container_allowed("blocked-container") is False
    
    def test_is_container_allowed_blacklist(self, monkeypatch):
        """Test container allowed with blacklist"""
        monkeypatch.setattr('utils.docker_client.get_config', lambda: {
            'docker': {'filter': {'whitelist': [], 'blacklist': ['blocked-container']}}
        })
        
        assert is_container_allowed("allowed-container") is True
        assert is_container_allowed("blocked-container") is False
    
    def test_filter_containers(self, mock_container, monkeypatch):
        """Test container filtering"""
        monkeypatch.setattr('utils.docker_client.get_config', lambda: {
            'docker': {'filter': {'whitelist': [], 'blacklist': []}}
        })
        
        containers = [mock_container]
        filtered = filter_containers(containers)
        
        assert len(filtered) == 1
        assert filtered[0].name == "test-container"
