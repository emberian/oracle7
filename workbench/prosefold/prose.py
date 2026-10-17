"""
prose.py — Fold toy for prose voice convergence.

Parameterizes writing style into measurable structural features,
encodes them as HRR vectors, and iterates until a generated text
converges on the target voice's parameters.

This is the original fold toy — the one that proved substrate independence.
If you can fold proteins and fold prose with the same four operations,
superposition is not a property of atoms.
"""

import re
import numpy as np
from typing import Any

from .engine import FoldToy, encode_dict, HRR_DIM


class ProseFoldToy(FoldToy):
    """Fold toy for prose voice convergence.

    Target: a corpus of writing (str) with a measurable voice signature.
    Candidate: a generated text (str) that should converge on that signature.

    Parameters extracted:
        comma_density       — clause-chaining frequency (commas per word)
        em_dash_density     — em dash frequency (should be ~0 for natural voice)
        sent_len_std        — sentence length variation (high = dynamic rhythm)
        max_sent_len        — longest sentence (tests for clause-chain rivers)
        snap_ratio          — short sentences (<=8 words) per long sentence (>=50)
        connective_density  — signature connective phrases per 1000 words
        i_ratio             — first-person pronoun share of all person pronouns
        slop_count          — count of AI slop words (should be 0)
        profanity_per_1k    — profanity per 1000 words

    The fold loop does NOT call an LLM. It parameterizes, compares, and
    returns corrections. The caller decides how to apply them (LLM rewrite,
    manual edit, rule-based transform, etc).
    """

    name = "prose"

    # Default target ranges — override with set_target_ranges()
    target_ranges: dict[str, tuple[float, float]] = {
        "comma_density": (0.045, 0.065),
        "em_dash_density": (0.0, 0.001),
        "sent_len_std": (30.0, 50.0),
        "max_sent_len": (150, 300),
        "snap_ratio": (0.35, 0.60),
        "connective_density_per_1k": (5.0, 10.0),
        "slop_count": (0, 0),
        "i_ratio": (0.25, 0.45),
        "profanity_per_1k": (0.0, 2.0),
    }

    SLOP_WORDS = [
        "delve", "tapestry", "landscape", "robust", "pivotal", "nuanced",
        "multifaceted", "groundbreaking", "leverage", "facilitate", "utilize",
        "harness", "streamline", "innovative", "seamless", "synergy",
    ]

    CONNECTIVE_PATTERNS = [
        ("if_only_because", r"if only because"),
        ("rather", r"\brather\b"),
        ("yet", r"\byet\b"),
        ("which_then", r"which then"),
        ("to_a_degree", r"to a degree"),
        ("even_further", r"even further|furthermore"),
        ("let_alone", r"let alone"),
        ("in_some_form", r"in some (form|way)"),
    ]

    def set_target_ranges(self, ranges: dict[str, tuple[float, float]]):
        """Override default target ranges with corpus-derived ones."""
        self.target_ranges = {**self.target_ranges, **ranges}

    def parameterize(self, data: Any) -> dict:
        """Extract measurable voice parameters from prose text."""
        text = str(data)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        words = text.split()
        word_count = len(words)

        # Sentence length distribution
        sent_lengths = [len(s.split()) for s in sentences]
        sent_len_std = float(np.std(sent_lengths)) if sent_lengths else 0.0
        max_sent_len = max(sent_lengths) if sent_lengths else 0

        # Comma density
        comma_count = text.count(",")
        comma_density = comma_count / max(word_count, 1)

        # Em dash density
        em_dash_count = text.count("\u2014") + text.count("--")
        em_dash_density = em_dash_count / max(word_count, 1)

        # Connective density
        text_lower = text.lower()
        connective_total = 0
        for _, pattern in self.CONNECTIVE_PATTERNS:
            connective_total += len(re.findall(pattern, text_lower))
        connective_density = connective_total / max(word_count / 1000, 0.1)

        # Person pronoun ratios
        i_count = len(re.findall(r"\bI\b", text))
        you_count = len(re.findall(r"\byou\b", text_lower))
        we_count = len(re.findall(r"\bwe\b", text_lower))
        person_total = max(i_count + you_count + we_count, 1)
        i_ratio = i_count / person_total

        # Snap ratio
        short_sents = sum(1 for l in sent_lengths if l <= 8)
        long_sents = sum(1 for l in sent_lengths if l >= 50)
        snap_ratio = short_sents / max(long_sents, 1)

        # Slop count
        slop_count = sum(text_lower.count(w) for w in self.SLOP_WORDS)

        # Profanity
        profanity = len(re.findall(r"\b(fuck|shit|damn|hell|ass)\b", text_lower))
        profanity_per_1k = profanity / max(word_count / 1000, 0.1)

        return {
            "word_count": word_count,
            "comma_density": round(comma_density, 4),
            "em_dash_density": round(em_dash_density, 4),
            "sent_len_std": round(sent_len_std, 1),
            "max_sent_len": max_sent_len,
            "snap_ratio": round(snap_ratio, 2),
            "connective_density_per_1k": round(connective_density, 2),
            "i_ratio": round(i_ratio, 4),
            "slop_count": slop_count,
            "profanity_per_1k": round(profanity_per_1k, 2),
        }

    def to_vector(self, params: dict) -> np.ndarray:
        """Encode prose params as HRR vector, scaling to comparable magnitudes."""
        flat = {
            "comma_density": params["comma_density"] * 100,
            "em_dash_density": params["em_dash_density"] * 100,
            "sent_len_std": params["sent_len_std"],
            "max_sent_len": params["max_sent_len"] / 10,
            "snap_ratio": params["snap_ratio"] * 10,
            "connective_density": params["connective_density_per_1k"],
            "i_ratio": params["i_ratio"] * 10,
            "slop_count": params["slop_count"],
            "profanity": params["profanity_per_1k"],
        }
        return encode_dict(flat, self.dim)

    def generate(self, seed: Any, **kwargs) -> Any:
        """Identity — the candidate text is passed in directly.
        Prose generation happens externally (LLM call, manual writing, etc)."""
        return seed

    def corrections(self, target_params: dict, candidate_params: dict) -> list[str]:
        """Compare candidate against target ranges. Returns correction instructions."""
        fixes = []
        ranges = self.target_ranges

        cd = candidate_params["comma_density"]
        if cd < ranges["comma_density"][0]:
            fixes.append("MORE comma-chaining. Stack more clauses with commas.")
        elif cd > ranges["comma_density"][1]:
            fixes.append("Slightly fewer commas. Some sentences can end.")

        ed = candidate_params["em_dash_density"]
        if ed > ranges["em_dash_density"][1]:
            n = int(ed * candidate_params["word_count"])
            fixes.append(f"Replace ALL {n} em dashes with commas. Zero allowed.")

        std = candidate_params["sent_len_std"]
        if std < ranges["sent_len_std"][0]:
            fixes.append("More sentence length VARIATION. Mix snap lines with long clause chains.")

        mx = candidate_params["max_sent_len"]
        if mx < ranges["max_sent_len"][0]:
            fixes.append(f"Longest sentence is {mx} words. Need at least one 150+ word chain.")

        sr = candidate_params["snap_ratio"]
        if sr < ranges["snap_ratio"][0]:
            fixes.append("Need MORE snap lines (3-8 word sentences after long builds).")

        conn = candidate_params["connective_density_per_1k"]
        if conn < ranges["connective_density_per_1k"][0]:
            fixes.append("Use MORE signature connectives: 'if only because', 'rather', 'yet', 'which then'.")

        slop = candidate_params["slop_count"]
        if slop > ranges["slop_count"][1]:
            fixes.append(f"REMOVE {slop} AI slop words.")

        ir = candidate_params["i_ratio"]
        if ir < ranges["i_ratio"][0]:
            fixes.append(f"More first-person 'I' (currently {ir:.0%}, need 25-45%).")
        elif ir > ranges["i_ratio"][1]:
            fixes.append("Less first-person. More 'you' and 'we'.")

        prof = candidate_params["profanity_per_1k"]
        if prof > ranges["profanity_per_1k"][1]:
            fixes.append("Too much profanity. Max once or twice per piece.")

        return fixes

    def apply_corrections(self, candidate: Any, corrections: list[str], **kwargs) -> Any:
        """Return the candidate with corrections attached as metadata.
        Actual rewriting is external — this toy is the measurement instrument,
        not the generator."""
        return {"text": str(candidate), "pending_corrections": corrections}

    @classmethod
    def from_corpus(cls, corpus_text: str) -> "ProseFoldToy":
        """Create a ProseFoldToy with target ranges derived from a corpus.
        Measures the corpus and sets ranges as ±20% of observed values."""
        toy = cls()
        params = toy.parameterize(corpus_text)

        derived_ranges = {}
        for key in ["comma_density", "em_dash_density", "sent_len_std",
                     "connective_density_per_1k", "profanity_per_1k"]:
            val = params[key]
            margin = max(abs(val) * 0.2, 0.001)
            derived_ranges[key] = (round(val - margin, 4), round(val + margin, 4))

        derived_ranges["max_sent_len"] = (
            int(params["max_sent_len"] * 0.6),
            int(params["max_sent_len"] * 1.2),
        )
        derived_ranges["snap_ratio"] = (
            max(0, round(params["snap_ratio"] - 0.15, 2)),
            round(params["snap_ratio"] + 0.15, 2),
        )
        derived_ranges["i_ratio"] = (
            max(0, round(params["i_ratio"] - 0.1, 2)),
            min(1, round(params["i_ratio"] + 0.1, 2)),
        )
        derived_ranges["slop_count"] = (0, 0)

        toy.set_target_ranges(derived_ranges)
        return toy
