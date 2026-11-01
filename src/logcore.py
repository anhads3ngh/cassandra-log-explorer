"""Parser, persistence, and filters for simulated Cassandra-node logs."""
from __future__ import annotations
import json
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

PATTERN = re.compile(r'^(?P<level>TRACE|DEBUG|INFO|WARN|ERROR)\s+\[(?P<thread>[^]]+)\]\s+(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+(?P<source>[^ ]+)\s+-\s+(?P<message>.*)$')

@dataclass
class Record:
    timestamp: str
    level: str
    node: str
    thread: str
    source: str
    message: str


def parse_line(line: str, node: str) -> Record | None:
    m = PATTERN.match(line.strip())
    if not m:
        return None
    d = m.groupdict()
    ts = datetime.strptime(d['time'], '%Y-%m-%d %H:%M:%S,%f').replace(tzinfo=timezone.utc)
    return Record(timestamp=ts.isoformat(timespec='milliseconds'), level=d['level'], node=node,
                  thread=d['thread'], source=d['source'], message=d['message'])


def initialize(db_path: str | Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL, level TEXT NOT NULL, node TEXT NOT NULL,
            thread TEXT NOT NULL, source TEXT NOT NULL, message TEXT NOT NULL
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS ix_logs_lookup ON logs (timestamp, level, node)')


def insert(db_path: str | Path, records: list[Record]) -> int:
    with sqlite3.connect(db_path) as conn:
        conn.executemany('''INSERT INTO logs (timestamp,level,node,thread,source,message)
            VALUES (:timestamp,:level,:node,:thread,:source,:message)''', [asdict(r) for r in records])
    return len(records)


def query(db_path: str | Path, *, level: str = '', node: str = '', q: str = '', limit: int = 200) -> list[dict]:
    where, args = [], []
    if level:
        where.append('level = ?'); args.append(level)
    if node:
        where.append('node = ?'); args.append(node)
    if q:
        where.append('(message LIKE ? OR source LIKE ?)'); args.extend([f'%{q}%',f'%{q}%'])
    clause = ' WHERE ' + ' AND '.join(where) if where else ''
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT timestamp, level, node, thread, source, message FROM logs'
                            + clause + ' ORDER BY timestamp DESC, id DESC LIMIT ?', args + [max(1,min(limit,1000))])
        return [dict(r) for r in rows]


def read_log_files(folder: str | Path) -> list[Record]:
    items = []
    for path in sorted(Path(folder).glob('*.log')):
        for line in path.read_text(encoding='utf-8').splitlines():
            record = parse_line(line, path.stem)
            if record: items.append(record)
    return items
