import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from logcore import parse_line, initialize, insert, query

class LogCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name)/'logs.db'
    def tearDown(self): self.temp.cleanup()
    def test_parse(self):
        item=parse_line('WARN  [main] 2026-10-31 15:00:01,002 StorageService.java:44 - Read timeout','node-1')
        self.assertEqual(item.level,'WARN'); self.assertEqual(item.node,'node-1'); self.assertIn('2026-10-31T15:00:01.002',item.timestamp)
    def test_filters(self):
        a=parse_line('ERROR [main] 2026-10-31 15:00:01,002 x.java:1 - replica offline','node-1')
        b=parse_line('INFO [main] 2026-10-31 15:00:02,002 y.java:2 - online','node-2')
        initialize(self.db); insert(self.db,[a,b]); result=query(self.db,level='ERROR',node='node-1',q='replica')
        self.assertEqual(len(result),1); self.assertEqual(result[0]['message'],'replica offline')
        self.assertEqual(query(self.db,node='node-3'),[])
    def test_injection_is_parameterized(self):
        initialize(self.db)
        self.assertEqual(query(self.db,q="%' OR 1=1 --"),[])
if __name__=='__main__': unittest.main()
