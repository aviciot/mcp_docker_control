"""
Pytest Configuration
===================
"""

import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'server': {'port': 8300, 'host': '0.0.0.0'},
        'mcp': {'name': 'docker-control'},
        'security': {'authentication': {'enabled': False, 'password': ''}},
        'docker': {
            'socket_path': '/var/run/docker.sock',
            'filter': {'whitelist': [], 'blacklist': []},
            'audit': {'enabled': True, 'log_path': 'logs/audit.log'}
        }
    }


@pytest.fixture
def mock_container():
    """Mock Docker container for testing"""
    class MockContainer:
        def __init__(self):
            self.name = "test-container"
            self.short_id = "abc123"
            self.status = "running"
            self.ports = {}
            self.labels = {}
            self.image = type('obj', (object,), {'tags': ['test:latest'], 'short_id': 'img123'})
            self.attrs = {
                'State': {
                    'Status': 'running',
                    'Running': True,
                    'Paused': False,
                    'Restarting': False,
                    'OOMKilled': False,
                    'Dead': False,
                    'Pid': 1234,
                    'ExitCode': 0,
                    'StartedAt': '2024-01-01T00:00:00.000000000Z',
                    'FinishedAt': '0001-01-01T00:00:00Z'
                },
                'Created': '2024-01-01T00:00:00.000000000Z'
            }
        
        def start(self):
            self.status = "running"
        
        def stop(self, timeout=10):
            self.status = "exited"
        
        def restart(self, timeout=10):
            pass
        
        def logs(self, **kwargs):
            return b"Sample log output\nLine 2\nLine 3"
    
    return MockContainer()
