import flet as ft
import database as db  # Importiere unser Backend
from datetime import datetime

def main(page: ft.Page):
    page.title = "Meine ToDo App (SQLite)"
    page.window_width = 500
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- Container für die Aufgabenliste ---
    # Wir nutzen eine Column (Spalte), um die Checkboxen untereinander zu stapeln
    tasks_view = ft.Column()

    # --- Hilfsfunktion: Liste neu zeichnen ---
    def render_tasks():
        # 1. Alte Ansicht leeren
        tasks_view.controls.clear()
        
        # 2. Daten aus der DB holen (Select * ...)
        tasks = db.get_all_tasks()
        
        # 3. Für jeden Datensatz ein UI-Element bauen
        for task in tasks:
            # Zugriff jetzt über Spaltennamen möglich (dank row_factory in database.py)
            t_id = task['id']
            t_title = task['title']
            t_status = task['status']
            t_prio = task['priority']

            # Checkbox (dient aktuell nur der Optik, Status-Logik kommt später)
            # Wir prüfen: Ist Status 'Final' oder 'Cancelled'?
            is_done = t_status in ['Final', 'Cancelled']

            # WICHTIG: Wir nutzen Lambda-Funktionen, um die ID an den Event-Handler zu übergeben
            checkbox = ft.Checkbox(
                label=f"{t_title} (Prio: {t_prio})", 
                value=is_done,
                on_change=lambda e, id=t_id: print("Status ändern bauen wir noch!") 
            )
            
            # Löschen Button
            delete_btn = ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color="red",
                on_click=lambda e, id=t_id: delete_clicked(id)
            )

            row = ft.Row([checkbox, delete_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            tasks_view.controls.append(row)
        
        # 4. Seite aktualisieren
        page.update()

    # --- Event Handler ---
    def add_clicked(e):
        if not new_task_input.value:
            return
        
        # Hier nutzen wir jetzt die neue create_task Funktion mit vielen Parametern.
        # Da wir im Quick-Add nur den Titel haben, füllen wir den Rest mit "Dummy"-Werten oder None.
        db.create_task(
            title=new_task_input.value,
            description="",          # Leer
            category="Inbox",        # Standard-Kategorie
            task_type="Task",        # Standard-Typ
            priority=3,              # Standard-Prio (Mittel)
            start_date=datetime.now().isoformat(), # Heute
            external_link=""
        )
        
        new_task_input.value = ""
        new_task_input.focus()
        render_tasks()

    def delete_clicked(task_id):
        db.delete_task(task_id)
        render_tasks()

    # --- UI Aufbau ---
    new_task_input = ft.TextField(hint_text="Schnell-Erfassung (Nur Titel)", expand=True, on_submit=add_clicked)
    add_button = ft.ElevatedButton("Add", on_click=add_clicked)
    
    input_row = ft.Row([new_task_input, add_button])

    page.add(
        ft.Text("Projekt Cockpit", size=24, weight="bold"),
        input_row, 
        ft.Divider(), 
        tasks_view
    )

    render_tasks()

if __name__ == "__main__":
    ft.app(target=main)