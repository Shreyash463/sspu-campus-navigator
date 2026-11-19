"""
SSPU Campus Navigator - Seed Data
Contains realistic facilities, buildings, categories, path nodes, and edges
for Symbiosis Skills and Professional University (SSPU), Kiwale, Pune.
All data is placeholder and fully editable via the admin panel.
"""

import math

CATEGORIES = [
    {"id": "academic", "name": "Academic", "color": "#ff5a3c", "icon": "graduation-cap"},
    {"id": "laboratory", "name": "Laboratory", "color": "#e0231c", "icon": "flask"},
    {"id": "library", "name": "Library", "color": "#c9a24a", "icon": "book-open"},
    {"id": "administrative", "name": "Administrative", "color": "#4a90e2", "icon": "building"},
    {"id": "cafeteria", "name": "Cafeteria", "color": "#50e3c2", "icon": "utensils"},
    {"id": "auditorium", "name": "Auditorium & Events", "color": "#b8e986", "icon": "theater-masks"},
    {"id": "sports", "name": "Sports & Recreation", "color": "#bd10e0", "icon": "running"},
    {"id": "services", "name": "Student Services", "color": "#f5a623", "icon": "handshake"}
]

BUILDINGS = [
    "Main Entrance & Plaza",
    "Administrative Block",
    "Central Library & Knowledge Center",
    "Engineering & Tech Block (A)",
    "Science & Computing Hub (B)",
    "Mechanical & Workshops Block (C)",
    "Auditorium & Convention Hall",
    "Student Amenities & Cafeteria",
    "Sports Complex & Stadium",
    "Hostel Quadrangle",
    "Innovation & Incubation Hub",
    "Health & Medical Center"
]

FACILITIES = [
    {
        "id": 1,
        "name": "Main Campus Gate & Security Post",
        "category": "Student Services",
        "building": "Main Entrance & Plaza",
        "floor": "Ground Floor",
        "description": "Primary security check-in, visitor registration, campus map kiosk, and 24/7 security control post.",
        "operating_hours": "24 Hours",
        "x": 120, "y": 640,
        "contact": "+91 20 6793 5000",
        "node_id": "N_GATE"
    },
    {
        "id": 2,
        "name": "ATM & Banking Kiosk",
        "category": "Student Services",
        "building": "Main Entrance & Plaza",
        "floor": "Ground Floor",
        "description": "24/7 automated teller machine providing banking and cash withdrawal services for students and staff.",
        "operating_hours": "24 Hours",
        "x": 160, "y": 620,
        "contact": "Toll Free: 1800 425 3800",
        "node_id": "N_ENTRANCE_PLAZA"
    },
    {
        "id": 3,
        "name": "Central Administrative Office",
        "category": "Administrative",
        "building": "Administrative Block",
        "floor": "1st Floor",
        "description": "Registrar office, university general administration, student record verifications, and public relations.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 230, "y": 480,
        "contact": "+91 20 6793 5010 / admin@sspu.ac.in",
        "node_id": "N_ADMIN_ENTRANCE"
    },
    {
        "id": 4,
        "name": "Accounts & Finance Office",
        "category": "Administrative",
        "building": "Administrative Block",
        "floor": "Ground Floor",
        "description": "Tuition fee payments, student scholarships, financial clearances, receipts, and payroll queries.",
        "operating_hours": "Mon-Fri 09:30-16:30",
        "x": 210, "y": 490,
        "contact": "+91 20 6793 5015 / accounts@sspu.ac.in",
        "node_id": "N_ADMIN_ENTRANCE"
    },
    {
        "id": 5,
        "name": "Vice Chancellor's Secretariat",
        "category": "Administrative",
        "building": "Administrative Block",
        "floor": "2nd Floor",
        "description": "Office of the Vice Chancellor and Academic Council executive conference hall.",
        "operating_hours": "Mon-Fri 09:00-18:00",
        "x": 250, "y": 460,
        "contact": "+91 20 6793 5001 / vc@sspu.ac.in",
        "node_id": "N_ADMIN_ENTRANCE"
    },
    {
        "id": 6,
        "name": "Training & Placement Cell",
        "category": "Administrative",
        "building": "Administrative Block",
        "floor": "1st Floor",
        "description": "Corporate recruitment relations, campus interviews, career counseling, and industry internship desk.",
        "operating_hours": "Mon-Sat 09:00-17:30",
        "x": 230, "y": 460,
        "contact": "+91 20 6793 5030 / placements@sspu.ac.in",
        "node_id": "N_ADMIN_ENTRANCE"
    },
    {
        "id": 7,
        "name": "Examination & Assessment Cell",
        "category": "Administrative",
        "building": "Administrative Block",
        "floor": "2nd Floor",
        "description": "University examinations controller, grade transcripts, re-evaluations, and degree certificates.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 250, "y": 490,
        "contact": "+91 20 6793 5022 / exam@sspu.ac.in",
        "node_id": "N_ADMIN_ENTRANCE"
    },
    {
        "id": 8,
        "name": "Central Library",
        "category": "Library",
        "building": "Central Library & Knowledge Center",
        "floor": "Ground Floor",
        "description": "Extensive collection of engineering, skill technology and humanities books, periodicals, and lending desk.",
        "operating_hours": "Mon-Sat 08:00-21:00",
        "x": 230, "y": 300,
        "contact": "+91 20 6793 5040 / library@sspu.ac.in",
        "node_id": "N_LIBRARY_ENTRANCE"
    },
    {
        "id": 9,
        "name": "Digital Knowledge Repository & Reading Hall",
        "category": "Library",
        "building": "Central Library & Knowledge Center",
        "floor": "1st Floor",
        "description": "High-speed internet workstations, IEEE & ACM digital database access, e-journals, and silent study zones.",
        "operating_hours": "Mon-Sun 08:00-22:00",
        "x": 250, "y": 280,
        "contact": "+91 20 6793 5042",
        "node_id": "N_LIBRARY_ENTRANCE"
    },
    {
        "id": 10,
        "name": "Campus Health & Medical Centre",
        "category": "Student Services",
        "building": "Health & Medical Center",
        "floor": "Ground Floor",
        "description": "Outpatient clinic, emergency first aid, doctor consultation, paramedic support, and ambulance bay.",
        "operating_hours": "24 Hours",
        "x": 120, "y": 400,
        "contact": "+91 20 6793 5099 / Emergency Ext 108",
        "node_id": "N_MEDICAL_ENTRANCE"
    },
    {
        "id": 11,
        "name": "Student Counseling & Wellness Cell",
        "category": "Student Services",
        "building": "Health & Medical Center",
        "floor": "1st Floor",
        "description": "Confidential mental health guidance, psychological counseling, stress management, and wellbeing workshops.",
        "operating_hours": "Mon-Fri 10:00-16:00",
        "x": 120, "y": 380,
        "contact": "+91 20 6793 5095 / wellness@sspu.ac.in",
        "node_id": "N_MEDICAL_ENTRANCE"
    },
    {
        "id": 12,
        "name": "Mechanical Engineering Department",
        "category": "Academic",
        "building": "Engineering & Tech Block (A)",
        "floor": "1st Floor",
        "description": "Faculty chambers, student mentorship desks, departmental seminar room, and smart lecture theaters.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 450, "y": 180,
        "contact": "+91 20 6793 5050 / mech@sspu.ac.in",
        "node_id": "N_ENGINEERING_ENTRANCE"
    },
    {
        "id": 13,
        "name": "Electrical & Electronics Engineering Dept",
        "category": "Academic",
        "building": "Engineering & Tech Block (A)",
        "floor": "2nd Floor",
        "description": "Offices for Electrical, Mechatronics and Electronics faculty, project display rooms, and department office.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 490, "y": 180,
        "contact": "+91 20 6793 5055 / eee@sspu.ac.in",
        "node_id": "N_ENGINEERING_ENTRANCE"
    },
    {
        "id": 14,
        "name": "VLSI Design & Embedded Systems Lab",
        "category": "Laboratory",
        "building": "Engineering & Tech Block (A)",
        "floor": "2nd Floor",
        "description": "FPGA test benches, Cadence EDA suites, ARM Cortex microcontroller development boards, and logic analyzers.",
        "operating_hours": "Mon-Fri 08:30-18:00",
        "x": 500, "y": 200,
        "contact": "+91 20 6793 5058",
        "node_id": "N_ENGINEERING_ENTRANCE"
    },
    {
        "id": 15,
        "name": "IoT & Sensors Development Laboratory",
        "category": "Laboratory",
        "building": "Engineering & Tech Block (A)",
        "floor": "3rd Floor",
        "description": "Rapid hardware prototyping kits, LoRaWAN gateways, sensor calibration rigs, and 3D printing equipment.",
        "operating_hours": "Mon-Fri 09:00-17:30",
        "x": 470, "y": 210,
        "contact": "+91 20 6793 5059",
        "node_id": "N_ENGINEERING_ENTRANCE"
    },
    {
        "id": 16,
        "name": "CSE & Data Science Department",
        "category": "Academic",
        "building": "Science & Computing Hub (B)",
        "floor": "1st Floor",
        "description": "Head of Department office, computer science academic counseling, tutorial rooms, and faculty lounges.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 680, "y": 180,
        "contact": "+91 20 6793 5060 / cse@sspu.ac.in",
        "node_id": "N_COMPUTING_ENTRANCE"
    },
    {
        "id": 17,
        "name": "IT & Systems Department",
        "category": "Academic",
        "building": "Science & Computing Hub (B)",
        "floor": "Ground Floor",
        "description": "Information Technology departmental administration, curriculum coordinator desk, and conference hall.",
        "operating_hours": "Mon-Sat 09:00-17:00",
        "x": 660, "y": 190,
        "contact": "+91 20 6793 5062 / it@sspu.ac.in",
        "node_id": "N_COMPUTING_ENTRANCE"
    },
    {
        "id": 18,
        "name": "Advanced AI & Cloud Computing Lab",
        "category": "Laboratory",
        "building": "Science & Computing Hub (B)",
        "floor": "2nd Floor",
        "description": "High-performance GPU cluster (NVIDIA A100), deep learning development rigs, and cloud architecture simulators.",
        "operating_hours": "Mon-Sat 08:30-18:30",
        "x": 730, "y": 210,
        "contact": "+91 20 6793 5066",
        "node_id": "N_COMPUTING_ENTRANCE"
    },
    {
        "id": 19,
        "name": "Software Engineering & Web Tech Lab",
        "category": "Laboratory",
        "building": "Science & Computing Hub (B)",
        "floor": "1st Floor",
        "description": "Full-stack development environments, DevOps CI/CD pipelines, container testbeds, and agile scrum pods.",
        "operating_hours": "Mon-Fri 08:30-18:00",
        "x": 690, "y": 210,
        "contact": "+91 20 6793 5068",
        "node_id": "N_COMPUTING_ENTRANCE"
    },
    {
        "id": 20,
        "name": "Cyber Security & Digital Forensics Lab",
        "category": "Laboratory",
        "building": "Science & Computing Hub (B)",
        "floor": "3rd Floor",
        "description": "Air-gapped ethical hacking network, SIEM monitoring dashboards, malware reverse engineering workstations.",
        "operating_hours": "Mon-Fri 09:00-17:30",
        "x": 750, "y": 200,
        "contact": "+91 20 6793 5069",
        "node_id": "N_COMPUTING_ENTRANCE"
    },
    {
        "id": 21,
        "name": "Automobile Systems & CAD/CAM Lab",
        "category": "Laboratory",
        "building": "Mechanical & Workshops Block (C)",
        "floor": "Ground Floor",
        "description": "Vehicle powertrain test benches, chassis dynamometers, SolidWorks/CATIA workstations, and EV battery testing.",
        "operating_hours": "Mon-Fri 08:30-17:30",
        "x": 860, "y": 190,
        "contact": "+91 20 6793 5075",
        "node_id": "N_WORKSHOP_ENTRANCE"
    },
    {
        "id": 22,
        "name": "CNC Machining & Robotics Workshop",
        "category": "Laboratory",
        "building": "Mechanical & Workshops Block (C)",
        "floor": "Ground Floor",
        "description": "5-axis industrial CNC milling centers, robotic arc welding cells, precision lathe rows, and metrology room.",
        "operating_hours": "Mon-Sat 08:30-17:00",
        "x": 880, "y": 230,
        "contact": "+91 20 6793 5077",
        "node_id": "N_WORKSHOP_ENTRANCE"
    },
    {
        "id": 23,
        "name": "University Grand Auditorium",
        "category": "Auditorium & Events",
        "building": "Auditorium & Convention Hall",
        "floor": "Ground Floor",
        "description": "1,200-seater air-conditioned acoustic auditorium for convocation ceremonies, keynote symposiums, and cultural events.",
        "operating_hours": "Mon-Sat 08:30-20:00",
        "x": 460, "y": 390,
        "contact": "+91 20 6793 5080 / events@sspu.ac.in",
        "node_id": "N_AUDITORIUM_ENTRANCE"
    },
    {
        "id": 24,
        "name": "Mini Seminar Hall - Symphony",
        "category": "Auditorium & Events",
        "building": "Auditorium & Convention Hall",
        "floor": "1st Floor",
        "description": "250-seater multimedia amphitheater equipped with dual 4K laser projection, surround sound, and video conferencing.",
        "operating_hours": "Mon-Sat 09:00-18:00",
        "x": 480, "y": 370,
        "contact": "+91 20 6793 5082",
        "node_id": "N_AUDITORIUM_ENTRANCE"
    },
    {
        "id": 25,
        "name": "Central Cafeteria & Food Court",
        "category": "Cafeteria",
        "building": "Student Amenities & Cafeteria",
        "floor": "Ground Floor",
        "description": "Multi-cuisine dining hall serving hygienic North Indian, South Indian, Continental meals, fresh juices, and snacks.",
        "operating_hours": "Mon-Sun 07:30-21:30",
        "x": 650, "y": 380,
        "contact": "+91 20 6793 5088",
        "node_id": "N_CAFETERIA_ENTRANCE"
    },
    {
        "id": 26,
        "name": "Campus Book & Stationery Store",
        "category": "Student Services",
        "building": "Student Amenities & Cafeteria",
        "floor": "Ground Floor",
        "description": "Engineering drawing instruments, university notebooks, textbooks, xerox, spiral binding, and academic supplies.",
        "operating_hours": "Mon-Sat 09:00-19:00",
        "x": 680, "y": 390,
        "contact": "+91 20 6793 5089",
        "node_id": "N_CAFETERIA_ENTRANCE"
    },
    {
        "id": 27,
        "name": "Nescafe Coffee Kiosk & Bakery",
        "category": "Cafeteria",
        "building": "Main Entrance & Plaza",
        "floor": "Ground Floor",
        "description": "Quick-serve outdoor kiosk serving freshly brewed espresso, iced beverages, sandwiches, and fresh pastries.",
        "operating_hours": "Mon-Sat 08:00-20:00",
        "x": 370, "y": 310,
        "contact": "Kiosk #3",
        "node_id": "N_CENTER_CROSS"
    },
    {
        "id": 28,
        "name": "Athletics Track & Football Arena",
        "category": "Sports & Recreation",
        "building": "Sports Complex & Stadium",
        "floor": "Ground Floor",
        "description": "FIFA standard natural grass football turf, 400m synthetic running track, spectator stands, and floodlights.",
        "operating_hours": "Mon-Sun 06:00-21:00",
        "x": 600, "y": 560,
        "contact": "+91 20 6793 5090 / sports@sspu.ac.in",
        "node_id": "N_TRACK_ENTRANCE"
    },
    {
        "id": 29,
        "name": "Indoor Sports Complex & Gymnasium",
        "category": "Sports & Recreation",
        "building": "Sports Complex & Stadium",
        "floor": "Ground Floor",
        "description": "Teakwood badminton courts, table tennis arena, Olympic weightlifting gym, and cardio fitness center.",
        "operating_hours": "Mon-Sun 06:00-22:00",
        "x": 840, "y": 520,
        "contact": "+91 20 6793 5092",
        "node_id": "N_INDOOR_SPORTS_ENTRANCE"
    },
    {
        "id": 30,
        "name": "Hostel Quadrangle & Common Rooms",
        "category": "Student Services",
        "building": "Hostel Quadrangle",
        "floor": "Ground Floor",
        "description": "Residential halls warden office, student recreation lounge, TV room, study hall, and guest visitor lobby.",
        "operating_hours": "24 Hours",
        "x": 230, "y": 140,
        "contact": "+91 20 6793 5098 / warden@sspu.ac.in",
        "node_id": "N_HOSTEL_ENTRANCE"
    },
    {
        "id": 31,
        "name": "Innovation & Incubation Hub",
        "category": "Academic",
        "building": "Innovation & Incubation Hub",
        "floor": "1st Floor",
        "description": "Student venture incubator, intellectual property / patent guidance cell, co-working space, and seed fund office.",
        "operating_hours": "Mon-Sat 09:00-19:00",
        "x": 450, "y": 90,
        "contact": "+91 20 6793 5085 / startup@sspu.ac.in",
        "node_id": "N_INCUBATION_ENTRANCE"
    },
    {
        "id": 32,
        "name": "North Visitor & Staff Parking",
        "category": "Student Services",
        "building": "Main Entrance & Plaza",
        "floor": "Ground Floor",
        "description": "Designated multi-bay covered parking area with EV charging stations for faculty, students, and visitors.",
        "operating_hours": "Mon-Sun 06:00-23:00",
        "x": 850, "y": 100,
        "contact": "Security Booth #2",
        "node_id": "N_NORTH_PARKING"
    }
]

# Graph Nodes
NODES = [
    {"id": "N_GATE", "name": "Main Campus Gate", "x": 120, "y": 640, "building": "Main Entrance & Plaza", "floor": "Ground Floor"},
    {"id": "N_ENTRANCE_PLAZA", "name": "Entrance Plaza & ATM", "x": 180, "y": 620, "building": "Main Entrance & Plaza", "floor": "Ground Floor"},
    {"id": "N_ADMIN_JUNCTION", "name": "Admin South Walkway", "x": 230, "y": 560, "building": "Administrative Block", "floor": "Ground Floor"},
    {"id": "N_ADMIN_ENTRANCE", "name": "Administrative Block Foyer", "x": 230, "y": 480, "building": "Administrative Block", "floor": "Ground Floor"},
    {"id": "N_MEDICAL_JUNCTION", "name": "Health Center Path", "x": 150, "y": 430, "building": "Health & Medical Center", "floor": "Ground Floor"},
    {"id": "N_MEDICAL_ENTRANCE", "name": "Medical Center Entrance", "x": 120, "y": 400, "building": "Health & Medical Center", "floor": "Ground Floor"},
    {"id": "N_SOUTH_PROMENADE", "name": "South Central Promenade", "x": 380, "y": 560, "building": "Main Entrance & Plaza", "floor": "Ground Floor"},
    {"id": "N_SPORTS_JUNCTION", "name": "Sports Arena Plaza", "x": 580, "y": 540, "building": "Sports Complex & Stadium", "floor": "Ground Floor"},
    {"id": "N_TRACK_ENTRANCE", "name": "Athletics Track Gate", "x": 600, "y": 560, "building": "Sports Complex & Stadium", "floor": "Ground Floor"},
    {"id": "N_INDOOR_SPORTS_ENTRANCE", "name": "Indoor Sports Complex Foyer", "x": 820, "y": 530, "building": "Sports Complex & Stadium", "floor": "Ground Floor"},
    {"id": "N_AUDITORIUM_JUNCTION", "name": "Auditorium Walkway", "x": 380, "y": 420, "building": "Auditorium & Convention Hall", "floor": "Ground Floor"},
    {"id": "N_AUDITORIUM_ENTRANCE", "name": "Grand Auditorium Main Portico", "x": 440, "y": 400, "building": "Auditorium & Convention Hall", "floor": "Ground Floor"},
    {"id": "N_CAFETERIA_JUNCTION", "name": "Cafeteria Crossroads", "x": 580, "y": 420, "building": "Student Amenities & Cafeteria", "floor": "Ground Floor"},
    {"id": "N_CAFETERIA_ENTRANCE", "name": "Food Court Main Entrance", "x": 640, "y": 400, "building": "Student Amenities & Cafeteria", "floor": "Ground Floor"},
    {"id": "N_LIBRARY_JUNCTION", "name": "Knowledge Garden Path", "x": 290, "y": 330, "building": "Central Library & Knowledge Center", "floor": "Ground Floor"},
    {"id": "N_LIBRARY_ENTRANCE", "name": "Central Library Entrance", "x": 250, "y": 310, "building": "Central Library & Knowledge Center", "floor": "Ground Floor"},
    {"id": "N_CENTER_CROSS", "name": "Central Boulevard Crossroads", "x": 380, "y": 280, "building": "Main Entrance & Plaza", "floor": "Ground Floor"},
    {"id": "N_ENGINEERING_JUNCTION", "name": "Engineering Promenade", "x": 440, "y": 260, "building": "Engineering & Tech Block (A)", "floor": "Ground Floor"},
    {"id": "N_ENGINEERING_ENTRANCE", "name": "Engineering Block A Portico", "x": 470, "y": 220, "building": "Engineering & Tech Block (A)", "floor": "Ground Floor"},
    {"id": "N_COMPUTING_JUNCTION", "name": "Computing Hub Plaza", "x": 660, "y": 260, "building": "Science & Computing Hub (B)", "floor": "Ground Floor"},
    {"id": "N_COMPUTING_ENTRANCE", "name": "Computing Hub Block B Foyer", "x": 690, "y": 220, "building": "Science & Computing Hub (B)", "floor": "Ground Floor"},
    {"id": "N_WORKSHOP_JUNCTION", "name": "Technology Lane", "x": 820, "y": 260, "building": "Mechanical & Workshops Block (C)", "floor": "Ground Floor"},
    {"id": "N_WORKSHOP_ENTRANCE", "name": "Workshops Block C Gate", "x": 860, "y": 220, "building": "Mechanical & Workshops Block (C)", "floor": "Ground Floor"},
    {"id": "N_NORTH_PROMENADE", "name": "North Campus Promenade", "x": 380, "y": 140, "building": "Main Entrance & Plaza", "floor": "Ground Floor"},
    {"id": "N_HOSTEL_JUNCTION", "name": "Hostel Walkway", "x": 270, "y": 140, "building": "Hostel Quadrangle", "floor": "Ground Floor"},
    {"id": "N_HOSTEL_ENTRANCE", "name": "Hostel Quad Entrance", "x": 230, "y": 140, "building": "Hostel Quadrangle", "floor": "Ground Floor"},
    {"id": "N_INCUBATION_ENTRANCE", "name": "Incubation Hub Entrance", "x": 450, "y": 90, "building": "Innovation & Incubation Hub", "floor": "Ground Floor"},
    {"id": "N_NORTH_PARKING", "name": "North Parking Bay", "x": 850, "y": 100, "building": "Main Entrance & Plaza", "floor": "Ground Floor"}
]

# Raw Edge Pairs: will compute euclidean distance scaled to realistic campus metres
RAW_EDGES = [
    # Main Gate to Plaza & Admin
    ("N_GATE", "N_ENTRANCE_PLAZA", "Paved Walkway", "Walk along the tree-lined campus entry walkway"),
    ("N_ENTRANCE_PLAZA", "N_ADMIN_JUNCTION", "Paved Walkway", "Walk north towards the Administrative Block courtyard"),
    ("N_ADMIN_JUNCTION", "N_ADMIN_ENTRANCE", "Corridor Path", "Enter through the Administrative Block main entrance foyer"),
    ("N_ADMIN_JUNCTION", "N_MEDICAL_JUNCTION", "Paved Walkway", "Follow the west path towards the Health & Medical Center"),
    ("N_MEDICAL_JUNCTION", "N_MEDICAL_ENTRANCE", "Entrance Walkway", "Proceed to the 24/7 Medical Center entrance"),
    ("N_ADMIN_JUNCTION", "N_SOUTH_PROMENADE", "Central Promenade", "Walk east onto the wide South Central Promenade"),
    
    # South Promenade connections
    ("N_ENTRANCE_PLAZA", "N_SOUTH_PROMENADE", "Main Boulevard", "Walk along the south boulevard towards central campus"),
    ("N_SOUTH_PROMENADE", "N_SPORTS_JUNCTION", "Sports Avenue", "Head east along the sports avenue towards the athletics complex"),
    ("N_SPORTS_JUNCTION", "N_TRACK_ENTRANCE", "Track Gate", "Turn right towards the Athletics Track and football arena"),
    ("N_SPORTS_JUNCTION", "N_INDOOR_SPORTS_ENTRANCE", "Sports Promenade", "Follow the lighted walkway to the Indoor Sports Complex"),
    ("N_SPORTS_JUNCTION", "N_CAFETERIA_JUNCTION", "Garden Path", "Walk north along the landscaped student green towards Cafeteria"),
    
    # Central spine
    ("N_SOUTH_PROMENADE", "N_AUDITORIUM_JUNCTION", "Central Promenade", "Walk north along the central avenue past the flower gardens"),
    ("N_AUDITORIUM_JUNCTION", "N_AUDITORIUM_ENTRANCE", "Grand Portico", "Walk up the steps to the University Grand Auditorium portico"),
    ("N_AUDITORIUM_JUNCTION", "N_CAFETERIA_JUNCTION", "Plaza Walkway", "Walk east across the central plaza towards the Cafeteria"),
    ("N_CAFETERIA_JUNCTION", "N_CAFETERIA_ENTRANCE", "Cafeteria Portico", "Enter the Central Cafeteria & Food Court dining pavilion"),
    
    # Middle crossroad
    ("N_AUDITORIUM_JUNCTION", "N_CENTER_CROSS", "Central Boulevard", "Walk north towards the central crossroads and coffee kiosk"),
    ("N_CENTER_CROSS", "N_LIBRARY_JUNCTION", "Library Garden Path", "Turn west along the shaded knowledge pathway towards the Library"),
    ("N_LIBRARY_JUNCTION", "N_LIBRARY_ENTRANCE", "Library Steps", "Proceed to the Central Library and Knowledge Center glass entrance"),
    ("N_MEDICAL_JUNCTION", "N_LIBRARY_JUNCTION", "West Walkway", "Walk north along the west gardens towards the Library"),
    
    # Engineering & Science connections
    ("N_CENTER_CROSS", "N_ENGINEERING_JUNCTION", "Tech Promenade", "Walk northeast towards Engineering & Tech Block A"),
    ("N_ENGINEERING_JUNCTION", "N_ENGINEERING_ENTRANCE", "Block A Portico", "Enter Engineering Block A through the main glass portico"),
    ("N_ENGINEERING_JUNCTION", "N_COMPUTING_JUNCTION", "Academic Bridge", "Walk east along the covered academic concourse to Computing Hub"),
    ("N_CAFETERIA_JUNCTION", "N_COMPUTING_JUNCTION", "Hub Pathway", "Walk north along the plaza towards the Science & Computing Hub"),
    ("N_COMPUTING_JUNCTION", "N_COMPUTING_ENTRANCE", "Block B Foyer", "Enter Science & Computing Hub Block B through the main entrance"),
    
    # Workshops & East
    ("N_COMPUTING_JUNCTION", "N_WORKSHOP_JUNCTION", "Technology Lane", "Follow Technology Lane east towards the Mechanical Workshops"),
    ("N_WORKSHOP_JUNCTION", "N_WORKSHOP_ENTRANCE", "Workshop Bay", "Enter Mechanical & Automobile Workshops Block C"),
    ("N_INDOOR_SPORTS_ENTRANCE", "N_WORKSHOP_JUNCTION", "Perimeter Road", "Walk north along the east perimeter walkway"),
    
    # North Promenade & Hostels
    ("N_CENTER_CROSS", "N_NORTH_PROMENADE", "North Promenade", "Walk north along the main promenade towards the residential area"),
    ("N_ENGINEERING_JUNCTION", "N_NORTH_PROMENADE", "Promenade Path", "Follow the northwest path to the North Promenade"),
    ("N_NORTH_PROMENADE", "N_HOSTEL_JUNCTION", "Hostel Avenue", "Turn west along the quiet hostel garden walkway"),
    ("N_HOSTEL_JUNCTION", "N_HOSTEL_ENTRANCE", "Hostel Gate", "Enter the Hostel Quadrangle main gate"),
    ("N_LIBRARY_JUNCTION", "N_HOSTEL_JUNCTION", "West Campus Path", "Walk north past the library courtyard towards the hostels"),
    
    # North Incubation & Parking
    ("N_NORTH_PROMENADE", "N_INCUBATION_ENTRANCE", "Incubation Plaza", "Walk straight north to the Innovation & Incubation Hub"),
    ("N_NORTH_PROMENADE", "N_NORTH_PARKING", "North Perimeter Way", "Walk northeast along the ring road towards North Parking"),
    ("N_WORKSHOP_JUNCTION", "N_NORTH_PARKING", "Service Road", "Walk north towards the North Visitor & Staff Parking bay")
]

def build_edges_with_distance():
    node_map = {n["id"]: n for n in NODES}
    edges = []
    edge_id = 1
    for u, v, p_type, desc in RAW_EDGES:
        n1 = node_map[u]
        n2 = node_map[v]
        dx = n1["x"] - n2["x"]
        dy = n1["y"] - n2["y"]
        # Scale: ~1 svg pixel = 0.85 metres
        dist = round(math.hypot(dx, dy) * 0.85, 1)
        if dist < 15:
            dist = 15.0  # minimum realistic segment
        edges.append({
            "id": edge_id,
            "from_node": u,
            "to_node": v,
            "distance": dist,
            "path_type": p_type,
            "description": desc
        })
        edge_id += 1
    return edges

EDGES = build_edges_with_distance()
