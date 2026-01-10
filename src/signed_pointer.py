"""
Crovia Signed Pointer
---------------------

Cryptographically signed evidence pointers for Global Registry.
These pointers prove that an observation was made at a specific time
and can be verified independently.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SignedPointer:
    """
    A cryptographically signed pointer to an evidence observation.
    
    This is the atomic unit that gets registered in the Global Registry.
    """
    pointer_id: str
    schema: str
    version: str
    
    # Observation
    observed_at: str
    repository: str
    commit_sha: Optional[str]
    branch: Optional[str]
    
    # Verdict
    status: str
    reason: str
    evidence_found: list
    critical_omissions: int
    
    # Cryptographic
    observation_hash: str
    signature: Optional[str]
    signer_key_id: Optional[str]
    
    # Registry
    registry_eligible: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class SignedPointerGenerator:
    """
    Generates signed pointers for Crovia Global Registry.
    
    Pointers are cryptographically signed observations that can be:
    - Verified offline
    - Registered globally
    - Used as proof of observation
    """
    
    def __init__(self, signer=None):
        """
        Initialize generator.
        
        Args:
            signer: Optional CroviaSigner for cryptographic signatures
        """
        self._signer = signer
    
    def generate(
        self,
        status: str,
        reason: str,
        evidence_found: list,
        critical_omissions: int = 0,
        repository: Optional[str] = None,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> SignedPointer:
        """
        Generate a signed pointer for the current observation.
        
        Args:
            status: GREEN or RED
            reason: evidence_recorded, evidence_absent, etc.
            evidence_found: List of evidence artifacts found
            critical_omissions: Number of critical gaps
            repository: Repository name (from env if not provided)
            commit_sha: Commit SHA (from env if not provided)
            branch: Branch name (from env if not provided)
        
        Returns:
            SignedPointer ready for registry
        """
        now = datetime.now(timezone.utc)
        
        # Get from environment if not provided
        repository = repository or os.getenv("GITHUB_REPOSITORY", "unknown/unknown")
        commit_sha = commit_sha or os.getenv("GITHUB_SHA", None)
        branch = branch or os.getenv("GITHUB_REF_NAME", None)
        
        # Build observation payload
        observation = {
            "timestamp": now.isoformat(),
            "repository": repository,
            "commit": commit_sha,
            "status": status,
            "reason": reason,
            "evidence": sorted(evidence_found),
            "omissions": critical_omissions,
        }
        
        # Hash the observation
        observation_bytes = json.dumps(observation, sort_keys=True, separators=(",", ":")).encode()
        observation_hash = hashlib.sha256(observation_bytes).hexdigest()
        
        # Generate pointer ID
        pointer_id = f"PTR-{now.strftime('%Y%m%d')}-{observation_hash[:12].upper()}"
        
        # Sign if signer available
        signature = None
        signer_key_id = None
        
        if self._signer:
            sig = self._signer.sign(observation_bytes)
            signature = sig.signature
            signer_key_id = sig.key_id
        
        return SignedPointer(
            pointer_id=pointer_id,
            schema="crovia.pointer.v1",
            version="1.0.0",
            observed_at=now.isoformat(),
            repository=repository,
            commit_sha=commit_sha,
            branch=branch,
            status=status,
            reason=reason,
            evidence_found=sorted(evidence_found),
            critical_omissions=critical_omissions,
            observation_hash=observation_hash,
            signature=signature,
            signer_key_id=signer_key_id,
            registry_eligible=signature is not None,
        )
    
    def save(self, pointer: SignedPointer, output_dir: str = ".crovia") -> str:
        """Save pointer to file."""
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{pointer.pointer_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(pointer.to_json())
        return path
    
    @staticmethod
    def verify(pointer: SignedPointer, public_key: str) -> bool:
        """
        Verify a signed pointer.
        
        Args:
            pointer: The pointer to verify
            public_key: Public key hex string
        
        Returns:
            True if signature is valid
        """
        if not pointer.signature:
            return False
        
        # Rebuild observation
        observation = {
            "timestamp": pointer.observed_at,
            "repository": pointer.repository,
            "commit": pointer.commit_sha,
            "status": pointer.status,
            "reason": pointer.reason,
            "evidence": pointer.evidence_found,
            "omissions": pointer.critical_omissions,
        }
        
        observation_bytes = json.dumps(observation, sort_keys=True, separators=(",", ":")).encode()
        
        # Verify hash
        computed_hash = hashlib.sha256(observation_bytes).hexdigest()
        if computed_hash != pointer.observation_hash:
            return False
        
        # Verify signature (requires CroviaSigner)
        try:
            from croviapro.crypto.signer import CroviaSigner, CroviaSignature
            
            sig = CroviaSignature(
                signature=pointer.signature,
                key_id=pointer.signer_key_id or "",
                algorithm="ed25519",
                signed_at=pointer.observed_at,
                message_hash=computed_hash,
            )
            
            return CroviaSigner.verify(sig, observation_bytes, public_key)
        except ImportError:
            # Can't verify without crypto module
            return False


def generate_pointer(
    status: str,
    reason: str,
    evidence_found: list,
    output_dir: str = ".crovia",
) -> SignedPointer:
    """Convenience function for pointer generation."""
    generator = SignedPointerGenerator()
    pointer = generator.generate(status, reason, evidence_found)
    generator.save(pointer, output_dir)
    return pointer


if __name__ == "__main__":
    # Test pointer generation
    gen = SignedPointerGenerator()
    
    print("Generating unsigned pointer...")
    ptr = gen.generate(
        status="GREEN",
        reason="evidence_recorded",
        evidence_found=["EVIDENCE.json", "trust_bundle.v1.json"],
        repository="test/repo",
        commit_sha="abc123",
    )
    
    print(f"Pointer ID: {ptr.pointer_id}")
    print(f"Hash: {ptr.observation_hash}")
    print(f"Registry eligible: {ptr.registry_eligible}")
    print(f"\n{ptr.to_json()}")
