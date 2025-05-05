import os

def getParams():
    """
    获取参数配置
    :return: 参数列表
    """
    # 读取参数配置文件
    with open('BisicConfig.txt', 'r', encoding='utf-8') as file:
        params = [param.strip() for param in file.readlines()]
    return {
        'username': params[0],
        'password': params[1],
        'filename': params[2],
        're_run_num': params[3],
        'siteType': params[6],
        'errorRecordsDir': params[7],
        'upLoadData': params[8],
        }
    # 数据文件路径
    base_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    upload_folder = os.path.join(base_path, 'UpLoadData')  # 指定 UpLoadData 文件夹
    params = [param.strip() for param in open(os.path.join(base_path, 'BisicConfig.txt'), 'r', encoding='utf-8').readlines()]
    filename = params[2]
    siteType = params[6]
    print(filename)

export = getParams()