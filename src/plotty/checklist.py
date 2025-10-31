"""
Checklist system for ploTTY pre-flight validation.

This module provides checklist management for job preparation
as specified in the PRD user stories.
"""

from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChecklistItem:
    """Represents a single checklist item."""

    def __init__(self, name: str, description: str, required: bool = True):
        """Initialize checklist item.

        Args:
            name: Item identifier
            description: Human-readable description
            required: Whether this item is required
        """
        self.name = name
        self.description = description
        self.required = required
        self.completed = False
        self.completed_at = None
        self.notes = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ChecklistItem:
        """Create from dictionary."""
        item = cls(data["name"], data["description"], data.get("required", True))
        item.completed = data.get("completed", False)
        item.notes = data.get("notes", "")

        if data.get("completed_at"):
            item.completed_at = datetime.fromisoformat(data["completed_at"])

        return item

    def complete(self, notes: str = "") -> None:
        """Mark item as completed."""
        self.completed = True
        self.completed_at = datetime.utcnow()
        self.notes = notes

    def uncomplete(self) -> None:
        """Mark item as not completed."""
        self.completed = False
        self.completed_at = None
        self.notes = ""


class Checklist:
    """Manages checklist for a job."""

    # Default checklist items as per PRD
    DEFAULT_ITEMS = [
        ChecklistItem("paper_size_set", "Paper size/orientation selected", True),
        ChecklistItem(
            "paper_one_per_session", "One paper per session rule followed", True
        ),
        ChecklistItem("paper_taped", "Paper taped down and square", True),
        ChecklistItem("origin_set", "Plot origin set", True),
        ChecklistItem("pen_loaded", "Pen loaded and ink test passed", True),
        ChecklistItem("pen_one_per_layer", "One pen per layer rule followed", True),
        ChecklistItem("surface_clear", "Surface clear and adequate clearance", True),
        ChecklistItem("camera_ok", "Camera working (soft-fail allowed)", False),
        ChecklistItem("ink_swatch", "Ink swatch completed (optional)", False),
    ]

    def __init__(self, job_id: str, job_dir: Path):
        """Initialize checklist for a job.

        Args:
            job_id: Job identifier
            job_dir: Path to job directory
        """
        self.job_id = job_id
        self.job_dir = job_dir
        self.checklist_file = job_dir / "checklist.json"
        self.items: Dict[str, ChecklistItem] = {}

        self._load_checklist()

    def _load_checklist(self) -> None:
        """Load existing checklist or create default."""
        if self.checklist_file.exists():
            try:
                with open(self.checklist_file, "r") as f:
                    data = json.load(f)

                for item_data in data.get("items", []):
                    item = ChecklistItem.from_dict(item_data)
                    self.items[item.name] = item

            except Exception as e:
                logger.error(f"Failed to load checklist: {e}")
                self._create_default()
        else:
            self._create_default()

    def _create_default(self) -> None:
        """Create default checklist."""
        self.items = {}
        for item in self.DEFAULT_ITEMS:
            # Create a copy for this job
            job_item = ChecklistItem(item.name, item.description, item.required)
            self.items[item.name] = job_item

        self.save()

    def save(self) -> None:
        """Save checklist to file."""
        self.job_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "job_id": self.job_id,
            "updated_at": datetime.utcnow().isoformat(),
            "items": [item.to_dict() for item in self.items.values()],
        }

        with open(self.checklist_file, "w") as f:
            json.dump(data, f, indent=2)

    def complete_item(self, name: str, notes: str = "") -> bool:
        """Complete a checklist item.

        Args:
            name: Item name to complete
            notes: Optional notes

        Returns:
            True if item completed, False if not found
        """
        if name not in self.items:
            return False

        self.items[name].complete(notes)
        self.save()
        return True

    def uncomplete_item(self, name: str) -> bool:
        """Uncomplete a checklist item.

        Args:
            name: Item name to uncomplete

        Returns:
            True if item uncompleted, False if not found
        """
        if name not in self.items:
            return False

        self.items[name].uncomplete()
        self.save()
        return True

    def get_item(self, name: str) -> Optional[ChecklistItem]:
        """Get a specific checklist item.

        Args:
            name: Item name

        Returns:
            ChecklistItem or None if not found
        """
        return self.items.get(name)

    def get_all_items(self) -> List[ChecklistItem]:
        """Get all checklist items.

        Returns:
            List of all items
        """
        return list(self.items.values())

    def get_required_items(self) -> List[ChecklistItem]:
        """Get required checklist items.

        Returns:
            List of required items
        """
        return [item for item in self.items.values() if item.required]

    def get_completed_items(self) -> List[ChecklistItem]:
        """Get completed checklist items.

        Returns:
            List of completed items
        """
        return [item for item in self.items.values() if item.completed]

    def get_incomplete_items(self) -> List[ChecklistItem]:
        """Get incomplete checklist items.

        Returns:
            List of incomplete items
        """
        return [item for item in self.items.values() if not item.completed]

    def is_complete(self) -> bool:
        """Check if all required items are completed.

        Returns:
            True if all required items completed
        """
        required_items = self.get_required_items()
        return all(item.completed for item in required_items)

    def get_progress(self) -> Dict[str, Any]:
        """Get checklist progress summary.

        Returns:
            Progress dictionary
        """
        required_items = self.get_required_items()
        completed_required = [item for item in required_items if item.completed]

        all_items = self.get_all_items()
        completed_all = [item for item in all_items if item.completed]

        return {
            "required_total": len(required_items),
            "required_completed": len(completed_required),
            "total_items": len(all_items),
            "total_completed": len(completed_all),
            "is_complete": self.is_complete(),
            "progress_percent": (len(completed_required) / len(required_items)) * 100
            if required_items
            else 100,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert entire checklist to dictionary.

        Returns:
            Checklist data
        """
        return {
            "job_id": self.job_id,
            "progress": self.get_progress(),
            "items": [item.to_dict() for item in self.items.values()],
        }


def create_checklist(job_id: str, job_dir: Path) -> Checklist:
    """Factory function to create checklist.

    Args:
        job_id: Job identifier
        job_dir: Path to job directory

    Returns:
        Checklist instance
    """
    return Checklist(job_id, job_dir)
