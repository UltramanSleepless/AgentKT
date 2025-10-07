# import os
# import csv
# import sys
# from tqdm import tqdm

# def get_code_content(problem_id, submission_id, language, codenet_data_dir):
#     """根据problem_id, submission_id, language从Project_CodeNet/data获取代码内容"""
#     # 构建文件路径：data/pXXXXX/Language/sXXXXXXXXX.ext
#     problem_dir = os.path.join(codenet_data_dir, problem_id)
#     if not os.path.exists(problem_dir):
#         return ""
    
#     # 直接查找对应的语言目录
#     lang_path = os.path.join(problem_dir, language)
#     if not os.path.exists(lang_path):
#         return ""
    
#     # 查找提交文件
#     for filename in os.listdir(lang_path):
#         if filename.startswith(submission_id + "."):
#             file_path = os.path.join(lang_path, filename)
#             try:
#                 with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                     return f.read()
#             except:
#                 try:
#                     with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
#                         return f.read()
#                 except:
#                     return ""
#     return ""

# # 主处理逻辑
# if len(sys.argv) < 2:
#     print("用法: python script.py <target_language>")
#     print("例如: python script.py Python")
#     sys.exit(1)

# target_language = sys.argv[1]
# userdata_dir = "/data2/liyu/KT/OKT/Project_CodeNet/userdata"
# codenet_data_dir = "/data2/liyu/KT/OKT/Project_CodeNet/data"

# lang_path = os.path.join(userdata_dir, target_language)
# if not os.path.exists(lang_path):
#     print(f"语言目录不存在: {target_language}")
#     sys.exit(1)

# print(f"处理语言: {target_language}")

# # 获取所有用户CSV文件列表
# user_files = [f for f in os.listdir(lang_path) if f.endswith('.csv')]
# print(f"找到 {len(user_files)} 个用户文件")

# # 使用tqdm显示进度条
# for user_file in tqdm(user_files, desc=f"处理{target_language}用户", unit="用户"):
#     user_csv_path = os.path.join(lang_path, user_file)
    
#     # 读取原CSV
#     rows = []
#     with open(user_csv_path, 'r', newline='', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         rows = list(reader)
    
#     if not rows:
#         continue
        
#     header = rows[0]
#     # 添加新列
#     header.append('code_content')
    
#     # 处理数据行
#     for i in range(1, len(rows)):
#         row = rows[i]
#         if len(row) < 6:  # 确保有足够的列
#             row.extend([''] * (6 - len(row)))
        
#         # 提取关键信息：submission_id(0), problem_id(1), language(4)
#         submission_id = row[0]
#         problem_id = row[1] 
#         language = row[4]
        
#         # 获取代码内容
#         code_content = get_code_content(problem_id, submission_id, language, codenet_data_dir)
#         row.append(code_content)
    
#     # 写回CSV
#     with open(user_csv_path, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)

# print(f"完成！{target_language}语言下所有用户CSV已添加代码内容列")




"""
多线程版本
"""
import os
import csv
import sys
from tqdm import tqdm

# 增加CSV字段大小限制
csv.field_size_limit(1000000)

def get_code_content(problem_id, submission_id, language, codenet_data_dir):
    """根据problem_id, submission_id, language从Project_CodeNet/data获取代码内容"""
    # 构建文件路径：data/pXXXXX/Language/sXXXXXXXXX.ext
    problem_dir = os.path.join(codenet_data_dir, problem_id)
    if not os.path.exists(problem_dir):
        return ""
    
    # 直接查找对应的语言目录
    lang_path = os.path.join(problem_dir, language)
    if not os.path.exists(lang_path):
        return ""
    
    # 查找提交文件
    for filename in os.listdir(lang_path):
        if filename.startswith(submission_id + "."):
            file_path = os.path.join(lang_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                try:
                    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                        return f.read()
                except:
                    return ""
    return ""

# 主处理逻辑
if len(sys.argv) < 2:
    print("用法: python script.py <target_language>")
    print("例如: python script.py Python")
    sys.exit(1)

target_language = sys.argv[1]
userdata_dir = "/data2/liyu/KT/OKT/Project_CodeNet/userdata"
codenet_data_dir = "/data2/liyu/KT/OKT/Project_CodeNet/data"

lang_path = os.path.join(userdata_dir, target_language)
if not os.path.exists(lang_path):
    print(f"语言目录不存在: {target_language}")
    sys.exit(1)

print(f"处理语言: {target_language}")

# 获取所有用户CSV文件列表
user_files = [f for f in os.listdir(lang_path) if f.endswith('.csv')]
print(f"找到 {len(user_files)} 个用户文件")

# 使用tqdm显示进度条
for user_file in tqdm(user_files, desc=f"处理{target_language}用户", unit="用户"):
    user_csv_path = os.path.join(lang_path, user_file)
    
    # 读取原CSV
    rows = []
    with open(user_csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        continue
        
    header = rows[0]
    # 添加新列
    header.append('code_content')
    
    # 处理数据行
    for i in range(1, len(rows)):
        row = rows[i]
        if len(row) < 6:  # 确保有足够的列
            row.extend([''] * (6 - len(row)))
        
        # 提取关键信息：submission_id(0), problem_id(1), language(4)
        submission_id = row[0]
        problem_id = row[1] 
        language = row[4]
        
        # 获取代码内容
        code_content = get_code_content(problem_id, submission_id, language, codenet_data_dir)
        row.append(code_content)
    
    # 写回CSV
    with open(user_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

print(f"完成！{target_language}语言下所有用户CSV已添加代码内容列")