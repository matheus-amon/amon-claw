"""Resolving the configured model id, with or without a pin.

The config field `openrouter_model_id` used to default to a hardcoded `:free`
model, which is a bet on an id that OpenRouter will eventually retire — and a
retired `:free` id is a 404 at run time on someone else's machine, with nothing
in the suite to have caught it. Empty now means "resolve from the catalogue".
"""

from __future__ import annotations

from amon_claw.core.settings.llm import LLMConfig, configured_model_id
from amon_claw.infrastructure.llm.models import resolve_free_model as resolve_module


def test_an_empty_config_resolves_from_the_catalogue(monkeypatch):
    monkeypatch.setattr(
        resolve_module, 'resolve_free_model', lambda: 'resolved/model:free'
    )
    # Field names, not env-prefixed names: the prefix applies to the environment
    # and to nothing else, so `llm_openrouter_model_id` is an unknown field that
    # extra='ignore' silently drops.
    config = LLMConfig(openrouter_api_key='dummy', openrouter_model_id='')

    assert configured_model_id(config) == 'openrouter/resolved/model:free'


def test_a_pinned_config_uses_the_pin_without_calling_the_catalogue(monkeypatch):
    # A pin is the operator saying "I know what I want"; it should not cost a
    # network call or fail because OpenRouter is down.
    def explode():
        raise AssertionError('must not resolve when a pin is set')

    monkeypatch.setattr(resolve_module, 'resolve_free_model', explode)
    config = LLMConfig(
        openrouter_api_key='dummy', openrouter_model_id='pinned/model:free'
    )

    assert configured_model_id(config) == 'pinned/model:free'


def test_whitespace_only_counts_as_no_pin():
    config = LLMConfig(openrouter_api_key='dummy', openrouter_model_id='   ')

    assert config.openrouter_model_id.strip() == ''
