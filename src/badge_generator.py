"""
Crovia Badge Generator
----------------------

Generates visual badges for repository evidence status.
Badges can be embedded in README files for instant visibility.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional


BADGE_TEMPLATE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="{width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h{label_width}v20H0z"/>
    <path fill="{color}" d="M{label_width} 0h{value_width}v20H{label_width}z"/>
    <path fill="url(#b)" d="M0 0h{width}v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_x}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_x}" y="14">{label}</text>
    <text x="{value_x}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{value_x}" y="14">{value}</text>
  </g>
</svg>'''


class CroviaBadgeGenerator:
    """
    Generates Crovia evidence badges for repositories.
    
    Badges indicate:
    - GREEN: Evidence recorded
    - RED: No evidence / compromised
    - PENDING: Check in progress
    """
    
    COLORS = {
        "GREEN": "#4c1",      # Bright green
        "RED": "#e05d44",     # Red
        "PENDING": "#9f9f9f", # Gray
        "CERTIFIED": "#007ec6", # Blue (for CFIC-backed)
    }
    
    def __init__(self, output_dir: str = ".crovia"):
        self.output_dir = output_dir
    
    def generate(
        self,
        status: str,
        reason: str,
        repo_name: Optional[str] = None,
        certified: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate badge files and metadata.
        
        Args:
            status: GREEN, RED, or PENDING
            reason: evidence_recorded, evidence_absent, etc.
            repo_name: Optional repository name for badge
            certified: If True, uses CERTIFIED color (CFIC-backed)
        
        Returns:
            Dict with badge paths and metadata
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Determine badge appearance
        if certified:
            color = self.COLORS["CERTIFIED"]
            value = "certified"
        elif status == "GREEN":
            color = self.COLORS["GREEN"]
            value = "evidence"
        elif status == "RED":
            color = self.COLORS["RED"]
            value = "no evidence"
        else:
            color = self.COLORS["PENDING"]
            value = "pending"
        
        label = "crovia"
        
        # Generate SVG
        svg_content = self._generate_svg(label, value, color)
        svg_path = os.path.join(self.output_dir, "badge.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        # Generate badge metadata
        now = datetime.now(timezone.utc)
        metadata = {
            "schema": "crovia.badge.v1",
            "generated_at": now.isoformat(),
            "status": status,
            "reason": reason,
            "certified": certified,
            "badge_svg": svg_path,
            "badge_url": f"https://img.shields.io/badge/crovia-{value.replace(' ', '_')}-{color[1:]}.svg",
            "embed_markdown": f"[![Crovia Evidence]({svg_path})](https://crovia.trust)",
            "badge_hash": hashlib.sha256(svg_content.encode()).hexdigest()[:16],
        }
        
        meta_path = os.path.join(self.output_dir, "badge_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def _generate_svg(self, label: str, value: str, color: str) -> str:
        """Generate SVG badge content."""
        label_width = len(label) * 7 + 10
        value_width = len(value) * 7 + 10
        width = label_width + value_width
        
        return BADGE_TEMPLATE_SVG.format(
            width=width,
            label_width=label_width,
            value_width=value_width,
            color=color,
            label=label,
            value=value,
            label_x=label_width // 2,
            value_x=label_width + value_width // 2,
        )
    
    def generate_shields_url(self, status: str, certified: bool = False) -> str:
        """Generate shields.io compatible URL."""
        if certified:
            return "https://img.shields.io/badge/crovia-certified-blue.svg"
        elif status == "GREEN":
            return "https://img.shields.io/badge/crovia-evidence-brightgreen.svg"
        else:
            return "https://img.shields.io/badge/crovia-no_evidence-red.svg"


def generate_badge(status: str, reason: str, output_dir: str = ".crovia") -> Dict[str, Any]:
    """Convenience function for badge generation."""
    generator = CroviaBadgeGenerator(output_dir)
    return generator.generate(status, reason)


if __name__ == "__main__":
    # Test badge generation
    gen = CroviaBadgeGenerator(".crovia")
    
    print("Generating GREEN badge...")
    meta = gen.generate("GREEN", "evidence_recorded")
    print(f"  SVG: {meta['badge_svg']}")
    print(f"  Markdown: {meta['embed_markdown']}")
    
    print("\nGenerating RED badge...")
    meta = gen.generate("RED", "evidence_absent")
    print(f"  SVG: {meta['badge_svg']}")
    
    print("\nGenerating CERTIFIED badge...")
    meta = gen.generate("GREEN", "cfic_verified", certified=True)
    print(f"  SVG: {meta['badge_svg']}")
    print(f"  URL: {meta['badge_url']}")
