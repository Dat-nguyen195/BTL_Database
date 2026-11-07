from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil, re

root = Path(__file__).resolve().parents[1]
target = root / 'docs/report/latex/assets/eer'

with sync_playwright() as p:
    b = p.chromium.launch(
        executable_path=shutil.which('google-chrome') or shutil.which('chromium'),
        headless=True,
        args=['--no-sandbox']
    )
    page = b.new_page()
    for name in ['erd_full_vector']:
        text = (target / (name + '.svg')).read_text()
        a = re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', text)
        w, h = map(float, a.groups())
        page.set_content(
            f'<html><style>@page{{size:{w}pt {h}pt;margin:0}}html,body{{margin:0;padding:0;width:{w}pt;height:{h}pt}}svg{{display:block;width:{w}pt;height:{h}pt}}</style>{text}'
        )
        page.pdf(
            path=str(target / (name + '.pdf')),
            width=f'{w/72}in',
            height=f'{h/72}in',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        print(f'Exported {name}: width={w}pt, height={h}pt')
    b.close()
