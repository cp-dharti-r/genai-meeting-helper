from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

