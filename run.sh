#!/bin/bash

# Start health check server in background
python3 -m http.server 8080 &

# Start telegram bot
python3 telegram_bot.py
