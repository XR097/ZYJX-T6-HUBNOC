"""Rendering/router geometry helpers; checker intentionally has independent geometry. Owner: WangYizhao."""
def segments(points): return list(zip(points,points[1:]))
def inside(p,r,margin=0):
    x,y,w,h=r;return x-margin<p[0]<x+w+margin and y-margin<p[1]<y+h+margin
def simplify(points):
    out=[]
    for p in points:
        if out and p==out[-1]:continue
        while len(out)>1 and (out[-2][0]==out[-1][0]==p[0] or out[-2][1]==out[-1][1]==p[1]):out.pop()
        out.append(tuple(p))
    return out
def length(points):return sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in segments(points))
def hit(a,b,r,pad=0):
    x,y,w,h=r;x-=pad;y-=pad;w+=2*pad;h+=2*pad
    if a[0]==b[0]:return x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)
    if a[1]==b[1]:return y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w)
    return True
def overlap(a,b,pad=0):return a[0]<b[0]+b[2]+pad and a[0]+a[2]+pad>b[0] and a[1]<b[1]+b[3]+pad and a[1]+a[3]+pad>b[1]
def cross(a,b,c,d):
    if a[1]==b[1] and c[0]==d[0]:
        return (c[0],a[1]) if min(a[0],b[0])<c[0]<max(a[0],b[0]) and min(c[1],d[1])<a[1]<max(c[1],d[1]) else None
    if a[0]==b[0] and c[1]==d[1]:return cross(c,d,a,b)
    return None
def boundary_hits(points,r):
    x,y,w,h=r;hits=set()
    for a,b in segments(points):
        if a[0]==b[0] and x<a[0]<x+w:
            for yy in (y,y+h):
                if min(a[1],b[1])<=yy<=max(a[1],b[1]):hits.add((a[0],yy))
        if a[1]==b[1] and y<a[1]<y+h:
            for xx in (x,x+w):
                if min(a[0],b[0])<=xx<=max(a[0],b[0]):hits.add((xx,a[1]))
    return sorted(hits)
