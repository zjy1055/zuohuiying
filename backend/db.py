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
            
            # 获取表数据
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000;")  # 限制显示前1000行
            rows = cursor.fetchall()
            
            # 插入数据
            for row in rows:
                values = [row[col] for col in columns]
                self.tree.insert('', tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("错误", f"加载表数据失败: {str(e)}")
    
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
                    self.tree.insert('', tk.END, values=row)
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
                    result_tree.insert('', tk.END, values=row)
            else:
                # 对于非SELECT语句，提交更改
                self.connection.commit()
                messagebox.showinfo("成功", f"查询执行成功，影响了 {cursor.rowcount} 行")
            
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"查询执行失败: {str(e)}")
    
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