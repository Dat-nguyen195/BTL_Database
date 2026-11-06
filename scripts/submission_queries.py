from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def queries():
    statements=[]
    for name in ('01_operations.sql','02_reports.sql'):
        text='\n'.join(l for l in (ROOT/'database/05_queries'/name).read_text().splitlines() if not l.strip().startswith('--'))
        statements.extend(s.strip() for s in text.split(';') if s.strip())
    return {f'Q-P12-{i:02d}':s+';' for i,s in enumerate(statements,1)}
