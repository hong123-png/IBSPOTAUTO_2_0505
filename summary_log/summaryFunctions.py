import re
import os
from datetime import datetime
import shutil

# 如果此文件上传成功，则可以运行此函数删除所有相应过程文件，并原始文件到DNOE文件夹
def process_log_and_delete_files(log_file):
    """
    读取日志文件，检查每行的时间戳后面的数字，如果倒数第三、四、五位之和等于第一个数字，
    则删除该行末尾指定的文件。

    Args:
        log_file (str): 日志文件的路径。
    """

    # reNametheFailedFiles(log_file)

    lines_to_keep = []
    deleted_count = 0
    first_line_skipped = False

    try:
        with open(log_file, 'r') as f:
            # 跳过第一行
            for line in f:
                line = line.strip()
                if not first_line_skipped:
                    first_line_skipped = True
                    continue  # 跳过第一行
                parts = line.split()
                if len(parts) > 11:  # 确保行包含足够的数据
                    timestamp_str = parts[0] + " " + parts[1] + " " + parts[2]
                    try:
                        datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        numbers = [int(num) for num in numbers_str]
                        first_num = numbers[0]
                        third_last = numbers[-3]
                        fourth_last = numbers[-4]
                        fifth_last = numbers[-5]

                        if third_last + fourth_last + fifth_last == first_num:
                            file_to_delete = parts[11]
                            delete_done_error_file(file_to_delete, line)
                        else:
                            lines_to_keep.append(line)
                    except ValueError:
                        print(f"警告: 无法解析时间戳或数字: {line}")
                        lines_to_keep.append(line)
                else:
                    lines_to_keep.append(line)

        # 将保留的行写回日志文件 (覆盖原有内容)
        log_done_file = os.path.join(os.path.dirname(log_file),os.path.splitext(os.path.basename(log_file))[0]+"_s.log")
        with open(log_done_file, 'w') as f:
            for line in lines_to_keep:
                f.write(line + '\n')

        print(f"\n处理完成。共删除了 {deleted_count} 个文件。")

    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")

def delete_done_error_file(file_to_delete, line):
    result = True
    fileDir = os.path.dirname(file_to_delete)
    fileName = os.path.basename(file_to_delete)
    fileNameWithoutExtension = os.path.splitext(fileName)[0]
    file_to_delete = os.path.join(fileDir, "IBA_DONE4_IBA_DONE3_" + fileName)
    if os.path.exists(file_to_delete):
        try:
            os.remove(file_to_delete)
            print(f"已删除文件: {file_to_delete} (根据日志行: {line})")
        except OSError as e:
            print(f"删除文件 '{file_to_delete}' 失败: {e}")
    else:
        print(f"警告: 文件 '{file_to_delete}' 不存在 (根据日志行: {line})\n")
    
    Current_path = os.path.dirname(os.path.abspath(__file__))
    Parent_path = os.path.dirname(Current_path)
    folder_to_delete = os.path.join(Parent_path, "pictures", fileNameWithoutExtension)
    # delect folder and file/folders in this folder
    if os.path.exists(folder_to_delete):
        try:
            shutil.rmtree(folder_to_delete)
            print(f"已删除文夹: {folder_to_delete} (根据日志行: {line})")
        except OSError as e:
            print(f"删除文件 '{folder_to_delete}' 失败: {e}")
    file_to_delete = os.path.join(Parent_path, "untreated", "IBA_DONE_" + fileName)
    if os.path.exists(file_to_delete):
        try:
            os.remove(file_to_delete)
            print(f"已删除文件: {file_to_delete} (根据日志行: {line})")
        except OSError as e:
            print(f"删除文件 '{file_to_delete}' 失败: {e}")
    else:
        print(f"警告: 文件 '{file_to_delete}' 不存在 (根据日志行: {line})")

    file_to_delete = os.path.join(Parent_path, "untreated_a1", "IBA_DONE_" + fileName)
    if os.path.exists(file_to_delete):
        try:
            os.remove(file_to_delete)
            print(f"已删除文件: {file_to_delete} (根据日志行: {line})")
        except OSError as e:
            print(f"删除文件 '{file_to_delete}' 失败: {e}")
    else:
        print(f"警告: 文件 '{file_to_delete}' 不存在 (根据日志行: {line})")

    file_to_move = os.path.join(Parent_path, "untreated", "IBA_DONE_" + fileNameWithoutExtension+".xlsx")
    if os.path.exists(file_to_move):
        try:
            if not os.path.exists(os.path.join(Parent_path, "untreated","DONE")):
                os.makedirs(os.path.join(Parent_path, "untreated","DONE"))
            if os.path.exists(os.path.join(Parent_path, "untreated", "DONE","IBA_DONE_" + fileNameWithoutExtension+".xlsx")):
                os.remove(os.path.join(Parent_path, "untreated", "DONE","IBA_DONE_" + fileNameWithoutExtension+".xlsx"))
            shutil.move(file_to_move, os.path.join(Parent_path, "untreated","DONE"))

            print(f"已移动文件: {file_to_delete} (根据日志行: {line})")
        except OSError as e:
            print(f"移动文件 '{file_to_delete}' 失败: {e}")
    else:
        print(f"警告: 文件 '{file_to_delete}' 不存在 (根据日志行: {line})")
    
    return result

# 日上传 Listing 总数量
def sum_of_success_numbers(log_file):
    """
    读取日志文件，跳过第一行（标题），计算每行中倒数第三个数字的总和。
    跳过格式不正确的行。

    Args:
        log_file (str): 日志文件的路径。

    Returns:
        int: 所有行倒数第三个数字的总和。如果文件为空或没有符合格式的行，则返回 0。
    """
    total_sum = 0
    line_count = 0
    first_line_skipped = False

    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not first_line_skipped:
                    first_line_skipped = True
                    continue  # 跳过第一行

                parts = line.split()
                # print(parts)
                if len(parts) > 11:  # 确保行包含足够的数据来提取倒数第三个数字
                    try:
                        numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        numbers = [int(num) for num in numbers_str]
                        # print(numbers_str)
                        # print(numbers)
                        if len(numbers) >= 3:
                            third_last_num = numbers[-3]
                            total_sum += third_last_num
                            line_count += 1
                        else:
                            print(f"警告: 行 '{line}' 包含的数字少于 3 个，无法提取倒数第三个数字。")
                    except ValueError:
                        print(f"警告: 行 '{line}' 中包含非数字字符，无法进行计算。")
                    except IndexError:
                        print(f"警告: 行 '{line}' 的数字部分索引超出范围。")
                else:
                    print(f"警告: 行 '{line}' 的格式不符合预期，无法提取数字。")

    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
        return 0
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")
        return 0

    print(f"\n已处理 {line_count} 行（跳过了第一行），今日总成功上传数量为: {total_sum}")
    return total_sum

# 得到上传失败的数量，包括没有图片的和过程中未知错误失败的
def getFailedUploadingCount(log_file):
    total_sum = 0
    line_count = 0
    first_line_skipped = False
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not first_line_skipped:
                    first_line_skipped = True
                    continue  # 跳过第一行

                parts = line.split()

                if len(parts) > 11:  # 确保行包含足够的数据来提取倒数第三个数字
                    try:
                        numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        numbers = [int(num) for num in numbers_str]

                        if len(numbers) >= 3:
                            first_last_num = numbers[-1]
                            second_last_num = numbers[-2]
                            total_sum += (first_last_num + second_last_num)
                            line_count += 1
                        else:
                            print(f"警告: 行 '{line}' 包含的数字少于 3 个，无法提取倒数第三个数字。")
                    except ValueError:
                        print(f"警告: 行 '{line}' 中包含非数字字符，无法进行计算。")
                    except IndexError:
                        print(f"警告: 行 '{line}' 的数字部分索引超出范围。")
                else:
                    print(f"警告: 行 '{line}' 的格式不符合预期，无法提取数字。")

    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
        return 0
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")
        return 0

    print(f"\n已处理 {line_count} 行（跳过了第一行），今日总失败上传数量为: {total_sum}")
    return total_sum

def reUploadFailedRecordsAgain(log_file):
    total_sum = 0
    line_count = 0
    first_line_skipped = False
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not first_line_skipped:
                    first_line_skipped = True
                    continue  # 跳过第一行

                parts = line.split()

                if len(parts) > 11:  # 确保行包含足够的数据来提取倒数第三个数字
                    try:
                        file_path = parts[-1]
                        noPicNum = int(parts[-2])
                        failedNum = int(parts[-3])
                        
                        #numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        #numbers = [int(num) for num in numbers_str]
                        
                        print(failedNum)
                        print(noPicNum)
                        print(file_path)
                        if (failedNum+noPicNum) == 0:
                            continue
                        if noPicNum > 0:
                            print('把 DONE4, DONE3都去掉，从新下载一次图片，然后载上传')
                        else:
                            if failedNum > 0:
                                print('把 DONE4 去掉，重新上传')

                        """
                        if len(numbers) >= 3:
                            first_last_num = numbers[-1]
                            second_last_num = numbers[-2]
                            total_sum += (first_last_num + second_last_num)
                            line_count += 1
                            
                            if first_last_num == 0:
                                if second_last_num > 0:
                                    # 把 DONE4 去掉，重新上传
                            else: # 图片没下载完全
                                # 把 DONE4, DONE3都去掉，从新下载一次图片，然后载上传
                        
                        else:
                            print(f"警告: 行 '{line}' 包含的数字少于 3 个，无法提取倒数第三个数字。")
                        """
                    except ValueError:
                        print(f"警告: 行 '{line}' 中包含非数字字符，无法进行计算。")
                    except IndexError:
                        print(f"警告: 行 '{line}' 的数字部分索引超出范围。")
                else:
                    print(f"警告: 行 '{line}' 的格式不符合预期，无法提取数字。")

    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
        return 0
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")
        return 0

    print(f"\n已处理 {line_count} 行（跳过了第一行），今日总成功上传数量为: {total_sum}")
    return total_sum

def reNametheFailedFiles(log_file):
    """
    读取日志文件，检查每行的时间戳后面的数字，如果倒数第三、四、五位之和不等于第一个数字，
    则删根据倒数第一个数字和倒数第二个数字的情况修改文件名。

    Args:
        log_file (str): 日志文件的路径。
    """
    first_line_skipped = False

    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not first_line_skipped:
                    first_line_skipped = True
                    continue  # 跳过第一行

                parts = line.split()
                if len(parts) > 11:  # 确保行包含足够的数据来提取倒数第三个数字
                    try:
                        numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        numbers = [int(num) for num in numbers_str]
                        noPicNum = numbers[-1]
                        failedNum = numbers[-2]
                        if failedNum + noPicNum > 0:
                            filePath = parts[11]
                            fileDir = os.path.dirname(filePath)
                            fileName = os.path.basename(filePath)
                            fileNameWithoutExtension = os.path.splitext(fileName)[0]
                            file_to_rename = os.path.join(fileDir, "IBA_DONE4_IBA_DONE3_" + fileName)
                            if os.path.exists(file_to_rename):
                                if failedNum > 0:
                                    print('把 DONE4 去掉，重新上传')
                                    os.rename(file_to_rename, os.path.join(fileDir, "IBA_DONE3_" + fileName))
                                elif noPicNum > 0:
                                    print('把 DONE4, DONE3都去掉，从新下载一次图片，然后载上传')
                                    os.rename(file_to_rename, os.path.join(fileDir, fileName))
                                print(f"已重命名文件: {file_to_rename} (根据日志行: {line})")
                            else:
                                if os.path.exists( os.path.join(fileDir, fileName)) or os.path.exists( os.path.join(fileDir, "IBA_DONE3_" + fileName)):
                                    print(f"已重命名文件: {file_to_rename} (根据日志行: {line})")
                                else:
                                    print(f"【【【警告】】】: 文件 '{file_to_rename}' 不存在 (根据日志行: {line})\n")
                                    delete_done_error_file(filePath, line)
                    except ValueError:
                        print(f"警告: 行 '{line}' 中包含非数字字符，无法进行计算。")
                    except IndexError:
                        print(f"警告: 行 '{line}' 的数字部分索引超出范围。")
                else:
                    print(f"警告: 行 '{line}' 的格式不符合预期，无法提取数字。")
    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
        return 0
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")
        return 0

def delete_done_files_and_rename_failed_files(log_file):
    process_log_and_delete_files(log_file)
    reNametheFailedFiles(log_file)

def delete_done_files_before_n_days(log_file, days = 10):
    """
    删除指定天数之前的文件。

    Args:
        log_file (str): 日志文件的路径。
        days (int): 指定的天数。
    """
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                parts = line.split()
                if len(parts) > 11:  # 确保行包含足够的数据来提取时间戳
                    filePath = parts[11]
                    fileName = os.path.basename(filePath)
                    # fileName 类似于这样的格式：2025-05-01-13-15-20C_mars+made+shampoo+bar.csv， 得到文件名当中的时间戳
                    match = re.search(r'(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})', fileName)
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S')
                            if (datetime.now() - timestamp).days > days:
                                file_to_delete = parts[11]
                                delete_done_error_file(file_to_delete, line)
                                print(f"已删除文件: {file_to_delete} 及其相关文件 (根据日志行: {line})")
                        except ValueError:
                            print(f"警告：无法将提取到的字符串 '{timestamp_str}' 解析为日期时间，删除指定天数{days}之前的DONE文件失败。")
                            return None
                    else:
                        print(f"警告：文件名 '{fileName}' 中未找到符合 'YYYY-MM-DD-HH-MM-SS' 格式的时间戳。")
                        return None
    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")

def delete_done_files_with_fail_rate(log_file, fail_rate = 0.05):
    """
    删除失败率比较低的文件

    Args:
        log_file (str): 日志文件的路径。
        fail_rate (float): 指定的天数。
    """
    if fail_rate < 0 or fail_rate > 0.1:
        print("错误: 失败率必须在 0 到 0.1 之间。")
        return
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                parts = line.split()
                if len(parts) > 11:  # 确保行包含足够的数据来提取时间戳
                    try:
                        numbers_str = parts[3:11]  # 提取时间戳后面的9个数字字符串
                        numbers = [int(num) for num in numbers_str]
                        first_num = numbers[0]
                        noPicNum = numbers[-1]
                        failedNum = numbers[-2]
                        # third_last = numbers[-3]
                        # fourth_last = numbers[-4]
                        # fifth_last = numbers[-5]
                        if (noPicNum + failedNum) / first_num <= fail_rate:
                            file_to_delete = parts[11]
                            delete_done_error_file(file_to_delete, line)
                    except ValueError:
                        print(f"警告: 行 '{line}' 中包含非数字字符，无法进行计算。 删除小于指定失败率的文件失败。")
                    except IndexError:
                        print(f"警告: 行 '{line}' 的数字部分索引超出范围。") 
    except FileNotFoundError:
        print(f"错误: 日志文件 '{log_file}' 未找到。")
    except Exception as e:
        print(f"处理日志文件时发生错误: {e}")

if __name__ == "__main__":
    Current_path = os.path.dirname(os.path.abspath(__file__))
    log_file_path = 'summary2025-05-02.log'  # 替换为您的日志文件路径
    log_file_path = os.path.join(Current_path, log_file_path)
    # print(log_file_path)

    # 计算成功上传的数量 和 失败的数量
    sum_of_success_numbers(log_file_path)
    getFailedUploadingCount(log_file_path)

    # 删除指定天数之前的文件（默认10天）
    # delete_done_files_before_n_days(log_file_path, 10)

    # # 删除失败率比较低的文件（默认0.05）
    # # delete_done_files_with_fail_rate(log_file_path, 0.05)

    # # 删除完全处理好的文件 并修改运行有失败的文件名，让程序重新处理和上传
    # delete_done_files_and_rename_failed_files(log_file_path)
    
