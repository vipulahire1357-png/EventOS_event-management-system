# ⚙️ Setup & Run Guide — EventOS

## Prerequisites

Make sure you have **Python 3.8+** installed.

```bash
python --version
```

---

## 📁 Project Structure

```
event_management/
├── app.py
├── database.db          ← auto-created on first run
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── events.html
│   ├── add_event.html
│   ├── event_detail.html
│   ├── participants.html
│   ├── add_participant.html
│   ├── registration.html
│   ├── schedule.html
│   ├── attendance.html
│   ├── feedback.html
│   └── reports.html
└── static/
    └── style.css
```

---

## 🚀 Quick Start (3 Steps)

### Step 1 — Create a Virtual Environment

```bash
# Navigate to project folder
cd event_management

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2 — Install Flask

```bash
pip install flask
```

### Step 3 — Run the App

```bash
python app.py
```

The app will start at: **http://127.0.0.1:5000**

---

## 🗄️ Database

- SQLite database (`database.db`) is **auto-created** on first run.
- Sample data (3 events, 4 participants, registrations, schedules, attendance, feedback) is inserted automatically.
- To **reset** the database: delete `database.db` and restart the app.

---

## 🌐 Available Pages

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:5000/ |
| Events | http://127.0.0.1:5000/events |
| Add Event | http://127.0.0.1:5000/events/add |
| Participants | http://127.0.0.1:5000/participants |
| Registration | http://127.0.0.1:5000/registration |
| Schedule | http://127.0.0.1:5000/schedule |
| Attendance | http://127.0.0.1:5000/attendance |
| Feedback | http://127.0.0.1:5000/feedback |
| Reports | http://127.0.0.1:5000/reports |

---

## 🛑 Stopping the App

Press `Ctrl + C` in the terminal.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: flask` | Run `pip install flask` |
| Port 5000 already in use | Change port in `app.py`: `app.run(port=5001)` |
| Database errors | Delete `database.db` and restart |
| Templates not found | Make sure you're running from the `event_management/` directory |