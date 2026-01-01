import sqlite3
from datetime import datetime

# Verbindung zur DB herstellen (erstellt die Datei automatisch, falls nicht vorhanden)
# check_same_thread=False ist wichtig bei GUIs wie Flet, da Events oft in Threads laufen
DB_NAME = "sqlite_todo.db"

def get_db_connection():
    """Erstellt eine Verbindung und nutzt den Row-Modus für Namens-Zugriff."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    # Das hier ist Gold wert: Erlaubt Zugriff via Spaltennamen statt nur Index
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Erstellt die Tabellen, falls sie noch nicht existieren."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabelle 1: Die Aufgaben
    # Wir speichern Datumsangaben als ISO-String (YYYY-MM-DD), da SQLite keinen DATE-Typ hat.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        task_type TEXT,
        status TEXT DEFAULT 'New',
        priority INTEGER DEFAULT 3,
        start_date TEXT,
        effort_planned REAL DEFAULT 0.0,
        effort_actual REAL DEFAULT 0.0,
        percent_done INTEGER DEFAULT 0,
        external_link TEXT,
        created_at TEXT
    )
    """)

    # Tabelle 2: Verlauf / Kommentare (1:n Beziehung)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        comment_text TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

######################################################################################################  
# --- CRUD Operationen ---

def create_task(title, description, category, task_type, priority, start_date, external_link):
    """Erstellt einen neuen Task."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().isoformat()
    
    # Status ist initial immer 'New', Fortschritt 0
    sql = """
    INSERT INTO tasks (title, description, category, task_type, priority, start_date, external_link, created_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'New')
    """
    cursor.execute(sql, (title, description, category, task_type, priority, start_date, external_link, created_at))
    conn.commit()
    conn.close()

def get_all_tasks():
    """Holt alle Tasks. Gibt sqlite3.Row Objekte zurück."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Wir sortieren standardmäßig nach ID absteigend (neueste oben)
    # Deine komplexe Rang-Logik machen wir später in Python (Frontend)
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status(task_id, new_status, percent_done):
    """Updated Status und Fortschritt."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ?, percent_done = ? WHERE id = ?", (new_status, percent_done, task_id))
    conn.commit()
    conn.close()

def update_task_efforts(task_id, planned, actual):
    """Updated die Aufwände."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET effort_planned = ?, effort_actual = ? WHERE id = ?", (planned, actual, task_id))
    conn.commit()
    conn.close()

def add_comment(task_id, text):
    """Fügt einen Verlaufseintrag hinzu."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("INSERT INTO comments (task_id, comment_text, created_at) VALUES (?, ?, ?)", (task_id, text, created_at))
    conn.commit()
    conn.close()

def get_comments_for_task(task_id):
    """Holt alle Kommentare zu einer Task ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE task_id = ? ORDER BY created_at DESC", (task_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def delete_task(task_id):
    """Löscht Task und (dank Cascade eigentlich auch) Kommentare."""
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

# Init ausführen
init_db()