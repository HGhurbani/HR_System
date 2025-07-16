import sqlite3

conn = sqlite3.connect("hr_system.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT,
        salary REAL,
        hire_date TEXT
    )
''')

conn.commit()
conn.close()
