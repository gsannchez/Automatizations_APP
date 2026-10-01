import contextvars
from typing import Optional
from dataclasses import dataclass

@dataclass
class TenantInfo:
    tenant_id: str
    tier: str # free, pro, enterprise
    max_concurrency: int

# Context variable to hold the current tenant information across async contexts
_tenant_context = contextvars.ContextVar[Optional[TenantInfo]]("tenant_context", default=None)

class TenantContext:
    """
    Manages the dependency injection of the active Tenant throughout 
    the request lifecycle or Celery task execution.
    """
    
    @staticmethod
    def set_tenant(tenant: TenantInfo):
        _tenant_context.set(tenant)

    @staticmethod
    def get_tenant() -> Optional[TenantInfo]:
        return _tenant_context.get()
        
    @staticmethod
    def get_tenant_id() -> str:
        tenant = _tenant_context.get()
        return tenant.tenant_id if tenant else "default_tenant"
