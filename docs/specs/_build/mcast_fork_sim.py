"""多播分叉点逐拍模型（V18-TP-53）。Owner: WangYizhao · 2026-11-06
协议篇 FIG-TP-STREAM-BEAT、HUB_NOC 篇 FIG-HUB_NOC-MCAST、HUB_IDN 篇 FIG-HUB_IDN-MCAST 共用。

模型（每拍按拍初状态算，ready 都是寄存器输出）：
  分叉点 = 一级通用链路块（存 1 拍）+ 每目的核 1 位已取标志，不另配存储。
  每个目的核的分支 = 分支链路块 skid + 该核接收侧入口 FIFO，合计容量 cap 拍（示意值）。
  拍 t：
    1. 各分支：拍初非空且该核写进 L1 一侧 ready[t] = 1 → 写进 L1 一拍（"核 c 写进 k"）。
    2. 分叉点：对掩码内未取走的目的核，若其分支拍初占用 < cap（分支对分叉点的 ready）→ 送入该分支、置已取位；
       en 只看已取位，不看 ready。
    3. 掩码内已取位全部置位 → 分叉点本拍收进上游下一拍（若还有），已取位清零。
  分叉点在拍 0 已持有单位第 0 拍。
"""


def simulate(n_beats, ready, cap, n_t):
    """ready: {核: [0/1] * n_t}；返回 dict：
    push[c][t] = 本拍送入核 c 分支的 k；write[c][t] = 本拍核 c 写进 L1 的 k；
    occ[c][t] = 核 c 分支拍初占用；accept[t] = 分叉点本拍是否收进下一拍（单位最后一拍送完记 True）；
    stall = 分叉点停收上游的拍数（单位内）。"""
    cores = sorted(ready)
    q = {c: [] for c in cores}
    cur, taken = 0, set()
    push = {c: {} for c in cores}
    write = {c: {} for c in cores}
    occ = {c: {} for c in cores}
    accept = {}
    for t in range(n_t):
        start = {c: len(q[c]) for c in cores}
        for c in cores:
            occ[c][t] = start[c]
        # 1 分支写进 L1
        for c in cores:
            if start[c] and ready[c][t]:
                write[c][t] = q[c].pop(0)
        # 2 分叉点送入分支
        if cur < n_beats:
            for c in cores:
                if c not in taken and start[c] < cap:
                    q[c].append(cur)
                    push[c][t] = cur
                    taken.add(c)
            # 3 全部取走才收下一拍
            if len(taken) == len(cores):
                accept[t] = True
                cur += 1
                taken = set()
            else:
                accept[t] = False
    stall = sum(1 for v in accept.values() if not v)
    return dict(push=push, write=write, occ=occ, accept=accept, stall=stall, cores=cores)


def finish_time(res, c):
    """核 c 写进最后一拍的时钟拍。"""
    return max(res['write'][c])
