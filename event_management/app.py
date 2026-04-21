from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'event_mgmt_secret_2024'

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS Events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                time        TEXT    NOT NULL,
                location    TEXT    NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS Participants (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT    NOT NULL,
                email TEXT    NOT NULL UNIQUE,
                phone TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Registrations (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL REFERENCES Participants(id) ON DELETE CASCADE,
                event_id       INTEGER NOT NULL REFERENCES Events(id)       ON DELETE CASCADE,
                UNIQUE(participant_id, event_id)
            );

            CREATE TABLE IF NOT EXISTS Schedule (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id     INTEGER NOT NULL REFERENCES Events(id) ON DELETE CASCADE,
                session_name TEXT    NOT NULL,
                session_time TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Attendance (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL REFERENCES Participants(id) ON DELETE CASCADE,
                event_id       INTEGER NOT NULL REFERENCES Events(id)       ON DELETE CASCADE,
                status         TEXT    NOT NULL CHECK(status IN ('Present','Absent')),
                UNIQUE(participant_id, event_id)
            );

            CREATE TABLE IF NOT EXISTS Feedback (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL REFERENCES Participants(id) ON DELETE CASCADE,
                event_id       INTEGER NOT NULL REFERENCES Events(id)       ON DELETE CASCADE,
                rating         INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comments       TEXT,
                UNIQUE(participant_id, event_id)
            );
        ''')
        _insert_sample_data(conn)

def _insert_sample_data(conn):
    # Only insert if empty
    if conn.execute("SELECT COUNT(*) FROM Events").fetchone()[0] > 0:
        return

    conn.executescript('''
        INSERT INTO Events (name, date, time, location, description) VALUES
            ('Tech Summit 2024',       '2024-12-15', '09:00', 'Nashik Convention Hall',   'Annual technology summit featuring keynotes and workshops.'),
            ('AI & ML Workshop',       '2024-12-20', '10:00', 'Innovation Hub, Pune',     'Hands-on workshop covering machine learning fundamentals.'),
            ('Startup Networking Night','2024-12-28', '18:00', 'CoWork Space, Mumbai',     'Evening event for startup founders and investors to connect.');

        INSERT INTO Participants (name, email, phone) VALUES
            ('Aditya Sharma',   'aditya@example.com',  '9876543210'),
            ('Priya Mehta',     'priya@example.com',   '9876543211'),
            ('Rahul Verma',     'rahul@example.com',   '9876543212'),
            ('Sneha Patil',     'sneha@example.com',   '9876543213');

        INSERT INTO Registrations (participant_id, event_id) VALUES
            (1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(3,3),(4,3);

        INSERT INTO Schedule (event_id, session_name, session_time) VALUES
            (1,'Opening Keynote','09:00 AM'),
            (1,'Cloud Computing Talk','10:30 AM'),
            (1,'Networking Lunch','01:00 PM'),
            (1,'Panel Discussion','02:30 PM'),
            (1,'Closing Ceremony','05:00 PM'),
            (2,'Intro to ML','10:00 AM'),
            (2,'Python for Data Science','11:30 AM'),
            (2,'Hands-on Lab','02:00 PM'),
            (3,'Welcome & Drinks','06:00 PM'),
            (3,'Pitch Sessions','07:00 PM'),
            (3,'Open Networking','08:30 PM');

        INSERT INTO Attendance (participant_id, event_id, status) VALUES
            (1,1,'Present'),(2,1,'Present'),(3,1,'Absent'),(4,1,'Present'),
            (1,2,'Present'),(2,2,'Absent');

        INSERT INTO Feedback (participant_id, event_id, rating, comments) VALUES
            (1,1,5,'Excellent event! Loved the keynote.'),
            (2,1,4,'Great sessions, venue was nice.'),
            (4,1,5,'One of the best tech events I attended.'),
            (1,2,4,'Very informative workshop.'),
            (3,3,3,'Good networking opportunity, could be better organised.');
    ''')

# ─────────────────────────────────────────────
# DB OPERATION FUNCTIONS
# ─────────────────────────────────────────────

def db_get_all_events():
    with get_db() as conn:
        return conn.execute('''
            SELECT e.*,
                   COUNT(DISTINCT r.participant_id) AS participant_count,
                   ROUND(AVG(f.rating), 1)          AS avg_rating
            FROM Events e
            LEFT JOIN Registrations r ON r.event_id = e.id
            LEFT JOIN Feedback f      ON f.event_id = e.id
            GROUP BY e.id
            ORDER BY e.date DESC
        ''').fetchall()

def db_get_event(event_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM Events WHERE id=?", (event_id,)).fetchone()

def db_add_event(name, date, time, location, description):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO Events (name,date,time,location,description) VALUES (?,?,?,?,?)",
            (name, date, time, location, description)
        )

def db_get_all_participants():
    with get_db() as conn:
        return conn.execute('''
            SELECT p.*, COUNT(DISTINCT r.event_id) AS event_count
            FROM Participants p
            LEFT JOIN Registrations r ON r.participant_id = p.id
            GROUP BY p.id ORDER BY p.name
        ''').fetchall()

def db_get_participant(pid):
    with get_db() as conn:
        return conn.execute("SELECT * FROM Participants WHERE id=?", (pid,)).fetchone()

def db_add_participant(name, email, phone):
    with get_db() as conn:
        conn.execute("INSERT INTO Participants (name,email,phone) VALUES (?,?,?)", (name, email, phone))

def db_get_participants_for_event(event_id):
    with get_db() as conn:
        return conn.execute('''
            SELECT p.*, a.status
            FROM Participants p
            JOIN Registrations r ON r.participant_id = p.id
            LEFT JOIN Attendance a ON a.participant_id = p.id AND a.event_id = ?
            WHERE r.event_id = ?
        ''', (event_id, event_id)).fetchall()

def db_register_participant(participant_id, event_id):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM Registrations WHERE participant_id=? AND event_id=?",
            (participant_id, event_id)
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT INTO Registrations (participant_id,event_id) VALUES (?,?)",
            (participant_id, event_id)
        )
        return True

def db_get_schedule(event_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM Schedule WHERE event_id=? ORDER BY session_time",
            (event_id,)
        ).fetchall()

def db_add_schedule(event_id, session_name, session_time):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO Schedule (event_id,session_name,session_time) VALUES (?,?,?)",
            (event_id, session_name, session_time)
        )

def db_mark_attendance(participant_id, event_id, status):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM Attendance WHERE participant_id=? AND event_id=?",
            (participant_id, event_id)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE Attendance SET status=? WHERE participant_id=? AND event_id=?",
                (status, participant_id, event_id)
            )
        else:
            conn.execute(
                "INSERT INTO Attendance (participant_id,event_id,status) VALUES (?,?,?)",
                (participant_id, event_id, status)
            )

def db_submit_feedback(participant_id, event_id, rating, comments):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM Feedback WHERE participant_id=? AND event_id=?",
            (participant_id, event_id)
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT INTO Feedback (participant_id,event_id,rating,comments) VALUES (?,?,?,?)",
            (participant_id, event_id, rating, comments)
        )
        return True

def db_get_feedback(event_id):
    with get_db() as conn:
        return conn.execute('''
            SELECT f.*, p.name AS participant_name
            FROM Feedback f
            JOIN Participants p ON p.id = f.participant_id
            WHERE f.event_id = ?
            ORDER BY f.id DESC
        ''', (event_id,)).fetchall()

def db_get_dashboard_stats():
    with get_db() as conn:
        stats = {}
        stats['total_events']       = conn.execute("SELECT COUNT(*) FROM Events").fetchone()[0]
        stats['total_participants']  = conn.execute("SELECT COUNT(*) FROM Participants").fetchone()[0]
        stats['total_registrations'] = conn.execute("SELECT COUNT(*) FROM Registrations").fetchone()[0]
        stats['total_feedback']      = conn.execute("SELECT COUNT(*) FROM Feedback").fetchone()[0]
        stats['avg_rating']          = conn.execute("SELECT ROUND(AVG(rating),1) FROM Feedback").fetchone()[0] or 0
        stats['present_count']       = conn.execute("SELECT COUNT(*) FROM Attendance WHERE status='Present'").fetchone()[0]
        stats['top_events']          = conn.execute('''
            SELECT e.name, ROUND(AVG(f.rating),1) AS avg_r, COUNT(f.id) AS cnt
            FROM Events e JOIN Feedback f ON f.event_id=e.id
            GROUP BY e.id ORDER BY avg_r DESC LIMIT 3
        ''').fetchall()
        stats['recent_events']       = conn.execute(
            "SELECT * FROM Events ORDER BY date DESC LIMIT 5"
        ).fetchall()
        return stats

def db_attendance_report(event_id):
    with get_db() as conn:
        rows = conn.execute('''
            SELECT p.name, p.email,
                   COALESCE(a.status,'Not Marked') AS status
            FROM Participants p
            JOIN Registrations r ON r.participant_id = p.id
            LEFT JOIN Attendance a ON a.participant_id = p.id AND a.event_id = ?
            WHERE r.event_id = ?
        ''', (event_id, event_id)).fetchall()
        total   = len(rows)
        present = sum(1 for r in rows if r['status'] == 'Present')
        absent  = sum(1 for r in rows if r['status'] == 'Absent')
        return rows, total, present, absent

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    stats = db_get_dashboard_stats()
    events = db_get_all_events()
    return render_template('index.html', stats=stats, events=events)

# ── Events ──────────────────────────────────

@app.route('/events')
def events():
    date_filter = request.args.get('date', '')
    with get_db() as conn:
        if date_filter:
            rows = conn.execute('''
                SELECT e.*, COUNT(DISTINCT r.participant_id) AS participant_count,
                       ROUND(AVG(f.rating),1) AS avg_rating
                FROM Events e
                LEFT JOIN Registrations r ON r.event_id=e.id
                LEFT JOIN Feedback f ON f.event_id=e.id
                WHERE e.date=? GROUP BY e.id ORDER BY e.date DESC
            ''', (date_filter,)).fetchall()
        else:
            rows = db_get_all_events()
    return render_template('events.html', events=rows, date_filter=date_filter)

@app.route('/events/add', methods=['GET','POST'])
def add_event():
    if request.method == 'POST':
        name        = request.form.get('name','').strip()
        date        = request.form.get('date','').strip()
        time        = request.form.get('time','').strip()
        location    = request.form.get('location','').strip()
        description = request.form.get('description','').strip()
        if not all([name, date, time, location]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('add_event'))
        db_add_event(name, date, time, location, description)
        flash(f'Event "{name}" added successfully!', 'success')
        return redirect(url_for('events'))
    return render_template('add_event.html')

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db_get_event(event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('events'))
    participants = db_get_participants_for_event(event_id)
    schedule     = db_get_schedule(event_id)
    feedback     = db_get_feedback(event_id)
    with get_db() as conn:
        avg_rating = conn.execute(
            "SELECT ROUND(AVG(rating),1) FROM Feedback WHERE event_id=?", (event_id,)
        ).fetchone()[0]
    return render_template('event_detail.html',
        event=event, participants=participants,
        schedule=schedule, feedback=feedback, avg_rating=avg_rating)

# ── Participants ─────────────────────────────

@app.route('/participants')
def participants():
    rows = db_get_all_participants()
    return render_template('participants.html', participants=rows)

@app.route('/participants/add', methods=['GET','POST'])
def add_participant():
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        phone = request.form.get('phone','').strip()
        if not all([name, email, phone]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('add_participant'))
        try:
            db_add_participant(name, email, phone)
            flash(f'Participant "{name}" registered!', 'success')
            return redirect(url_for('participants'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'error')
            return redirect(url_for('add_participant'))
    return render_template('add_participant.html')

# ── Registration ─────────────────────────────

@app.route('/registration', methods=['GET','POST'])
def registration():
    events       = db_get_all_events()
    participants = db_get_all_participants()
    if request.method == 'POST':
        pid = request.form.get('participant_id')
        eid = request.form.get('event_id')
        if not pid or not eid:
            flash('Please select both a participant and an event.', 'error')
            return redirect(url_for('registration'))
        success = db_register_participant(int(pid), int(eid))
        if success:
            flash('Registration successful!', 'success')
        else:
            flash('Participant is already registered for this event.', 'error')
        return redirect(url_for('registration'))
    with get_db() as conn:
        recent_regs = conn.execute('''
            SELECT p.name AS pname, e.name AS ename, r.id
            FROM Registrations r
            JOIN Participants p ON p.id=r.participant_id
            JOIN Events e ON e.id=r.event_id
            ORDER BY r.id DESC LIMIT 10
        ''').fetchall()
    return render_template('registration.html',
        events=events, participants=participants, recent_regs=recent_regs)

# ── Schedule ─────────────────────────────────

@app.route('/schedule')
def schedule():
    events = db_get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    sessions = []
    selected_event = None
    if selected_event_id:
        sessions = db_get_schedule(selected_event_id)
        selected_event = db_get_event(selected_event_id)
    return render_template('schedule.html',
        events=events, sessions=sessions,
        selected_event=selected_event, selected_event_id=selected_event_id)

@app.route('/schedule/add', methods=['POST'])
def add_schedule():
    event_id     = request.form.get('event_id', '').strip()
    session_name = request.form.get('session_name', '').strip()
    session_time = request.form.get('session_time', '').strip()
    if not all([event_id, session_name, session_time]):
        flash('All fields required.', 'error')
        return redirect(url_for('schedule'))
    try:
        db_add_schedule(int(event_id), session_name, session_time)
        flash('Session added!', 'success')
    except Exception:
        flash('Could not add session. Please try again.', 'error')
    return redirect(url_for('schedule', event_id=event_id))

# ── Attendance ────────────────────────────────

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    events = db_get_all_events()
    if request.method == 'POST':
        # Handle attendance form submission
        eid = request.form.get('event_id', type=int)
        if eid:
            for key, val in request.form.items():
                if key.startswith('status_') and val in ('Present', 'Absent'):
                    try:
                        pid = int(key.split('_')[1])
                        db_mark_attendance(pid, eid, val)
                    except (ValueError, IndexError):
                        continue  # skip malformed keys safely
            flash('Attendance saved!', 'success')
        else:
            flash('Invalid event. Please try again.', 'error')
        return redirect(url_for('attendance', event_id=eid))
    # GET: load data for the selected event
    selected_event_id = request.args.get('event_id', type=int)
    participants  = []
    selected_event = None
    if selected_event_id:
        selected_event = db_get_event(selected_event_id)
        if selected_event:
            participants = db_get_participants_for_event(selected_event_id)
        else:
            flash('Event not found.', 'error')
            return redirect(url_for('attendance'))
    return render_template('attendance.html',
        events=events, participants=participants,
        selected_event=selected_event, selected_event_id=selected_event_id)

# ── Feedback ──────────────────────────────────

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    events       = db_get_all_events()
    participants = db_get_all_participants()
    selected_event_id = request.args.get('event_id', type=int)
    all_feedback = []
    selected_event = None
    if selected_event_id:
        all_feedback   = db_get_feedback(selected_event_id)
        selected_event = db_get_event(selected_event_id)
    if request.method == 'POST':
        pid      = request.form.get('participant_id', type=int)
        eid      = request.form.get('event_id', type=int)
        rating   = request.form.get('rating', type=int)
        comments = request.form.get('comments', '').strip()
        if not all([pid, eid, rating]):
            flash('Please select a participant, event, and rating.', 'error')
            return redirect(url_for('feedback', event_id=eid or ''))
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5.', 'error')
            return redirect(url_for('feedback', event_id=eid))
        ok = db_submit_feedback(pid, eid, rating, comments)
        if ok:
            flash('Feedback submitted! Thank you.', 'success')
        else:
            flash('You have already submitted feedback for this event.', 'error')
        return redirect(url_for('feedback', event_id=eid))
    return render_template('feedback.html',
        events=events, participants=participants,
        all_feedback=all_feedback,
        selected_event=selected_event, selected_event_id=selected_event_id)

# ── Reports ───────────────────────────────────

@app.route('/reports')
def reports():
    selected_event_id = request.args.get('event_id', type=int)
    events = db_get_all_events()
    report_data    = None
    selected_event = None
    if selected_event_id:
        selected_event = db_get_event(selected_event_id)
        if not selected_event:
            flash('Event not found.', 'error')
            return redirect(url_for('reports'))
        att_rows, total, present, absent = db_attendance_report(selected_event_id)
        feedback_rows = db_get_feedback(selected_event_id)
        with get_db() as conn:
            avg_r = conn.execute(
                "SELECT ROUND(AVG(rating),1) FROM Feedback WHERE event_id=?",
                (selected_event_id,)
            ).fetchone()[0]
        report_data = dict(
            att_rows=att_rows, total=total,
            present=present, absent=absent,
            feedback_rows=feedback_rows, avg_rating=avg_r
        )
    return render_template('reports.html',
        events=events, report_data=report_data,
        selected_event=selected_event, selected_event_id=selected_event_id)

# ─────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)