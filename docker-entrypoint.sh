#!/bin/sh

set -e

# Wait for mysql and redis both to be alive 
wait-for-it "mysql:3306
wait-for-it "redis:6379

# Run the main container command.
nohup python3 app.py  &
nohup streamlit run --theme.base light --server.port 5001 --server.headless true frontend.py &
nohup streamlit run --theme.base light --server.port 5002 --server.headless true chat.py
