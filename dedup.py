import argparse, hashlib, os, stat, tempfile
from pathlib import Path

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.digest()

def equal(a,b):
    with a.open('rb') as x, b.open('rb') as y:
        while True:
            u,v=x.read(1048576),y.read(1048576)
            if u != v: return False
            if not u: return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('directory',type=Path); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    seen={}; saved=0
    for p in sorted(args.directory.rglob('*')):
        if p.is_symlink() or not p.is_file(): continue
        s=p.stat(); key=(s.st_dev,s.st_size,stat.S_IMODE(s.st_mode),s.st_uid,s.st_gid,digest(p))
        first=seen.get(key)
        if first is None: seen[key]=p; continue
        if os.path.samefile(first,p) or not equal(first,p): continue
        # Existing external hard links would keep the old inode alive.
        gain=s.st_blocks*512 if s.st_nlink==1 else 0
        print(f'{p} -> {first}: {gain} bytes potentially saved')
        if args.apply:
            with tempfile.TemporaryDirectory(dir=p.parent) as tmp:
                link=Path(tmp)/'link'; os.link(first,link); os.replace(link,p)
        saved+=gain
    print(f'{"Estimated freed" if args.apply else "Potential"} allocated bytes: {saved}')
if __name__=='__main__': main()
