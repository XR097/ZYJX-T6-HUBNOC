"""Compact orthogonal router with true multi-sink nets and post-route labels.
Owner: WangYizhao. G1-G6: crossing=30 cells, bounded detours, edge cost,
all successful orders optimized, finite titles, actual-stub port ordering.
"""
from collections import defaultdict,deque
from heapq import heappush,heappop
import math,random,copy,json
from pathlib import Path
from html import escape
from geometry import segments,simplify,inside,length,hit,overlap,cross,boundary_hits
STEP=14
DIRS=((1,0),(-1,0),(0,1),(0,-1))
VECT=dict(l=(-1,0),r=(1,0),t=(0,-1),b=(0,1))

def reversals(path):
    return sum((b[0]-a[0])*(d[0]-c[0])+(b[1]-a[1])*(d[1]-c[1])<0
               for a,b,c,d in zip(path,path[1:],path[2:],path[3:]))

def close_parallel(path):
    ss=list(segments(path))
    for i,(a,b) in enumerate(ss):
        for c,d in ss[i+1:]:
            if a[0]==b[0] and c[0]==d[0] and 0<abs(a[0]-c[0])<32:return True
            if a[1]==b[1] and c[1]==d[1] and 0<abs(a[1]-c[1])<32:return True
    return False

def cells(points):
    out=[]
    for a,b in segments(points):
        dx=0 if a[0]==b[0] else (1 if b[0]>a[0] else -1)
        dy=0 if a[1]==b[1] else (1 if b[1]>a[1] else -1)
        p=(round(a[0]/STEP),round(a[1]/STEP));q=(round(b[0]/STEP),round(b[1]/STEP))
        if not out:out.append(p)
        while p!=q:p=(p[0]+dx,p[1]+dy);out.append(p)
    return out
def center(r):return r[0]+r[2]/2,r[1]+r[3]/2
def endpoints(net):return [('src',net['src'])]+[(f'dst{i}',e) for i,e in enumerate(net['dsts'])]
def visibility_sides(fig,nodes):
    """Automatic obstacle-aware alternative, with no author edge hints.

    Score all16 side pairs using straight/L/Z visibility paths. The detailed
    A* router and independent checker still decide acceptance afterwards.
    """
    rs=[b['rect'] for b in fig['blocks']]+[[c['rect'][0],c['rect'][1],c['title_width'],42] for c in fig.get('containers',[])]
    xs=sorted({round(v/STEP)*STEP for r in rs for v in (r[0]-42,r[0]+r[2]+42) if 60<=v<=fig['width']-60})
    ys=sorted({round(v/STEP)*STEP for r in rs for v in (r[1]-42,r[1]+r[3]+42) if 70<=v<=fig['height']-60})
    counts=defaultdict(int);receipt=[];static_cache={}
    def perturb(bid,s,did,t):
        seed=fig.get('side_search_seed',0)
        return random.Random(f'{seed}:{bid}:{s}:{did}:{t}').uniform(-112,112) if seed else 0
    def face(bid,s,toward=None):
        x,y,w,h=nodes[bid]['rect']
        # Match the later barycentric slot projection. A tall block's
        # midpoint otherwise makes an adjacent request incorrectly prefer
        # its distant top/bottom edge over the directly facing long edge.
        tx,ty=toward if toward is not None else (x+w/2,y+h/2)
        cx=max(x+28,min(x+w-28,round(tx/STEP)*STEP));cy=max(y+28,min(y+h-28,round(ty/STEP)*STEP))
        p=({'l':x,'r':x+w}.get(s,cx),{'t':y,'b':y+h}.get(s,cy));v=VECT[s]
        return p,(p[0]+42*v[0],p[1]+42*v[1])
    def cost(bid,s,did,t):
        # Side candidates must fit real independent-net slots; a low path
        # score cannot authorize more ports than a block edge can carry.
        for ident,side in ((bid,s),(did,t)):
            rect=nodes[ident]['rect'];span=rect[2] if side in 'tb' else rect[3]
            spacing=max(42,nodes[ident].get('port_spacing',42))
            if counts[ident,side]*spacing+56>span:return math.inf
        cachekey=(bid,s,did,t)
        if cachekey in static_cache:return static_cache[cachekey]+42*(counts[bid,s]+counts[did,t])+perturb(*cachekey)
        p,a=face(bid,s,center(nodes[did]['rect']));q,b=face(did,t,center(nodes[bid]['rect']))
        if any(inside(v,r,42) for v in (a,b) for r in rs):return math.inf
        if not all(60<=v[0]<=fig['width']-60 and 70<=v[1]<=fig['height']-60 for v in (a,b)):return math.inf
        for con in fig.get('containers',[]):
            r=con['rect'];srcstate=inside(center(nodes[bid]['rect']),r);dststate=inside(center(nodes[did]['rect']),r)
            if srcstate==dststate and (inside(a,r)!=srcstate or inside(b,r)!=dststate):return math.inf
        options=[[a,(b[0],a[1]),b],[a,(a[0],b[1]),b]]
        options.extend([a,(x,a[1]),(x,b[1]),b] for x in xs)
        options.extend([a,(a[0],y),(b[0],y),b] for y in ys)
        best=math.inf
        for path in options:
            path=simplify(path)
            if any(hit(u,v,r,42) for u,v in segments(path) for r in rs):continue
            full=simplify([p]+path+[q])
            if reversals(full) or close_parallel(full):continue
            if any(len(boundary_hits(full,c['rect']))>1 for c in fig.get('containers',[])):continue
            v=length(full)+28*(len(full)-2)
            best=min(best,v)
        if not math.isfinite(best) and fig.get('allow_complex_visibility',False):
            # L/Z visibility misses routes around two or more obstacles.
            # Search a bounded orthogonal grid for those candidates too;
            # this remains geometry-derived, without authored side hints.
            start=(round(a[0]/STEP),round(a[1]/STEP));end=(round(b[0]/STEP),round(b[1]/STEP))
            def legal(v):
                xy=(v[0]*STEP,v[1]*STEP)
                if not(60<=xy[0]<=fig['width']-60 and 70<=xy[1]<=fig['height']-60):return False
                if any(inside(xy,r,42) for r in rs):return False
                return all(inside(xy,c['rect'])==inside(a,c['rect']) for c in fig.get('containers',[]) if inside(a,c['rect'])==inside(b,c['rect']))
            if legal(start) and legal(end):
                heap=[(0,0,start,-1)];dist={(start,-1):0}
                while heap:
                    _,score,v,di=heappop(heap)
                    if score!=dist.get((v,di)):continue
                    if v==end:best=score*STEP+84;break
                    for nd,(dx,dy) in enumerate(DIRS):
                        u=(v[0]+dx,v[1]+dy)
                        if not legal(u):continue
                        # A candidate cannot leave and re-enter a container.
                        if any(inside(a,c['rect'])!=inside(b,c['rect']) and inside((v[0]*STEP,v[1]*STEP),c['rect'])==inside(b,c['rect']) and inside((u[0]*STEP,u[1]*STEP),c['rect'])!=inside(b,c['rect']) for c in fig.get('containers',[])):continue
                        ns=score+1+(0 if di in (-1,nd) else 2)
                        if ns<dist.get((u,nd),math.inf):
                            dist[u,nd]=ns;heappush(heap,(ns+abs(u[0]-end[0])+abs(u[1]-end[1]),ns,u,nd))
        static_cache[cachekey]=best
        return best+42*(counts[bid,s]+counts[did,t])+perturb(*cachekey)
    for n in fig['nets']:
        src=n['src']['block'];candidates=[]
        for s in VECT:
            picks=[];total=0
            for de in n['dsts']:
                ds=min(((cost(src,s,de['block'],t),t) for t in VECT),key=lambda z:z[0]);picks.append(ds[1]);total+=ds[0]
            candidates.append((total,s,picks))
        total,s,picks=min(candidates,key=lambda z:z[0])
        if not math.isfinite(total):continue
        n['src']['side']=s;counts[src,s]+=1
        for de,t in zip(n['dsts'],picks):de['side']=t;counts[de['block'],t]+=1
        receipt.append(dict(net=n['net_id'],strategy='visibility',cost=total,source=s,destinations=picks))
    fig['automatic_side_candidates']=receipt
def allocate(fig,measure):
    nodes={b['id']:b for b in fig['blocks']+fig.get('containers',[])}
    for c in fig.get('containers',[]):c['title_width']=min(c['rect'][2],math.ceil(measure(c.get('title',''),22))+40)
    for n in fig['nets']:
        for _,e in endpoints(n):
            if e.get('side','auto')!='auto':raise ValueError(('H9 manual author side',n['net_id']))
    if fig.get('side_strategy')=='visibility':visibility_sides(fig,nodes)
    # Auto sides use geometry, including reverse and same-row control relations.
    for n in fig['nets']:
        sc=center(nodes[n['src']['block']]['rect']);dc=[center(nodes[e['block']]['rect']) for e in n['dsts']]
        avg=(sum(x for x,y in dc)/len(dc),sum(y for x,y in dc)/len(dc))
        def side(a,b):
            dx,dy=b[0]-a[0],b[1]-a[1]
            return ('r' if dx>=0 else 'l') if abs(dx)>=abs(dy) else ('b' if dy>=0 else 't')
        if n['src'].get('side','auto')=='auto':n['src']['side']=side(sc,avg)
        for e,co in zip(n['dsts'],dc):
            if e.get('side','auto')=='auto':e['side']=side(co,sc)
    fig['side_selection']='automatic_geometry'
    fig['side_strategy_used']=fig.get('side_strategy','relative')
    done={r['net'] for r in fig.get('automatic_side_candidates',[])}
    fig.setdefault('automatic_side_candidates',[]).extend(dict(net=n['net_id'],strategy='relative',source=n['src']['side'],destinations=[e['side'] for e in n['dsts']]) for n in fig['nets'] if n['net_id'] not in done)
    slots=defaultdict(list);lookup={}
    for n in fig['nets']:
        for eid,e in endpoints(n):
            key=(n['net_id'],eid);slots[e['block'],e['side']].append(key);lookup[key]=(n,e)
    anchors={}
    def assign(values,bid,side,desired=None):
        x,y,w,h=nodes[bid]['rect'];gap=max(42,nodes[bid].get('port_spacing',42));span=w if side in 'tb' else h
        if (len(values)-1)*gap+56>span:raise ValueError(f'{bid}.{side}: {len(values)} ports need {(len(values)-1)*gap+56}px, have {span}')
        mid=x+w/2 if side in 'tb' else y+h/2;first=round((mid-(len(values)-1)*gap/2)/STEP)*STEP
        positions=[first+i*gap for i in range(len(values))]
        if desired is not None:
            lo=(x if side in 'tb' else y)+28;hi=(x+w if side in 'tb' else y+h)-28
            positions=[max(lo,min(hi,round(v/STEP)*STEP)) for v in desired]
            for i in range(1,len(positions)):positions[i]=max(positions[i],positions[i-1]+gap)
            if positions and positions[-1]>hi:
                positions[-1]=hi
                for i in range(len(positions)-2,-1,-1):positions[i]=min(positions[i],positions[i+1]-gap)
        for key,p in zip(values,positions):anchors[key]=({'l':x,'r':x+w}.get(side,p),{'t':y,'b':y+h}.get(side,p))
    for (bid,side),values in slots.items():assign(values,bid,side)
    # Barycentric iteration uses actual opposite port locations, not block centers.
    for _ in range(8):
        old=dict(anchors)
        for (bid,side),values in slots.items():
            axis=0 if side in 'tb' else 1
            def order(key):
                n,e=lookup[key]
                other=[anchors[n['net_id'],f'dst{i}'] for i in range(len(n['dsts']))] if key[1]=='src' else [anchors[n['net_id'],'src']]
                return sum(p[axis] for p in other)/len(other),key
            sortedvalues=sorted(values,key=order)
            # Project onto the actual facing track. Averaging then snapping
            # can get stuck with a14px offset and make opposed arrow stubs
            # meet a different net inside a narrow channel (33B H4).
            desired=[order(key)[0] for key in sortedvalues]
            assign(sortedvalues,bid,side,desired)
        if anchors==old:break
    if fig.get('refine_anchors',True):refine_anchors(fig,nodes,anchors)
    return nodes,anchors

def refine_anchors(fig,nodes,anchors):
    """Geometry-based port location/side repair, without authored edge hints.

    A projected midpoint can strand a port behind another block or force a
    short step. Search the free edge locations before detailed routing.
    """
    rects=[b['rect'] for b in fig['blocks']]+[[c['rect'][0],c['rect'][1],c['title_width'],42] for c in fig.get('containers',[])]
    registry={}
    prior_routes=fig.get('_routing_reference',[])
    prior_names={n['net_id'] for n in prior_routes}
    for n in fig['nets']:
        for eid,e in endpoints(n):registry[n['net_id'],eid]=e
    def options(key,side,toward):
        e=registry[key];r=nodes[e['block']]['rect'];x,y,w,h=r;axis=0 if side in 'tb' else 1;lo=(x if axis==0 else y)+28;hi=(x+w if axis==0 else y+h)-28
        vals={lo,hi,round((lo+hi)/28)*14,round(toward[axis]/14)*14}
        vals.update(range(lo,hi+1,42));vals.add(anchors[key][axis])
        for kk,ee in registry.items():
            if kk[0]!=key[0] and ee['block']==e['block'] and ee['side']==side:
                v=anchors[kk][axis];vals.update((v-42,v+42))
        out=[]
        for v in vals:
            if not lo<=v<=hi:continue
            p=({'l':x,'r':x+w}.get(side,v),{'t':y,'b':y+h}.get(side,v))
            if any(kk[0]!=key[0] and ee['block']==e['block'] and ee['side']==side and abs(anchors[kk][axis]-v)<42 for kk,ee in registry.items()):continue
            a=(p[0]+42*VECT[side][0],p[1]+42*VECT[side][1])
            if not(60<=a[0]<=fig['width']-60 and 70<=a[1]<=fig['height']-60):continue
            if any(inside(a,r,42) for r in rects):continue
            out.append(p)
        return sorted(out,key=lambda p:abs(p[0]-toward[0])+abs(p[1]-toward[1]))
    current_net=None
    def score(p,q,s,t):
        a=(p[0]+42*VECT[s][0],p[1]+42*VECT[s][1]);b=(q[0]+42*VECT[t][0],q[1]+42*VECT[t][1])
        candidates=[[a,(b[0],a[1]),b],[a,(a[0],b[1]),b]]
        # Three-bend staircase candidates remain monotone in both axes.
        for x in {a[0],b[0],round((a[0]+b[0])/28)*14}:candidates.append([a,(x,a[1]),(x,b[1]),b])
        for y in {a[1],b[1],round((a[1]+b[1])/28)*14}:candidates.append([a,(a[0],y),(b[0],y),b])
        best=math.inf
        for mid in candidates:
            full=simplify([p]+mid+[q])
            if reversals(full) or close_parallel(full):continue
            if any(hit(u,v,r,42) for u,v in segments(simplify(mid)) for r in rects):continue
            # Foreign terminal stubs are reserved physical segments, not free
            # crossing channels. Midpoint projection can otherwise block a
            # whole net before the detailed router gets a chance to search.
            blocked_stub=False
            for kk,ee in registry.items():
                if kk[0]==current_net:continue
                z=anchors[kk];vv=VECT[ee['side']];zz=(z[0]+42*vv[0],z[1]+42*vv[1])
                for u,v in segments(full):
                    if any((abs(pp[0]-u[0])+max(min(u[1],v[1])-pp[1],0,pp[1]-max(u[1],v[1])) if u[0]==v[0] else abs(pp[1]-u[1])+max(min(u[0],v[0])-pp[0],0,pp[0]-max(u[0],v[0])))<24 for pp in (z,zz)):
                        blocked_stub=True;break
                    if cross(u,v,z,zz) or any((u[0]==v[0]==pp[0] and min(u[1],v[1])<=pp[1]<=max(u[1],v[1])) or (u[1]==v[1]==pp[1] and min(u[0],v[0])<=pp[0]<=max(u[0],v[0])) for pp in (z,zz)):
                        blocked_stub=True;break
                if blocked_stub:break
            if blocked_stub:continue
            if any(len(boundary_hits(full,c['rect']))>1 for c in fig.get('containers',[])):continue
            if any(any((u[0]==v[0] and min(abs(u[0]-r[0]),abs(u[0]-r[0]-r[2]))<42 and max(min(u[1],v[1]),r[1])<min(max(u[1],v[1]),r[1]+r[3])) or (u[1]==v[1] and min(abs(u[1]-r[1]),abs(u[1]-r[1]-r[3]))<42 and max(min(u[0],v[0]),r[0])<min(max(u[0],v[0]),r[0]+r[2])) for u,v in segments(full)) for r in [c['rect'] for c in fig.get('containers',[])]):continue
            crossings=set();near_prior=False
            for oldnet in prior_routes:
                if oldnet['net_id']==current_net:continue
                for op in oldnet['paths']:
                    for u,v in segments(full):
                        for c,d in segments(op):
                            cp=cross(u,v,c,d)
                            if cp:crossings.add((oldnet['net_id'],cp))
                            if u[0]==v[0]==c[0]==d[0] and max(min(u[1],v[1]),min(c[1],d[1]))<min(max(u[1],v[1]),max(c[1],d[1])):near_prior=True
                            if u[1]==v[1]==c[1]==d[1] and max(min(u[0],v[0]),min(c[0],d[0]))<min(max(u[0],v[0]),max(c[0],d[0])):near_prior=True
            if near_prior:continue
            best=min(best,length(full)+28*(len(full)-2)+420*len(crossings))
        return best
    for iteration in range(2):
        for n in fig['nets']:
            nid=n['net_id'];current_net=nid;sk=(nid,'src');p0=anchors[sk];s0=n['src']['side']
            if (not prior_routes or nid in prior_names) and all(math.isfinite(score(p0,anchors[nid,f'dst{i}'],s0,d['side'])) for i,d in enumerate(n['dsts'])):continue
            qs=[anchors[nid,f'dst{i}'] for i in range(len(n['dsts']))];avg=tuple(sum(q[a] for q in qs)/len(qs) for a in (0,1));best=None
            for s in VECT:
                for p in options(sk,s,avg):
                    choices=[];total=0
                    for i,d in enumerate(n['dsts']):
                        dk=(nid,f'dst{i}');ds=[]
                        for t in VECT:
                            for q in options(dk,t,p):
                                sc=score(p,q,s,t)
                                if math.isfinite(sc):ds.append((sc+0.05*(abs(q[0]-qs[i][0])+abs(q[1]-qs[i][1])),t,q))
                        if not ds:break
                        pick=min(ds);total+=pick[0];choices.append(pick)
                    if len(choices)==len(n['dsts']):
                        total+=0.05*(abs(p[0]-p0[0])+abs(p[1]-p0[1]))
                        if best is None or total<best[0]:best=(total,s,p,choices)
            if best:
                _,s,p,choices=best;n['src']['side']=s;anchors[sk]=p
                for i,(_,t,q) in enumerate(choices):n['dsts'][i]['side']=t;anchors[nid,f'dst{i}']=q
    fig['automatic_side_candidates']=[dict(net=n['net_id'],strategy=fig.get('side_strategy','relative'),refinement='free-edge geometry search',source=n['src']['side'],destinations=[d['side'] for d in n['dsts']]) for n in fig['nets']]

def place_labels(nets,fig,measure):
    rects=[b['rect'] for b in fig['blocks']]
    titles=[[c['rect'][0],c['rect'][1],c['title_width'],42] for c in fig.get('containers',[])]
    allsegs=[(n['net_id'],a,b) for n in nets for p in n['paths'] for a,b in segments(p)]
    used=[];leaders=[]
    def safe_container_label(r,anchor,center):
        for con in fig.get('containers',[]):
            for c,d in rect_edges(con['rect']):
                if hit(c,d,r,12):return False
                if cross(anchor,center,c,d):return False
        return True
    # Long text is placed first; labels never affect route search.
    for n in sorted(nets,key=lambda n:measure(n['label'],17),reverse=True):
        lw=math.ceil(measure(n['label'],17))+14;lh=26
        unique=list(dict.fromkeys((a,b) for p in n['paths'] for a,b in segments(p)))
        horizontal=sorted([(a,b) for a,b in unique if a[1]==b[1]],key=lambda ab:abs(ab[1][0]-ab[0][0]),reverse=True)
        vertical=sorted([(a,b) for a,b in unique if a[0]==b[0]],key=lambda ab:abs(ab[1][1]-ab[0][1]),reverse=True)
        # A vertical label is allowed only when the net has no horizontal segment.
        options=horizontal;chosen=None
        for a,b in options:
            L=abs(a[0]-b[0])+abs(a[1]-b[1]);hor=a[1]==b[1]
            if L<lw+8:continue
            # Search actual legal subsegments, including sections split by a
            # container border; five fixed fractional samples can miss them.
            samples=[.5,.35,.65,.2,.8]
            samples+=sorted([v/L for v in range(math.ceil((lw/2+4)/STEP)*STEP,math.floor((L-lw/2-4)/STEP)*STEP+1,STEP)],key=lambda t:abs(t-.5))
            for f in dict.fromkeys(samples):
                xx=a[0]+(b[0]-a[0])*f;yy=a[1]+(b[1]-a[1])*f
                for off in (-22,22,-36,36):
                    r=[xx-lw/2,yy+off-lh/2,lw,lh] if hor else [xx+off-lh/2,yy-lw/2,lh,lw]
                    if r[0]<60 or r[0]+r[2]>fig['width']-60 or r[1]<70 or r[1]+r[3]>fig['height']-60:continue
                    if any(overlap(r,z,3) for z in rects+titles+used):continue
                    if any(hit(c,d,r,3) for _,c,d in allsegs):continue
                    if any(hit(c,d,r,3) for c,d in leaders):continue
                    if not safe_container_label(r,(xx,yy),(xx,yy+off)):continue
                    chosen=dict(rect=r,x=xx if hor else xx+off,y=yy+off if hor else yy,rotate=0 if hor else -90,segment=[a,b],offset=off)
                    break
                if chosen:break
            if chosen:break
        # Keep text horizontal without stretching the data wire: a short,
        # visually secondary annotation leader can attach to a long vertical
        # segment. This is annotation geometry, never a data/control branch.
        if chosen is None:
            for a,b in vertical:
                if abs(a[1]-b[1])<56:continue
                for f in (.5,.35,.65,.2,.8):
                    yy=a[1]+(b[1]-a[1])*f
                    for side in (-1,1):
                        edge=a[0]+side*22;xx=edge+side*lw/2;r=[xx-lw/2,yy-lh/2,lw,lh]
                        leader=[(a[0],yy),(edge,yy)]
                        if r[0]<60 or r[0]+r[2]>fig['width']-60 or r[1]<70 or r[1]+r[3]>fig['height']-60:continue
                        if any(overlap(r,z,3) for z in rects+titles+used):continue
                        if any(hit(c,d,r,3) for _,c,d in allsegs):continue
                        if any(hit(c,d,r,3) for c,d in leaders):continue
                        if not safe_container_label(r,(a[0],yy),(xx,yy)):continue
                        if any(hit(*leader,z,3) for z in rects+titles+used):continue
                        if any(cross(*leader,c,d) or (hit(*leader,[min(c[0],d[0])-2,min(c[1],d[1])-2,abs(c[0]-d[0])+4,abs(c[1]-d[1])+4])) for oid,c,d in allsegs if oid!=n['net_id']):continue
                        if any(cross(*leader,c,d) for con in fig.get('containers',[]) for c,d in rect_edges(con['rect'])):continue
                        chosen=dict(rect=r,x=xx,y=yy,rotate=0,segment=[a,b],orientation='callout',leader=leader)
                        break
                    if chosen:break
                if chosen:break
        # Pure vertical nets still prefer a horizontal callout. Rotated text
        # is the last fallback only, and remains subject to the 15% cap.
        if chosen is None and not horizontal:
            for a,b in vertical:
                L=abs(a[1]-b[1])
                if L<lw+8:continue
                samples=[.5,.35,.65,.2,.8]
                samples+=sorted([v/L for v in range(math.ceil((lw/2+4)/STEP)*STEP,math.floor((L-lw/2-4)/STEP)*STEP+1,STEP)],key=lambda t:abs(t-.5))
                for f in dict.fromkeys(samples):
                    yy=a[1]+(b[1]-a[1])*f
                    for off in (-22,22,-36,36):
                        r=[a[0]+off-lh/2,yy-lw/2,lh,lw]
                        if r[0]<60 or r[0]+r[2]>fig['width']-60 or r[1]<70 or r[1]+r[3]>fig['height']-60:continue
                        if any(overlap(r,z,3) for z in rects+titles+used):continue
                        if any(hit(c,d,r,3) for _,c,d in allsegs):continue
                        if any(hit(c,d,r,3) for c,d in leaders):continue
                        if not safe_container_label(r,(a[0],yy),(a[0]+off,yy)):continue
                        chosen=dict(rect=r,x=a[0]+off,y=yy,rotate=-90,segment=[a,b],offset=off)
                        break
                    if chosen:break
                if chosen:break
        if chosen is None:raise ValueError(('label placement',n['net_id'],lw))
        n['label_box']=chosen;used.append(chosen['rect'])
        if chosen.get('leader'):leaders.append(chosen['leader'])
    if sum(bool(n['label_box']['rotate']) for n in nets)>len(nets)*.15:raise ValueError('vertical label ratio > 15%')

def rect_edges(r):
    x,y,w,h=r;return [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]

def route(fig,measure,attempts=24):
    unallocated=copy.deepcopy(fig)
    nodes,anchors=allocate(fig,measure);W,H=fig['width'],fig['height']
    blockrect=[b['rect'] for b in fig['blocks']]
    titles=[[c['rect'][0],c['rect'][1],c['title_width'],42] for c in fig.get('containers',[])]
    blocked=set()
    for r in blockrect+titles:
        x,y,w,h=r
        for ix in range(math.floor((x-42)/STEP),math.ceil((x+w+42)/STEP)+1):
            for iy in range(math.floor((y-42)/STEP),math.ceil((y+h+42)/STEP)+1):
                if inside((ix*STEP,iy*STEP),r,42):blocked.add((ix,iy))
    def stub(e,p):
        dx,dy=VECT[e['side']];return p[0]+42*dx,p[1]+42*dy
    stubs={}
    for n in fig['nets']:
        for eid,e in endpoints(n):
            p=anchors[n['net_id'],eid];stubs[n['net_id'],eid]=(p,stub(e,p))
    allstub={key:set(cells(pair)) for key,pair in stubs.items()}
    best=None;failure=None;valid=0;failedbest=None;failures=defaultdict(int)
    for attempt in range(attempts):
        order=sorted(fig['nets'],key=lambda n:sum(abs(anchors[n['net_id'],'src'][a]-anchors[n['net_id'],f'dst{i}'][a]) for i in range(len(n['dsts'])) for a in (0,1)),reverse=bool(attempt%2))
        if fig.get('multisink_search') and attempt<2:
            # Reserve a real multi-drop trunk before point-to-point wires
            # fragment its channels. Other attempts retain random orders.
            order.sort(key=lambda n:-len(n['dsts']))
        if attempt>1:random.Random(attempt+fig.get('seed',0)).shuffle(order)
        occupied=defaultdict(dict);edges={};vertices={};results={};costtotal=0;xs={}
        try:
            for n in order:
                nid=n['net_id'];p,a=stubs[nid,'src'];source=(a[0]//STEP,a[1]//STEP)
                tree=defaultdict(set);owncells=set(cells([p,a]));paths=[];path_by_sink={}
                for u,v in zip(cells([p,a]),cells([p,a])[1:]):tree[u].add(v);tree[v].add(u)
                # A multi-sink bus must not depend on the author's listing
                # order. Try near-first and far-first trees across attempts,
                # then return paths in original semantic sink order.
                sink_order=list(range(len(n['dsts'])))
                if fig.get('multisink_search'):
                    sink_order=sorted(sink_order,key=lambda j:sum(abs(anchors[nid,'src'][a]-anchors[nid,f'dst{j}'][a]) for a in (0,1)),reverse=bool(attempt%2))
                for sink_step,i in enumerate(sink_order):
                    target=n['dsts'][i]
                    q,b=stubs[nid,f'dst{i}'];start=(b[0]//STEP,b[1]//STEP);end=source
                    sp=center(nodes[n['src']['block']]['rect']);dp=center(nodes[target['block']]['rect'])
                    constraints=[(c['rect'],inside(sp,c['rect'])) for c in fig.get('containers',[]) if inside(sp,c['rect'])==inside(dp,c['rect'])]
                    forbidden=set().union(*(cs for (other,eid),cs in allstub.items() if other!=nid))
                    for (other,eid),(fp,fs) in stubs.items():
                        if other==nid:continue
                        for fx,fy in (fp,fs):
                            forbidden.update((fx//STEP+dx,fy//STEP+dy) for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)))
                    # A trunk may not consume another sink's arrow stub,
                    # including a sink that has not been routed yet.
                    for (other,eid),(fp,fs) in stubs.items():
                        if other!=nid or eid in ('src',f'dst{i}'):continue
                        forbidden.update(allstub[other,eid])
                        for fx,fy in (fp,fs):
                            forbidden.update((fx//STEP+dx,fy//STEP+dy) for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)))
                    def legal(pos):
                        xy=(pos[0]*STEP,pos[1]*STEP)
                        if pos in blocked or pos in forbidden:return False
                        if xy[0]<60 or xy[0]>W-60 or xy[1]<70 or xy[1]>H-60:return False
                        if not all(inside(xy,r)==state for r,state in constraints):return False
                        # No near endpoint / near T ambiguity with already routed nets.
                        if any(abs(xy[0]-v[0])+abs(xy[1]-v[1])<24 for v,owner in vertices.items() if owner!=nid):return False
                        return True
                    if not legal(start) or (not sink_step and not legal(source)):raise ValueError(('blocked stub',nid,i,start,source))
                    arrow_ends=[stubs[nid,f'dst{j}'][0] for j in range(len(n['dsts']))]
                    goals={g for g in owncells if abs(g[0]*STEP-p[0])+abs(g[1]*STEP-p[1])>=42 and (sink_step==0 or all(abs(g[0]*STEP-q0[0])+abs(g[1]*STEP-q0[1])>=56 for q0 in arrow_ends))}
                    if sink_step:
                        old_segments=[ab for path in path_by_sink.values() for ab in segments(path)]
                        goals={g for g in goals if all(min(p[ax],q[ax])<=g[ax]*STEP<=max(p[ax],q[ax]) for ax in (0,1))
                            and all(not(0<abs(g[0]*STEP-aa[0])<32) if aa[0]==bb[0] else not(0<abs(g[1]*STEP-aa[1])<32) for aa,bb in old_segments)}
                    if not goals:raise ValueError(('H3 no branch-safe goals',nid,i))
                    def heuristic(v):return min(abs(v[0]-g[0])+abs(v[1]-g[1]) for g in goals)
                    initial_dir=DIRS.index(VECT[target['side']])
                    # Respect the final crossing cap during search as well as
                    # in the independent checker. Otherwise the cheapest
                    # invalid path can repeatedly hide a slightly longer
                    # admissible path, especially in the outer margin.
                    committed=sum(len(owners)>1 for owners in occupied.values())
                    own_cross=sum(bool(occupied.get(v)) for v in owncells)
                    cross_budget=fig.get('max_crossings',2)-committed-own_cross
                    heap=[(heuristic(start),0,0,0,start,initial_dir,3)];dist={(start,initial_dir,0,3):0};prev={};goal=None
                    def near_other_track(v):
                        return any(any(owner!=nid for owner in occupied.get((v[0]+dx,v[1]+dy),{})) for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)))
                    maxsteps=math.ceil(2.5*(abs(p[0]-q[0])+abs(p[1]-q[1]))/STEP)
                    while heap:
                        _,cost,steps,ncross,pos,di,run=heappop(heap)
                        if cost!=dist.get((pos,di,ncross,run)):continue
                        if pos in goals:
                            if near_other_track(pos):continue
                            if sink_step==0:
                                toward_source=DIRS.index(tuple(-v for v in VECT[n['src']['side']]))
                                if di!=toward_source and run<3:continue
                            goal=(pos,di,ncross,run);break
                        for ndi,(dx,dy) in enumerate(DIRS):
                            nv=(pos[0]+dx,pos[1]+dy);axis=0 if dx else 1
                            if sink_step:
                                if nv in owncells and nv not in goals:continue
                                if any((axis==0 and aa[1]==bb[1] and 0<abs(pos[1]*STEP-aa[1])<32) or (axis==1 and aa[0]==bb[0] and 0<abs(pos[0]*STEP-aa[0])<32) for aa,bb in old_segments):continue
                            # Monotone source/destination routes cannot hide a
                            # down-and-back U behind a wide intermediate leg.
                            if fig.get('monotone',True):
                                if dx and (p[0]-q[0])*dx<=0:continue
                                if dy and (p[1]-q[1])*dy<=0:continue
                            # A turn is a visible endpoint of both segments.
                            # Keep it >=24 px from existing foreign tracks,
                            # rather than rejecting the completed route later.
                            if di!=ndi and near_other_track(pos):continue
                            if di!=ndi and run<3:continue
                            if steps+1+heuristic(nv)>maxsteps:continue
                            if not legal(nv):continue
                            tangent=any(any((vv[0]*STEP in (r[0],r[0]+r[2]) and r[1]<=vv[1]*STEP<=r[1]+r[3] and dy) or (vv[1]*STEP in (r[1],r[1]+r[3]) and r[0]<=vv[0]*STEP<=r[0]+r[2] and dx) for vv in (pos,nv)) for r in [c['rect'] for c in fig.get('containers',[])])
                            if tangent:continue
                            # Container boundaries may be crossed normally,
                            # but no track may run along their <28px band.
                            if any((dx and min(abs(pos[1]*STEP-r[1]),abs(pos[1]*STEP-r[1]-r[3]))<42 and max(min(pos[0],nv[0])*STEP,r[0])<min(max(pos[0],nv[0])*STEP,r[0]+r[2])) or (dy and min(abs(pos[0]*STEP-r[0]),abs(pos[0]*STEP-r[0]-r[2]))<42 and max(min(pos[1],nv[1])*STEP,r[1])<min(max(pos[1],nv[1])*STEP,r[1]+r[3])) for r in [c['rect'] for c in fig.get('containers',[])]):continue
                            edge=tuple(sorted((pos,nv)))
                            if edge in edges and edges[edge]!=nid:continue
                            uses={owner:axes for owner,axes in occupied.get(nv,{}).items() if owner!=nid}
                            if any(axis in axes for axes in uses.values()):continue
                            usesprev={owner:axes for owner,axes in occupied.get(pos,{}).items() if owner!=nid}
                            if any(axis in axes for axes in usesprev.values()):continue
                            if uses and (any(len(a)>1 for a in uses.values()) or nv==start or nv in goals):continue
                            next_cross=ncross+len(uses)
                            if next_cross>cross_budget:continue
                            edgecost=12 if min(nv[0]*STEP,W-nv[0]*STEP,nv[1]*STEP,H-nv[1]*STEP)<84 else 0
                            nc=cost+1+(0 if di in (-1,ndi) else 3)+30*len(uses)+edgecost
                            # Collinear endpoints need a clear >=32px gap.
                            if any(any(owner!=nid and axis in axes for owner,axes in occupied.get((nv[0]+delta if axis==0 else nv[0],nv[1]+delta if axis==1 else nv[1]),{}).items()) for delta in (-2,-1,0,1,2)):continue
                            newrun=min(3,run+1) if di==ndi else 1
                            state=(nv,ndi,next_cross,newrun)
                            if nc<dist.get(state,1e20):
                                dist[state]=nc;prev[state]=(pos,di,ncross,run);heappush(heap,(nc+heuristic(nv),nc,steps+1,next_cross,nv,ndi,newrun))
                    if goal is None:
                        # Bounded L/Z fallback. This independently enumerates
                        # monotone grid polylines when the A* state pruning
                        # loses a legal crossing/terminal history.
                        candidates=[];fallback_rejections=[]
                        for gg in goals:
                            xx=sorted({start[0],gg[0],(start[0]+gg[0])//2}|set(range(min(start[0],gg[0]),max(start[0],gg[0])+1,3)))
                            yy=sorted({start[1],gg[1],(start[1]+gg[1])//2}|set(range(min(start[1],gg[1]),max(start[1],gg[1])+1,3)))
                            polylines=[[start,(gg[0],start[1]),gg],[start,(start[0],gg[1]),gg]]
                            polylines.extend([start,(x,start[1]),(x,gg[1]),gg] for x in xx)
                            polylines.extend([start,(start[0],y),(gg[0],y),gg] for y in yy)
                            for pp0 in polylines:
                                pp1=simplify([(x*STEP,y*STEP) for x,y in pp0])
                                cc=cells(pp1)
                                if sink_step and any(v in owncells and v not in goals for v in cc):continue
                                if sink_step and any((u[1]==v[1] and aa[1]==bb[1] and 0<abs(u[1]-aa[1])<32) or (u[0]==v[0] and aa[0]==bb[0] and 0<abs(u[0]-aa[0])<32) for u,v in segments(pp1) for aa,bb in old_segments):continue
                                invalid=[v for v in cc if not legal(v)]
                                if invalid:
                                    if len(fallback_rejections)<12:
                                        v=invalid[0];xy=(v[0]*STEP,v[1]*STEP)
                                        fallback_rejections.append(dict(path=pp1,reason='legal',point=xy,block=v in blocked,stub=v in forbidden,near=[(vv,who) for vv,who in vertices.items() if abs(xy[0]-vv[0])+abs(xy[1]-vv[1])<24]))
                                    continue
                                if any(near_other_track((x//STEP,y//STEP)) for x,y in pp1[1:-1]):continue
                                bad=False;cross_cells=set()
                                for u,v in zip(cc,cc[1:]):
                                    axis=0 if u[1]==v[1] else 1
                                    for z in (u,v):
                                        uses=occupied.get(z,{})
                                        if any(axis in aa for owner,aa in uses.items() if owner!=nid):bad=True;break
                                        if uses:cross_cells.add(z)
                                    if bad:break
                                    if any(any(owner!=nid and axis in aa for owner,aa in occupied.get((v[0]+d if axis==0 else v[0],v[1]+d if axis==1 else v[1]),{}).items()) for d in (-2,-1,0,1,2)):bad=True;break
                                if bad or len(cross_cells)>cross_budget:
                                    if len(fallback_rejections)<12:fallback_rejections.append(dict(path=pp1,reason='track' if bad else 'cross_budget',cross=len(cross_cells),budget=cross_budget))
                                    continue
                                if any(any((u[0]==v[0] and min(abs(u[0]-r[0]),abs(u[0]-r[0]-r[2]))<42 and max(min(u[1],v[1]),r[1])<min(max(u[1],v[1]),r[1]+r[3])) or (u[1]==v[1] and min(abs(u[1]-r[1]),abs(u[1]-r[1]-r[3]))<42 and max(min(u[0],v[0]),r[0])<min(max(u[0],v[0]),r[0]+r[2])) for u,v in segments(pp1)) for r in [c['rect'] for c in fig.get('containers',[])]):continue
                                candidates.append((len(cc)+3*len(pp1)+30*len(cross_cells),cc))
                        if candidates:
                            cost,cc=min(candidates)
                            state=(cc[0],initial_dir,0,3)
                            for aa,bb in zip(cc,cc[1:]):
                                direction=DIRS.index((bb[0]-aa[0],bb[1]-aa[1]))
                                following=(bb,direction,0,3);prev[following]=state;state=following
                            goal=state;dist[goal]=cost
                        else:
                            if True:
                                (Path(__file__).resolve().parent/f'fallback_{fig["id"]}_{nid}.json').write_text(json.dumps(fallback_rejections,ensure_ascii=False,indent=2),encoding='utf-8')
                            raise ValueError(('no route',nid,i))
                    back=[];cur=goal
                    while cur in prev:back.append(cur[0]);cur=prev[cur]
                    back.append(start) # junction -> destination stub
                    # Find the unique source-to-junction path in the already built tree.
                    root=(p[0]//STEP,p[1]//STEP);targetcell=back[0];queue=deque([root]);prior={root:None}
                    while queue:
                        v=queue.popleft()
                        if v==targetcell:break
                        for u in tree[v]:
                            if u not in prior:prior[u]=v;queue.append(u)
                    prefix=[];cur=targetcell
                    while cur is not None:prefix.append(cur);cur=prior[cur]
                    prefix.reverse();chain=prefix+back[1:]+cells([b,q])[1:]
                    pts=simplify([(x*STEP,y*STEP) for x,y in chain])
                    if reversals(pts):raise ValueError(('H11 reversal',nid,i,pts))
                    if close_parallel(pts):raise ValueError(('H12 step',nid,i,pts))
                    manh=abs(p[0]-q[0])+abs(p[1]-q[1]);ratio=length(pts)/max(1,manh)
                    if ratio>2.5:raise ValueError(('detour',nid,i,ratio))
                    if any(len(boundary_hits(pts,c['rect']))>1 for c in fig.get('containers',[])):raise ValueError(('boundary',nid,i))
                    path_by_sink[i]=pts;costtotal+=dist[goal]+max(0,ratio-1)*10
                    for u,v in zip(chain,chain[1:]):tree[u].add(v);tree[v].add(u)
                    owncells.update(chain)
                paths=[path_by_sink[i] for i in range(len(n['dsts']))]
                # The initial 28px source stub is a routing reservation, not
                # an emitted dangling branch. Derive dots solely from the
                # union of the paths actually emitted to destinations.
                emitted=defaultdict(set)
                for path in paths:
                    chain=cells(path)
                    for u,v in zip(chain,chain[1:]):emitted[u].add(v);emitted[v].add(u)
                junctions=[(x*STEP,y*STEP) for (x,y),adj in emitted.items() if len(adj)>2]
                item={**copy.deepcopy(n),'paths':paths,'points':paths[0],'junctions':junctions}
                results[nid]=item
                for path in paths:
                    for v in path:vertices[v]=nid
                    cs=cells(path)
                    for u,v in zip(cs,cs[1:]):
                        axis=0 if u[1]==v[1] else 1;edges[tuple(sorted((u,v)))]=nid
                        occupied[u].setdefault(nid,set()).add(axis);occupied[v].setdefault(nid,set()).add(axis)
            routed=[results[n['net_id']] for n in fig['nets']];xs={}
            for i,n in enumerate(routed):
                for m in routed[i+1:]:
                    for p1 in n['paths']:
                        for p2 in m['paths']:
                            for a,b in segments(p1):
                                for c,d in segments(p2):
                                    pt=cross(a,b,c,d)
                                    if pt:xs[n['net_id'],m['net_id'],pt]=dict(nets=[n['net_id'],m['net_id']],point=pt)
            if len(xs)>fig.get('max_crossings',2):raise ValueError(('crossings',len(xs)))
            # Reject a future route that approached an earlier endpoint within
            # one grid cell, including an apparent T without a branch marker.
            for n in routed:
                for path in n['paths']:
                    for point in path:
                        for other in routed:
                            if other['net_id']==n['net_id']:continue
                            for op in other['paths']:
                                for aa,bb in segments(op):
                                    if aa[0]==bb[0]:near=abs(point[0]-aa[0])+max(min(aa[1],bb[1])-point[1],0,point[1]-max(aa[1],bb[1]))
                                    else:near=abs(point[1]-aa[1])+max(min(aa[0],bb[0])-point[0],0,point[0]-max(aa[0],bb[0]))
                                    if near<24:raise ValueError(('near endpoint/T',n['net_id'],other['net_id']))
            place_labels(routed,fig,measure)
            valid+=1;score=costtotal+len(xs)*30
            if best is None or score<best[0]:best=(score,routed,list(xs.values()),attempt)
        except ValueError as e:
            failure=str(e);failures[failure]+=1;rank=(len(results),-len(xs),-costtotal)
            if failedbest is None or rank>failedbest[0]:failedbest=(rank,copy.deepcopy(list(results.values())),list(xs.values()),failure,attempt)
    if best is None:
        if failedbest and fig.get('_routing_round',0)<2:
            retry=unallocated
            retry['_routing_reference']=failedbest[1]
            retry['_routing_round']=fig.get('_routing_round',0)+1
            try:
                outcome=route(retry,measure,attempts)
                fig.update({k:v for k,v in retry.items() if k not in ('_routing_reference',)})
                return outcome
            except RuntimeError:
                pass
        if not fig.get('save_diagnostic',True):raise RuntimeError((fig['id'],'no valid bounded route',failure))
        here=Path(__file__).resolve().parent
        diagnostic={**copy.deepcopy(fig),'nets':failedbest[1] if failedbest else [],'crossings':failedbest[2] if failedbest else [],
            'status':'DIAGNOSTIC_ONLY_NOT_ACCEPTED','route_failure':failedbest[3] if failedbest else failure,'route_attempt':failedbest[4] if failedbest else None,
            'failure_counts':dict(failures)}
        (here/f'debug_{fig["id"]}.json').write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2),encoding='utf-8')
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/>',
             '<text x="20" y="32" font-size="18" fill="red">DIAGNOSTIC ONLY — NOT ACCEPTED — '+escape(str(diagnostic['route_failure']))+'</text>']
        for c in fig.get('containers',[]):
            x,y,w,h=c['rect'];out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#bbb" stroke-dasharray="5 4"/>')
        for b in fig['blocks']:
            x,y,w,h=b['rect'];out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#eee" stroke="#345"/><text x="{x+8}" y="{y+24}" font-size="18">{escape(b["id"])}</text>')
        for n in diagnostic['nets']:
            for path in n['paths']:
                points=' '.join(f'{x},{y}' for x,y in path);out.append(f'<polyline points="{points}" fill="none" stroke="{"#222" if n["kind"]=="data" else "#5784b7"}" stroke-width="2"/>')
            path=max(n['paths'],key=length);a,b=max(segments(path),key=lambda s:abs(s[0][0]-s[1][0])+abs(s[0][1]-s[1][1]))
            out.append(f'<text x="{(a[0]+b[0])/2}" y="{(a[1]+b[1])/2-6}" font-size="13" fill="#922">{escape(n["net_id"])}</text>')
        out.append('</svg>');(here/f'debug_{fig["id"]}.svg').write_text('\n'.join(out),encoding='utf-8')
        raise RuntimeError((fig['id'],'no valid bounded route',diagnostic['route_failure'],'routed',len(diagnostic['nets']),'of',len(fig['nets'])))
    fig['route_optimization']=dict(attempts=attempts,valid_solutions=valid,cost=best[0],crossing_cost_cells=30,max_detour=2.5,labels_after_routing=True)
    return best[1],best[2],best[3]
