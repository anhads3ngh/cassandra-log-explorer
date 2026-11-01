# Distributed Cassandra Log Explorer (Portfolio Prototype)

A small learning prototype that collects **synthetic Cassandra-format** log messages from three simulated nodes and lets engineers search by severity, node, or keyword. It has a local SQLite backend that works entirely with Python's standard library. An **optional** Dockerized OpenSearch service provides indexing and querying by REST API.

**Status and scope:** Created as a demonstration project. The logs are generated, not connected to a live Apache Cassandra cluster. OpenSearch integration is included, but depends on Docker availability and is not required to run the demo. This is not production software, and has no authentication, TLS, alerting, ingestion agents, or retention policies.

## Quick start: zero external packages

Requires Python 3.10+.

```bash
python src/generate_sample.py
python src/app.py --load
```

Open http://localhost:8080. Try searching `timeout`, or filtering `ERROR` and `cassandra-node-2`. Note that `--load` adds events each time you run it; omit the flag on subsequent runs.

## Optional: OpenSearch backend

Requires Docker with Compose. This deliberately binds the unauthenticated demo OpenSearch container to **127.0.0.1 only**; don't expose it publicly.

```bash
docker compose up -d
python src/index_opensearch.py
python src/app.py --backend opensearch --port 8081
```

Open http://localhost:8081. If OpenSearch is still starting, retry indexing after it's healthy. To stop: `docker compose down`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Structure

- `src/generate_sample.py`: deterministic synthetic Cassandra-style log generator for 3 nodes.
- `src/logcore.py`: regex parser, UTC timestamp conversion, parameterized SQLite queries.
- `src/opensearch_client.py`: OpenSearch REST mapping/indexing and filter/search.
- `src/app.py`: threaded local HTTP server + JSON endpoint `/api/logs`.
- `dashboard.html`: browser filter and results table; safe DOM text rendering.
- `docker-compose.yml`: optional single-node local OpenSearch service.

## Development next steps

Run a real Cassandra dev cluster, collect real `system.log` output, support multiline stack traces, add ingestion checkpoints and deduplication, add pagination and date-range filters, introduce role-based access/auth, and add alerting.
