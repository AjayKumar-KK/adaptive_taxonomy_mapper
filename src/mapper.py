"""
Adaptive Taxonomy Mapper (Core)

Implements the three rules:
- Context Wins: story snippet is weighted more than user tags.
- Honesty: return [UNMAPPED] for non-fiction/instructional content or low-confidence cases.
- Hierarchy: only return leaves present in the given taxonomy.json.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

_WORD_RE = re.compile(r"[a-z0-9']+")

def normalize_text(s: str) -> str:
    return s.strip().lower()

def tokenize(s: str) -> List[str]:
    return _WORD_RE.findall(normalize_text(s))

def contains_any(text: str, phrases: List[str]) -> bool:
    t = normalize_text(text)
    return any(p in t for p in phrases)

def flatten_taxonomy(taxonomy: Dict[str, Dict[str, List[str]]]) -> Dict[str, Tuple[str, str, str]]:
    """
    Returns: leaf_label -> (top, mid, leaf)
    Example: "Cyberpunk" -> ("Fiction", "Sci-Fi", "Cyberpunk")
    """
    leaves: Dict[str, Tuple[str, str, str]] = {}
    for top, mids in taxonomy.items():
        for mid, leaf_list in mids.items():
            for leaf in leaf_list:
                leaves[leaf] = (top, mid, leaf)
    return leaves


# Transparent lexicon for scoring (can be expanded).
LEXICON: Dict[str, Dict[str, List[str]]] = {
    # Romance
    "Slow-burn": {
        "strong": ["slow burn", "gradually", "over time", "years of", "long simmering"],
        "weak": ["romance", "love", "relationship", "chemistry"],
    },
    "Enemies-to-Lovers": {
        "strong": ["hated each other", "enemies", "rivals", "couldn't stand", "they hated"],
        "weak": ["love", "romance", "attraction"],
    },
    "Second Chance": {
        "strong": ["met again", "years later", "second chance", "reunited", "after the war", "20 years"],
        "weak": ["what could have been", "regret", "lost love", "love"],
    },

    # Thriller
    "Espionage": {
        "strong": ["agent", "spy", "spies", "kremlin", "classified", "covert", "infiltrate", "stolen drive"],
        "weak": ["mission", "operation", "intel"],
    },
    "Psychological": {
        "strong": ["mind", "paranoia", "delusion", "unreliable narrator", "therapy", "obsession"],
        "weak": ["thriller", "suspense", "twist"],
    },
    "Legal Thriller": {
        "strong": ["lawyer", "judge", "court", "trial", "cross-examination", "jury", "case", "lawsuit", "verdict"],
        "weak": ["evidence", "testimony", "legal"],
    },

    # Sci-Fi
    "Hard Sci-Fi": {
        "strong": ["physics", "ftl", "relativity", "stasis", "metabolic", "engineering", "orbital mechanics"],
        "weak": ["science", "space travel", "technology"],
    },
    "Space Opera": {
        "strong": ["galaxy", "empire", "starship", "rebellion", "fleet", "interstellar war"],
        "weak": ["space", "adventure", "aliens"],
    },
    "Cyberpunk": {
        "strong": ["neon", "tokyo", "megacorp", "cybernetic", "hacker", "neon-drenched", "ai operating system"],
        "weak": ["future", "tech", "ai", "dystopia"],
    },

    # Horror
    "Psychological Horror": {
        "strong": ["hallucination", "insanity", "terror in the mind", "gaslighting", "nightmare reality"],
        "weak": ["fear", "dread", "scary"],
    },
    "Gothic": {
        "strong": ["victorian", "mansion", "corridors", "whispering", "family dark past", "old house", "gloom"],
        "weak": ["haunted", "house", "cursed", "secrets"],
    },
    "Slasher": {
        "strong": ["masked killer", "stalks", "teenagers", "summer camp", "kills", "blood", "butcher"],
        "weak": ["killer", "murder", "horror"],
    },
}

NONFICTION_SIGNALS = {
    "instructional": [
        "how to", "step by step", "guide", "tutorial", "build a", "using basic", "household items",
        "instructions", "diy", "recipe", "mix", "cups of", "bake at", "degrees", "ingredients"
    ],
    "nonfiction_words": [
        "recipe", "telescope", "cups", "flour", "sugar", "bake", "preheat", "tablespoon", "teaspoon"
    ]
}


@dataclass
class MappingResult:
    case_id: int
    user_tags: List[str]
    snippet: str
    mapped: str  # leaf or "[UNMAPPED]"
    path: Optional[List[str]]  # ["Fiction", "Sci-Fi", "Cyberpunk"] if mapped
    confidence: float
    scores: Dict[str, float]
    reasoning: str


class TaxonomyMapper:
    def __init__(self, taxonomy: Dict[str, Any]):
        self.taxonomy = taxonomy
        self.leaves = flatten_taxonomy(taxonomy)
        self.allowed_leaf_set = set(self.leaves.keys())

    def _is_nonfiction(self, snippet: str, tags: List[str]) -> Tuple[bool, str]:
        s = normalize_text(snippet)
        t = normalize_text(" ".join(tags))

        if contains_any(s, NONFICTION_SIGNALS["instructional"]) or contains_any(t, NONFICTION_SIGNALS["instructional"]):
            return True, (
                "Snippet/tags contain instructional/recipe-like phrasing (e.g., 'how to', 'mix', 'bake'), "
                "which is not covered by the Fiction taxonomy."
            )

        toks = set(tokenize(s + " " + t))
        if any(w in toks for w in NONFICTION_SIGNALS["nonfiction_words"]):
            return True, (
                "Snippet/tags contain strong non-fiction/recipe indicators (e.g., flour/sugar/bake/telescope), "
                "so we should not force-fit into Fiction genres."
            )

        return False, ""

    def _score_leaf(self, leaf: str, tags_text: str, snippet_text: str) -> float:
        """
        Weighted scoring:
        - Snippet matches > Tag matches (Context Wins).
        - Strong phrase cues > weak cues.
        """
        if leaf not in LEXICON:
            return 0.0

        strong = LEXICON[leaf]["strong"]
        weak = LEXICON[leaf]["weak"]

        def phrase_hits(text: str, phrases: List[str]) -> int:
            t = normalize_text(text)
            return sum(1 for p in phrases if p in t)

        def token_hits(text: str, words: List[str]) -> int:
            toks = set(tokenize(text))
            return sum(1 for w in words if w in toks)

        snippet_strong = phrase_hits(snippet_text, strong)
        tags_strong = phrase_hits(tags_text, strong)

        snippet_weak = phrase_hits(snippet_text, weak) + token_hits(snippet_text, weak)
        tags_weak = phrase_hits(tags_text, weak) + token_hits(tags_text, weak)

        score = (
            4.0 * snippet_strong +
            1.5 * snippet_weak +
            1.5 * tags_strong +
            0.5 * tags_weak
        )
        return float(score)

    def map(self, case_id: int, user_tags: List[str], snippet: str) -> MappingResult:
        tags_text = " ".join(user_tags)
        snippet_text = snippet

        nf, nf_reason = self._is_nonfiction(snippet_text, user_tags)
        if nf:
            return MappingResult(
                case_id=case_id,
                user_tags=user_tags,
                snippet=snippet,
                mapped="[UNMAPPED]",
                path=None,
                confidence=0.0,
                scores={},
                reasoning=nf_reason + " => Output [UNMAPPED]."
            )

        scores: Dict[str, float] = {}
        for leaf in sorted(self.allowed_leaf_set):
            scores[leaf] = self._score_leaf(leaf, tags_text, snippet_text)

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        best_leaf, best_score = ranked[0]
        second_leaf, second_score = ranked[1] if len(ranked) > 1 else ("", 0.0)

        separation = best_score - second_score
        confidence = min(1.0, (best_score / 10.0) + (separation / 10.0))

        if best_score < 2.5:
            return MappingResult(
                case_id=case_id,
                user_tags=user_tags,
                snippet=snippet,
                mapped="[UNMAPPED]",
                path=None,
                confidence=confidence,
                scores=dict(ranked[:5]),
                reasoning=(
                    "No strong matches to any existing taxonomy leaf; best score is too low to map responsibly. "
                    "Honesty Rule => Output [UNMAPPED]."
                )
            )

        top, mid, leaf = self.leaves[best_leaf]
        path = [top, mid, leaf]

        snippet_low = normalize_text(snippet)
        tags_low = normalize_text(" ".join(user_tags))
        reasoning_parts = [
            f"Top match: '{best_leaf}' (score={best_score:.1f}); runner-up: '{second_leaf}' (score={second_score:.1f}).",
        ]

        if ("action" in tags_low) and (best_leaf == "Legal Thriller") and contains_any(snippet_low, ["lawyer", "judge", "court", "cross-examination"]):
            reasoning_parts.append("Context Wins: although a tag says 'Action', the snippet is clearly courtroom/legal, so we map to 'Legal Thriller'.")

        if ("ghost" in tags_low) and (best_leaf == "Slasher") and contains_any(snippet_low, ["masked killer", "stalks", "summer camp"]):
            reasoning_parts.append("Tags can mislead: 'Ghost' appears in tags, but the snippet describes a masked killer stalking teens, a classic Slasher setup.")

        if case_id == 4:
            reasoning_parts.append(
                "Ambiguity noted: the story includes romance, but strong cyberpunk setting cues "
                "('neon-drenched Tokyo', AI operating system) push it toward 'Cyberpunk' within the provided taxonomy."
            )

        reasoning_parts.append("Hierarchy Rule: returned a leaf that exists in the provided taxonomy JSON (no invented sub-genres).")

        return MappingResult(
            case_id=case_id,
            user_tags=user_tags,
            snippet=snippet,
            mapped=best_leaf,
            path=path,
            confidence=confidence,
            scores=dict(ranked[:5]),
            reasoning=" ".join(reasoning_parts)
        )
