
#! /bin/bash

## run any setup steps or pre-processing tasks here
echo "starting hospital RAG based FASTAPI service using Graph db ..."

## Start the main application
uvicorn main:app --host 0.0.0.0 --port 8000