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
    'primary': '#2E4057',  # لون أزرق داكن/رمادي للاستخدام الأساسي
    'secondary': '#048A81',  # لون أخضر مائل للزرقة للاستخدام الثانوي/تمييز
    'success': '#54C392',  # لون أخضر للنجاح
    'warning': '#F4B942',  # لون برتقالي للتنبيهات/التحذيرات
    'danger': '#F45B69',  # لون أحمر للأخطاء/الحذف
    'light': '#F8F9FA',  # لون فاتح للخلفيات
    'dark': '#343A40'  # لون داكن للنصوص الرئيسية
}


# تفعيل المحاذاة من اليمين لليسار
def enable_rtl(root):
    """تهيئة الواجهة للعمل من اليمين لليسار"""
    # تهيئة اتجاه العناصر في الواجهة
    root.option_add('*Label.anchor', 'e')  # محاذاة النص داخل Label إلى اليمين
    root.option_add('*Label.justify', 'right')  # محاذاة النص داخل Label إلى اليمين (للنصوص متعددة الأسطر)
    root.option_add('*Entry.justify', 'right')  # محاذاة النص داخل Entry إلى اليمين
    root.option_add('*Button.justify', 'right')  # محاذاة النص داخل Button إلى اليمين
    root.option_add('*Listbox.justify', 'right')  # محاذاة النص داخل Listbox إلى اليمين
    root.option_add('*Menu.direction', 'rtl')  # اتجاه القوائم المنسدلة من اليمين لليسار
    root.option_add('*TNotebook.Tab.textDirection', 'rtl')  # اتجاه نصوص التبويبات في ttk.Notebook
    root.option_add('*Treeview.Heading.textDirection', 'rtl')  # اتجاه عناوين الأعمدة في Treeview
    root.option_add('*Treeview.Item.textDirection', 'rtl')  # اتجاه عناصر الصفوف في Treeview


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الموارد البشرية - تسجيل الدخول")
        self.geometry("450x350")
        self.resizable(False, False)
        self.configure(bg=COLORS['light'])
        enable_rtl(self)  # تفعيل RTL للنافذة الرئيسية

        # إنشاء الواجهة
        self.create_login_ui()

        # محاولة تسجيل دخول تلقائي للمطور (إذا لم يكن موجودًا)
        self.create_default_admin()

        # تركيز على حقل اسم المستخدم
        self.username_entry.focus()

        # ربط مفتاح Enter بتسجيل الدخول
        self.bind('<Return>', lambda event: self.login())

        # تفعيل قائمة النسخ واللصق
        self.add_context_menu(self.username_entry)
        self.add_context_menu(self.password_entry)

    def create_login_ui(self):
        # إطار رئيسي يحتضن جميع عناصر تسجيل الدخول
        main_frame = tk.Frame(self, bg=COLORS['light'])
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)

        # عنوان النظام
        title_label = tk.Label(main_frame, text="نظام الموارد البشرية",
                               font=('Arial', 18, 'bold'),
                               bg=COLORS['light'], fg=COLORS['primary'])
        title_label.pack(pady=(0, 30))

        # إطار تسجيل الدخول - يحتوي على حقول الإدخال والأزرار
        login_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2, padx=20, pady=20)
        login_frame.pack(fill='both', expand=True, padx=20, pady=20)
        login_frame.columnconfigure(0, weight=1)  # جعل العمود 0 يتمدد
        login_frame.columnconfigure(1, weight=1)  # جعل العمود 1 يتمدد

        # العنوان الفرعي
        subtitle = tk.Label(login_frame, text="تسجيل الدخول",
                            font=('Arial', 14, 'bold'),
                            bg='white', fg=COLORS['primary'])
        subtitle.grid(row=0, column=0, columnspan=2, pady=(20, 30))  # يمتد على عمودين

        # حقل اسم المستخدم
        tk.Label(login_frame, text="اسم المستخدم:",
                 font=('Arial', 10), bg='white', fg=COLORS['dark']) \
            .grid(row=1, column=1, sticky='w', padx=5, pady=(0, 5))  # Label في العمود الأيمن
        self.username_entry = tk.Entry(login_frame, font=('Arial', 12),
                                       width=25, relief='solid', bd=1)
        self.username_entry.grid(row=1, column=0, padx=5, pady=(0, 15), sticky='ew')  # Entry في العمود الأيسر، يتمدد
        self.username_entry.insert(0, "admin")  # قيمة افتراضية

        # حقل كلمة المرور
        tk.Label(login_frame, text="كلمة المرور:",
                 font=('Arial', 10), bg='white', fg=COLORS['dark']) \
            .grid(row=2, column=1, sticky='w', padx=5, pady=(0, 5))  # Label في العمود الأيمن
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12),
                                       width=25, show="*", relief='solid', bd=1)
        self.password_entry.grid(row=2, column=0, padx=5, pady=(0, 20), sticky='ew')  # Entry في العمود الأيسر، يتمدد
        self.password_entry.insert(0, "admin")  # قيمة افتراضية

        # زر تسجيل الدخول
        login_btn = tk.Button(login_frame, text="دخول",
                              font=('Arial', 12, 'bold'),
                              bg=COLORS['primary'], fg='white',
                              width=20, pady=8, cursor='hand2',
                              command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky='ew')  # يمتد على عمودين ويتمدد

        # معلومات المطور
        info_text = "المطور الافتراضي: admin / admin"
        info_label = tk.Label(login_frame, text=info_text,
                              font=('Arial', 9),
                              bg='white', fg=COLORS['secondary'])
        info_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))  # يمتد على عمودين

    def create_default_admin(self):
        """إنشاء حساب مدير افتراضي إذا لم يكن موجوداً"""
        try:
            # استخدام database.safe_connect إذا كانت موجودة، وإلا الاتصال بـ sqlite3 مباشرة
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            # التأكد من وجود جدول admin
            c.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            # تشفير كلمة المرور الافتراضية
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            # التحقق مما إذا كان الحساب "admin" موجوداً
            c.execute("SELECT password FROM admin WHERE username=?", ("admin",))
            row = c.fetchone()
            if row:
                # إذا كانت كلمة المرور غير مشفرة (مثل الإصدارات القديمة)، قم بتحديثها
                if len(row[0]) != 64:  # طول تجزئة SHA256 هو 64 حرفاً
                    c.execute("UPDATE admin SET password=? WHERE username=?",
                              (password_hash, "admin"))
            else:
                # إذا لم يكن الحساب موجوداً، قم بإضافته
                c.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                          ("admin", password_hash))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطأ في إنشاء المدير الافتراضي: {e}")
            # يمكن إضافة messagebox هنا إذا أردت إظهار الخطأ للمستخدم عند بدء التشغيل

    def login(self):
        """التحقق من بيانات تسجيل الدخول"""
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()

        if not user or not pw:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        # تشفير كلمة المرور المدخلة للمقارنة
        password_hash = hashlib.sha256(pw.encode()).hexdigest()

        conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # محاولة البحث بكلمة المرور المشفرة
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, password_hash))
        row = c.fetchone()
        if not row:
            # التوافق مع قواعد البيانات القديمة حيث كانت كلمة المرور غير مشفرة
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pw))
            row = c.fetchone()
            if row:
                # إذا تم العثور على مطابقة بكلمة مرور غير مشفرة، قم بتشفيرها وتحديثها في قاعدة البيانات
                try:
                    c.execute("UPDATE admin SET password=? WHERE username=?", (password_hash, user))
                    conn.commit()
                except Exception as e:
                    print(f"خطأ في ترقية كلمة المرور: {e}")
        conn.close()

        if row:
            self.destroy()  # إغلاق نافذة تسجيل الدخول
            app = HRApp()  # فتح نافذة التطبيق الرئيسية
            app.mainloop()
        else:
            messagebox.showerror("خطأ", "بيانات الدخول غير صحيحة")
            self.password_entry.delete(0, tk.END)  # مسح حقل كلمة المرور
            self.username_entry.focus()  # إعادة التركيز على حقل اسم المستخدم

    def add_context_menu(self, widget):
        """إضافة قائمة نسخ/لصق/قص لحقول الإدخال"""
        menu = tk.Menu(widget, tearoff=0, direction='rtl')  # تحديد اتجاه القائمة كـ RTL
        menu.add_command(label="قص", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="نسخ", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="لصق", command=lambda: widget.event_generate("<<Paste>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)  # ربط الزر الأيمن للفأرة (Button-3) بفتح القائمة


class HRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الموارد البشرية المتقدم")
        self.geometry("1400x800")
        self.state('zoomed')  # تكبير النافذة إلى أقصى حجم
        self.configure(bg=COLORS['light'])
        enable_rtl(self)  # تفعيل RTL للنافذة الرئيسية

        # تهيئة قاعدة البيانات (لضمان وجود الجداول قبل استخدامها)
        self.init_database()

        # إنشاء شريط الحالة
        self.create_status_bar()

        # إنشاء شريط الأدوات
        self.create_toolbar()

        # إنشاء الواجهة الرئيسية (التبويبات)
        self.create_main_interface()

        # تحديث الوقت في شريط الحالة بشكل مستمر
        self.update_time()

        # إنشاء قاموس لربط أسماء الموظفين بمعرفاتهم (لـ Comboboxes)
        self.emp_dict = {}
        self.refresh_employees_combobox()  # تحديث هذا القاموس عند بدء التشغيل

    def init_database(self):
        """تهيئة جداول قاعدة البيانات إذا لم تكن موجودة"""
        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            # جدول الموظفين
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
            # جدول الحضور والانصراف
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
            # جدول الإجازات
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
            # جدول الرواتب
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
            # جدول المشرفين (Admin) - يجب أن يكون موجوداً من شاشة تسجيل الدخول
            c.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("خطأ في تهيئة قاعدة البيانات", str(e))

    def create_status_bar(self):
        """إنشاء شريط الحالة في أسفل النافذة"""
        self.status_frame = tk.Frame(self, bg=COLORS['primary'], height=30)
        self.status_frame.pack(side='bottom', fill='x')

        self.status_label = tk.Label(self.status_frame, text="جاهز",
                                     bg=COLORS['primary'], fg='white',
                                     font=('Arial', 10))
        self.status_label.pack(side='right', padx=10, pady=5)  # محاذاة لليمين لرسالة الحالة

        self.time_label = tk.Label(self.status_frame, text="",
                                   bg=COLORS['primary'], fg='white',
                                   font=('Arial', 10))
        self.time_label.pack(side='left', padx=10, pady=5)  # محاذاة لليسار للوقت

    def create_toolbar(self):
        """إنشاء شريط الأدوات في أعلى النافذة"""
        toolbar = tk.Frame(self, bg=COLORS['secondary'], height=50)
        toolbar.pack(side='top', fill='x')

        # تعريف أزرار شريط الأدوات (أيقونة، نص، أمر)
        tools = [
            ("🏠", "الرئيسية", self.go_home),
            ("👥", "الموظفون", lambda: self.notebook.select(0)),  # التبديل للتبويب الأول
            ("⏰", "الحضور", lambda: self.notebook.select(1)),  # التبديل للتبويب الثاني
            ("🏖️", "الإجازات", lambda: self.notebook.select(2)),  # التبديل للتبويب الثالث
            ("💰", "الرواتب", lambda: self.notebook.select(3)),  # التبديل للتبويب الرابع
            ("📊", "التقارير", lambda: self.notebook.select(4)),  # التبديل للتبويب الخامس
            ("🔧", "الإعدادات", lambda: self.notebook.select(5)),  # التبديل للتبويب السادس
            ("🚪", "خروج", self.logout)
        ]

        # إنشاء الأزرار وتعبئتها من اليمين إلى اليسار
        for icon, text, command in tools:
            btn = tk.Button(toolbar, text=f"{icon}\n{text}",  # نص وزر في سطرين
                            bg=COLORS['secondary'], fg='white',
                            font=('Arial', 9), relief='flat',  # تصميم مسطح
                            cursor='hand2', command=command,  # تغيير شكل المؤشر
                            width=8, height=2, compound=tk.TOP)  # الأيقونة في الأعلى
            btn.pack(side='right', padx=2, pady=5)  # ترتيب الأزرار من اليمين لليسار

    def create_main_interface(self):
        """إنشاء الواجهة الرئيسية التي تحتوي على ألسنة التبويب"""
        # تحسين مظهر ttk.Notebook
        style = ttk.Style()
        style.theme_use('clam')  # استخدام سمة 'clam' لمظهر أفضل
        style.configure('TNotebook', tabposition='n', background=COLORS['light'])  # وضع التبويبات في الأعلى
        style.configure('TNotebook.Tab', padding=[20, 10], background=COLORS['primary'], foreground='white',
                        font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', COLORS['secondary'])],
                  foreground=[('selected', 'white')])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # إنشاء كل تبويب على حدة
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_leave_tab()
        self.create_salary_tab()
        self.create_report_tab()
        self.create_settings_tab()

    def update_time(self):
        """تحديث الوقت والتاريخ في شريط الحالة كل ثانية"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)  # استدعاء هذه الدالة بعد 1000 مللي ثانية (ثانية واحدة)

    def update_status(self, message):
        """تحديث رسالة الحالة في شريط الحالة لفترة زمنية محددة"""
        self.status_label.config(text=message)
        self.after(3000, lambda: self.status_label.config(text="جاهز"))  # إعادة الحالة إلى "جاهز" بعد 3 ثوانٍ

    def go_home(self):
        """العودة إلى تبويب الموظفين (الصفحة الرئيسية الافتراضية)"""
        self.notebook.select(0)  # تحديد التبويب الأول (الموظفون)

    def logout(self):
        """تسجيل الخروج من التطبيق والعودة إلى شاشة تسجيل الدخول"""
        if messagebox.askyesno("تأكيد", "هل تريد تسجيل الخروج؟"):
            self.destroy()  # إغلاق نافذة التطبيق الرئيسية
            LoginWindow().mainloop()  # فتح نافذة تسجيل الدخول مرة أخرى

    def execute_db(self, query, params=(), fetch=False):
        """
        تنفيذ استعلام قاعدة البيانات مع معالجة الأخطاء.
        :param query: استعلام SQL المراد تنفيذه.
        :param params: معاملات الاستعلام (tuple).
        :param fetch: True لجلب البيانات، False للتنفيذ فقط.
        :return: البيانات إذا كان fetch=True، وإلا None.
        """
        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(query, params)
            data = c.fetchall() if fetch else None
            conn.commit()
            conn.close()
            return data
        except Exception as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ: {e}\nالاستعلام: {query}")
            return None

    def validate_email(self, email):
        """التحقق من صحة تنسيق البريد الإلكتروني باستخدام التعبيرات النمطية"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """التحقق من صحة تنسيق رقم الهاتف (يسمح بالأرقام، +, -, مسافات، أقواس)"""
        pattern = r'^[0-9+\-\s()]{7,15}$'  # تم تعديل الحد الأدنى ليكون 7 أرقام ليكون أكثر مرونة
        return re.match(pattern, phone) is not None

    def refresh_employees_combobox(self):
        """تحديث قائمة الموظفين في مربعات الاختيار (Combobox) المستخدمة في تبويبات أخرى"""
        employees = self.execute_db("SELECT id, full_name FROM employees ORDER BY full_name ASC", fetch=True)
        self.emp_dict = {name: eid for eid, name in (employees or [])}  # إنشاء قاموس (الاسم: المعرف)

        employee_names = sorted(list(self.emp_dict.keys()))  # الحصول على الأسماء مرتبة أبجدياً

        # تحديث مربعات الاختيار في التبويبات الأخرى إن وجدت
        if hasattr(self, 'atten_emp'):
            self.atten_emp['values'] = employee_names
        if hasattr(self, 'leave_emp'):
            self.leave_emp['values'] = employee_names
        if hasattr(self, 'salary_emp'):
            self.salary_emp['values'] = employee_names

    # ---------------- تبويب الموظفون المحسن -----------------
    def create_employee_tab(self):
        """إنشاء تبويب إدارة الموظفين"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👥 الموظفون")  # إضافة التبويب إلى Notebook

        # إطار البحث
        search_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=5)
        search_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(search_frame, text="البحث:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).pack(side='right', padx=10, pady=5)
        self.search_var = tk.StringVar()  # متغير لربط حقل البحث
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=('Arial', 10), width=30, relief='solid', bd=1)
        self.search_entry.pack(side='right', padx=5, pady=5)
        self.search_var.trace('w', self.search_employees)  # ربط تغيير النص بدالة البحث

        # إطار الإدخال الرئيسي للحقول
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        # تقسيم الحقول إلى عمودين داخل input_frame
        left_frame = tk.Frame(input_frame, bg='white')
        left_frame.pack(side='right', fill='both', expand=True, padx=10,
                        pady=10)  # وضع الإطار الأيسر (من منظور الكود) على اليمين ليتناسب مع RTL

        right_frame = tk.Frame(input_frame, bg='white')
        right_frame.pack(side='left', fill='both', expand=True, padx=10,
                         pady=10)  # وضع الإطار الأيمن (من منظور الكود) على اليسار

        # تعريف الحقول الأساسية
        labels_right_col = [  # الحقول التي ستكون في العمود الأيمن (من منظور المستخدم)
            ("الاسم الكامل*", "full_name"),
            ("الوظيفة*", "position"),
            ("الراتب الأساسي*", "salary"),
            ("تاريخ التعيين* (YYYY-MM-DD)", "hire_date")
        ]

        labels_left_col = [  # الحقول التي ستكون في العمود الأيسر (من منظور المستخدم)
            ("البريد الإلكتروني", "email"),
            ("رقم الهاتف", "phone"),
            ("العنوان", "address"),
            ("الرقم الوظيفي", "employee_code")
        ]

        self.emp_entries = {}  # قاموس لتخزين حقول الإدخال للوصول إليها بسهولة

        # إنشاء حقول الإدخال في العمود الأيمن
        for i, (label_text, key) in enumerate(labels_right_col):
            tk.Label(right_frame, text=label_text, font=('Arial', 10, 'bold'),
                     bg='white', fg=COLORS['dark']).grid(row=i, column=1, sticky="w", padx=5,
                                                         pady=5)  # Label على اليمين
            entry = tk.Entry(right_frame, font=('Arial', 10), width=30, relief='solid', bd=1)
            entry.grid(row=i, column=0, pady=5, padx=5, sticky="ew")  # Entry على اليسار
            self.emp_entries[key] = entry

        # إنشاء حقول الإدخال في العمود الأيسر
        for i, (label_text, key) in enumerate(labels_left_col):
            tk.Label(left_frame, text=label_text, font=('Arial', 10, 'bold'),
                     bg='white', fg=COLORS['dark']).grid(row=i, column=1, sticky="w", padx=5,
                                                         pady=5)  # Label على اليمين
            entry = tk.Entry(left_frame, font=('Arial', 10), width=30, relief='solid', bd=1)
            entry.grid(row=i, column=0, pady=5, padx=5, sticky="ew")  # Entry على اليسار
            self.emp_entries[key] = entry

        # تكوين تمدد الأعمدة في الأطر الفرعية
        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # إطار أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white', padx=10, pady=5)
        button_frame.pack(fill='x', pady=10)

        # تعريف الأزرار
        buttons = [
            ("➕ إضافة موظف", COLORS['success'], self.add_employee),
            ("✏️ تعديل", COLORS['warning'], self.edit_employee_load),  # أمر لتحميل البيانات للتعديل
            ("🗑️ حذف", COLORS['danger'], self.delete_employee),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_employees),
            ("📄 طباعة تقرير", COLORS['primary'], self.print_employee_report),
            ("🗑️ مسح الحقول", COLORS['dark'], self.clear_employee_entries)  # زر جديد لمسح الحقول
        ]

        self.employee_action_buttons = {}  # لتخزين الأزرار لتغيير الأمر والنص
        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=15, pady=5)
            btn.pack(side='right', padx=5)  # ترتيب الأزرار من اليمين لليسار
            self.employee_action_buttons[text] = btn  # تخزين الزر باستخدام نصه الأصلي

        # جدول الموظفين المحسن
        table_frame = tk.Frame(frame, padx=10, pady=5)
        table_frame.pack(fill='both', expand=True)

        # أعمدة الجدول
        columns = ("id", "الاسم الكامل", "الوظيفة", "الراتب", "تاريخ التعيين",
                   "البريد الإلكتروني", "الهاتف", "العنوان", "الرقم الوظيفي")

        self.emp_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة والعناوين
        column_widths = [0, 150, 120, 100, 110, 180, 110, 200, 100]
        # ضبط المحاذاة لكل عمود
        column_alignments = ['center', 'right', 'right', 'center', 'center', 'right', 'right', 'right', 'center']

        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=width, anchor=column_alignments[i])

        # إخفاء عمود المعرف
        self.emp_tree.column("id", width=0, stretch=False)
        self.emp_tree.heading("id", text="")

        # أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.emp_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.emp_tree.xview)
        self.emp_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تخطيط الجدول وأشرطة التمرير باستخدام grid
        self.emp_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # جعل الجدول يتمدد مع النافذة
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # ربط النقر المزدوج بالتعديل
        self.emp_tree.bind('<Double-1>', lambda e: self.edit_employee_load())

        self.refresh_employees()  # تحميل بيانات الموظفين عند إنشاء التبويب

    def search_employees(self, *args):
        """البحث في الموظفين بناءً على مصطلح البحث المدخل"""
        search_term = self.search_var.get().lower()
        for item in self.emp_tree.get_children():  # مسح جميع الصفوف الحالية
            self.emp_tree.delete(item)

        # استعلام SQL للبحث في عدة أعمدة
        query = """SELECT * FROM employees WHERE
                  LOWER(full_name) LIKE ? OR
                  LOWER(position) LIKE ? OR
                  LOWER(email) LIKE ? OR
                  LOWER(phone) LIKE ? OR
                  LOWER(employee_code) LIKE ?
                  ORDER BY full_name ASC"""
        params = [f"%{search_term}%"] * 5  # تكرار مصطلح البحث لكل عمود

        rows = self.execute_db(query, params, fetch=True)
        if rows:
            for row in rows:
                self.emp_tree.insert("", "end", values=row)  # إدراج الصفوف المطابقة

    def add_employee(self):
        """إضافة موظف جديد مع التحقق من البيانات المدخلة"""
        # التحقق من الحقول المطلوبة
        required_fields = ["full_name", "position", "salary", "hire_date"]
        for field in required_fields:
            if not self.emp_entries[field].get().strip():
                messagebox.showerror("خطأ",
                                     f"حقل '{self.emp_tree.heading(field)['text']}' مطلوب.")  # استخدام نص العنوان
                self.emp_entries[field].focus()
                return

        # التحقق من صحة البريد الإلكتروني
        email = self.emp_entries["email"].get().strip()
        if email and not self.validate_email(email):
            messagebox.showerror("خطأ", "تنسيق البريد الإلكتروني غير صحيح.")
            self.emp_entries["email"].focus()
            return

        # التحقق من صحة رقم الهاتف
        phone = self.emp_entries["phone"].get().strip()
        if phone and not self.validate_phone(phone):
            messagebox.showerror("خطأ", "تنسيق رقم الهاتف غير صحيح. يجب أن يحتوي على أرقام فقط (مع + أو - أو أقواس).")
            self.emp_entries["phone"].focus()
            return

        # التحقق من صحة الراتب
        try:
            salary = float(self.emp_entries["salary"].get().strip())
            if salary < 0:
                raise ValueError("الراتب لا يمكن أن يكون سالباً.")
        except ValueError:
            messagebox.showerror("خطأ", "الراتب يجب أن يكون رقماً موجباً صالحاً.")
            self.emp_entries["salary"].focus()
            return

        # التحقق من تنسيق تاريخ التعيين
        try:
            hire_date = self.emp_entries["hire_date"].get().strip()
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "تاريخ التعيين يجب أن يكون بالشكل YYYY-MM-DD.")
            self.emp_entries["hire_date"].focus()
            return

        # جمع القيم من حقول الإدخال بالترتيب الصحيح لـ SQL
        values = [self.emp_entries[key].get().strip() for key in
                  ["full_name", "position", "salary", "hire_date", "email", "phone", "address", "employee_code"]]

        result = self.execute_db(
            "INSERT INTO employees (full_name, position, salary, hire_date, email, phone, address, employee_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )

        if result is not None:  # إذا لم يكن هناك خطأ في التنفيذ
            messagebox.showinfo("تم", "تمت إضافة الموظف بنجاح.")
            self.clear_employee_entries()  # مسح الحقول بعد الإضافة
            self.refresh_employees()  # تحديث جدول الموظفين
            self.refresh_employees_combobox()  # تحديث قوائم الموظفين في التبويبات الأخرى
            self.update_status("تم إضافة موظف جديد.")

    def edit_employee_load(self):
        """تحميل بيانات الموظف المحدد في حقول الإدخال للتعديل"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للتعديل.")
            return

        emp_data = self.emp_tree.item(selected[0])["values"]  # الحصول على بيانات الصف المحدد

        # ملء الحقول ببيانات الموظف
        # ملاحظة: emp_data[0] هو الـ id، ثم تأتي باقي البيانات بالترتيب
        fields_order = ["id", "full_name", "position", "salary", "hire_date", "email", "phone", "address",
                        "employee_code"]
        for i, field_key in enumerate(fields_order):
            if field_key == "id":
                continue  # تخطي الـ ID لأنه لا يوجد حقل إدخال له
            self.emp_entries[field_key].delete(0, tk.END)  # مسح أي نص سابق
            self.emp_entries[field_key].insert(0, emp_data[i])  # إدراج البيانات

        # تغيير نص زر "إضافة موظف" إلى "تحديث الموظف" وتغيير وظيفته
        self.employee_action_buttons["➕ إضافة موظف"].config(text="✔️ تحديث الموظف", command=self.update_employee,
                                                            bg=COLORS['warning'])  # تغيير اللون لتمييزه
        self.update_status("تم تحميل بيانات الموظف للتعديل. اضغط 'تحديث الموظف' بعد التعديل.")

    def update_employee(self):
        """تحديث بيانات الموظف المحدد"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للتحديث.")
            return

        emp_id = self.emp_tree.item(selected[0])["values"][0]  # الحصول على ID الموظف من الصف المحدد

        # إعادة التحقق من البيانات المدخلة قبل التحديث (نفس منطق add_employee)
        required_fields = ["full_name", "position", "salary", "hire_date"]
        for field in required_fields:
            if not self.emp_entries[field].get().strip():
                messagebox.showerror("خطأ", f"حقل '{self.emp_tree.heading(field)['text']}' مطلوب.")
                self.emp_entries[field].focus()
                return

        email = self.emp_entries["email"].get().strip()
        if email and not self.validate_email(email):
            messagebox.showerror("خطأ", "تنسيق البريد الإلكتروني غير صحيح.")
            self.emp_entries["email"].focus()
            return

        phone = self.emp_entries["phone"].get().strip()
        if phone and not self.validate_phone(phone):
            messagebox.showerror("خطأ", "تنسيق رقم الهاتف غير صحيح. يجب أن يحتوي على أرقام فقط (مع + أو - أو أقواس).")
            self.emp_entries["phone"].focus()
            return

        try:
            salary = float(self.emp_entries["salary"].get().strip())
            if salary < 0:
                raise ValueError("الراتب لا يمكن أن يكون سالباً.")
        except ValueError:
            messagebox.showerror("خطأ", "الراتب يجب أن يكون رقماً موجباً صالحاً.")
            self.emp_entries["salary"].focus()
            return

        try:
            hire_date = self.emp_entries["hire_date"].get().strip()
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "تاريخ التعيين يجب أن يكون بالشكل YYYY-MM-DD.")
            self.emp_entries["hire_date"].focus()
            return

        # جمع القيم المحدثة
        values = [self.emp_entries[key].get().strip() for key in
                  ["full_name", "position", "salary", "hire_date", "email", "phone", "address", "employee_code"]]
        values.append(emp_id)  # إضافة الـ ID كآخر معلمة للاستعلام

        result = self.execute_db(
            "UPDATE employees SET full_name=?, position=?, salary=?, hire_date=?, email=?, phone=?, address=?, employee_code=? WHERE id=?",
            values,
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تحديث بيانات الموظف بنجاح.")
            self.clear_employee_entries()  # مسح الحقول
            self.refresh_employees()  # تحديث الجدول
            self.refresh_employees_combobox()  # تحديث قوائم الموظفين
            self.update_status(f"تم تحديث بيانات الموظف ID: {emp_id}.")
            # إعادة الزر إلى حالته الأصلية (إضافة موظف)
            self.employee_action_buttons["➕ إضافة موظف"].config(text="➕ إضافة موظف", command=self.add_employee,
                                                                bg=COLORS['success'])

    def delete_employee(self):
        """حذف موظف مع طلب التأكيد"""
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار موظف للحذف.")
            return

        emp_data = self.emp_tree.item(selected[0])["values"]
        emp_name = emp_data[1]  # اسم الموظف للعرض في رسالة التأكيد

        if messagebox.askyesno("تأكيد الحذف",
                               f"هل أنت متأكد من رغبتك في حذف الموظف '{emp_name}'؟\nهذا الإجراء لا يمكن التراجع عنه."):
            emp_id = emp_data[0]  # معرف الموظف
            result = self.execute_db("DELETE FROM employees WHERE id=?", (emp_id,))

            if result is not None:
                messagebox.showinfo("تم", "تم حذف الموظف بنجاح.")
                self.refresh_employees()  # تحديث الجدول
                self.refresh_employees_combobox()  # تحديث قوائم الموظفين
                self.update_status(f"تم حذف الموظف {emp_name}.")
                self.clear_employee_entries()  # مسح الحقول بعد الحذف

    def clear_employee_entries(self):
        """مسح جميع حقول إدخال بيانات الموظف وإعادة زر التحديث إلى إضافة"""
        for entry in self.emp_entries.values():
            entry.delete(0, tk.END)  # مسح محتوى كل حقل
        # إعادة زر "تحديث الموظف" إلى "إضافة موظف"
        self.employee_action_buttons["➕ إضافة موظف"].config(text="➕ إضافة موظف", command=self.add_employee,
                                                            bg=COLORS['success'])
        self.emp_tree.selection_remove(self.emp_tree.selection())  # إلغاء تحديد أي عنصر محدد في الجدول
        self.update_status("تم مسح حقول الموظف.")

    def print_employee_report(self):
        """طباعة تقرير الموظفين إلى ملف CSV"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")],
                                                 title="حفظ تقرير الموظفين")
        if not file_path:
            return  # إذا ألغى المستخدم الحفظ

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:  # استخدام utf-8-sig لدعم Excel بشكل أفضل
                writer = csv.writer(f)
                # كتابة عناوين الأعمدة
                headers = ["المعرف", "الاسم الكامل", "الوظيفة", "الراتب", "تاريخ التعيين",
                           "البريد الإلكتروني", "الهاتف", "العنوان", "الرقم الوظيفي"]
                writer.writerow(headers)

                # جلب جميع بيانات الموظفين وكتابتها في الملف
                rows = self.execute_db("SELECT * FROM employees ORDER BY full_name ASC", fetch=True)
                if rows:
                    writer.writerows(rows)  # كتابة جميع الصفوف مرة واحدة
            messagebox.showinfo("تم", f"تم حفظ تقرير الموظفين في: {file_path}")
            self.update_status("تم إنشاء تقرير الموظفين بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ في الطباعة", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def refresh_employees(self):
        """تحديث وعرض قائمة الموظفين في جدول Treeview"""
        for row in self.emp_tree.get_children():  # مسح جميع الصفوف الحالية
            self.emp_tree.delete(row)

        rows = self.execute_db("SELECT * FROM employees ORDER BY full_name ASC", fetch=True)
        if rows:
            for row in rows:
                self.emp_tree.insert("", "end", values=row)  # إدراج كل صف

        self.update_status(f"تم تحديث قائمة الموظفين ({len(rows) if rows else 0} موظف).")

    # ---------------- تبويب الحضور والانصراف المحسن -----------------
    def create_attendance_tab(self):
        """إنشاء تبويب إدارة الحضور والانصراف"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⏰ الحضور والانصراف")

        # إطار الإدخال الرئيسي
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان القسم
        tk.Label(input_frame, text="تسجيل الحضور والانصراف",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # إطار للحقول لترتيبها
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # الموظف (Combobox)
        tk.Label(fields_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.atten_emp_var = tk.StringVar()
        self.atten_emp = ttk.Combobox(fields_frame, textvariable=self.atten_emp_var,
                                      state="readonly", width=30, font=('Arial', 10),
                                      justify='right')  # محاذاة النص لليمين
        self.atten_emp.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        # التاريخ
        tk.Label(fields_frame, text="التاريخ (YYYY-MM-DD):", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.attendance_date = tk.Entry(fields_frame, font=('Arial', 10), width=30, relief='solid', bd=1)
        self.attendance_date.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))  # تاريخ اليوم افتراضياً

        # وقت الحضور
        tk.Label(fields_frame, text="وقت الحضور (HH:MM):", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.check_in_entry = tk.Entry(fields_frame, font=('Arial', 10), width=30, relief='solid', bd=1)
        self.check_in_entry.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        # وقت الانصراف
        tk.Label(fields_frame, text="وقت الانصراف (HH:MM):", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.check_out_entry = tk.Entry(fields_frame, font=('Arial', 10), width=30, relief='solid', bd=1)
        self.check_out_entry.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

        fields_frame.columnconfigure(0, weight=1)  # لجعل حقول الإدخال تتمدد

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white', padx=10, pady=5)
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("⏰ تسجيل حضور", COLORS['success'], self.add_check_in),
            ("🏃 تسجيل انصراف", COLORS['warning'], self.add_check_out),
            ("📝 تسجيل كامل", COLORS['primary'], self.add_attendance),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_attendance),
            ("📊 تقرير يومي", COLORS['primary'], self.daily_attendance_report),
            ("🗑️ مسح الحقول", COLORS['dark'], self.clear_attendance_entries)  # زر جديد
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=15, pady=5)
            btn.pack(side='right', padx=5)

        # إطار الإحصائيات اليومية
        stats_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=10)
        stats_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(stats_frame, text="إحصائيات الحضور لهذا اليوم",
                 font=('Arial', 12, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=5)

        self.stats_labels = {}  # لتخزين Labels الإحصائيات
        stats_info = tk.Frame(stats_frame, bg='white')
        stats_info.pack(fill='x', padx=20, pady=10)

        stats_items = [
            ("الحاضرون:", "present"),
            ("المتأخرون:", "late"),
            ("الغائبون:", "absent"),
            ("إجمالي ساعات العمل:", "work_hours")
        ]

        # إنشاء Labels للإحصائيات وتعبئتها من اليمين لليسار
        for i, (text, key) in enumerate(stats_items):
            # كل زوج (نص، قيمة) يأخذ عمودين
            tk.Label(stats_info, text=text, font=('Arial', 10, 'bold'),
                     bg='white', fg=COLORS['dark']).grid(row=0, column=(len(stats_items) - 1 - i) * 2 + 1, padx=10,
                                                         pady=5, sticky='w')  # Label على اليمين
            self.stats_labels[key] = tk.Label(stats_info, text="0",
                                              font=('Arial', 10, 'bold'), bg='white',
                                              fg=COLORS['secondary'])
            self.stats_labels[key].grid(row=0, column=(len(stats_items) - 1 - i) * 2, padx=5, pady=5,
                                        sticky='e')  # القيمة على اليسار

        # جدول الحضور
        table_frame = tk.Frame(frame, padx=10, pady=5)
        table_frame.pack(fill='both', expand=True)

        columns = ("id", "الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة")
        self.att_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 150, 100, 100, 100, 100, 100]
        column_alignments = ['center', 'right', 'center', 'center', 'center', 'center', 'center']

        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.att_tree.heading(col, text=col)
            self.att_tree.column(col, width=width, anchor=column_alignments[i])

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

        self.refresh_attendance()  # تحميل بيانات الحضور عند إنشاء التبويب
        self.update_attendance_stats()  # تحديث الإحصائيات

    def add_check_in(self):
        """تسجيل وقت حضور الموظف"""
        name = self.atten_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
            return

        emp_id = self.emp_dict[name]
        date_str = self.attendance_date.get().strip()
        check_in_time = self.check_in_entry.get().strip() or datetime.now().strftime("%H:%M")

        # التحقق من تنسيق التاريخ والوقت
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            datetime.strptime(check_in_time, "%H:%M")
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD ووقت الحضور HH:MM.")
            return

        # التحقق مما إذا كان هناك تسجيل حضور لهذا الموظف في نفس اليوم
        existing = self.execute_db(
            "SELECT id FROM attendance WHERE employee_id=? AND date=?",
            (emp_id, date_str), fetch=True
        )

        if existing:
            messagebox.showwarning("تنبيه", "الموظف مسجل حضوره لهذا اليوم بالفعل. يرجى تعديل التسجيل الموجود.")
            return

        result = self.execute_db(
            "INSERT INTO attendance (employee_id, date, check_in) VALUES (?, ?, ?)",
            (emp_id, date_str, check_in_time)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الحضور بنجاح.")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()
            self.update_status(f"تم تسجيل حضور {name}.")

    def add_check_out(self):
        """تسجيل وقت انصراف الموظف"""
        name = self.atten_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
            return

        emp_id = self.emp_dict[name]
        date_str = self.attendance_date.get().strip()
        check_out_time = self.check_out_entry.get().strip() or datetime.now().strftime("%H:%M")

        # التحقق من تنسيق التاريخ والوقت
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            datetime.strptime(check_out_time, "%H:%M")
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD ووقت الانصراف HH:MM.")
            return

        # البحث عن تسجيل حضور موجود لهذا الموظف في نفس اليوم
        existing_record = self.execute_db(
            "SELECT id, check_in, check_out FROM attendance WHERE employee_id=? AND date=?",
            (emp_id, date_str), fetch=True
        )

        if not existing_record:
            messagebox.showwarning("تنبيه", "لم يتم تسجيل حضور الموظف لهذا اليوم بعد. يرجى تسجيل الحضور أولاً.")
            return

        record_id = existing_record[0][0]
        existing_check_in = existing_record[0][1]
        existing_check_out = existing_record[0][2]

        if not existing_check_in:
            messagebox.showwarning("تنبيه",
                                   "لم يتم تسجيل وقت دخول الموظف لهذا اليوم. يرجى تسجيل وقت الدخول أولاً أو استخدام 'تسجيل كامل'.")
            return

        if existing_check_out:
            messagebox.showwarning("تنبيه", "تم تسجيل وقت انصراف الموظف لهذا اليوم بالفعل.")
            return

        # التأكد أن وقت الانصراف بعد وقت الحضور
        try:
            in_dt = datetime.strptime(existing_check_in, "%H:%M")
            out_dt = datetime.strptime(check_out_time, "%H:%M")
            if out_dt < in_dt:
                messagebox.showwarning("تنبيه", "وقت الانصراف لا يمكن أن يكون قبل وقت الحضور.")
                return
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق وقت الحضور أو الانصراف غير صحيح.")
            return

        result = self.execute_db(
            "UPDATE attendance SET check_out=? WHERE id=?",
            (check_out_time, record_id)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الانصراف بنجاح.")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()
            self.update_status(f"تم تسجيل انصراف {name}.")

    def add_attendance(self):
        """تسجيل الحضور والانصراف معاً في سجل جديد"""
        name = self.atten_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
            return

        emp_id = self.emp_dict[name]
        date_str = self.attendance_date.get().strip()
        check_in_time = self.check_in_entry.get().strip()
        check_out_time = self.check_out_entry.get().strip()

        if not check_in_time or not check_out_time:
            messagebox.showerror("خطأ", "يجب إدخال وقتي الحضور والانصراف للتسجيل الكامل.")
            return

        # التحقق من تنسيق التاريخ والوقت
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            in_dt = datetime.strptime(check_in_time, "%H:%M")
            out_dt = datetime.strptime(check_out_time, "%H:%M")
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD وأوقات الحضور/الانصراف HH:MM.")
            return

        # التحقق من أن وقت الانصراف ليس قبل وقت الحضور
        if out_dt < in_dt:
            messagebox.showerror("خطأ", "وقت الانصراف لا يمكن أن يكون قبل وقت الحضور.")
            return

        # التحقق من وجود تسجيل سابق لنفس اليوم
        existing = self.execute_db(
            "SELECT id FROM attendance WHERE employee_id=? AND date=?",
            (emp_id, date_str), fetch=True
        )

        if existing:
            messagebox.showwarning("تنبيه",
                                   "الموظف لديه تسجيل حضور/انصراف لهذا اليوم بالفعل. يرجى التحديث يدوياً أو حذف السجل الحالي.")
            return

        result = self.execute_db(
            "INSERT INTO attendance (employee_id, date, check_in, check_out) VALUES (?, ?, ?, ?)",
            (emp_id, date_str, check_in_time, check_out_time)
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تسجيل الحضور والانصراف بنجاح.")
            self.refresh_attendance()
            self.update_attendance_stats()
            self.clear_attendance_entries()
            self.update_status(f"تم تسجيل حضور وانصراف {name}.")

    def calculate_work_hours(self, check_in, check_out):
        """
        حساب ساعات العمل بين وقتي الحضور والانصراف.
        :param check_in: وقت الحضور (سلسلة نصية بتنسيق HH:MM).
        :param check_out: وقت الانصراف (سلسلة نصية بتنسيق HH:MM).
        :return: ساعات العمل كسلسلة نصية (مثال: "8.50 ساعة") أو "غير محدد" / "خطأ".
        """
        if not check_in or not check_out:
            return "غير محدد"

        try:
            in_time = datetime.strptime(check_in, "%H:%M")
            out_time = datetime.strptime(check_out, "%H:%M")

            # إذا كان وقت الانصراف أقل من وقت الحضور (يعني عبر منتصف الليل)
            if out_time < in_time:
                out_time += timedelta(days=1)  # إضافة يوم واحد لوقت الانصراف

            work_duration = out_time - in_time
            hours = work_duration.total_seconds() / 3600  # تحويل الثواني إلى ساعات
            return f"{hours:.2f} ساعة"
        except ValueError:  # إذا كان تنسيق الوقت غير صحيح
            return "خطأ في الحساب"
        except Exception as e:
            return f"خطأ: {e}"

    def get_attendance_status(self, check_in, check_out):
        """
        تحديد حالة حضور الموظف (حاضر، غائب، متأخر، لم ينصرف).
        :param check_in: وقت الحضور (سلسلة نصية بتنسيق HH:MM).
        :param check_out: وقت الانصراف (سلسلة نصية بتنسيق HH:MM).
        :return: حالة الحضور كسلسلة نصية.
        """
        if not check_in:
            return "غائب"  # إذا لم يسجل حضوراً

        try:
            in_time = datetime.strptime(check_in, "%H:%M")
            # يمكن جعل هذا الوقت (08:00) إعداداً قابلاً للتكوين
            work_start = datetime.strptime("08:00", "%H:%M")

            if in_time > work_start:
                return "متأخر"  # إذا سجل حضوره بعد وقت البدء المحدد
            elif check_out:
                return "حاضر"  # إذا سجل حضوراً وانصرافاً
            else:
                return "لم ينصرف"  # إذا سجل حضوراً فقط
        except ValueError:
            return "خطأ في التنسيق"
        except Exception as e:
            return "خطأ"

    def update_attendance_stats(self):
        """تحديث إحصائيات الحضور اليومية وعرضها في الواجهة"""
        today = datetime.now().strftime("%Y-%m-%d")

        # جلب جميع سجلات الحضور لهذا اليوم
        stats_raw = self.execute_db(
            "SELECT check_in, check_out FROM attendance WHERE date=?",
            (today,), fetch=True
        )

        present_count = 0
        late_count = 0
        total_work_hours = 0.0

        if stats_raw:
            for record in stats_raw:
                check_in = record[0]
                check_out = record[1]

                if check_in:
                    present_count += 1
                    try:
                        in_time = datetime.strptime(check_in, "%H:%M")
                        work_start = datetime.strptime("08:00", "%H:%M")
                        if in_time > work_start:
                            late_count += 1
                    except ValueError:
                        pass  # تجاهل الأخطاء في تنسيق الوقت للحساب

                if check_in and check_out:
                    try:
                        in_time = datetime.strptime(check_in, "%H:%M")
                        out_time = datetime.strptime(check_out, "%H:%M")
                        if out_time < in_time:  # معالجة حالات عبور منتصف الليل
                            out_time += timedelta(days=1)
                        total_work_hours += (out_time - in_time).total_seconds() / 3600
                    except ValueError:
                        pass  # تجاهل الأخطاء في تنسيق الوقت للحساب

        # حساب إجمالي الموظفين لمعرفة الغائبين
        total_employees_result = self.execute_db("SELECT COUNT(id) FROM employees", fetch=True)
        total_employees = total_employees_result[0][0] if total_employees_result else 0
        absent_count = total_employees - present_count

        # تحديث Labels في الواجهة
        self.stats_labels['present'].config(text=str(present_count))
        self.stats_labels['late'].config(text=str(late_count))
        self.stats_labels['absent'].config(text=str(absent_count))
        self.stats_labels['work_hours'].config(text=f"{total_work_hours:.1f} ساعة")

    def clear_attendance_entries(self):
        """مسح حقول إدخال الحضور والانصراف"""
        self.atten_emp_var.set('')  # مسح اختيار Combobox
        self.check_in_entry.delete(0, tk.END)
        self.check_out_entry.delete(0, tk.END)
        self.attendance_date.delete(0, tk.END)
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))  # إعادة تعيين تاريخ اليوم
        self.att_tree.selection_remove(self.att_tree.selection())
        self.update_status("تم مسح حقول الحضور والانصراف.")

    def daily_attendance_report(self):
        """إنشاء تقرير CSV للحضور اليومي"""
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
            messagebox.showinfo("تقرير الحضور اليومي", f"لا توجد بيانات حضور لليوم {today}.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")],
                                                 title=f"حفظ تقرير حضور {today}")
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة"])

                for row in report_data:
                    # حساب ساعات العمل والحالة لكل سجل
                    work_hours = self.calculate_work_hours(row[2], row[3])
                    status = self.get_attendance_status(row[2], row[3])
                    # كتابة الصف مع القيم المحسوبة
                    writer.writerow([row[0], row[1], row[2] or "غائب", row[3] or "لم ينصرف", work_hours, status])
            messagebox.showinfo("تم", f"تم حفظ تقرير الحضور اليومي في: {file_path}")
            self.update_status(f"تم إنشاء تقرير الحضور لليوم {today}.")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def refresh_attendance(self):
        """تحديث جدول عرض سجلات الحضور والانصراف"""
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)

        # استعلام لجلب سجلات الحضور مع أسماء الموظفين المرتبطة
        query = """
        SELECT a.id, e.full_name, a.date, a.check_in, a.check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        ORDER BY a.date DESC, a.check_in DESC
        """

        rows = self.execute_db(query, fetch=True)
        if rows:
            for row in rows:
                # حساب ساعات العمل والحالة لكل سجل للعرض
                work_hours = self.calculate_work_hours(row[3], row[4])
                status = self.get_attendance_status(row[3], row[4])

                display_row = (
                    row[0], row[1], row[2], row[3] or "لم يحضر",  # عرض "لم يحضر" إذا لم يكن هناك وقت دخول
                    row[4] or "لم ينصرف", work_hours, status  # عرض "لم ينصرف" إذا لم يكن هناك وقت خروج
                )
                self.att_tree.insert("", "end", values=display_row)
        self.update_attendance_stats()  # تحديث الإحصائيات بعد تحديث الجدول
        self.update_status(f"تم تحديث جدول الحضور ({len(rows) if rows else 0} سجل).")

    # ---------------- تبويب الإجازات المحسن -----------------
    def create_leave_tab(self):
        """إنشاء تبويب إدارة الإجازات"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏖️ الإجازات")

        # إطار الإدخال الرئيسي
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان القسم
        tk.Label(input_frame, text="إدارة الإجازات",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # إطار للحقول لترتيبها
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # تقسيم الحقول إلى عمودين
        left_frame = tk.Frame(fields_frame, bg='white')
        left_frame.pack(side='right', fill='both', expand=True,
                        padx=10)  # وضع الإطار الأيسر (من منظور الكود) على اليمين

        right_frame = tk.Frame(fields_frame, bg='white')
        right_frame.pack(side='left', fill='both', expand=True,
                         padx=10)  # وضع الإطار الأيمن (من منظور الكود) على اليسار

        # الحقول الأساسية في العمود الأيمن
        tk.Label(left_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.leave_emp_var = tk.StringVar()
        self.leave_emp = ttk.Combobox(left_frame, textvariable=self.leave_emp_var,
                                      state="readonly", width=25, font=('Arial', 10), justify='right')
        self.leave_emp.grid(row=0, column=0, pady=5, padx=5, sticky='ew')

        tk.Label(left_frame, text="نوع الإجازة:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.leave_type_var = tk.StringVar()
        self.leave_type = ttk.Combobox(left_frame, textvariable=self.leave_type_var,
                                       state="readonly", width=25, font=('Arial', 10), justify='right',
                                       values=["إجازة سنوية", "إجازة مرضية", "إجازة طارئة",
                                               "إجازة أمومة", "إجازة أبوة", "إجازة بدون راتب"])
        self.leave_type.grid(row=1, column=0, pady=5, padx=5, sticky='ew')

        tk.Label(left_frame, text="من تاريخ (YYYY-MM-DD):", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.leave_from = tk.Entry(left_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.leave_from.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        # الحقول الأساسية في العمود الأيسر
        tk.Label(right_frame, text="إلى تاريخ (YYYY-MM-DD):", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.leave_to = tk.Entry(right_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.leave_to.grid(row=0, column=0, pady=5, padx=5, sticky='ew')

        tk.Label(right_frame, text="عدد الأيام:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.leave_days = tk.Entry(right_frame, font=('Arial', 10), width=25, state='readonly', relief='solid', bd=1)
        self.leave_days.grid(row=1, column=0, pady=5, padx=5, sticky='ew')

        tk.Label(right_frame, text="السبب:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.leave_reason = tk.Entry(right_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.leave_reason.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        # تكوين تمدد الأعمدة
        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # ربط تغيير التاريخ بحساب الأيام
        self.leave_from.bind('<KeyRelease>', self.calculate_leave_days)
        self.leave_to.bind('<KeyRelease>', self.calculate_leave_days)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white', padx=10, pady=5)
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("📝 طلب إجازة", COLORS['primary'], self.add_leave),
            ("✅ اعتماد", COLORS['success'], self.approve_leave),
            ("❌ رفض", COLORS['danger'], self.reject_leave),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_leaves),
            ("📊 إحصائيات", COLORS['warning'], self.leave_statistics),
            ("🗑️ مسح الحقول", COLORS['dark'], self.clear_leave_entries)  # زر جديد
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=12, pady=5)
            btn.pack(side='right', padx=5)

        # جدول الإجازات
        table_frame = tk.Frame(frame, padx=10, pady=5)
        table_frame.pack(fill='both', expand=True)

        columns = ("id", "الموظف", "النوع", "من", "إلى", "الأيام", "السبب", "الحالة", "تاريخ الطلب")
        self.leave_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 150, 100, 100, 100, 80, 200, 100, 120]
        column_alignments = ['center', 'right', 'right', 'center', 'center', 'center', 'right', 'center', 'center']

        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=width, anchor=column_alignments[i])

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

        self.refresh_leaves()  # تحميل بيانات الإجازات عند إنشاء التبويب

    def calculate_leave_days(self, event=None):
        """
        حساب عدد أيام الإجازة بناءً على تاريخي البدء والانتهاء.
        يتم استدعاؤها عند تغيير حقول التاريخ.
        """
        try:
            from_date_str = self.leave_from.get().strip()
            to_date_str = self.leave_to.get().strip()

            # مسح حقل الأيام إذا كانت التواريخ فارغة
            if not from_date_str or not to_date_str:
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.config(state='readonly')
                return

            # تحويل التواريخ من نص إلى كائنات datetime
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

            if to_date >= from_date:
                days = (to_date - from_date).days + 1  # +1 لتضمين يوم البداية
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.insert(0, str(days))
                self.leave_days.config(state='readonly')
            else:
                self.leave_days.config(state='normal')
                self.leave_days.delete(0, tk.END)
                self.leave_days.insert(0, "تاريخ انتهاء قبل البدء!")
                self.leave_days.config(state='readonly')
        except ValueError:  # إذا كان تنسيق التاريخ غير صحيح
            self.leave_days.config(state='normal')
            self.leave_days.delete(0, tk.END)
            self.leave_days.insert(0, "تنسيق تاريخ خاطئ")
            self.leave_days.config(state='readonly')

    def add_leave(self):
        """إضافة طلب إجازة جديد بعد التحقق من البيانات"""
        name = self.leave_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
            return

        # جلب البيانات من الحقول
        leave_type = self.leave_type_var.get().strip()
        from_date_str = self.leave_from.get().strip()
        to_date_str = self.leave_to.get().strip()
        reason = self.leave_reason.get().strip()

        # التحقق من البيانات المطلوبة
        if not all([leave_type, from_date_str, to_date_str, reason]):
            messagebox.showerror("خطأ",
                                 "يرجى ملء جميع الحقول المطلوبة (الموظف، نوع الإجازة، من تاريخ، إلى تاريخ، السبب).")
            return

        # التحقق من صحة التواريخ
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

            if to_date < from_date:
                messagebox.showerror("خطأ", "تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية.")
                return
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ يجب أن يكون YYYY-MM-DD.")
            return

        # حساب عدد الأيام
        days = (to_date - from_date).days + 1

        data = (
            self.emp_dict[name],  # Employee ID
            leave_type,
            from_date_str,
            to_date_str,
            days,
            reason,
            "معلق",  # الحالة الافتراضية لطلب الإجازة
            datetime.now().strftime("%Y-%m-%d")  # تاريخ طلب الإجازة
        )

        result = self.execute_db(
            "INSERT INTO leaves (employee_id, type, start_date, end_date, days, reason, status, request_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم إرسال طلب الإجازة بنجاح.")
            self.clear_leave_entries()  # مسح الحقول
            self.refresh_leaves()  # تحديث الجدول
            self.update_status("تم إضافة طلب إجازة جديد.")

    def approve_leave(self):
        """اعتماد طلب الإجازة المحدد"""
        self.update_leave_status("معتمد")

    def reject_leave(self):
        """رفض طلب الإجازة المحدد"""
        self.update_leave_status("مرفوض")

    def update_leave_status(self, status):
        """
        تحديث حالة طلب الإجازة المحدد في الجدول.
        :param status: الحالة الجديدة (مثال: "معتمد", "مرفوض").
        """
        selected = self.leave_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار طلب إجازة لتغيير حالته.")
            return

        leave_data = self.leave_tree.item(selected[0])["values"]
        leave_id = leave_data[0]
        employee_name = leave_data[1]
        current_status = leave_data[7]

        if current_status == status:
            messagebox.showinfo("تنبيه", f"حالة الإجازة بالفعل '{status}'.")
            return

        if messagebox.askyesno("تأكيد",
                               f"هل أنت متأكد من رغبتك في تغيير حالة إجازة الموظف '{employee_name}' إلى '{status}'؟"):
            result = self.execute_db("UPDATE leaves SET status=? WHERE id=?", (status, leave_id))

            if result is not None:
                messagebox.showinfo("تم", f"تم تحديث حالة الإجازة إلى '{status}'.")
                self.refresh_leaves()
                self.update_status(f"تم تحديث حالة إجازة {employee_name} إلى '{status}'.")
                self.clear_leave_entries()  # مسح الحقول بعد الإجراء

    def clear_leave_entries(self):
        """مسح جميع حقول إدخال بيانات الإجازة"""
        self.leave_emp_var.set('')
        self.leave_type_var.set('')
        self.leave_from.delete(0, tk.END)
        self.leave_to.delete(0, tk.END)
        self.leave_reason.delete(0, tk.END)
        self.leave_days.config(state='normal')  # السماح بتعديل الحقل لمسحه
        self.leave_days.delete(0, tk.END)
        self.leave_days.config(state='readonly')  # إعادة الحقل لحالة القراءة فقط
        self.leave_tree.selection_remove(self.leave_tree.selection())  # إلغاء تحديد أي عنصر
        self.update_status("تم مسح حقول الإجازة.")

    def leave_statistics(self):
        """عرض إحصائيات حول عدد الإجازات المعتمدة، المعلقة، والمرفوضة"""
        approved_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'معتمد'", fetch=True)
        pending_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'معلق'", fetch=True)
        rejected_leaves = self.execute_db("SELECT COUNT(*) FROM leaves WHERE status = 'مرفوض'", fetch=True)

        # جلب القيم، مع التأكد من عدم وجود أخطاء إذا كانت النتائج فارغة
        approved_count = approved_leaves[0][0] if approved_leaves and approved_leaves[0] else 0
        pending_count = pending_leaves[0][0] if pending_leaves and pending_leaves[0] else 0
        rejected_count = rejected_leaves[0][0] if rejected_leaves and rejected_leaves[0] else 0

        messagebox.showinfo("إحصائيات الإجازات",
                            f"إجازات معتمدة: {approved_count}\n"
                            f"إجازات معلقة: {pending_count}\n"
                            f"إجازات مرفوضة: {rejected_count}")
        self.update_status("تم عرض إحصائيات الإجازات.")

    def refresh_leaves(self):
        """تحديث جدول عرض طلبات الإجازات"""
        for row in self.leave_tree.get_children():
            self.leave_tree.delete(row)

        # استعلام لجلب طلبات الإجازات مع أسماء الموظفين المرتبطة
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
        self.update_status(f"تم تحديث جدول الإجازات ({len(rows) if rows else 0} طلب).")

    # ---------------- تبويب الرواتب المحسن -----------------
    def create_salary_tab(self):
        """إنشاء تبويب إدارة الرواتب"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💰 الرواتب")

        # إطار الإدخال الرئيسي
        input_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=10, pady=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        # عنوان القسم
        tk.Label(input_frame, text="إدارة الرواتب",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=10)

        # إطار للحقول لترتيبها
        fields_frame = tk.Frame(input_frame, bg='white')
        fields_frame.pack(fill='x', padx=20, pady=10)

        # تقسيم الحقول إلى عمودين
        left_frame = tk.Frame(fields_frame, bg='white')
        left_frame.pack(side='right', fill='both', expand=True, padx=10)

        right_frame = tk.Frame(fields_frame, bg='white')
        right_frame.pack(side='left', fill='both', expand=True, padx=10)

        # الحقول الأساسية في العمود الأيمن
        tk.Label(left_frame, text="الموظف:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.salary_emp_var = tk.StringVar()
        self.salary_emp = ttk.Combobox(left_frame, textvariable=self.salary_emp_var,
                                       state="readonly", width=25, font=('Arial', 10), justify='right')
        self.salary_emp.grid(row=0, column=0, pady=5, padx=5, sticky='ew')
        # ربط حدث تحديد موظف بتحميل راتبه الأساسي
        self.salary_emp.bind("<<ComboboxSelected>>", self.load_employee_salary)

        tk.Label(left_frame, text="الشهر:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.salary_month = ttk.Combobox(left_frame, values=[f"{i:02d}" for i in range(1, 13)],
                                         state="readonly", width=25, font=('Arial', 10), justify='right')
        self.salary_month.grid(row=1, column=0, pady=5, padx=5, sticky='ew')
        self.salary_month.set(datetime.now().strftime("%m"))  # الشهر الحالي افتراضياً

        tk.Label(left_frame, text="السنة:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.salary_year = ttk.Combobox(left_frame, values=[str(i) for i in
                                                            range(datetime.now().year - 5, datetime.now().year + 2)],
                                        state="readonly", width=25, font=('Arial', 10), justify='right')
        self.salary_year.grid(row=2, column=0, pady=5, padx=5, sticky='ew')
        self.salary_year.set(datetime.now().year)  # السنة الحالية افتراضياً

        # الحقول الأساسية في العمود الأيسر
        tk.Label(right_frame, text="الراتب الأساسي:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.basic_salary_entry = tk.Entry(right_frame, font=('Arial', 10), width=25, state='readonly', relief='solid',
                                           bd=1)
        self.basic_salary_entry.grid(row=0, column=0, pady=5, padx=5, sticky='ew')

        tk.Label(right_frame, text="المكافآت:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.bonuses_entry = tk.Entry(right_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.bonuses_entry.grid(row=1, column=0, pady=5, padx=5, sticky='ew')
        self.bonuses_entry.insert(0, "0.0")  # قيمة افتراضية

        tk.Label(right_frame, text="الخصومات:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.deductions_entry = tk.Entry(right_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.deductions_entry.grid(row=2, column=0, pady=5, padx=5, sticky='ew')
        self.deductions_entry.insert(0, "0.0")  # قيمة افتراضية

        tk.Label(right_frame, text="صافي الراتب:", font=('Arial', 10, 'bold'),
                 bg='white', fg=COLORS['dark']).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        self.net_salary_label = tk.Label(right_frame, text="0.00", font=('Arial', 12, 'bold'),  # حجم خط أكبر
                                         bg='white', fg=COLORS['primary'])
        self.net_salary_label.grid(row=3, column=0, pady=5, padx=5, sticky='ew')

        # ربط الأحداث بحساب صافي الراتب تلقائياً
        self.bonuses_entry.bind('<KeyRelease>', self.calculate_net_salary)
        self.deductions_entry.bind('<KeyRelease>', self.calculate_net_salary)
        # هذا تم ربطه بالفعل في ComboboxSelected: self.salary_emp.bind("<<ComboboxSelected>>", self.load_employee_salary)

        # تكوين تمدد الأعمدة
        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # أزرار العمليات
        button_frame = tk.Frame(input_frame, bg='white', padx=10, pady=5)
        button_frame.pack(fill='x', pady=10)

        buttons = [
            ("➕ إضافة راتب", COLORS['success'], self.add_salary),
            ("✏️ تعديل راتب", COLORS['warning'], self.edit_salary),
            ("🗑️ حذف راتب", COLORS['danger'], self.delete_salary),
            ("🔄 تحديث", COLORS['secondary'], self.refresh_salaries),
            ("📄 طباعة كشوفات", COLORS['primary'], self.print_payslips),
            ("🗑️ مسح الحقول", COLORS['dark'], self.clear_salary_entries)  # زر جديد
        ]

        for text, color, command in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                            font=('Arial', 10, 'bold'), cursor='hand2',
                            command=command, width=15, pady=5)
            btn.pack(side='right', padx=5)

        # جدول الرواتب
        table_frame = tk.Frame(frame, padx=10, pady=5)
        table_frame.pack(fill='both', expand=True)

        columns = ("id", "الموظف", "الشهر", "السنة", "الراتب الأساسي",
                   "المكافآت", "الخصومات", "صافي الراتب", "تاريخ الدفع")
        self.salary_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # تنسيق الأعمدة
        column_widths = [0, 150, 80, 80, 120, 100, 100, 120, 120]
        column_alignments = ['center', 'right', 'center', 'center', 'center', 'center', 'center', 'center', 'center']

        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.salary_tree.heading(col, text=col)
            self.salary_tree.column(col, width=width, anchor=column_alignments[i])

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

        self.salary_tree.bind('<Double-1>', self.load_salary_for_edit)  # ربط النقر المزدوج بتحميل البيانات للتعديل

        self.refresh_salaries()  # تحميل بيانات الرواتب عند إنشاء التبويب

    def load_employee_salary(self, event=None):
        """
        تحميل الراتب الأساسي للموظف المحدد في حقل 'الراتب الأساسي'
        واستدعاء دالة حساب صافي الراتب.
        """
        selected_name = self.salary_emp_var.get()
        if selected_name:
            emp_id = self.emp_dict.get(selected_name)
            if emp_id:
                employee_data = self.execute_db("SELECT salary FROM employees WHERE id = ?", (emp_id,), fetch=True)
                if employee_data:
                    basic_salary = employee_data[0][0]
                    self.basic_salary_entry.config(state='normal')  # لتمكين الكتابة مؤقتاً
                    self.basic_salary_entry.delete(0, tk.END)
                    self.basic_salary_entry.insert(0, str(basic_salary))
                    self.basic_salary_entry.config(state='readonly')  # إعادة الحقل لحالة القراءة فقط
                    self.calculate_net_salary()  # إعادة حساب صافي الراتب بعد تحميل الأساسي

    def calculate_net_salary(self, event=None):
        """حساب صافي الراتب (الأساسي + المكافآت - الخصومات) وتحديث العرض"""
        try:
            basic_salary = float(self.basic_salary_entry.get() or 0.0)
            bonuses = float(self.bonuses_entry.get() or 0.0)
            deductions = float(self.deductions_entry.get() or 0.0)

            net_salary = basic_salary + bonuses - deductions
            self.net_salary_label.config(text=f"{net_salary:.2f}")  # عرض صافي الراتب مع تنسيق عشري
        except ValueError:
            self.net_salary_label.config(text="خطأ في الحساب")  # في حالة إدخال قيم غير رقمية
            self.update_status("خطأ: يرجى إدخال أرقام صحيحة للرواتب والمكافآت والخصومات.")

    def add_salary(self):
        """إضافة سجل راتب جديد لموظف في شهر وسنة محددين"""
        name = self.salary_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
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
            messagebox.showerror("خطأ", "يرجى إدخال قيم رقمية صحيحة للراتب الأساسي، المكافآت، والخصومات.")
            return

        payment_date = datetime.now().strftime("%Y-%m-%d")

        # التحقق من وجود سجل راتب لنفس الموظف والشهر والسنة لتجنب التكرار
        existing_salary = self.execute_db(
            "SELECT id FROM salaries WHERE employee_id = ? AND month = ? AND year = ?",
            (emp_id, month, year), fetch=True
        )

        if existing_salary:
            messagebox.showwarning("تنبيه",
                                   "سجل الراتب لهذا الموظف وهذا الشهر والسنة موجود بالفعل. يمكنك تعديله بدلاً من الإضافة.")
            return

        data = (emp_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date)

        result = self.execute_db(
            "INSERT INTO salaries (employee_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم إضافة سجل الراتب بنجاح.")
            self.clear_salary_entries()
            self.refresh_salaries()
            self.update_status(f"تم إضافة راتب جديد للموظف {name} لشهر {month}/{year}.")

    def load_salary_for_edit(self, event=None):
        """تحميل بيانات سجل الراتب المحدد في الحقول للتعديل"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للتعديل.")
            return

        salary_data = self.salary_tree.item(selected[0])["values"]

        # فك بيانات الصف المحدد
        # (id, الموظف, الشهر, السنة, الراتب الأساسي, المكافآت, الخصومات, صافي الراتب, تاريخ الدفع)
        salary_id, emp_name, month, year, basic_salary, bonuses, deductions, net_salary, payment_date = salary_data

        # تعيين قيم Comboboxes
        self.salary_emp_var.set(emp_name)
        self.salary_month.set(month)
        self.salary_year.set(str(year))

        # تعيين قيم حقول الإدخال
        self.basic_salary_entry.config(state='normal')  # تمكين مؤقت
        self.basic_salary_entry.delete(0, tk.END)
        self.basic_salary_entry.insert(0, str(basic_salary))
        self.basic_salary_entry.config(state='readonly')  # إعادة حالة القراءة فقط

        self.bonuses_entry.delete(0, tk.END)
        self.bonuses_entry.insert(0, str(bonuses))

        self.deductions_entry.delete(0, tk.END)
        self.deductions_entry.insert(0, str(deductions))

        self.net_salary_label.config(text=f"{net_salary:.2f}")

        self.update_status(f"تم تحميل سجل الراتب للموظف {emp_name} لشهر {month}/{year} للتعديل.")

    def edit_salary(self):
        """تعديل سجل راتب موجود بعد التحقق من البيانات"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للتعديل.")
            return

        salary_id = self.salary_tree.item(selected[0])["values"][0]  # الحصول على معرف سجل الراتب

        name = self.salary_emp_var.get()
        if not name or name not in self.emp_dict:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الموظف.")
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
            messagebox.showerror("خطأ", "يرجى إدخال قيم رقمية صحيحة للراتب الأساسي، المكافآت، والخصومات.")
            return

        payment_date = datetime.now().strftime("%Y-%m-%d")  # تحديث تاريخ الدفع إلى التاريخ الحالي عند التعديل

        # جمع البيانات للتحديث
        data = (emp_id, month, year, basic_salary, bonuses, deductions, net_salary, payment_date, salary_id)

        result = self.execute_db(
            "UPDATE salaries SET employee_id=?, month=?, year=?, basic_salary=?, bonuses=?, deductions=?, net_salary=?, payment_date=? WHERE id=?",
            data
        )

        if result is not None:
            messagebox.showinfo("تم", "تم تحديث سجل الراتب بنجاح.")
            self.clear_salary_entries()
            self.refresh_salaries()
            self.update_status(f"تم تحديث راتب الموظف {name} لشهر {month}/{year}.")

    def delete_salary(self):
        """حذف سجل راتب محدد مع طلب التأكيد"""
        selected = self.salary_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سجل راتب للحذف.")
            return

        salary_data = self.salary_tree.item(selected[0])["values"]
        salary_id = salary_data[0]
        emp_name = salary_data[1]
        month_year = f"{salary_data[2]}/{salary_data[3]}"

        if messagebox.askyesno("تأكيد الحذف",
                               f"هل أنت متأكد من رغبتك في حذف سجل راتب الموظف '{emp_name}' لشهر {month_year}؟\nهذا الإجراء لا يمكن التراجع عنه."):
            result = self.execute_db("DELETE FROM salaries WHERE id=?", (salary_id,))

            if result is not None:
                messagebox.showinfo("تم", "تم حذف سجل الراتب بنجاح.")
                self.refresh_salaries()
                self.update_status(f"تم حذف سجل راتب الموظف {emp_name} لشهر {month_year}.")
                self.clear_salary_entries()  # مسح الحقول بعد الحذف

    def clear_salary_entries(self):
        """مسح جميع حقول إدخال بيانات الرواتب"""
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
        self.net_salary_label.config(text="0.00")
        self.salary_tree.selection_remove(self.salary_tree.selection())
        self.update_status("تم مسح حقول الرواتب.")

    def print_payslips(self):
        """طباعة كشوفات الرواتب (وظيفة مستقبلية)"""
        messagebox.showinfo("طباعة كشوفات الرواتب",
                            "هذه الميزة قيد التطوير. يمكنك استخدام 'تقرير الرواتب' لإنشاء تقرير CSV حالياً.")
        # هنا يمكن إضافة منطق لإنشاء PDF أو ملفات CSV لكشوفات الرواتب الفردية.
        # قد يتطلب مكتبات إضافية مثل reportlab أو fpdf لإنشاء PDF مع تنسيق جيد.

    def refresh_salaries(self):
        """تحديث جدول عرض سجلات الرواتب"""
        for row in self.salary_tree.get_children():
            self.salary_tree.delete(row)

        # استعلام لجلب سجلات الرواتب مع أسماء الموظفين المرتبطة
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
        self.update_status(f"تم تحديث جدول الرواتب ({len(rows) if rows else 0} سجل).")

    # ---------------- تبويب التقارير المحسن -----------------
    def create_report_tab(self):
        """إنشاء تبويب التقارير"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 التقارير")

        # إطار الأدوات للتقارير
        report_tools_frame = tk.Frame(frame, bg='white', relief='raised', bd=1, padx=20, pady=20)
        report_tools_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(report_tools_frame, text="اختر نوع التقرير الذي ترغب في إنشائه:",
                 font=('Arial', 14, 'bold'), bg='white',
                 fg=COLORS['primary']).pack(pady=20)

        report_buttons = [
            ("تقرير الموظفين الشامل", self.generate_employee_report, COLORS['secondary']),
            ("تقرير الحضور والغياب المفصل", self.generate_attendance_report, COLORS['secondary']),
            ("تقرير الإجازات التفصيلي", self.generate_leave_report, COLORS['secondary']),
            ("تقرير الرواتب الشامل", self.generate_salary_report, COLORS['secondary']),
            ("تقرير الأداء (قريباً)", lambda: messagebox.showinfo("تقرير", "هذه الميزة قيد التطوير."), COLORS['dark']),
        ]

        # إنشاء الأزرار وتعبئتها في وسط الإطار
        for text, command, color in report_buttons:
            btn = tk.Button(report_tools_frame, text=text, bg=color, fg='white',
                            font=('Arial', 11, 'bold'), cursor='hand2',
                            command=command, width=35, height=2, bd=2, relief='raised')
            btn.pack(pady=8)  # مسافة بين الأزرار

    def generate_employee_report(self):
        """
        إنشاء تقرير شامل للموظفين.
        يعيد استخدام دالة print_employee_report الحالية لإنشاء ملف CSV.
        """
        self.print_employee_report()
        self.update_status("تم طلب تقرير الموظفين الشامل.")

    def generate_attendance_report(self):
        """
        إنشاء تقرير شامل للحضور والغياب.
        تفتح نافذة منبثقة للسماح للمستخدم بتحديد نطاق تاريخ للتقرير.
        """
        date_range_window = tk.Toplevel(self)  # نافذة علوية جديدة
        date_range_window.title("تحديد نطاق التقرير")
        date_range_window.geometry("350x250")
        date_range_window.grab_set()  # لجعل النافذة حصرية (لا يمكن التفاعل مع النافذة الرئيسية)
        date_range_window.transient(self)  # لجعلها تابعة للنافذة الرئيسية
        date_range_window.resizable(False, False)
        date_range_window.configure(bg=COLORS['light'])
        enable_rtl(date_range_window)

        # إطار للحقول داخل النافذة المنبثقة
        input_frame = tk.Frame(date_range_window, bg='white', padx=20, pady=20, relief='raised', bd=1)
        input_frame.pack(padx=20, pady=20)

        tk.Label(input_frame, text="من تاريخ (YYYY-MM-DD):", bg='white', font=('Arial', 10, 'bold')).grid(row=0,
                                                                                                          column=1,
                                                                                                          sticky='w',
                                                                                                          pady=5,
                                                                                                          padx=5)
        from_date_entry = tk.Entry(input_frame, font=('Arial', 10), width=20, relief='solid', bd=1)
        from_date_entry.grid(row=0, column=0, pady=5, padx=5, sticky='ew')
        from_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))  # تاريخ قبل 30 يوم

        tk.Label(input_frame, text="إلى تاريخ (YYYY-MM-DD):", bg='white', font=('Arial', 10, 'bold')).grid(row=1,
                                                                                                           column=1,
                                                                                                           sticky='w',
                                                                                                           pady=5,
                                                                                                           padx=5)
        to_date_entry = tk.Entry(input_frame, font=('Arial', 10), width=20, relief='solid', bd=1)
        to_date_entry.grid(row=1, column=0, pady=5, padx=5, sticky='ew')
        to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # تاريخ اليوم

        input_frame.columnconfigure(0, weight=1)

        def generate_report_action():
            from_date = from_date_entry.get().strip()
            to_date = to_date_entry.get().strip()
            try:
                # التحقق من صحة تنسيق التواريخ
                datetime.strptime(from_date, "%Y-%m-%d")
                datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. يجب أن يكون YYYY-MM-DD.")
                return

            if datetime.strptime(from_date, "%Y-%m-%d") > datetime.strptime(to_date, "%Y-%m-%d"):
                messagebox.showerror("خطأ", "تاريخ البدء لا يمكن أن يكون بعد تاريخ الانتهاء.")
                return

            self._generate_detailed_attendance_report(from_date, to_date)  # استدعاء دالة إنشاء التقرير
            date_range_window.destroy()  # إغلاق النافذة المنبثقة

        tk.Button(input_frame, text="إنشاء التقرير", command=generate_report_action,
                  bg=COLORS['primary'], fg='white', font=('Arial', 10, 'bold'), width=20, pady=5, cursor='hand2').grid(
            row=2, column=0, columnspan=2, pady=15)

    def _generate_detailed_attendance_report(self, from_date, to_date):
        """
        يولد تقرير حضور مفصل لنطاق تاريخ معين إلى ملف CSV.
        :param from_date: تاريخ البدء (YYYY-MM-DD).
        :param to_date: تاريخ الانتهاء (YYYY-MM-DD).
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")],
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
            messagebox.showinfo("تقرير الحضور", f"لا توجد بيانات حضور للفترة المحددة ({from_date} إلى {to_date}).")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف", "ساعات العمل", "الحالة"])

                for row in report_data:
                    work_hours = self.calculate_work_hours(row[2], row[3])
                    status = self.get_attendance_status(row[2], row[3])
                    writer.writerow([row[0], row[1], row[2] or "غائب", row[3] or "لم ينصرف", work_hours, status])
            messagebox.showinfo("تم", f"تم حفظ تقرير الحضور في: {file_path}")
            self.update_status(f"تم إنشاء تقرير حضور للفترة {from_date} - {to_date}.")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def generate_leave_report(self):
        """إنشاء تقرير شامل للإجازات إلى ملف CSV"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")],
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
            messagebox.showinfo("تقرير الإجازات", "لا توجد بيانات إجازات مسجلة.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["اسم الموظف", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة",
                                 "تاريخ الطلب"])
                writer.writerows(report_data)
            messagebox.showinfo("تم", f"تم حفظ تقرير الإجازات في: {file_path}")
            self.update_status("تم إنشاء تقرير الإجازات بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    def generate_salary_report(self):
        """إنشاء تقرير شامل للرواتب إلى ملف CSV"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("ملفات CSV", "*.csv"), ("جميع الملفات", "*.*")],
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
            messagebox.showinfo("تقرير الرواتب", "لا توجد بيانات رواتب مسجلة.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["اسم الموظف", "الشهر", "السنة", "الراتب الأساسي", "المكافآت", "الخصومات", "صافي الراتب",
                     "تاريخ الدفع"])
                writer.writerows(report_data)
            messagebox.showinfo("تم", f"تم حفظ تقرير الرواتب في: {file_path}")
            self.update_status("تم إنشاء تقرير الرواتب بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ في التقرير", f"حدث خطأ أثناء حفظ التقرير: {e}")

    # ---------------- تبويب الإعدادات المحسن -----------------
    def create_settings_tab(self):
        """إنشاء تبويب الإعدادات"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔧 الإعدادات")

        # إطار الإعدادات العامة
        general_settings_frame = tk.LabelFrame(frame, text="إعدادات عامة", bg='white', relief='raised', bd=1, padx=10,
                                               pady=10, font=('Arial', 11, 'bold'), fg=COLORS['primary'])
        general_settings_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(general_settings_frame, text="اسم قاعدة البيانات:", font=('Arial', 10, 'bold'), bg='white',
                 fg=COLORS['dark']).grid(row=0,
                                         column=1,
                                         sticky='w',
                                         pady=5, padx=5)
        self.db_name_label = tk.Label(general_settings_frame, text=os.path.basename(DB_NAME), font=('Arial', 10),
                                      bg='white', fg=COLORS['secondary'])
        self.db_name_label.grid(row=0, column=0, sticky='w', pady=5, padx=5)

        tk.Button(general_settings_frame, text="فتح مجلد قاعدة البيانات", command=self.open_db_folder,
                  bg=COLORS['secondary'], fg='white', font=('Arial', 10, 'bold'), cursor='hand2', width=20,
                  pady=5).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(general_settings_frame, text="إعادة ضبط قاعدة البيانات (حذف جميع البيانات)",
                  command=self.reset_database,
                  bg=COLORS['danger'], fg='white', font=('Arial', 10, 'bold'), cursor='hand2', width=30, pady=5).grid(
            row=1, column=0, columnspan=3,
            pady=10)

        # إعدادات المستخدمين (المسؤولين)
        admin_settings_frame = tk.LabelFrame(frame, text="إدارة حسابات المسؤولين", bg='white', relief='raised', bd=1,
                                             padx=10, pady=10, font=('Arial', 11, 'bold'), fg=COLORS['primary'])
        admin_settings_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(admin_settings_frame, text="اسم المستخدم:", font=('Arial', 10), bg='white', fg=COLORS['dark']).grid(
            row=0, column=1,
            sticky='w', pady=5, padx=5)
        self.admin_username_entry = tk.Entry(admin_settings_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
        self.admin_username_entry.grid(row=0, column=0, pady=5, padx=5)

        tk.Label(admin_settings_frame, text="كلمة المرور الجديدة:", font=('Arial', 10), bg='white',
                 fg=COLORS['dark']).grid(row=1,
                                         column=1,
                                         sticky='w',
                                         pady=5, padx=5)
        self.admin_password_entry = tk.Entry(admin_settings_frame, show="*", font=('Arial', 10), width=25,
                                             relief='solid', bd=1)
        self.admin_password_entry.grid(row=1, column=0, pady=5, padx=5)

        tk.Label(admin_settings_frame, text="تأكيد كلمة المرور:", font=('Arial', 10), bg='white',
                 fg=COLORS['dark']).grid(row=2, column=1,
                                         sticky='w',
                                         pady=5, padx=5)
        self.admin_confirm_password_entry = tk.Entry(admin_settings_frame, show="*", font=('Arial', 10), width=25,
                                                     relief='solid', bd=1)
        self.admin_confirm_password_entry.grid(row=2, column=0, pady=5, padx=5)

        tk.Button(admin_settings_frame, text="إضافة / تعديل مسؤول", command=self.add_or_update_admin,
                  bg=COLORS['success'], fg='white', font=('Arial', 10, 'bold'), cursor='hand2', width=20, pady=5).grid(
            row=3, column=0, columnspan=2,
            pady=10, padx=5, sticky='e')
        tk.Button(admin_settings_frame, text="حذف مسؤول", command=self.delete_admin, bg=COLORS['danger'], fg='white',
                  font=('Arial', 10, 'bold'), cursor='hand2', width=15, pady=5).grid(row=3, column=2, pady=10, padx=5,
                                                                                     sticky='w')

        # قائمة المسؤولين (للحذف)
        tk.Label(admin_settings_frame, text="المسؤولون الحاليون:", font=('Arial', 10, 'bold'), bg='white',
                 fg=COLORS['dark']).grid(row=4,
                                         column=0,
                                         columnspan=3,
                                         sticky='w',
                                         pady=10, padx=5)
        self.admin_listbox = tk.Listbox(admin_settings_frame, height=5, font=('Arial', 10), relief='solid', bd=1)
        self.admin_listbox.grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        self.refresh_admin_list()

        admin_settings_frame.columnconfigure(0, weight=1)  # لجعل حقول الإدخال تتمدد
        admin_settings_frame.columnconfigure(1, weight=0)  # العمود الخاص بالـ Labels لا يتمدد
        admin_settings_frame.columnconfigure(2, weight=1)  # لجعل حقول الإدخال تتمدد

    def open_db_folder(self):
        """فتح مجلد قاعدة البيانات في مستكشف الملفات (يتوافق مع أنظمة التشغيل المختلفة)"""
        db_directory = os.path.dirname(DB_NAME)
        if not db_directory:  # إذا كان DB_NAME مجرد اسم ملف، فالمجلد الحالي هو المجلد
            db_directory = os.getcwd()
        try:
            if os.path.exists(db_directory):
                if os.name == 'nt':  # Windows
                    os.startfile(db_directory)
                elif os.uname().sysname == 'Darwin':  # macOS
                    os.system(f'open "{db_directory}"')
                else:  # Linux/Unix
                    os.system(f'xdg-open "{db_directory}"')
            else:
                messagebox.showwarning("تنبيه", f"المجلد '{db_directory}' غير موجود.")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن فتح المجلد: {e}")

    def reset_database(self):
        """إعادة ضبط قاعدة البيانات بحذف جميع الجداول وإعادة إنشائها. هذا يحذف جميع البيانات."""
        if messagebox.askyesno("تأكيد إعادة الضبط",
                               "هل أنت متأكد تماماً من رغبتك في إعادة ضبط قاعدة البيانات؟\n\n"
                               "سيؤدي هذا إلى حذف *جميع* البيانات (الموظفين، الحضور، الإجازات، الرواتب، المسؤولين) "
                               "ولا يمكن التراجع عن هذا الإجراء!\n\n"
                               "اضغط 'نعم' للمتابعة أو 'لا' للإلغاء."):
            try:
                conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
                c = conn.cursor()

                # حذف جميع الجداول
                c.execute("DROP TABLE IF EXISTS employees")
                c.execute("DROP TABLE IF EXISTS attendance")
                c.execute("DROP TABLE IF EXISTS leaves")
                c.execute("DROP TABLE IF EXISTS salaries")
                c.execute("DROP TABLE IF EXISTS admin")
                conn.commit()
                conn.close()

                # إعادة تهيئة قاعدة البيانات (لإعادة إنشاء الجداول وحساب المسؤول الافتراضي)
                self.init_database()
                self.create_default_admin()  # يجب إعادة إنشاء المدير الافتراضي بعد حذف جدول admin

                messagebox.showinfo("تم",
                                    "تمت إعادة ضبط قاعدة البيانات بنجاح. جميع البيانات القديمة حذفت وتم إنشاء هيكل جديد.")
                # تحديث جميع الجداول والقوائم في الواجهة
                self.refresh_employees()
                self.refresh_attendance()
                self.refresh_leaves()
                self.refresh_salaries()
                self.refresh_employees_combobox()
                self.refresh_admin_list()
                self.update_status("تمت إعادة ضبط قاعدة البيانات.")
            except Exception as e:
                messagebox.showerror("خطأ في إعادة الضبط", f"حدث خطأ أثناء إعادة ضبط قاعدة البيانات: {e}")

    def refresh_admin_list(self):
        """تحديث قائمة المسؤولين المعروضة في Listbox بتبويب الإعدادات"""
        self.admin_listbox.delete(0, tk.END)  # مسح القائمة الحالية
        admins = self.execute_db("SELECT username FROM admin ORDER BY username ASC", fetch=True)
        if admins:
            for admin_username in admins:
                self.admin_listbox.insert(tk.END, admin_username[0])  # إضافة كل اسم مستخدم

    def add_or_update_admin(self):
        """إضافة حساب مسؤول جديد أو تحديث كلمة مرور مسؤول موجود"""
        username = self.admin_username_entry.get().strip()
        password = self.admin_password_entry.get().strip()
        confirm_password = self.admin_confirm_password_entry.get().strip()

        if not username or not password or not confirm_password:
            messagebox.showerror("خطأ", "يرجى ملء جميع حقول اسم المستخدم وكلمة المرور.")
            return

        if password != confirm_password:
            messagebox.showerror("خطأ", "كلمة المرور وتأكيدها غير متطابقين. يرجى التأكد من تطابقهما.")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = database.safe_connect() if hasattr(database, 'safe_connect') else sqlite3.connect(DB_NAME)
            c = conn.cursor()

            # التحقق مما إذا كان اسم المستخدم موجوداً بالفعل
            c.execute("SELECT id FROM admin WHERE username = ?", (username,))
            existing_admin = c.fetchone()

            if existing_admin:
                # إذا كان موجوداً، قم بتحديث كلمة المرور
                c.execute("UPDATE admin SET password = ? WHERE id = ?", (password_hash, existing_admin[0]))
                messagebox.showinfo("تم", f"تم تحديث كلمة مرور المسؤول '{username}' بنجاح.")
            else:
                # إذا لم يكن موجوداً، قم بإضافة مسؤول جديد
                c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, password_hash))
                messagebox.showinfo("تم", f"تم إضافة المسؤول '{username}' بنجاح.")

            conn.commit()
            conn.close()
            # مسح حقول الإدخال
            self.admin_username_entry.delete(0, tk.END)
            self.admin_password_entry.delete(0, tk.END)
            self.admin_confirm_password_entry.delete(0, tk.END)
            self.refresh_admin_list()  # تحديث قائمة المسؤولين
            self.update_status(f"تم تحديث معلومات المسؤول {username}.")
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "اسم المستخدم هذا موجود بالفعل. يرجى اختيار اسم مستخدم آخر.")
        except Exception as e:
            messagebox.showerror("خطأ في إدارة المسؤولين", f"حدث خطأ: {e}")

    def delete_admin(self):
        """حذف حساب مسؤول محدد من القائمة"""
        selected_index = self.admin_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("تنبيه", "يرجى اختيار مسؤول لحذفه من القائمة.")
            return

        selected_admin = self.admin_listbox.get(selected_index[0])

        if selected_admin == "admin":
            messagebox.showwarning("تنبيه", "لا يمكنك حذف المسؤول الافتراضي 'admin' لأسباب أمنية.")
            return

        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من رغبتك في حذف المسؤول '{selected_admin}'؟\n"
                                              "هذا الإجراء لا يمكن التراجع عنه."):
            result = self.execute_db("DELETE FROM admin WHERE username=?", (selected_admin,))
            if result is not None:
                messagebox.showinfo("تم", f"تم حذف المسؤول '{selected_admin}' بنجاح.")
                self.refresh_admin_list()  # تحديث القائمة
                self.update_status(f"تم حذف المسؤول {selected_admin}.")


# نقطة بداية تشغيل التطبيق
if __name__ == '__main__':
    # تهيئة قاعدة البيانات عند بدء تشغيل التطبيق (لضمان وجود الجداول الأساسية)
    try:
        conn = None
        # محاولة الاتصال باستخدام database.safe_connect إذا كانت موجودة
        if hasattr(database, 'safe_connect'):
            conn = database.safe_connect()
        else:  # وإلا، الاتصال المباشر
            conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # إنشاء جدول admin (إذا لم يكن موجوداً)
        c.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        # إنشاء الجداول الأخرى أيضاً عند بدء التشغيل الرئيسي
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
        print(f"خطأ في إنشاء الجداول عند بدء التشغيل: {e}")

    # بدء تشغيل نافذة تسجيل الدخول
    login_app = LoginWindow()
    login_app.mainloop()