import os

# 当前任务计划列表
# 增加新的计划任务时： 1. 制作计划任务对应执行文件，2. 增加对应文件夹， 3. 添加计划任务 3. 在下面的列表中登记对应的计划任务
# ** 新添加的计划任务何时生效： 在前一步的计划任务新一次执行的时候才生效（所以，要么重启前一步的计划任务，要么等待前一步正在执行的计划任务结束后的下一次自动执行的时候才生效）
# untreated
StepAs = ['']
# untreated
StepBs = ['', '_a1', '_a2']
# UpLoadData
StepCs = ['', '_a1', '_a2', '_a3']
# UpLoadData
StepDs = ['', '_a1', '_a2', '_a3']

def fileArrangeCenterBetweenOA():
    CurrentPath = os.path.dirname(os.path.abspath(__file__))
    fileCountinFolder = []
    # 循环StepAs
    for stepA in StepAs:
        untreatedPath = os.path.join(CurrentPath, 'untreated'+stepA)
        # 如果untreatedPath存在，以key和value方式存储 stepA 和对应文件夹内的文件数量
        if os.path.exists(untreatedPath):
            csv_files_not_IBA_DONE = [f for f in os.listdir(untreatedPath) if f.endswith('.xlsx') and not f.startswith('IBA_DONE_')]
            print(f"untreatedPath: {untreatedPath}, csv_files_not_IBA_DONE: {len(csv_files_not_IBA_DONE)}")
            fileCountinFolder.append((stepA, len(csv_files_not_IBA_DONE)))

    # 如果 fileCountinFolder 不为空， 则获取最小值的 stepA 和文件数量
    if fileCountinFolder:
        min_stepA, min_file_count = min(fileCountinFolder, key=lambda x: x[1])
        print(f"最小文件数量的 StepA: {min_stepA}, 文件数量: {min_file_count}")
    else:
        print("没有找到符合条件的文件夹。")
        return False
    
    min_stepA_path = os.path.join(CurrentPath, 'untreated'+min_stepA)

    return min_stepA_path

def fileArrangeCenterBetweenAB():
    CurrentPath = os.path.dirname(os.path.abspath(__file__))
    fileCountinFolder = []
    # 循环StepBs
    for stepB in StepBs:
        untreatedPath = os.path.join(CurrentPath, 'untreated'+stepB)
        # 如果untreatedPath存在，以key和value方式存储 stepB 和对应文件夹内的文件数量
        if os.path.exists(untreatedPath):
            csv_files_not_IBA_DONE = [f for f in os.listdir(untreatedPath) if f.endswith('.csv') and not f.startswith('IBA_DONE_')]
            fileCountinFolder.append((stepB, len(csv_files_not_IBA_DONE)))

    # 如果 fileCountinFolder 不为空， 则获取最小值的 stepB 和文件数量
    if fileCountinFolder:
        min_stepB, min_file_count = min(fileCountinFolder, key=lambda x: x[1])
        print(f"最小文件数量的 StepB: {min_stepB}, 文件数量: {min_file_count}")
    else:
        print("没有找到符合条件的文件夹。")
        return False
    
    min_stepB_path = os.path.join(CurrentPath, 'untreated'+min_stepB)

    return min_stepB_path

def fileArrangeCenterBetweenBC():
    CurrentPath = os.path.dirname(os.path.abspath(__file__))
    fileCountinFolder = []
    # 循环StepCs
    for stepC in StepCs:
        untreatedPath = os.path.join(CurrentPath, 'UpLoadData'+stepC)
        # 如果untreatedPath存在，以key和value方式存储 stepC 和对应文件夹内的文件数量
        if os.path.exists(untreatedPath):
            csv_files_not_IBA_DONE = [f for f in os.listdir(untreatedPath) if f.endswith('.csv') and not f.startswith('IBA_DONE3_') and not f.startswith('IBA_DONE4_IBA_DONE3_')]
            fileCountinFolder.append((stepC, len(csv_files_not_IBA_DONE)))

    # 如果 fileCountinFolder 不为空， 则获取最小值的 stepC 和文件数量
    if fileCountinFolder:
        min_stepC, min_file_count = min(fileCountinFolder, key=lambda x: x[1])
        print(f"最小文件数量的 StepC: {min_stepC}, 文件数量: {min_file_count}")
    else:
        print("没有找到符合条件的文件夹。")
        return False
    
    min_stepC_path = os.path.join(CurrentPath, 'UpLoadData'+min_stepC)

    return min_stepC_path

def fileArrangeCenterBetweenCD():
    CurrentPath = os.path.dirname(os.path.abspath(__file__))
    fileCountinFolder = []
    # 循环StepDs
    for stepD in StepDs:
        untreatedPath = os.path.join(CurrentPath, 'UpLoadData'+stepD)
        # 如果untreatedPath存在，以key和value方式存储 stepD 和对应文件夹内的文件数量
        if os.path.exists(untreatedPath):
            csv_files_not_IBA_DONE = [f for f in os.listdir(untreatedPath) if f.endswith('.csv') and f.startswith('IBA_DONE3_')]
            fileCountinFolder.append((stepD, len(csv_files_not_IBA_DONE)))

    # 如果 fileCountinFolder 不为空， 则获取最小值的 stepD 和文件数量
    if fileCountinFolder:
        min_stepD, min_file_count = min(fileCountinFolder, key=lambda x: x[1])
        print(f"最小文件数量的 StepD: {min_stepD}, 文件数量: {min_file_count}")
    else:
        print("没有找到符合条件的文件夹。")
        return False
    
    min_stepD_path = os.path.join(CurrentPath, 'UpLoadData'+min_stepD)

    return min_stepD_path