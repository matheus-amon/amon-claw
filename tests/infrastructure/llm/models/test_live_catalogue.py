"""Live catalogue check, marked so the default run skips it.

This is the test that would have caught the original problem: a hardcoded
`:free` model id that has been retired. The fixture is a recording, and
recordings go stale — so this one asks the real endpoint what the answer is now.

Opt in with `AMON_CLAW_LIVE=1`. It is not in CI: a network call in the suite
means the suite fails for reasons that have nothing to do with the code.
"""

from __future__ import annotations

import os

import pytest

from amon_claw.infrastructure.llm.models.free_models import (
    load_catalogue,
    parse_models,
    pick_model,
)

pytestmark = pytest.mark.skipif(
    os.getenv('AMON_CLAW_LIVE') != '1',
    reason='set AMON_CLAW_LIVE=1 to run tests that call OpenRouter',
)


def test_the_live_catalogue_has_a_free_tool_calling_model():
    models = parse_models(load_catalogue())

    chosen = pick_model(models)

    assert chosen.is_free
    assert chosen.supports_tools


def test_every_preferred_model_still_exists():
    """The preference list is allowed to rot, but not silently.

    A retired entry in `PREFERRED_MODEL_IDS` just stops being preferred, which
    is harmless. This test makes that visible instead: when it fails, remove the
    entry rather than wondering why resolution changed.
    """
    from amon_claw.infrastructure.llm.models.free_models import PREFERRED_MODEL_IDS

    available = {m.id for m in parse_models(load_catalogue())}

    missing = [model_id for model_id in PREFERRED_MODEL_IDS if model_id not in available]

    assert not missing, f'retired from the free catalogue: {missing}'
