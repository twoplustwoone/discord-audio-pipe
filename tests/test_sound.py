import importlib
import importlib.util
from pathlib import Path
import sys
import types
import pytest


def load_sound(dummy_sd, monkeypatch):
    """Import the ``sound`` module using a provided dummy sounddevice module."""
    monkeypatch.setitem(sys.modules, 'sounddevice', dummy_sd)
    if 'sound' in sys.modules:
        del sys.modules['sound']

    spec = importlib.util.spec_from_file_location('sound', Path('sound.py'))
    sound = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sound)
    return sound


def test_query_devices_no_devices(monkeypatch):
    dummy_sd = types.SimpleNamespace(
        default=types.SimpleNamespace(hostapi=0, channels=None, dtype=None, latency=None, samplerate=None),
        query_devices=lambda: [],
        query_hostapis=lambda: []
    )
    sound = load_sound(dummy_sd, monkeypatch)
    with pytest.raises(sound.DeviceNotFoundError) as exc:
        sound.query_devices()
    msg = str(exc.value)
    assert "Devices" in msg and "Host APIs" in msg


def test_query_devices_filters(monkeypatch):
    devices = [
        {"name": "mic1", "max_input_channels": 2, "hostapi": 0},
        {"name": "mic2", "max_input_channels": 0, "hostapi": 0},
        {"name": "mic3", "max_input_channels": 2, "hostapi": 1},
    ]
    dummy_sd = types.SimpleNamespace(
        default=types.SimpleNamespace(hostapi=0, channels=None, dtype=None, latency=None, samplerate=48000),
        query_devices=lambda: devices,
    )
    sound = load_sound(dummy_sd, monkeypatch)
    assert sound.query_devices() == {"mic1": 0}


def test_pcmstream_change_device(monkeypatch):
    class DummyStream:
        def __init__(self, device):
            self.device = device
            self.started = False
            self.stopped = False
            self.closed = False

        def start(self):
            self.started = True

        def stop(self):
            self.stopped = True

        def close(self):
            self.closed = True

        def read(self, frames):
            return (b"x" * frames * 4, None)

    dummy_sd = types.SimpleNamespace(
        default=types.SimpleNamespace(hostapi=0, channels=2, dtype="int16", latency="low", samplerate=48000),
        RawInputStream=lambda device: DummyStream(device),
    )
    sound = load_sound(dummy_sd, monkeypatch)

    stream = sound.PCMStream()
    assert stream.read() is None

    stream.change_device(1)
    assert stream.stream.device == 1
    assert stream.stream.started

    data = stream.read()
    assert isinstance(data, bytes)
    assert len(data) == stream.frames * 4

    prev_stream = stream.stream
    stream.change_device(2)
    assert prev_stream.stopped and prev_stream.closed
    assert stream.stream.device == 2

