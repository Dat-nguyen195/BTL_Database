"""Đóng gói bản nộp, kiểm tra bí mật và hash từng tệp trước khi bàn giao."""
from pathlib import Path
import hashlib,os,zipfile
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
OUTPUT_ZIP=ROOT/'deliverables/BTL2_L09_Nhom10_BanGiao.zip'
EXCLUDE_DIRS={'.git','.venv','__pycache__','.pytest_cache','.idea','.vscode','.agents','.aws','.codex','tmp','node_modules'}
def should_include(p):
    return (
        not any(s in EXCLUDE_DIRS or s == 'build' for s in p.parts)
        and not (p.name.startswith('.env') and p.name != '.env.example')
        and p.name not in {'.DS_Store','Thumbs.db'}
        and p != Path('deliverables/SHA256SUMS')
        and p.suffix not in {'.pyc','.pyo','.pyd','.zip','.tmp','.aux','.log','.out','.toc','.lof','.lot','.fls','.fdb_latexmk','.xdv'}
        and not p.name.endswith('.synctex.gz')
    )

def make_archive(output, files, prefix):
    hashes=[hashlib.sha256(data).hexdigest()+'  '+str(rel) for rel,data in files]
    temp=output.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel,data in files:z.writestr(prefix+str(rel),data)
        z.writestr(prefix+'MANIFEST.sha256','\n'.join(hashes)+'\n')
    with zipfile.ZipFile(temp) as z:
        if z.testzip():raise RuntimeError('ZIP corrupt: '+output.name)
        for rel,data in files:
            if z.read(prefix+str(rel))!=data:raise RuntimeError('ZIP mismatch: '+str(rel))
    os.replace(temp,output)
def package():
    secret_values=[v.encode() for k,v in dotenv_values(ROOT/'.env').items() if v and len(v)>=16 and any(t in k for t in ['PASSWORD','SECRET','TOKEN'])]
    files=[]
    for path in sorted(ROOT.rglob('*')):
        rel=path.relative_to(ROOT)
        if not path.is_file() or not should_include(rel):continue
        data=path.read_bytes();check=[data]
        if path.suffix=='.docx':
            with zipfile.ZipFile(path) as z:check.extend(z.read(n) for n in z.namelist() if n.endswith('.xml'))
        if any(secret in content for secret in secret_values for content in check):raise RuntimeError('Phát hiện bí mật cấu hình trong '+str(rel))
        files.append((rel,data))
    OUTPUT_ZIP.parent.mkdir(exist_ok=True)
    latex_root=Path('docs/report/latex')
    latex_files=[(p.relative_to(latex_root),d) for p,d in files if p.is_relative_to(latex_root)]
    if not any(p == Path('main.tex') for p,_ in latex_files):
        raise RuntimeError('Missing main.tex')
    if not (ROOT/'deliverables/BTL2_L09_Nhom10_P1_P2.pdf').is_file():
        raise RuntimeError('Build the report PDF before packaging')
    make_archive(ROOT/'deliverables/BTL2_L09_Nhom10_LaTeX.zip',latex_files,'BTL2_L09_Nhom10_LaTeX/')
    make_archive(OUTPUT_ZIP,files,'BTL2_L09_Nhom10/')
    final=[ROOT/'deliverables/BTL2_L09_Nhom10_P1_P2.pdf',ROOT/'deliverables/BTL2_L09_Nhom10_LaTeX.zip',OUTPUT_ZIP]
    (ROOT/'deliverables/SHA256SUMS').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in final)+'\n')
    print('ZIP verified:',len(files),'files; no configured secrets; manifest included.')
if __name__=='__main__':package()
