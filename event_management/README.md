# 🎯 EventOS — Event Management System

> A full-featured DBMS project built with **Python (Flask)** + **SQLite** demonstrating database relationships, CRUD operations, and a real-world event workflow.

---

## 📸 Features at a Glance

| Feature | Description |
|---------|-------------|
| 🎉 **Event Management** | Add and browse events with date, time, location, description |
| 👥 **Participant Management** | Register participants with name, email, phone |
| 📝 **Event Registration** | Link participants to events; duplicate prevention built-in |
| 📅 **Schedule Management** | Add sessions/timings per event; timeline view |
| ✅ **Attendance Tracking** | Mark Present/Absent per participant per event |
| 💬 **Feedback System** | 1–5 star ratings with comments; average rating display |
| 📊 **Reports** | Attendance % report + feedback summary per event |
| 🏆 **Dashboard** | Live stats: total events, participants, registrations, avg rating |

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+ / Flask |
| Database | SQLite (via `sqlite3` stdlib) |
| Frontend | HTML5, CSS3 (custom dark theme) |
| Fonts | Syne + DM Sans (Google Fonts) |

---

## 🗄️ Database Schema

```
Events          Participants
  id PK           id PK
  name             name
  date             email (UNIQUE)
  time             phone
  location
  description

Registrations   Schedule        Attendance      Feedback
  id PK           id PK           id PK           id PK
  participant_id  event_id FK     participant_id  participant_id
  event_id        session_name    event_id        event_id
  UNIQUE(p,e)     session_time    status          rating (1-5)
                                  UNIQUE(p,e)     comments
                                                  UNIQUE(p,e)
```

### Relationships
- **One Event → Many Participants** (via Registrations)
- **One Participant → Many Events** (via Registrations)
- **One Event → Many Schedule entries**
- **One Event → Many Feedback entries**
- **One Event → Many Attendance records**

---

## ⚙️ Setup

See **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)** for full instructions.

```bash
cd event_management
python -m venv venv && source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install flask
python app.py
# → open http://127.0.0.1:5000
```

---

## 🗂️ Project Structure

```
event_management/
├── app.py                  ← Flask app + all routes + DB functions
├── database.db             ← Auto-created SQLite database
├── SETUP_AND_RUN.md        ← Setup instructions
├── README.md               ← This file
├── templates/
│   ├── base.html           ← Sidebar layout
│   ├── index.html          ← Dashboard
│   ├── events.html         ← Events list (with date filter)
│   ├── add_event.html      ← Add event form
│   ├── event_detail.html   ← Event detail + participants + schedule + feedback
│   ├── participants.html   ← Participants list
│   ├── add_participant.html← Register participant form
│   ├── registration.html   ← Register participant for event
│   ├── schedule.html       ← Schedule management + timeline
│   ├── attendance.html     ← Mark attendance
│   ├── feedback.html       ← Submit & view feedback
│   └── reports.html        ← Attendance + feedback reports
└── static/
    └── style.css           ← Dark theme CSS
```

---

## 🔗 Routes Reference

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Dashboard with stats |
| GET | `/events` | List all events (filter by date) |
| GET/POST | `/events/add` | Add new event |
| GET | `/events/<id>` | Event detail page |
| GET | `/participants` | List all participants |
| GET/POST | `/participants/add` | Add new participant |
| GET/POST | `/registration` | Register participant for event |
| GET | `/schedule` | View event schedule |
| POST | `/schedule/add` | Add session to schedule |
| GET/POST | `/attendance` | Mark attendance |
| GET/POST | `/feedback` | Submit / view feedback |
| GET | `/reports` | Attendance + feedback reports |

---

## ✅ DBMS Concepts Demonstrated

- **Primary & Foreign Keys** with `ON DELETE CASCADE`
- **UNIQUE constraints** (prevent duplicate registration/feedback)
- **CHECK constraints** (attendance status, rating range)
- **JOIN queries** across 3+ tables
- **Aggregate functions**: `COUNT`, `AVG`, `ROUND`
- **GROUP BY** for per-event statistics
- **Parameterized queries** (SQL injection prevention)
- **Transaction management** via SQLite context managers

---

## 📝 Sample Data

The app auto-inserts sample data on first run:
- **3 Events**: Tech Summit 2024, AI & ML Workshop, Startup Networking Night
- **4 Participants**: Aditya, Priya, Rahul, Sneha
- **8 Registrations**, **11 Schedule sessions**, **6 Attendance records**, **5 Feedback entries**

---

## 👨‍💻 Author : Vipul Ahire

Built as a DBMS Project demonstrating real-world database design with Flask.
