import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

def add_employee():
    name = name_entry.get()
    position = position_entry.get()
    salary = salary_entry.get()
    hire_date = hire_date_entry.get()

    if not name or not salary or not hire_date:
        messagebox.showwarning("تحذير", "يرجى إدخال جميع البيانات المطلوبة")
        return

    conn = sqlite3.connect("hr_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, position, salary, hire_date) VALUES (?, ?, ?, ?)",
                   (name, position, salary, hire_date))
    conn.commit()
    conn.close()
    messagebox.showinfo("تم", "تمت إضافة الموظف بنجاح")
    refresh_employees()

def refresh_employees():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("hr_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

root = tk.Tk()
root.title("نظام الموارد البشرية")
root.geometry("600x400")

tk.Label(root, text="الاسم:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="الوظيفة:").grid(row=1, column=0)
position_entry = tk.Entry(root)
position_entry.grid(row=1, column=1)

tk.Label(root, text="الراتب:").grid(row=2, column=0)
salary_entry = tk.Entry(root)
salary_entry.grid(row=2, column=1)

tk.Label(root, text="تاريخ التعيين (YYYY-MM-DD):").grid(row=3, column=0)
hire_date_entry = tk.Entry(root)
hire_date_entry.grid(row=3, column=1)

tk.Button(root, text="إضافة موظف", command=add_employee).grid(row=4, column=1, pady=10)

# جدول عرض الموظفين
columns = ("id", "name", "position", "salary", "hire_date")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=2, sticky="nsew")

refresh_employees()

root.mainloop()
