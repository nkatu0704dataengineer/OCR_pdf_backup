import re
from pathlib import Path
from typing import List, Optional

from src.ocr.domain.models.keyword import KeywordCount, KeywordReport


# Default keywords to write when config/keywords.txt does not exist
_DEFAULT_KEYWORDS = [
    "Trí tuệ nhân tạo",
    "Đổi mới",
    "Chuyển đổi số",
    "Xấu xí",
]


class KeywordCounter:
    """
    Tier 1 Pure Algorithmic Keyword Counter:
    Fast, deterministic, 100% exact matching (case-insensitive Unicode regex)
    based on the extracted result.md text.
    """

    @staticmethod
    def load_keywords(keywords_file: str) -> List[str]:
        """
        Loads keywords from the given file path (one keyword per line).
        If the file does not exist, creates it with a default set of sample keywords.
        Blank lines and leading/trailing whitespace are stripped.
        """
        kw_path = Path(keywords_file)

        if not kw_path.exists():
            kw_path.parent.mkdir(parents=True, exist_ok=True)
            with open(kw_path, "w", encoding="utf-8") as f:
                for kw in _DEFAULT_KEYWORDS:
                    f.write(kw + "\n")
            print(f"[KEYWORDS] Created default keywords file: {kw_path}")

        keywords: List[str] = []
        with open(kw_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    keywords.append(stripped)

        return keywords

    @staticmethod
    def count_keywords(
        text: str,
        keywords: List[str],
        document_id: str = "",
        source_file: str = "",
        enable_llm: bool = False,
        min_similarity: float = 0.86,
        **kwargs,
    ) -> KeywordReport:
        """
        Counts exact occurrences of each keyword in *text* using pure deterministic
        case-insensitive Unicode regex pattern matching.
        """
        text_lower = text.lower()
        keyword_counts: dict[str, KeywordCount] = {}
        total_exact = 0

        # Tier 1: Pure Exact Matching
        for kw in keywords:
            pattern = re.escape(kw.lower())
            matches = list(re.finditer(pattern, text_lower, flags=re.UNICODE))
            exact_count = len(matches)

            kw_obj = KeywordCount(
                keyword=kw,
                exact_count=exact_count,
                fuzzy_count=0,
                count=exact_count,
                variants=[],
            )
            keyword_counts[kw] = kw_obj
            total_exact += exact_count

        return KeywordReport(
            document_id=document_id,
            source_file=source_file,
            keywords=list(keyword_counts.values()),
            total_keywords_searched=len(keywords),
            total_exact_matches=total_exact,
            total_fuzzy_matches=0,
            total_matches=total_exact,
            llm_enabled=False,
        )

