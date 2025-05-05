import os
import datetime
from globalFunctions import log_msg
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
            file_path = os.path.join(Step00Path, file_name)
            move_to_path = fileArrangeCenterBetweenOA()
            if move_to_path:
                # 移动文件到目标路径
                os.rename(file_path, os.path.join(move_to_path, file_name))
                print(f"文件 {file_name} 已移动到 {move_to_path}")
                log_msg(log_file, f"文件 {file_name} 已移动到 {move_to_path}")

    log_msg(log_file, "Step00程序执行完毕")
    print("====================== Step00程序执行完毕 ======================")