import flet as ft
import database as db  # Importiere unser Backend
from datetime import datetime

def main(page: ft.Page):
    page.title = "Meine ToDo App (SQLite)"
    page.window.width = 1000
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- Container für die Aufgabenliste ---
    # Wir nutzen eine Column (Spalte), um die Checkboxen untereinander zu stapeln
    tasks_view = ft.Column()

    # --- 1. Die Logik für den Detail-Dialog ---
    def open_edit_dialog(task):
        """Öffnet ein Modal-Fenster zum Bearbeiten der Task-Details."""
        
        # Helper: ID extrahieren (brauchen wir zum Speichern)
        task_id = task['id']

        # --- A. Die Eingabefelder definieren und mit DB-Werten füllen ---
        edit_title = ft.TextField(label="Titel", value=task['title'])
        edit_desc = ft.TextField(label="Beschreibung", value=task['description'], multiline=True, min_lines=3)
        
        # Dropdowns (Enums)
        # Wir definieren die Optionen direkt hier. Später könnten die auch aus der DB kommen.
        edit_status = ft.Dropdown(
            label="Status",
            value=task['status'],
            options=[
                ft.dropdown.Option("New"),
                ft.dropdown.Option("Work"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Final"),
                ft.dropdown.Option("Cancelled"),
            ]
        )

        edit_prio = ft.Dropdown(
            label="Prio",
            value=str(task['priority']), # Dropdown erwartet String, DB ist Integer
            options=[
                ft.dropdown.Option("1", "1 - Kritisch"),
                ft.dropdown.Option("2", "2 - Hoch"),
                ft.dropdown.Option("3", "3 - Normal"),
                ft.dropdown.Option("4", "4 - Niedrig"),
            ]
        )

        edit_category = ft.Dropdown(
            label="Kategorie",
            value=task['category'],
            options=[
                ft.dropdown.Option("Inbox"),
                ft.dropdown.Option("Projekt A"),
                ft.dropdown.Option("Tagesgeschäft"),
                ft.dropdown.Option("Privat"),
            ]
        )

        edit_effort = ft.TextField(label="Plan (h)", value=str(task['effort_planned']), width=100)
        edit_link = ft.TextField(label="Link", value=task['external_link'], expand=True)

        def open_link_clicked(e):
            if edit_link.value:
                # Das öffnet den Browser oder OneNote
                page.launch_url(edit_link.value)
        
        btn_open_link = ft.IconButton(icon=ft.icons.OPEN_IN_NEW, on_click=open_link_clicked, tooltip="Link öffnen")

        # --- NEU: Kommentar-Sektion ---
        
        # 1. Container für die Liste der Kommentare
        comments_column = ft.Column()
        
        # 2. Eingabefeld für neuen Kommentar
        new_comment_input = ft.TextField(hint_text="Neuer Statusbericht...", expand=True)

        def load_comments():
            """Lädt Kommentare aus der DB und baut die Liste neu."""
            comments_column.controls.clear()
            comments = db.get_comments_for_task(task_id)
            
            for c in comments:
                # c ist eine Row: [0]=id, [1]=task_id, [2]=text, [3]=created_at
                # Wir parsen das Datum schön
                raw_date = c['created_at']
                try:
                    dt = datetime.fromisoformat(raw_date)
                    pretty_date = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    pretty_date = raw_date

                # Optik: Ein kleiner grauer Kasten pro Kommentar
                c_item = ft.Container(
                    content=ft.Column([
                        ft.Text(pretty_date, size=10, color="grey"),
                        ft.Text(c['comment_text'], size=14)
                    ]),
                    padding=10,
                    bgcolor=ft.colors.BLUE_GREY_50, # Helles Grau
                    border_radius=5,
                    margin=ft.margin.only(bottom=5)
                )
                comments_column.controls.append(c_item)
            
            # Wichtig: Wir updaten nur den Dialog-Inhalt, nicht die ganze Seite
            page.update()

        def add_comment_clicked(e):
            if not new_comment_input.value:
                return
            
            # Ab in die DB
            db.add_comment(task_id, new_comment_input.value)
            
            # Input leeren und Liste neu laden
            new_comment_input.value = ""
            load_comments()

        # Initiales Laden der Kommentare
        load_comments()

        # --- B. Speicher-Logik ---
        def save_clicked(e):
            # Validierung: Aufwand muss eine Zahl sein
            try:
                plan_val = float(edit_effort.value)
            except ValueError:
                plan_val = 0.0

            # Update in DB aufrufen
            db.update_task_details(
                task_id=task_id,
                title=edit_title.value,
                description=edit_desc.value,
                category=edit_category.value,
                task_type="Task", # Lassen wir erstmal statisch
                priority=int(edit_prio.value),
                effort_planned=plan_val,
                external_link=edit_link.value,
                status=edit_status.value
            )
            
            # Dialog schließen und Liste aktualisieren
            dlg_modal.open = False
            page.update()
            render_tasks()
            page.open(ft.SnackBar(ft.Text("Gespeichert!")))

        def cancel_clicked(e):
            dlg_modal.open = False
            page.update()

        # --- C. Dialog zusammenbauen ---
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Aufgabe bearbeiten"),
            content=ft.Container(
                width=700, # Breiter für die Kommentare
                content=ft.Column([
                    edit_title,
                    ft.Row([edit_status, edit_prio, edit_category]),
                    ft.Row([edit_effort, edit_link, btn_open_link]),
                    edit_desc,
                    ft.Divider(),
                    ft.Text("Verlauf / Kommentare", weight="bold"),
                    # Kommentar-Liste (in einem scrollbaren Container mit fester Höhe)
                    ft.Container(content=comments_column, height=150, padding=5, border=ft.border.all(1, "grey"), border_radius=5),
                    # Eingabezeile für Kommentare
                    ft.Row([new_comment_input, ft.IconButton(ft.icons.SEND, on_click=add_comment_clicked)])
                ], scroll=ft.ScrollMode.AUTO)
            ),
            actions=[
                ft.TextButton("Abbrechen", on_click=cancel_clicked),
                ft.ElevatedButton("Speichern", on_click=save_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Dialog zur Seite hinzufügen und öffnen
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()


    # --- 2. Hauptansicht (Liste) ---
    def render_tasks():
        tasks_view.controls.clear()
        tasks = db.get_all_tasks()
        
        for task in tasks:
            # Wir holen uns die Werte für die Anzeige
            t_id = task['id']
            t_title = task['title']
            t_status = task['status']
            t_prio = task['priority']
            
            # Farb-Logik für Prio (Kleines UI Detail)
            prio_color = "red" if t_prio == 1 else "orange" if t_prio == 2 else "blue"
            
            # Ein "Container" der klickbar ist (InkWell oder GestureDetector)
            # Wir nutzen hier ListTile, das sieht professionell aus
            list_item = ft.ListTile(
                leading=ft.Icon(ft.Icons.CIRCLE, color=prio_color), # Punkt zeigt Prio
                title=ft.Text(t_title, weight="bold"),
                subtitle=ft.Text(f"{t_status} | {task['category']}"),
                trailing=ft.IconButton(ft.Icons.DELETE, icon_color="grey", on_click=lambda e, id=t_id: delete_clicked(id)),
                on_click=lambda e, t=task: open_edit_dialog(t) # WICHTIG: Hier übergeben wir den ganzen Task an den Dialog
            )
            
            # Card drumherum für schönen Schatten
            card = ft.Card(content=list_item)
            tasks_view.controls.append(card)
        
        page.update()

    def add_clicked(e):
        if not new_task_input.value:
            return
        
        # Standard-Werte beim Erstellen
        db.create_task(
            title=new_task_input.value,
            description="",
            category="Inbox",
            task_type="Task",
            priority=3,
            start_date=datetime.now().isoformat(),
            external_link=""
        )
        new_task_input.value = ""
        render_tasks()

    def delete_clicked(task_id):
        db.delete_task(task_id)
        render_tasks()

    # --- UI Layout ---
    new_task_input = ft.TextField(hint_text="Neue Aufgabe (Enter zum Erstellen)", expand=True, on_submit=add_clicked)
    
    page.add(
        ft.Row([ft.Text("Mein Cockpit", size=24, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=20), # Abstand
        ft.Row([new_task_input, ft.ElevatedButton("Quick Add", on_click=add_clicked)]),
        ft.Divider(),
        tasks_view
    )

    render_tasks()

if __name__ == "__main__":
    ft.app(target=main)