from sqlalchemy import Integer, String, ForeignKey, Text, DateTime, Float, Enum as PgEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB  
import uuid
from datetime import datetime
from .base_model import Base  
from app.schemas.training_schema import VisibilityMode, DifficultyLevel

class Presentation(Base):
    __tablename__ = "presentations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    file_url: Mapped[str] = mapped_column(String(255), nullable=True)
    # DEPRECATED: Remove this in future migration
    # findings: Mapped[dict] = mapped_column(JSONB, default=dict)

    trainings: Mapped[list["Training"]] = relationship(
        "Training", back_populates="presentation", cascade="all, delete", 
        lazy="selectin",  
    )

    finding_entries: Mapped[list["PresentationFinding"]] = relationship(
        "PresentationFinding",
        back_populates="presentation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Training(Base):
    __tablename__ = "trainings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    presentation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("presentations.id"), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="Total score for the training session")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    presentation: Mapped["Presentation"] = relationship("Presentation", back_populates="trainings")
    video_url: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Permanent MinIO URL for the recording"
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Total session time in seconds"
    )

    visibility_mode: Mapped[VisibilityMode] = mapped_column(
        PgEnum(VisibilityMode, name="visibility_mode"), nullable=True
    )

    difficulty: Mapped[DifficultyLevel] = mapped_column(
        PgEnum(DifficultyLevel, name="difficulty_level"), nullable=True
    )

    eye_calibration: Mapped[dict] = mapped_column(
        JSONB, nullable=True, comment="Raw calibration JSON from frontend"
    )
    blendshapes: Mapped[list["Blendshape"]] = relationship(
    "Blendshape",
    back_populates="training",
    cascade="all, delete-orphan",
    lazy="selectin"
) 
    training_results: Mapped[list["TrainingResult"]] = relationship(
        "TrainingResult",
        back_populates="training",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    slide_events: Mapped[list[dict]] = mapped_column(
        JSONB, nullable=True, comment="List of slide change events as [{timestamp, page}]"
    )



class PresentationFinding(Base):
    __tablename__ = "presentation_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    presentation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False
    )
    findings: Mapped[dict] = mapped_column(JSONB, default=dict)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    cockpit_score: Mapped[float] = mapped_column(Float, nullable=True)
    flight_path_score: Mapped[float] = mapped_column(Float, nullable=True)
    altitude_score: Mapped[float] = mapped_column(Float, nullable=True)
    preflight_check_score: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=False)
    presentation: Mapped["Presentation"] = relationship("Presentation", back_populates="finding_entries")


class Blendshape(Base):
    __tablename__ = "blendshapes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    training_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trainings.id", ondelete="CASCADE"),
        nullable=False
    )

    timestamp: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Seconds since training start"
    )

    scores: Mapped[dict] = mapped_column(
        JSONB, nullable=False, comment="Map of blendshape scores, e.g. {'jawOpen': 0.42}"
    )

    training: Mapped["Training"] = relationship(
        "Training", back_populates="blendshapes", lazy="selectin"
    )


class TrainingResult(Base):
    __tablename__ = "training_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    training_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trainings.id", ondelete="CASCADE"),
        nullable=False
    )

    eye_tracking_scores: Mapped[dict] = mapped_column(
        JSONB, nullable=True, comment="Raw eye tracking metrics"
    )

    eye_tracking_total_score: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Aggregated score from eye tracking"
    )

    audio_scores: Mapped[dict] = mapped_column(
        JSONB, nullable=True, comment="Detailed metrics from audio analysis"
    )

    audio_total_score: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Aggregated score from audio analysis"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    training: Mapped["Training"] = relationship(
        "Training", back_populates="training_results", lazy="selectin"
    )
