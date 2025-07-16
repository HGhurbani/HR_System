import os
import shutil
import csv
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import database

DB_NAME = database.DB_NAME

database.init_db()


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تسجيل الدخول")
        self.geometry("300x150")
        self.resizable(False, False)

        ttk.Label(self, text="اسم المستخدم").pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack()

        ttk.Label(self, text="كلمة المرور").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        ttk.Button(self, text="دخول", command=self.login).pack(pady=10)

    def login(self):
        user = self.username_entry.get()
        pw = self.password_entry.get()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pw))
        row = c.fetchone()
        conn.close()
        if row:
            self.destroy()
            app = HRApp()
            app.mainloop()
        else:
            messagebox.showerror("خطأ", "بيانات الدخول غير صحيحة")


class HRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الموارد البشرية")
        self.geometry("1000x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_leave_tab()
        self.create_salary_tab()
        self.create_report_tab()
        self.create_backup_tab()

    def execute_db(self, query, params=(), fetch=False):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(query, params)
        data = c.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return data

    # ---------------- Employees -----------------
    def create_employee_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="الموظفون")

        labels = [
            "الاسم الكامل",
            "الوظيفة",
            "الراتب",
            "تاريخ التعيين",
            "البريد الإلكتروني",
            "رقم الهاتف",
            "العنوان",
            "الرقم الوظيفي",
        ]
        self.emp_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, pady=2, sticky="ew")
            self.emp_entries[label] = entry

        ttk.Button(frame, text="إضافة", command=self.add_employee).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="حذف", command=self.delete_employee).grid(row=1, column=2, padx=5)
        ttk.Button(frame, text="تحديث", command=self.refresh_employees).grid(row=2, column=2, padx=5)

        columns = (
            "id",
            "full_name",
            "position",
            "salary",
            "hire_date",
            "email",
            "phone",
            "address",
            "employee_code",
        )
        self.emp_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.emp_tree.heading(col, text=col)
        self.emp_tree.grid(row=9, column=0, columnspan=3, sticky="nsew")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)

        self.refresh_employees()

    def add_employee(self):
        values = [e.get() for e in self.emp_entries.values()]
        if not values[0]:
            messagebox.showwarning("تنبيه", "الاسم مطلوب")
            return
        self.execute_db(
            "INSERT INTO employees (full_name, position, salary, hire_date, email, phone, address, employee_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        messagebox.showinfo("تم", "تمت الإضافة")
        self.refresh_employees()
        self.refresh_employees_combobox()

    def delete_employee(self):
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل")
            return
        emp_id = self.emp_tree.item(selected[0])["values"][0]
        self.execute_db("DELETE FROM employees WHERE id=?", (emp_id,))
        self.refresh_employees()
        self.refresh_employees_combobox()

    def refresh_employees(self):
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        rows = self.execute_db("SELECT * FROM employees", fetch=True)
        for row in rows:
            self.emp_tree.insert("", "end", values=row)

    # ---------------- Attendance -----------------
    def create_attendance_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="الحضور والانصراف")

        ttk.Label(frame, text="الموظف").grid(row=0, column=0, pady=5, sticky="w")
        self.atten_emp_var = tk.StringVar()
        self.atten_emp = ttk.Combobox(frame, textvariable=self.atten_emp_var, state="readonly")
        self.atten_emp.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="وقت الحضور").grid(row=1, column=0, pady=5, sticky="w")
        self.check_in_entry = ttk.Entry(frame)
        self.check_in_entry.grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="وقت الانصراف").grid(row=2, column=0, pady=5, sticky="w")
        self.check_out_entry = ttk.Entry(frame)
        self.check_out_entry.grid(row=2, column=1, pady=5, sticky="ew")

        ttk.Button(frame, text="إضافة", command=self.add_attendance).grid(row=3, column=1, pady=5)

        columns = ("id", "employee_id", "check_in", "check_out", "date")
        self.att_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.att_tree.heading(col, text=col)
        self.att_tree.grid(row=4, column=0, columnspan=3, sticky="nsew")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

        self.refresh_employees_combobox()
        self.refresh_attendance()

    def refresh_employees_combobox(self):
        rows = self.execute_db("SELECT id, full_name FROM employees", fetch=True)
        self.emp_dict = {r[1]: r[0] for r in rows}
        names = list(self.emp_dict.keys())
        if hasattr(self, 'atten_emp'):
            self.atten_emp['values'] = names
        if hasattr(self, 'leave_emp'):
            self.leave_emp['values'] = names
        if hasattr(self, 'salary_emp'):
            self.salary_emp['values'] = names

    def add_attendance(self):
        name = self.atten_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return
        check_in = self.check_in_entry.get() or datetime.now().strftime("%H:%M")
        check_out = self.check_out_entry.get()
        date = datetime.now().strftime("%Y-%m-%d")
        self.execute_db(
            "INSERT INTO attendance (employee_id, check_in, check_out, date) VALUES (?, ?, ?, ?)",
            (self.emp_dict[name], check_in, check_out, date),
        )
        self.refresh_attendance()
        self.check_in_entry.delete(0, tk.END)
        self.check_out_entry.delete(0, tk.END)

    def refresh_attendance(self):
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)
        rows = self.execute_db("SELECT * FROM attendance", fetch=True)
        for row in rows:
            self.att_tree.insert("", "end", values=row)

    # ---------------- Leaves -----------------
    def create_leave_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="الإجازات")

        ttk.Label(frame, text="الموظف").grid(row=0, column=0, sticky='w')
        self.leave_emp_var = tk.StringVar()
        self.leave_emp = ttk.Combobox(frame, textvariable=self.leave_emp_var, state="readonly")
        self.leave_emp.grid(row=0, column=1, sticky='ew')

        ttk.Label(frame, text="النوع").grid(row=1, column=0, sticky='w')
        self.leave_type_var = tk.StringVar()
        self.leave_type = ttk.Combobox(frame, textvariable=self.leave_type_var, state="readonly",
                                       values=["إجازة سنوية", "مرضية", "طارئة"])
        self.leave_type.grid(row=1, column=1, sticky='ew')

        ttk.Label(frame, text="من تاريخ").grid(row=2, column=0, sticky='w')
        self.leave_from = ttk.Entry(frame)
        self.leave_from.grid(row=2, column=1, sticky='ew')

        ttk.Label(frame, text="إلى تاريخ").grid(row=3, column=0, sticky='w')
        self.leave_to = ttk.Entry(frame)
        self.leave_to.grid(row=3, column=1, sticky='ew')

        ttk.Label(frame, text="السبب").grid(row=4, column=0, sticky='w')
        self.leave_reason = ttk.Entry(frame)
        self.leave_reason.grid(row=4, column=1, sticky='ew')

        ttk.Button(frame, text="طلب إجازة", command=self.add_leave).grid(row=5, column=1, pady=5)
        ttk.Button(frame, text="اعتماد", command=self.approve_leave).grid(row=5, column=2, pady=5)
        ttk.Button(frame, text="رفض", command=self.reject_leave).grid(row=5, column=3, pady=5)

        columns = (
            "id",
            "employee_id",
            "type",
            "start_date",
            "end_date",
            "reason",
            "status",
        )
        self.leave_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.leave_tree.heading(col, text=col)
        self.leave_tree.grid(row=6, column=0, columnspan=4, sticky='nsew')
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(6, weight=1)
        self.refresh_leaves()

    def add_leave(self):
        name = self.leave_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "اختر الموظف")
            return
        data = (
            self.emp_dict[name],
            self.leave_type_var.get(),
            self.leave_from.get(),
            self.leave_to.get(),
            self.leave_reason.get(),
            "معلق",
        )
        self.execute_db(
            "INSERT INTO leaves (employee_id, type, start_date, end_date, reason, status) VALUES (?, ?, ?, ?, ?, ?)",
            data,
        )
        self.refresh_leaves()

    def approve_leave(self):
        self.update_leave_status("معتمد")

    def reject_leave(self):
        self.update_leave_status("مرفوض")

    def update_leave_status(self, status):
        selected = self.leave_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر طلب إجازة")
            return
        leave_id = self.leave_tree.item(selected[0])["values"][0]
        self.execute_db("UPDATE leaves SET status=? WHERE id=?", (status, leave_id))
        self.refresh_leaves()

    def refresh_leaves(self):
        for row in self.leave_tree.get_children():
            self.leave_tree.delete(row)
        rows = self.execute_db("SELECT * FROM leaves", fetch=True)
        for row in rows:
            self.leave_tree.insert("", "end", values=row)

    # ---------------- Salaries -----------------
    def create_salary_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="الرواتب")

        ttk.Label(frame, text="الموظف").grid(row=0, column=0, sticky='w')
        self.salary_emp_var = tk.StringVar()
        self.salary_emp = ttk.Combobox(frame, textvariable=self.salary_emp_var, state="readonly")
        self.salary_emp.grid(row=0, column=1, sticky='ew')

        ttk.Label(frame, text="الشهر (YYYY-MM)").grid(row=1, column=0, sticky='w')
        self.salary_month = ttk.Entry(frame)
        self.salary_month.grid(row=1, column=1, sticky='ew')

        ttk.Label(frame, text="البدلات").grid(row=2, column=0, sticky='w')
        self.salary_allow = ttk.Entry(frame)
        self.salary_allow.grid(row=2, column=1, sticky='ew')

        ttk.Label(frame, text="الاستقطاعات").grid(row=3, column=0, sticky='w')
        self.salary_ded = ttk.Entry(frame)
        self.salary_ded.grid(row=3, column=1, sticky='ew')

        ttk.Label(frame, text="المكافأة").grid(row=4, column=0, sticky='w')
        self.salary_bonus = ttk.Entry(frame)
        self.salary_bonus.grid(row=4, column=1, sticky='ew')

        ttk.Button(frame, text="حساب", command=self.add_salary).grid(row=5, column=1, pady=5)

        columns = (
            "id",
            "employee_id",
            "month",
            "base_salary",
            "allowances",
            "deductions",
            "bonus",
            "total",
        )
        self.salary_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.salary_tree.heading(col, text=col)
        self.salary_tree.grid(row=6, column=0, columnspan=3, sticky='nsew')
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(6, weight=1)
        self.refresh_salaries()

    def add_salary(self):
        name = self.salary_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "اختر الموظف")
            return
        base_salary = self.execute_db(
            "SELECT salary FROM employees WHERE id=?",
            (self.emp_dict[name],),
            fetch=True,
        )[0][0]
        allow = float(self.salary_allow.get() or 0)
        ded = float(self.salary_ded.get() or 0)
        bonus = float(self.salary_bonus.get() or 0)
        total = base_salary + allow - ded + bonus
        data = (
            self.emp_dict[name],
            self.salary_month.get(),
            base_salary,
            allow,
            ded,
            bonus,
            total,
        )
        self.execute_db(
            """INSERT INTO salaries (employee_id, month, base_salary, allowances, deductions, bonus, total)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.refresh_salaries()
        messagebox.showinfo("تم", "تم حفظ الراتب")

    def refresh_salaries(self):
        for r in self.salary_tree.get_children():
            self.salary_tree.delete(r)
        rows = self.execute_db("SELECT * FROM salaries", fetch=True)
        for row in rows:
            self.salary_tree.insert("", "end", values=row)

    # ---------------- Reports -----------------
    def create_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="التقارير")

        ttk.Button(frame, text="تصدير الموظفين", command=lambda: self.export_csv("employees")).pack(pady=5)
        ttk.Button(frame, text="تصدير الحضور", command=lambda: self.export_csv("attendance")).pack(pady=5)
        ttk.Button(frame, text="تصدير الإجازات", command=lambda: self.export_csv("leaves")).pack(pady=5)
        ttk.Button(frame, text="تصدير الرواتب", command=lambda: self.export_csv("salaries")).pack(pady=5)

    def export_csv(self, table):
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        if not file:
            return
        rows = self.execute_db(f"SELECT * FROM {table}", fetch=True)
        headers = [d[1] for d in self.execute_db(f"PRAGMA table_info({table})", fetch=True)]
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        messagebox.showinfo("تم", "تم تصدير الملف")

    # ---------------- Backup -----------------
    def create_backup_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="النسخ الاحتياطي")
        ttk.Button(frame, text="نسخ احتياطي", command=self.backup_db).pack(pady=10)
        ttk.Button(frame, text="استعادة", command=self.restore_db).pack(pady=10)

    def backup_db(self):
        file = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('DB files', '*.db')])
        if file:
            shutil.copyfile(DB_NAME, file)
            messagebox.showinfo("تم", "تم إنشاء النسخة الاحتياطية")

    def restore_db(self):
        file = filedialog.askopenfilename(filetypes=[('DB files', '*.db')])
        if file:
            shutil.copyfile(file, DB_NAME)
            database.init_db()
            self.refresh_all()
            messagebox.showinfo("تم", "تمت الاستعادة")

    def refresh_all(self):
        self.refresh_employees_combobox()
        self.refresh_employees()
        self.refresh_attendance()
        self.refresh_leaves()
        self.refresh_salaries()


if __name__ == "__main__":
    LoginWindow().mainloop()
