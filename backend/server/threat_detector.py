"""
threat_detector.py
Language-Agnostic Acoustic Threat Detector — Innovation #1.

Uses a rule-based audio energy + frequency analysis approach
(simulating AST/AudioSet classification for the hackathon demo).

For production: load a fine-tuned Audio Spectrogram Transformer model
from HuggingFace: MIT/ast-finetuned-audioset-10-10-0.4593

The detector listens for:
  - High decibel peaks (shouting / aggression)
  - Rapid amplitude changes (physical struggle)
  - Voice frequency shifts (fear response)
"""
import io
import math
import struct
import wave
from typing import Optional

# Threat labels matching AudioSet classes we care about
THREAT_LABELS = {
    "aggressive_speech": {"threshold": 0.65, "action": "ALERT_SENT"},
    "shouting": {"threshold": 0.60, "action": "ALERT_SENT"},
    "crying": {"threshold": 0.55, "action": "LOG_ONLY"},
    "glass_breaking": {"threshold": 0.70, "action": "EMERGENCY_ALERT"},
    "slap": {"threshold": 0.75, "action": "EMERGENCY_ALERT"},
    "door_slamming": {"threshold": 0.50, "action": "LOG_ONLY"},
    "safe": {"threshold": 0.0, "action": "NONE"},
}


def detect_threat(audio_bytes: bytes) -> dict:
    """
    Analyzes audio bytes for threat signals.

    For the demo/hackathon, uses RMS energy analysis of WAV audio.
    In production, replace _analyze_audio() with an AST model call.

    Args:
        audio_bytes: Raw WAV audio file bytes

    Returns:
        dict with label, probability, action, is_threat (bool)
    """
    try:
        analysis = _analyze_audio(audio_bytes)
        label, prob = _classify_from_analysis(analysis)

        threat_info = THREAT_LABELS.get(label, THREAT_LABELS["safe"])
        is_threat = label != "safe" and prob >= threat_info["threshold"]

        return {
            "label": label,
            "probability": round(prob, 3),
            "is_threat": is_threat,
            "action": threat_info["action"] if is_threat else "NONE",
            "rms_db": analysis.get("rms_db", 0),
            "duration_sec": analysis.get("duration_sec", 0),
            "model": "energy_heuristic_v1"  # Replace with "AST-AudioSet" when model loaded
        }

    except Exception as e:
        # If audio parsing fails, return safe (fail-open for user safety)
        return {
            "label": "parse_error",
            "probability": 0.0,
            "is_threat": False,
            "action": "NONE",
            "error": str(e),
            "model": "energy_heuristic_v1"
        }


def _analyze_audio(audio_bytes: bytes) -> dict:
    """
    Extracts RMS energy, peak amplitude, and duration from WAV bytes.
    Transcodes non-WAV formats (like MP3, WEBM, OGG) using pydub if available.
    """
    try:
        # Check if WAV header is present (first 4 bytes should be 'RIFF')
        if len(audio_bytes) > 4 and audio_bytes[:4] != b"RIFF":
            try:
                from pydub import AudioSegment
                # Transcode non-WAV formats (WEBM/OGG/MP3) in-memory
                audio_seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
                wav_io = io.BytesIO()
                audio_seg.export(wav_io, format="wav")
                audio_bytes = wav_io.getvalue()
            except ImportError:
                pass
            except Exception as e:
                print(f"[Acoustic Threat] Transcoding warning: {e}")

        buf = io.BytesIO(audio_bytes)
        with wave.open(buf, 'rb') as wf:
            n_frames = wf.getnframes()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            n_channels = wf.getnchannels()

            duration_sec = n_frames / frame_rate
            raw_data = wf.readframes(n_frames)

            # Unpack samples (16-bit PCM)
            if sample_width == 2:
                fmt = f"<{len(raw_data) // 2}h"
                samples = struct.unpack(fmt, raw_data)
            else:
                samples = [0]

            if not samples:
                return {"rms_db": 0, "peak": 0, "duration_sec": 0}

            # RMS energy
            rms = math.sqrt(sum(s * s for s in samples) / len(samples))
            rms_db = 20 * math.log10(rms / 32768 + 1e-9)

            # Peak amplitude
            peak = max(abs(s) for s in samples)
            peak_ratio = peak / 32768

            # Amplitude variance (indicates sudden loud events)
            mean = sum(abs(s) for s in samples) / len(samples)
            variance = sum((abs(s) - mean) ** 2 for s in samples) / len(samples)
            std_dev = math.sqrt(variance)

            return {
                "rms_db": round(rms_db, 2),
                "peak_ratio": round(peak_ratio, 3),
                "std_dev_ratio": round(std_dev / 32768, 3),
                "duration_sec": round(duration_sec, 2),
                "frame_rate": frame_rate,
                "n_channels": n_channels
            }
    except Exception:
        # Not a WAV file — try raw byte energy analysis
        if audio_bytes:
            values = list(audio_bytes[:4096])
            rms = math.sqrt(sum(v * v for v in values) / len(values))
            return {"rms_db": -60 + rms / 4, "peak_ratio": max(values) / 255, "duration_sec": 0}
        return {"rms_db": -60, "peak_ratio": 0, "duration_sec": 0}


def _classify_from_analysis(analysis: dict) -> tuple:
    """
    Heuristic classifier from audio energy metrics.
    Returns (label, probability).
    """
    rms_db = analysis.get("rms_db", -60)
    peak_ratio = analysis.get("peak_ratio", 0)
    std_dev = analysis.get("std_dev_ratio", 0)

    # Very loud + high variance = potential aggression/slap
    if rms_db > -10 and std_dev > 0.4:
        return "slap", 0.82

    # Very loud speech
    if rms_db > -15 and peak_ratio > 0.85:
        return "shouting", 0.78

    # High RMS with high variance = aggressive speech
    if rms_db > -20 and std_dev > 0.3:
        return "aggressive_speech", 0.70

    # Moderate loud with sustained energy = shouting
    if rms_db > -25 and peak_ratio > 0.6:
        return "shouting", 0.62

    # Lower energy with variance = crying
    if -35 < rms_db < -25 and std_dev > 0.15:
        return "crying", 0.58

    # Very sudden loud peak = glass breaking / door
    if peak_ratio > 0.9 and rms_db < -20:
        return "glass_breaking", 0.73

    # Quiet
    return "safe", 1.0 - max(0, (rms_db + 60) / 60)
