#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Current Python Version:"
python --version

# Install dependencies
pip install -r requirements.txt

# Download TextBlob/NLTK corpora for AI analysis
export NLTK_DATA=/opt/render/nltk_data
python -m textblob.download_corpora
python -c "import nltk; nltk.download('punkt_tab', download_dir='/opt/render/nltk_data')"
