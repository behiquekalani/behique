"""
Image Handler — Validates and recommends improvements for eBay listing photos.

V1: Read-only validation using stdlib only (no Pillow dependency).
V2: Resize, optimize, and upload via eBay Picture Services.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


# eBay image requirements
EBAY_MIN_DIMENSION = 500      # Minimum 500px on longest side
EBAY_MAX_FILE_SIZE_MB = 12    # Max file size
EBAY_SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".avif", ".heic"}


@dataclass
class ImageValidation:
    path: str
    valid: bool
    format_ok: bool
    size_ok: bool
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    file_size_kb: float = 0
    file_format: str = ""


class ImageHandler:
    """Validates images against eBay requirements."""

    def validate(self, image_path: str) -> ImageValidation:
        """
        Check if an image meets eBay's requirements.

        Checks: file exists, format supported, file size within limits.
        Note: V1 doesn't check pixel dimensions (would need Pillow).
        """
        path = Path(image_path)
        issues = []
        recommendations = []

        # Check existence
        if not path.exists():
            return ImageValidation(
                path=image_path, valid=False, format_ok=False, size_ok=False,
                issues=["File not found"],
            )

        # Check format
        ext = path.suffix.lower()
        format_ok = ext in EBAY_SUPPORTED_FORMATS
        if not format_ok:
            issues.append(f"Unsupported format: {ext}. Use JPG, PNG, or WebP.")

        # Check file size
        file_size_bytes = path.stat().st_size
        file_size_kb = file_size_bytes / 1024
        file_size_mb = file_size_kb / 1024
        size_ok = file_size_mb <= EBAY_MAX_FILE_SIZE_MB
        if not size_ok:
            issues.append(f"File too large: {file_size_mb:.1f}MB (max {EBAY_MAX_FILE_SIZE_MB}MB)")

        # Recommendations
        if ext not in (".jpg", ".jpeg"):
            recommendations.append("JPG is preferred for eBay — smaller file size, fast loading")
        if file_size_mb > 5:
            recommendations.append("Consider compressing — large images slow down listing page")
        if file_size_kb < 50:
            recommendations.append("Image seems very small — may be low resolution. eBay needs min 500x500px")

        # General photo tips
        recommendations.extend([
            "First photo is the thumbnail — make it the best angle",
            "Use natural lighting or white background",
            "Show all sides and any defects for used items",
            "eBay allows up to 24 photos — use as many as relevant",
        ])

        valid = format_ok and size_ok and len(issues) == 0

        return ImageValidation(
            path=image_path,
            valid=valid,
            format_ok=format_ok,
            size_ok=size_ok,
            issues=issues,
            recommendations=recommendations,
            file_size_kb=round(file_size_kb, 1),
            file_format=ext,
        )

    def validate_batch(self, image_paths: list[str]) -> list[ImageValidation]:
        """Validate multiple images at once."""
        return [self.validate(p) for p in image_paths]

    def summary(self, validations: list[ImageValidation]) -> str:
        """Generate a human-readable summary of image validations."""
        lines = [f"📸 Image Validation ({len(validations)} files)\n"]
        for v in validations:
            status = "✅" if v.valid else "❌"
            lines.append(f"  {status} {os.path.basename(v.path)} ({v.file_size_kb:.0f}KB, {v.file_format})")
            for issue in v.issues:
                lines.append(f"     ⚠️  {issue}")
        return "\n".join(lines)
