"""Optional index bootstrap; run after docker compose up -d and sample generation."""
from pathlib import Path
from logcore import read_log_files
from opensearch_client import index_records

if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    records=read_log_files(root/'sample_logs')
    print('Indexed',index_records(records),'synthetic events in OpenSearch')
