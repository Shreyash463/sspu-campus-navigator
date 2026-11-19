# SSPU Campus Navigator
### Symbi Skillympics 2026 — Web Technology (Problem Statement 32)
**Campus Navigation and Facility Directory for Symbiosis Skills and Professional University (SSPU), Kiwale, Pune**

---

## 1. Project Overview

**SSPU Campus Navigator** is an enterprise-grade, responsive campus navigation and facility directory platform engineered specifically for the Symbiosis Skills and Professional University (SSPU) campus at Kiwale, Pune. It empowers students, faculty members, visiting industry leaders, and guests to seamlessly explore 30+ facilities across departments, laboratories, auditoriums, offices, and amenities.

The solution integrates two complementary experiences:
1. **Cinematic Hero Experience (`/`):** A scroll-driven, WebGL-powered 3D introduction re-skinned from ThreeUI's *Kage* landing template (Three.js camera rig, cloth simulation, localized assets, zero external runtime CDN dependencies, and automatic CSS fallback).
2. **Interactive Campus Navigator (`/app`) & Admin Suite (`/admin`):** A high-performance, full-featured web application with an inline SVG top-down campus map, category and building filters, instant search-as-you-type, live "Open now / Closed" status calculations, Dijkstra shortest-path navigation with animated routes, and a protected administrative console with an interactive map coordinate picker.

---

## 2. Requirements Compliance Matrix

Every requirement from the official Symbi Skillympics 2026 Problem Statement 32 is strictly addressed:

| Req # | Problem Statement Requirement | Implementation in SSPU Campus Navigator | UI Location / Feature |
|:---:|:---|:---|:---|
| **1** | **Display facilities** (departments, laboratories, libraries, offices, cafeterias, auditoriums) | 32 realistic SSPU Pune facilities cataloged across 9 distinct categories with distinct color codes and iconography. | `/app` Directory list, Category filter chips, SVG map markers. |
| **2** | **Maintain facility information** (name, building, floor, description, operating hours) | Complete SQLite schema and data model preserving name, category, building, floor, description, operating hours, coordinates, and contact details. | SQLite `facilities` table, `/api/facilities/<id>`, Details card. |
| **3** | **Search facility** to quickly locate a room or service | Instant search-as-you-type indexing name, category, building, floor, and full description with live match count. | `/app` search input (`#facility-search-input`). |
| **4** | **Filter by category and building** | Combinable interactive category pills (All, Academic, Lab, Office, Library, Food, Sports, Hostel, Facility) and Building dropdown. | `/app` filter panel (`#category-chips-container`, `#building-filter-select`). |
| **5** | **Campus map with selectable markers** | Custom inline SVG map (roads, paths, landscaped lawns, sports arena, parking) with clickable pins and hover tooltips. | `/app` center map canvas (`#campus-svg-map`). |
| **6** | **Show facility details and location** | Selecting a facility centers map viewport, pulses marker, and renders details card with live "Open now / Closed" indicator based on operating hours. | `/app` Details panel (`#detail-card-panel`). |
| **7** | **Simple route description using predefined paths** | Dijkstra algorithm across 28 campus path nodes and 35 weighted walkway edges. Animates route polyline, computes total meters, walking time (80 m/min), and turn-by-turn steps. | `/app` Route drawer (`#route-drawer-panel`), `#map-route-layer`. |
| **8** | **Administrator management** (add, update, delete) | Authenticated session dashboard (`/admin`), form validation, interactive map coordinate click-picker, path graph manager, instant public sync, and audit log. | `/admin`, `/api/facilities`, `/api/paths`. |

---

## 3. Architecture & Tech Stack

```
+-----------------------------------------------------------------------------------+
|                                  BROWSER CLIENT                                   |
|                                                                                   |
|   Landing Page ("/")                    Campus Navigator ("/") & Admin ("/admin") |
|   +----------------------------+        +-------------------------------------+   |
|   | - Three.js WebGL Scene     |        | - Interactive Pan/Zoom SVG Map      |   |
|   | - Cloth Physics Simulation |        | - Instant Search & Combined Filters |   |
|   | - Localized WebP & Fonts   |        | - Dijkstra Animated Route Visualizer|   |
|   | - Automated CSS Fallback   |        | - Admin Map Picker & Path Manager   |   |
|   +----------------------------+        +-------------------------------------+   |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST JSON
                                           v
+-----------------------------------------------------------------------------------+
|                               BACKEND SERVICES                                    |
|                                                                                   |
|                           Flask Python Web Server (app.py)                        |
|   +---------------------------------------------------------------------------+   |
|   | Routing & Endpoints:                                                      |   |
|   |   GET  /                       -> Re-skinned Kage landing page            |   |
|   |   GET  /app                    -> Campus Navigator single-page app        |   |
|   |   GET  /admin                  -> Protected administrator dashboard       |   |
|   |   GET  /admin/login            -> Session authentication portal           |   |
|   |   REST /api/facilities         -> Facilities CRUD (GET, POST, PUT, DELETE)|   |
|   |   REST /api/route              -> Dijkstra shortest path calculation      |   |
|   |   REST /api/paths              -> Node & edge network graph management    |   |
|   |   POST /api/ask                -> Smart Q&A (Gemini AI + Keyword matcher) |   |
|   +---------------------------------------------------------------------------+   |
|                                           |                                       |
|             +-----------------------------+-----------------------------+         |
|             v                                                           v         |
|    Dijkstra Path Engine (graph.py)                             SQLite DB (campus.db)
|    - 28 Waypoint nodes                                         - facilities table |
|    - 35 Walkway edges                                          - path_nodes       |
|    - Turn-by-turn heading analysis                             - path_edges       |
|    - Walking time calculation (80 m/min)                       - audit_logs       |
|    - Floor & level transitions                                 - users (admins)   |
+-----------------------------------------------------------------------------------+
```

- **Backend:** Python 3.10+, Flask 3.1.0, Werkzeug 3.1.3 (password hashing).
- **Database:** SQLite 3 (`campus.db`) with parameterized SQL queries and full foreign keys.
- **Frontend:** Vanilla HTML5, CSS3 with Global Design Tokens, Vanilla JavaScript (ES6+), zero frontend build tools or npm bundler required.
- **3D Graphics Engine:** Three.js r128 (localized `three.min.js`, self-hosted Onest Latin typography, self-hosted WebP textures).
- **Automated Testing:** pytest for API verification, Playwright with Chromium & SwiftShader for E2E browser automation.

---

## 4. Setup and Quick Start

### Prerequisites
- Python 3.10 or higher.
- Standard internet connection for initial virtual environment setup only (runtime runs 100% offline).

### One-Command Launch
```bash
# 1. Navigate to the project directory
cd sspu-campus-navigator

# 2. Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Run the application
python app.py
```

Open your browser and navigate to:
- **Landing Page:** [http://localhost:5000/](http://localhost:5000/)
- **Campus Navigator:** [http://localhost:5000/app](http://localhost:5000/app)
- **Admin Dashboard:** [http://localhost:5000/admin](http://localhost:5000/admin)

> [!NOTE]
> All facility names, locations, and path coordinates are seeded for demonstration purposes. Everything is editable and configurable via the `/admin` console.

---

## 5. Demonstration Credentials

Demo credentials are automatically displayed on the login page and seeded in `campus.db`:
- **Username:** `admin`
- **Password:** `Admin@123`
- **Role:** Administrator (Full Read/Write/Delete + Path Graph & Audit Access)

---

## 6. REST API Reference

| Endpoint | Method | Authentication | Parameters / Payload | Description |
|:---|:---:|:---:|:---|:---|
| `/api/facilities` | `GET` | Public | `q` (search), `category`, `building` | List all facilities with optional search & filter. |
| `/api/facilities/<id>` | `GET` | Public | *None* | Get details of a single facility. |
| `/api/facilities` | `POST` | **Admin Session** | `{ name, category, building, floor, description, operating_hours, x, y, contact }` | Create a new campus facility. |
| `/api/facilities/<id>` | `PUT` | **Admin Session** | `{ name, category, building, floor, ... }` | Update facility details. |
| `/api/facilities/<id>` | `DELETE` | **Admin Session** | *None* | Delete a facility from directory and map. |
| `/api/categories` | `GET` | Public | *None* | Retrieve list of all unique facility categories. |
| `/api/buildings` | `GET` | Public | *None* | Retrieve list of all campus building blocks. |
| `/api/route` | `GET` | Public | `from` (origin ID), `to` (destination ID) | Compute Dijkstra shortest path, duration, and turns. |
| `/api/paths` | `GET` | Public | *None* | Get full node and edge topology for map rendering. |
| `/api/paths/nodes` | `POST` | **Admin Session** | `{ label, building, floor, x, y }` | Add a new navigational waypoint. |
| `/api/paths/edges` | `POST` | **Admin Session** | `{ node1, node2, distance, bidirectional }` | Connect two nodes with a walkable edge. |
| `/api/paths/edges/<id>` | `DELETE` | **Admin Session** | *None* | Delete an edge connection. |
| `/api/audit` | `GET` | **Admin Session** | *None* | Fetch the last 20 administrative actions. |
| `/api/login` | `POST` | Public | `{ username, password }` | Authenticate admin user and establish session. |
| `/api/logout` | `POST` | **Admin Session** | *None* | Invalidate session. |
| `/api/me` | `GET` | Public | *None* | Check current authentication status. |
| `/api/ask` | `POST` | Public | `{ query }` | Natural language campus query helper (bonus). |

---

## 7. Shortest Path Navigation (Dijkstra)

The path engine in `graph.py` computes real-time walking directions using Dijkstra's algorithm across an undirected weighted graph:
- **Waypoints ($V$):** 28 pre-mapped nodes representing campus gates, crossroad junctions, building porticos, stairwells, and department thresholds.
- **Walkways ($E$):** 35 measured edges with Euclidean-calibrated physical distances in metres.
- **Pace Calibration:** Walking speed is normalized to $80\text{ m/min}$ (~$4.8\text{ km/h}$).
- **Turn-by-Turn Guidance:** Calculates bearing changes between successive path vectors ($\Delta \theta$) to output directional instructions:
  - Slight left / Sharp left ($30^\circ \le \theta \le 120^\circ$)
  - Straight ahead ($-30^\circ < \theta < 30^\circ$)
  - Slight right / Sharp right ($-120^\circ \le \theta \le -30^\circ$)
- **Vertical Routing:** Detects when origin and destination reside on different floors (e.g., Ground Floor to Floor 2) and injects stair/elevator transitions into the directions.
- **Edge Cases:** Identical start/destination points return instantaneous 0 m distance with a courteous note; unreachable points return clear advisories.

---

## 8. Two-Minute Judge Demo Script

1. **The Entrance (Landing Page at `/`):**
   - Open `http://localhost:5000/`.
   - Observe the 3D dark-mode scene, cloth-simulated campus banners, and wordmark reveal.
   - Click **"Open Navigator"** in the top navigation bar or the floating **"Skip intro"** button at bottom-left to transition directly to the application.
2. **Instant Search & Dynamic Filtering (`/app`):**
   - Type `"Robotics"` in the search bar — see results filter instantaneously to 1 item and the map focus on the Mechatronics lab.
   - Click **"Reset"** or clear the search.
   - Click the **"Laboratory"** category chip and select **"Mechanical & Workshops Block (C)"** from the building dropdown — verify combined filtering in real time.
3. **Interactive Map & Facility Details:**
   - Click any pin on the map (e.g., **Central Library**).
   - Observe smooth auto-centering and zoom.
   - Note the **Details Card** showing category badge, location, contact, and the live **"Open now"** status indicator with operating hours.
4. **Campus Wayfinding & Pathfinding:**
   - In the details card, click **"Directions To Here"**.
   - Select **"Main Gate & Security Post"** as the origin.
   - Click **"Find Walking Route"**.
   - Watch the animated route polyline draw on the SVG map from the gate to the library.
   - Inspect the route summary: total distance in metres, estimated walking time in minutes, and step-by-step navigational milestones.
5. **Administrative Control (`/admin`):**
   - Click **"Admin"** in the header. Enter `admin` / `Admin@123`.
   - Click **"+ Add Facility"**.
   - Fill in `"Automated Inspection & Metrology Lab"`.
   - Click **"📍 Pick on Map"** — click directly on the interactive campus map modal to set exact $(X, Y)$ coordinates.
   - Save the facility.
   - Switch back to the public `/app` tab, search for `"Metrology"` — **confirm it appears on the public map immediately without any server restart!**
   - View the **"Audit Log"** tab in Admin to verify the recorded `CREATE_FACILITY` action.

---

## 9. Third-Party Code Attribution

- **Landing Page 3D Experience (`/`):** Built upon the open-source *Kage* landing page template by ThreeUI (featuring Three.js camera transitions and cloth physics).
  - *SSPU Customizations:* Completely re-skinned for SSPU Kiwale Pune; 100% of Japanese characters and copy replaced with English institutional content; fonts localized with Google Onest Latin woff2; remote Supabase CDN images replaced with self-hosted WebP campus visuals; integrated skip-intro navigation, direct links into `/app`, and an automated CSS-only fallback.
- **Campus Navigator Core Application (`/app`, `/admin`, API, Map, Dijkstra engine):** 100% original custom implementation created for Symbi Skillympics 2026.
