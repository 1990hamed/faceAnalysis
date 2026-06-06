# Face Analysis — سیستم تحلیل چهره

A desktop application that analyses facial features (eyebrows, lips, nose) and maps them to personality archetypes drawn from Greek mythology and Jungian psychology. Results are presented in-app and exported as a Persian-language PDF report.

## Features

- **Facial feature input** — select eyebrow, lip, and nose types via a guided GUI
- **Archetype matching** — cross-references feature selections against seven archetypes (Persephone, Demeter, Athena, Aphrodite, Hestia, Artemis, Hera / their male counterparts)
- **Psychology method mapping** — each archetype maps to a therapeutic approach (e.g. psychoanalysis, Adlerian, CBT, Gestalt)
- **PDF report generation** — RTL Persian report produced with ReportLab and Vazirmatn font
- **MediaPipe integration** — optional landmark-based face mesh analysis via MediaPipe

## Requirements

- Python ≥ 3.13
- [`uv`](https://docs.astral.sh/uv/) package manager

## Installation

```bash
git clone https://github.com/1990hamed/faceAnalysis.git
cd faceAnalysis
uv sync
```

## Usage

```bash
uv run python main.py
```

## Project Structure

```
faceAnalysis/
├── main.py                   # Entry point — bootstraps the Tkinter GUI
├── src/face_analysis/
│   ├── config/               # Archetype definitions and feature weight tables
│   ├── core/                 # Analysis logic and PDF generation
│   ├── vision/               # MediaPipe face-mesh utilities
│   └── gui/                  # Tkinter pages, widgets, and theme
├── Font/                     # Vazirmatn font family (RTL support)
├── data/                     # Sample images and reference documents
└── tests/                    # pytest test suite
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix . && uv run ruff format .
```

## License

MIT — see [LICENSE](LICENSE).
