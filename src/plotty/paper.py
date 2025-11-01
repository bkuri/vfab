from __future__ import annotations
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class PaperSize(Enum):
    """Standard paper sizes with dimensions in millimeters."""

    # ISO A Series
    A0 = ("A0", 841, 1189)
    A1 = ("A1", 594, 841)
    A2 = ("A2", 420, 594)
    A3 = ("A3", 297, 420)
    A4 = ("A4", 210, 297)
    A5 = ("A5", 148, 210)
    A6 = ("A6", 105, 148)

    # US Standard
    LETTER = ("Letter", 215.9, 279.4)
    LEGAL = ("Legal", 215.9, 355.6)
    TABLOID = ("Tabloid", 279.4, 431.8)

    # Special Sizes
    POSTCARD = ("Postcard", 100, 148)
    INDEX_CARD = ("Index Card", 76, 127)
    BUSINESS_CARD = ("Business Card", 85.6, 53.98)

    @classmethod
    def get_all_sizes(cls) -> List[str]:
        """Get all available paper size names."""
        return [size.value[0] for size in cls]

    @classmethod
    def get_dimensions(cls, name: str) -> Optional[tuple[float, float]]:
        """Get dimensions for a paper size name."""
        for size in cls:
            if size.value[0] == name:
                return float(size.value[1]), float(size.value[2])
        return None

    @classmethod
    def is_valid_size(cls, name: str) -> bool:
        """Check if a paper size name is valid."""
        return name in cls.get_all_sizes()


@dataclass
class PaperConfig:
    """Paper configuration with dimensions and settings."""

    name: str
    width_mm: float
    height_mm: float
    margin_mm: float = 10.0
    orientation: str = "portrait"  # portrait, landscape
    description: Optional[str] = None

    def __post_init__(self):
        """Validate paper configuration."""
        if self.width_mm <= 0 or self.height_mm <= 0:
            raise ValueError("Paper dimensions must be positive")
        if self.margin_mm < 0:
            raise ValueError("Margin cannot be negative")
        if self.orientation not in ["portrait", "landscape"]:
            raise ValueError("Orientation must be 'portrait' or 'landscape'")

    @property
    def effective_width(self) -> float:
        """Get effective width after margin."""
        return self.width_mm - (2 * self.margin_mm)

    @property
    def effective_height(self) -> float:
        """Get effective height after margin."""
        return self.height_mm - (2 * self.margin_mm)

    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio (width/height)."""
        return self.width_mm / self.height_mm

    def to_landscape(self) -> "PaperConfig":
        """Return a landscape version of this paper."""
        if self.orientation == "landscape":
            return self

        return PaperConfig(
            name=f"{self.name} (landscape)",
            width_mm=self.height_mm,
            height_mm=self.width_mm,
            margin_mm=self.margin_mm,
            orientation="landscape",
            description=self.description,
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage."""
        return {
            "name": self.name,
            "width_mm": self.width_mm,
            "height_mm": self.height_mm,
            "margin_mm": self.margin_mm,
            "orientation": self.orientation,
            "description": self.description,
        }

    @classmethod
    def from_size(
        cls, size_name: str, margin_mm: float = 10.0, orientation: str = "portrait"
    ) -> "PaperConfig":
        """Create PaperConfig from standard size."""
        if not PaperSize.is_valid_size(size_name):
            raise ValueError(f"Unknown paper size: {size_name}")

        width_mm, height_mm = PaperSize.get_dimensions(size_name)

        return cls(
            name=size_name,
            width_mm=width_mm,
            height_mm=height_mm,
            margin_mm=margin_mm,
            orientation=orientation,
            description=f"Standard {size_name} paper",
        )

    @classmethod
    def custom(
        cls,
        name: str,
        width_mm: float,
        height_mm: float,
        margin_mm: float = 10.0,
        orientation: str = "portrait",
        description: Optional[str] = None,
    ) -> "PaperConfig":
        """Create custom paper configuration."""
        return cls(
            name=name,
            width_mm=width_mm,
            height_mm=height_mm,
            margin_mm=margin_mm,
            orientation=orientation,
            description=description or f"Custom {width_mm}x{height_mm}mm paper",
        )


class PaperManager:
    """Manages paper configurations and database operations."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create_standard_papers(self) -> List[PaperConfig]:
        """Create standard paper configurations."""
        standard_papers = []

        # ISO A Series
        for size_name in ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]:
            standard_papers.append(PaperConfig.from_size(size_name))

        # US Standard
        for size_name in ["Letter", "Legal", "Tabloid"]:
            standard_papers.append(PaperConfig.from_size(size_name))

        # Special Sizes
        for size_name in ["Postcard", "Index Card", "Business Card"]:
            standard_papers.append(PaperConfig.from_size(size_name))

        return standard_papers

    def get_paper_by_name(self, name: str) -> Optional[PaperConfig]:
        """Get paper configuration by name from database."""
        try:
            with self.session_factory() as session:
                from .models import Paper

                paper = session.query(Paper).filter(Paper.name == name).first()
                if paper:
                    return PaperConfig(
                        name=paper.name,
                        width_mm=paper.width_mm,
                        height_mm=paper.height_mm,
                        margin_mm=paper.margin_mm,
                        orientation=paper.orientation,
                        description="Paper from database",
                    )
        except Exception:
            pass
        return None

    def list_papers(self) -> List[PaperConfig]:
        """List all available papers."""
        papers = []

        # Add standard papers
        papers.extend(self.create_standard_papers())

        # Add custom papers from database
        try:
            with self.session_factory() as session:
                from .models import Paper

                db_papers = session.query(Paper).all()
                for paper in db_papers:
                    papers.append(
                        PaperConfig(
                            name=paper.name,
                            width_mm=paper.width_mm,
                            height_mm=paper.height_mm,
                            margin_mm=paper.margin_mm,
                            orientation=paper.orientation,
                            description="Custom paper from database",
                        )
                    )
        except Exception:
            pass

        return papers

    def add_custom_paper(self, paper: PaperConfig) -> bool:
        """Add custom paper to database."""
        try:
            with self.session_factory() as session:
                from .models import Paper

                # Check if paper already exists
                existing = session.query(Paper).filter(Paper.name == paper.name).first()
                if existing:
                    return False

                # Add new paper
                db_paper = Paper(
                    name=paper.name,
                    width_mm=paper.width_mm,
                    height_mm=paper.height_mm,
                    margin_mm=paper.margin_mm,
                    orientation=paper.orientation,
                )
                session.add(db_paper)
                session.commit()
                return True
        except Exception:
            return False

    def remove_paper(self, name: str) -> bool:
        """Remove paper from database (only custom papers)."""
        try:
            with self.session_factory() as session:
                from .models import Paper

                paper = session.query(Paper).filter(Paper.name == name).first()
                if paper:
                    session.delete(paper)
                    session.commit()
                    return True
        except Exception:
            pass
        return False

    def get_suitable_papers(
        self,
        max_width_mm: Optional[float] = None,
        max_height_mm: Optional[float] = None,
    ) -> List[PaperConfig]:
        """Get papers that fit within given dimensions."""
        suitable_papers = []

        for paper in self.list_papers():
            width_ok = max_width_mm is None or paper.width_mm <= max_width_mm
            height_ok = max_height_mm is None or paper.height_mm <= max_height_mm

            if width_ok and height_ok:
                suitable_papers.append(paper)

        return suitable_papers


def get_paper_presets() -> Dict[str, Dict]:
    """Get paper presets for vpype configuration."""
    presets = {}

    for size in PaperSize:
        name, width_mm, height_mm = size.value
        presets[name.lower()] = {
            "width_mm": width_mm,
            "height_mm": height_mm,
            "vpype_pagesize": (
                name.upper()
                if name.upper() in ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
                else "Letter"
            ),
            "description": f"Standard {name} paper ({width_mm}x{height_mm}mm)",
        }

    return presets
