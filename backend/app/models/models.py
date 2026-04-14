"""
SQLAlchemy ORM Models
----------------------
Defines all database tables used by the application:
  • requirements  — raw requirement text
  • test_cases    — generated test cases linked to requirements
  • defect_data   — module-level metrics for ML training / prediction
  • predictions   — stored prediction results
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.database import Base


class Requirement(Base):
    """Stores raw requirement text submitted by users."""

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    design_text = Column(Text, nullable=True)
    folder_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One requirement → many test cases
    test_cases = relationship("TestCase", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Requirement(id={self.id}, text={self.text[:40]}...)>"


class TestCase(Base):
    """Individual test case generated from a requirement."""

    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    module_name = Column(String(255), nullable=False)
    scenario = Column(Text, nullable=False)
    test_type = Column(String(100), nullable=False)  # positive / negative / boundary / edge / security
    test_level = Column(String(50), nullable=True, default="Unit")  # Unit / Integration / System / UAT
    expected_result = Column(Text, nullable=False)
    precondition = Column(Text, nullable=True, default="")
    test_steps = Column(Text, nullable=True, default="")  # Stored as JSON string
    priority = Column(String(10), nullable=False, default="P3")  # P1 / P2 / P3
    created_at = Column(DateTime, server_default=func.now())  # auto-set on insert
    complexity_score = Column(Integer, nullable=True, default=1)  # 1–5
    duplicate_score = Column(Float, nullable=True, default=0.0)  # 0.0–1.0
    coverage_tag = Column(String(100), nullable=True, default="")  # e.g. auth, validation, ui

    requirement = relationship("Requirement", back_populates="test_cases")

    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, module={self.module_name}, type={self.test_type})>"


class DefectData(Base):
    """Module-level software metrics used to train / feed the defect prediction model."""

    __tablename__ = "defect_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_name = Column(String(255), nullable=False)
    lines_of_code = Column(Integer, nullable=False)
    complexity_score = Column(Float, nullable=False)
    past_defects = Column(Integer, nullable=False)
    code_churn = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<DefectData(id={self.id}, module={self.module_name})>"


class Prediction(Base):
    """Stored defect-prediction results."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_name = Column(String(255), nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # Low / Medium / High
    defect_category = Column(String(50), nullable=True, default="Function Level")  # UI / API / Integration / Function / System / Non-functional
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Prediction(id={self.id}, module={self.module_name}, risk={self.risk_level})>"


class DesignDocument(Base):
    """Stores uploaded design documentation metadata linked to a requirement."""

    __tablename__ = "design_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)
    file_names = Column(Text, nullable=True)         # JSON list of uploaded file names
    file_paths = Column(Text, nullable=True)         # JSON list of stored file paths
    design_urls = Column(Text, nullable=True)        # JSON list of design URLs
    analysis_result = Column(Text, nullable=True)    # JSON of design analysis output
    folder_path = Column(String(500), nullable=True) # Path to design subfolder
    # Enterprise metadata
    ui_schema = Column(Text, nullable=True)          # JSON of unified UI schema
    detected_flows = Column(Text, nullable=True)     # JSON of detected flows
    coverage_percentage = Column(Float, nullable=True)  # Enterprise coverage %
    total_components = Column(Integer, nullable=True)   # Total UI components detected
    total_pages = Column(Integer, nullable=True)        # Total pages analyzed
    source_type = Column(String(50), nullable=True)     # "url" / "document" / "image" / "text"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    requirement = relationship("Requirement", backref="design_documents")

    def __repr__(self) -> str:
        return f"<DesignDocument(id={self.id}, req_id={self.requirement_id})>"
