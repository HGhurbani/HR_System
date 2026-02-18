# HR System (Desktop Application)

A professional Human Resources Management desktop application built with **Python**, **Tkinter**, and **SQLite**.  
The system provides an Arabic RTL-friendly interface for managing employees, attendance, leaves, payroll, and reports.

---

## ✨ Key Features

- **Secure login flow** with hashed admin passwords.
- **Employee management**:
  - Add, edit, search, and delete employee records.
  - Track profile details (department, status, contact info, nationality, profession, etc.).
- **Attendance tracking**:
  - Check-in / check-out records.
  - Daily attendance reporting and status summaries.
- **Leave management**:
  - Register and monitor leave requests.
- **Payroll management**:
  - Store monthly salary details (basic salary, bonuses, deductions, net salary).
  - Prevent duplicate salary entries for the same employee/month/year.
- **Reporting tools** for HR visibility and operations.
- **Database initialization and upgrade utilities** to support evolving schema.
- **Arabic-first UI enhancements** (RTL alignment and font defaults).

---

## 🧱 Tech Stack

- **Language:** Python 3
- **GUI:** Tkinter / ttk
- **Database:** SQLite3
- **Data files:** Local `.db` file (no external DB server required)

---

## 📁 Project Structure

```text
HR_System/
├── main.py        # Main GUI application (login + HR modules)
├── database.py    # DB initialization, safe connection, and schema upgrades
├── hr_system.db   # SQLite database file (generated/used at runtime)
└── README.md
```

---

## 🚀 Getting Started

### 1) Prerequisites

- Python **3.8+** (recommended)
- Tkinter available in your Python distribution

### 2) Clone the repository

```bash
git clone <your-repo-url>
cd HR_System
```

### 3) Run the application

```bash
python main.py
```

> On first run, the app initializes database tables automatically if needed.

---

## 🔐 Default Login

The app creates a default admin account when no admin user exists:

- **Username:** `admin`
- **Password:** `admin`

⚠️ For production usage, change default credentials immediately.

---

## 🗄️ Database Notes

- Main DB file: `hr_system.db`
- Corruption fallback/backup pattern may generate: `hr_system.db.corrupt`
- The app contains schema upgrade logic to keep older databases compatible with newer fields.

---

## 📌 Usage Overview

After login, you can navigate tabs/modules such as:

1. **Employees** – maintain employee records.
2. **Attendance** – register in/out times and view daily summaries.
3. **Leaves** – manage leave entries.
4. **Salaries** – calculate/store monthly payroll details.
5. **Reports** – export and review HR insights.
6. **Settings** – administrative/system options.

---

## 🛠️ Development Tips

- Keep database-related changes centralized in `database.py`.
- Maintain consistency between DB schema and UI field mappings in `main.py`.
- Use UTF-8 encoding for full Arabic text support.

---

## 📄 License

Add your preferred license here (MIT, Apache-2.0, proprietary, etc.).

---

## 🤝 Contributing

Contributions are welcome.

- Open an issue for bug reports or feature requests.
- Submit a pull request with a clear description and testing notes.

