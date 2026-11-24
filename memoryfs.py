#!/usr/bin/env python3
import errno, os, stat, sys, time
from fuse import FUSE, FuseOSError, Operations

class MemoryFS(Operations):
    def __init__(self):
        self.files={}; self.versions={}; self.uid=os.getuid(); self.gid=os.getgid()
    def getattr(self,path,fh=None):
        if path=='/':
            return dict(st_mode=stat.S_IFDIR|0o755,st_nlink=2,st_uid=self.uid,st_gid=self.gid)
        if path not in self.files: raise FuseOSError(errno.ENOENT)
        data,attrs=self.files[path]; return dict(attrs,st_size=len(data))
    def readdir(self,path,fh):
        return ['.','..']+[p[1:] for p in self.files]
    def create(self,path,mode,fi=None):
        if path in self.files: raise FuseOSError(errno.EEXIST)
        if '/' in path[1:]: raise FuseOSError(errno.ENOENT)
        now=time.time(); self.files[path]=(bytearray(),dict(st_mode=stat.S_IFREG|mode,st_nlink=1,st_uid=self.uid,st_gid=self.gid,st_atime=now,st_mtime=now,st_ctime=now)); return 0
    def open(self,path,flags):
        self.getattr(path); return 0
    def read(self,path,size,offset,fh):
        self.getattr(path); return bytes(self.files[path][0][offset:offset+size])
    def snapshot(self,path):
        data,attrs=self.files[path]; n=self.versions.get(path,0)+1
        while f'{path}.v{n}' in self.files: n+=1
        self.versions[path]=n; self.files[f'{path}.v{n}']=(bytearray(data),dict(attrs,st_mode=stat.S_IFREG|0o444))
    def mutable(self,path):
        self.getattr(path)
        if not self.files[path][1]['st_mode'] & 0o222: raise FuseOSError(errno.EACCES)
        return self.files[path]
    def write(self,path,data,offset,fh):
        buf,attrs=self.mutable(path)
        if buf: self.snapshot(path)
        if offset+len(data)>len(buf): buf.extend(b'\0'*(offset+len(data)-len(buf)))
        buf[offset:offset+len(data)]=data; attrs['st_mtime']=attrs['st_ctime']=time.time(); return len(data)
    def truncate(self,path,length,fh=None):
        buf,attrs=self.mutable(path)
        if length!=len(buf) and buf: self.snapshot(path)
        if length<len(buf): del buf[length:]
        else: buf.extend(b'\0'*(length-len(buf)))
        attrs['st_mtime']=attrs['st_ctime']=time.time()
    def unlink(self,path):
        self.getattr(path); del self.files[path]
    def utimens(self,path,times=None):
        _,attrs=self.mutable(path); attrs['st_atime'],attrs['st_mtime']=times or (time.time(),)*2
    def statfs(self,path):
        return dict(f_bsize=4096,f_frsize=4096,f_blocks=262144,f_bfree=262144,f_bavail=262144,f_files=100000,f_ffree=100000)
if __name__=='__main__':
    FUSE(MemoryFS(),sys.argv[1],foreground=True,nothreads=True,default_permissions=True)
