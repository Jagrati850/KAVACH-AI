"""
KAVACH AI — Database Engine & Session Management
Async SQLAlchemy setup with SQLite for hackathon, PostgreSQL-ready.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ── Engine ──────────────────────────────────────────────────
# SQLite needs connect_args for async; PostgreSQL does not
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# ── Session Factory ─────────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ──────────────────────────────────────────────
class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Dependency ──────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session per request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Lifecycle ───────────────────────────────────────────────
async def init_db():
    """Create all tables. Called on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db():
    """Drop and recreate all tables. Used by seeder."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seed_demo_users_if_missing():
    """Safely and idempotently seed required demo accounts if missing from database."""
    import uuid
    from sqlalchemy import select
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    demo_users = [
        {
            "email": "priya.sharma@gmail.com",
            "full_name": "Priya Sharma",
            "password": "Demo@2026",
            "role": UserRole.CITIZEN,
            "phone": "+919876543210",
            "organization": None,
            "designation": None,
        },
        {
            "email": "inspector.rajesh@cybercell.gov.in",
            "full_name": "Inspector Rajesh Kumar",
            "password": "Demo@2026",
            "role": UserRole.LEO,
            "phone": "+919876543220",
            "organization": "Cyber Crime Cell, Delhi Police",
            "designation": "Cyber Crime Inspector",
        },
        {
            "email": "vikram.shah@sbi.co.in",
            "full_name": "Vikram Shah",
            "password": "Demo@2026",
            "role": UserRole.BANK_ANALYST,
            "phone": "+919876543230",
            "organization": "State Bank of India",
            "designation": "Fraud Risk Analyst",
        },
        {
            "email": "admin@kavach.ai",
            "full_name": "System Administrator",
            "password": "Admin@2026",
            "role": UserRole.ADMIN,
            "phone": "+919876543200",
            "organization": "KAVACH AI Platform",
            "designation": "System Administrator",
        },
    ]

    async with async_session() as session:
        created_count = 0
        for u_data in demo_users:
            email = u_data["email"].strip().lower()
            result = await session.execute(select(User).where(User.email == email))
            existing = result.scalar_one_or_none()
            if not existing:
                user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    full_name=u_data["full_name"],
                    password_hash=hash_password(u_data["password"]),
                    phone=u_data["phone"],
                    role=u_data["role"],
                    organization=u_data["organization"],
                    designation=u_data["designation"],
                    is_active=True,
                    is_verified=True,
                )
                session.add(user)
                created_count += 1
        if created_count > 0:
            await session.commit()
            print(f"[OK] Seeded {created_count} missing demo user(s)")


async def close_db():
    """Dispose engine connections. Called on application shutdown."""
    await engine.dispose()
