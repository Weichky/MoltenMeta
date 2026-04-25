"""
Data source discovery for Toop module.

Re-exports BinaryDataSourceDiscovery from geometric_model_core as ToopDataSourceDiscovery.
See geometric_model_core.data_source_discovery for the canonical implementation.
"""

from ..geometric_model_core.data_source_discovery import BinaryDataSourceDiscovery

ToopDataSourceDiscovery = BinaryDataSourceDiscovery

__all__ = ["ToopDataSourceDiscovery"]
