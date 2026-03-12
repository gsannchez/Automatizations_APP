"""UUID v7 generation utility for time-ordered UUIDs.

UUID v7 provides better database indexing performance than UUID v4
due to time-based ordering while maintaining uniqueness.
"""
from uuid import UUID
from uuid6 import uuid7


def generate_uuid7() -> UUID:
    """Generate a UUID v7 (time-ordered UUID).
    
    Returns:
        UUID: A version 7 UUID with timestamp-based ordering
    """
    return uuid7()
