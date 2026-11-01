"""Small single-user dashboard for Cassandra-style distributed logs."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logcore import initialize, insert, query, read_log_files

ROOT=Path(__file__).resolve().parent.parent
HTML=(ROOT/'dashboard.html').read_bytes()

def run(db_path, port, backend):
    initialize(db_path)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=urlparse(self.path)
            if path.path=='/':
                self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(HTML)
            elif path.path=='/api/logs':
                p=parse_qs(path.query)
                fields={k:p.get(k,[''])[0] for k in ('level','node','q')}
                try:
                    if backend=='opensearch':
                        from opensearch_client import search_records
                        data=search_records(**fields)
                    else: data=query(db_path,**fields)
                    payload=json.dumps({'count':len(data),'logs':data}).encode()
                    self.send_response(200)
                except Exception as e:
                    payload=json.dumps({'error':str(e)}).encode(); self.send_response(503)
                self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(payload)
            else: self.send_error(404)
    print(f'Dashboard: http://localhost:{port} | backend={backend}')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--db',default=str(ROOT/'logs.db'))
    parser.add_argument('--backend',choices=('sqlite','opensearch'),default='sqlite')
    parser.add_argument('--load',action='store_true',help='Load sample .log files into SQLite')
    args=parser.parse_args()
    if args.load:
        initialize(args.db); print('Inserted',insert(args.db,read_log_files(ROOT/'sample_logs')),'events')
    run(args.db,args.port,args.backend)
