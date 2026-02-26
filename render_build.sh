#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora for AI analysis
python -m textblob.download_corpora
