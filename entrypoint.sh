#!/usr/bin/env bash
set -e

# Configuration defaults (can be overridden via environment variables in docker-compose)
CHANNEL="${DAB_CHANNEL:-7D}"
GAIN="${DAB_GAIN:-25.4}"
WELLE_PORT="${DAB_PORT:-8008}"
APP_PORT="${DAB_APP_PORT:-8009}"
DRIVER="${DAB_DRIVER:-auto}"

echo "[+] Starting welle-cli on channel ${CHANNEL} with gain ${GAIN}..."

# Launch welle-cli in web server mode in the background
# -c: DAB channel
# -g: RF gain
# -w: Web server port
# -D: Decode all programmes/streams on the multiplex
# -P: Cycle programmes until DLS & MOT slide are decoded
#welle-cli -c "${CHANNEL}" -g "${GAIN}" -w "${WELLE_PORT}" -F "${DRIVER}" -D -P &
welle-cli -c "${CHANNEL}" -g "${GAIN}" -w "${WELLE_PORT}" -F "${DRIVER}" -g 1 -D &

# Save the PID for process management
WELLE_PID=$!

echo "[+] welle-cli started with PID ${WELLE_PID}"

echo "[+] Serving app/index.html dashboard on port ${APP_PORT}..."
exec python3 /app/server.py

