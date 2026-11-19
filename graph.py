"""
SSPU Campus Navigator - Route Guidance & Dijkstra Engine
Computes shortest path between campus facilities over predefined path graph,
calculates walking distance and duration, and generates human-friendly step-by-step directions.
"""

import heapq
import math
from database import get_nodes, get_edges, get_facility

WALKING_SPEED_METRES_PER_MIN = 80.0

def build_adjacency():
    nodes = {n["id"]: n for n in get_nodes()}
    edges = get_edges()
    adj = {nid: [] for nid in nodes}
    edge_map = {}

    for e in edges:
        u = e["from_node"]
        v = e["to_node"]
        d = float(e["distance"])
        if u in adj and v in adj:
            adj[u].append((v, d, e))
            adj[v].append((u, d, e))
            edge_map[(u, v)] = e
            edge_map[(v, u)] = e

    return nodes, adj, edge_map

def find_nearest_node(x, y, nodes):
    best_id = None
    best_dist = float("inf")
    for nid, node in nodes.items():
        dist = math.hypot(node["x"] - x, node["y"] - y)
        if dist < best_dist:
            best_dist = dist
            best_id = nid
    return best_id

def dijkstra(start_node, end_node, nodes, adj):
    if start_node not in nodes or end_node not in nodes:
        return None, float("inf")
    if start_node == end_node:
        return [start_node], 0.0

    distances = {n: float("inf") for n in nodes}
    previous = {n: None for n in nodes}
    distances[start_node] = 0.0

    pq = [(0.0, start_node)]

    while pq:
        cur_dist, u = heapq.heappop(pq)

        if cur_dist > distances[u]:
            continue

        if u == end_node:
            break

        for v, weight, _ in adj.get(u, []):
            new_dist = cur_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                previous[v] = u
                heapq.heappush(pq, (new_dist, v))

    if distances[end_node] == float("inf"):
        return None, float("inf")

    # Reconstruct path
    path = []
    curr = end_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    return path, distances[end_node]

def get_compass_direction(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx) * 180 / math.pi
    # Screen coordinates: y is downwards
    if -22.5 <= angle < 22.5:
        return "east"
    elif 22.5 <= angle < 67.5:
        return "southeast"
    elif 67.5 <= angle < 112.5:
        return "south"
    elif 112.5 <= angle < 157.5:
        return "southwest"
    elif angle >= 157.5 or angle < -157.5:
        return "west"
    elif -157.5 <= angle < -112.5:
        return "northwest"
    elif -112.5 <= angle < -67.5:
        return "north"
    else:
        return "northeast"

def generate_route(from_facility_id, to_facility_id):
    f1 = get_facility(from_facility_id)
    f2 = get_facility(to_facility_id)

    if not f1 or not f2:
        return {
            "success": False,
            "error": "One or both facilities not found."
        }

    # Handle same-facility case
    if int(from_facility_id) == int(to_facility_id):
        return {
            "success": True,
            "from_facility": f1,
            "to_facility": f2,
            "total_distance": 0.0,
            "walking_time_minutes": 0.0,
            "walking_time_formatted": "0 min",
            "is_same_facility": True,
            "steps": [
                f"You are already at {f1['name']} ({f1['building']}, {f1['floor']})."
            ],
            "coordinates": [[f1["x"], f1["y"]]],
            "nodes": []
        }

    nodes, adj, edge_map = build_adjacency()

    # Determine start and end nodes
    start_node = f1.get("node_id")
    if not start_node or start_node not in nodes:
        start_node = find_nearest_node(f1["x"], f1["y"], nodes)

    end_node = f2.get("node_id")
    if not end_node or end_node not in nodes:
        end_node = find_nearest_node(f2["x"], f2["y"], nodes)

    path_nodes, route_distance = dijkstra(start_node, end_node, nodes, adj)

    if path_nodes is None:
        return {
            "success": False,
            "from_facility": f1,
            "to_facility": f2,
            "error": "No navigable route found between the selected facilities.",
            "total_distance": 0.0,
            "walking_time_minutes": 0.0,
            "steps": ["No pathway exists connecting these two locations."]
        }

    # Assemble coordinates: start facility -> path nodes -> destination facility
    coords = [[f1["x"], f1["y"]]]
    for nid in path_nodes:
        n = nodes[nid]
        # Avoid duplicate coordinate if identical to start
        if not (abs(n["x"] - coords[-1][0]) < 1 and abs(n["y"] - coords[-1][1]) < 1):
            coords.append([n["x"], n["y"]])
    if not (abs(f2["x"] - coords[-1][0]) < 1 and abs(f2["y"] - coords[-1][1]) < 1):
        coords.append([f2["x"], f2["y"]])

    # Additional connector distances
    start_connector = round(math.hypot(f1["x"] - nodes[start_node]["x"], f1["y"] - nodes[start_node]["y"]) * 0.85, 1)
    end_connector = round(math.hypot(f2["x"] - nodes[end_node]["x"], f2["y"] - nodes[end_node]["y"]) * 0.85, 1)
    total_dist = round(route_distance + start_connector + end_connector, 1)
    
    walking_time_min = round(total_dist / WALKING_SPEED_METRES_PER_MIN, 1)
    if walking_time_min < 1.0:
        time_str = f"~{int(walking_time_min * 60)} sec"
    else:
        time_str = f"{walking_time_min:.1f} min"

    # Generate step-by-step instructions
    steps = []
    
    # Departure step
    if f1.get("floor") and f1["floor"] != "Ground Floor":
        steps.append(f"Exit {f1['name']} on {f1['floor']}; take stairs or elevator down to Ground Level exit.")
    else:
        steps.append(f"Exit {f1['name']} ({f1['building']}) towards {nodes[start_node]['name']}.")

    # Path traversal steps
    if len(path_nodes) > 1:
        for i in range(len(path_nodes) - 1):
            u_id = path_nodes[i]
            v_id = path_nodes[i + 1]
            u = nodes[u_id]
            v = nodes[v_id]
            edge = edge_map.get((u_id, v_id))
            dist = edge["distance"] if edge else round(math.hypot(v["x"] - u["x"], v["y"] - u["y"]) * 0.85, 1)
            heading = get_compass_direction(u["x"], u["y"], v["x"], v["y"])
            desc = edge.get("description") if edge and edge.get("description") else f"Walk {dist} m {heading} towards {v['name']}"
            steps.append(f"{desc} ({dist} m)")
    else:
        steps.append(f"Walk across courtyard towards {nodes[end_node]['name']} ({total_dist} m).")

    # Arrival step
    if f2.get("floor") and f2["floor"] != "Ground Floor":
        steps.append(f"Enter {f2['building']}; take stairs or elevator up to {f2['floor']}.")
    steps.append(f"Arrive at your destination: {f2['name']} ({f2['building']}, {f2['floor']}).")

    return {
        "success": True,
        "from_facility": f1,
        "to_facility": f2,
        "total_distance": total_dist,
        "walking_time_minutes": walking_time_min,
        "walking_time_formatted": time_str,
        "is_same_facility": False,
        "steps": steps,
        "coordinates": coords,
        "nodes": [nodes[nid] for nid in path_nodes]
    }
