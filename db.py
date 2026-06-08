import sqlite3

from fastapi import FastAPI
from sqlalchemy import Integer
from main import get_connection
from models import Flights

app = FastAPI(
    title="EquipRent Hub API",
    description="Equipment rental management platform API",
    version="1.0.0"
)

@app.get("/flights") 
def get_items(): 
    conn = get_connection() 
    rows = conn.execute("SELECT * FROM flights ORDER BY FLIGHT_ID").fetchall() 
    conn.close() 
    return [dict(row) for row in rows] 

@app.post("/addFlight") 
def add_item(item: Flights): 
    try: 
        conn = get_connection() 
        conn.execute( 
            "INSERT INTO flights (FLIGHT_ID, FLIGHT_NUMBER, DESTINATION, PRICE) VALUES (?, ?, ?, ?)", 
            (item.flightId, item.flightNumber, item.destionation, item.price) 
        ) 
        conn.commit() 
        conn.close() 
        return {"message": "Record added successfully", "item": item} 
    except sqlite3.IntegrityError: 
        return {"error": f"ID '{item.flightId}' already exists"}
    
@app.delete("/delete") 
def delete_item(id: str): 
    try: 
        conn = get_connection() 
        conn.execute( 
            "DELETE FROM flights WHERE FLIGHT_ID = ?", 
            (id) 
        ) 
        conn.commit() 
        conn.close() 
        return {"message": "Record deleted successfully", "item": id} 
    except sqlite3.IntegrityError: 
        return {"error": f"ID '{id}' no exists"}