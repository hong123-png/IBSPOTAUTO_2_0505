import random
from HandleCsv import read_csv_data, get_g2lb, get_cm2inch
import os
import csv
import pandas as pd
import chardet
from getParams import getParams

upLoadData = "UpLoadData"
if getParams()['upLoadData'] != '':
    upLoadData = getParams()['upLoadData']

def set_my_variable(value):
    global my_variable
    my_variable = value
    
def get_file_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        return result['encoding']
    
# 数据文件路径
base_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
upload_folder = os.path.join(base_path, upLoadData)  # 指定 UpLoadData 文件夹
print(upload_folder)
params = []

file_encoding = get_file_encoding(os.path.join(base_path, 'BisicConfig.txt'))
try:
    with open(os.path.join(base_path, 'BisicConfig.txt'), 'r', encoding=file_encoding) as f:
        lines = f.readlines()
        for line in lines:
            param = line.strip()
            params.append(param)
except UnicodeDecodeError:
    with open(os.path.join(base_path, 'BisicConfig.txt'), 'r', encoding='ISO-8859-1') as f:
        lines = f.readlines()
        for line in lines:
            param = line.strip()
            params.append(param)


# params = [param.strip() for param in open(os.path.join(base_path, 'BisicConfig.txt'), 'r', encoding='utf-8').readlines()]
filename = params[2]
print(filename)

# 拼接完整路径
filename = os.path.join(upload_folder, filename)

# 获取数据的方法
start_row = 1  # 起始行索引
end_row = 0
try:
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        # 读取 CSV 文件
        end_row = len(f.readlines())  # 获取文件的总行数
        f.seek(0)  # 重置文件指针到开头
    # reader = csv.reader(open(filename, 'r', errors='ignore'))
except FileNotFoundError:
    print(f"错误：文件 '{filename}' 未找到。")
    exit()

def getdata(filename, column):
    result = read_csv_data(filename, start_row, end_row, column)
    return result

def get_title():
    file_encoding = get_file_encoding(filename)
    try:
        with open(filename, 'r', encoding=file_encoding, errors='ignore') as f:
            # 读取 CSV 文件
            reader = csv.reader(f)
            data = list(reader)
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='ISO-8859-1', errors='ignore') as f:
            # 读取 CSV 文件
            reader = csv.reader(f)
            data = list(reader)
    dic = {}
    for index, col in enumerate(data[0]):
        if col == 'Image':
            dic['Image'] = index
        elif col == 'Title':
            dic['name'] = index
        elif col == 'Description & Features: Description':
            dic['description'] = index
        elif col == 'Description & Features: Feature 1':
            dic['column_data_1'] = index
        elif col == 'Description & Features: Feature 10':
            dic['column_data_10'] = index
        elif col in ['Buy Box 🚚: Current', 'Buy Box : Current', 'Buy Box: Current']:
            dic['cost_price'] = index
        elif col == 'Categories: Root':
            dic['categorie'] = index
        elif col == 'ASIN':
            dic['sins'] = index
        elif col == 'Brand':
            dic['brand'] = index
        elif col == 'Prime Eligible (Buy Box)':
            dic['is_prime'] = index
        elif col == 'Item: Length (cm)':
            dic['item_length'] = index
        elif col == 'Item: Width (cm)':
            dic['item_width'] = index
        elif col == 'Item: Height (cm)':
            dic['item_height'] = index
        elif col == 'Item: Weight (g)':
            dic['item_weight'] = index
        elif col == 'siteType':
            dic['siteType'] = index
        elif col == 'isFreeShipping':
            dic['isFreeShipping'] = index
        elif col == 'productInUS':
            dic['productInUS'] = index
        elif col == 'ShortDescriptionUpdated':
            dic['ShortDescriptionUpdated'] = index
        elif col == 'properties':
            dic['properties'] = index  # 添加对 properties 列的识别
        elif col == 'Shipping Fee':
            dic['Shipping Fee'] = index  # 添加对 properties 列的识别
        elif col == 'IsVariation':
            dic['IsVariation'] = index  # 添加对 properties 列的识别
        elif col == 'VariationName':
            dic['VariationName'] = index  # 添加对 properties 列的识别

    # 确保所有键都有默认值 -1
    keys = ['Image', 'name', 'description', 'column_data_1', 'column_data_10', 'cost_price', 'categorie', 'sins', 'brand', 'is_prime',
            'item_length', 'item_width', 'item_height', 'item_weight', 'siteType', 'isFreeShipping', 'productInUS',
            'ShortDescriptionUpdated', 'properties', 'Shipping Fee', 'IsVariation', 'VariationName']
    for key in keys:
        if key not in dic:
            dic[key] = -1  # 如果列不存在，返回 -1

    return dic

# 根据行获取到 feature 的列表
def get_row_datas(row_num):
    file_encoding = get_file_encoding(filename)
    try:
        with open(filename, 'r', encoding=file_encoding, errors='ignore') as f:
            # 读取 CSV 文件
            reader = csv.reader(f)
            data = list(reader)
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='ISO-8859-1', errors='ignore') as f:
            # 读取 CSV 文件
            reader = csv.reader(f)
            data = list(reader)

    # reader = csv.reader(open(filename, 'r', encoding='utf-8', errors='ignore'))
    single_features = []
    title_dict = get_title()

    # 获取数据，检查索引是否有效
    def get_value(index):
        return data[row_num][index] if index != -1 else ''

    name = get_value(title_dict['name'])
    description = get_value(title_dict['description'])
    for i in range(title_dict['column_data_1'], title_dict['column_data_10'] + 1):
        column_data = get_value(i)
        if column_data:
            single_features.append(column_data)

    single_features2 = [f"{s}\n" if i != len(single_features) - 1 else s for i, s in enumerate(single_features)]
    cost_price = get_value(title_dict['cost_price'])
    categorie = get_value(title_dict['categorie'])
    sins = get_value(title_dict['sins'])
    brand = get_value(title_dict['brand'])
    Image = get_value(title_dict['Image'])
    is_prime = ''
    item_length = get_value(title_dict['item_length'])
    item_width = get_value(title_dict['item_width'])
    item_height = get_value(title_dict['item_height'])
    item_weight = get_value(title_dict['item_weight'])
    siteType = get_value(title_dict['siteType'])
    isFreeShipping = get_value(title_dict['isFreeShipping'])
    productInUS = get_value(title_dict['productInUS'])
    ShortDescriptionUpdated = get_value(title_dict['ShortDescriptionUpdated'])
    properties = get_value(title_dict['properties'])  # 读取 properties 列数据
    shippingFee = get_value(title_dict['Shipping Fee'])  # shipping fee
    isVariation = get_value(title_dict['IsVariation'])  # isVariation
    variationName = get_value(title_dict['VariationName'])  # variationName

    return name, description, single_features2, cost_price, categorie, sins, brand, Image, is_prime, item_length, item_width, item_height, item_weight, siteType, isFreeShipping, shippingFee, productInUS, ShortDescriptionUpdated, properties, isVariation, variationName

# 获取 ASIN 列表
def getasins():
    asins_index = get_title()['sins']
    asins = getdata(filename, asins_index)
    return asins

# 获取图片 URL 列表
def get_pictures():
    Image_index = get_title()['Image']
    pictures = getdata(filename, Image_index)
    return pictures

def get_siteTypes():
    siteType_index = get_title()['siteType']
    siteTypes = getdata(filename, siteType_index)
    return siteTypes

def get_isVariations():
    isVariation_index = get_title()['IsVariation']
    isVariations = getdata(filename, isVariation_index)
    return isVariations

def get_variationNames():
    variationName_index = get_title()['VariationName']
    variationNames = getdata(filename, variationName_index)
    return variationNames

if __name__ == '__main__':
    # 读取 CSV 第四行数据（索引 3）
    name, description, single_features, cost_price, categorie, sins, brand, is_prime, item_length, item_width, item_height, item_weight, siteType, isFreeShipping, productInUS, ShortDescriptionUpdated, properties, isVariation, variationName = get_row_datas(3)

    # 打印 properties 列数据
    print("Properties:", properties)
    print("Product in US:", productInUS)

    # 其他代码
    if not item_length:
        print(222)
        print(get_cm2inch(item_length))
    print(get_cm2inch(item_width))
    print(get_cm2inch(item_height))
    print(111)

    if get_row_datas(1)[11]:  # 检查 item_weight
        print(type(get_row_datas(3)[11]))
    else:
        print('kongklong')
