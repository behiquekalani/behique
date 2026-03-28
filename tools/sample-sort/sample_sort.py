#!/usr/bin/env python3
"""
SampleSort - AI Sample Library Organizer
Scans audio files, analyzes them, auto-categorizes, and tags with metadata.

Usage:
    python3 sample_sort.py ~/Music/Samples              # Scan and organize
    python3 sample_sort.py ~/Music/Samples --dry-run     # Preview without moving
    python3 sample_sort.py ~/Music/Samples --search "dark 808"  # Search by description
    python3 sample_sort.py --stats                       # Show library stats

Product: $19.99 on Gumroad (part of FL Studio AI Plugin Suite)
"""

import os
import sys
import json
import wave
import struct
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_FILE = Path(os.path.expanduser("~/behique/Ceiba/projects/sample-sort-db.json"))
AUDIO_EXTS = {'.wav', '.mp3', '.flac', '.aif', '.aiff', '.ogg', '.m4a'}

# Category detection by filename patterns
CATEGORIES = {
    'kick': ['kick', 'kik', 'bd', 'bass drum', 'bassdrum'],
    'snare': ['snare', 'snr', 'sd', 'clap', 'rimshot', 'rim'],
    'hihat': ['hihat', 'hi-hat', 'hh', 'hat', 'open hat', 'closed hat', 'oh', 'ch'],
    'percussion': ['perc', 'shaker', 'tamb', 'conga', 'bongo', 'tom', 'crash', 'ride', 'cymbal', 'bell', 'cowbell', 'wood', 'block'],
    'bass': ['bass', '808', 'sub', 'low', 'reese'],
    'synth': ['synth', 'lead', 'pad', 'arp', 'pluck', 'stab', 'chord', 'keys', 'organ', 'piano', 'electric piano', 'ep'],
    'vocal': ['vocal', 'vox', 'voice', 'chant', 'choir', 'adlib', 'ad-lib', 'sing'],
    'fx': ['fx', 'sfx', 'effect', 'riser', 'sweep', 'impact', 'downlifter', 'uplifter', 'transition', 'noise', 'foley', 'ambient', 'texture', 'atmosphere', 'atmos', 'whoosh', 'reverse'],
    'loop': ['loop', 'break', 'breakbeat', 'groove', 'pattern', 'toploop', 'top loop', 'drum loop', 'melody loop'],
    'guitar': ['guitar', 'gtr', 'acoustic', 'electric guitar', 'strum'],
    'strings': ['strings', 'violin', 'cello', 'viola', 'orchestra', 'orch'],
    'brass': ['brass', 'trumpet', 'horn', 'trombone', 'sax', 'saxophone'],
}

# Genre detection by folder/filename patterns
GENRES = {
    'trap': ['trap', 'drill', 'uk drill'],
    'hiphop': ['hip hop', 'hiphop', 'hip-hop', 'boom bap', 'boombap', 'rap'],
    'edm': ['edm', 'house', 'techno', 'trance', 'dubstep', 'dnb', 'drum and bass', 'future bass'],
    'lofi': ['lofi', 'lo-fi', 'lo fi', 'chill'],
    'pop': ['pop', 'mainstream'],
    'rnb': ['rnb', 'r&b', 'soul', 'neo soul'],
    'reggaeton': ['reggaeton', 'dembow', 'latin'],
    'rock': ['rock', 'punk', 'metal', 'grunge'],
    'jazz': ['jazz', 'swing', 'bebop'],
    'classical': ['classical', 'orchestral', 'cinematic', 'film', 'soundtrack'],
    'ambient': ['ambient', 'drone', 'meditation', 'nature'],
}

# Key detection from filename
KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
KEY_PATTERNS = []
for k in KEYS:
    KEY_PATTERNS.append((k.lower(), k))
    KEY_PATTERNS.append((k.lower() + ' major', k + ' Major'))
    KEY_PATTERNS.append((k.lower() + ' minor', k + ' Minor'))
    KEY_PATTERNS.append((k.lower() + 'maj', k + ' Major'))
    KEY_PATTERNS.append((k.lower() + 'min', k + ' Minor'))
    KEY_PATTERNS.append((k.lower() + 'm', k + 'm'))


def detect_category(filepath):
    """Detect sample category from filename and path."""
    name = filepath.stem.lower()
    parent = filepath.parent.name.lower()
    full = f"{parent}/{name}"

    for cat, patterns in CATEGORIES.items():
        for p in patterns:
            if p in full:
                return cat
    return 'uncategorized'


def detect_genre(filepath):
    """Detect genre from path."""
    full_path = str(filepath).lower()
    for genre, patterns in GENRES.items():
        for p in patterns:
            if p in full_path:
                return genre
    return 'unknown'


def detect_key(filepath):
    """Detect musical key from filename."""
    name = filepath.stem.lower()
    # Check for key patterns (longer patterns first to avoid false matches)
    sorted_patterns = sorted(KEY_PATTERNS, key=lambda x: -len(x[0]))
    for pattern, key in sorted_patterns:
        if f' {pattern} ' in f' {name} ' or name.endswith(f' {pattern}') or name.startswith(f'{pattern} '):
            return key
    return None


def detect_bpm(filepath):
    """Detect BPM from filename."""
    import re
    name = filepath.stem
    # Look for BPM patterns: "120bpm", "120 bpm", "bpm120", "tempo 120"
    patterns = [
        r'(\d{2,3})\s*bpm',
        r'bpm\s*(\d{2,3})',
        r'tempo\s*(\d{2,3})',
        r'_(\d{2,3})_',  # Common in sample packs: "kick_120_C.wav"
    ]
    for p in patterns:
        match = re.search(p, name, re.IGNORECASE)
        if match:
            bpm = int(match.group(1))
            if 60 <= bpm <= 300:
                return bpm
    return None


def get_wav_info(filepath):
    """Get basic WAV file info."""
    try:
        with wave.open(str(filepath), 'rb') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            channels = w.getnchannels()
            duration = frames / rate if rate > 0 else 0
            return {
                'duration': round(duration, 2),
                'sample_rate': rate,
                'channels': channels,
                'bit_depth': w.getsampwidth() * 8,
            }
    except Exception:
        return None


def file_hash(filepath):
    """Quick hash for duplicate detection (first 8KB + size)."""
    h = hashlib.md5()
    size = filepath.stat().st_size
    h.update(str(size).encode())
    with open(filepath, 'rb') as f:
        h.update(f.read(8192))
    return h.hexdigest()


def scan_directory(root_path):
    """Scan directory for audio files and analyze them."""
    root = Path(root_path)
    if not root.exists():
        print(f"  Error: {root} does not exist.")
        return []

    samples = []
    seen_hashes = set()
    duplicates = 0

    print(f"  Scanning {root}...")
    for filepath in root.rglob('*'):
        if filepath.suffix.lower() not in AUDIO_EXTS:
            continue

        # Duplicate detection
        fhash = file_hash(filepath)
        if fhash in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(fhash)

        category = detect_category(filepath)
        genre = detect_genre(filepath)
        key = detect_key(filepath)
        bpm = detect_bpm(filepath)

        info = get_wav_info(filepath) if filepath.suffix.lower() == '.wav' else None

        sample = {
            'path': str(filepath),
            'name': filepath.stem,
            'ext': filepath.suffix.lower(),
            'size': filepath.stat().st_size,
            'category': category,
            'genre': genre,
            'key': key,
            'bpm': bpm,
            'hash': fhash,
            'duration': info['duration'] if info else None,
            'sample_rate': info['sample_rate'] if info else None,
            'channels': info['channels'] if info else None,
            'scanned': datetime.now().isoformat(),
        }
        samples.append(sample)

    print(f"  Found {len(samples)} unique audio files ({duplicates} duplicates skipped)")
    return samples


def organize(samples, root_path, dry_run=False):
    """Organize samples into category folders."""
    root = Path(root_path)
    organized_dir = root / '_organized'
    moves = defaultdict(list)

    for s in samples:
        cat = s['category']
        src = Path(s['path'])
        dest = organized_dir / cat / src.name

        # Avoid name collisions
        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            i = 1
            while dest.exists():
                dest = organized_dir / cat / f"{stem}_{i}{suffix}"
                i += 1

        moves[cat].append((src, dest))

    print(f"\n  Organization plan:")
    for cat, files in sorted(moves.items()):
        print(f"    {cat}: {len(files)} files")

    if dry_run:
        print(f"\n  [DRY RUN] No files moved. Run without --dry-run to organize.")
        return

    # Execute moves
    moved = 0
    for cat, files in moves.items():
        cat_dir = organized_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        for src, dest in files:
            try:
                import shutil
                shutil.copy2(str(src), str(dest))
                moved += 1
            except Exception as e:
                print(f"    Error: {src.name}: {e}")

    print(f"\n  Organized {moved} files into {organized_dir}")


def search_samples(samples, query):
    """Search samples by description."""
    query_parts = query.lower().split()
    results = []

    for s in samples:
        searchable = f"{s['name']} {s['category']} {s['genre']} {s.get('key', '')} {s.get('bpm', '')}".lower()
        if all(part in searchable for part in query_parts):
            results.append(s)

    return results


def show_stats(samples):
    """Show library statistics."""
    if not samples:
        print("  No samples in database. Scan a directory first.")
        return

    cats = defaultdict(int)
    genres = defaultdict(int)
    total_size = 0
    with_key = 0
    with_bpm = 0

    for s in samples:
        cats[s['category']] += 1
        genres[s['genre']] += 1
        total_size += s['size']
        if s.get('key'): with_key += 1
        if s.get('bpm'): with_bpm += 1

    print(f"\n  ═══════════════════════════════════════")
    print(f"  SAMPLE LIBRARY STATS")
    print(f"  ═══════════════════════════════════════")
    print(f"  Total samples: {len(samples)}")
    print(f"  Total size: {total_size / (1024*1024):.1f} MB")
    print(f"  With key detected: {with_key} ({with_key/len(samples)*100:.0f}%)")
    print(f"  With BPM detected: {with_bpm} ({with_bpm/len(samples)*100:.0f}%)")
    print(f"\n  Categories:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        bar = '█' * min(30, count // max(1, len(samples) // 30))
        print(f"    {cat:15s} {count:4d} {bar}")
    print(f"\n  Genres:")
    for genre, count in sorted(genres.items(), key=lambda x: -x[1]):
        print(f"    {genre:15s} {count:4d}")
    print(f"  ═══════════════════════════════════════\n")


def load_db():
    """Load sample database."""
    if DB_FILE.exists():
        with open(DB_FILE) as f:
            return json.load(f)
    return []


def save_db(samples):
    """Save sample database."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_FILE, 'w') as f:
        json.dump(samples, f, indent=2)


def main():
    args = sys.argv[1:]

    if not args or '--help' in args:
        print("""
  SampleSort - AI Sample Library Organizer

  Usage:
    python3 sample_sort.py <folder>              Scan and categorize
    python3 sample_sort.py <folder> --organize    Organize into category folders
    python3 sample_sort.py <folder> --dry-run     Preview organization
    python3 sample_sort.py --search "dark 808"    Search samples
    python3 sample_sort.py --stats                Library statistics
    python3 sample_sort.py --help                 This message
        """)
        return

    if '--stats' in args:
        samples = load_db()
        show_stats(samples)
        return

    if '--search' in args:
        idx = args.index('--search')
        if idx + 1 < len(args):
            query = args[idx + 1]
            samples = load_db()
            results = search_samples(samples, query)
            print(f"\n  Search: '{query}' ({len(results)} results)")
            for r in results[:20]:
                key_str = f" [{r['key']}]" if r.get('key') else ""
                bpm_str = f" {r['bpm']}bpm" if r.get('bpm') else ""
                dur_str = f" {r['duration']:.1f}s" if r.get('duration') else ""
                print(f"    [{r['category']:12s}] {r['name']}{key_str}{bpm_str}{dur_str}")
                print(f"                  {r['path']}")
            if len(results) > 20:
                print(f"    ... and {len(results) - 20} more")
        return

    # Scan directory
    folder = args[0]
    if not os.path.isdir(folder):
        print(f"  Error: '{folder}' is not a directory.")
        return

    samples = scan_directory(folder)
    if not samples:
        print("  No audio files found.")
        return

    save_db(samples)
    print(f"  Database saved ({len(samples)} samples)")
    show_stats(samples)

    if '--organize' in args or '--dry-run' in args:
        dry_run = '--dry-run' in args
        organize(samples, folder, dry_run)


if __name__ == "__main__":
    main()
