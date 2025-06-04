import importlib
import importlib.util
from pathlib import Path
import sys
import types
import pytest


def test_query_devices_no_devices(monkeypatch):
    dummy_sd = types.SimpleNamespace(
        default=types.SimpleNamespace(hostapi=0, channels=None, dtype=None, latency=None, samplerate=None),
        query_devices=lambda: [],
        query_hostapis=lambda: []
    )
    monkeypatch.setitem(sys.modules, 'sounddevice', dummy_sd)
    if 'sound' in sys.modules:
        del sys.modules['sound']

    spec = importlib.util.spec_from_file_location('sound', Path('sound.py'))
    sound = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sound)
    with pytest.raises(sound.DeviceNotFoundError):
        sound.query_devices()
