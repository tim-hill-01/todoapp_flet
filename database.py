import sqlite3

# Verbindung zur DB herstellen (erstellt die Datei automatisch, falls nicht vorhanden)
# check_same_thread=False ist wichtig bei GUIs wie Flet, da Events oft in Threads laufen
conn = sqlite3.connect("sqlite_todo.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    """Erstellt die Tabelle, falls sie noch nicht existiert."""
    sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        is_completed BOOLEAN NOT NULL DEFAULT 0
    )
    """
    cursor.execute(sql)
    conn.commit()

def add_task(title):
    """Fügt einen neuen Task hinzu."""
    with conn:
        cursor.execute("INSERT INTO tasks (title, is_completed) VALUES (?, ?)", (title, False))

def get_all_tasks():
    """Holt alle Tasks."""
    cursor.execute("SELECT id, title, is_completed FROM tasks")
    return cursor.fetchall() # Gibt eine Liste von Tupeln zurück: [(1, 'Einkaufen', 0), ...]

def delete_task(task_id):
    """Löscht einen Task anhand der ID."""
    with conn:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def toggle_task(task_id, current_status):
    """Ändert den Status (Invertiert den aktuellen Status)."""
    new_status = not current_status
    with conn:
        cursor.execute("UPDATE tasks SET is_completed = ? WHERE id = ?", (new_status, task_id))

# Initialisierung direkt beim Import ausführen
init_db()