from dataclasses import dataclass

from fastapi import FastAPI
import sqlite3
import flet as ft
import requests

app = FastAPI() 

DB_NAME = "FLIGHTMS.db"
API_URL = "http://127.0.0.1:8000"

def get_connection(): 
    conn = sqlite3.connect(DB_NAME, check_same_thread=False) 
    conn.row_factory = sqlite3.Row  # allows accessing columns by name 
    return conn 

def init_db(): 
    conn = get_connection() 
    conn.execute(""" 
        CREATE TABLE IF NOT EXISTS flights ( 
            FLIGHT_ID int PRIMARY KEY, 
            FLIGHT_NUMBER varchar(10) NOT NULL, 
            DESTINATION varchar NOT NULL, 
            PRICE FLOAT NOT NULL 
        )
    """) 
    conn.commit() 
    conn.close() 
 
init_db()

# ── Form fields ──────────────────────────────────── 
flightId     = ft.TextField(label="FLIGHT+_ID",     width=320) 
flightNumber = ft.TextField(label="FLIGHT_NUMBER", width=320) 
destionation = ft.TextField(label="DESTIONATION", width=320) 
price = ft.TextField(label="PRICE", width=320) 


def show_snack(message, color=ft.Colors.GREEN): 
        page.snack_bar = ft.SnackBar( 
            content=ft.Text(message, color=ft.Colors.WHITE), 
            bgcolor=color, 
        ) 
        page.snack_bar.open = True 
        page.update()

def main(page: ft.Page):
    page.title = "SkyBook"
    page.window.width = 1920
    page.window.height = 1080

    title = ft.Text(
        "SkyBook",
        size=16,
        text_align=ft.TextAlign.LEFT,
        weight=ft.FontWeight.BOLD,
        color="#fff"
    )

    navbar = ft.Row([
        ft.Container(
            title,
            bgcolor="#0084ff", 
            width=1920, 
            height=40,
            padding=8
        )
    ])

    table = ft.DataTable( 
        columns=[ 
            ft.DataColumn(ft.Text("FLIGHT_ID")), 
            ft.DataColumn(ft.Text("FLIGHT_NUMBER")), 
            ft.DataColumn(ft.Text("DESTINATION")), 
            ft.DataColumn(ft.Text("PRICE")), 
        ], 
        rows=[], 
    )

    def load_table(): 
        try: 
            response = requests.get(f"{API_URL}/items") 
            table.rows.clear() 
            for item in response.json(): 
                table.rows.append( 
                    ft.DataRow(cells=[ 
                        ft.DataCell(ft.Text(item["id"])), 
                        ft.DataCell(ft.Text(item["field1"])), 
                        ft.DataCell(ft.Text(item["field2"])), 
                        ft.DataCell(ft.Text(item["field3"])), 
                    ]) 
                ) 
            page.update() 
        except Exception: 
            show_snack("Cannot connect to API", ft.Colors.RED)

    def show_snack(message, color=ft.Colors.GREEN): 
        page.snack_bar = ft.SnackBar( 
            content=ft.Text(message, color=ft.Colors.WHITE), 
            bgcolor=color, 
        ) 
        page.snack_bar.open = True 
        page.update()
        
    main_view = ft.Column( 
        visible=True, 
        expand=True, 
        controls=[ 
            ft.Container( 
                padding=16, 
                content=ft.Column([ 
                    ft.Row( 
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[ 
                            ft.ElevatedButton( 
                                "Refresh", 
                                icon=ft.Icons.REFRESH, 
                                on_click=lambda _: load_table(), 
                            ), 
                        ], 
                    ), 
                    ft.Container(height=8), 
                    ft.Row( 
                        scroll=ft.ScrollMode.AUTO, 
                        controls=[table],
                        
                    )
                ]), 
            ), 
        ], 
    )

    window1 = ft.Container(
        ft.Column([
            navbar,
            ft.Text("GET / flights -> loads data from FastAPI", weight=ft.FontWeight.BOLD, color="#363636", margin=12),
            main_view
        ])
    )

    # ------------- WINDOW 2 --------------
    def submit_record(e): 
        # Validate fields 
        if not flightId.value or not flightNumber.value or not destionation.value or not price.value: 
            show_snack("Please fill in all fields!", ft.Colors.RED) 
            return 
 
        payload = { 
            "flightId":     flightId.value.strip(), 
            "flightNumber": flightNumber.value.strip(), 
            "destionation": destionation.value.strip(), 
            "price": price.value.strip(),
        } 
 
        try: 
            response = requests.post(f"{API_URL}/addFlight", json=payload) 
            result = response.json() 
 
            if "error" in result: 
                # ID already exists in SQLite 
                show_snack(f"Error: {result['error']}", ft.Colors.RED) 
            else: 
                # Clear form fields 
                flightId.value = flightNumber.value = destionation.value = price.value = "" 
                show_snack("Record added successfully!") 
                load_table()      # refresh table from API 
                nav.selected_index = 0 
                main_view.visible = True 
                add_view.visible  = False 
                page.update() 
 
        except Exception: 
            show_snack("API connection error", ft.Colors.RED)

    
    add_view = ft.Column( 
        visible=False, 
        expand=True, 
        controls=[ 
            ft.AppBar( 
                title=ft.Text("Add New Record", color=ft.Colors.WHITE), 
                bgcolor="#1565c0", 
            ), 
            ft.Container( 
                padding=24, 
                content=ft.Column([ 
                    ft.Text("Fill in all fields", size=16, color="#757575"), 
                    ft.Container(height=8), 
                    flightId, 
                    flightNumber, 
                    destionation, 
                    price, 
                    ft.Container(height=16), 
                    ft.ElevatedButton( 
                        "Submit Record", 
                        icon=ft.Icons.SAVE, 
                        bgcolor="#1565c0", 
                        color=ft.Colors.WHITE, 
                        width=320, 
                        on_click=submit_record, 
                    ), 
                ]), 
            ), 
        ], 
    ) 

     # ── Navigation ─────────────────────────────────────
     # 
     #  
    
    
    def nav_change(e): 
        index = e.control.selected_index 
        main_view.visible = (index == 0) 
        add_view.visible  = (index == 1) 
        if index == 0: 
            load_table() 
        page.update() 
 
    nav = ft.NavigationBar( 
        selected_index=0, 
        on_change=nav_change, 
        destinations=[ 
            ft.NavigationBarDestination( 
                icon=ft.Icons.LIST_ALT, 
                label="Records", 
            ), 
            ft.NavigationBarDestination( 
                icon=ft.Icons.ADD_BOX, 
                label="Add New", 
            ), 
        ], 
    )

    
def load_table(search_text: str = ""): 
    try: 
        params = {} 
        if search_text: 
            params["search"] = search_text 
        response = requests.get(f"{API_URL}/items", params=params) 
        table.rows.clear() 
        for item in response.json(): 
            item_id = item["id"] 
 
            def make_delete(iid): 
                def on_delete(e): 
                    r = requests.delete(f"{API_URL}/items/{iid}") 
                    if "error" in r.json(): 
                        show_snack(r.json()["error"], ft.Colors.RED) 
                    else: 
                        show_snack(f"Deleted: {iid}") 
                        load_table(search.value) 
                return on_delete 
 
            def make_edit(row_data): 
                def on_edit(e): 
                    open_edit_dialog(row_data) 
                return on_edit 
 
            table.rows.append( 
                ft.DataRow(cells=[ 
                    ft.DataCell(ft.Text(item["id"])), 
                    ft.DataCell(ft.Text(item["field1"])), 
                    ft.DataCell(ft.Text(item["field2"])), 
                    ft.DataCell(ft.Text(item["field3"])), 
                    ft.DataCell(ft.Row([ 
                        ft.IconButton( 
                            ft.Icons.EDIT, 
                            tooltip="Edit", 
                            on_click=make_edit(item), 
                        ), 
                        ft.IconButton( 
                            ft.Icons.DELETE, 
                            tooltip="Delete", 
                            icon_color=ft.Colors.RED_400, 
                            on_click=make_delete(item_id), 
                        ), 
                    ])), 
                ]) 
            ) 
        page.update() 
    except Exception: 

     
    # ── Layout ───────────────────────────────────────── 
    page.add( 
       
    )

    
def load_table(search_text: str = ""): 
    try: 
        params = {} 
        if search_text: 
            params["search"] = search_text 
        response = requests.get(f"{API_URL}/items", params=params) 
        table.rows.clear() 
        for item in response.json(): 
            item_id = item["id"] 
 
            def make_delete(iid): 
                def on_delete(e): 
                    r = requests.delete(f"{API_URL}/delete/{iid}") 
                    if "error" in r.json(): 
                        show_snack(r.json()["error"], ft.Colors.RED) 
                    else: 
                        show_snack(f"Deleted: {iid}") 
                        load_table(search.value) 
                return on_delete 
 
            def make_edit(row_data): 
                def on_edit(e): 
                    open_edit_dialog(row_data) 
                return on_edit 
 
            table.rows.append( 
                ft.DataRow(cells=[ 
                    ft.DataCell(ft.Text(item["id"])), 
                    ft.DataCell(ft.Text(item["field1"])), 
                    ft.DataCell(ft.Text(item["field2"])), 
                    ft.DataCell(ft.Text(item["field3"])), 
                    ft.DataCell(ft.Row([ 
                        ft.IconButton( 
                            ft.Icons.EDIT, 
                            tooltip="Edit", 
                            on_click=make_edit(item), 
                        ), 
                        ft.IconButton( 
                            ft.Icons.DELETE, 
                            tooltip="Delete", 
                            icon_color=ft.Colors.RED_400, 
                            on_click=make_delete(item_id), 
                        ), 
                    ])), 
                ]) 
            ) 
        page.update() 
    except Exception: 
        show_snack("Cannot connect to API", ft.Colors.RED) 

    window2 = ft.Container(
        ft.Column([

        ])
    )

    page.add(
        window2,
         ft.Column( 
            expand=True, 
            spacing=0, 
            controls=[ 
                ft.Container( 
                    expand=True, 
                    content=ft.Stack([main_view, add_view]), 
                ), 
                nav, 
            ], 
        ) 
    )

    load_table()


ft.run(main)