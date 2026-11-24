"""
SSPU Campus Navigator - Main Flask Server
Serves the Kage scroll landing page at '/', the interactive Campus Navigator at '/app',
the Admin area at '/admin', and complete RESTful JSON API.
"""

import os
import re
import json
import sqlite3
import requests
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, send_from_directory, abort, make_response
)
from database import (
    init_db, get_facilities, get_facility, create_facility,
    update_facility, delete_facility, get_categories, get_buildings,
    get_nodes, get_edges, add_edge, delete_edge, get_audit_logs,
    verify_admin, log_audit
)
from graph import generate_route

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "sspu-navigator-secure-key-2026")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Ensure database is initialized on startup
with app.app_context():
    init_db()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Authentication required. Please log in as administrator."}), 401
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# Static and Landing Page Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    landing_path = os.path.join(app.root_path, "static", "landing", "index.html")
    if os.path.exists(landing_path):
        return send_from_directory(os.path.join(app.root_path, "static", "landing"), "index.html")
    # Graceful fallback if landing page is not yet populated
    return redirect(url_for("navigator_app"))

@app.route("/secret-pathways-assets/<path:subpath>")
def secret_pathways_assets(subpath):
    assets_dir = os.path.join(app.root_path, "static", "landing", "secret-pathways-assets")
    response = make_response(send_from_directory(assets_dir, subpath))
    # Add caching headers
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response

@app.route("/app")
def navigator_app():
    return render_template("app.html")

@app.route("/admin/login")
def admin_login_page():
    if session.get("user"):
        return redirect(url_for("admin_dashboard"))
    return render_template("login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("user"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin.html")

# -------------------------------------------------------------
# Authentication Endpoints
# -------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required."}), 400

    if verify_admin(username, password):
        session["user"] = username
        log_audit("ADMIN_LOGIN", f"Admin user '{username}' logged in successfully.")
        return jsonify({"success": True, "message": "Login successful.", "user": username})
    
    return jsonify({"success": False, "error": "Invalid username or password."}), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    user = session.pop("user", None)
    if user:
        log_audit("ADMIN_LOGOUT", f"Admin user '{user}' logged out.")
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/me", methods=["GET"])
def api_me():
    user = session.get("user")
    if user:
        return jsonify({"authenticated": True, "username": user})
    return jsonify({"authenticated": False, "username": None})

# -------------------------------------------------------------
# Facilities API Endpoints
# -------------------------------------------------------------

@app.route("/api/facilities", methods=["GET"])
def api_get_facilities():
    q = request.args.get("q")
    category = request.args.get("category")
    building = request.args.get("building")
    facilities = get_facilities(q=q, category=category, building=building)
    return jsonify({"success": True, "count": len(facilities), "facilities": facilities})

@app.route("/api/facilities/<int:fac_id>", methods=["GET"])
def api_get_facility(fac_id):
    facility = get_facility(fac_id)
    if not facility:
        return jsonify({"success": False, "error": "Facility not found."}), 404
    return jsonify({"success": True, "facility": facility})

@app.route("/api/facilities", methods=["POST"])
@admin_required
def api_create_facility():
    data = request.get_json(silent=True) or {}
    
    # Required validation
    required_fields = ["name", "category", "building", "floor", "description", "operating_hours", "x", "y"]
    missing = [f for f in required_fields if f not in data or str(data[f]).strip() == ""]
    if missing:
        return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        x_val = float(data["x"])
        y_val = float(data["y"])
        if not (0 <= x_val <= 1000 and 0 <= y_val <= 700):
            return jsonify({"success": False, "error": "Coordinates X (0-1000) and Y (0-700) are out of bounds."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Coordinates X and Y must be valid numbers."}), 400

    new_fac = create_facility(data)
    return jsonify({"success": True, "facility": new_fac, "message": "Facility created successfully."}), 201

@app.route("/api/facilities/<int:fac_id>", methods=["PUT"])
@admin_required
def api_update_facility(fac_id):
    fac = get_facility(fac_id)
    if not fac:
        return jsonify({"success": False, "error": "Facility not found."}), 404

    data = request.get_json(silent=True) or {}
    required_fields = ["name", "category", "building", "floor", "description", "operating_hours", "x", "y"]
    missing = [f for f in required_fields if f not in data or str(data[f]).strip() == ""]
    if missing:
        return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        x_val = float(data["x"])
        y_val = float(data["y"])
        if not (0 <= x_val <= 1000 and 0 <= y_val <= 700):
            return jsonify({"success": False, "error": "Coordinates X (0-1000) and Y (0-700) are out of bounds."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Coordinates X and Y must be valid numbers."}), 400

    updated_fac = update_facility(fac_id, data)
    return jsonify({"success": True, "facility": updated_fac, "message": "Facility updated successfully."})

@app.route("/api/facilities/<int:fac_id>", methods=["DELETE"])
@admin_required
def api_delete_facility(fac_id):
    fac = get_facility(fac_id)
    if not fac:
        return jsonify({"success": False, "error": "Facility not found."}), 404

    success = delete_facility(fac_id)
    if success:
        return jsonify({"success": True, "message": f"Facility '{fac['name']}' deleted successfully."})
    return jsonify({"success": False, "error": "Could not delete facility."}), 500

# -------------------------------------------------------------
# Metadata Endpoints
# -------------------------------------------------------------

@app.route("/api/categories", methods=["GET"])
def api_get_categories():
    categories = get_categories()
    return jsonify({"success": True, "categories": categories})

@app.route("/api/buildings", methods=["GET"])
def api_get_buildings():
    buildings = get_buildings()
    return jsonify({"success": True, "buildings": buildings})

# -------------------------------------------------------------
# Route Finder (Dijkstra)
# -------------------------------------------------------------

@app.route("/api/route", methods=["GET"])
def api_get_route():
    from_id = request.args.get("from")
    to_id = request.args.get("to")

    if not from_id or not to_id:
        return jsonify({"success": False, "error": "Both 'from' and 'to' facility IDs are required."}), 400

    try:
        from_id = int(from_id)
        to_id = int(to_id)
    except ValueError:
        return jsonify({"success": False, "error": "Facility IDs must be integers."}), 400

    route_info = generate_route(from_id, to_id)
    if not route_info["success"]:
        return jsonify(route_info), 404 if "not found" in route_info.get("error", "").lower() else 200

    return jsonify(route_info)

# -------------------------------------------------------------
# Path Graph Management Endpoints (Admin)
# -------------------------------------------------------------

@app.route("/api/paths", methods=["GET"])
def api_get_paths():
    nodes = get_nodes()
    edges = get_edges()
    return jsonify({"success": True, "nodes": nodes, "edges": edges})

@app.route("/api/paths/edges", methods=["POST"])
@admin_required
def api_add_edge():
    data = request.get_json(silent=True) or {}
    from_node = data.get("from_node")
    to_node = data.get("to_node")
    distance = data.get("distance")
    path_type = data.get("path_type", "footpath")
    description = data.get("description", "")

    if not from_node or not to_node or distance is None:
        return jsonify({"success": False, "error": "from_node, to_node and distance are required."}), 400

    edge_id = add_edge(from_node, to_node, distance, path_type, description)
    return jsonify({"success": True, "edge_id": edge_id, "message": "Path connection created successfully."}), 201

@app.route("/api/paths/edges/<int:edge_id>", methods=["DELETE"])
@admin_required
def api_delete_edge(edge_id):
    delete_edge(edge_id)
    return jsonify({"success": True, "message": f"Path connection {edge_id} removed."})

@app.route("/api/audit", methods=["GET"])
@admin_required
def api_get_audit():
    logs = get_audit_logs(limit=20)
    return jsonify({"success": True, "logs": logs})

# -------------------------------------------------------------
# Bonus "Ask the Campus" (Gemini with Keyword Matcher Fallback)
# -------------------------------------------------------------

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    query = data.get("question", "").strip()

    if not query:
        return jsonify({"success": False, "error": "Query question is required."}), 400

    all_facs = get_facilities()
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if gemini_api_key:
        try:
            # Use Gemini API to answer with facilities context
            prompt = f"""
You are the AI Campus Assistant for Symbiosis Skills and Professional University (SSPU), Kiwale, Pune.
User Question: "{query}"

Here is the campus directory context:
{json.dumps([{
    'id': f['id'],
    'name': f['name'],
    'category': f['category'],
    'building': f['building'],
    'floor': f['floor'],
    'description': f['description'],
    'operating_hours': f['operating_hours'],
    'is_open': f['is_open']
} for f in all_facs], indent=2)}

Provide a concise, helpful answer (2-3 sentences max) mentioning relevant buildings, floors, and operating hours.
Also identify matching facility IDs that should be highlighted on the campus map.
Respond strictly in JSON format:
{{
  "answer": "your answer here",
  "matched_facility_ids": [id1, id2]
}}
"""
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                res_data = res.json()
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)
                return jsonify({
                    "success": True,
                    "mode": "gemini",
                    "answer": parsed.get("answer", "Here are the matching campus facilities."),
                    "matched_facility_ids": parsed.get("matched_facility_ids", [])
                })
        except Exception as e:
            # Silently fall back to keyword matching
            pass

    # Keyword matcher fallback
    query_lower = query.lower()
    words = [w for w in re.findall(r'\b\w+\b', query_lower) if len(w) > 2 and w not in ["the", "and", "where", "what", "find", "how", "can"]]
    matches = []
    
    for f in all_facs:
        score = 0
        haystack = f"{f['name']} {f['category']} {f['building']} {f['floor']} {f['description']}".lower()
        for w in words:
            if w in f["name"].lower():
                score += 5
            elif w in f["category"].lower() or w in f["building"].lower():
                score += 3
            elif w in haystack:
                score += 1
        if score > 0:
            matches.append((score, f))

    matches.sort(key=lambda x: x[0], reverse=True)
    top_facs = [m[1] for m in matches[:4]]
    matched_ids = [f["id"] for f in top_facs]

    if top_facs:
        summary = f"Found {len(top_facs)} relevant location{'s' if len(top_facs)>1 else ''}: " + ", ".join([f"{f['name']} ({f['building']}, {f['floor']})" for f in top_facs])
    else:
        summary = "I couldn't find a direct match. Try searching for specific terms like 'Library', 'Lab', 'Hostel', 'Auditorium' or 'Canteen'."

    return jsonify({
        "success": True,
        "mode": "keyword_fallback",
        "answer": summary,
        "matched_facility_ids": matched_ids
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
