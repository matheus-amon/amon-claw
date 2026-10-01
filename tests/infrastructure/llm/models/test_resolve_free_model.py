"""`resolve_free_model`: the one function that touches the network.

Everything with an opinion in it lives in `free_models` and is tested against a
recorded catalogue. This is the thin wrapper, and its tests hand it a fake
loader so they never touch OpenRouter.
"""

from __future__ import annotations

from pathlib import Path

from amon_claw.infrastructure.llm.models import resolve_free_model as resolve_module
from amon_claw.infrastructure.llm.models.resolve_free_model import (
    reset_cache,
    resolve_free_model,
)


def _fake_loader(payload):
    """A `load_catalogue` stand-in returning a fixed catalogue.

    Patched into the *resolver's* namespace: `resolve_free_model` binds
    `load_catalogue` at import time, so patching the source module or this test
    module would leave the resolver still calling the real one.
    """

    def loader(cache_path=None):
        return payload

    return loader


def _model(model_id: str, prompt: str = '0', completion: str = '0', tools: bool = True):
    return {
        'id': model_id,
        'pricing': {'prompt': prompt, 'completion': completion},
        'supported_parameters': ['tools'] if tools else [],
    }


class TestResolveFreeModel:
    def setup_method(self):
        reset_cache()

    def teardown_method(self):
        reset_cache()

    def test_returns_a_free_tool_calling_model(self, monkeypatch):
        monkeypatch.setattr(
            resolve_module,
            'load_catalogue',
            _fake_loader(
                {
                    'data': [
                        _model('free/with-tools:free'),
                        _model('paid/model', '0.001', '0.002'),
                    ]
                }
            ),
        )

        assert resolve_free_model() == 'free/with-tools:free'

    def test_a_pinned_id_wins(self, monkeypatch):
        monkeypatch.setattr(
            resolve_module,
            'load_catalogue',
            _fake_loader(
                {
                    'data': [
                        _model('best/default:free'),
                        _model('pinned/model:free'),
                    ]
                }
            ),
        )

        assert resolve_free_model(preferred='pinned/model:free') == 'pinned/model:free'

    def test_a_retired_pin_degrades_to_the_ranking(self, monkeypatch):
        # A `:free` id that has been retired must not take the system down.
        monkeypatch.setattr(
            resolve_module,
            'load_catalogue',
            _fake_loader({'data': [_model('survivor:free')]}),
        )

        assert resolve_free_model(preferred='retired/model:free') == 'survivor:free'

    def test_the_result_is_memoised(self, monkeypatch):
        calls = {'n': 0}

        def counting_loader(cache_path=None):
            calls['n'] += 1
            return {'data': [_model('m:free')]}

        monkeypatch.setattr(resolve_module, 'load_catalogue', counting_loader)

        first = resolve_free_model()
        second = resolve_free_model()

        assert first == second
        assert calls['n'] == 1

    def test_an_explicit_pin_bypasses_the_memo(self, monkeypatch):
        # Otherwise pinning a model after startup would silently do nothing.
        monkeypatch.setattr(
            resolve_module,
            'load_catalogue',
            _fake_loader({'data': [_model('a:free'), _model('b:free')]}),
        )

        resolve_free_model()
        pinned = resolve_free_model(preferred='b:free')

        assert pinned == 'b:free'

    def test_reset_cache_forces_re_resolution(self, monkeypatch):
        calls = {'n': 0}

        def counting_loader(cache_path=None):
            calls['n'] += 1
            return {'data': [_model('m:free')]}

        monkeypatch.setattr(resolve_module, 'load_catalogue', counting_loader)

        resolve_free_model()
        reset_cache()
        resolve_free_model()

        assert calls['n'] == 2

    def test_it_propagates_a_lookup_error_when_nothing_is_free(self, monkeypatch):
        monkeypatch.setattr(
            resolve_module,
            'load_catalogue',
            _fake_loader({'data': [_model('paid/only', '1', '1')]}),
        )

        try:
            resolve_free_model()
        except LookupError as error:
            assert 'free' in str(error).lower()
        else:
            raise AssertionError('expected LookupError when nothing is free')

    def test_a_cache_path_is_passed_through_to_the_loader(self, monkeypatch):
        seen: list[Path | None] = []

        def recording_loader(cache_path=None):
            seen.append(cache_path)
            return {'data': [_model('m:free')]}

        monkeypatch.setattr(resolve_module, 'load_catalogue', recording_loader)

        resolve_free_model(cache_path=Path('/tmp/catalogue.json'), use_cache=False)

        assert seen == [Path('/tmp/catalogue.json')]
