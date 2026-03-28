#!/usr/bin/env python3
"""
OpenSage HTTP API - Simple REST API for OpenSage memory.

Run: python opensage_api.py
Then use: http://localhost:5555/
"""

import sys

sys.path.insert(0, "/Users/ghostgear/opensage/src")

from neo4j import GraphDatabase
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

import os

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def get_driver():
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
                with get_driver() as driver:
                    driver.execute_query(
                        "MERGE (m:Memory {key: $key}) SET m.value = $value, m.updated = timestamp()",
                        key=key,
                        value=value,
                    )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "key": key}).encode())
            else:
                self.send_response(400)
                self.end_headers()

        elif path == "/recall":
            key = query.get("key", [""])[0]
            if key:
                with get_driver() as driver:
                    result = driver.execute_query(
                        "MATCH (m:Memory {key: $key}) RETURN m.value as value", key=key
                    )
                    records = list(result.records)
                    value = (
                        records[0]["value"] if records and records[0]["value"] else None
                    )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"key": key, "value": value}).encode())
            else:
                self.send_response(400)
                self.end_headers()

        elif path == "/list":
            with get_driver() as driver:
                result = driver.execute_query(
                    "MATCH (m:Memory) RETURN m.key as key, m.value as value ORDER BY m.updated DESC"
                )
                memories = [
                    {"key": r["key"], "value": r["value"]} for r in result.records
                ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(memories).encode())

        elif path == "/search":
            q = query.get("q", [""])[0]
            if q:
                with get_driver() as driver:
                    result = driver.execute_query(
                        "MATCH (m:Memory) WHERE m.value CONTAINS $q OR m.key CONTAINS $q RETURN m.key as key, m.value as value",
                        q=q,
                    )
                    memories = [
                        {"key": r["key"], "value": r["value"]} for r in result.records
                    ]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(memories).encode())
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging


if __name__ == "__main__":
    port = 5555
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"OpenSage API: http://localhost:{port}")
    print("Endpoints:")
    print(f"  GET /remember?key=<key>&value=<value>")
    print(f"  GET /recall?key=<key>")
    print(f"  GET /list")
    print(f"  GET /search?q=<query>")
    server.serve_forever()
