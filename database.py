import sqlite3
import hashlib # For hashing the default admin password

DB_NAME = "hr_system.db"

def init_db():
    """
    Initializes the SQLite database by creating necessary tables
    if they don't already exist and inserts a default admin user.
    """
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create 'employees' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                position TEXT,
                salary REAL,
                hire_date TEXT,
                email TEXT UNIQUE,  -- Added UNIQUE constraint for email
                phone TEXT,
                address TEXT,
                employee_code TEXT UNIQUE -- Added UNIQUE constraint for employee code
            )
        ''')

        # Create 'attendance' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL, -- Changed to NOT NULL
                date TEXT NOT NULL,           -- Changed to NOT NULL
                check_in TEXT,
                check_out TEXT,
                FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE -- Added ON DELETE CASCADE
            )
        ''')

        # Create 'leaves' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL, -- Changed to NOT NULL
                type TEXT NOT NULL,           -- Changed to NOT NULL
                start_date TEXT NOT NULL,     -- Changed to NOT NULL
                end_date TEXT NOT NULL,       -- Changed to NOT NULL
                days INTEGER NOT NULL,        -- Added days column and NOT NULL
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'معلق', -- Added status and default value
                request_date TEXT NOT NULL,      -- Added request_date
                FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE -- Added ON DELETE CASCADE
            )
        ''')

        # Create 'salaries' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL, -- Changed to NOT NULL
                month TEXT NOT NULL,          -- Changed to NOT NULL
                year INTEGER NOT NULL,        -- Added year and NOT NULL
                basic_salary REAL NOT NULL,   -- Renamed from base_salary and NOT NULL
                bonuses REAL DEFAULT 0,       -- Renamed from allowances, added DEFAULT
                deductions REAL DEFAULT 0,    -- Added DEFAULT
                net_salary REAL NOT NULL,     -- Added net_salary and NOT NULL
                payment_date TEXT NOT NULL,   -- Added payment_date
                FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
                UNIQUE(employee_id, month, year) -- Ensures only one salary record per employee per month/year
            )
        ''')

        # Create 'admin' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Added id for better management
                username TEXT UNIQUE NOT NULL,        -- Added UNIQUE and NOT NULL
                password TEXT NOT NULL                -- Changed to NOT NULL
            )
        ''')

        # Insert default admin user if no admin users exist
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            # Hash the default password for security
            default_password_hash = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO admin (username, password) VALUES (?, ?)",
                ("admin", default_password_hash)
            )
            print("Default admin user 'admin' created with password 'admin'.")

        conn.commit()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()