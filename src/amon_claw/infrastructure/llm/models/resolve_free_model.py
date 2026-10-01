"""`resolve_free_model`: the one function that touches the network.

Everything with an opinion in it lives in `free_models` and is tested against a
recorded catalogue. This is the thin wrapper, and its tests hand it a fake
loader so they never touch OpenRouter.
"""

from __future__ import annotations

from pathlib import Path

from amon_claw.infrastructure.llm.models.free_models import (
    load_catalogue,
    parse_models,
    pick_model,
)

# The resolved model is cached for the process lifetime. Resolution is on the
# startup path and the catalogue does not change within a run.
_resolved: str | None = None


def resolve_free_model(
    preferred: str | None = None,
    cache_path: Path | None = None,
    use_cache: bool = True,
) -> str:
    """The OpenRouter model id to use, resolved from the live free catalogue.

    Raises `LookupError` when nothing qualifies. A caller that would rather fall
    back to a default should do that explicitly rather than get `None` and
    discover it three frames later.
    """
    global _resolved

    if use_cache and _resolved is not None and preferred is None:
        return _resolved

    catalogue = load_catalogue(cache_path)
    chosen = pick_model(parse_models(catalogue), preferred=preferred).id

    if chosen is None:
        raise LookupError('resolved a model with no id')

    if use_cache and preferred is None:
        _resolved = chosen

    return chosen


def reset_cache() -> None:
    """Clear the memoised resolution. For tests, and to re-resolve."""
    global _resolved
    _resolved = None
