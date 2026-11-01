"""Create deterministic, synthetic Cassandra-format logs; no actual Cassandra cluster."""
from pathlib import Path
from datetime import datetime, timedelta
import random
import argparse

EVENTS = [
    ('INFO','StorageService.java:775','Node joined token ring; gossip state synchronized'),
    ('INFO','CompactionManager.java:426','Compaction completed for keyspace animation_assets'),
    ('WARN','ReadTimeoutException.java:88','Read timeout at consistency LOCAL_QUORUM; tracing request'),
    ('ERROR','StorageProxy.java:2212','UnavailableException: required 2 replicas but only 1 alive'),
    ('INFO','CommitLog.java:177','Commit log segment recycled successfully'),
    ('WARN','GCInspector.java:190','GC pause exceeded threshold 250ms'),
    ('ERROR','HintsService.java:310','Failed to dispatch hints to replica; retry scheduled'),
    ('DEBUG','MessagingService.java:890','Outbound connection pool refreshed'),
]

def generate(folder: Path, count: int = 60) -> None:
    random.seed(7)
    folder.mkdir(parents=True,exist_ok=True)
    start=datetime(2026,10,31,15,0,0)
    for node_idx in range(1,4):
        lines=[]
        for i in range(count):
            level, source, message=random.choices(EVENTS, weights=[14,10,5,3,10,5,3,8],k=1)[0]
            stamp=(start+timedelta(seconds=i*19+node_idx*7)).strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            lines.append(f'{level}  [MessagingService-{node_idx}] {stamp} {source} - {message}')
        (folder/f'cassandra-node-{node_idx}.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Generated {count*3} synthetic events across 3 nodes in {folder}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',default='sample_logs'); parser.add_argument('--per-node',type=int,default=60)
    args=parser.parse_args(); generate(Path(args.out),args.per_node)
