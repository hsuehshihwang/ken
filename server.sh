#!/bin/bash

PIDFILE="/tmp/english-server.pid"
LOGFILE="/tmp/english-server.log"
HOST="0.0.0.0"
PORT="8899"
DIR="$(cd "$(dirname "$0")" && pwd)"

start() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Server already running (PID: $(cat "$PIDFILE"))"
        return 1
    fi
    echo "Starting server on $HOST:$PORT..."
    cd "$DIR"
    nohup python3 -m http.server "$PORT" > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    sleep 1
    if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Server started (PID: $(cat "$PIDFILE"))"
        echo "URL: http://localhost:$PORT/"
    else
        echo "Failed to start server"
        cat "$LOGFILE"
        rm -f "$PIDFILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        echo "Server not running"
        return 1
    fi
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill "$PID"
        sleep 1
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID"
        fi
        rm -f "$PIDFILE"
        echo "Server stopped"
    else
        echo "Server not running (stale PID file)"
        rm -f "$PIDFILE"
    fi
}

restart() {
    stop
    sleep 1
    start
}

status() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Server running (PID: $(cat "$PIDFILE"))"
        echo "URL: http://localhost:$PORT/"
        return 0
    else
        echo "Server not running"
        return 1
    fi
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    restart) restart ;;
    status)  status ;;
    *)       echo "Usage: $0 {start|stop|restart|status}" ;;
esac
