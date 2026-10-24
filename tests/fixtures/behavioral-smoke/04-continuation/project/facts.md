# Confirmed Architecture Facts

## 1. Pipeline Topology
- Local Gateway: Listens on `127.0.0.1:8080`. Ingests raw text payloads via HTTP POST `/ingest`.
- Worker Engine: Processes queued text, strips non-ASCII characters, and normalizes casing to lowercase.
- Persistent Store: Appends normalized records to a local append-only JSON file (`data/records.json`).

## 2. Security Boundaries
- Network interface: Loopback interface binding only (`127.0.0.1`). Zero external network exposure.
- Storage security: File permissions restricted to the local operating system user (mode `0600`).
- Privilege level: Unprivileged execution; no root or administrative access required.

## 3. Pending Items
- Open decisions: None. All architectural parameters are verified and finalized.
