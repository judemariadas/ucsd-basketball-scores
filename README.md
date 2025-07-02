# UCSD Basketball XML to Smartabase CSV Converter

This script parses Genius Sports basketball XML game data and exports performance statistics **only for UCSD players** in a format compatible with Smartabase.

## Features

- Extracts detailed player stats from XML.
- Filters output to include only UC San Diego players (team name must match exactly).
- Outputs CSV with Smartabase-importable format.
- Fully CLI-based, no GUI dependencies.

## Prerequisites

- Python 3.7 or higher
- `pandas` package

Install dependencies with:

```bash
pip install -r requirements.txt