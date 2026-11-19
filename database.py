"""
SSPU Campus Navigator - Database Layer
Manages SQLite database, initialization, migrations, seeding,
CRUD operations, admin authentication, audit logging, and hours evaluation.
"""

import sqlite3
import os
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from seed_data import CATEGORIES, BUILDINGS, FACILITIES, NODES, EDGES

DB_PATH = os.path.join(os.path.dirname(__file__), "campus.db")

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_INDEX = {day: idx for idx, day in enumerate(DAY_NAMES)}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force_reseed=False):
    conn = get_db()
    cur = conn.cursor()

    if force_reseed:
        cur.executescript("""
            DROP TABLE IF EXISTS audit_logs;
            DROP TABLE IF EXISTS path_edges;
            DROP TABLE IF EXISTS path_nodes;
            DROP TABLE IF EXISTS facilities;
            DROP TABLE IF EXISTS admins;
        """)

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            building TEXT NOT NULL,
            floor TEXT NOT NULL,
            description TEXT NOT NULL,
            operating_hours TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            contact TEXT,
            node_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS path_nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            building TEXT,
            floor TEXT
        );

        CREATE TABLE IF NOT EXISTS path_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_node TEXT NOT NULL,
            to_node TEXT NOT NULL,
            distance REAL NOT NULL,
            path_type TEXT DEFAULT 'footpath',
            description TEXT,
            FOREIGN KEY (from_node) REFERENCES path_nodes (id) ON DELETE CASCADE,
            FOREIGN KEY (to_node) REFERENCES path_nodes (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed Admin if not exists
    cur.execute("SELECT id FROM admins WHERE username = 'admin'")
    if not cur.fetchone():
        hashed = generate_password_hash("Admin@123")
        cur.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ("admin", hashed))
        cur.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", 
                    ("INIT_SYSTEM", "Initialized default administrator account (admin)"))

    # Seed Path Nodes if empty
    cur.execute("SELECT COUNT(*) as count FROM path_nodes")
    if cur.fetchone()["count"] == 0:
        for node in NODES:
            cur.execute("""
                INSERT INTO path_nodes (id, name, x, y, building, floor)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (node["id"], node["name"], node["x"], node["y"], node.get("building"), node.get("floor")))

    # Seed Path Edges if empty
    cur.execute("SELECT COUNT(*) as count FROM path_edges")
    if cur.fetchone()["count"] == 0:
        for edge in EDGES:
            cur.execute("""
                INSERT INTO path_edges (id, from_node, to_node, distance, path_type, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (edge["id"], edge["from_node"], edge["to_node"], edge["distance"], edge["path_type"], edge["description"]))

    # Seed Facilities if empty
    cur.execute("SELECT COUNT(*) as count FROM facilities")
    if cur.fetchone()["count"] == 0:
        for f in FACILITIES:
            cur.execute("""
                INSERT INTO facilities (id, name, category, building, floor, description, operating_hours, x, y, contact, node_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f["id"], f["name"], f["category"], f["building"], f["floor"],
                f["description"], f["operating_hours"], f["x"], f["y"],
                f.get("contact", ""), f.get("node_id", "")
            ))
        cur.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", 
                    ("SEED_DATA", f"Seeded {len(FACILITIES)} facilities and {len(EDGES)} path connections"))

    conn.commit()
    conn.close()

def check_is_open(hours_str, current_dt=None):
    """
    Parses human-readable operating hours and returns (is_open: bool, status_badge: str).
    Examples:
      - '24 Hours', '24/7' -> True, 'Open 24/7'
      - 'Mon-Sat 09:00-17:00' -> True/False depending on current day & time
      - '09:00-17:00' -> True/False (assumes daily)
    """
    if not hours_str:
        return False, "Hours unavailable"
    
    clean = hours_str.strip().lower()
    if "24 hour" in clean or "24/7" in clean or "24 hr" in clean:
        return True, "Open 24 Hours"

    if current_dt is None:
        current_dt = datetime.now()

    cur_day_idx = current_dt.weekday() # 0 = Mon, 6 = Sun
    cur_time = current_dt.time()

    # Search for time range pattern e.g. 09:00-17:00 or 9:00 - 17:00
    time_match = re.search(r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})', hours_str)
    if not time_match:
        return True, hours_str # fallback to open if cannot strictly parse

    sh, sm, eh, em = map(int, time_match.groups())
    start_time = datetime.strptime(f"{sh:02d}:{sm:02d}", "%H:%M").time()
    end_time = datetime.strptime(f"{eh:02d}:{em:02d}", "%H:%M").time()

    # Determine day bounds
    active_days = set(range(7)) # default all days
    day_match = re.search(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*-\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', hours_str, re.IGNORECASE)
    if day_match:
        d1, d2 = day_match.group(1).capitalize(), day_match.group(2).capitalize()
        i1, i2 = DAY_INDEX[d1], DAY_INDEX[d2]
        if i1 <= i2:
            active_days = set(range(i1, i2 + 1))
        else:
            active_days = set(range(i1, 7)) | set(range(0, i2 + 1))

    if cur_day_idx not in active_days:
        return False, f"Closed today ({DAY_NAMES[cur_day_idx]})"

    if start_time <= cur_time <= end_time:
        return True, f"Open now · Closes at {eh:02d}:{em:02d}"
    elif cur_time < start_time:
        return False, f"Closed now · Opens at {sh:02d}:{sm:02d}"
    else:
        return False, f"Closed · Closed at {eh:02d}:{em:02d}"

def get_facilities(q=None, category=None, building=None):
    conn = get_db()
    query = "SELECT * FROM facilities WHERE 1=1"
    params = []

    if q:
        query += """ AND (
            name LIKE ? OR 
            building LIKE ? OR 
            floor LIKE ? OR 
            description LIKE ? OR 
            category LIKE ?
        )"""
        pattern = f"%{q.strip()}%"
        params.extend([pattern, pattern, pattern, pattern, pattern])

    if category and category.lower() != 'all':
        query += " AND LOWER(category) = ?"
        params.append(category.strip().lower())

    if building and building.lower() != 'all':
        query += " AND LOWER(building) = ?"
        params.append(building.strip().lower())

    query += " ORDER BY name ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        is_open, status_badge = check_is_open(d["operating_hours"])
        d["is_open"] = is_open
        d["status_badge"] = status_badge
        result.append(d)
    return result

def get_facility(facility_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM facilities WHERE id = ?", (facility_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    is_open, status_badge = check_is_open(d["operating_hours"])
    d["is_open"] = is_open
    d["status_badge"] = status_badge
    return d

def create_facility(data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO facilities (name, category, building, floor, description, operating_hours, x, y, contact, node_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["category"], data["building"], data["floor"],
        data["description"], data["operating_hours"], float(data["x"]), float(data["y"]),
        data.get("contact", ""), data.get("node_id", "")
    ))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_audit("CREATE_FACILITY", f"Created facility ID {new_id}: {data['name']} ({data['building']})")
    return get_facility(new_id)

def update_facility(facility_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE facilities
        SET name = ?, category = ?, building = ?, floor = ?, description = ?,
            operating_hours = ?, x = ?, y = ?, contact = ?, node_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        data["name"], data["category"], data["building"], data["floor"],
        data["description"], data["operating_hours"], float(data["x"]), float(data["y"]),
        data.get("contact", ""), data.get("node_id", ""), facility_id
    ))
    conn.commit()
    conn.close()
    log_audit("UPDATE_FACILITY", f"Updated facility ID {facility_id}: {data['name']}")
    return get_facility(facility_id)

def delete_facility(facility_id):
    fac = get_facility(facility_id)
    if not fac:
        return False
    conn = get_db()
    conn.execute("DELETE FROM facilities WHERE id = ?", (facility_id,))
    conn.commit()
    conn.close()
    log_audit("DELETE_FACILITY", f"Deleted facility ID {facility_id}: {fac['name']}")
    return True

def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM facilities ORDER BY category ASC").fetchall()
    conn.close()
    cat_names = [r["category"] for r in rows]
    # Merge with full category metadata
    meta_map = {c["name"].lower(): c for c in CATEGORIES}
    result = []
    for c in cat_names:
        meta = meta_map.get(c.lower(), {"id": c.lower().replace(" ", "-"), "name": c, "color": "#c9a24a", "icon": "tag"})
        result.append(meta)
    return result

def get_buildings():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT building FROM facilities ORDER BY building ASC").fetchall()
    conn.close()
    return [r["building"] for r in rows]

def get_nodes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM path_nodes ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_edges():
    conn = get_db()
    rows = conn.execute("""
        SELECT e.*, 
               n1.name as from_name, n1.x as from_x, n1.y as from_y,
               n2.name as to_name, n2.x as to_x, n2.y as to_y
        FROM path_edges e
        JOIN path_nodes n1 ON e.from_node = n1.id
        JOIN path_nodes n2 ON e.to_node = n2.id
        ORDER BY e.id ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_edge(from_node, to_node, distance, path_type="footpath", description=""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO path_edges (from_node, to_node, distance, path_type, description)
        VALUES (?, ?, ?, ?, ?)
    """, (from_node, to_node, float(distance), path_type, description))
    edge_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_audit("ADD_EDGE", f"Added path connection between {from_node} and {to_node} ({distance}m)")
    return edge_id

def delete_edge(edge_id):
    conn = get_db()
    conn.execute("DELETE FROM path_edges WHERE id = ?", (edge_id,))
    conn.commit()
    conn.close()
    log_audit("DELETE_EDGE", f"Deleted path edge ID {edge_id}")
    return True

def log_audit(action, details):
    try:
        conn = get_db()
        conn.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", (action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging audit: {e}")

def get_audit_logs(limit=20):
    conn = get_db()
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def verify_admin(username, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row and check_password_hash(row["password_hash"], password):
        return True
    return False
