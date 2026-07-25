.PHONY: run

HOST ?= 0.0.0.0
PORT ?= 5000

run:
	uv run uvicorn main:app --host $(HOST) --port $(PORT)