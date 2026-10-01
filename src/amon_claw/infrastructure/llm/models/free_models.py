"""Choosing a free OpenRouter model.

## Why this exists

OpenRouter's free tier rotates. Models get retired and `:free` ids disappear, so
a hardcoded id turns into a 404 at run time — in production, on someone else's
machine, with nothing in the test suite to have caught it. Every repo reviewed
from SamoraDC pinned a `:free` model and every one of them is now unrunnable for
that reason.

So the model is resolved from the live catalogue, and the *policy* that picks one
is a pure function over that catalogue. That split is the whole design: the part
that needs the network is three lines, and the part with the opinions is tested
against a recorded catalogue with no network at all.

## The policy

1. Free before paid. Non-free models are eligible only when nothing free works.
2. Tool-calling before no-tools. These agents are built on tool use, so a free
   model that cannot call tools is not a candidate.
3. A preferred list, in order, among models that tie on 1 and 2. Without this the
   choice is arbitrary and can shift on an unrelated catalogue change.
4. A pinned id wins outright if it is still in the catalogue; if it has been
   retired, fall back rather than fail. A stale pin should degrade, not take the
   system down.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'

# Tried in order, among models that already tie on free-ness and tool support.
# Reasoning models are listed last: they are the slowest way to answer a
# scheduling question.
PREFERRED_MODEL_IDS: tuple[str, ...] = (
    'qwen/qwen3.8-27b:free',
    'google/gemma-4-31b-it:free',
    'google/gemma-4-26b-a4b-it:free',
    'nvidia/nemotron-3-super-120b-a12b:free',
)


@dataclass(frozen=True)
class FreeModel:
    id: str | None
    name: str | None
    context_length: int
    prompt_price: float | None
    completion_price: float | None
    supports_tools: bool

    @property
    def is_free(self) -> bool:
        """Free means zero on both directions.

        Prompt-only checks are the trap: a model with a zero input price and a
        paid output price bills per token generated, which is exactly what an
        agent loop does most of.
        """
        return self.prompt_price == 0 and self.completion_price == 0


def _price(raw: Any) -> float | None:
    """OpenRouter returns prices as strings; `None` when unknown."""
    if raw is None or raw == '':
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def parse_models(payload: dict[str, Any]) -> list[FreeModel]:
    """Turn a catalogue response into models, skipping nothing.

    Entries with no `id` are kept with `id=None` rather than dropped: the
    catalogue is an upstream shape we do not control, and a parser that raises on
    an entry it does not recognise turns a harmless upstream change into an
    outage. They simply never win a ranking.
    """
    models: list[FreeModel] = []

    for entry in payload.get('data') or []:
        if not isinstance(entry, dict):
            continue

        pricing = entry.get('pricing') or {}
        parameters = entry.get('supported_parameters') or []

        models.append(
            FreeModel(
                id=entry.get('id'),
                name=entry.get('name'),
                context_length=entry.get('context_length') or 0,
                prompt_price=_price(pricing.get('prompt')),
                completion_price=_price(pricing.get('completion')),
                supports_tools='tools' in parameters,
            )
        )

    return models


def rank_models(models: list[FreeModel]) -> list[FreeModel]:
    """Best first. Stable within a tier, so the order does not shuffle."""
    preference = {model_id: index for index, model_id in enumerate(PREFERRED_MODEL_IDS)}

    def sort_key(model: FreeModel) -> tuple:
        known = model.id in preference
        return (
            not model.is_free,
            not model.supports_tools,
            # An unrecognised id sorts after every preferred one; a None id
            # sorts after everything, which is what we want.
            preference.get(model.id, len(preference)) if known else len(preference),
            model.id or '',
        )

    return sorted(models, key=sort_key)


def pick_model(models: list[FreeModel], preferred: str | None = None) -> FreeModel:
    """The model to use, or `LookupError` explaining why nothing qualifies."""
    ranked = [m for m in rank_models(models) if m.id]

    if preferred:
        pinned = next((m for m in ranked if m.id == preferred), None)
        if pinned is not None:
            return pinned

    for candidate in ranked:
        if candidate.is_free and candidate.supports_tools:
            return candidate

    for candidate in ranked:
        if candidate.is_free:
            return candidate

    free_count = sum(1 for m in ranked if m.is_free)
    raise LookupError(
        f'no free OpenRouter model available '
        f'({len(ranked)} models in the catalogue, {free_count} of them free). '
        f'Set LLM_OPENROUTER_MODEL_ID to pin one explicitly.'
    )


def load_catalogue(cache_path: Path | None = None) -> dict[str, Any]:
    """Fetch the live catalogue, falling back to a cached copy.

    The fallback matters more than it looks: model resolution is on the startup
    path, so an OpenRouter outage would otherwise be an outage here too. A stale
    catalogue still yields a model that works — free ids rotate, they do not all
    vanish at once.
    """
    import httpx

    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = httpx.get(OPENROUTER_MODELS_URL, timeout=15.0)
        response.raise_for_status()
        payload = response.json()

        if cache_path is not None:
            cache_path.write_text(json.dumps(payload, indent=1))

        return payload

    except Exception:  # noqa: BLE001 - any failure falls back, by design
        if cache_path is not None and cache_path.exists():
            return json.loads(cache_path.read_text())
        raise
