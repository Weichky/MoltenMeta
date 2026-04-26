"""
Data source discovery for Maggianu module.

Re-exports BinaryDataSourceDiscovery from geometric_model_core as MaggianuDataSourceDiscovery.
See geometric_model_core.data_source_discovery for the canonical implementation.
"""

from ..geometric_model_core.data_source_discovery import BinaryDataSourceDiscovery

MaggianuDataSourceDiscovery = BinaryDataSourceDiscovery

__all__ = ["MaggianuDataSourceDiscovery"]
