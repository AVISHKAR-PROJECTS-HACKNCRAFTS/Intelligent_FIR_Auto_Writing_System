"""
TensorFlow import patch to prevent broken TensorFlow installation from breaking transformers.
This module must be imported BEFORE any transformers imports.
"""

import sys
import types
from unittest.mock import MagicMock
from importlib.machinery import ModuleSpec

class TensorFlowMockLoader:
    """Mock loader for TensorFlow modules."""
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        pass

class TensorFlowMockModule(types.ModuleType):
    """Mock module that returns mocks for any attribute access and has proper __spec__."""
    def __init__(self, name):
        super().__init__(name)
        # Create a proper spec for importlib
        loader = TensorFlowMockLoader()
        self.__spec__ = ModuleSpec(name, loader, origin='mock-tensorflow')
        self.__spec__.submodule_search_locations = []
    
    def __getattr__(self, name):
        # Return another mock for any attribute access
        mock = MagicMock()
        setattr(self, name, mock)
        return mock

def patch_tensorflow():
    """Patch TensorFlow imports to prevent broken installation errors."""
    # Create mock modules with proper specs
    def create_mock_module(name):
        mock = TensorFlowMockModule(name)
        sys.modules[name] = mock
        return mock
    
    # Mock all TensorFlow modules
    tf_root = create_mock_module('tensorflow')
    create_mock_module('tensorflow._api')
    create_mock_module('tensorflow._api.v2')
    create_mock_module('tensorflow._api.v2.compat')
    create_mock_module('tensorflow._api.v2.compat.v1')
    create_mock_module('tensorflow._api.v2.compat.v1.compat')
    create_mock_module('tensorflow._api.v2.compat.v1.compat.v1')
    create_mock_module('tensorflow._api.v2.compat.v1.distribute')
    create_mock_module('tensorflow._api.v2.compat.v1.distribute.cluster_resolver')
    
    create_mock_module('tensorflow.python')
    create_mock_module('tensorflow.python.distribute')
    create_mock_module('tensorflow.python.distribute.cluster_resolver')
    
    # Handle the specific problematic import
    k8s_resolver = create_mock_module('tensorflow.python.distribute.cluster_resolver.kubernetes_cluster_resolver')
    # Add ExecutableLocation attribute that's being imported
    k8s_resolver.ExecutableLocation = MagicMock()
    
    sys.modules['tf'] = tf_root

# Apply the patch immediately when this module is imported
patch_tensorflow()

