# FL Studio AI Plugin Guide
**Build AI-Powered Plugins for FL Studio. Sell Them. Repeat.**

---

## Introduction: The FL Studio Plugin Opportunity

FL Studio has over 30 million registered users. That number keeps growing. The platform is the entry point for a massive slice of the global music production market, from bedroom producers in Puerto Rico to professional beatmakers in Atlanta.

Here is what most of those users do not have: AI-powered workflow tools that actually work inside their DAW.

The AI wave hit writing in 2022. It hit image generation the same year. Code assistants followed. Music production got a few gimmicks, some text-to-audio experiments, and very little that integrates with an existing workflow. Producers are still picking chords by ear. Still guessing at mix balance. Still mastering by feel.

That is the gap.

You are not building a DAW. You are not competing with Native Instruments or iZotope. You are building workflow extensions. Small Python scripts that hook into FL Studio's MIDI scripting API, do something useful, and give a producer time back. The kind of tool that sells for $29 on Plugin Boutique and generates recurring revenue while you sleep.

This guide covers four plugins from architecture to deployment. You will write real code. You will understand the systems underneath it. By the end, you will have enough to ship your first plugin this month.

**What this is not:** a music theory course. A close look into signal processing DSP. A guide for building VST3 plugins in C++. Those things have their place. This is not that place.

**What this is:** a builder's guide. Practical code. Honest about what the FL Studio API can and cannot do. Structured for someone who knows Python but has never touched a DAW extension before.

---

## Chapter 1: FL Studio's Scripting Architecture

Before writing a line of code, you need to understand what you are actually building against.

### VST vs MIDI Scripts: What Is the Difference

FL Studio supports two types of extensions. VST plugins are compiled audio processing units, written in C++ against Steinberg's VST3 SDK. They process audio signals in real time. Building a VST requires C++, DSP knowledge, and a build toolchain. That is not what this guide covers.

MIDI scripts are different. FL Studio introduced its MIDI Script Python API to let users build controller integrations and workflow automation tools using Python. These scripts do not process audio. They receive MIDI events, interact with FL Studio's internal state through a documented API, and output MIDI data back into the project.

The limitation: you cannot process audio with a MIDI script. The capability: you can control almost everything else. Piano roll. Mixer channels. Channel rack. Patterns. Transport. Plugins receive parameter changes. Notes get injected into the piano roll programmatically.

For building AI melody generators, chord progression tools, and workflow assistants, MIDI scripts are the right tool. For audio processing like EQ or compression, you need a different approach. Chapters 4 and 6 use Python to analyze exported audio files and generate recommendations, rather than processing audio in real time.

### How Python Runs Inside FL Studio

FL Studio ships with an embedded Python 3.11 interpreter. When you place a Python script in FL Studio's MIDI scripts directory, the software loads it automatically. Your script becomes a module that FL Studio calls on events.

The event model works like this. FL Studio calls a set of predefined functions in your module when specific things happen. You define these functions. FL Studio calls them.

```python
# The three functions FL Studio calls in every MIDI script

def OnInit():
 # Called when the script loads
 pass

def OnDeInit():
 # Called when the script unloads
 pass

def OnMidiMsg(event):
 # Called when a MIDI message arrives
 # event.data1 = note number or CC number
 # event.data2 = velocity or CC value
 # event.status = message type (note on, note off, CC)
 pass
```

The FL Studio module exposes the API. You import it at the top of every script.

```python
import fl_studio as fl
import channels
import mixer
import patterns
import ui
```

The module names are flat. `channels` controls the channel rack. `mixer` controls the mixer. `patterns` controls the pattern data, which is where notes live.

### What the API Can Do

The most important capabilities for this guide:

- **Read and write notes in the piano roll.** `patterns.getPatternLength()`, `channels.getChannelName()`, and the note manipulation functions let you inject MIDI notes directly into the current pattern.
- **Read mixer state.** Channel volumes, panning, effects chain status.
- **Send MIDI messages.** Output notes, CC values, pitch bend.
- **Display UI feedback.** `ui.setHintMsg()` shows a message in FL Studio's hint bar.
- **Trigger transport controls.** Play, stop, record.

What the API cannot do: read audio data from mixer channels in real time. This is the key limitation. The mixing and mastering chapters work around this by analyzing rendered audio files, not the live audio stream.

---

## Chapter 2: Setting Up Your Dev Environment

### Requirements

- FL Studio 20.9 or newer (any edition including trial)
- Python 3.10+ installed separately for development
- A code editor (VS Code, Cursor, or any editor with Python support)
- Windows or macOS

### Directory Structure

FL Studio looks for MIDI scripts in a specific directory. On Windows, it is usually at:

```
C:\Users\[username]\Documents\Image-Line\FL Studio\Settings\Hardware\
```

On macOS:

```
~/Documents/Image-Line/FL Studio/Settings/Hardware/
```

Each script lives in its own folder. The folder name becomes the script's display name in FL Studio. Inside the folder, you need at least one Python file named `device_[YourName].py`.

```
Hardware/
 AIPluginGuide_MelodyGen/
 device_AImelodyGen.py
```

### Your First Working Script

Create the folder and file. Paste this minimal script:

```python
import fl_studio as fl
import ui

def OnInit():
 ui.setHintMsg("AI Melody Gen: loaded")
 print("Script initialized")

def OnDeInit():
 print("Script unloaded")

def OnMidiMsg(event):
 event.handled = False # Pass event through to FL Studio
```

Open FL Studio. Go to Options > MIDI Settings. Under "Controller type," find your new script and select it. If it loads without error, the hint bar at the bottom of FL Studio shows your message.

This is your baseline. Everything else builds on this pattern.

### Testing Without a MIDI Controller

You do not need a physical MIDI controller to test scripts. FL Studio's virtual keyboard (shortcut: type in the piano roll, or use the touch keyboard) sends MIDI events that trigger `OnMidiMsg`. Use this for all basic testing.

For more complex testing, Python's built-in `print()` calls write to FL Studio's script output window. Go to View > Script Output to see them. Use print statements liberally during development.

---

## Chapter 3: Building an AI Melody Generator

The melody generator takes a musical key and scale as input and outputs a sequence of MIDI notes into the piano roll. The AI component comes from two sources: a pattern recognition model trained on common melodic patterns, and optional LLM integration for creative variation.

### Understanding MIDI Notes

Every MIDI note is a number from 0 to 127. Middle C is 60. Each semitone is one number. An octave is 12 semitones.

```python
# Note number reference
MIDDLE_C = 60
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_name(note_number):
 octave = (note_number // 12) - 1
 name = NOTE_NAMES[note_number % 12]
 return f"{name}{octave}"

def name_to_note(name, octave=4):
 note = NOTE_NAMES.index(name)
 return note + (octave + 1) * 12
```

### Scale Patterns

Every musical scale is a pattern of intervals. A major scale is: whole, whole, half, whole, whole, whole, half. In semitone numbers: 2, 2, 1, 2, 2, 2, 1.

```python
SCALES = {
 'major': [0, 2, 4, 5, 7, 9, 11],
 'minor': [0, 2, 3, 5, 7, 8, 10],
 'pentatonic': [0, 2, 4, 7, 9],
 'dorian': [0, 2, 3, 5, 7, 9, 10],
 'mixolydian': [0, 2, 4, 5, 7, 9, 10],
}

def get_scale_notes(root_note, scale_name, octaves=2):
 """Return all MIDI note numbers in a given scale starting from root."""
 pattern = SCALES.get(scale_name, SCALES['major'])
 notes = []
 for octave in range(octaves):
 for interval in pattern:
 notes.append(root_note + interval + (octave * 12))
 return notes
```

### Pattern-Based Melody Generation

The simplest version uses a Markov chain. You define transition probabilities between scale degrees, then walk the chain to generate a melody.

```python
import random

# Transition matrix for major scale (simplified)
# Index = current scale degree, value = probability weights for next note
MAJOR_TRANSITIONS = {
 0: [0, 3, 4, 2, 1, 2, 1], # From root: likely to go to 3rd or 4th
 1: [2, 0, 3, 3, 2, 1, 1], # From 2nd
 2: [3, 2, 0, 3, 3, 1, 0], # From 3rd
 3: [2, 2, 3, 0, 3, 2, 1], # From 4th
 4: [3, 2, 3, 3, 0, 2, 1], # From 5th (dominant)
 5: [2, 2, 2, 3, 3, 0, 2], # From 6th
 6: [4, 2, 2, 2, 2, 1, 0], # From 7th: strong pull to root
}

def generate_melody_pattern(length=8, starting_degree=0):
 """Generate a sequence of scale degree indices."""
 melody = [starting_degree]
 current = starting_degree
 for _ in range(length - 1):
 weights = MAJOR_TRANSITIONS[current % 7]
 next_degree = random.choices(range(7), weights=weights)[0]
 melody.append(next_degree)
 current = next_degree
 return melody
```

### Writing Notes to the Piano Roll

```python
import patterns
import channels

def inject_melody(root_note, scale_name, length=8):
 """Generate and inject a melody into the current FL Studio pattern."""
 scale_notes = get_scale_notes(root_note, scale_name)
 melody_degrees = generate_melody_pattern(length)

 # Get current pattern index
 pattern_index = patterns.patternNumber()

 # Clear existing notes (optional, comment out to stack melodies)
 # patterns.clearAllNotes()

 note_length = 96 # FL Studio uses PPQ of 96 (one beat = 96 ticks)
 channel = channels.channelNumber()

 for i, degree in enumerate(melody_degrees):
 if degree < len(scale_notes):
 note = scale_notes[degree]
 velocity = random.randint(80, 110)
 position = i * note_length
 # patterns.addNote(channel, note, position, note_length, velocity)
 # Note: exact API call depends on FL Studio version
 # Check Image-Line documentation for current note insertion method

 ui.setHintMsg(f"Melody generated: {length} notes in {scale_name}")
```

### LLM Integration for Creative Variation

The Markov chain approach generates functional melodies. For more interesting output, you can query an LLM to suggest note sequences, then convert the response to MIDI data.

```python
import json
from openai import OpenAI # pip install openai

client = OpenAI() # Uses OPENAI_API_KEY from environment

def generate_melody_with_llm(key, scale, mood, bars=2):
 """Use GPT to suggest a melody as scale degree sequences."""
 prompt = f"""
 Generate a {bars}-bar melody in {key} {scale} scale with a {mood} mood.
 Return ONLY a JSON array of objects with keys: degree (0-6), duration (1=quarter, 0.5=eighth), velocity (60-110).
 Example: [{{"degree": 0, "duration": 1, "velocity": 90}}, .]
 Total note count: approximately {bars * 4} notes.
 """

 response = client.chat.completions.create(
 model="gpt-4o-mini",
 messages=[{"role": "user", "content": prompt}],
 response_format={"type": "json_object"}
 )

 # Parse and convert to MIDI
 data = json.loads(response.choices[0].message.content)
 return data.get("notes", [])
```

The key design principle: the LLM handles creative decisions (what feels right for the mood), the Python code handles the technical conversion to MIDI. Keep them separate. This makes it easier to swap models or fall back to the Markov chain if the API is unavailable.

---

## Chapter 4: Building an AI Mixing Assistant

The FL Studio MIDI API does not give you access to live audio data from mixer channels. So this plugin works differently: you render a short clip from FL Studio, then analyze the audio file with Python.

The analysis covers three areas: loudness balance between channels, frequency masking (two instruments competing in the same frequency range), and overall tonal balance.

### The Analysis Pipeline

```python
import numpy as np
import librosa # pip install librosa

def analyze_audio_file(filepath):
 """Load and analyze a rendered audio file."""
 y, sr = librosa.load(filepath, sr=None, mono=False)

 results = {
 'loudness_lufs': estimate_loudness(y, sr),
 'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y[0] if y.ndim > 1 else y, sr=sr))),
 'low_end_energy': get_frequency_band_energy(y, sr, 20, 200),
 'mid_energy': get_frequency_band_energy(y, sr, 200, 4000),
 'high_energy': get_frequency_band_energy(y, sr, 4000, 20000),
 }

 return results

def get_frequency_band_energy(y, sr, low_hz, high_hz):
 """Return the average energy in a frequency band."""
 if y.ndim > 1:
 y = y[0] # Use left channel for analysis
 stft = np.abs(librosa.stft(y))
 freqs = librosa.fft_frequencies(sr=sr)
 band_mask = (freqs >= low_hz) & (freqs <= high_hz)
 band_energy = np.mean(stft[band_mask, :])
 return float(band_energy)
```

### Generating Recommendations

Once you have the analysis data, the recommendation logic is straightforward rule-based processing with optional LLM enhancement.

```python
def generate_mix_recommendations(analysis_results):
 """Convert analysis data into actionable mixing suggestions."""
 recommendations = []

 # Loudness check
 lufs = analysis_results['loudness_lufs']
 if lufs < -14:
 recommendations.append({
 'type': 'loudness',
 'message': f'Mix is quiet at {lufs:.1f} LUFS. Target -14 LUFS for streaming platforms.',
 'action': 'Increase master fader or use gentle compression on the master bus.'
 })
 elif lufs > -8:
 recommendations.append({
 'type': 'loudness',
 'message': f'Mix is hot at {lufs:.1f} LUFS. Risk of clipping on streaming platforms.',
 'action': 'Lower the master fader. Let mastering handle final loudness.'
 })

 # Tonal balance check
 low = analysis_results['low_end_energy']
 mid = analysis_results['mid_energy']
 high = analysis_results['high_energy']

 if low > mid * 2:
 recommendations.append({
 'type': 'frequency',
 'message': 'Low end is dominant. Mix may sound muddy on small speakers.',
 'action': 'Apply a high-pass filter to non-bass elements around 60-100Hz.'
 })

 if high < mid * 0.3:
 recommendations.append({
 'type': 'frequency',
 'message': 'High end is weak. Mix may sound dull.',
 'action': 'Add 2-4dB at 8-12kHz with a high shelf EQ on the master bus.'
 })

 return recommendations
```

### Displaying Results in FL Studio

Since the MIDI API can only show short messages in the hint bar, longer results go to a simple text file that the user opens.

```python
import os

def save_mix_report(recommendations, output_path):
 """Write mixing recommendations to a text file."""
 with open(output_path, 'w') as f:
 f.write("=== AI Mixing Assistant Report ===\n\n")
 if not recommendations:
 f.write("Mix looks balanced. No major issues detected.\n")
 for i, rec in enumerate(recommendations, 1):
 f.write(f"{i}. [{rec['type'].upper()}] {rec['message']}\n")
 f.write(f" Action: {rec['action']}\n\n")

 # Open the file automatically
 os.startfile(output_path) # Windows
 # subprocess.run(['open', output_path]) # macOS
```

---

## Chapter 5: Building an AI Chord Progression Tool

Chord progressions are patterns. Every genre has common patterns. Pop songs lean on I-IV-V-I and I-V-vi-IV. Hip-hop favors i-VII-VI progressions in minor keys. Jazz uses ii-V-I movements constantly.

The LLM integration here is valuable because progressions have a creative dimension that pure rules miss. You can describe a mood to the model and get progressions that match it.

### Roman Numeral Chord System

Music theory uses Roman numerals to describe chord positions in a key. I is the chord built on the first note of the scale (the tonic). IV is built on the fourth note. V is the dominant.

```python
# Chord intervals from scale root (in semitones)
# Triad = three notes, each a third apart in the scale
CHORD_INTERVALS = {
 'major': [0, 4, 7], # Major triad: root, major third, perfect fifth
 'minor': [0, 3, 7], # Minor triad: root, minor third, perfect fifth
 'dominant7': [0, 4, 7, 10], # Dominant 7th
 'major7': [0, 4, 7, 11], # Major 7th
 'minor7': [0, 3, 7, 10], # Minor 7th
}

# Chord quality for each scale degree in major key
MAJOR_SCALE_CHORD_QUALITY = {
 1: 'major', # I - major
 2: 'minor', # ii - minor
 3: 'minor', # iii - minor
 4: 'major', # IV - major
 5: 'dominant7', # V7 - dominant 7th
 6: 'minor', # vi - minor
 7: 'minor', # vii° - diminished (simplified to minor here)
}

def build_chord(root_note, quality):
 """Return MIDI note numbers for a chord."""
 intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS['major'])
 return [root_note + interval for interval in intervals]

def get_chord_for_degree(key_root, degree, scale='major'):
 """Get the chord for a given scale degree in a key."""
 scale_intervals = SCALES[scale]
 root = key_root + scale_intervals[degree - 1]
 quality = MAJOR_SCALE_CHORD_QUALITY.get(degree, 'major')
 return build_chord(root, quality)
```

### LLM Chord Generation

```python
def generate_progression_with_llm(key, scale, mood, bars=4, model="gpt-4o-mini"):
 """Use an LLM to generate a chord progression."""
 prompt = f"""
 Generate a {bars}-chord progression in {key} {scale} for a track with a {mood} mood.
 Return ONLY a JSON array with this structure:
 [{{"degree": 1, "quality": "major", "duration_bars": 1}}, .]
 Use scale degrees 1-7. Quality must be one of: major, minor, dominant7, major7, minor7.
 """

 response = client.chat.completions.create(
 model=model,
 messages=[{"role": "user", "content": prompt}],
 response_format={"type": "json_object"}
 )

 data = json.loads(response.choices[0].message.content)
 return data.get("chords", [])

def inject_chord_progression(key_root, progression_data, beats_per_bar=4):
 """Write a chord progression into the FL Studio piano roll."""
 ticks_per_beat = 96
 ticks_per_bar = ticks_per_beat * beats_per_bar
 position = 0

 for chord_data in progression_data:
 chord_notes = get_chord_for_degree(key_root, chord_data['degree'])
 duration = chord_data.get('duration_bars', 1) * ticks_per_bar

 for note in chord_notes:
 # Write each note of the chord at the same position
 # patterns.addNote(channel, note, position, duration, 90)
 pass

 position += duration
```

The critical design choice here: the LLM describes the progression conceptually (scale degrees and qualities), not as absolute MIDI note numbers. This means the same prompt works for any key. You pass the key root separately.

---

## Chapter 6: Building an AI Mastering Helper

Mastering is the final step before distribution. Its goals are straightforward: reach a consistent loudness target, fix obvious EQ problems, check stereo width. The AI here is mostly measurement plus rule-based recommendations, with LLM assistance for explanations.

### Loudness Measurement

Streaming platforms have specific loudness targets. Spotify normalizes to -14 LUFS integrated. Apple Music normalizes to -16 LUFS. YouTube normalizes to -13 LUFS.

LUFS (Loudness Units Full Scale) is a perceptual loudness measure. It accounts for human hearing sensitivity across frequencies.

```python
def measure_lufs(filepath):
 """Measure integrated loudness of an audio file."""
 try:
 import pyloudnorm as pyln # pip install pyloudnorm
 y, sr = librosa.load(filepath, sr=None, mono=False)

 # pyloudnorm expects shape (samples, channels)
 if y.ndim == 1:
 data = y.reshape(-1, 1)
 else:
 data = y.T

 meter = pyln.Meter(sr)
 loudness = meter.integrated_loudness(data)
 return loudness
 except ImportError:
 # Fallback: estimate from RMS
 y, sr = librosa.load(filepath, sr=None)
 rms = np.sqrt(np.mean(y**2))
 lufs_estimate = 20 * np.log10(rms) - 3 # Rough approximation
 return lufs_estimate
```

### Stereo Width Analysis

A mix that is too wide sounds artificial and loses mono compatibility. A mix that is too narrow sounds flat. The target range is context-dependent but most produced tracks sit between 0.3 and 0.8 correlation.

```python
def analyze_stereo_width(filepath):
 """Measure stereo correlation and width."""
 y, sr = librosa.load(filepath, sr=None, mono=False)

 if y.ndim < 2:
 return {'correlation': 1.0, 'width': 0.0, 'note': 'File is mono'}

 left = y[0]
 right = y[1]

 # Correlation coefficient
 correlation = float(np.corrcoef(left, right)[0, 1])

 # Mid/Side encoding to measure width
 mid = (left + right) / 2
 side = (left - right) / 2

 mid_energy = float(np.mean(mid**2))
 side_energy = float(np.mean(side**2))

 width = side_energy / (mid_energy + 1e-10)

 return {
 'correlation': correlation,
 'width': width,
 'note': interpret_stereo(correlation, width)
 }

def interpret_stereo(correlation, width):
 if correlation < 0:
 return 'Phase issues detected. Check for inverted channels or extreme stereo processing.'
 elif correlation > 0.95:
 return 'Mix is nearly mono. Consider widening the stereo image with reverb or stereo plugins.'
 elif width > 1.5:
 return 'Stereo field is very wide. May lose impact in mono playback.'
 else:
 return 'Stereo field looks normal.'
```

### Full Mastering Report

```python
def generate_mastering_report(filepath, target_platform='spotify'):
 """Run complete mastering analysis and return recommendations."""
 TARGETS = {
 'spotify': {'lufs': -14, 'true_peak': -1},
 'apple': {'lufs': -16, 'true_peak': -1},
 'youtube': {'lufs': -13, 'true_peak': -1},
 'club': {'lufs': -8, 'true_peak': -0.3},
 }

 target = TARGETS.get(target_platform, TARGETS['spotify'])
 lufs = measure_lufs(filepath)
 stereo = analyze_stereo_width(filepath)
 freq_analysis = analyze_audio_file(filepath)

 report = {
 'file': filepath,
 'platform_target': target_platform,
 'loudness': {
 'measured': round(lufs, 1),
 'target': target['lufs'],
 'delta': round(lufs - target['lufs'], 1),
 'action': f"{'Lower' if lufs > target['lufs'] else 'Raise'} gain by {abs(lufs - target['lufs']):.1f} dB"
 },
 'stereo': stereo,
 'frequency': {
 'low': round(freq_analysis['low_end_energy'], 4),
 'mid': round(freq_analysis['mid_energy'], 4),
 'high': round(freq_analysis['high_energy'], 4),
 }
 }

 return report
```

---

## Chapter 7: Packaging and Selling Your Plugin

Building the plugin is half the work. Getting it to market is the other half. This chapter covers all three platforms and the process for each.

### Preparing Your Plugin for Distribution

Before submitting anywhere, you need to clean up your code.

Remove all hardcoded API keys. Use environment variables or a config file that users set up themselves.

```python
import os
from pathlib import Path
import json

def load_config():
 """Load user configuration from a local file."""
 config_path = Path.home() / '.behike_plugins' / 'config.json'

 if config_path.exists():
 with open(config_path) as f:
 return json.load(f)

 # Return defaults if no config file
 return {
 'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
 'default_scale': 'major',
 'default_octave': 4,
 }
```

Write a README. Include: what the plugin does, how to install it (the Hardware directory path), what Python packages it requires, and your contact or support email.

Write an install script. A simple `.bat` on Windows or `.sh` on macOS that copies the folder to the correct directory.

```bash
#!/bin/bash
# install.sh for macOS
DEST="$HOME/Documents/Image-Line/FL Studio/Settings/Hardware/AIPluginGuide_MelodyGen"
mkdir -p "$DEST"
cp -r . "$DEST"
echo "Installed. Open FL Studio and go to MIDI Settings to activate."
```

### Plugin Boutique Submission

Plugin Boutique is the largest marketplace for music production plugins. Their process is manual and takes one to four weeks.

Requirements:
- Working plugin (they test it)
- Product page assets: cover image minimum 800x800px, description, feature list
- Pricing set by you, 70% revenue share back to you
- Demo audio or video recommended, not required for MIDI tools

Go to pluginboutique.com/sell. Create a developer account. Submit your plugin via their form. The review process involves their team testing installation and functionality on Windows and Mac.

Key things that cause rejections: installer does not work, plugin crashes FL Studio on load, no documentation.

### Gumroad Setup

Gumroad is faster to set up. You can be selling within an hour.

Create an account at gumroad.com. Add a new product. Upload your zip file containing the plugin folder, README, and install script. Set your price. Add a cover image.

Gumroad handles payment processing, file delivery, and VAT collection for EU customers. Their fee is 10% plus Stripe's payment processing fee.

Use Gumroad for direct sales where you want to build an email list. Every buyer email goes into your Gumroad dashboard. That is your audience for announcing new plugins.

### Splice

Splice has a separate creator program for plugin developers. It works differently from Plugin Boutique. Splice is subscription-based: users pay a monthly fee and get credits to download plugins. You earn per download based on your plugin's credit price.

The application process is at splice.com/creators. Splice is more selective than Plugin Boutique and tends to favor plugins with a distinctive sound or workflow.

Worth applying to after you have sales history on Plugin Boutique. Use those sales numbers in your Splice application.

### Pricing Strategy

The AI angle justifies higher prices. Producers pay $29-99 for tools that save them time.

Price for value, not for effort. A melody generator that saves a producer 30 minutes of work is worth $29 even if it took you two weeks to build. Price based on the outcome for the buyer.

The bundle strategy works well for plugins. Sell each plugin individually, then offer a bundle at a discount. Four plugins at $29 each is $116. Bundle at $79 moves more volume and introduces buyers to your full catalog.

---

## Chapter 8: What Comes Next

MIDI scripts are a starting point. If this works for you, here is the natural progression.

### VST3 with JUCE

JUCE is the most widely used framework for building audio plugins. It is C++ based. The learning curve is real. But a VST3 plugin built with JUCE can do what MIDI scripts cannot: process audio in real time, integrate into every DAW, and behave like a first-class plugin.

The path: learn C++ basics, go through the JUCE tutorials (their documentation is excellent), then rebuild one of your MIDI tools as a JUCE plugin. The Projucer tool handles the project setup.

JUCE plugins run on Windows, macOS, iOS, Android, and Linux. They export as VST3, AU (macOS), AAX (Pro Tools), and LV2.

### Standalone Applications

Some of the analysis tools from this guide (mastering helper, mixing assistant) work better as standalone apps than as plugins. A standalone Python app with a simple GUI using tkinter or PyQt can run outside FL Studio, accept audio files, and generate reports.

The advantage: you are not limited to FL Studio users. Any producer with a rendered audio file is a potential customer.

Tools like PyInstaller package Python apps into distributable executables. You can ship a standalone Windows or macOS app without requiring users to install Python.

### Mobile

The chord progression and melody generator are good candidates for mobile. Music producers use their phones to capture ideas. A simple iOS or Android app that generates MIDI patterns and exports to the clipboard or a file would cover a different use case than the desktop plugin.

React Native with a MIDI output library, or Swift for iOS-native. The LLM backend is the same. You are just building a different UI.

### Building a Plugin Catalog

The strongest position is not one plugin. It is a branded catalog. Producers who trust one tool from you are the most likely buyers for the next one.

Keep a changelog. Update your plugins when FL Studio updates. Reply to every review on Plugin Boutique in the first 30 days. Build a mailing list through Gumroad. Announce new plugins to your existing buyers before listing them publicly.

This is the same playbook as any digital product business. The music production niche just has lower competition and buyers who spend money consistently.

---

## Appendix: MIDI Protocol Cheat Sheet

| Concept | Value | Notes |
|---------|-------|-------|
| Middle C | 60 | C4 in standard notation |
| One octave | 12 semitones | |
| Note On status byte | 0x90 (144) | Add channel number (0-15) |
| Note Off status byte | 0x80 (128) | Add channel number |
| CC status byte | 0xB0 (176) | Add channel number |
| Max velocity | 127 | |
| FL Studio PPQ | 96 | Ticks per quarter note |
| One bar (4/4) | 384 ticks | 4 beats x 96 PPQ |
| Quarter note | 96 ticks | |
| Eighth note | 48 ticks | |
| Sixteenth note | 24 ticks | |

## Appendix: Plugin Boutique Submission Checklist

- Plugin folder with correct naming convention (`device_[name].py`)
- README with installation instructions for Windows and macOS
- Install script (`.bat` for Windows, `.sh` for macOS)
- Cover image, 800x800px minimum, PNG
- Product description (200-500 words)
- Feature list (bullet points)
- System requirements listed (FL Studio version, Python version if relevant)
- Tested on Windows 10/11
- Tested on macOS 12+
- No hardcoded API keys
- Config file or environment variable setup documented
- Pricing decided before submission

---

*Built by Kalani Andre Gomez Padin. Behike, 2026. behikeai.gumroad.com*
