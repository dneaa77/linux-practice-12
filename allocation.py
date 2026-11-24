# Each slot is a block; X denotes a block already occupied.
N=16
occupied={3,7,11,15}
size=4
free=[i for i in range(N) if i not in occupied]

def contiguous():
    for start in range(N-size+1):
        blocks=list(range(start,start+size))
        if not occupied.intersection(blocks): return blocks
    return None

def linked(): return free[:size]
def indexed(): return free[0],free[1:size+1]
def show(name,blocks):
    print(name, ''.join('X' if i in occupied else 'F' if i in blocks else '.' for i in range(N)))
print('Free blocks:', free)
c=contiguous(); print('Contiguous:', c, '(no run of four blocks)')
l=linked(); show('Linked ',l); print('Pointers:', dict(zip(l,l[1:]+[None])))
idx,data=indexed(); show('Indexed', [idx]+data); print('Index:',idx,'table:',data)
for k in range(size):
    print('Logical block',k, 'contiguous reads if allocated: 1; linked reads:',k+1,'indexed reads (uncached): 2')
