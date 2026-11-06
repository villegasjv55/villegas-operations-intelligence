#!/usr/bin/env bash
# One command to set up (first time only) and launch Villegas Operations Intelligence.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating the virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "Checking packages..."
pip install -q -r requirements.txt

if [ ! -f "data/olist.db" ]; then
  mkdir -p data/raw
  if [ "$(ls data/raw/*.csv 2>/dev/null | wc -l)" -lt 9 ]; then
    echo ""
    echo "The data files are missing. Download the free Olist dataset from:"
    echo "  https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
    echo "Unzip the 9 CSV files into data/raw/ and run ./run.sh again."
    exit 1
  fi
  echo "Building the database (first time only, about 30 seconds)..."
  python src/data_loader.py
  python -m src.cleaning
fi

echo "Starting the app at http://localhost:8501"
streamlit run app.py
