import os
import shutil
import csv
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from collections import defaultdict
import hashlib

# افترض أن ملف database.py موجود في نفس المجلد ويحتوي على DB_NAME
# وإلا، قم بتعريف DB_NAME هنا مباشرة أو قم بتوفير المسار الصحيح للملف
try:
    import database

    DB_NAME = database.DB_NAME
except ImportError:
    DB_NAME = "hr_system.db"  # تعريف افتراضي إذا لم يتم العثور على database.py

# إضافة متغيرات عامة للتحكم في الواجهة
COLORS = {
    'primary': '#2E4057',
    'secondary': '#048A81',
    'success': '#54C392',
    'warning': '#F4B942',
    'danger': '#F45B69',
    'light': '#F8F9FA',
    'dark': '#343A40'
}

# تفعيل المحاذاة من اليمين لليسار
def enable_rtl(root):
    """تهيئة الواجهة للعمل من اليمين لليسار وتحسين الخط"""
    # استخدام خط يدعم العربية بشكل جيد
    default_font = ('Arial', 11)
    root.option_add('*Font', default_font)
    root.option_add('*Label.font', default_font)
    root.option_add('*Entry.font', default_font)
    root.option_add('*Button.font', default_font)
    root.option_add('*Listbox.font', default_font)
    root.option_add('*Menu.font', default_font)

    # محاذاة العناصر لليمين
    root.option_add('*Label.anchor', 'e')
    root.option_add('*Label.justify', 'right')
    root.option_add('*Entry.justify', 'right')
    root.option_add('*Button.justify', 'right')
    root.option_add('*Listbox.justify', 'right')


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الموارد البشرية - تسجيل الدخول")
        self.geometry("450x350")
        self.resizable(False, False)
        self.configure(bg=COLORS['light'])
        enable_rtl(self)

        # إنشاء الواجهة
        self.create_login_ui()

        # محاولة تسجيل دخول تلقائي للمطور
        self.create_default_admin()

        # تركيز على حقل اسم المستخدم
        self.username_entry.focus()

        # ربط مفتاح Enter بتسجيل الدخول
        self.bind('<Return>', lambda event: self.login())

        # تفعيل قائمة النسخ واللصق
        self.add_context_menu(self.username_entry)
        self.add_context_menu(self.password_entry)

    def create_login_ui(self):
        # إطار رئيسي
        main_frame = tk.Frame(self, bg=COLORS['light'])
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)

        # عنوان النظام
        title_label = tk.Label(main_frame, text="نظام الموارد البشرية",
                               font=('Arial', 18, 'bold'),
                               bg=COLORS['light'], fg=COLORS['primary'])
        title_label.pack(pady=(0, 30))

        # إطار تسجيل الدخول
        login_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        login_frame.pack(fill='both', expand=True, padx=20, pady=20)
        login_frame.columnconfigure(0, weight=1)
        login_frame.columnconfigure(1, weight=1)

        # العنوان الفرعي
        subtitle = tk.Label(login_frame, text="تسجيل الدخول",
                            font=('Arial', 14, 'bold'),
                            bg='white', fg=COLORS['primary'])
        subtitle.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # حقل اسم المستخدم
        tk.Label(login_frame, text="اسم المستخدم:",
                 font=('Arial', 10), bg='white', fg=COLORS['dark']) \
            .grid(row=1, column=1, sticky='e', padx=5, pady=(0, 5))
        self.username_entry = tk.Entry(login_frame, font=('Arial', 12),
                                       width=25, relief='solid', bd=1,
                                       justify='right')
        self.username_entry.grid(row=1, column=0, padx=5, pady=(0, 15))
        self.username_entry.insert(0, "admin")

        # حقل كلمة المرور
        tk.Label(login_frame, text="كلمة المرور:",
                 font=('Arial', 10), bg='white', fg=COLORS['dark']) \
            .grid(row=2, column=1, sticky='e', padx=5, pady=(0, 5))
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12),
                                       width=25, show="*", relief='solid', bd=1,
                                       justify='right')
        self.password_entry.grid(row=2, column=0, padx=5, pady=(0, 20))
        self.password_entry.insert(0, "admin")

        # زر تسجيل الدخول
        login_btn = tk.Button(login_frame, text="دخول",
                              font=('Arial', 12, 'bold'),
                              bg=COLORS['primary'], fg='white',
                              width=20, pady=8, cursor='hand2',
                              command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # معلومات المطور
        info_text = "المطور الافتراضي: admin / admin"
        info_label = tk.Label(login_frame, text=info_text,
                              font=('Arial', 9),
                              bg='white', fg=COLORS['secondary'])
        info_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

    def create_default_admin(self):
        """إنشاء حساب مدير افتراضي"""
        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            # تشفير كلمة المرور
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            c.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            # تحقق مما إذا كان الحساب موجوداً مسبقاً
            c.execute("SELECT password FROM admin WHERE username=?", ("admin",))
            row = c.fetchone()
            if row:
                # إذا كانت كلمة المرور غير مشفرة (مثل الإصدارات القديمة)
                if len(row[0]) != 64:
                    c.execute("UPDATE admin SET password=? WHERE username=?",
                              (password_hash, "admin"))
            else:
                c.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                          ("admin", password_hash))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطأ في إنشاء المدير الافتراضي: {e}")

    def login(self):
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()

        if not user or not pw:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        # تشفير كلمة المرور
        password_hash = hashlib.sha256(pw.encode()).hexdigest()

        conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, password_hash))
        row = c.fetchone()
        if not row:
            # التوافق مع قواعد البيانات القديمة حيث كانت كلمة المرور غير مشفرة
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pw))
            row = c.fetchone()
            if row:
                try:
                    c.execute("UPDATE admin SET password=? WHERE username=?", (password_hash, user))
                    conn.commit()
                except Exception as e:
                    print(f"خطأ في ترقية كلمة المرور: {e}")
        conn.close()

        if row:
            self.destroy()
            app = HRApp()
            app.mainloop()
        else:
            messagebox.showerror("خطأ", "بيانات الدخول غير صحيحة")
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

    def add_context_menu(self, widget):
        """إضافة قائمة نسخ/لصق لحقول الإدخال"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="قص", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="نسخ", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="لصق", command=lambda: widget.event_generate("<<Paste>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)


class HRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الموارد البشرية المتقدم")
        self.geometry("1400x800")
        self.state('zoomed')  # تكبير النافذة
        self.configure(bg=COLORS['light'])
        enable_rtl(self)

        # إنشاء شريط الحالة
        self.create_status_bar()

        # إنشاء شريط الأدوات
        self.create_toolbar()

        # تهيئة قاعدة البيانات (نقلها إلى هنا لضمان وجود الجداول قبل استخدامها)
        self.init_database()

        # إنشاء الواجهة الرئيسية
        self.create_main_interface()

        # تحديث الوقت
        self.update_time()

    def init_database(self):
        """تهيئة جداول قاعدة البيانات إذا لم تكن موجودة"""
        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    position TEXT,
                    salary REAL,
                    hire_date TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    employee_code TEXT UNIQUE
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    check_in TEXT,
                    check_out TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    days INTEGER NOT NULL,
                    reason TEXT,
                    status TEXT NOT NULL DEFAULT 'معلق',
                    request_date TEXT NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS salaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    month TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    basic_salary REAL NOT NULL,
                    bonuses REAL DEFAULT 0,
                    deductions REAL DEFAULT 0,
                    net_salary REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                    UNIQUE(employee_id, month, year)
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("خطأ في تهيئة قاعدة البيانات", str(e))

    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_frame = tk.Frame(self, bg=COLORS['primary'], height=30)
        self.status_frame.pack(side='bottom', fill='x')

        self.status_label = tk.Label(self.status_frame, text="جاهز",
                                     bg=COLORS['primary'], fg='white',
                                     font=('Arial', 10))
        self.status_label.pack(side='right', padx=10, pady=5)

        self.time_label = tk.Label(self.status_frame, text="",
                                   bg=COLORS['primary'], fg='white',
                                   font=('Arial', 10))
        self.time_label.pack(side='left', padx=10, pady=5)

    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = tk.Frame(self, bg=COLORS['secondary'], height=50)
        toolbar.pack(side='top', fill='x')

        # أزرار الأدوات
        tools = [
            ("🏠", "الرئيسية", self.go_home),
            ("👥", "الموظفون", lambda: self.notebook.select(0)),
            ("⏰", "الحضور", lambda: self.notebook.select(1)),
            ("🏖️", "الإجازات", lambda: self.notebook.select(2)),
            ("💰", "الرواتب", lambda: self.notebook.select(3)),
            ("📊", "التقارير", lambda: self.notebook.select(4)),
            ("🔧", "الإعدادات", lambda: self.notebook.select(5)),
            ("🚪", "خروج", self.logout)
        ]

        for icon, text, command in tools:
            btn = tk.Button(toolbar, text=f"{icon}\n{text}",
                            bg=COLORS['secondary'], fg='white',
                            font=('Arial', 9), relief='flat',
                            cursor='hand2', command=command,
                            width=8, height=2)
            btn.pack(side='right', padx=2, pady=5)

    def create_main_interface(self):
        """إنشاء الواجهة الرئيسية"""
        # إنشاء notebook محسن
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', tabposition='ne')
        style.configure('TNotebook.Tab', padding=[20, 10])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # إنشاء التبويبات
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_leave_tab()
        self.create_salary_tab()
        self.create_report_tab()
        self.create_settings_tab()

        # إنشاء قاموس البيانات
        self.emp_dict = {}
        self.refresh_employees_combobox()

    def update_time(self):
        """تحديث الوقت في شريط الحالة"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def update_status(self, message):
        """تحديث رسالة الحالة"""
        self.status_label.config(text=message)
        self.after(3000, lambda: self.status_label.config(text="جاهز"))

    def go_home(self):
        """العودة للصفحة الرئيسية"""
        self.notebook.select(0)

    def logout(self):
        """تسجيل الخروج"""
        if messagebox.askyesno("تأكيد", "هل تريد تسجيل الخروج؟"):
            self.destroy()
            LoginWindow().mainloop()

    def execute_db(self, query, params=(), fetch=False):
        """تنفيذ استعلام قاعدة البيانات مع معالجة الأخطاء"""
        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(query, params)
            data = c.fetchall() if fetch else None
            conn.commit()
            conn.close()
            return data
        except Exception as e:
            messagebox.showerror("خطأ في قاعدة البيانات", str(e))
            return None

    def validate_email(self, email):
        """التحقق من صحة البريد الإلكتروني"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """التحقق من صحة رقم الهاتف"""
        pattern = r'^[0-9+\-\s()]{10,15}$'
        return re.match(pattern, phone) is not None

    def refresh_employees_combobox(self):
        """تحديث قائمة الموظفين في مربعات الاختيار"""
        employees = self.execute_db("SELECT id, full_name FROM employees", fetch=True)
        self.emp_dict = {name: eid for eid, name in (employees or [])}

        employee_names = sorted(list(self.emp_dict.keys()))

        if hasattr(self, 'atten_emp'):
            self.atten_emp['values'] = employee_names
        if hasattr(self, 'leave_emp'):
            self.leave_emp['values'] = employee_names
        if hasattr(self, 'salary_emp'):
            self.salary_emp['values'] = employee_names

    # ---------------- تبويب الموظفون المحسن -----------------
    def create_employee_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👥 الموظفون")

        # إطار البحث
        search_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        search_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(search_frame, text="البحث:", font=('Arial', 10, 'bold'),
                 bg='white').pack(side='right', padx=10, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=('Arial', 10), width=30,
                                     justify='right')
        self.search_entry.pack(side='right', padx=5, pady=5)
        self.search_var.trace('w', self.search_employees)

        # إطار الإدخال
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        input_frame.pack(fill='x', padx=10, pady=5)

        # تقسيم الحقول إلى عمودين
        left_frame = tk.Frame(input_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        right_frame = tk.Frame(input_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # الحقول الأساسية
        labels_left = [
            ("الاسم الكامل*", "full_name"),
            ("الوظيفة*", "position"),
            ("الراتب الأساسي*", "salary"),
            ("تاريخ التعيين*", "hire_date")
        ]

        labels_right = [
            ("البريد الإلكتروني", "email"),
            ("رقم الهاتف", "phone"),
            ("العنوان", "address"),
            ("الرقم الوظيفي", "employee_code")
        ]

        self.emp_entries = {}

        for i, (label, key) in enumerate(labels_left):
            tk.Label(left_frame, text=label, font=('Arial', 10),
                     bg='white').grid(row=i, column=1, sticky="e", pady=5)
            entry = tk.Entry(left_frame, font=('Arial', 10), width=25,
                             justify='right')
            entry.grid(row=i, column=0, pady=5, padx=5, sticky="ew")
            self.emp_entries[key] = entry

        for i, (label, key) in enumerate(labels_right):
            tk.Label(right_frame, text=label, font=('Arial', 10),
                     bg='white').grid(row=i, column=1, sticky="e", pady=5)
            entry = tk.Entry(right_frame, font=('Arial', 10), width=25,
                             justify='right')
            entry.grid(row=i, column=0, pady=5, padx=5, sticky="ew")
            self.emp_entries[key] = entry

        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("➕ إضافة موظف", COLORS['success'], self.add_employee),
            ("✏️ تعديل", COLORS['warning'], self.edit_employee_load),  # Changed command
            ("🗑️ حذف", COLORS['danger'], self.delete_employee),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_employees),
            ("📄 طباعة", COLORS['primary'], self.print_employee_report)
        ]

        self.employee_action_buttons = {}  # Store buttons to change command for update
        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=12, pady=5)
            btn.pack(side='right', padx=5)
            self.employee_action_buttons[text] = btn  # Store the button

        # جدول الموظفين المحسن
        table_frame = tk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # أعمدة الجدول
        columns = ("id", "الاسم الكامل", "الوظيفة", "الراتب", "تاريخ التعيين",
                   "البريد الإلكتروني", "الهاتف", "العنوان", "الرقم الوظيفي")

        self.emp_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [50, 150, 120, 100, 100, 180, 120, 200, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=width, anchor='e')

        # إخفاء عمود المعرف
        self.emp_tree.column("id", width=0, stretch=False)
        self.emp_tree.heading("id", text="")

        # أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.emp_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.emp_tree.xview)
        self.emp_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تخطيط الجدول
        self.emp_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # ربط النقر المزدوج بالتعديل
        self.emp_tree.bind('<Double-1>', lambda e: self.edit_employee_load())

        self.refresh_employees()

    def search_employees(self, *args):
        """البحث في الموظفين"""
        search_term = self.search_var.get().lower()
        for item in self.emp_tree.get_children():
            self.emp_tree.delete(item)

        query = """SELECT * FROM employees WHERE 
                  LOWER(full_name) LIKE ? OR 
                  LOWER(position) LIKE ? OR 
                  LOWER(email) LIKE ? OR 
                  LOWER(phone) LIKE ? OR
                  LOWER(employee_code) LIKE ?
                  """
        params = [f"%{search_term}%"] * 5

        rows = self.execute_db(query, params, fetch=True)
        if rows:
            for row in rows:
                self.emp_tree.insert("", "end", values=row)

    def add_employee(self):
        """إضافة موظف جديد مع التحقق من البيانات"""
        # التحقق من البيانات المطلوبة
        required_fields = ["full_name", "position", "salary", "hire_date"]
        for field in required_fields:
            if not self.emp_entries[field].get().strip():
                messagebox.showerror("خطأ", f"الحقل '{field}' مطلوب")
                self.emp_entries[field].focus()
                return

        # التحقق من صحة البريد الإلكتروني
        email = self.emp_entries["email"].get().strip()
        if email and not self.validate_email(email):
            messagebox.showerror("خطأ", "البريد الإلكتروني غير صحيح")
            self.emp_entries["email"].focus()
            return

        # التحقق من صحة رقم الهاتف
        phone = self.emp_entries["phone"].get().strip()
        if phone and not self.validate_phone(phone):
            messagebox.showerror("خطأ", "رقم الهاتف غير صحيح")
            self.emp_entries["phone"].focus()
            return

        # التحقق من صحة الراتب
        try:
            salary = float(self.emp_entries["salary"].get())
            if salary < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("خطأ", "الراتب يجب أن يكون رقماً موجباً")
            self.emp_entries["salary"].focus()
            return

        # التحقق من تاريخ التعيين
        try:
            hire_date = self.emp_entries["hire_date"].get().strip()
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "تاريخ التعيين يجب أن يكون بالشكل YYYY-MM-DD")
            self.emp_entries["hire_date"].focus()
            return

        # إضافة الموظف
        values = [self.emp_entries[key].get().strip() for key in
                  ["full_name", "position", "salary", "hire_date", "email", "phone", "address", "employee_code"]]

        result = self.execute_db(
            "INSERT INTO employees (full_name, position, salary, hire_date, email, phone, address, employee_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )

        if result is not None:
            messagebox.showinfo("تم", "تمت إضافة الموظف بنجاح")
            self.clear_employee_entries()
            self.refresh_employees()
            self.refresh_employees_combobox()
            self.update_status("تم إضافة موظف جديد")

    def edit_employee_load(self):
        """تحميل بيانات الموظف المحدد في حقول الإدخال للتعديل"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للتعديل")
            return

        emp_data = self.emp_tree.item(selected[0])["values"]

        # ملء الحقول ببيانات الموظف
        fields = ["id", "full_name", "position", "salary", "hire_date", "email", "phone", "address", "employee_code"]
        for i, field in enumerate(fields):
            if field == "id":  # Skip ID for entry fields
                continue
            self.emp_entries[field].delete(0, tk.END)
            self.emp_entries[field].insert(0, emp_data[i])

        # تغيير نص زر "إضافة موظف" إلى "تحديث" وتغيير وظيفته
        self.employee_action_buttons["➕ إضافة موظف"].config(text="✔️ تحديث الموظف", command=self.update_employee,
                                                            bg=COLORS['warning'])
        self.update_status("تم تحميل بيانات الموظف للتعديل. اضغط 'تحديث الموظف' بعد التعديل.")

    def update_employee(self):
        """تحديث بيانات الموظف"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للتحديث")
            return

        emp_id = self.emp_tree.item(selected[0])["values"][0]  # Get ID from the first element of selected row

        # التحقق من البيانات المطلوبة
        required_fields = ["full_name", "position", "salary", "hire_date"]
        for field in required_fields:
            if not self.emp_entries[field].get().strip():
                messagebox.showerror("خطأ", f"الحقل '{field}' مطلوب")
                self.emp_entries[field].focus()
                return

        # التحقق من صحة البريد الإلكتروني
        email = self.emp_entries["email"].get().strip()
        if email and not self.validate_email(email):
            messagebox.showerror("خطأ", "البريد الإلكتروني غير صحيح")
            self.emp_entries["email"].focus()
            return

        # التحقق من صحة رقم الهاتف
        phone = self.emp_entries["phone"].get().strip()
        if phone and not self.validate_phone(phone):
            messagebox.showerror("خطأ", "رقم الهاتف غير صحيح")
            self.emp_entries["phone"].focus()
            return

        # التحقق من صحة الراتب
        try:
            salary = float(self.emp_entries["salary"].get())
            if salary < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("خطأ", "الراتب يجب أن يكون رقماً موجباً")
            self.emp_entries["salary"].focus()
            return

        # التحقق من تاريخ التعيين
        try:
            hire_date = self.emp_entries["hire_date"].get().strip()
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "تاريخ التعيين يجب أن يكون بالشكل YYYY-MM-DD")
            self.emp_entries["hire_date"].focus()
            return

        values = [self.emp_entries[key].get().strip() for key in
                  ["full_name", "position", "salary", "hire_date", "email", "phone", "address", "employee_code"]]
        values.append(emp_id)

        result = self.execute_db(
            "UPDATE employees SET full_name=?, position=?, salary=?, hire_date=?, email=?, phone=?, address=?, employee_code=? WHERE id=?",
            values,
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تحديث بيانات الموظف")
            self.clear_employee_entries()
            self.refresh_employees()
            self.refresh_employees_combobox()
            self.update_status(f"تم تحديث بيانات الموظف ID: {emp_id}")
            # إعادة الزر إلى حالته الأصلية
            self.employee_action_buttons["➕ إضافة موظف"].config(text="➕ إضافة موظف", command=self.add_employee,
                                                                bg=COLORS['success'])

    def delete_employee(self):
        """حذف موظف مع التأكيد"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للحذف")
            return

        emp_data = self.emp_tree.item(selected[0])["values"]
        emp_name = emp_data[1]

        if messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف الموظف '{emp_name}'؟\nهذا الإجراء لا يمكن التراجع عنه."):
            emp_id = emp_data[0]
            result = self.execute_db("DELETE FROM employees WHERE id=?", (emp_id,))

            if result is not None:
                messagebox.showinfo("تم", "تم حذف الموظف")
                self.refresh_employees()
                self.refresh_employees_combobox()
                self.update_status(f"تم حذف الموظف {emp_name}")
                self.clear_employee_entries()  # Clear entries after deletion

    def clear_employee_entries(self):
        """مسح جميع حقول الموظف وإعادة زر التحديث إلى إضافة"""
        for entry in self.emp_entries.values():
            entry.delete(0, tk.END)
        self.employee_action_buttons["➕ إضافة موظف"].config(text="➕ إضافة موظف", command=self.add_employee,
                                                            bg=COLORS['success'])
        self.emp_tree.selection_remove(self.emp_tree.selection())  # Deselect any selected item

    def print_employee_report(self):
        """طباعة تقرير الموظفين"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="حفظ تقرير الموظفين")
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = ["المعرف", "الاسم الكامل", "الوظيفة", "الراتب", "تاريخ التعيين",
                           "البريد الإلكتروني", "الهاتف", "العنوان", "الرقم الوظيفي"]
                writer.writerow(headers)

                rows = self.execute_db("SELECT * FROM employees ORDER BY full_name", fetch=True)
                if rows:
                    for row in rows:
                        writer.writerow(row)
            messagebox.showinfo("تم", f"تم حفظ تقرير الموظفين في: {file_path}")
            self.update_status("تم إنشاء تقرير الموظفين بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ في الطباعة", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def refresh_employees(self):
        """تحديث قائمة الموظفين"""
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)

        rows = self.execute_db("SELECT * FROM employees ORDER BY full_name", fetch=True)
        if rows:
            for row in rows:
                self.emp_tree.insert("", "end", values=row)

        self.update_status(f"تم تحديث قائمة الموظفين ({len(rows) if rows else 0} موظف)")

    # ---------------- تبويب الحضور والانصراف المحسن -----------------
    def create_attendance_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⏰ الحضور والانصراف")

        # إطار الإدخال
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان
        tk.Label(input_frame, text="تسجيل الحضور والانصراف",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # الحقول
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # الموظف
        tk.Label(fields_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=0, column=1, sticky="e", pady=5)
        self.atten_emp_var = tk.StringVar()
        self.atten_emp = ttk.Combobox(fields_frame, textvariable=self.atten_emp_var,
                                      state="readonly", width=30, font=('Arial', 10))
        self.atten_emp.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        # التاريخ
        tk.Label(fields_frame, text="التاريخ:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=1, column=1, sticky="e", pady=5)
        self.attendance_date = tk.Entry(fields_frame, font=('Arial', 10), width=30,
                                        justify='right')
        self.attendance_date.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # وقت الحضور
        tk.Label(fields_frame, text="وقت الحضور:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=2, column=1, sticky="e", pady=5)
        self.check_in_entry = tk.Entry(fields_frame, font=('Arial', 10), width=30,
                                       justify='right')
        self.check_in_entry.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        # وقت الانصراف
        tk.Label(fields_frame, text="وقت الانصراف:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=3, column=1, sticky="e", pady=5)
        self.check_out_entry = tk.Entry(fields_frame, font=('Arial', 10), width=30,
                                        justify='right')
        self.check_out_entry.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

        fields_frame.columnconfigure(0, weight=1)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("⏰ تسجيل حضور", COLORS['success'], self.add_check_in),
            ("🏃 تسجيل انصراف", COLORS['warning'], self.add_check_out),
            ("📝 تسجيل كامل", COLORS['primary'], self.add_attendance),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_attendance),
            ("📊 تقرير يومي", COLORS['primary'], self.daily_attendance_report)
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=15, pady=5)
            btn.pack(side='right', padx=5)

        # إطار الإحصائيات
        stats_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        stats_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(stats_frame, text="إحصائيات اليوم",
                 font=('Arial', 12, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=5)

        self.stats_labels = {}
        stats_info = tk.Frame(stats_frame, bg='white')
        stats_info.pack(fill='x', padx=20, pady=10)

        stats_items = [
            ("الحاضرون", "present"),
            ("المتأخرون", "late"),
            ("الغائبون", "absent"),
            ("ساعات العمل", "work_hours")
        ]

        for i, (text, key) in enumerate(stats_items):
            tk.Label(stats_info, text=f"{text}:", font=('Arial', 10, 'bold'),
                     bg='white').grid(row=0, column=i * 2, padx=10, pady=5, sticky='e')
            self.stats_labels[key] = tk.Label(stats_info, text="0",
                                              font=('Arial', 10), bg='white',
                                              fg=COLORS['secondary'])
            self.stats_labels[key].grid(row=0, column=i * 2 + 1, padx=5, pady=5, sticky='e')

        # جدول الحضور
        table_frame = tk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة")
        self.att_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 200, 120, 120, 120, 120, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.att_tree.heading(col, text=col)
            self.att_tree.column(col, width=width, anchor='e')

        # إخفاء عمود المعرف
        self.att_tree.column("id", width=0, stretch=False)
        self.att_tree.heading("id", text="")

        # أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.att_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.att_tree.xview)
        self.att_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تخطيط الجدول
        self.att_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.refresh_attendance()
        self.update_attendance_stats()

    def add_check_in(self):
        """تسجيل الحضور فقط"""
        name = self.atten_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return

        date = self.attendance_date.get() or datetime.now().strftime("%Y-%m-%d")
        check_in = self.check_in_entry.get() or datetime.now().strftime("%H:%M")

        # التحقق من وجود تسجيل سابق لنفس اليوم
        existing = self.execute_db(
            "SELECT * FROM attendance WHERE employee_id=? AND date=?",
            (self.emp_dict[name], date), fetch=True
        )

        if existing:
            messagebox.showwarning("تنبيه", "الموظف مسجل حضوره لهذا اليوم")
            return

        result = self.execute_db(
            "INSERT INTO attendance (employee_id, check_in, date) VALUES (?, ?, ?)",
            (self.emp_dict[name], check_in, date)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الحضور")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()

    def add_check_out(self):
        """تسجيل الانصراف فقط"""
        name = self.atten_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return

        date = self.attendance_date.get() or datetime.now().strftime("%Y-%m-%d")
        check_out = self.check_out_entry.get() or datetime.now().strftime("%H:%M")

        # البحث عن تسجيل الحضور
        existing = self.execute_db(
            "SELECT * FROM attendance WHERE employee_id=? AND date=? AND check_in IS NOT NULL",
            (self.emp_dict[name], date), fetch=True
        )

        if not existing:
            messagebox.showwarning("تنبيه", "لم يتم تسجيل حضور الموظف لهذا اليوم")
            return

        if existing[0][4]:  # إذا كان الانصراف مسجل مسبقاً
            messagebox.showwarning("تنبيه", "الموظف مسجل انصرافه لهذا اليوم")
            return

        result = self.execute_db(
            "UPDATE attendance SET check_out=? WHERE employee_id=? AND date=?",
            (check_out, self.emp_dict[name], date)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الانصراف")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()

    def add_attendance(self):
        """تسجيل الحضور والانصراف معاً"""
        name = self.atten_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return

        date = self.attendance_date.get() or datetime.now().strftime("%Y-%m-%d")
        check_in = self.check_in_entry.get()
        check_out = self.check_out_entry.get()

        if not check_in or not check_out:
            messagebox.showerror("خطأ", "يجب إدخال وقتي الحضور والانصراف للتسجيل الكامل")
            return

        # التحقق من وجود تسجيل سابق لنفس اليوم
        existing = self.execute_db(
            "SELECT * FROM attendance WHERE employee_id=? AND date=?",
            (self.emp_dict[name], date), fetch=True
        )

        if existing:
            messagebox.showwarning("تنبيه", "الموظف لديه تسجيل حضور/انصراف لهذا اليوم بالفعل. يرجى التحديث يدوياً.")
            return

        result = self.execute_db(
            "INSERT INTO attendance (employee_id, check_in, check_out, date) VALUES (?, ?, ?, ?)",
            (self.emp_dict[name], check_in, check_out, date)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الحضور والانصراف")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()

    def calculate_work_hours(self, check_in, check_out):
        """حساب ساعات العمل"""
        if not check_in or not check_out:
            return "غير محدد"

        try:
            in_time = datetime.strptime(check_in, "%H:%M")
            out_time = datetime.strptime(check_out, "%H:%M")

            # إذا كان الانصراف في اليوم التالي
            if out_time < in_time:
                out_time += timedelta(days=1)

            work_duration = out_time - in_time
            hours = work_duration.total_seconds() / 3600
            return f"{hours:.2f} ساعة"
        except:
            return "خطأ في الحساب"

    def get_attendance_status(self, check_in, check_out):
        """تحديد حالة الحضور"""
        if not check_in:
            return "غائب"

        try:
            in_time = datetime.strptime(check_in, "%H:%M")
            work_start = datetime.strptime("08:00", "%H:%M")  # يمكن جعل هذا إعداداً

            if in_time > work_start:
                return "متأخر"
            elif check_out:
                return "حاضر"
            else:
                return "لم ينصرف"
        except:
            return "خطأ"

    def update_attendance_stats(self):
        """تحديث إحصائيات الحضور"""
        today = datetime.now().strftime("%Y-%m-%d")

        # إحصائيات اليوم
        stats = self.execute_db(
            "SELECT check_in, check_out FROM attendance WHERE date=?",
            (today,), fetch=True
        )

        present = 0
        late = 0
        total_hours = 0

        if stats:
            for s in stats:
                if s[0]:  # If check_in exists
                    present += 1
                    try:
                        in_time = datetime.strptime(s[0], "%H:%M")
                        work_start = datetime.strptime("08:00", "%H:%M")
                        if in_time > work_start:
                            late += 1
                    except ValueError:
                        pass  # Handle invalid time format

                if s[0] and s[1]:  # If both check_in and check_out exist
                    try:
                        in_time = datetime.strptime(s[0], "%H:%M")
                        out_time = datetime.strptime(s[1], "%H:%M")
                        if out_time < in_time:
                            out_time += timedelta(days=1)
                        total_hours += (out_time - in_time).total_seconds() / 3600
                    except ValueError:
                        continue  # Handle invalid time format

            total_employees = len(self.execute_db("SELECT id FROM employees", fetch=True) or [])
            absent = total_employees - present

            self.stats_labels['present'].config(text=str(present))
            self.stats_labels['late'].config(text=str(late))
            self.stats_labels['absent'].config(text=str(absent))
            self.stats_labels['work_hours'].config(text=f"{total_hours:.1f}")
        else:
            total_employees = len(self.execute_db("SELECT id FROM employees", fetch=True) or [])
            for key in self.stats_labels:
                if key == 'absent':
                    self.stats_labels[key].config(text=str(total_employees))
                else:
                    self.stats_labels[key].config(text="0")

    def clear_attendance_entries(self):
        """مسح حقول الحضور"""
        self.atten_emp_var.set('')  # Clear combobox selection
        self.check_in_entry.delete(0, tk.END)
        self.check_out_entry.delete(0, tk.END)
        self.attendance_date.delete(0, tk.END)
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def daily_attendance_report(self):
        """تقرير الحضور اليومي"""
        today = datetime.now().strftime("%Y-%m-%d")

        report_data = self.execute_db(
            """
            SELECT e.full_name, a.date, a.check_in, a.check_out
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.date = ?
            ORDER BY e.full_name
            """,
            (today,), fetch=True
        )

        if not report_data:
            messagebox.showinfo("تقرير الحضور اليومي", f"لا توجد بيانات حضور لليوم {today}")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title=f"حفظ تقرير حضور {today}")
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة"])

                for row in report_data:
                    work_hours = self.calculate_work_hours(row[2], row[3])
                    status = self.get_attendance_status(row[2], row[3])
                    writer.writerow([row[0], row[1], row[2] or "غائب", row[3] or "لم ينصرف", work_hours, status])
            messagebox.showinfo("تم", f"تم حفظ تقرير الحضور اليومي في: {file_path}")
            self.update_status(f"تم إنشاء تقرير الحضور لليوم {today}")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def refresh_attendance(self):
        """تحديث جدول الحضور"""
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)

        # استعلام محسن مع أسماء الموظفين
        query = """
        SELECT a.id, e.full_name, a.date, a.check_in, a.check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        ORDER BY a.date DESC, a.check_in DESC
        """

        rows = self.execute_db(query, fetch=True)
        if rows:
            for row in rows:
                work_hours = self.calculate_work_hours(row[3], row[4])
                status = self.get_attendance_status(row[3], row[4])

                display_row = (
                    row[0], row[1], row[2], row[3] or "لم يحضر",
                    row[4] or "لم ينصرف", work_hours, status
                )
                self.att_tree.insert("", "end", values=display_row)
        self.update_attendance_stats()  # Update stats when refreshing table
        self.update_status(f"تم تحديث جدول الحضور ({len(rows) if rows else 0} سجل)")

    # ---------------- تبويب الإجازات المحسن -----------------
    def create_leave_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏖️ الإجازات")

        # إطار الإدخال
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان
        tk.Label(input_frame, text="إدارة الإجازات",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # الحقول
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # تقسيم الحقول
        left_frame = tk.Frame(fields_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10)

        right_frame = tk.Frame(fields_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10)

        # الحقول الأساسية
        tk.Label(left_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=0, column=1, sticky='e', pady=5)
        self.leave_emp_var = tk.StringVar()
        self.leave_emp = ttk.Combobox(left_frame, textvariable=self.leave_emp_var,
                                      state="readonly", width=25, font=('Arial', 10))
        self.leave_emp.grid(row=0, column=0, pady=5, sticky='ew')

        tk.Label(left_frame, text="نوع الإجازة:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=1, column=1, sticky='e', pady=5)
        self.leave_type_var = tk.StringVar()
        self.leave_type = ttk.Combobox(left_frame, textvariable=self.leave_type_var,
                                       state="readonly", width=25, font=('Arial', 10),
                                       values=["إجازة سنوية", "إجازة مرضية", "إجازة طارئة",
                                               "إجازة أمومة", "إجازة أبوة", "إجازة بدون راتب"])
        self.leave_type.grid(row=1, column=0, pady=5, sticky='ew')

        tk.Label(left_frame, text="من تاريخ:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=2, column=1, sticky='e', pady=5)
        self.leave_from = tk.Entry(left_frame, font=('Arial', 10), width=25,
                                   justify='right')
        self.leave_from.grid(row=2, column=0, pady=5, sticky='ew')

        tk.Label(right_frame, text="إلى تاريخ:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=0, column=1, sticky='e', pady=5)
        self.leave_to = tk.Entry(right_frame, font=('Arial', 10), width=25,
                                 justify='right')
        self.leave_to.grid(row=0, column=0, pady=5, sticky='ew')

        tk.Label(right_frame, text="عدد الأيام:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=1, column=1, sticky='e', pady=5)
        self.leave_days = tk.Entry(right_frame, font=('Arial', 10), width=25, state='readonly',
                                   justify='right')
        self.leave_days.grid(row=1, column=0, pady=5, sticky='ew')

        tk.Label(right_frame, text="السبب:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=2, column=1, sticky='e', pady=5)
        self.leave_reason = tk.Entry(right_frame, font=('Arial', 10), width=25,
                                     justify='right')
        self.leave_reason.grid(row=2, column=0, pady=5, sticky='ew')

        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # ربط تغيير التاريخ بحساب الأيام
        self.leave_from.bind('<KeyRelease>', self.calculate_leave_days)
        self.leave_to.bind('<KeyRelease>', self.calculate_leave_days)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("📝 طلب إجازة", COLORS['primary'], self.add_leave),
            ("✅ اعتماد", COLORS['success'], self.approve_leave),
            ("❌ رفض", COLORS['danger'], self.reject_leave),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_leaves),
            ("📊 إحصائيات", COLORS['warning'], self.leave_statistics)
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=12, pady=5)
            btn.pack(side='right', padx=5)

        # جدول الإجازات
        table_frame = tk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "الموظف", "النوع", "من", "إلى", "الأيام", "السبب", "الحالة", "تاريخ الطلب")
        self.leave_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 150, 100, 100, 100, 80, 200, 100, 120]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=width, anchor='e')

        # إخفاء عمود المعرف
        self.leave_tree.column("id", width=0, stretch=False)
        self.leave_tree.heading("id", text="")

        # أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.leave_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.leave_tree.xview)
        self.leave_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تخطيط الجدول
        self.leave_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.refresh_leaves()

    def calculate_leave_days(self, event=None):
        """حساب عدد أيام الإجازة"""
        try:
            from_date_str = self.leave_from.get()
            to_date_str = self.leave_to.get()

            if not from_date_str or not to_date_str:
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.config(state='readonly')
                return

            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

            if to_date >= from_date:
                days = (to_date - from_date).days + 1
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.insert(0, str(days))
                self.leave_days.config(state='readonly')
            else:
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.insert(0, "تاريخ غير صحيح")
                self.leave_days.config(state='readonly')
        except ValueError:
            self.leave_days.config(state='normal')
            self.leave_days.delete(0, tk.END)
            self.leave_days.insert(0, "تنسيق تاريخ خاطئ")
            self.leave_days.config(state='readonly')

    def add_leave(self):
        """إضافة طلب إجازة"""
        name = self.leave_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "اختر الموظف")
            return

        # التحقق من البيانات
        if not all([self.leave_type_var.get(), self.leave_from.get(),
                    self.leave_to.get(), self.leave_reason.get()]):
            messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
            return

        # التحقق من صحة التواريخ
        try:
            from_date = datetime.strptime(self.leave_from.get(), "%Y-%m-%d")
            to_date = datetime.strptime(self.leave_to.get(), "%Y-%m-%d")

            if to_date < from_date:
                messagebox.showerror("خطأ", "تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية")
                return
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD")
            return

        # حساب عدد الأيام
        days = (to_date - from_date).days + 1

        data = (
            self.emp_dict[name],
            self.leave_type_var.get(),
            self.leave_from.get(),
            self.leave_to.get(),
            days,
            self.leave_reason.get(),
            "معلق",
            datetime.now().strftime("%Y-%m-%d")
        )

        result = self.execute_db(
            "INSERT INTO leaves (employee_id, type, start_date, end_date, days, reason, status, request_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم إرسال طلب الإجازة")
            self.clear_leave_entries()
            self.refresh_leaves()
            self.update_status("تم إضافة طلب إجازة جديد")

    def approve_leave(self):
        """اعتماد الإجازة"""
        self.update_leave_status("معتمد")

    def reject_leave(self):
        """رفض الإجازة"""
        self.update_leave_status("مرفوض")

    def update_leave_status(self, status):
        """تحديث حالة الإجازة"""
        selected = self.leave_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر طلب إجازة")
            return

        leave_data = self.leave_tree.item(selected[0])["values"]
        employee_name = leave_data[1]

        if messagebox.askyesno("تأكيد", f"هل تريد {status} إجازة الموظف {employee_name}؟"):
            leave_id = leave_data[0]
            result = self.execute_db("UPDATE leaves SET status=? WHERE id=?", (status, leave_id))

            if result is not None:
                messagebox.showinfo("تم", f"تم {status} الإجازة")
                self.refresh_leaves()
                self.update_status(f"تم {status} إجازة {employee_name}")
                self.clear_leave_entries()  # Clear entries after action

    def clear_leave_entries(self):
        """مسح حقول الإجازة"""
        self.leave_emp_var.set('')
        self.leave_type_var.set('')
        self.leave_from.delete(0, tk.END)
        self.leave_to.delete(0, tk.END)
        self.leave_reason.delete(0, tk.END)
        self.leave_days.config(state='normal')
        self.leave_days.delete(0, tk.END)
        self.leave_days.config(state='readonly')
        self.leave_tree.selection_remove(self.leave_tree.selection())  # Deselect any selected item

    def leave_statistics(self):
        """إحصائيات الإجازات"""
        approved_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'معتمد'", fetch=True)
        pending_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'معلق'", fetch=True)
        rejected_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'مرفوض'", fetch=True)

        approved_count = approved_leaves[0][0] if approved_leaves else 0
        pending_count = pending_leaves[0][0] if pending_leaves else 0
        rejected_count = rejected_leaves[0][0] if rejected_leaves else 0

        messagebox.showinfo("إحصائيات الإجازات",
                            f"إجازات معتمدة: {approved_count}\n"
                            f"إجازات معلقة: {pending_count}\n"
                            f"إجازات مرفوضة: {rejected_count}")

    def refresh_leaves(self):
        """تحديث جدول الإجازات"""
        for row in self.leave_tree.get_children():
            self.leave_tree.delete(row)

        # استعلام محسن
        query = """
        SELECT l.id, e.full_name, l.type, l.start_date, l.end_date, 
               l.days, l.reason, l.status, l.request_date
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
        ORDER BY l.request_date DESC
        """

        rows = self.execute_db(query, fetch=True)
        if rows:
            for row in rows:
                self.leave_tree.insert("", "end", values=row)
        self.update_status(f"تم تحديث جدول الإجازات ({len(rows) if rows else 0} طلب)")

    # ---------------- تبويب الرواتب المحسن -----------------
    def create_salary_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💰 الرواتب")

        # إطار الإدخال
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان
        tk.Label(input_frame, text="إدارة الرواتب",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # الحقول
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # تقسيم الحقول
        left_frame = tk.Frame(fields_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10)

        right_frame = tk.Frame(fields_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10)

        # الحقول الأساسية
        tk.Label(left_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=0, column=1, sticky='e', pady=5)
        self.salary_emp_var = tk.StringVar()
        self.salary_emp = ttk.Combobox(left_frame, textvariable=self.salary_emp_var,
                                       state="readonly", width=25, font=('Arial', 10))
        self.salary_emp.grid(row=0, column=0, pady=5, sticky='ew')
        self.salary_emp.bind("<<ComboboxSelected>>", self.load_employee_salary)

        tk.Label(left_frame, text="الشهر:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=1, column=1, sticky='e', pady=5)
        self.salary_month = ttk.Combobox(left_frame, values=[f"{i:02d}" for i in range(1, 13)],
                                         state="readonly", width=25, font=('Arial', 10))
        self.salary_month.grid(row=1, column=0, pady=5, sticky='ew')
        self.salary_month.set(datetime.now().strftime("%m"))

        tk.Label(left_frame, text="السنة:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=2, column=1, sticky='e', pady=5)
        self.salary_year = ttk.Combobox(left_frame, values=[str(i) for i in
                                                            range(datetime.now().year - 5, datetime.now().year + 2)],
                                        state="readonly", width=25, font=('Arial', 10))
        self.salary_year.grid(row=2, column=0, pady=5, sticky='ew')
        self.salary_year.set(datetime.now().year)

        tk.Label(right_frame, text="الراتب الأساسي:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=0, column=1, sticky='e', pady=5)
        self.basic_salary_entry = tk.Entry(right_frame, font=('Arial', 10), width=25, state='readonly',
                                           justify='right')
        self.basic_salary_entry.grid(row=0, column=0, pady=5, sticky='ew')

        tk.Label(right_frame, text="المكافآت:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=1, column=1, sticky='e', pady=5)
        self.bonuses_entry = tk.Entry(right_frame, font=('Arial', 10), width=25,
                                     justify='right')
        self.bonuses_entry.grid(row=1, column=0, pady=5, sticky='ew')
        self.bonuses_entry.insert(0, "0.0")

        tk.Label(right_frame, text="الخصومات:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=2, column=1, sticky='e', pady=5)
        self.deductions_entry = tk.Entry(right_frame, font=('Arial', 10), width=25,
                                        justify='right')
        self.deductions_entry.grid(row=2, column=0, pady=5, sticky='ew')
        self.deductions_entry.insert(0, "0.0")

        tk.Label(right_frame, text="صافي الراتب:", font=('Arial', 10, 'bold'),
                 bg='white').grid(row=3, column=1, sticky='e', pady=5)
        self.net_salary_label = tk.Label(right_frame, text="0.0", font=('Arial', 10, 'bold'),
                                         bg='white', fg=COLORS['primary'])
        self.net_salary_label.grid(row=3, column=0, pady=5, sticky='ew')

        # Bind events to calculate net salary automatically
        self.bonuses_entry.bind('<KeyRelease>', self.calculate_net_salary)
        self.deductions_entry.bind('<KeyRelease>', self.calculate_net_salary)
        self.salary_emp.bind('<<ComboboxSelected>>', self.load_employee_salary)

        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("➕ إضافة راتب", COLORS['success'], self.add_salary),
            ("✏️ تعديل راتب", COLORS['warning'], self.edit_salary),
            ("🗑️ حذف راتب", COLORS['danger'], self.delete_salary),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_salaries),
            ("📄 طباعة كشوفات", COLORS['primary'], self.print_payslips)
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=15, pady=5)
            btn.pack(side='right', padx=5)

        # جدول الرواتب
        table_frame = tk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "الموظف", "الشهر", "السنة", "الراتب الأساسي",
                   "المكافآت", "الخصومات", "صافي الراتب", "تاريخ الدفع")
        self.salary_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 150, 80, 80, 120, 100, 100, 120, 120]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.salary_tree.heading(col, text=col)
            self.salary_tree.column(col, width=width, anchor='e')

        # إخفاء عمود المعرف
        self.salary_tree.column("id", width=0, stretch=False)
        self.salary_tree.heading("id", text="")

        # أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.salary_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.salary_tree.xview)
        self.salary_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تخطيط الجدول
        self.salary_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.salary_tree.bind('<Double-1>', self.load_salary_for_edit)  # Bind double click to load for edit

        self.refresh_salaries()

    def load_employee_salary(self, event=None):
        """تحميل الراتب الأساسي للموظف المحدد"""
        selected_name = self.salary_emp_var.get()
        if selected_name:
            emp_id = self.emp_dict.get(selected_name)
            if emp_id:
                employee_data = self.execute_db("SELECT salary FROM employees WHERE id = ?", (emp_id,), fetch=True)
                if employee_data:
                    basic_salary = employee_data[0][0]
                    self.basic_salary_entry.config(state='normal')
                    self.basic_salary_entry.delete(0, tk.END)
                    self.basic_salary_entry.insert(0, str(basic_salary))
                    self.basic_salary_entry.config(state='readonly')
                    self.calculate_net_salary()  # Recalculate net salary when basic salary changes

    def calculate_net_salary(self, event=None):
        """حساب صافي الراتب"""
        try:
            basic_salary = float(self.basic_salary_entry.get() or 0)
            bonuses = float(self.bonuses_entry.get() or 0)
            deductions = float(self.deductions_entry.get() or 0)

            net_salary = basic_salary + bonuses - deductions
            self.net_salary_label.config(text=f"{net_salary:.2f}")
        except ValueError:
            self.net_salary_label.config(text="خطأ في الحساب")

    def add_salary(self):
        """إضافة سجل راتب جديد"""
        name = self.salary_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return

        emp_id = self.emp_dict[name]
        month = self.salary_month.get()
        year = int(self.salary_year.get())

        try:
            basic_salary = float(self.basic_salary_entry.get())
            bonuses = float(self.bonuses_entry.get())
            deductions = float(self.deductions_entry.get())
            net_salary = basic_salary + bonuses - deductions
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال قيم رقمية صحيحة للرواتب والمكافآت والخصومات.")
            return

        payment_date = datetime.now().strftime("%Y-%m-%d")

        # Check for existing salary record for the same employee, month, and year
        existing_salary = self.execute_db(
            "SELECT id FROM salaries WHERE employee_id = ? AND month = ? AND year = ?",
            (emp_id, month, year), fetch=True
        )

        if existing_salary:
            messagebox.showwarning("تنبيه", "سجل الراتب لهذا الموظف وهذا الشهر والسنة موجود بالفعل. يمكنك تعديله.")
            return

        data = (emp_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date)

        result = self.execute_db(
            "INSERT INTO salaries (employee_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم إضافة سجل الراتب بنجاح")
            self.clear_salary_entries()
            self.refresh_salaries()
            self.update_status(f"تم إضافة راتب جديد للموظف {name}")

    def load_salary_for_edit(self, event=None):
        """تحميل بيانات الراتب المحددة في الحقول للتعديل"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للتعديل")
            return

        salary_data = self.salary_tree.item(selected[0])["values"]

        # Unpack data
        salary_id, emp_name, month, year, basic_salary, bonuses, deductions, net_salary, payment_date = salary_data

        # Set combobox values
        self.salary_emp_var.set(emp_name)
        self.salary_month.set(month)
        self.salary_year.set(str(year))

        # Set entry values
        self.basic_salary_entry.config(state='normal')
        self.basic_salary_entry.delete(0, tk.END)
        self.basic_salary_entry.insert(0, str(basic_salary))
        self.basic_salary_entry.config(state='readonly')

        self.bonuses_entry.delete(0, tk.END)
        self.bonuses_entry.insert(0, str(bonuses))

        self.deductions_entry.delete(0, tk.END)
        self.deductions_entry.insert(0, str(deductions))

        self.net_salary_label.config(text=f"{net_salary:.2f}")

        self.update_status("تم تحميل سجل الراتب للتعديل. عدل البيانات واضغط 'تعديل راتب'.")

    def edit_salary(self):
        """تعديل سجل راتب موجود"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للتعديل")
            return

        salary_id = self.salary_tree.item(selected[0])["values"][0]

        name = self.salary_emp_var.get()
        if name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف")
            return

        emp_id = self.emp_dict[name]
        month = self.salary_month.get()
        year = int(self.salary_year.get())

        try:
            basic_salary = float(self.basic_salary_entry.get())
            bonuses = float(self.bonuses_entry.get())
            deductions = float(self.deductions_entry.get())
            net_salary = basic_salary + bonuses - deductions
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال قيم رقمية صحيحة للرواتب والمكافآت والخصومات.")
            return

        payment_date = datetime.now().strftime("%Y-%m-%d")  # Update payment date to current date on edit

        data = (emp_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date, salary_id)

        result = self.execute_db(
            "UPDATE salaries SET employee_id=?, month=?, year=?, basic_salary=?, bonuses=?, deductions=?, net_salary=?, payment_date=? WHERE id=?",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تحديث سجل الراتب بنجاح")
            self.clear_salary_entries()
            self.refresh_salaries()
            self.update_status(f"تم تحديث راتب الموظف {name}")

    def delete_salary(self):
        """حذف سجل راتب مع التأكيد"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للحذف")
            return

        salary_data = self.salary_tree.item(selected[0])["values"]
        salary_id = salary_data[0]
        emp_name = salary_data[1]
        month_year = f"{salary_data[2]}/{salary_data[3]}"

        if messagebox.askyesno("تأكيد الحذف",
                               f"هل تريد حذف سجل راتب الموظف '{emp_name}' لشهر {month_year}؟\nهذا الإجراء لا يمكن التراجع عنه."):
            result = self.execute_db("DELETE FROM salaries WHERE id=?", (salary_id,))

            if result is not None:
                messagebox.showinfo("تم", "تم حذف سجل الراتب")
                self.refresh_salaries()
                self.update_status(f"تم حذف سجل راتب الموظف {emp_name}")
                self.clear_salary_entries()  # Clear entries after deletion

    def clear_salary_entries(self):
        """مسح حقول الرواتب"""
        self.salary_emp_var.set('')
        self.salary_month.set(datetime.now().strftime("%m"))
        self.salary_year.set(datetime.now().year)
        self.basic_salary_entry.config(state='normal')
        self.basic_salary_entry.delete(0, tk.END)
        self.basic_salary_entry.config(state='readonly')
        self.bonuses_entry.delete(0, tk.END)
        self.bonuses_entry.insert(0, "0.0")
        self.deductions_entry.delete(0, tk.END)
        self.deductions_entry.insert(0, "0.0")
        self.net_salary_label.config(text="0.0")
        self.salary_tree.selection_remove(self.salary_tree.selection())  # Deselect any selected item

    def print_payslips(self):
        """طباعة كشوفات الرواتب"""
        messagebox.showinfo("طباعة كشوفات الرواتب", "سيتم تنفيذ وظيفة طباعة كشوفات الرواتب قريباً.")
        # هنا يمكن إضافة منطق لإنشاء PDF أو ملفات CSV لكشوفات الرواتب
        # قد يتطلب مكتبات إضافية مثل reportlab أو fpdf لإنشاء PDF

    def refresh_salaries(self):
        """تحديث جدول الرواتب"""
        for row in self.salary_tree.get_children():
            self.salary_tree.delete(row)

        query = """
        SELECT s.id, e.full_name, s.month, s.year, s.basic_salary, 
               s.bonuses, s.deductions, s.net_salary, s.payment_date
        FROM salaries s
        JOIN employees e ON s.employee_id = e.id
        ORDER BY s.year DESC, s.month DESC, e.full_name ASC
        """

        rows = self.execute_db(query, fetch=True)
        if rows:
            for row in rows:
                self.salary_tree.insert("", "end", values=row)
        self.update_status(f"تم تحديث جدول الرواتب ({len(rows) if rows else 0} سجل)")

    # ---------------- تبويب التقارير المحسن -----------------
    def create_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 التقارير")

        # إطار الأدوات للتقارير
        report_tools_frame = tk.Frame(frame, bg='white', relief='raised', bd=1)
        report_tools_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(report_tools_frame, text="اختر نوع التقرير:",
                 font=('Arial', 12, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        report_buttons = [
            ("تقرير الموظفين", self.generate_employee_report),
            ("تقرير الحضور والغياب", self.generate_attendance_report),
            ("تقرير الإجازات", self.generate_leave_report),
            ("تقرير الرواتب", self.generate_salary_report),
            ("تقرير الأداء (مستقبلي)", lambda: messagebox.showinfo("تقرير", "هذه الميزة قيد التطوير.")),
        ]

        for text, command in report_buttons:
            btn = tk.Button(report_tools_frame, text=text, bg=COLORS['primary'], fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=25, pady=8)
            btn.pack(pady=5)

    def generate_employee_report(self):
        """إنشاء تقرير شامل للموظفين"""
        self.print_employee_report()  # Reusing the existing print function for now
        # For more advanced reporting, could use pandas and matplotlib for charts or more complex data export

    def generate_attendance_report(self):
        """إنشاء تقرير شامل للحضور والغياب"""
        # A more comprehensive attendance report might involve selecting a date range
        date_range_window = tk.Toplevel(self)
        date_range_window.title("تحديد نطاق التقرير")
        date_range_window.geometry("300x200")
        date_range_window.grab_set()

        tk.Label(date_range_window, text="من تاريخ (YYYY-MM-DD):").pack(pady=5)
        from_date_entry = tk.Entry(date_range_window, justify='right')
        from_date_entry.pack(pady=2)
        from_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        tk.Label(date_range_window, text="إلى تاريخ (YYYY-MM-DD):").pack(pady=5)
        to_date_entry = tk.Entry(date_range_window, justify='right')
        to_date_entry.pack(pady=2)
        to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def generate_report_action():
            from_date = from_date_entry.get()
            to_date = to_date_entry.get()
            try:
                datetime.strptime(from_date, "%Y-%m-%d")
                datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD")
                return

            self._generate_detailed_attendance_report(from_date, to_date)
            date_range_window.destroy()

        tk.Button(date_range_window, text="إنشاء التقرير", command=generate_report_action).pack(pady=10)

    def _generate_detailed_attendance_report(self, from_date, to_date):
        """يولد تقرير حضور مفصل لنطاق تاريخ معين"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title=f"حفظ تقرير الحضور من {from_date} إلى {to_date}")
        if not file_path:
            return

        query = """
        SELECT e.full_name, a.date, a.check_in, a.check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE a.date BETWEEN ? AND ?
        ORDER BY e.full_name, a.date
        """
        report_data = self.execute_db(query, (from_date, to_date), fetch=True)

        if not report_data:
            messagebox.showinfo("تقرير الحضور", "لا توجد بيانات حضور للفترة المحددة.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة"])

                for row in report_data:
                    work_hours = self.calculate_work_hours(row[2], row[3])
                    status = self.get_attendance_status(row[2], row[3])
                    writer.writerow([row[0], row[1], row[2] or "غائب", row[3] or "لم ينصرف", work_hours, status])
            messagebox.showinfo("تم", f"تم حفظ تقرير الحضور في: {file_path}")
            self.update_status(f"تم إنشاء تقرير حضور للفترة {from_date} - {to_date}")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def generate_leave_report(self):
        """إنشاء تقرير شامل للإجازات"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="حفظ تقرير الإجازات")
        if not file_path:
            return

        query = """
        SELECT e.full_name, l.type, l.start_date, l.end_date, l.days, l.reason, l.status, l.request_date
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
        ORDER BY l.request_date DESC
        """
        report_data = self.execute_db(query, fetch=True)

        if not report_data:
            messagebox.showinfo("تقرير الإجازات", "لا توجد بيانات إجازات.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة",
                                 "تاريخ الطلب"])
                for row in report_data:
                    writer.writerow(row)
            messagebox.showinfo("تم", f"تم حفظ تقرير الإجازات في: {file_path}")
            self.update_status("تم إنشاء تقرير الإجازات بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def generate_salary_report(self):
        """إنشاء تقرير شامل للرواتب"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="حفظ تقرير الرواتب")
        if not file_path:
            return

        query = """
        SELECT e.full_name, s.month, s.year, s.basic_salary, s.bonuses, s.deductions, s.net_salary, s.payment_date
        FROM salaries s
        JOIN employees e ON s.employee_id = e.id
        ORDER BY s.year DESC, s.month DESC, e.full_name ASC
        """
        report_data = self.execute_db(query, fetch=True)

        if not report_data:
            messagebox.showinfo("تقرير الرواتب", "لا توجد بيانات رواتب.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["اسم الموظف", "الشهر", "السنة", "الراتب الأساسي", "المكافآت", "الخصومات", "صافي الراتب",
                     "تاريخ الدفع"])
                for row in report_data:
                    writer.writerow(row)
            messagebox.showinfo("تم", f"تم حفظ تقرير الرواتب في: {file_path}")
            self.update_status("تم إنشاء تقرير الرواتب بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    # ---------------- تبويب الإعدادات المحسن -----------------
    def create_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔧 الإعدادات")

        # إطار الإعدادات العامة
        general_settings_frame = tk.LabelFrame(frame, text="إعدادات عامة", bg='white', relief='raised', bd=1, padx=10,
                                               pady=10)
        general_settings_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(general_settings_frame, text="اسم قاعدة البيانات:", font=('Arial', 10, 'bold'), bg='white').grid(row=0,
                                  column=1,
                                  sticky='e',
                                  pady=5)
        self.db_name_label = tk.Label(general_settings_frame, text=DB_NAME, font=('Arial', 10), bg='white')
        self.db_name_label.grid(row=0, column=0, sticky='e', pady=5)

        tk.Button(general_settings_frame, text="فتح مجلد قاعدة البيانات", command=self.open_db_folder,
                  bg=COLORS['secondary'], fg='white', font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(general_settings_frame, text="إعادة ضبط قاعدة البيانات", command=self.reset_database,
                  bg=COLORS['danger'], fg='white', font=('Arial', 10, 'bold')).grid(row=1, column=0, columnspan=3,
                                                                                    pady=10)

        # إعدادات المستخدمين (المسؤولين)
        admin_settings_frame = tk.LabelFrame(frame, text="إدارة حسابات المسؤولين", bg='white', relief='raised', bd=1,
                                             padx=10, pady=10)
        admin_settings_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(admin_settings_frame, text="اسم المستخدم:", font=('Arial', 10), bg='white').grid(row=0, column=1,
                  sticky='e', pady=5)
        self.admin_username_entry = tk.Entry(admin_settings_frame, font=('Arial', 10), width=25,
                                             justify='right')
        self.admin_username_entry.grid(row=0, column=0, pady=5, padx=5)

        tk.Label(admin_settings_frame, text="كلمة المرور الجديدة:", font=('Arial', 10), bg='white').grid(row=1,
                         column=1,
                         sticky='e',
                         pady=5)
        self.admin_password_entry = tk.Entry(admin_settings_frame, show="*", font=('Arial', 10), width=25,
                                             justify='right')
        self.admin_password_entry.grid(row=1, column=0, pady=5, padx=5)

        tk.Label(admin_settings_frame, text="تأكيد كلمة المرور:", font=('Arial', 10), bg='white').grid(row=2, column=1,
                       sticky='e',
                       pady=5)
        self.admin_confirm_password_entry = tk.Entry(admin_settings_frame, show="*", font=('Arial', 10), width=25,
                                                     justify='right')
        self.admin_confirm_password_entry.grid(row=2, column=0, pady=5, padx=5)

        tk.Button(admin_settings_frame, text="إضافة/تعديل مسؤول", command=self.add_or_update_admin,
                  bg=COLORS['success'], fg='white', font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2,
                                                                                     pady=10)
        tk.Button(admin_settings_frame, text="حذف مسؤول", command=self.delete_admin, bg=COLORS['danger'], fg='white',
                  font=('Arial', 10, 'bold')).grid(row=3, column=2, pady=10)

        # قائمة المسؤولين (للحذف)
        tk.Label(admin_settings_frame, text="المسؤولون الحاليون:", font=('Arial', 10, 'bold'), bg='white').grid(row=4,
                                                                                                                column=0,
                                                                                                                columnspan=3,
                                                                                                                sticky='e',
                                                                                                                pady=10)
        self.admin_listbox = tk.Listbox(admin_settings_frame, height=5, font=('Arial', 10))
        self.admin_listbox.grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        self.refresh_admin_list()

    def open_db_folder(self):
        """فتح مجلد قاعدة البيانات في مستكشف الملفات"""
        db_directory = os.path.dirname(DB_NAME)
        if not db_directory:
            db_directory = os.getcwd()  # If DB_NAME is just a filename, assume current directory
        try:
            if os.path.exists(db_directory):
                os.startfile(db_directory)
            else:
                messagebox.showwarning("تنبيه", f"المجلد '{db_directory}' غير موجود.")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن فتح المجلد: {e}")

    def reset_database(self):
        """إعادة ضبط قاعدة البيانات (حذف وإعادة إنشاء الجداول)"""
        if messagebox.askyesno("تأكيد إعادة الضبط",
                               "هل أنت متأكد من رغبتك في إعادة ضبط قاعدة البيانات؟\nسيؤدي هذا إلى حذف جميع البيانات الحالية ولا يمكن التراجع عنه!"):
            try:
                conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
                c = conn.cursor()

                # Drop all tables
                c.execute("DROP TABLE IF EXISTS employees")
                c.execute("DROP TABLE IF EXISTS attendance")
                c.execute("DROP TABLE IF EXISTS leaves")
                c.execute("DROP TABLE IF EXISTS salaries")
                c.execute("DROP TABLE IF EXISTS admin")
                conn.commit()
                conn.close()

                # Re-initialize database (creates tables and default admin)
                self.init_database()
                self.create_default_admin()  # Recreate default admin after dropping tables

                messagebox.showinfo("تم", "تمت إعادة ضبط قاعدة البيانات بنجاح.")
                self.refresh_employees()
                self.refresh_attendance()
                self.refresh_leaves()
                self.refresh_salaries()
                self.refresh_employees_combobox()
                self.refresh_admin_list()
                self.update_status("تمت إعادة ضبط قاعدة البيانات")
            except Exception as e:
                messagebox.showerror("خطأ في إعادة الضبط", str(e))

    def refresh_admin_list(self):
        """تحديث قائمة المسؤولين في Listbox"""
        self.admin_listbox.delete(0, tk.END)
        admins = self.execute_db("SELECT username FROM admin", fetch=True)
        if admins:
            for admin in admins:
                self.admin_listbox.insert(tk.END, admin[0])

    def add_or_update_admin(self):
        """إضافة مسؤول جديد أو تعديل مسؤول موجود"""
        username = self.admin_username_entry.get().strip()
        password = self.admin_password_entry.get().strip()
        confirm_password = self.admin_confirm_password_entry.get().strip()

        if not username or not password or not confirm_password:
            messagebox.showerror("خطأ", "يرجى ملء جميع حقول المسؤول.")
            return

        if password != confirm_password:
            messagebox.showerror("خطأ", "كلمة المرور وتأكيدها غير متطابقين.")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()

            # Check if admin exists
            c.execute("SELECT id FROM admin WHERE username = ?", (username,))
            existing_admin = c.fetchone()

            if existing_admin:
                # Update existing admin
                c.execute("UPDATE admin SET password = ? WHERE id = ?", (password_hash, existing_admin[0]))
                messagebox.showinfo("تم", f"تم تحديث كلمة مرور المسؤول '{username}' بنجاح.")
            else:
                # Add new admin
                c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, password_hash))
                messagebox.showinfo("تم", f"تم إضافة المسؤول '{username}' بنجاح.")

            conn.commit()
            conn.close()
            self.admin_username_entry.delete(0, tk.END)
            self.admin_password_entry.delete(0, tk.END)
            self.admin_confirm_password_entry.delete(0, tk.END)
            self.refresh_admin_list()
            self.update_status(f"تم تحديث معلومات المسؤول {username}")
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "اسم المستخدم هذا موجود بالفعل.")
        except Exception as e:
            messagebox.showerror("خطأ في إدارة المسؤولين", str(e))

    def delete_admin(self):
        """حذف مسؤول محدد"""
        selected_admin = self.admin_listbox.get(tk.ACTIVE)
        if not selected_admin:
            messagebox.showwarning("تنبيه", "يرجى اختيار مسؤول لحذفه.")
            return

        if selected_admin == "admin":
            messagebox.showwarning("تنبيه", "لا يمكنك حذف المسؤول الافتراضي 'admin'.")
            return

        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من رغبتك في حذف المسؤول '{selected_admin}'؟"):
            result = self.execute_db("DELETE FROM admin WHERE username=?", (selected_admin,))
            if result is not None:
                messagebox.showinfo("تم", f"تم حذف المسؤول '{selected_admin}' بنجاح.")
                self.refresh_admin_list()
                self.update_status(f"تم حذف المسؤول {selected_admin}")


if __name__ == '__main__':
    # تهيئة قاعدة البيانات عند بدء تشغيل التطبيق
    # (هذا سيتم استدعاؤه أيضاً في HRApp.__init__ ولكن يمكن أن يكون هنا لتشغيل مستقل للتحقق)
    try:
        conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        # Create other tables if running without HRApp (e.g., for direct DB management)
        c.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                position TEXT,
                salary REAL,
                hire_date TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                employee_code TEXT UNIQUE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                check_in TEXT,
                check_out TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                days INTEGER NOT NULL,
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'معلق',
                request_date TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                year INTEGER NOT NULL,
                basic_salary REAL NOT NULL,
                bonuses REAL DEFAULT 0,
                deductions REAL DEFAULT 0,
                net_salary REAL NOT NULL,
                payment_date TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                UNIQUE(employee_id, month, year)
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating tables on startup: {e}")

    login_app = LoginWindow()
    login_app.mainloop()