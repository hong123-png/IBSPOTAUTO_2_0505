import os
import datetime
import pandas as pd
from globalFunctions import log_msg, split_excel2
from fileArrangeCenter import fileArrangeCenterBetweenOA

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__))+'\\log\\', 'step00'+now+'.log')  # 日志文件路径
print('====================== step00程序开始运行 ======================')
log_msg(log_file, "step00程序开始运行")

if __name__ == "__main__":
    CurrentPath = os.path.dirname(os.path.abspath(__file__))
    Step00Path = os.path.join(CurrentPath, 'Step00')
    # 检查 Step00 文件夹是否存在
    if not os.path.exists(Step00Path):
        print(f"Step00 文件夹不存在: {Step00Path}")
        log_msg(log_file, f"Step00 文件夹不存在: {Step00Path}")
        exit(1)
    # 遍历 Step00 文件夹下
    for file_name in os.listdir(Step00Path):
        # 检查文件名是否以 .xlsx 结尾
        if file_name.endswith('.xlsx'):
            # 构造文件的完整路径
            file_path = os.path.join(Step00Path, file_name)
            # 获取文件的行数
            df = pd.read_excel(file_path)
            line_count = len(df)
            print(f"文件 {file_name} 共有 {line_count} 行")
            # 拆分文件 文件中的数据可能过多，如果数据行数大于50，则拆分为多个文件，每个文件不超过50行
            if line_count >50:
                split_excel2(file_path,output_dir="Step00")
                # 原始文件移动到 Step00/Done 文件夹
                # 检查 Step00/Done 文件夹是否存在
                DonePath = os.path.join(Step00Path, 'Done')
                if not os.path.exists(DonePath):
                    os.makedirs(DonePath)
                os.rename(file_path, os.path.join(Step00Path, 'Done', file_name))
                print(f"文件 {file_name} 已移动到 Step00/Done 文件夹")
            else:
                # 调用 fileArrangeCenterBetweenOA 函数获取目标路径
                move_to_path = fileArrangeCenterBetweenOA()
                if move_to_path:
                    # 移动文件到目标路径
                    os.rename(file_path, os.path.join(move_to_path, file_name))
                    print(f"文件 {file_name} 已移动到 {move_to_path}")
                    log_msg(log_file, f"文件 {file_name} 已移动到 {move_to_path}")

    log_msg(log_file, "Step00程序执行完毕")
    print("====================== Step00程序执行完毕 ======================")