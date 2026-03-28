#!/usr/bin/env python3
"""
OpenSage HTTP API - Simple REST API for OpenSage memory.

Environment:
  NEO4J_URI       (default: bolt://127.0.0.1:7687)
  NEO4J_USER      (default: neo4j)
  NEO4J_PASSWORD  (required)
  OPENSAGE_API_PORT (default: 5555)

Run: python opensage_api.py
Then use: http://localhost:5555/
"""

import json
import logging
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")


def get_driver():
    if not NEO4J_PASSWORD:
        raise RuntimeError(
            "NEO4J_PASSWORD is not set. Export it or use a .env file (see .env.example)."
        )
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/remember":
            key = query.get("key", [""])[0]
            value = query.get("value", [""])[0]
            if key and value:
                try:
                    with get_driver() as driver:
                        with driver.session() as session:
                            session.run(
                                "MERGE (m:Memory {key: $key}) SET m.value = $value, m.updated = timestamp()",
                                key=key,
                                value=value,
                            )
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok", "key": key}).encode())
                except Exception as e:
                    logger.exception("Error handling /remember")
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                self.send_response(400)
                self.end_headers()

        elif path == "/recall":
            key = query.get("key", [""])[0]
            if key:
                try:
                    with get_driver() as driver:
                        with driver.session() as session:
                            result = session.run(
                                "MATCH (m:Memory {key: $key}) RETURN m.value as value",
                                key=key,
                            )
                            records = list(result)
                            value = (
                                records[0]["value"]
                                if records and records[0]["value"]
                                else None
                            )
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"key": key, "value": value}).encode())
                except Exception as e:
                    logger.exception("Error handling /recall")
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                self.send_response(400)
                self.end_headers()

        elif path == "/list":
            try:
                with get_driver() as driver:
                    with driver.session() as session:
                        result = session.run(
                            "MATCH (m:Memory) RETURN m.key as key, m.value as value ORDER BY m.updated DESC"
                        )
                        memories = [
                            {"key": r["key"], "value": r["value"]} for r in result
                        ]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(memories).encode())
            except Exception as e:
                logger.exception("Error handling /list")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif path == "/search":
            q = query.get("q", [""])[0]
            if q:
                with get_driver() as driver:
                    with driver.session() as session:
                        result = session.run(
                            "MATCH (m:Memory) WHERE m.value CONTAINS $q OR m.key CONTAINS $q RETURN m.key as key, m.value as value",
                            q=q,
                        )
                        memories = [
                            {"key": r["key"], "value": r["value"]} for r in result
                        ]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(memories).encode())
            else:
                self.send_response(400)
                self.end_headers()
        elif path == "/health":
            try:
                with get_driver() as driver:
                    with driver.session() as session:
                        session.run("RETURN 1")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                logger.exception("Health check failed")
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "fail", "error": str(e)}).encode()
                )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging


if __name__ == "__main__":
    if not NEO4J_PASSWORD:
        print(
            "Error: NEO4J_PASSWORD is not set. Copy .env.example to .env, set NEO4J_PASSWORD, "
            "or export it in your shell.",
            file=sys.stderr,
        )
        sys.exit(1)
    port = int(os.environ.get("OPENSAGE_API_PORT", "5555"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"OpenSage API: http://localhost:{port}")
    print("Endpoints:")
    print(f"  GET /remember?key=<key>&value=<value>")
    print(f"  GET /recall?key=<key>")
    print(f"  GET /list")
    print(f"  GET /search?q=<query>")
    server.serve_forever()
