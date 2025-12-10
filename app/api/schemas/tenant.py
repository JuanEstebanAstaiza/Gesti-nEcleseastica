"""Schemas para gestión de tenants (super admin)"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class TenantCreate(BaseModel):
    name: str
    slug: str
    subdomain: str | None = None
    custom_domain: str | None = None
    plan_id: int | None = None


class TenantUpdate(BaseModel):
    name: str | None = None
    subdomain: str | None = None
    custom_domain: str | None = None
    is_active: bool | None = None
    plan_id: int | None = None


class TenantRead(BaseModel):
    id: UUID
    slug: str
    name: str
    subdomain: str | None
    custom_domain: str | None
    db_name: str
    is_active: bool
    plan_id: int | None
    created_at: datetime
    expires_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TenantAdminCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class TenantAdminRead(BaseModel):
    id: int
    tenant_id: UUID
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SuperAdminCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class SuperAdminRead(BaseModel):
    id: int
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str


class SubscriptionPlanCreate(BaseModel):
    name: str
    description: str | None = None
    max_users: int | None = None
    max_storage_mb: int | None = None
    features: dict | None = None
    price_monthly: float | None = None


class SubscriptionPlanRead(BaseModel):
    id: int
    name: str
    description: str | None
    max_users: int | None
    max_storage_mb: int | None
    features: dict | None
    price_monthly: float | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PlatformStats(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users: int
    total_donations_amount: float

