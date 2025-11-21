import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

class SQLiteVisualizer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.current_table = None
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title(f"SQLite数据库可视化 - {os.path.basename(db_path)}")
        self.root.geometry("1200x800")
        
        # 创建菜单
        self.create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧表列表框架
        left_frame = ttk.LabelFrame(main_frame, text="数据库表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 表列表
        self.table_listbox = tk.Listbox(left_frame)
        self.table_listbox.pack(fill=tk.BOTH, expand=True)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # 右侧数据展示框架
        right_frame = ttk.LabelFrame(main_frame, text="表数据", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建一个标签来显示当前表名
        self.table_label = ttk.Label(right_frame, text="选择一个表以查看数据", font=("SimHei", 12, "bold"))
        self.table_label.pack(fill=tk.X, pady=5)
        
        # 创建操作按钮区域
        self.button_frame = ttk.Frame(right_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # 添加增删改查按钮
        self.add_button = ttk.Button(self.button_frame, text="添加记录", command=self.add_record_dialog)
        self.add_button.pack(side=tk.LEFT, padx=2)
        
        self.edit_button = ttk.Button(self.button_frame, text="编辑记录", command=self.edit_record_dialog)
        self.edit_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_button = ttk.Button(self.button_frame, text="删除记录", command=self.delete_record)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        self.refresh_button = ttk.Button(self.button_frame, text="刷新数据", command=self.refresh_data)
        self.refresh_button.pack(side=tk.LEFT, padx=2)
        
        # 创建搜索框
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=2)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.search_button = ttk.Button(search_frame, text="查找", command=self.search_data)
        self.search_button.pack(side=tk.LEFT, padx=2)
        
        self.clear_search_button = ttk.Button(search_frame, text="清除", command=self.clear_search)
        self.clear_search_button.pack(side=tk.LEFT, padx=2)
        
        # 查询框架
        query_frame = ttk.Frame(right_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(query_frame, text="SQL查询:").pack(side=tk.LEFT)
        self.query_entry = ttk.Entry(query_frame, width=70)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.query_entry.bind('<Return>', self.execute_query)
        
        ttk.Button(query_frame, text="执行", command=self.execute_query).pack(side=tk.RIGHT)
        
        # 数据表格框架
        table_frame = ttk.Frame(right_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview和滚动条
        self.tree = ttk.Treeview(table_frame)
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 连接数据库
        self.connect_db()
        # 加载表列表
        self.load_tables()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开数据库", command=self.open_database)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据", menu=data_menu)
        data_menu.add_command(label="执行SQL", command=self.execute_sql_dialog)
        data_menu.add_command(label="导出数据", command=self.export_data)
        data_menu.add_command(label="添加记录", command=self.add_record_dialog)
        data_menu.add_command(label="编辑记录", command=self.edit_record_dialog)
        data_menu.add_command(label="删除记录", command=self.delete_record)
        
    def connect_db(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到数据库: {str(e)}")
            self.root.destroy()
    
    def load_tables(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.table_listbox.delete(0, tk.END)
            for table in tables:
                self.table_listbox.insert(tk.END, table[0])
        except Exception as e:
            messagebox.showerror("错误", f"加载表列表失败: {str(e)}")
    
    def on_table_select(self, event):
        selection = self.table_listbox.curselection()
        if selection:
            table_name = self.table_listbox.get(selection[0])
            self.current_table = table_name
            self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        try:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取表结构
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            
            # 设置列标题
            columns = [col[1] for col in columns_info]
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor=tk.W)
            
            # 获取表数据 - 移除LIMIT限制，显示所有数据
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # 插入数据
            for row in rows:
                # 确保将sqlite3.Row对象转换为元组，以便正确显示值
                if isinstance(row, sqlite3.Row):
                    # 对于Row对象，提取其所有值
                    row_values = tuple(row)
                else:
                    row_values = row
                self.tree.insert('', tk.END, values=row_values)
                
            # 更新标签，显示记录数量
            self.table_label.config(text=f"表: {table_name} (共{len(rows)}条记录)")
            self.current_table = table_name
                
        except Exception as e:
            messagebox.showerror("错误", f"加载表数据失败: {str(e)}")
    
    def refresh_data(self):
        # 刷新当前表的数据
        if hasattr(self, 'current_table') and self.current_table:
            self.load_table_data(self.current_table)
        else:
            messagebox.showinfo("信息", "请先选择一个表")
    
    def search_data(self):
        # 搜索数据
        if not hasattr(self, 'current_table') or not self.current_table:
            messagebox.showinfo("信息", "请先选择一个表")
            return
        
        search_text = self.search_entry.get().strip()
        if not search_text:
            messagebox.showinfo("信息", "请输入搜索内容")
            return
        
        try:
            # 获取当前表的所有列
            columns = self.tree['columns']
            if not columns:
                messagebox.showinfo("信息", "没有可搜索的列")
                return
            
            # 构建搜索条件（在所有列中搜索）
            search_conditions = []
            params = {}
            
            for i, col in enumerate(columns):
                search_conditions.append(f"{col} LIKE :search{i}")
                params[f"search{i}"] = f"%{search_text}%"
            
            where_clause = " OR ".join(search_conditions)
            sql = f"SELECT * FROM {self.current_table} WHERE {where_clause}"
            
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # 清空当前表格并显示搜索结果
            self.tree.delete(*self.tree.get_children())
            
            # 确保将sqlite3.Row对象转换为元组，以便正确显示值
            for row in rows:
                if isinstance(row, sqlite3.Row):
                    # 对于Row对象，提取其所有值
                    row_values = tuple(row)
                else:
                    row_values = row
                self.tree.insert('', tk.END, values=row_values)
                
            messagebox.showinfo("搜索结果", f"找到 {len(rows)} 条匹配记录")
                
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")
    
    def clear_search(self):
        # 清除搜索内容并重新加载全部数据
        self.search_entry.delete(0, tk.END)
        self.refresh_data()
    
    def execute_query(self, event=None):
        query = self.query_entry.get().strip()
        if not query:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                # 清空现有数据
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # 获取列名
                columns = [description[0] for description in cursor.description]
                self.tree['columns'] = columns
                self.tree['show'] = 'headings'
                
                for col in columns:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, width=100, anchor=tk.W)
                
                # 插入数据
                rows = cursor.fetchall()
                for row in rows:
                    # 确保将sqlite3.Row对象转换为元组，以便正确显示值
                    if isinstance(row, sqlite3.Row):
                        row_values = tuple(row)
                    else:
                        row_values = row
                    self.tree.insert('', tk.END, values=row_values)
            else:
                # 对于非SELECT语句，提交更改
                self.connection.commit()
                messagebox.showinfo("成功", f"查询执行成功，影响了 {cursor.rowcount} 行")
                
        except Exception as e:
            messagebox.showerror("错误", f"查询执行失败: {str(e)}")
    
    def execute_sql_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("执行SQL")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="请输入SQL语句:").pack(anchor=tk.W)
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="执行", 
                  command=lambda: self.execute_sql_from_dialog(text_widget, dialog)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
    
    def execute_sql_from_dialog(self, text_widget, dialog):
        query = text_widget.get("1.0", tk.END).strip()
        if not query:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                # 在新窗口中显示结果
                result_window = tk.Toplevel(self.root)
                result_window.title("查询结果")
                result_window.geometry("800x600")
                
                result_frame = ttk.Frame(result_window)
                result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                result_tree = ttk.Treeview(result_frame)
                v_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_tree.yview)
                h_scrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=result_tree.xview)
                
                result_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
                
                v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                # 设置列标题
                columns = [description[0] for description in cursor.description]
                result_tree['columns'] = columns
                result_tree['show'] = 'headings'
                
                for col in columns:
                    result_tree.heading(col, text=col)
                    result_tree.column(col, width=100, anchor=tk.W)
                
                # 插入数据
                rows = cursor.fetchall()
                for row in rows:
                    # 确保将sqlite3.Row对象转换为元组，以便正确显示值
                    if isinstance(row, sqlite3.Row):
                        row_values = tuple(row)
                    else:
                        row_values = row
                    result_tree.insert('', tk.END, values=row_values)
            else:
                # 对于非SELECT语句，提交更改
                self.connection.commit()
                messagebox.showinfo("成功", f"查询执行成功，影响了 {cursor.rowcount} 行")
            
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"查询执行失败: {str(e)}")
    
    def edit_record_dialog(self):
        # 检查是否选择了表
        selection = self.table_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个表")
            return
        
        table_name = self.table_listbox.get(selection[0])
        
        # 检查是否选择了要编辑的记录
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一条要编辑的记录")
            return
        
        # 只处理第一条选择的记录
        item = selected_items[0]
        
        # 获取选中记录的数据
        item_data = self.tree.item(item, "values")
        columns = self.tree['columns']
        
        # 获取表结构
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(f"编辑记录 - {table_name}")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建滚动框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 存储输入框的字典和主键信息
        entry_fields = {}
        primary_key = {}
        
        # 创建每个字段的标签和输入框
        for col_info in columns_info:
            col_name = col_info[1]
            col_type = col_info[2]
            not_null = col_info[3]
            is_pk = col_info[5]
            
            # 查找字段在当前数据中的索引
            if col_name in columns:
                col_index = columns.index(col_name)
                current_value = item_data[col_index] if col_index < len(item_data) else ""
            else:
                current_value = ""
            
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # 标签显示字段名，标记非空字段
            label_text = f"{col_name} ({col_type})"
            if not_null:
                label_text += " *"
            if is_pk:
                label_text += " [主键]"
            
            ttk.Label(frame, text=label_text, width=20).pack(side=tk.LEFT, padx=5)
            
            # 对于主键，显示但不允许编辑
            if is_pk:
                ttk.Label(frame, text=str(current_value), width=40, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                primary_key[col_name] = current_value
            else:
                # 创建可编辑的输入框
                entry = ttk.Entry(frame, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                if current_value is not None:
                    entry.insert(0, str(current_value))
                entry_fields[col_name] = (entry, not_null)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 确认按钮
        ttk.Button(button_frame, text="保存", 
                  command=lambda: self.update_record(table_name, entry_fields, primary_key, dialog)).pack(side=tk.LEFT)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
    
    def update_record(self, table_name, entry_fields, primary_key, dialog):
        # 验证非空字段
        values = {}
        for col_name, (entry, not_null) in entry_fields.items():
            value = entry.get().strip()
            if not_null and not value:
                messagebox.showerror("错误", f"字段 '{col_name}' 不能为空")
                return
            values[col_name] = value if value else None
        
        try:
            # 构建WHERE条件（使用主键）
            where_clauses = [f"{col} = :{col}_pk" for col in primary_key.keys()]
            where_sql = " AND ".join(where_clauses)
            
            # 构建更新SQL
            set_clauses = [f"{col} = :{col}" for col in values.keys()]
            set_sql = ", ".join(set_clauses)
            
            sql = f"UPDATE {table_name} SET {set_sql} WHERE {where_sql}"
            
            # 准备参数（包含主键值和更新值）
            params = values.copy()
            for col, val in primary_key.items():
                params[f"{col}_pk"] = val
            
            # 执行更新
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("成功", "记录更新成功")
                # 刷新表格数据
                if self.current_table == table_name:
                    self.load_table_data(table_name)
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "未找到要更新的记录")
                
        except Exception as e:
            messagebox.showerror("错误", f"更新记录失败: {str(e)}")
    
    def delete_record(self):
        # 检查是否选择了表
        selection = self.table_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个表")
            return
        
        table_name = self.table_listbox.get(selection[0])
        
        # 检查是否选择了要删除的记录
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
        
        # 获取表的主键信息
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # 找出主键列
        pk_columns = [col_info[1] for col_info in columns_info if col_info[5]]
        
        # 如果没有明确的主键，使用所有列作为条件
        if not pk_columns:
            pk_columns = [col_info[1] for col_info in columns_info]
        
        # 获取选中记录的主键值
        records_to_delete = []
        columns = self.tree['columns']
        
        for item in selected_items:
            item_data = self.tree.item(item, "values")
            pk_values = {}
            
            for pk_col in pk_columns:
                if pk_col in columns:
                    col_index = columns.index(pk_col)
                    if col_index < len(item_data):
                        pk_values[pk_col] = item_data[col_index]
                    else:
                        pk_values[pk_col] = None
                else:
                    pk_values[pk_col] = None
            
            records_to_delete.append(pk_values)
        
        # 确认删除操作
        if len(records_to_delete) == 1:
            msg = f"确定要删除这条记录吗？"
        else:
            msg = f"确定要删除这 {len(records_to_delete)} 条记录吗？"
        
        if not messagebox.askyesno("确认删除", msg):
            return
        
        # 执行删除操作
        try:
            cursor = self.connection.cursor()
            
            for pk_values in records_to_delete:
                # 构建WHERE条件
                where_clauses = []
                params = {}
                
                for col, val in pk_values.items():
                    if val is None:
                        where_clauses.append(f"{col} IS NULL")
                    else:
                        where_clauses.append(f"{col} = :{col}")
                        params[col] = val
                
                where_sql = " AND ".join(where_clauses)
                sql = f"DELETE FROM {table_name} WHERE {where_sql}"
                
                cursor.execute(sql, params)
            
            self.connection.commit()
            
            messagebox.showinfo("成功", f"成功删除 {len(records_to_delete)} 条记录")
            
            # 刷新表格数据
            if self.current_table == table_name:
                self.load_table_data(table_name)
                
        except Exception as e:
            messagebox.showerror("错误", f"删除记录失败: {str(e)}")
            self.connection.rollback()
    
    def add_record_dialog(self):
        selection = self.table_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个表")
            return
        
        table_name = self.table_listbox.get(selection[0])
        
        # 获取表结构
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(f"添加记录 - {table_name}")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建滚动框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 存储输入框的字典
        entry_fields = {}
        
        # 创建每个字段的标签和输入框
        for idx, col_info in enumerate(columns_info):
            col_name = col_info[1]
            col_type = col_info[2]
            not_null = col_info[3]
            default_val = col_info[4]
            is_pk = col_info[5]
            
            # 不允许用户编辑主键
            if is_pk:
                continue
                
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # 标签显示字段名，标记非空字段
            label_text = f"{col_name} ({col_type})"
            if not_null:
                label_text += " *"
            
            ttk.Label(frame, text=label_text, width=20).pack(side=tk.LEFT, padx=5)
            
            # 创建输入框
            entry = ttk.Entry(frame, width=40)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # 如果有默认值，显示默认值提示
            if default_val is not None:
                entry.insert(0, str(default_val))
            
            entry_fields[col_name] = (entry, not_null)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 确认按钮
        ttk.Button(button_frame, text="添加", 
                  command=lambda: self.add_record(table_name, columns_info, entry_fields, dialog)).pack(side=tk.LEFT)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
    
    def add_record(self, table_name, columns_info, entry_fields, dialog):
        # 验证非空字段
        values = {}
        for col_name, (entry, not_null) in entry_fields.items():
            value = entry.get().strip()
            if not_null and not value:
                messagebox.showerror("错误", f"字段 '{col_name}' 不能为空")
                return
            values[col_name] = value if value else None
        
        try:
            # 构建插入SQL
            fields = list(values.keys())
            placeholders = [f":{field}" for field in fields]
            
            sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            
            # 执行插入
            cursor = self.connection.cursor()
            cursor.execute(sql, values)
            self.connection.commit()
            
            messagebox.showinfo("成功", "记录添加成功")
            
            # 刷新表格数据
            if self.current_table == table_name:
                self.load_table_data(table_name)
            
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"添加记录失败: {str(e)}")
    
    def export_data(self):
        selection = self.table_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个表")
            return
        
        table_name = self.table_listbox.get(selection[0])
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="导出数据"
        )
        
        if not file_path:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            
            # 写入CSV文件
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(columns)  # 写入列名
                writer.writerows(rows)    # 写入数据
            
            messagebox.showinfo("成功", f"数据已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def open_database(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite files", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")],
            title="选择SQLite数据库文件"
        )
        
        if file_path:
            # 关闭当前连接
            if self.connection:
                self.connection.close()
            
            # 创建新的可视化器实例
            self.__init__(file_path)
    
    def run(self):
        self.root.mainloop()
    
    def __del__(self):
        if self.connection:
            self.connection.close()

def main():
    # 检查命令行参数或当前目录下的数据库文件
    db_path = None
    
    if len(sys.argv) > 1:
        # 使用命令行参数指定的数据库文件
        db_path = sys.argv[1]
    else:
        # 搜索当前目录下的SQLite数据库文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_extensions = ['.db', '.sqlite', '.sqlite3']
        
        for file in os.listdir(current_dir):
            if any(file.lower().endswith(ext) for ext in db_extensions):
                db_path = os.path.join(current_dir, file)
                break
    
    if not db_path:
        # 如果没有找到数据库文件，让用户选择
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        db_path = filedialog.askopenfilename(
            filetypes=[("SQLite files", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")],
            title="选择SQLite数据库文件"
        )
        
        root.destroy()
    
    if db_path and os.path.exists(db_path):
        app = SQLiteVisualizer(db_path)
        app.run()
    else:
        print("未找到数据库文件或文件不存在")

if __name__ == "__main__":
    main()