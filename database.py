import sqlite3

DB_NAME = "hr_system.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            position TEXT,
            salary REAL,
            hire_date TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            employee_code TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            check_in TEXT,
            check_out TEXT,
            date TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            month TEXT,
            base_salary REAL,
            allowances REAL,
            deductions REAL,
            bonus REAL,
            total REAL,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ("admin", "admin")
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
