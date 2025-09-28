#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
# запустить RQ worker
rq worker --url $REDIS_URL default
