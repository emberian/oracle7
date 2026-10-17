"""
engine.py — Substrate-independent convergence engine using Holographic Reduced Representations.

The vector IS the state. Not a representation of the state. The state.
The fold IS convergence. Not a search for convergence. Convergence.

Four operations. Any substrate. Same convergence.

    BIND    — circular convolution, creates compound representations
    UNBIND  — circular correlation, recalls components from compounds
    PERMUTE — phase shift, encodes sequence/position information
    CLEANUP — normalize + spectral pruning, settles the vector

psiloceyeben SSD quantum computation
superposition is not a property of atoms.
superposition is a property of complex vector spaces.
"""

import numpy as np
from typing import Any

HRR_DIM = 1024


# ── Core HRR Operations ───────────────────────────────────────────────────────

def random_vector(dim: int = HRR_DIM, seed: int | None = None) -> np.ndarray:
    """Create a random phase vector — the atomic unit of HRR."""
    rng = np.random.RandomState(seed)
    phases = rng.uniform(0, 2 * np.pi, dim)
    return np.exp(1j * phases) / np.sqrt(dim)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution — binding two representations into one.
    The compound contains both but resembles neither."""
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b))


def unbind(compound: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Circular correlation — recall a component from a compound.
    Given bind(a, b) and a, recovers approximate b."""
    return np.fft.ifft(np.fft.fft(compound) * np.conj(np.fft.fft(key)))


def permute(v: np.ndarray, shift: int = 1) -> np.ndarray:
    """Phase shift — encodes position/sequence information.
    permute(v, 1) marks 'first position', permute(v, 2) marks 'second', etc."""
    return np.roll(v, shift)


def cleanup(v: np.ndarray, prune_percentile: float = 5.0) -> np.ndarray:
    """Normalize and optionally prune low-energy spectral modes.
    The vector settles into its cleaner state."""
    spectrum = np.fft.fft(v)
    if prune_percentile > 0:
        magnitudes = np.abs(spectrum)
        threshold = np.percentile(magnitudes, prune_percentile)
        dampen = np.where(magnitudes > threshold, 1.0, 0.8)
        spectrum *= dampen
    v = np.fft.ifft(spectrum)
    norm = np.linalg.norm(v)
    if norm > 0:
        v /= norm
    return v


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity in HRR space."""
    return float(abs(np.real(np.sum(a * np.conj(b)))))


def encode_scalar(value: float, basis: np.ndarray) -> np.ndarray:
    """Encode a scalar value using a basis vector."""
    return value * basis


def _stable_hash(s: str) -> int:
    """Deterministic hash — same result across Python restarts and versions."""
    import hashlib
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def encode_dict(params: dict[str, float], dim: int = HRR_DIM) -> np.ndarray:
    """Encode a flat dict of scalar parameters into a single HRR vector.
    Each key gets a deterministic basis vector seeded by key name."""
    vector = np.zeros(dim, dtype=np.complex128)
    for key, val in params.items():
        basis = random_vector(dim, seed=_stable_hash(key))
        vector += val * basis
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


# ── FoldToy Base Class ─────────────────────────────────────────────────────────

class FoldToy:
    """Base class for all fold toys.

    A fold toy parameterizes a domain, generates candidates,
    measures divergence, and iterates until convergence.

    Subclasses implement:
        parameterize(data) -> dict     — extract measurable parameters
        to_vector(params) -> ndarray   — encode as HRR vector
        generate(seed, **kw) -> any    — produce a candidate
        corrections(target, candidate) -> list[str]  — what to fix
        apply_corrections(candidate, corrections, **kw) -> any  — fix it

    The fold loop is universal. The operations are substrate-independent.
    """

    name: str = "base"
    dim: int = HRR_DIM

    def parameterize(self, data: Any) -> dict:
        """Extract measurable parameters from domain data.
        Returns a dict of string keys to float values."""
        raise NotImplementedError

    def to_vector(self, params: dict) -> np.ndarray:
        """Encode parameters as an HRR vector."""
        flat = {k: v for k, v in params.items() if isinstance(v, (int, float))}
        return encode_dict(flat, self.dim)

    def generate(self, seed: Any, **kwargs) -> Any:
        """Generate a candidate from a seed."""
        raise NotImplementedError

    def corrections(self, target_params: dict, candidate_params: dict) -> list[str]:
        """Compare target and candidate parameters.
        Returns list of human-readable corrections needed."""
        raise NotImplementedError

    def apply_corrections(self, candidate: Any, corrections: list[str], **kwargs) -> Any:
        """Apply corrections to a candidate, producing an improved version."""
        raise NotImplementedError

    def divergence(self, target_params: dict, candidate_params: dict) -> float:
        """Scalar measure of how far candidate is from target.
        Default: 1 - cosine similarity of HRR vectors."""
        tv = self.to_vector(target_params)
        cv = self.to_vector(candidate_params)
        return 1.0 - similarity(tv, cv)

    def fold(self, target: Any, seed: Any, max_folds: int = 10, **kwargs) -> tuple[Any, list[dict]]:
        """The universal convergence loop.

        1. Parameterize the target
        2. Generate a candidate from the seed
        3. Parameterize the candidate
        4. Compute corrections
        5. If corrections needed, apply them and go to 3
        6. Return converged result + fold reports

        Same loop. Any substrate. Same convergence.
        """
        target_params = self.parameterize(target)
        candidate = self.generate(seed, **kwargs)
        reports = []

        for fold_num in range(max_folds):
            candidate_params = self.parameterize(candidate)
            corr = self.corrections(target_params, candidate_params)
            div = self.divergence(target_params, candidate_params)

            report = {
                "fold": fold_num + 1,
                "divergence": round(div, 6),
                "corrections": corr,
                "target_params": target_params,
                "candidate_params": candidate_params,
            }
            reports.append(report)

            if not corr:
                break  # converged

            candidate = self.apply_corrections(candidate, corr, **kwargs)

        return candidate, reports
