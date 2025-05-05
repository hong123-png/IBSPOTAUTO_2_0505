import os
import pandas as pd
import datetime
from filelock import FileLock
import math
import shutil

def log_msg(file_name, msg, withLock=True):
    """将日志消息写入指定文件"""
    now = datetime.datetime.now()

    if withLock:
        # 将日志消息写入文件
        lock = lock_file(file_name)
        if lock:
            with open(file_name, "a") as f:
                f.write(str(now)+ ":" + msg + "\n")
            unlock_file(lock)
    else:
        # 如果不需要锁定文件，直接打开文件
        with open(file_name, "a") as f:
            f.write(str(now)+ ":" + msg + "\n")

def lock_file(filename):
    lock = FileLock(f"{filename}.lock")
    try:
        lock.acquire(timeout=10)  # 等待 10 秒尝试获取锁
        print(f"文件{filename}锁定成功。")
        return lock
    except Exception as e:
        print(f"锁定文件{filename}时出错: {e}")
        return None

def unlock_file(lock):
    try:
        lock.release()  # 释放锁
        print(f"文件解锁成功。")
    except Exception as e:
        print(f"解锁文件时出错: {e}")
        
def saveFailedRecord(record, excelFileDir):
    # 确保目录存在
    if not os.path.exists(excelFileDir):
        os.makedirs(excelFileDir)
    # 获取目录中所有符合命名规则的 Excel 文件名
    existing_files = [f for f in os.listdir(excelFileDir) if f.startswith("error_records_") and f.endswith(".xlsx")]
    # print("保存失败记录s1111111133333333333111ssss")
    existing_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))  # 按文件编号排序
    # print("保存失败记录s22222222222222211ssss")
    # 确定当前文件编号
    if existing_files:
        last_file = existing_files[-1]
        last_file_path = os.path.join(excelFileDir, last_file)
        # 读取最后一个文件的记录数
        try:
            df = pd.read_excel(last_file_path)
        except Exception as e:
            print(f"读取文件失败: {last_file_path}, 错误: {e}")
            df = pd.DataFrame()
    else:
        # 如果没有文件，初始化
        last_file = "error_records_1.xlsx"
        last_file_path = os.path.join(excelFileDir, last_file)
        df = pd.DataFrame()
    
    # 如果最后一个文件记录数超过 70，则创建新文件
    if len(df) >= 100:
        new_file_number = int(last_file.split('_')[-1].split('.')[0]) + 1
        new_file_name = f"error_records_{new_file_number}.xlsx"
        new_file_path = os.path.join(excelFileDir, new_file_name)
        df = pd.DataFrame()  # 初始化新文件的 DataFrame
    else:
        new_file_path = last_file_path
    
    # 将记录追加到 DataFrame
    new_record_df = pd.DataFrame([record])  # 将记录转换为 DataFrame
    df = pd.concat([df, new_record_df], ignore_index=True)

    # 保存到文件
    df.to_excel(new_file_path, index=False)
    print(f"记录已保存到: {new_file_path}")

def sanitize_folder_name(folder_name):
    # 定义非法字符
    invalid_chars = '<>:"/\\|?*'
    # 删除非法字符
    sanitized_name = ''.join(c for c in folder_name if c not in invalid_chars)
    return sanitized_name

def split_excel(input_file, records_per_file=50, output_prefix="part_"):
    """
    将大型 Excel 文件分割成多个包含固定记录数的小文件，并保留表头。

    Args:
        input_file (str): 输入的 Excel 文件路径。
        records_per_file (int): 每个输出文件包含的记录数（不包括表头）。
        output_prefix (str): 输出文件名的前缀。
    """
    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print(f"错误：文件 '{input_file}' 未找到。")
        return

    total_records = len(df)
    if total_records == 0:
        print("警告：输入文件为空，没有数据需要分割。")
        return

    num_files = math.ceil(total_records / records_per_file)
    header = list(df.columns)  # 获取表头

    output_dir = "split_files"  # 设置输出文件夹名称
    os.makedirs(output_dir, exist_ok=True)  # 创建输出文件夹，如果已存在则不报错

    # 得到文件名
    filename = os.path.basename(input_file)
    filename_without_extension = os.path.splitext(filename)[0]

    for i in range(num_files):
        start_index = i * records_per_file
        end_index = min((i + 1) * records_per_file, total_records)

        # 获取当前分割部分的数据
        df_part = df.iloc[start_index:end_index].copy()

        # 构建输出文件名
        output_file_path = os.path.join(output_dir, f"{filename_without_extension}_{output_prefix}{i+1}.xlsx")

        # 将数据写入新的 Excel 文件，包含表头
        df_part.to_excel(output_file_path, index=False, header=True)

        print(f"已创建文件: {output_file_path}，包含 {len(df_part)} 条记录。")

    print("文件分割完成！")

def split_excel2(input_file, records_per_file=50, output_prefix="part_"):
    """
    将大型 Excel 文件分割成多个包含固定记录数的小文件，并保留表头。
    确保第二列作为文本读取和写入，避免科学计数法显示。

    Args:
        input_file (str): 输入的 Excel 文件路径。
        records_per_file (int): 每个输出文件包含的记录数（不包括表头）。
        output_prefix (str): 输出文件名的前缀。
    """
    try:
        # 指定第二列 (索引为 1) 的数据类型为字符串
        df = pd.read_excel(input_file, dtype={1: str})
    except FileNotFoundError:
        print(f"错误：文件 '{input_file}' 未找到。")
        return

    total_records = len(df)
    if total_records == 0:
        print("警告：输入文件为空，没有数据需要分割。")
        return

    num_files = math.ceil(total_records / records_per_file)
    header = list(df.columns)  # 获取表头

    output_dir = "split_files"  # 设置输出文件夹名称
    os.makedirs(output_dir, exist_ok=True)  # 创建输出文件夹，如果已存在则不报错

    # 得到文件名
    filename = os.path.basename(input_file)
    filename_without_extension = os.path.splitext(filename)[0]

    for i in range(num_files):
        start_index = i * records_per_file
        end_index = min((i + 1) * records_per_file, total_records)

        # 获取当前分割部分的数据
        df_part = df.iloc[start_index:end_index].copy()

        # 构建输出文件名
        output_file_path = os.path.join(output_dir, f"{filename_without_extension}_{output_prefix}{i+1}.xlsx")

        # 将数据写入新的 Excel 文件，包含表头，并指定写入格式 (尝试保持文本格式)
        # 注意：pandas 在写入时对格式的控制有限，Excel 可能会根据内容自动调整显示格式
        df_part.to_excel(output_file_path, index=False, header=True, float_format='%.0f') # 尝试禁用浮点数的科学计数法

        print(f"已创建文件: {output_file_path}，包含 {len(df_part)} 条记录。")

    print("文件分割完成！")

def delete_empty_directory(folder_path):
    """
    检查指定文件夹下是否没有任何文件，如果是则删除该文件夹。

    Args:
        folder_path (str): 要检查的文件夹的路径。
    """
    try:
        # 使用 os.listdir() 获取文件夹中的所有条目（包括文件和子文件夹）
        items = os.listdir(folder_path)

        # 过滤出文件
        files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]

        if not files:
            # 如果文件列表为空，则说明文件夹下没有文件
            try:
                os.rmdir(folder_path)
                print(f"文件夹 '{folder_path}' 已删除 (因为不包含任何文件)。")
            except OSError as e:
                print(f"删除文件夹 '{folder_path}' 失败: {e}")
        else:
            print(f"文件夹 '{folder_path}' 包含 {len(files)} 个文件，未删除。")

    except FileNotFoundError:
        print(f"错误: 文件夹 '{folder_path}' 未找到。")
    except OSError as e:
        print(f"处理文件夹 '{folder_path}' 时发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


# 删除Pictures文件夹下空文件夹
def delete_empty_directories_in_pictures_folder():
    pathC = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.join(pathC, 'pictures')
    for dirpath, dirnames, filenames in os.walk(parent_dir):
        for dirname in dirnames:
            sub_dir_path = os.path.join(parent_dir, dirname)
            for sub_dirpath, sub_dirnames, sub_filenames in os.walk(sub_dir_path):
                for sub_dirname in sub_dirnames:
                    folder_to_check = os.path.join(parent_dir, dirname, sub_dirname)
                    delete_empty_directory(folder_to_check)


def get_free_space_c():
  """获取 C 盘的剩余空间（以 GB 为单位）。"""
  try:
    total, used, free = shutil.disk_usage('C:')
    free_gb = free // (2**30)  # 转换为 GB
    return free_gb
  except FileNotFoundError:
    return "C 盘不存在。"
  except Exception as e:
    return f"获取 C 盘剩余空间时发生错误：{e}"