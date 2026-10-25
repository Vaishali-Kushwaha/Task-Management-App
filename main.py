import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import hmac
from datetime import datetime

from database import get_connection


class TaskManagementApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Task Management System")
        self.root.geometry("1150x720")
        self.root.minsize(950, 620)
        self.root.configure(bg="#F3F6FB")

        self.current_user_id = None
        self.current_username = None
        self.selected_task_id = None

        self.setup_styles()
        self.show_login()

    # ---------------- STYLES ----------------

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10),
            background="white",
            fieldbackground="white"
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            padding=8
        )

    # ---------------- PASSWORD ----------------

    @staticmethod
    def hash_password(password):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            b"TaskManagementAppSalt",
            200000
        ).hex()

    # ---------------- DATABASE ----------------

    def get_db(self):
        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to MySQL. Check database.py."
            )

        return connection

    # ---------------- CLEAR SCREEN ----------------

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------- LOGIN ----------------

    def show_login(self):
        self.clear_window()

        container = tk.Frame(
            self.root,
            bg="white",
            padx=40,
            pady=35
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text="TASK MANAGEMENT",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#153448"
        ).pack(pady=(0, 8))

        tk.Label(
            container,
            text="Login to manage your tasks",
            font=("Arial", 11),
            bg="white",
            fg="#64748B"
        ).pack(pady=(0, 25))

        tk.Label(
            container,
            text="Username",
            bg="white",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.login_username = tk.Entry(
            container,
            font=("Arial", 12),
            width=30
        )
        self.login_username.pack(pady=(5, 15), ipady=5)

        tk.Label(
            container,
            text="Password",
            bg="white",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.login_password = tk.Entry(
            container,
            font=("Arial", 12),
            width=30,
            show="*"
        )
        self.login_password.pack(pady=(5, 20), ipady=5)

        tk.Button(
            container,
            text="LOGIN",
            command=self.login,
            bg="#176B87",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(pady=5)

        tk.Button(
            container,
            text="Create New Account",
            command=self.show_register,
            bg="white",
            fg="#176B87",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=(12, 0))

        self.login_username.focus_set()
        self.root.bind("<Return>", lambda event: self.login())

    # ---------------- REGISTER SCREEN ----------------

    def show_register(self):
        self.clear_window()
        self.root.unbind("<Return>")

        container = tk.Frame(
            self.root,
            bg="white",
            padx=40,
            pady=30
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text="CREATE ACCOUNT",
            font=("Arial", 22, "bold"),
            bg="white",
            fg="#153448"
        ).pack(pady=(0, 20))

        tk.Label(
            container,
            text="Username",
            bg="white",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.register_username = tk.Entry(
            container,
            font=("Arial", 12),
            width=30
        )
        self.register_username.pack(pady=(5, 15), ipady=5)

        tk.Label(
            container,
            text="Password (minimum 8 characters)",
            bg="white",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.register_password = tk.Entry(
            container,
            font=("Arial", 12),
            width=30,
            show="*"
        )
        self.register_password.pack(pady=(5, 15), ipady=5)

        tk.Label(
            container,
            text="Confirm Password",
            bg="white",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.confirm_password = tk.Entry(
            container,
            font=("Arial", 12),
            width=30,
            show="*"
        )
        self.confirm_password.pack(pady=(5, 20), ipady=5)

        tk.Button(
            container,
            text="REGISTER",
            command=self.register,
            bg="#176B87",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack()

        tk.Button(
            container,
            text="Back to Login",
            command=self.show_login,
            bg="white",
            fg="#176B87",
            relief="flat",
            cursor="hand2"
        ).pack(pady=(12, 0))

    # ---------------- REGISTER ----------------

    def register(self):
        username = self.register_username.get().strip()
        password = self.register_password.get()
        confirm = self.confirm_password.get()

        if not username or not password or not confirm:
            messagebox.showwarning(
                "Validation",
                "Please fill in all fields."
            )
            return

        if len(username) < 3:
            messagebox.showwarning(
                "Validation",
                "Username must contain at least 3 characters."
            )
            return

        if len(password) < 8:
            messagebox.showwarning(
                "Validation",
                "Password must contain at least 8 characters."
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Validation",
                "Passwords do not match."
            )
            return

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            query = """
                INSERT INTO app_users (username, password_hash)
                VALUES (%s, %s)
            """

            cursor.execute(
                query,
                (username, self.hash_password(password))
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Account created successfully!"
            )

            self.show_login()
            self.login_username.insert(0, username)

        except Exception as error:
            connection.rollback()

            if getattr(error, "errno", None) == 1062:
                messagebox.showerror(
                    "Registration Error",
                    "Username already exists."
                )
            else:
                messagebox.showerror(
                    "Registration Error",
                    str(error)
                )

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ---------------- LOGIN ----------------

    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showwarning(
                "Validation",
                "Enter username and password."
            )
            return

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, username, password_hash
                FROM app_users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user is None:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )
                return

            entered_hash = self.hash_password(password)

            if not hmac.compare_digest(user[2], entered_hash):
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )
                return

            self.current_user_id = user[0]
            self.current_username = user[1]

            self.root.unbind("<Return>")
            self.show_dashboard()

        except Exception as error:
            messagebox.showerror("Login Error", str(error))

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):
        self.clear_window()
        self.selected_task_id = None

        header = tk.Frame(self.root, bg="#153448", height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="TASK MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold"),
            bg="#153448",
            fg="white"
        ).pack(side="left", padx=20, pady=18)

        tk.Button(
            header,
            text="Logout",
            command=self.logout,
            bg="#E76F51",
            fg="white",
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="right", padx=20)

        tk.Label(
            self.root,
            text=f"Welcome, {self.current_username}!",
            font=("Arial", 18, "bold"),
            bg="#F3F6FB",
            fg="#153448"
        ).pack(anchor="w", padx=22, pady=(15, 5))

        self.stats_frame = tk.Frame(self.root, bg="#F3F6FB")
        self.stats_frame.pack(fill="x", padx=15, pady=10)

        self.refresh_stats()

        # Search and filter section
        filters = tk.Frame(self.root, bg="#F3F6FB")
        filters.pack(fill="x", padx=22, pady=8)

        tk.Label(
            filters,
            text="Search:",
            bg="#F3F6FB",
            font=("Arial", 10, "bold")
        ).pack(side="left")

        self.search_var = tk.StringVar()

        tk.Entry(
            filters,
            textvariable=self.search_var,
            width=25
        ).pack(side="left", padx=8, ipady=4)

        tk.Button(
            filters,
            text="Search",
            command=self.load_tasks,
            bg="#176B87",
            fg="white",
            relief="flat",
            padx=12
        ).pack(side="left", padx=3)

        tk.Button(
            filters,
            text="Clear Search",
            command=self.clear_search,
            bg="#64748B",
            fg="white",
            relief="flat",
            padx=10
        ).pack(side="left", padx=3)

        tk.Label(
            filters,
            text="Status:",
            bg="#F3F6FB"
        ).pack(side="left", padx=(15, 5))

        self.filter_var = tk.StringVar(value="All")

        status_box = ttk.Combobox(
            filters,
            textvariable=self.filter_var,
            values=[
                "All",
                "Pending",
                "In Progress",
                "Completed"
            ],
            state="readonly",
            width=15
        )
        status_box.pack(side="left")
        status_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.load_tasks()
        )

        # Task table
        table_frame = tk.Frame(self.root, bg="#F3F6FB")
        table_frame.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(5, 10)
        )

        columns = (
            "id",
            "title",
            "due_date",
            "priority",
            "status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "title": "Task Title",
            "due_date": "Due Date",
            "priority": "Priority",
            "status": "Status"
        }

        widths = {
            "id": 55,
            "title": 350,
            "due_date": 130,
            "priority": 120,
            "status": 140
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_task
        )

        # Buttons
        buttons = tk.Frame(self.root, bg="#F3F6FB")
        buttons.pack(fill="x", padx=18, pady=(0, 15))

        button_data = [
            ("Add Task", self.add_task, "#176B87"),
            ("Update Task", self.update_task, "#287D5A"),
            ("Delete Task", self.delete_task, "#D9534F"),
            ("Refresh", self.refresh_all, "#64748B")
        ]

        for label, command, color in button_data:
            tk.Button(
                buttons,
                text=label,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=15,
                pady=8,
                cursor="hand2"
            ).pack(side="left", padx=5)

        self.load_tasks()

    # ---------------- DASHBOARD STATS ----------------

    def refresh_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(SUM(status = 'Pending'), 0),
                    COALESCE(SUM(status = 'In Progress'), 0),
                    COALESCE(SUM(status = 'Completed'), 0)
                FROM tasks
                WHERE user_id = %s
                """,
                (self.current_user_id,)
            )

            total, pending, progress, completed = cursor.fetchone()

            values = [
                ("TOTAL TASKS", total),
                ("PENDING", pending),
                ("IN PROGRESS", progress),
                ("COMPLETED", completed)
            ]

            for title, value in values:
                card = tk.Frame(
                    self.stats_frame,
                    bg="white",
                    padx=12,
                    pady=12,
                    highlightbackground="#DCE4ED",
                    highlightthickness=1
                )

                card.pack(
                    side="left",
                    fill="both",
                    expand=True,
                    padx=5
                )

                tk.Label(
                    card,
                    text=title,
                    font=("Arial", 9, "bold"),
                    bg="white",
                    fg="#64748B"
                ).pack()

                tk.Label(
                    card,
                    text=str(value),
                    font=("Arial", 22, "bold"),
                    bg="white",
                    fg="#176B87"
                ).pack(pady=(5, 0))

        except Exception as error:
            messagebox.showerror("Dashboard Error", str(error))

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ---------------- LOAD TASKS ----------------

    def load_tasks(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            search_text = self.search_var.get().strip()
            status = self.filter_var.get()

            query = """
                SELECT id, title, due_date, priority, status
                FROM tasks
                WHERE user_id = %s
            """

            params = [self.current_user_id]

            if search_text:
                query += " AND title LIKE %s"
                params.append("%" + search_text + "%")

            if status != "All":
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY id DESC"

            cursor.execute(query, tuple(params))

            for row in cursor.fetchall():
                task_id, title, due_date, priority, status = row

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        task_id,
                        title,
                        due_date.strftime("%Y-%m-%d")
                        if due_date else "",
                        priority,
                        status
                    )
                )

        except Exception as error:
            messagebox.showerror("Task Loading Error", str(error))

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ---------------- CLEAR SEARCH ----------------

    def clear_search(self):
        self.search_var.set("")
        self.filter_var.set("All")
        self.load_tasks()

    # ---------------- SELECT TASK ----------------

    def select_task(self, event=None):
        selected = self.tree.selection()

        if not selected:
            self.selected_task_id = None
            return

        values = self.tree.item(selected[0], "values")

        if values:
            self.selected_task_id = int(values[0])

    # ---------------- TASK FORM ----------------

    def task_form(self, title, initial=None, task_id=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("460x540")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=title,
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#153448"
        ).pack(pady=15)

        form = tk.Frame(dialog, bg="white", padx=25)
        form.pack(fill="both", expand=True)

        tk.Label(
            form,
            text="Task Title *",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        title_var = tk.StringVar(
            value=initial[0] if initial else ""
        )

        title_entry = tk.Entry(
            form,
            textvariable=title_var,
            font=("Arial", 11)
        )
        title_entry.pack(fill="x", pady=(5, 12), ipady=5)

        tk.Label(
            form,
            text="Description",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        description_box = tk.Text(
            form,
            height=4,
            font=("Arial", 10)
        )
        description_box.pack(fill="x", pady=(5, 12))

        if initial and initial[1]:
            description_box.insert("1.0", initial[1])

        tk.Label(
            form,
            text="Due Date (YYYY-MM-DD)",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        date_var = tk.StringVar(
            value=str(initial[2]) if initial and initial[2] else ""
        )

        tk.Entry(
            form,
            textvariable=date_var,
            font=("Arial", 11)
        ).pack(fill="x", pady=(5, 12), ipady=4)

        tk.Label(
            form,
            text="Priority",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        priority_var = tk.StringVar(
            value=initial[3] if initial else "Medium"
        )

        ttk.Combobox(
            form,
            textvariable=priority_var,
            values=["Low", "Medium", "High"],
            state="readonly"
        ).pack(fill="x", pady=(5, 12))

        tk.Label(
            form,
            text="Status",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        status_var = tk.StringVar(
            value=initial[4] if initial else "Pending"
        )

        ttk.Combobox(
            form,
            textvariable=status_var,
            values=["Pending", "In Progress", "Completed"],
            state="readonly"
        ).pack(fill="x", pady=(5, 12))

        def save_task():
            task_title = title_var.get().strip()
            description = description_box.get("1.0", "end").strip()
            due_date = date_var.get().strip()
            priority = priority_var.get()
            status = status_var.get()

            if not task_title:
                messagebox.showwarning(
                    "Validation",
                    "Task title is required.",
                    parent=dialog
                )
                return

            if len(task_title) > 150:
                messagebox.showwarning(
                    "Validation",
                    "Task title cannot exceed 150 characters.",
                    parent=dialog
                )
                return

            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning(
                        "Validation",
                        "Enter the date in YYYY-MM-DD format.",
                        parent=dialog
                    )
                    return

            connection = self.get_db()

            if connection is None:
                return

            cursor = None

            try:
                cursor = connection.cursor()

                if task_id is None:
                    query = """
                        INSERT INTO tasks
                        (user_id, title, description, due_date,
                         priority, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """

                    cursor.execute(
                        query,
                        (
                            self.current_user_id,
                            task_title,
                            description,
                            due_date or None,
                            priority,
                            status
                        )
                    )

                else:
                    query = """
                        UPDATE tasks
                        SET title = %s,
                            description = %s,
                            due_date = %s,
                            priority = %s,
                            status = %s
                        WHERE id = %s AND user_id = %s
                    """

                    cursor.execute(
                        query,
                        (
                            task_title,
                            description,
                            due_date or None,
                            priority,
                            status,
                            task_id,
                            self.current_user_id
                        )
                    )

                connection.commit()
                dialog.destroy()

                self.refresh_all()

                messagebox.showinfo(
                    "Success",
                    "Task saved successfully!"
                    if task_id is None
                    else "Task updated successfully!"
                )

            except Exception as error:
                connection.rollback()

                messagebox.showerror(
                    "Database Error",
                    str(error),
                    parent=dialog
                )

            finally:
                if cursor:
                    cursor.close()

                connection.close()

        tk.Button(
            dialog,
            text="Save Task",
            command=save_task,
            bg="#176B87",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            pady=8,
            cursor="hand2"
        ).pack(fill="x", padx=25, pady=15)

        title_entry.focus_set()

    # ---------------- ADD TASK ----------------

    def add_task(self):
        self.task_form("Add New Task")

    # ---------------- UPDATE TASK ----------------

    def update_task(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Task",
                "Please select a task to update."
            )
            return

        task_id = int(self.tree.item(selected[0], "values")[0])

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT title, description, due_date, priority, status
                FROM tasks
                WHERE id = %s AND user_id = %s
                """,
                (task_id, self.current_user_id)
            )

            task = cursor.fetchone()

            if task is None:
                messagebox.showerror(
                    "Error",
                    "Task not found."
                )
                return

            initial = (
                task[0],
                task[1] or "",
                task[2].strftime("%Y-%m-%d") if task[2] else "",
                task[3],
                task[4]
            )

        except Exception as error:
            messagebox.showerror("Error", str(error))
            return

        finally:
            if cursor:
                cursor.close()

            connection.close()

        self.task_form(
            "Update Task",
            initial=initial,
            task_id=task_id
        )

        # ---------------- DELETE TASK ----------------

    def delete_task(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Task",
                "Please select a task to delete."
            )
            return

        values = self.tree.item(selected[0], "values")
        task_id = int(values[0])
        task_title = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n{task_title}?"
        )

        if not confirm:
            return

        connection = self.get_db()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM tasks
                WHERE id = %s AND user_id = %s
                """,
                (task_id, self.current_user_id)
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Task deleted successfully!"
            )

            self.refresh_all()

        except Exception as error:
            connection.rollback()
            messagebox.showerror("Delete Error", str(error))

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ---------------- REFRESH ----------------

    def refresh_all(self):
        self.selected_task_id = None
        self.refresh_stats()
        self.load_tasks()

    # ---------------- LOGOUT ----------------

    def logout(self):
        self.current_user_id = None
        self.current_username = None

        self.root.unbind("<Return>")
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagementApp(root)
    root.mainloop()