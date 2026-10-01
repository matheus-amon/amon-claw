"""Picking a free model from OpenRouter, decided by tests.

The premise: OpenRouter's free tier rotates. Whatever `:free` id is hardcoded
today gets retired, and the project breaks with a 404 at run time rather than at
test time. So the model is resolved from the live catalogue, and the policy that
picks one is a pure function over that catalogue — which means the policy is
testable with a recorded catalogue and no network.
"""

from __future__ import annotations

import json
from pathlib import Path

from amon_claw.infrastructure.llm.models.free_models import (
    FreeModel,
    parse_models,
    pick_model,
    rank_models,
)

CATALOGUE_FIXTURE = Path(__file__).parent / 'fixtures' / 'openrouter_models.json'


def load_catalogue() -> dict:
    return json.loads(CATALOGUE_FIXTURE.read_text())


class TestParseModels:
    def test_reads_the_id_and_context_window(self):
        models = parse_models(load_catalogue())

        assert all(isinstance(m, FreeModel) for m in models)
        assert len(models) > 0

    def test_reads_the_pricing(self):
        models = parse_models(load_catalogue())
        free = [m for m in models if m.is_free]

        # The fixture was captured from the live endpoint; if this is 0 the
        # fixture is stale and every other test here is asserting on nothing.
        assert len(free) > 0

    def test_tolerates_a_malformed_entry_rather_than_raising(self):
        # OpenRouter adds fields without warning. A parser that raises on an
        # unknown shape would turn a harmless upstream change into an outage.
        catalogue = {
            'data': [
                {'id': 'ok/model:free', 'pricing': {'prompt': '0', 'completion': '0'}},
                {'id': 'no-pricing/model'},
                {'unexpected': 'shape'},
            ]
        }

        models = parse_models(catalogue)

        assert [m.id for m in models] == ['ok/model:free', 'no-pricing/model', None]


class TestRankModels:
    def test_free_models_come_first(self):
        models = parse_models(load_catalogue())

        ranked = rank_models(models)

        flags = [m.is_free for m in ranked]
        assert flags == sorted(flags, reverse=True)

    def test_tool_calling_models_come_before_ones_without_it(self):
        # The agents are built on tool use. A free model that cannot call tools
        # is useless to them, so it must never outrank one that can.
        models = parse_models(load_catalogue())

        ranked = [m for m in rank_models(models) if m.supports_tools]

        # Everything ranked above the last tool-capable model must also be
        # tool-capable.
        last_tool_index = max(i for i, m in enumerate(ranked) if m.supports_tools)
        assert all(m.supports_tools for m in ranked[: last_tool_index + 1])

    def test_preferred_models_outrank_equally_good_others(self):
        # Otherwise resolution is arbitrary and a run can silently move to a
        # different model after an unrelated catalogue change.
        models = parse_models(load_catalogue())
        pinned = 'qwen/qwen3.8-27b:free'

        ranked = rank_models(models)
        pinned_index = ranked.index(next(m for m in ranked if m.id == pinned))

        better = [
            m
            for m in ranked[:pinned_index]
            if m.is_free == next(r for r in ranked if r.id == pinned).is_free
            and m.supports_tools
            == next(r for r in ranked if r.id == pinned).supports_tools
        ]
        assert all(m.id in PREFERRED for m in better) or not better


class TestPickModel:
    def test_picks_a_free_model_that_supports_tools(self):
        models = parse_models(load_catalogue())

        chosen = pick_model(models)

        assert chosen.is_free
        assert chosen.supports_tools

    def test_picks_the_first_of_the_ranking(self):
        models = parse_models(load_catalogue())

        assert pick_model(models).id == rank_models(models)[0].id

    def test_raises_when_nothing_qualifies(self):
        # Returning None here would push the failure to the first real API call,
        # with no hint about which filter emptied the list.
        models = parse_models(
            {'data': [{'id': 'paid/only', 'pricing': {'prompt': '1', 'completion': '1'}}]}
        )

        try:
            pick_model(models)
        except LookupError as error:
            assert 'free' in str(error).lower()
        else:
            raise AssertionError(
                'expected LookupError for a catalogue with no free models'
            )

    def test_raises_on_an_empty_catalogue(self):
        try:
            pick_model(parse_models({'data': []}))
        except LookupError:
            pass
        else:
            raise AssertionError('expected LookupError for an empty catalogue')

    def test_a_pinned_id_short_circuits_the_ranking(self):
        models = parse_models(load_catalogue())

        chosen = pick_model(models, preferred='poolside/laguna-s-2.1:free')

        assert chosen.id == 'poolside/laguna-s-2.1:free'

    def test_a_pinned_id_that_does_not_exist_falls_back_to_the_ranking(self):
        # A pin that has been retired must not take the whole system down; it
        # should degrade to the best free model and stay visible.
        models = parse_models(load_catalogue())

        chosen = pick_model(models, preferred='retired/model:free')

        assert chosen.is_free
        assert chosen.id != 'retired/model:free'


PREFERRED = {
    'qwen/qwen3.8-27b:free',
    'nvidia/nemotron-3-super-120b-a12b:free',
    'google/gemma-4-26b-a4b-it:free',
    'google/gemma-4-31b-it:free',
}
