"""
Data source discovery for Kohler module.

Re-exports BinaryDataSourceDiscovery from geometric_model_core as KohlerDataSourceDiscovery.
See geometric_model_core.data_source_discovery for the canonical implementation.
"""

from ..geometric_model_core.data_source_discovery import BinaryDataSourceDiscovery

KohlerDataSourceDiscovery = BinaryDataSourceDiscovery

__all__ = ["KohlerDataSourceDiscovery"]
