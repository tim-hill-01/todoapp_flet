import flet as ft
import database as db  # Importiere unser Backend

def main(page: ft.Page):
    page.title = "Meine ToDo App (SQLite)"
    page.window_width = 450
    page.window_height = 600
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
            task_id = task[0]
            task_title = task[1]
            is_completed = bool(task[2])

            # Wir bauen eine Row (Zeile) für jeden Task: [Checkbox] [Lösch-Button]
            # WICHTIG: Wir nutzen Lambda-Funktionen, um die ID an den Event-Handler zu übergeben
            checkbox = ft.Checkbox(
                label=task_title, 
                value=is_completed,
                on_change=lambda e, id=task_id, status=is_completed: status_changed(id, status)
            )
            
            # Button (Jetzt funktioniert die Standard-Schreibweise wieder!)
            delete_btn = ft.IconButton(
                icon=ft.icons.DELETE,  # Das hier geht in v0.25.2 sicher
                icon_color="red",
                on_click=lambda e, id=task_id: delete_clicked(id)
            )

            row = ft.Row([checkbox, delete_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            tasks_view.controls.append(row)
        
        # 4. Seite aktualisieren
        page.update()

    # --- Event Handler ---
    def add_clicked(e):
        if not new_task_input.value:
            return
        # In DB speichern
        db.add_task(new_task_input.value)
        # UI resetten
        new_task_input.value = ""
        new_task_input.focus()
        render_tasks() # Liste neu laden

    def delete_clicked(task_id):
        db.delete_task(task_id)
        render_tasks()

    def status_changed(task_id, current_status):
        db.toggle_task(task_id, current_status)
        render_tasks()

    # --- UI Aufbau ---
    new_task_input = ft.TextField(hint_text="Neue Aufgabe...", expand=True, on_submit=add_clicked)
    add_button = ft.FilledButton("Add", on_click=add_clicked)
    
    input_row = ft.Row([new_task_input, add_button])

    # Alles auf die Seite packen
    page.add(input_row, ft.Divider(), tasks_view)

    # Initiale Ladung der Daten beim Start
    render_tasks()

if __name__ == "__main__":
    ft.app(target=main)