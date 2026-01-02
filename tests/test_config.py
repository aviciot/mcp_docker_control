"""
Tests for Configuration Module
==============================
"""

import pytest
from config import load_config, validate_config


class TestConfig:
    """Test cases for configuration module"""
    
    def test_load_config(self, sample_config, monkeypatch, tmp_path):
        """Test configuration loading"""
        # This is a placeholder - actual implementation would need file mocking
        assert True  # Placeholder
    
    def test_validate_config_success(self, sample_config):
        """Test configuration validation with valid config"""
        result = validate_config(sample_config)
        assert result is True
    
    def test_validate_config_missing_server(self):
        """Test configuration validation with missing server config"""
        config = {'mcp': {}, 'security': {}, 'docker': {}}
        
        with pytest.raises(ValueError, match="Missing required configuration key: server"):
            validate_config(config)
    
    def test_validate_config_missing_port(self):
        """Test configuration validation with missing port"""
        config = {
            'server': {},
            'mcp': {'name': 'test'},
            'security': {'authentication': {}},
            'docker': {'socket_path': '/var/run/docker.sock'}
        }
        
        with pytest.raises(ValueError, match="Missing required configuration: server.port"):
            validate_config(config)
    
    def test_validate_config_auth_without_password(self):
        """Test configuration validation with auth enabled but no password"""
        config = {
            'server': {'port': 8300},
            'mcp': {'name': 'test'},
            'security': {'authentication': {'enabled': True, 'password': ''}},
            'docker': {'socket_path': '/var/run/docker.sock'}
        }
        
        with pytest.raises(ValueError, match="Authentication enabled but no password configured"):
            validate_config(config)
