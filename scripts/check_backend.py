"""Read-only readiness check; uses the restricted configured application account."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps/backend'))
from src.db import get_db_connection
from src.repositories.core import one

if __name__=='__main__':
    conn=get_db_connection()
    try:
        details=one(conn,'SELECT VERSION() AS version,DATABASE() AS db,CURRENT_USER() AS runtime_user,@@session.time_zone AS time_zone,@@session.transaction_isolation AS isolation_level')
        details['tables']=one(conn,'SELECT COUNT(*) AS n FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()')['n']
        details['procedures']=one(conn,"SELECT COUNT(*) AS n FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=DATABASE() AND ROUTINE_TYPE='PROCEDURE'")['n']
        if details['tables'] != 23 or details['procedures'] < 8:
            raise RuntimeError('Incomplete backend schema/routines')
        print(json.dumps(details,ensure_ascii=False,indent=2))
    finally:conn.close()
