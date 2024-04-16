import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
import pymysql

class DatabaseManager:
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='root', password='689900', db='students')
        self.cursor = self.connection.cursor()

    def execute_query(self, query, parameters=None):
        try:
            self.cursor.execute(query, parameters)
            self.connection.commit()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return False

    def fetch_data(self, query, parameters=None):
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

class InsertDialog(tk.Toplevel):
    def __init__(self, parent, table_name):
        super().__init__(parent)
        self.transient(parent)
        self.title("Insert Data")
        self.result = None
        self.table_name = table_name
        self.fields = self.get_columns(table_name)
        self.entries = {}
        self.create_widgets()

    def get_columns(self, table_name):
        # Include your implementation of fetching columns for the specified table
        db_manager = DatabaseManager()
        db_manager.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = [col[0] for col in db_manager.cursor.fetchall()]
        return columns

    def create_widgets(self):
        tk.Label(self, text="Insert data for table: " + self.table_name).pack()

        for field in self.fields:
            tk.Label(self, text=field).pack()

            if field == "gender":  # For gender field
                values = ["Male", "Female"]
                combo = ttk.Combobox(self, values=values)
                combo.pack()
                self.entries[field] = combo
            elif field == "course_id":  # For course_id field
                # Fetch existing courses and use them as options
                db_manager = DatabaseManager()
                courses = db_manager.fetch_data("SELECT course_id FROM course;")
                values = [course[0] for course in courses]
                combo = ttk.Combobox(self, values=values)
                combo.pack()
                self.entries[field] = combo
            else:
                entry = tk.Entry(self)
                entry.pack()
                self.entries[field] = entry

        tk.Button(self, text="Insert", command=self.ok).pack()

    def ok(self):
        values = [entry.get() if isinstance(entry, tk.Entry) else entry.get() for entry in self.entries.values()]
        query = f"INSERT INTO {self.table_name} VALUES ({', '.join(['%s'] * len(values))});"
        success = DatabaseManager().execute_query(query, tuple(values))
        if success:
            messagebox.showinfo("Success", f"Insertion into {self.table_name} successful.")
            self.destroy()
        else:
            messagebox.showerror("Error", f"Insertion into {self.table_name} failed.")


class UpdateDialog(tk.Toplevel):
    def __init__(self, parent, table_name, primary_key):
        super().__init__(parent)
        self.transient(parent)
        self.title("Update Data")
        self.result = None
        self.table_name = table_name
        self.primary_key = primary_key
        self.fields = self.get_columns(table_name)
        self.values = self.get_values(table_name, primary_key)
        self.entries = {}
        self.create_widgets()

    def get_columns(self, table_name):
        # Include your implementation of fetching columns for the specified table
        db_manager = DatabaseManager()
        db_manager.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = [col[0] for col in db_manager.cursor.fetchall()]
        return columns

    def get_values(self, table_name, primary_key):
        # Include your implementation of fetching values for the specified primary key
        query = f"SELECT * FROM {table_name} WHERE {table_name}_id = %s;"
        values = DatabaseManager().fetch_data(query, (primary_key,))
        return values[0] if values else None

    def create_widgets(self):
        tk.Label(self, text="Update data for table: " + self.table_name).pack()

        for field, value in zip(self.fields, self.values):
            tk.Label(self, text=field).pack()

            if field == "gender":  # For gender field
                values = ["Male", "Female"]
                combo = ttk.Combobox(self, values=values)
                combo.pack()
                combo.set(value)  # Set the current value
                self.entries[field] = combo
            else:
                entry = tk.Entry(self)
                entry.insert(0, value)
                entry.pack()
                self.entries[field] = entry

        tk.Button(self, text="Update", command=self.ok).pack()

    def ok(self):
        values = [entry.get() if isinstance(entry, tk.Entry) else entry.get() for entry in self.entries.values()]
        set_clause = ', '.join([f"{field} = %s" for field in self.fields])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.table_name}_id = %s;"
        success = DatabaseManager().execute_query(query, tuple(values + [self.primary_key]))
        if success:
            messagebox.showinfo("Success", f"Update in {self.table_name} successful.")
            self.destroy()
        else:
            messagebox.showerror("Error", f"Update in {self.table_name} failed.")



class SearchDialog(tk.Toplevel):
    def __init__(self, parent, table_name):
        super().__init__(parent)
        self.transient(parent)
        self.title("Search Data")
        self.result = None
        self.table_name = table_name
        self.fields = self.get_columns(table_name)
        self.entries = {}
        self.create_widgets()

    def get_columns(self, table_name):
        # Include your implementation of fetching columns for the specified table
        db_manager = DatabaseManager()
        db_manager.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = [col[0] for col in db_manager.cursor.fetchall()]
        return columns

    def create_widgets(self):
        tk.Label(self, text="Search data for table: " + self.table_name).pack()

        for field in self.fields:
            tk.Label(self, text=field).pack()
            entry = tk.Entry(self)
            entry.pack()
            self.entries[field] = entry

        tk.Button(self, text="Search", command=self.ok).pack()

    def apply(self):
        conditions = [f"{field} = %s" for field in self.fields if self.entries[field].get()]
        where_clause = ' AND '.join(conditions)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause};"
        parameters = tuple(entry.get() for entry in self.entries.values() if entry.get())
        data = DatabaseManager().fetch_data(query, parameters)
        self.master.display_data(data)

    def ok(self):
        self.apply()
        self.destroy()


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Database Management")
        self.geometry("800x600")
        self.current_table = "student"  # 选择 c 表进行显示
        self.tables = {}  # 存储每个表格的引用
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(fill="both", expand=True)

        self.tab_student = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_student, text="student")
        self.create_table(self.tab_student, "student")

        self.tab_course = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_course, text="course")
        self.create_table(self.tab_course, "course")

        self.tab_sc = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_sc, text="student_course")
        self.create_table(self.tab_sc, "student_course")

        self.tabControl.bind("<<NotebookTabChanged>>", self.on_table_select)

    def create_table(self, parent, table_name):
        columns = self.get_columns(table_name)
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.pack(side="left", fill="y")

        scroll_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scroll_y.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll_y.set)

        tree.bind("<ButtonRelease-1>", self.on_item_select)

        self.tables[table_name] = tree  # 存储表格引用

        self.insert_button = ttk.Button(parent, text="Insert", command=lambda: self.show_insert_dialog(table_name))
        self.insert_button.pack(pady=5)
        self.delete_button = ttk.Button(parent, text="Delete", command=lambda: self.delete_item())
        self.delete_button.pack(pady=5)
        self.update_button = ttk.Button(parent, text="Update", command=lambda: self.show_update_dialog(table_name))
        self.update_button.pack(pady=5)
        self.search_button = ttk.Button(parent, text="Search", command=lambda: self.show_search_dialog(table_name))
        self.search_button.pack(pady=5)

    def get_columns(self, table_name):
        db_manager = DatabaseManager()
        db_manager.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = [col[0] for col in db_manager.cursor.fetchall()]
        return columns

    def load_data(self):
        db_manager = DatabaseManager()
        query = f"SELECT * FROM {self.current_table};"
        data = db_manager.fetch_data(query)
        self.display_data(data)

    def display_data(self, data):
        tree = self.tables[self.current_table]  # 获取当前选择的表格引用
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert("", "end", values=row)

    def on_item_select(self, event):    
        selected_item = self.tables[self.current_table].selection()[0]
        print("Selected Item:", self.tables[self.current_table].item(selected_item, "values"))

    def show_insert_dialog(self, table_name):
        insert_window = InsertDialog(self, table_name)
        self.wait_window(insert_window)
        self.load_data()

    def show_update_dialog(self, table_name):
        selected_item = self.tables[self.current_table].selection()[0]
        if selected_item:
            primary_key = self.tables[self.current_table].item(selected_item, "values")[0]
            update_window = UpdateDialog(self, table_name, primary_key)
            self.wait_window(update_window)
            self.load_data()

    def show_search_dialog(self, table_name):
        search_window = SearchDialog(self, table_name)
        self.wait_window(search_window)

    def delete_item(self):
        selected_item = self.tables[self.current_table].selection()[0]
        if selected_item:
            primary_key_values = self.tables[self.current_table].item(selected_item, "values")
            primary_key_names = ["student_id", "course_id"]

            if self.current_table == "student":
                primary_key_names = ["student_id"]
                primary_key_values = primary_key_values[0]
            elif self.current_table == "course":
                primary_key_names = ["course_id"]
                primary_key_values = primary_key_values[0]

            conditions = " AND ".join([f"{name} = %s" for name in primary_key_names])
            query = f"DELETE FROM {self.current_table} WHERE {conditions};"

            success = DatabaseManager().execute_query(query, primary_key_values)
            
            if success:
                messagebox.showinfo("Success", f"Deletion from {self.current_table} successful.")
                self.load_data()
            else:
                messagebox.showerror("Error", f"Deletion from {self.current_table} failed.")



    
    # 切换表格时重新加载数据
    def on_table_select(self, event=None):
        # 获取当前选中的选项卡索引
        current_tab_index = self.tabControl.index(self.tabControl.select())

        # 获取当前选中选项卡的文本标签
        current_tab_label = self.tabControl.tab(current_tab_index, "text")
        table_name = current_tab_label
        self.current_table = table_name
        self.load_data()

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
