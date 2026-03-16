# Image References

Image paths and descriptions saved here so visual context survives across sessions.

## Format
- `IMAGES_{date}_{topic}.md` — image paths + descriptions of what they show

## Limitation
Claude Code can't persist actual image data between sessions, but we CAN:
1. Save file paths to images on disk
2. Save descriptions of what each image shows
3. Re-read images at session start using the paths

## Usage
At session start, Ceiba reads the latest image reference file and re-loads any images needed.
