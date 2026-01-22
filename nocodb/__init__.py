__version__ = "3.0.0"

from .nocodb import (
    NocoDBBase,
    NocoDBProject,  # Deprecated alias for NocoDBBase
    AuthToken,
    APIToken,
    JWTAuthToken,
    WhereFilter,
    NocoDBClient,
)
