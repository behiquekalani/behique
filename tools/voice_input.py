#!/usr/bin/env python3
"""
Voice Input for Ceiba -- Record from mic, transcribe with Whisper.

Records audio from the microphone, transcribes it locally with Whisper,
and outputs the text. Can run in continuous listen mode or single-shot.

Requirements:
    pip3 install openai-whisper sounddevice soundfile numpy

Usage:
    python3 voice_input.py                    # Record until Enter, transcribe
    python3 voice_input.py --duration 10      # Record 10 seconds
    python3 voice_input.py --continuous       # Keep listening, transcribe each pause
    python3 voice_input.py --model small      # Better accuracy (slower)
    python3 voice_input.py --lang es          # Force Spanish
    python3 voice_input.py --clipboard        # Copy result to clipboard
    python3 voice_input.py --file audio.wav   # Transcribe existing file
"""
import argparse
import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path

TRANSCRIPT_DIR = Path.home() / "behique" / "Ceiba" / "07-Transcripts"


def check_deps():
    """Check required dependencies."""
    missing = []
    try:
        import sounddevice
    except ImportError:
        missing.append("sounddevice")
    try:
        import soundfile
    except ImportError:
        missing.append("soundfile")
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip3 install {' '.join(missing)}")
        return False
    return True


def record_audio(duration=None, sample_rate=16000):
    """Record audio from microphone.

    If duration is None, records until user presses Enter.
    Returns numpy array of audio data.
    """
    import sounddevice as sd
    import numpy as np

    if duration:
        print(f"  Recording {duration}s...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        print("  Done recording.")
        return audio.flatten(), sample_rate
    else:
        print("  Recording... Press Enter to stop.")
        chunks = []
        recording = True

        def callback(indata, frames, time_info, status):
            if recording:
                chunks.append(indata.copy())

        stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32", callback=callback)
        stream.start()
        input()  # Wait for Enter
        recording = False
        stream.stop()
        stream.close()

        if not chunks:
            return np.array([]), sample_rate

        audio = np.concatenate(chunks).flatten()
        duration_s = len(audio) / sample_rate
        print(f"  Recorded {duration_s:.1f}s of audio.")
        return audio, sample_rate


def transcribe_audio(audio_path, model_name="base", language=None):
    """Transcribe audio file with Whisper."""
    import whisper

    print(f"  Loading Whisper ({model_name})...")
    model = whisper.load_model(model_name)

    print("  Transcribing...")
    start = time.time()
    result = model.transcribe(str(audio_path), language=language)
    elapsed = time.time() - start

    text = result["text"].strip()
    detected_lang = result.get("language", "unknown")
    print(f"  Transcribed in {elapsed:.1f}s (detected: {detected_lang})")

    return text, detected_lang


def copy_to_clipboard(text):
    """Copy text to macOS clipboard."""
    try:
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        return True
    except Exception:
        return False


def single_shot(args):
    """Record once, transcribe, output."""
    import soundfile as sf
    import numpy as np

    if args.file:
        text, lang = transcribe_audio(args.file, model_name=args.model, language=args.lang)
    else:
        audio, sr = record_audio(duration=args.duration)
        if len(audio) == 0:
            print("No audio recorded.")
            return

        # Save to temp file for Whisper
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(tmp.name, audio, sr)
        tmp.close()

        text, lang = transcribe_audio(tmp.name, model_name=args.model, language=args.lang)
        os.unlink(tmp.name)

    if not text:
        print("No speech detected.")
        return

    print(f"\n{'=' * 40}")
    print(text)
    print(f"{'=' * 40}")

    if args.clipboard:
        if copy_to_clipboard(text):
            print("  Copied to clipboard.")

    if args.save:
        TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_path = TRANSCRIPT_DIR / f"voice_{timestamp}.txt"
        with open(out_path, "w") as f:
            f.write(text)
        print(f"  Saved to {out_path}")

    return text


def continuous_mode(args):
    """Keep listening, transcribe each pause."""
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    print("\n  CONTINUOUS LISTEN MODE")
    print("  Speak naturally. Pauses trigger transcription.")
    print("  Press Ctrl+C to stop.\n")

    sample_rate = 16000
    silence_threshold = 0.01
    silence_duration = 1.5  # seconds of silence = end of utterance
    min_audio_duration = 0.5  # minimum audio to transcribe

    import whisper
    print(f"  Loading Whisper ({args.model})...")
    model = whisper.load_model(args.model)
    print("  Ready. Listening...\n")

    try:
        while True:
            chunks = []
            silent_chunks = 0
            has_speech = False
            chunk_duration = 0.1  # 100ms chunks
            chunk_samples = int(sample_rate * chunk_duration)
            silence_chunks_needed = int(silence_duration / chunk_duration)

            while True:
                chunk = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype="float32")
                sd.wait()
                level = np.abs(chunk).mean()

                if level > silence_threshold:
                    has_speech = True
                    silent_chunks = 0
                    chunks.append(chunk)
                elif has_speech:
                    silent_chunks += 1
                    chunks.append(chunk)
                    if silent_chunks >= silence_chunks_needed:
                        break

            if not has_speech or not chunks:
                continue

            audio = np.concatenate(chunks).flatten()
            duration_s = len(audio) / sample_rate

            if duration_s < min_audio_duration:
                continue

            # Save and transcribe
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp.name, audio, sample_rate)
            tmp.close()

            result = model.transcribe(tmp.name, language=args.lang)
            text = result["text"].strip()
            os.unlink(tmp.name)

            if text:
                print(f"  > {text}")
                if args.clipboard:
                    copy_to_clipboard(text)

    except KeyboardInterrupt:
        print("\n  Stopped listening.")


def main():
    parser = argparse.ArgumentParser(description="Voice input for Ceiba")
    parser.add_argument("--duration", type=float, help="Recording duration in seconds")
    parser.add_argument("--continuous", action="store_true", help="Continuous listen mode")
    parser.add_argument("--model", default="base", help="Whisper model (tiny/base/small/medium/large)")
    parser.add_argument("--lang", help="Force language (en, es, etc)")
    parser.add_argument("--clipboard", action="store_true", help="Copy result to clipboard")
    parser.add_argument("--save", action="store_true", help="Save transcript to file")
    parser.add_argument("--file", help="Transcribe existing audio file instead of recording")

    args = parser.parse_args()

    if not args.file and not check_deps():
        sys.exit(1)

    if args.continuous:
        continuous_mode(args)
    else:
        single_shot(args)


if __name__ == "__main__":
    main()
