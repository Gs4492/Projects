from sqlalchemy import DateTime, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class HealthLog(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    bp_systolic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bp_diastolic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sugar_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alcohol_units: Mapped[float | None] = mapped_column(Float, nullable=True)
    drink_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    drink_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    drink_size_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    drink_volume_ml: Mapped[float | None] = mapped_column(Float, nullable=True)
    salt_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    water_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_json: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(Text, nullable=False)
    reasons_json: Mapped[str] = mapped_column(Text, nullable=False)
    actions_json: Mapped[str] = mapped_column(Text, nullable=False)
