import heapq


def astar(start, goal, is_blocked, w: int, h: int, max_nodes: int = 4000):
    """Simple grid A* (4-neighbor). Returns a list of tile coords from start->goal (excluding start)."""

    if start == goal:
        return []

    sx, sy = start
    gx, gy = goal
    if not (0 <= sx < w and 0 <= sy < h and 0 <= gx < w and 0 <= gy < h):
        return []
    if is_blocked(gx, gy):
        return []

    def h_cost(x, y):
        return abs(x - gx) + abs(y - gy)

    open_heap = []
    heapq.heappush(open_heap, (h_cost(sx, sy), 0, (sx, sy)))

    came_from = {}
    g_score = {(sx, sy): 0}
    visited = 0

    while open_heap and visited < max_nodes:
        _, g, (x, y) = heapq.heappop(open_heap)
        visited += 1

        if (x, y) == (gx, gy):
            # Reconstruct path (excluding start)
            path = []
            cur = (x, y)
            while cur != (sx, sy):
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path

        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if is_blocked(nx, ny):
                continue

            ng = g + 1
            if ng < g_score.get((nx, ny), 10**9):
                g_score[(nx, ny)] = ng
                came_from[(nx, ny)] = (x, y)
                f = ng + h_cost(nx, ny)
                heapq.heappush(open_heap, (f, ng, (nx, ny)))

    return []


def inflate_blocked(blocked: set[tuple[int, int]], w: int, h: int, margin: int = 1):
    """Expand blocked tiles by `margin` (Chebyshev distance) to keep distance from walls."""

    if margin <= 0:
        return set(blocked)

    inflated = set(blocked)
    for (x, y) in blocked:
        for dy in range(-margin, margin + 1):
            for dx in range(-margin, margin + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    inflated.add((nx, ny))
    return inflated
