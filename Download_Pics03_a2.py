import time
import requests
import urllib3
import os
import shutil
import importlib
import sys
urllib3.disable_warnings()
from fileArrangeCenter import fileArrangeCenterBetweenCD
from globalFunctions import  sanitize_folder_name, log_msg, lock_file, unlock_file
import datetime

processId = '_a2'
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__))+"\\log\\", 'stepC'+processId+now+'.log')  # 日志文件路径
print('====================== stepC'+processId+'程序开始运行 ======================')
log_msg(log_file, "stepC"+processId+"程序开始运行", withLock=False)

# 获取当前脚本所在目录
path = os.path.dirname(os.path.abspath(__file__))
print('当前路径是---', path)

# 定义 UpLoadData 文件夹路径
upload_data_dir = os.path.join(path, 'UpLoadData')

config_file = 'BisicConfig.txt'


def check_pic_counts(asinsInFile, asinDirs,pictures_path):
    if not os.path.exists(pictures_path):
        os.makedirs(pictures_path, exist_ok=True)
    pic_dict = dict(zip(asinsInFile, g_imgsInFile))
    dirsNeedToDownload = []
    # 去掉下载图片数不够的 ASIN
    for k, v in pic_dict.items():
        if k == '':
            continue
        if not os.path.exists(os.path.join(pictures_path, k)):
            dirsNeedToDownload.append(k)
            continue
        for dirpath, dirnames, filenames in os.walk(os.path.join(pictures_path, k)):
            if len(filenames) < len(v.split(';')):
                print(f'\n-----目录 {os.path.join(pictures_path, k)} 中图片数量 比 表格 中 ASIN 对应的图片数少！-----')
                dirsNeedToDownload.append(k)
                continue

    zongshu = len(asinsInFile)
    print(f'\n-----【文件中共有】{len(asinsInFile)}组图片----')
    

    print(f'\n-----【已经成功下载的图片组数】{zongshu - len(dirsNeedToDownload)}----')
    print(f'\n-----【未成功下载(包括还未下载)的图片数】{len(dirsNeedToDownload)}组----')
    for pic in dirsNeedToDownload:
        print(f'-----【还没成功下载(下载不完全)图片的 ASIN】分别是：{pic}  ----')
    if len(dirsNeedToDownload) == 0:
        print("\n-----所有图片下载完成-----")



def Execute_Download_pics(count, try_count, asinDirs,pictures_path):
    hangshu = []
    already_exist_folder_count = 0
    for index, item in enumerate(getasins()):

        siteType = get_siteTypes()[index]
        isVariation = get_isVariations()[index]
        variationName = get_variationNames()[index]

        # 当前文件里有10条数据（无论是否连续）对应图片没有下载成功
        min_fail_count = int(len(getasins()) * 0.07)
        if try_count > min_fail_count:
            print(f'程序累计报错{try_count}次，需要检查是否网络有问题！！！')
            log_msg(log_file, f'程序累计报错{try_count}次，需要检查是否网络有问题！！！', withLock=False)
            return False
        
        if asinDirs:
            itemD = item
            if siteType == 'TK_US':
                if isVariation == 'True':
                    itemD = item + '_' + variationName
                else:
                    itemD = item + '_'
            else:
                itemD = item
            
            itemD = sanitize_folder_name(itemD)
            itemD = itemD.strip()
            if itemD in asinDirs:
                folder_path = os.path.join(pictures_path, itemD)
                #得到文件夹下文件的数量
                file_count = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
                pics = get_pictures()[index].split(';')
                if file_count >= len(pics):
                    print(f'-----第{index + 2}行 数据已下载，跳过！')
                    log_msg(log_file, f'-----第{index + 2}行 数据已下载，跳过！', withLock=False)
                    already_exist_folder_count += 1
                    continue
                # print(f'-----第{index + 2}行 数据已下载，跳过！')
                # log_msg(log_file, f'-----第{index + 2}行 数据已下载，跳过！', withLock=False)
                # already_exist_folder_count += 1
                # continue  # 如果图片已下载，跳过

        if item == '':
            hangshu.append(item+'_'+index)
            print(f'-----第{index + 2}行 数据没有 ASIN，请检查数据！！！！！')
            log_msg(log_file, f'-----第{index + 2}行 数据没有 ASIN，请检查数据！！！！！', withLock=False)
            continue

        if siteType == 'TK_US':
            if isVariation == 'True':
                if variationName != '':
                    itemD = item + '_' + variationName
                else:
                    itemD = item + '_'
        else:
            itemD = item

        itemD = sanitize_folder_name(itemD)
        itemD = itemD.strip()

        folder_path = os.path.join(pictures_path, itemD)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path, exist_ok=True)  # 创建 ASIN 对应的文件夹

        pics = get_pictures()[index].split(';')
        success_count = 0
        if len(pics) != 0:
            for pic_index, pic in enumerate(pics):
                url = pic
                try:
                    pic_jpg_path = os.path.join(folder_path, item) + "_" + str(index) + str(pic_index) + '.jpg'
                    print(url, pic_jpg_path)
                    if os.path.exists(pic_jpg_path):
                        print(f'-----图片 {pic_jpg_path} 已存在，跳过！')
                        log_msg(log_file, f'-----图片 {pic_jpg_path} 已存在，跳过！', withLock=False)
                        continue
                    if url.startswith("https://i.ebayimg.com/"):
                        response = requests.get(url, verify=False, timeout=20,proxies={"http": None, "https": None})
                    else:
                        response = requests.get(url, verify=False, timeout=20)
                    with open(pic_jpg_path, "wb") as file:
                        file.write(response.content)
                        print(f'\n-----正在下载{pic_jpg_path}-----')
                        log_msg(log_file, f'正在下载{pic_jpg_path}', withLock=False)
                        success_count += 1
                except Exception as e:
                    if url == '':
                        if item == '':
                            print(f'\n-----下载图片失败，失败图片 URL 是空链接，对应的 ASIN 是：空 ！！！')
                            log_msg(log_file, f'下载图片失败，失败图片 URL 是空链接，对应的 ASIN 是：空 ！！！', withLock=False)
                        else:
                            print(f'\n-----下载图片失败，失败图片 URL 是空链接，对应的 ASIN 是：{item} ！！！')
                            log_msg(log_file, f'下载图片失败，失败图片 URL 是空链接，对应的 ASIN 是：{item} ！！！', withLock=False)
                    else:
                        print(f'\n-----下载图片失败，失败图片 URL 是：{url}，请检查网络或磁盘空间！错误信息：{e}')
                        log_msg(log_file, f'下载图片失败，失败图片 URL 是：{url}，请检查网络或磁盘空间！错误信息：{e}', withLock=False)
                    
                

            if success_count == 0:
                try_count += 1
                shutil.rmtree(folder_path)
            else:
                already_exist_folder_count += 1

            count += 1
            print(f"\n-----第{count}组图片下载中-----")
            log_msg(log_file, f'第{count}组图片下载中', withLock=False)

    if len(hangshu) != 0:
        print(f'\n----------有{len(hangshu)}行数据没有 ASIN，请检查数据！！！！！')
        log_msg(log_file, f'----------有{len(hangshu)}行数据没有 ASIN，请检查数据！！！！！', withLock=False)
    
    return already_exist_folder_count

def check_pic_counts2(asinsInFile, asinDirs,pictures_path):
    if not os.path.isdir(pictures_path):
        os.makedirs(pictures_path, exist_ok=True)
    pic_dict = dict(zip(asinsInFile, g_imgsInFile))
    dirsNeedToDownload = []
    # 去掉下载图片数不够的 ASIN
    for k, v in pic_dict.items():
        if k == '':
            continue
        if not os.path.exists(os.path.join(pictures_path, k)):
            dirsNeedToDownload.append(k)
            continue
        for dirpath, dirnames, filenames in os.walk(os.path.join(pictures_path, k)):
            if len(filenames) < len(v.split(';')):
                print(f'\n-----目录 {os.path.join(pictures_path, k)} 中图片数量 比 表格 中 ASIN 对应的图片数少！-----')
                dirsNeedToDownload.append(k)
                continue
    print(f'\n-----本文件中共有【{len(dirsNeedToDownload)}】组图片未成功下载----')
    log_msg(log_file, f'本文件中共有【{len(dirsNeedToDownload)}】组图片未成功下载', withLock=False)

# 默认重试 5 次，可自定义
def rerun_counts(pictures_path):
    for i in range(5):
        print(f'\n-----程序第{i + 1}次执行-----')
        count, try_count = 0, 0
        if os.path.isdir(pictures_path):
            items = os.listdir(pictures_path)
            asinDirs = [item for item in items if len(items) != 0]
        else:
            asinDirs = []
        if not Execute_Download_pics(count, try_count, asinDirs,pictures_path):
            return False
        time.sleep(5)
    return True

# 修改配置文件中的 .csv 文件名
def update_config_file(csv_file):
    result = False
    if not os.path.exists(config_file):
        print(f"错误: 配置文件 {config_file} 不存在！")
        log_msg(log_file, f"错误: 配置文件 {config_file} 不存在！", withLock=False)
        return

    lock = lock_file(config_file)
    if lock:
        with open(config_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 3:
                lines[2] = csv_file + '\n'
            if len(lines) >= 9:
                lines[8] = "upLoadData"+processId  + '\n'
            f.writelines('') 
            f.seek(0)
            f.writelines(lines)
            f.flush()  # 刷新文件缓冲区
            result = True
        import GetDataFromAmazon
        importlib.reload(GetDataFromAmazon)
        unlock_file(lock)


    # with open(config_file, 'r', encoding='utf-8') as f:
    #     lines = f.readlines()
    # if len(lines) >= 3:
    #     lines[2] = csv_file + '\n'
    # with open(config_file, 'w', encoding='utf-8') as f:
    #     f.writelines(lines)
    #     result = True
    
    return result


if __name__ == '__main__':
    upload_data_dir_processId = upload_data_dir+processId
    if not os.path.exists(upload_data_dir_processId):
        print(f"错误: 文件夹 {upload_data_dir_processId} 不存在！")
        log_msg(log_file, f"错误: 文件夹 {upload_data_dir_processId} 不存在！", withLock=False)
        exit(1)

    lock_fileA = os.path.join(upload_data_dir_processId, "LOCK3.txt")  # 构建完整的文件路径
    if os.path.exists(lock_fileA):
        log_msg(log_file, f"文件夹 {os.path.basename(os.path.normpath(upload_data_dir_processId))} 中存在 LOCK3.txt 文件，程序退出！", withLock=False)
        exit(0)
    else:
        try:   
            # 创建文件
            with open(lock_fileA, "w") as f:
                f.write("Download_Pics03 is working.")
                log_msg(log_file, f"创建了目录 '{os.path.basename(os.path.normpath(upload_data_dir_processId))}' 下的 LOCK3.txt 文件。", withLock=False)
            
            for file in os.listdir(upload_data_dir_processId):
                if not file.endswith('.csv'):
                    continue
                # 如果 file 名字以 IBA_DONE_ 开头，则跳过
                if file.startswith('IBA_DONE3_') or file.startswith('IBA_DONE4_'):
                    continue

                csv_file = file
                if update_config_file(csv_file):
                    print(f"配置文件中的 .csv 文件名已更新为: {csv_file}")
                    log_msg(log_file, f"配置文件中的 .csv 文件名已更新为: {csv_file}", withLock=False)

                    file_path = os.path.join(upload_data_dir_processId, csv_file)
                    log_msg(log_file, f"开始处理文件: {file_path}", withLock=False)

                
                    # import GetDataFromAmazon
                    # importlib.reload(GetDataFromAmazon)
                    from GetDataFromAmazon import get_row_datas, getasins, get_pictures, get_siteTypes, get_isVariations, get_variationNames

                    # 读取配置文件
                    # params = [param.replace('\n', '') for param in open(os.path.join(path, '账号密码以及CSV文件配置.txt'), 'r', encoding='utf-8').readlines()]
                    pictures_path = os.path.join(path, "pictures", csv_file[:-4])
                    print(f'图片存放路径是：{pictures_path}')
                    # 检查 pictures 文件夹是否存在
                    if os.path.exists(pictures_path):
                        items = os.listdir(pictures_path)
                        asinDirs = [item for item in items if len(items) != 0]
                    else:
                        os.makedirs(pictures_path, exist_ok=True)  # 创建 pictures 文件夹
                        asinDirs = []

                    asinsInFile = getasins()
                    g_imgsInFile = get_pictures()

                    check_pic_counts(asinsInFile, asinDirs,pictures_path)
                    if not rerun_counts(pictures_path):
                        break
                    check_pic_counts2(asinsInFile, asinDirs, pictures_path) 

                    # 处理完成后，更新 file_path 的文件名
                    file_path = os.path.join(upload_data_dir_processId, csv_file)
                    new_file_name = f"IBA_DONE3_{csv_file}"

                    new_file_path = fileArrangeCenterBetweenCD()
                    if new_file_path:
                        new_file_path = os.path.join(new_file_path, new_file_name)
                        if os.path.exists(new_file_path):
                            os.remove(new_file_path)
                        shutil.move(file_path, new_file_path)  # 移动文件到新路径
                        print(f"文件已重命名为: {new_file_name}")
                        log_msg(log_file, f"文件已重命名为: {new_file_name}", withLock=False)
                    else:
                        print(f"文件夹 {new_file_path} 不存在， ArrangeCenter保存文件失败。")
                        log_msg(log_file, f"文件夹 {new_file_path} 不存在， ArrangeCenter保存文件失败。", withLock=False)
                    
                    # 获取目录中所有 CSV 文件
                    # csv_files = [f for f in os.listdir(upload_data_dir) if f.endswith('.csv') and f.startswith('IBA_DONE3_')]
                    # csv_files_a1 = [f for f in os.listdir(upload_data_dir_processId) if f.endswith('.csv') and f.startswith('IBA_DONE3_')]
                    # if len(csv_files_a1) < len(csv_files):
                    #     new_file_path = os.path.join(upload_data_dir_processId, new_file_name)
                    # else:
                    #     new_file_path = os.path.join(upload_data_dir, new_file_name)
                    # if os.path.exists(new_file_path):
                    #     os.remove(new_file_path)
                    # shutil.move(file_path, new_file_path)  # 移动文件到新路径
                    # print(f"文件已重命名为: {new_file_name}")
                    # log_msg(log_file, f"文件已重命名为: {new_file_name}", withLock=False)
                else:
                    print(f"错误: 更新配置文件失败！")
                    log_msg(log_file, f"错误: 更新配置文件中的文件参数失败！文件名: {csv_file}", withLock=False)
        finally:
            # 删除文件
            if os.path.exists(lock_fileA):
                os.remove(lock_fileA)
                print(f"成功删除了目录 '{upload_data_dir_processId}' 下的 LOCK3.txt 文件。")
                log_msg(log_file, f"成功删除了目录 '{os.path.basename(os.path.normpath(upload_data_dir_processId))}' 下的 LOCK3.txt 文件。", withLock=False)
                exit(0)

            log_msg(log_file, "stepC"+processId+"程序运行结束", withLock=False)
            print('====================== stepC'+processId+'程序运行结束 ======================')
            sys.exit(0)