import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('study_abroad.db')
cursor = conn.cursor()

print("数据库检查：")
try:
    # 首先检查数据库中所有的表
    print("\n数据库中的所有表：")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if tables:
        print(f"共找到 {len(tables)} 个表")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table[0]}")
            
            # 显示每个表的结构
            print(f"   {table[0]}表结构：")
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
                
            # 如果发现用户相关的表，查询数据
            if 'user' in table[0].lower():
                print(f"   {table[0]}表中的数据：")
                try:
                    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 10")
                    data = cursor.fetchall()
                    if data:
                        print(f"   共找到 {len(data)} 条记录")
                        # 只显示部分字段，避免显示密码
                        cursor.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{table[0]}')")
                        col_names = [row[0] for row in cursor.fetchall()]
                        print(f"   字段名: {', '.join(col_names)}")
                        for row in data:
                            # 隐藏密码字段
                            display_row = []
                            for i, val in enumerate(row):
                                if 'password' in col_names[i].lower():
                                    display_row.append('********')
                                else:
                                    display_row.append(str(val))
                            print(f"   记录: {', '.join(display_row)}")
                    else:
                        print(f"   表中没有数据")
                except Exception as e:
                    print(f"   查询表数据时出错：{e}")
    else:
        print("数据库中没有表，可能需要初始化数据库")
        
except Exception as e:
    print(f"检查数据库时出错：{e}")

finally:
    conn.close()