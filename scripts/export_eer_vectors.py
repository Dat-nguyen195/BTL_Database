from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil,re
root=Path(__file__).resolve().parents[1]
target=root/'docs/report/latex/assets/eer'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=b.new_page()
 for name in ['erd_full_vector','eerd_sub_user','eerd_sub_workstation','eerd_sub_wallet','eerd_sub_shift','eerd_sub_service_inventory','eerd_sub_inventory']:
  text=(target/(name+'.svg')).read_text();a=re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"',text);w,h=map(float,a.groups())
  page.set_content('<html><style>@page{size:'+str(w)+'pt '+str(h)+'pt;margin:0}html,body{margin:0;padding:0;width:'+str(w)+'pt;height:'+str(h)+'pt}svg{display:block;width:'+str(w)+'pt;height:'+str(h)+'pt}</style>'+text)
  page.pdf(path=str(target/(name+'.pdf')),width=str(w/72)+'in',height=str(h/72)+'in',print_background=True,margin={'top':'0','right':'0','bottom':'0','left':'0'})
  print(name,w,h)
 b.close()
