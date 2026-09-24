"""Static release checks. Run: python scripts/validate.py"""
from pathlib import Path
from html.parser import HTMLParser
import base64
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parent.parent
class Audit(HTMLParser):
 def __init__(self): super().__init__();self.scripts=[];self.styles=[];self.ids=[];self.anchors=[];self.local=[];self.external=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='script':self.scripts.append(a.get('src'))
  if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a.get('href'))
  if tag=='img':self.images.append(a)
  for key in ('src','poster'):
   if a.get(key) and not a[key].startswith(('http','data:')):self.local.append(a[key])
  if tag=='a':
   if a.get('href','').startswith('#'):self.anchors.append(a['href'][1:])
   if a.get('href','').startswith('http'):self.external.append(a)
html=(ROOT/'index.html').read_text(encoding='utf-8');a=Audit();a.feed(html)
script=(ROOT/'script.js').read_text(encoding='utf-8')
css=(ROOT/'styles.css').read_text(encoding='utf-8')
assert a.scripts==['script.js'],a.scripts
assert a.styles==['styles.css'],a.styles
assert sorted(p.name for p in ROOT.glob('*.js'))==['script.js']
assert sorted(p.name for p in ROOT.glob('*.css'))==['styles.css']
assert len(a.ids)==len(set(a.ids))
assert all(x in a.ids for x in a.anchors)
assert all((ROOT/x).is_file() for x in a.local)
assert all(x.get('target')=='_blank' and 'noopener' in x.get('rel','') for x in a.external)
assert all(x.get('alt') is not None for x in a.images)
assert all(x in a.ids for x in ['gig','suvinil','acelerai','eletromidia','inter'])
assert html.count('class="gallery-item"')==8
assert html.count('class="work-card"')==8
assert 'class="grain"' not in html and 'class="cursor"' not in html
assert 'https://www.instagram.com/nexya.tech/' in html
assert 'Explorar o arquivo original' not in html
assert 'ENRICO ROCHA' in html and 'MIASCOVSKY' in html
assert not any(0x2190<=ord(c)<=0x27bf or 0x1f000<=ord(c)<=0x1ffff for c in html+css+(ROOT/'README.md').read_text(encoding='utf-8'))
assert 'type="module"' not in html and 'import(' not in script
assert 'textureURL(src)' in script and 'await fileVideoReady' in script
assert all(token not in html+css+script for token in ('C:\\Users\\','file:///','localhost','127.0.0.1'))
assert '\u25b6' not in html+script
assert (ROOT/'assets/vendor/THREE-LICENSE.txt').is_file()
assert not list((ROOT/'assets/vendor').glob('*.js'))
video_data=ROOT/'assets/enrico/file-media-data.js'
assert video_data.is_file()
media_data=video_data.read_text(encoding='ascii')
textures=json.loads(media_data.split('window.__ENRICO_FILE_TEXTURES__=',1)[1].split(';\nwindow.__ENRICO_FILE_VIDEO_BASE64__',1)[0])
for image in (ROOT/'assets/enrico').rglob('*'):
 if image.suffix not in ('.webp','.jpg'): continue
 encoded_image=textures[image.relative_to(ROOT).as_posix()].split(',',1)[1]
 assert hashlib.sha256(base64.b64decode(encoded_image)).digest()==hashlib.sha256(image.read_bytes()).digest()
encoded=media_data.split('window.__ENRICO_FILE_VIDEO_BASE64__="',1)[1].split('";',1)[0]
assert hashlib.sha256(base64.b64decode(encoded)).digest()==hashlib.sha256((ROOT/'assets/enrico/gig/gig-manifesto-web.mp4').read_bytes()).digest()
assert 'file-media-data.js' in script and "location.protocol!=='file:'" in script
assert not list(ROOT.glob('.*-v*.css')) and not list(ROOT.glob('.*-v*.js'))
subprocess.run(['node','--check',str(ROOT/'script.js')],check=True)
print('PASS: one CSS and one JS entry; 5 cases, 8 photos, 8 previews; local assets, anchors, safe links and JS syntax.')
