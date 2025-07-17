import sqlite3
import os
import hashlib  # For hashing the default admin password

DB_NAME = "hr_system.db"

def safe_connect():
    """Return a SQLite connection, recreating the DB if corrupted."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        if cur.fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("Integrity check failed")
        return conn
    except sqlite3.DatabaseError:
        if conn:
            conn.close()
        if os.path.exists(DB_NAME):
            backup = DB_NAME + ".corrupt"
            os.replace(DB_NAME, backup)
            print(f"Corrupt database moved to {backup}. Creating new database...")
        init_db()
        return sqlite3.connect(DB_NAME)

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
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                employee_code TEXT UNIQUE,
                birth_date TEXT,
                gender TEXT,
                status TEXT,
                department TEXT,
                location TEXT,
                profession TEXT,
                nationality TEXT,
                religion TEXT,
                marital_status TEXT,
                emp_type TEXT,
                code_number TEXT,
                old_file_number TEXT,
                working_hours TEXT,
                payment_type TEXT,
                contract_entity TEXT
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

def upgrade_db():
    """Upgrade existing database schema and recover if corrupted."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Check database integrity first
        cur.execute("PRAGMA integrity_check")
        result = cur.fetchone()
        if result[0] != "ok":
            raise sqlite3.DatabaseError("Integrity check failed")

        # --- Upgrade employees table ---
        cur.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cur.fetchall()]

        if "full_name" not in columns:
            if "name" in columns:
                cur.execute("ALTER TABLE employees RENAME COLUMN name TO full_name")
            else:
                cur.execute("ALTER TABLE employees ADD COLUMN full_name TEXT")

        # New columns added in later versions
        for col_def in [
            ("email", "TEXT UNIQUE"),
            ("phone", "TEXT"),
            ("address", "TEXT"),
            ("employee_code", "TEXT UNIQUE"),
            ("birth_date", "TEXT"),
            ("gender", "TEXT"),
            ("status", "TEXT"),
            ("department", "TEXT"),
            ("location", "TEXT"),
            ("profession", "TEXT"),
            ("nationality", "TEXT"),
            ("religion", "TEXT"),
            ("marital_status", "TEXT"),
            ("emp_type", "TEXT"),
            ("code_number", "TEXT"),
            ("old_file_number", "TEXT"),
            ("working_hours", "TEXT"),
            ("payment_type", "TEXT"),
            ("contract_entity", "TEXT")
        ]:
            if col_def[0] not in columns:
                cur.execute(f"ALTER TABLE employees ADD COLUMN {col_def[0]} {col_def[1]}")

        conn.commit()

    except sqlite3.DatabaseError as e:
        print(f"Database upgrade error: {e}")
        if conn:
            conn.close()
        # If the database is malformed, recreate it
        if os.path.exists(DB_NAME):
            backup = DB_NAME + ".corrupt"
            os.replace(DB_NAME, backup)
            print(f"Corrupt database moved to {backup}. Creating new database...")
        init_db()
        return
    finally:
        if conn:
            conn.close()
def upgrade_db():
    """Ensure existing databases have required columns"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Upgrade employees table
    cur.execute("PRAGMA table_info(employees)")
    cols = [c[1] for c in cur.fetchall()]
    if 'full_name' not in cols:
        if 'name' in cols:
            try:
                cur.execute("ALTER TABLE employees RENAME COLUMN name TO full_name")
            except sqlite3.OperationalError:
                pass
        else:
            cur.execute("ALTER TABLE employees ADD COLUMN full_name TEXT")
    for col in [
        'email', 'phone', 'address', 'employee_code',
        'birth_date', 'gender', 'status', 'department', 'location',
        'profession', 'nationality', 'religion', 'marital_status',
        'emp_type', 'code_number', 'old_file_number', 'working_hours',
        'payment_type', 'contract_entity']:
        if col not in cols:
            cur.execute(f"ALTER TABLE employees ADD COLUMN {col} TEXT")

    # Upgrade leaves table
    cur.execute("PRAGMA table_info(leaves)")
    cols = [c[1] for c in cur.fetchall()]
    if 'days' not in cols:
        cur.execute("ALTER TABLE leaves ADD COLUMN days INTEGER")
    if 'request_date' not in cols:
        cur.execute("ALTER TABLE leaves ADD COLUMN request_date TEXT")

    # Upgrade salaries table
    cur.execute("PRAGMA table_info(salaries)")
    cols = [c[1] for c in cur.fetchall()]
    if 'year' not in cols:
        cur.execute("ALTER TABLE salaries ADD COLUMN year INTEGER")
    if 'basic_salary' not in cols:
        if 'base_salary' in cols:
            try:
                cur.execute("ALTER TABLE salaries RENAME COLUMN base_salary TO basic_salary")
            except sqlite3.OperationalError:
                pass
        else:
            cur.execute("ALTER TABLE salaries ADD COLUMN basic_salary REAL")
    if 'bonuses' not in cols:
        if 'allowances' in cols:
            try:
                cur.execute("ALTER TABLE salaries RENAME COLUMN allowances TO bonuses")
            except sqlite3.OperationalError:
                pass
        else:
            cur.execute("ALTER TABLE salaries ADD COLUMN bonuses REAL")
    if 'deductions' not in cols:
        cur.execute("ALTER TABLE salaries ADD COLUMN deductions REAL")
    if 'net_salary' not in cols:
        cur.execute("ALTER TABLE salaries ADD COLUMN net_salary REAL")
    if 'payment_date' not in cols:
        cur.execute("ALTER TABLE salaries ADD COLUMN payment_date TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()