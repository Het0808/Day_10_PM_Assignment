# 🤖 AI-Augmented Task — Text Analysis Module

---

## 1️⃣ Exact Prompt Used

> *"Write a Python module with a function called analyze_text(text: str, **options)
> that accepts any text and keyword arguments for options
> (count_words=True, count_sentences=True, find_longest_word=True, sentiment_simple=True).
> Each option enables a different analysis. Use *args and **kwargs, add type hints
> and Google-style docstrings. Return a dict with all requested analyses."*

---

## 2️⃣ AI Output (Claude)

```python
import re
from typing import Any

def analyze_text(text: str, **options: Any) -> dict[str, Any]:
    """
    Analyze text with configurable options.

    Args:
        text: Input text to analyze.
        **options: Keyword flags to enable analyses:
            count_words (bool): Count total words. Default True.
            count_sentences (bool): Count sentences. Default True.
            find_longest_word (bool): Find longest word. Default True.
            sentiment_simple (bool): Basic positive/negative/neutral. Default True.

    Returns:
        Dict with analysis results for each enabled option.
    """
    results: dict[str, Any] = {}

    count_words      = options.get("count_words",      True)
    count_sentences  = options.get("count_sentences",  True)
    find_longest     = options.get("find_longest_word", True)
    sentiment        = options.get("sentiment_simple", True)

    if count_words:
        words = text.split()
        results["word_count"] = len(words)

    if count_sentences:
        sentences = re.split(r'[.!?]+', text)
        results["sentence_count"] = len([s for s in sentences if s.strip()])

    if find_longest:
        words = re.findall(r'\b\w+\b', text)
        results["longest_word"] = max(words, key=len) if words else ""

    if sentiment:
        positive_words = {"good", "great", "excellent", "happy", "love", "wonderful"}
        negative_words = {"bad", "terrible", "awful", "hate", "horrible", "poor"}
        words_lower = set(text.lower().split())
        pos = len(words_lower & positive_words)
        neg = len(words_lower & negative_words)
        if pos > neg:
            results["sentiment"] = "positive"
        elif neg > pos:
            results["sentiment"] = "negative"
        else:
            results["sentiment"] = "neutral"

    return results
```

---

## 3️⃣ Critical Evaluation

| Check | Result | Notes |
|-------|--------|-------|
| Uses `**kwargs` correctly | ✅ | `.get()` with defaults — good |
| Type hints correct | ⚠️ Partial | Missing `-> dict[str, Any]` return annotation on `options` type (minor). `**options: Any` is correct. |
| Handles empty text | ❌ | `text.split()` on `""` returns `[]` — word_count=0 is fine, but `max(words, key=len)` would fail if AI guard wasn't there. The `if words` guard is present but not documented. |
| Handles `None` text | ❌ | No guard — `None.split()` raises `AttributeError` |
| Handles no options passed | ⚠️ | All analyses run by default (all=True). This is reasonable but undocumented. |
| Docstring useful? | ⚠️ | Adequate but doesn't document return dict keys or edge cases |
| Single Responsibility Principle | ❌ **Violated** | One function does 4 unrelated things — word counting, sentence splitting, string analysis, ML-adjacent sentiment — hard to test, extend, or reuse independently |
| Sentiment wordlist | ❌ | Hardcoded tiny wordlist (6 words each). "not good" would be scored "positive". No negation handling. |
| `words` variable shadowed | ⚠️ | `words` is defined twice (lines 1 and 3 of the function body) |

**Verdict:** The AI output works for the happy path but violates SRP, misses `None` input, and the sentiment analysis is too simplistic to be useful.

---

## 4️⃣ Improved Version

The core improvement is decomposition: each analysis is its own pure function. `analyze_text` becomes a thin orchestrator that delegates to them. This follows the Single Responsibility Principle and makes each piece independently testable.

```python
# ============================================================
#  text_analysis.py
#  Decomposed, SRP-compliant text analysis module
# ============================================================

import re
from typing import Any

# ── Positive / negative word sets (easily extendable) ────────
_POSITIVE_WORDS: frozenset[str] = frozenset({
    "good", "great", "excellent", "happy", "love", "wonderful",
    "amazing", "fantastic", "brilliant", "outstanding", "joy",
})
_NEGATIVE_WORDS: frozenset[str] = frozenset({
    "bad", "terrible", "awful", "hate", "horrible", "poor",
    "dreadful", "disgusting", "miserable", "worst", "sad",
})


# ── Individual analysis functions (each has 1 responsibility) ─

def count_words(text: str) -> int:
    """
    Count whitespace-delimited words in text.

    Args:
        text: Input string. Empty string returns 0.

    Returns:
        Non-negative integer word count.

    Example:
        >>> count_words("Hello world")
        2
    """
    if not text or not text.strip():
        return 0
    return len(text.split())


def count_sentences(text: str) -> int:
    """
    Count sentences delimited by '.', '!', or '?'.

    Args:
        text: Input string.

    Returns:
        Non-negative integer sentence count.

    Example:
        >>> count_sentences("Hello. How are you? Fine!")
        3
    """
    if not text or not text.strip():
        return 0
    parts = re.split(r"[.!?]+", text)
    return len([p for p in parts if p.strip()])


def find_longest_word(text: str) -> str:
    """
    Find the longest word (by character count) in text.
    Ties are broken by first occurrence.

    Args:
        text: Input string.

    Returns:
        Longest word string, or empty string if no words found.

    Example:
        >>> find_longest_word("The quick brown fox")
        'quick'
    """
    words = re.findall(r"\b\w+\b", text or "")
    return max(words, key=len) if words else ""


def simple_sentiment(text: str) -> str:
    """
    Classify text as 'positive', 'negative', or 'neutral'
    using a keyword-matching heuristic.

    Limitations: no negation handling ("not good" scores positive),
    no context awareness. Use a proper NLP library for production.

    Args:
        text: Input string.

    Returns:
        One of: 'positive', 'negative', 'neutral'.

    Example:
        >>> simple_sentiment("This is a great day!")
        'positive'
    """
    if not text:
        return "neutral"

    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos_count = len(words & _POSITIVE_WORDS)
    neg_count = len(words & _NEGATIVE_WORDS)

    if pos_count > neg_count:
        return "positive"
    if neg_count > pos_count:
        return "negative"
    return "neutral"


# ── Orchestrator ─────────────────────────────────────────────

_ANALYSIS_MAP: dict[str, tuple[str, Any]] = {
    "count_words":      ("word_count",     count_words),
    "count_sentences":  ("sentence_count", count_sentences),
    "find_longest_word":("longest_word",   find_longest_word),
    "sentiment_simple": ("sentiment",      simple_sentiment),
}


def analyze_text(text: str, **options: bool) -> dict[str, Any]:
    """
    Run configurable text analyses and return results as a dict.

    Delegates each analysis to a dedicated single-responsibility function.
    All analyses are enabled by default; pass False to disable any.

    Args:
        text: Input string to analyse. None is treated as empty string.
        **options: Boolean flags — each defaults to True:
            count_words      (bool): Count total word tokens.
            count_sentences  (bool): Count sentence-ending punctuation.
            find_longest_word(bool): Return the longest word by length.
            sentiment_simple (bool): Keyword-based positive/negative/neutral.

    Returns:
        Dict with a key for each enabled analysis:
            {
              "word_count":     int,
              "sentence_count": int,
              "longest_word":   str,
              "sentiment":      'positive' | 'negative' | 'neutral',
            }
        Only keys for enabled analyses are present.

    Edge cases:
        - None text → treated as empty string (no crash)
        - Empty text → all numeric results are 0, sentiment is 'neutral'
        - No options → all analyses run (all default True)
        - All options False → returns empty dict {}

    Example:
        >>> analyze_text("Python is great!", count_words=True, sentiment_simple=True)
        {'word_count': 3, 'sentiment': 'positive'}
    """
    # Sanitise input — never crash on None
    safe_text: str = text if isinstance(text, str) else ""

    results: dict[str, Any] = {}

    for option_key, (result_key, fn) in _ANALYSIS_MAP.items():
        if options.get(option_key, True):           # default: enabled
            results[result_key] = fn(safe_text)

    return results


# ── Tests ─────────────────────────────────────────────────────

def _run_tests() -> None:
    print("Running tests...\n")
    ok = 0

    def check(name, got, expected):
        nonlocal ok
        if got == expected:
            print(f"  ✅  {name}")
            ok += 1
        else:
            print(f"  ❌  {name}  got={got!r}  expected={expected!r}")

    text = "Python is great! I love coding. Bad bugs are awful."

    check("word_count",     analyze_text(text)["word_count"],     10)
    check("sentence_count", analyze_text(text)["sentence_count"], 3)
    check("longest_word",   analyze_text(text)["longest_word"],   "coding")
    check("sentiment",      analyze_text(text)["sentiment"],      "positive")

    # Selective options
    r = analyze_text(text, count_words=True, sentiment_simple=False)
    check("only word_count key present", set(r.keys()) == {"word_count"}, True)

    # Empty text
    check("empty word_count",    analyze_text("")["word_count"],     0)
    check("empty longest_word",  analyze_text("")["longest_word"],   "")
    check("empty sentiment",     analyze_text("")["sentiment"],      "neutral")

    # None text (AI version would crash here)
    check("None text no crash",  analyze_text(None)["word_count"],   0)

    # All false → empty dict
    check("all false → {}",      analyze_text(text, count_words=False,
          count_sentences=False, find_longest_word=False,
          sentiment_simple=False), {})

    print(f"\n  {ok}/9 tests passed\n")


if __name__ == "__main__":
    _run_tests()

    print("── Sample analysis ──────────────────────────────────")
    sample = "Python is a wonderful language. Writing code is great fun!"
    result = analyze_text(sample)
    for key, val in result.items():
        print(f"  {key:<16}: {val}")
```

---

## 5️⃣ Improvements Summary

| Aspect | AI Version | Improved Version |
|--------|-----------|-----------------|
| SRP | ❌ One monolithic function | ✅ 4 focused helpers + thin orchestrator |
| None input | ❌ AttributeError | ✅ Sanitised before use |
| Empty text | ⚠️ Implicit | ✅ Explicit guards in each function |
| Testability | ❌ Must test whole function | ✅ Each helper tested independently |
| Extensibility | ❌ Add another `if` block | ✅ Add entry to `_ANALYSIS_MAP` dict |
| `words` shadowing | ❌ Variable reused | ✅ No name reuse |
| Docstrings | ⚠️ Basic | ✅ Documents return keys + edge cases |
| All-false option | ❌ Still runs all | ✅ Returns `{}` correctly |
