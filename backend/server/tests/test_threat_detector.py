import pytest
import math
import struct
import io
import wave
from server.threat_detector import detect_threat

def _create_mock_wav(samples: list, frame_rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(frame_rate)
        raw_data = struct.pack(f"<{len(samples)}h", *samples)
        wf.writeframes(raw_data)
    return buf.getvalue()

def test_detect_threat_safe():
    # Quiet samples
    samples = [100] * 16000
    audio_bytes = _create_mock_wav(samples)
    res = detect_threat(audio_bytes)
    assert res["is_threat"] is False
    assert res["label"] == "safe"
    assert res["action"] == "NONE"

def test_detect_threat_shouting():
    # Loud samples
    samples = [28000 if i % 2 == 0 else -28000 for i in range(16000)]
    audio_bytes = _create_mock_wav(samples)
    res = detect_threat(audio_bytes)
    # The heuristic should trigger shout/slap/aggression because peak ratio is near 0.85+
    assert res["is_threat"] is True
    assert res["label"] in ["shouting", "slap", "aggressive_speech"]
    assert res["action"] in ["ALERT_SENT", "EMERGENCY_ALERT"]
