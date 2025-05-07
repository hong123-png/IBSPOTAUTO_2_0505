from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # 元素等待类
from selenium.webdriver.support import expected_conditions as EC  # 提供条件判断函数
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import os
from HandleCsv import get_g2lb, get_cm2inch
import sys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import messagebox
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
import json
import tkinter as tk
import re
from globalFunctions import saveFailedRecord, log_msg, lock_file, unlock_file, sanitize_folder_name
from getParams import getParams
import datetime
import importlib
import shutil
from urllib.parse import quote

processId = ''
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__))+'\\log\\', 'stepD'+processId+now+'.log')  # 日志文件路径
log_summary_file = os.path.join(os.path.dirname(os.path.abspath(__file__))+'\\summary_log\\', 'summary'+now+'.log')  # 日志文件路径
start_time = time.time()
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
# 定义 UpLoadData 文件夹路径
upload_data_dir = os.path.join(path, 'UpLoadData'+processId)
config_file = 'BisicConfig.txt'

if sys.platform.startswith('win32'):
    print('----------当前系统是：Windows----------')
    options = webdriver.ChromeOptions()
    options.add_argument('-ignore-certificate-errors')
    options.add_argument('-ignore-ssl-errors')
    options.add_argument('--force-device-scale-factor=0.5')
    
    # 使用 webdriver_manager 自动下载和配置 ChromeDriver
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # 清空浏览器缓存和存储
    browser.delete_all_cookies()  # 清空所有 cookies
else:
    print('----------当前系统是：macOS----------')
    options = webdriver.ChromeOptions()
    options.add_argument('--force-device-scale-factor=0.5')
    
    # 使用 webdriver_manager 自动下载和配置 ChromeDriver
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get('chrome://settings/')
    browser.execute_script('chrome.settingsPrivate.setDefaultZoom(0.5);')

def doThisFirstly():
    print("====================== stepD"+processId+"程序开始运行 ======================")
    log_msg(log_file, "stepD"+processId+"程序开始运行")
    #如果 log_summary_file 这个文件不存在，那就创建一个
    if not os.path.exists(log_summary_file):
        with open(log_summary_file, 'w') as f:
            f.write("dataTime \t totalNum \t startNum \t processedNum \t Price150Num \t duplicateNum \t successNum \t failedNum \t noPicNum \t fileName \t failedIds \t failedPics\n")
    # 调用函数
    warning()

def show_warning():
    messagebox.showwarning("执行程序之前轻轻的提醒！", "执行程序之前轻轻的提醒！")


# def warning():
#     root = tk.Tk()
#     root.geometry('400x300')
#     root.title("执行程序之前轻轻的提醒")
#     warning_button = tk.Button(root, text=f"1.程序是否已经更新到最新{' ' * 38}\n\n"
#                                           "2.数据文件(csv)是否已经去掉图标,问号,Amazon等字符\n\n"
#                                           "3.用户名和密码以及csv文件名称是否同步到配置文件中\n\n"
#                                           f"4.如果都完成,请点【X】,程序会开始运行{' ' * 20}", command=show_warning)
#     warning_button.pack(pady=50)
#     root.mainloop()


# warning()

def show_warning():
    print("警告：请确保所有步骤已完成！")  # 这里可以替换为实际的逻辑
    root.destroy()  # 关闭窗口

def auto_close():
    print("10 秒未操作，自动关闭窗口。")
    root.destroy()  # 关闭窗口

def warning():
    global root  # 声明 root 为全局变量，以便在其他函数中关闭窗口
    root = tk.Tk()
    root.geometry('500x300')  # 调整窗口大小以适应文本
    root.title("执行程序之前轻轻的提醒")

    # 使用 Label 显示提醒信息
    reminder_text = (
        "1. 程序是否已经更新到最新\n\n"
        "2. 数据文件 (csv) 是否已经去掉图标、问号、Amazon 等字符\n\n"
        "3. 用户名和密码以及 csv 文件名称是否同步到配置文件中\n\n"
        "4. 如果都完成，请点【X】，程序会开始运行"
    )
    reminder_label = tk.Label(root, text=reminder_text, justify="left", font=("Arial", 12))
    reminder_label.pack(pady=20)

    # 添加一个按钮，点击后关闭窗口
    close_button = tk.Button(root, text="关闭窗口并开始运行", command=show_warning)
    close_button.pack(pady=10)

    # 绑定窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", show_warning)

    # 设置 10 秒后自动关闭窗口
    root.after(10000, auto_close)  # 10000 毫秒 = 10 秒

    root.mainloop()


# 图片上传的方法
def pic_upload(sku):
    currentProductFileName = getParams()['filename']
    images_button = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div[2]/div[1]/div/div/input')
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
    # dir_path = path +'\\'+ "pictures" +'\\'+ currentProductFileName[:-4]
    dir_path = os.path.join(path , "pictures" +'\\'+ currentProductFileName[:-4])
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for dirname in dirnames:
            if dirname == sku:
                img_path = dir_path +'\\'+ dirname
                for dirpath, dirnames, filenames in os.walk(img_path):
                    for filename in filenames:
                        img_path1 = dirpath +'\\'+ filename
                        images_button.send_keys(img_path1)
    time.sleep(5)


# 将显示等待封装成了函数
def WaitEle_ByXpath(driver, findStr):
    ele = WebDriverWait(driver, 10, 0.5).until(
        EC.visibility_of_element_located(
            (By.XPATH, findStr)
        )
    )
    return ele


def WaitEle_ByID(driver, findStr):
    ele = WebDriverWait(driver, 10, 0.5).until(
        EC.visibility_of_element_located(
            (By.ID, findStr)
        )
    )
    return ele


def getSourceUrl(asin, siteType='ebay'):
    url = ''
    if siteType == 'Amazon':
        url = f"https://www.amazon.com/dp/{asin}"
    elif siteType == 'ebay':
        url = f"https://www.ebay.com/itm/{asin}"
    elif siteType == 'TK_US':
        url = f"https://shop.tiktok.com/view/product/{asin}?region=US"
    return url


def getInputSKU(asin, siteType='ebay'):
    sku = ''
    if siteType == 'Amazon':
        sku = asin + '_AMAZON_US'
    elif siteType == '':
        sku = asin + '_AMAZON_US'
    elif siteType == 'ebay':
        sku = asin + '_ebay_US'
    elif siteType == 'TK_US':
        sku = asin + '_TK_US'
    return sku

def fill_properties(properties):
    # # 将列表转换为 JSON 字符串（使用双引号）
    # properties = json.dumps(properties)
    print("传入的属性数据:", properties)  # 调试信息

    # 检查 properties 的数据类型
    if not properties:
        print("属性数据为空，跳过填充")
        return

    if isinstance(properties, str):  # 如果 properties 是字符串
        try:
            properties = json.loads(properties)  # 尝试解析为列表
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON format in properties: {properties}")
            return

    if not isinstance(properties, list):  # 如果 properties 不是列表
        print(f"Warning: properties is not a list: {properties}")
        return

    # 过滤不需要的属性
    filtered_properties = []
    for prop in properties:
        if not isinstance(prop, dict) or 'name' not in prop or 'value' not in prop:
            print(f"Warning: Invalid property format: {prop}")
            continue

        name = prop['name'].lower()  # 转换为小写，方便比较
        value = prop['value']

        # 跳过不需要的属性
        if name in ['ean', 'isbn','mpn','condition','upc'] or value.lower() in {'does not apply', 'unbranded', 'n/a','no'}:
            continue

        filtered_properties.append(prop)

    print("过滤后的属性数据:", filtered_properties)  # 调试信息

    # 跳转到 product_properties 页面
    product_properties_url = browser.current_url.replace("/edit", "/product_properties")
    browser.get(product_properties_url)

    # 等待页面加载完成
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="product_properties"]'))
    )

    # 获取所有属性行
    property_rows = browser.find_elements(By.XPATH, '//tr[contains(@id, "spree_product_property_")]')

    # 遍历传入的属性数据，覆盖页面中的属性
    for index, prop in enumerate(filtered_properties):
        name = prop['name']
        value = prop['value']
        value = len(value) > 150 and value[:140] or value  # 截取前255个字符

        try:
            # 如果属性行不够，点击“添加属性”按钮
            if index >= len(property_rows):
                continue
                add_property_button = browser.find_element(By.XPATH, '//a[contains(text(), "Add Product Properties")]')
                add_property_button.click()
                # 等待新行加载
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//tr[contains(@id, "spree_new_product_property")][0]'))
                )
                
                property_name_input = browser.find_elements(By.XPATH, '//tr[contains(@id, "spree_new_product_property")]')[0].find_element(By.XPATH, './/td[@class="property_name"]//input')
                value_input = browser.find_elements(By.XPATH, '//tr[contains(@id, "spree_new_product_property")]')[0].find_element(By.XPATH, './/td[@class="value"]//input')
            else:
                # 获取当前行的属性名称和属性值输入框
                property_name_input = property_rows[index].find_element(By.XPATH, './/td[@class="property_name"]//input')
                value_input = property_rows[index].find_element(By.XPATH, './/td[@class="value"]//input')

            # 覆盖属性名称和属性值
            property_name_input.clear()
            property_name_input.send_keys(name)

            value_input.clear()
            value_input.send_keys(value)

            # 调试信息
            print(f"成功填充属性: {name} = {value}")
            log_msg(log_file, f"成功填充属性: {name} = {value}")
        except (NoSuchElementException, ElementNotVisibleException, TimeoutException) as e:
            print(f"填充属性失败: {e}")
            log_msg(log_file, f"填充属性失败: {e}")

def searchSkuAndCheckIfHasImageAndUpdateStock(sku, asin, dir_path, siteType, isVariation,variationName):
    urlSearchA = "https://ibspot.com/admin/products?q%5Bvariants_including_master_and_children_isin_eq%5D=&q%5Bsearch_by_name%5D=&q%5Bvariants_including_master_and_children_sku_cont%5D="
    urlSearchB = "&q%5Bdeleted_at_null%5D=1&q%5Bnot_discontinued%5D=1&button=&per_page=25"
    urlSearch = urlSearchA + quote(sku) + urlSearchB
    try:
        browser.get(urlSearch)
        WebDriverWait(browser, 4).until(
            EC.presence_of_element_located(("xpath", '//*[@id="listing_products"]/tbody/tr[1]/td[2]/a'))
        )
        productImage = browser.find_element(By.XPATH, '//*[@id="listing_products"]/tbody/tr[1]/td[1]')
        # 如果 productImage 里面不包含有内容
        children = productImage.find_elements(By.XPATH, "./*")
        if len(children) == 0:
            productTitle = browser.find_element(By.XPATH, '//*[@id="listing_products"]/tbody/tr[1]/td[2]/a')
            productTitle.click()
            WebDriverWait(browser, 6).until(
                EC.presence_of_element_located(("xpath", '/html/body/div[1]/div/main/div/div[2]/div[2]/aside/ul/li[2]/a'))
            )
            image_button = browser.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/main/div/div[2]/div[2]/aside/ul/li[2]/a')
            image_button.click()

            # 上传图片的方法
            images_button = browser.find_element(By.XPATH,
                                                     '/html/body/div[1]/div/main/div/div[2]/div[1]/div/div/input')
            print('dir_path', dir_path)
            for dirpath, dirnames, filenames in os.walk(dir_path):
                
                for dirname in dirnames:
                    if siteType == 'TK_US':
                        if isVariation == 'True':
                            asinNew = asin + '_' + variationName
                        else:
                            asinNew = asin + '_'
                    else:
                        asinNew = asin
                    asinNew = sanitize_folder_name(asinNew)
                    asinNew = asinNew.strip()

                    if dirname == asinNew:
                        # img_path = dir_path +'\\'+ dirname
                        img_path = os.path.join(dir_path, dirname)
                        for dirpath, dirnames, filenames in os.walk(img_path):
                            names = sorted(filenames)
                            for i, filename in enumerate(names):
                                img_path1 = dirpath +'\\'+ filename
                                print('img_path', img_path1)
                                log_msg(log_file,'img_path', img_path1)
                                # return True
                                if i < 3:
                                    images_button.send_keys(img_path1)
                                    time.sleep(3)
                                else:
                                    images_button.send_keys(img_path1)
        time.sleep(1.2)
        # 返回到提交表单页面
        browser.back()
        time.sleep(1.2)

        setStockNumber(browser,asin,sku)
    except Exception as e:
        print("搜索失败:", e)
        log_msg(log_file, "搜索失败:" + str(e))
        return False

def setStockNumber(browser,asin,sku):
    try:
        add_stock = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div[2]/div[2]/aside/ul/li[5]/a')
        add_stock.click()
        time.sleep(1.2)
        stock = browser.find_element(By.XPATH,
                                    '/html/body/div[1]/div/main/div/div[2]/div[1]/div[1]/div[2]/form/div[1]/div[1]/div/div/input')
        stock.send_keys(Keys.CONTROL, 'a')
        stock.send_keys('50')

        # 点击库存按钮
        add_stock_button = browser.find_element(By.XPATH,
                                                '/html/body/div[1]/div/main/div/div[2]/div[1]/div[1]/div[2]/form/div[2]/button')
        add_stock_button.click()
        time.sleep(1.2)
        browser.back()
        time.sleep(1.2)
        browser.back()
        time.sleep(1.2)

        update_button = browser.find_element(By.XPATH,
                                            '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[2]/button')
        update_button.click()
    except:
        pass
        # saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "更新库存失败", "fileName": currentProductFileName}, errorRecordsDir)
        # record_failedNum = record_failedNum + 1
        # failedIds.append(asin)
        # failedSkus.append(sku)
    
    time.sleep(1.2)
    return True

def runSelenium():
    # f.write("dataTime \t totalNum \t startNum \t processedNum \t successNum \t failedNum  \t fileName\n")
    record_dataTime = ''
    record_totalNum = 0 # done
    record_startNum = 0 # done
    record_processedNum = 0 # done
    record_successNum = 0
    record_failedNum = 0
    record_noPicNum = 0
    record_Price150Num = 0
    record_fileName = '' # done
    record_duplicateNum = 0
    url_cannot_open = '0'
    failedIds = []
    failedPics = []
    failedSkus = []

    # 打开网站
    url = "https://ibspot.com/admin/products"
    urlNewProduct = "https://ibspot.com/admin/products/new"
 
    import GetDataFromAmazon
    importlib.reload(GetDataFromAmazon)
    from GetDataFromAmazon import getasins, get_row_datas
    # 读取配置文件
    username = getParams()['username']
    password = getParams()['password']
    re_run_num = getParams()['re_run_num']
    errorRecordsDir = getParams()['errorRecordsDir']
    currentProductFileName = getParams()['filename']
    print(username, password)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
    
    # 去掉文件名前面的 IBA_DONE3_ 部分
    if currentProductFileName.startswith('IBA_DONE3_'):
        original_file_name = currentProductFileName[10:]

    record_fileName = upload_data_dir +'\\'+ original_file_name
    original_file_name = original_file_name[:-4]
    
    # dir_path = path + "\\pictures" +'\\'+ original_file_name
    dir_path = os.path.join(path , "pictures" +'\\'+ original_file_name)
    print('dir_path---', dir_path)
    dir_names = []
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for dirname in dirnames:
            dir_names.append(dirname)
    
    count = 0
    re_run_num = int(re_run_num)
    record_startNum = re_run_num
    asinsInFile = getasins()
    record_totalNum = len(asinsInFile)
    for index, item in enumerate(asinsInFile):
        print(f'\n-----第{index + 1}行执行-----')
        log_msg(log_file, f'\n-----第{index + 1}行执行-----')
        if index < re_run_num:
            continue


        
        if count > 10:
            print(f'\n-----连续发生意外错误超过10次以上，本文将停止运行，第一次发生错误为第{index-10}行！-----')
            log_msg(log_file, f'\n-----连续发生意外错误超过10次以上，本文将停止运行，第一次发生错误为第{index-10}行！-----')
            break
        
        
        max_retries = 5  # 最大重试次数
        open_browser_failed_max_retries = False
        for attempt in range(max_retries):
            try:
                browser.get(url)
                print("页面加载成功！")
                break  # 成功则跳出循环
            except Exception as e:
                print(f"第 {attempt + 1} 次尝试失败，错误：{e}")
                if attempt == max_retries - 1:
                    print("达到最大重试次数，退出程序。")
                    open_browser_failed_max_retries = True
                    browser.quit()
                    # raise  # 重新抛出异常
                time.sleep(2)  # 等待 2 秒后重试
        if open_browser_failed_max_retries:
            print("浏览器打开页面连续5次失败，程序退出。")
            log_msg(log_file, "浏览器打开页面连续5次失败，程序退出。")
            url_cannot_open = '1'
            break

        record_processedNum = record_processedNum + 1

        asin = item
        print(asin)
        # print(dir_names)

        index = index + 1
        this_start_time = time.time()
        print(f'----asin:{asin}-----')
        log_msg(log_file, f'----asin:{asin}-----')
        name, description, single_features, cost_price, categorie, sins, brand, Image, is_prime, item_length, item_width, item_height, item_weight, siteType, isFreeShipping, shippingFee, productInUS, ShortDescriptionUpdated, properties, isVariation, variationName= get_row_datas(
            index)
        
        
        source_url = getSourceUrl(asin, siteType)
        sku = getInputSKU(asin, siteType)
        if siteType == 'TK_US':
            if isVariation == 'True':
                sku = asin + '_TK_US' + '_' + variationName.replace(' ', '')
        
        # 如果该商品没有图片，那就跳过
        asinD = asin
        if siteType == 'TK_US':
            if isVariation == 'True':
                asinD = asin + '_' + variationName
            else:
                asinD = asin + '_'
        else:
            asinD = asin
        asinD = sanitize_folder_name(asinD)
        asinD = asinD.strip()
        print('dir_names---', dir_names)
        if asinD not in dir_names:
            record_noPicNum = record_noPicNum + 1
            saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "图片文件夹不存在", "fileName": currentProductFileName}, errorRecordsDir)
            failedPics.append(asin)
            failedSkus.append(sku)
            print(f'-----第{index}行执行时候，图片文件夹{asinD}不存在，跳过！-----')
            continue
        
        # Unbranded = 'Unbranded'
        brand = '' if brand == 'Unbranded' else brand

        # 处理 ShortDescriptionUpdated 的连续空行
        if ShortDescriptionUpdated:
            # 使用正则表达式将超过 3 个连续空行替换为 1 个空行
            ShortDescriptionUpdated = re.sub(r'(\n\s*){3,}', '\n', ShortDescriptionUpdated)
        # 判断 ShortDescriptionUpdated 是否包含超过 5 个段落
        if ShortDescriptionUpdated and len(ShortDescriptionUpdated.split('\n')) > 5:
            description = ShortDescriptionUpdated
            single_features = "WELCOME TO OUR STORE"
        else:
            single_features = ShortDescriptionUpdated

        if siteType == 'TK_US':
            if ShortDescriptionUpdated and len(ShortDescriptionUpdated.split('\n')) > 5:
                description = ShortDescriptionUpdated
                single_features = "WELCOME TO OUR STORE"
            else:
                description = "WELCOME TO OUR STORE"
                single_features = ShortDescriptionUpdated

        if(siteType == 'ebay'):
            description = ""
            single_features = ShortDescriptionUpdated
        
        cost_price = cost_price.replace('$', '').replace(',', '').replace(' ', '')
        if cost_price == '' or int(float(cost_price)) > 150:
            print('cost_price===', cost_price)
            print(f'\n-----第{index}行执行时候，价格为空或者大于150，跳过！-----')
            record_Price150Num = record_Price150Num + 1
            continue
        print('cost_price===', cost_price)
        cost_price = "{:.2f}".format(float(cost_price))
        print('111111111cost_price===', cost_price)
        shippingFee = "{:.2f}".format(float(shippingFee))
        if(siteType == 'ebay' or siteType == 'TK_US'):
            cost_price = "{:.2f}".format(float(cost_price) + float(shippingFee))

        print('cost_price---', cost_price, 'seep_fee---', cost_price)
        
        if siteType == 'TK_US':
                if isVariation == 'True':
                    name = name + ':' + variationName
        
        if int(float(cost_price)) < 20:
            master_price = str("{:.2f}".format(float(cost_price) + 20))
        else:
            master_price = str("{:.2f}".format(2 * float(cost_price)))
        print('master_price---', master_price)

        # 先访问创建产品页面，若获取不到，那就是登录失效
        try:
            try:
                # 等待新页面的某个关键元素出现
                WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located(("xpath", '//*[@id="admin_new_product"]'))
                )
                creat_product_btn = browser.find_element(By.XPATH, '//*[@id="admin_new_product"]')
                creat_product_btn.click()
            except:
                try:
                    # 等待新页面的某个关键元素出现
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located(("xpath", '//*[@id="spree_user_email"]'))
                    )
                except TimeoutException:
                    url_cannot_open = '1'
                    break

                username_input = browser.find_element(By.XPATH, '//*[@id="spree_user_email"]')
                username_input.send_keys(username)
                passward_input = browser.find_element(By.XPATH, '//*[@id="spree_user_password"]')
                passward_input.send_keys(password)

                remember_checkbox = browser.find_element(By.XPATH, '//*[@id="spree_user_remember_me"]')
                if not remember_checkbox.is_selected():  # 若没有记忆用户名和密码，勾选
                    remember_checkbox.click()
                login_btn = browser.find_element(By.XPATH, '//*[@id="new_spree_user"]/div[3]/input')
                login_btn.click()
                time.sleep(1.2)

                # 登录后，重写创建产品
                creat_product_btn = browser.find_element(By.XPATH, '//*[@id="admin_new_product"]')
                creat_product_btn.click()
                time.sleep(1.2)

            try:
                WebDriverWait(browser, 4).until(
                    EC.presence_of_element_located(("xpath", '//*[@id="product_name"]'))
                )
                productname_input = browser.find_element(By.XPATH, '//*[@id="product_name"]')
                productname_input.send_keys(name)

                product_sku_input = browser.find_element(By.XPATH, '//*[@id="product_sku"]')
                product_sku_input.send_keys(sku)

                dropdown = browser.find_element(By.ID, 'select2-product_prototype_id-container')
                dropdown.click()

                 # 选择 Prototype
                select = browser.find_element(By.XPATH,
                                            '/html/body/div[1]/div/main/div/div[2]/div/form/fieldset/div[2]/div[2]/div/span/span[1]/span/span[1]')
                select.click()
                select.click()
                time.sleep(1.2)
                select1 = browser.find_element(By.XPATH, '/html/body/span/span/span[2]/ul/li[1]')
                select1.click()
                time.sleep(2)

                # Master Price
                if int(float(cost_price)) < 20:
                    master_price = round(float(cost_price) + 20, 2)
                else:
                    master_price = round(float(2 * float(cost_price)))
                compare_at_price = master_price + 7
                price_input = browser.find_element(By.XPATH, '//*[@id="product_price"]')
                price_input.send_keys(master_price)

                # 选择日期
                available_on = browser.find_element(By.XPATH,
                                                    '//*[@id="product_available_on_field"]/div/input[2]')
                available_on.click()
                available_on.click()

                available_on_time = browser.find_element(By.XPATH, '/html/body/div[6]/div[2]/div/div[2]/div/span[1]')
                available_on_time.click()
                time.sleep(1.2)

                # 选择 Shipping Categories
                select_shipping = browser.find_element(By.XPATH,
                                                    '//*[@id="select2-product_shipping_category_id-container"]')
                select_shipping.click()
                time.sleep(1.2)

                # url填写
                source_url_input = browser.find_element(By.XPATH,
                                                        '//*[@id="product_source_url"]')
                source_url_input.send_keys(source_url)

                if siteType == 'Amazon':
                    select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - US to US by Weight"]')
                if siteType == '':
                    select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - US to US by Weight"]')
                if siteType == 'TK_US':
                    select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - TKUS to US by Item"]')
                if siteType == 'ebay':
                    if productInUS == 'TRUE':
                        if isFreeShipping == 'TRUE':
                            select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - Ebay to US Free Shipping"]')
                        else:
                            select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - US to US by Weight"]')
                    elif productInUS == 'FALSE':
                        select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - US to US by Weight Longer EDD"]')
                    else:
                        select_shipping2 = browser.find_element(By.XPATH, '//*[text()="Public - US to US by Weight"]')
                
                select_shipping2.click()
                time.sleep(1.2)

                # 提交
                submit = browser.find_element(By.XPATH, '//*[@id="new_product"]/fieldset/div[4]/button')
                submit.click()
            except:
                print(f'----\033[91m   当前 {asin} submit 定位失败！！！！   \033[0m -----')
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "新建产品提交异常", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                continue

            # 判断商品sku是否已经创建
            try:
                sku_isExist_js_text = browser.find_element(By.XPATH,
                                                           '/html/body/div[1]/div/main/div/div[2]/div/form/fieldset/div[2]/div[1]/div/span[3]')
                if sku_isExist_js_text.text == 'has already been taken':
                    print('sku_isExist_text----', '商品已经存在')
                    saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "商品sku已经存在", "fileName": currentProductFileName}, errorRecordsDir)
                    record_duplicateNum = record_duplicateNum + 1
                    searchSkuAndCheckIfHasImageAndUpdateStock(sku, asin, dir_path, siteType, isVariation,variationName)
                    continue
                else:
                    print('sku_NoExist_text----')
            except:
                pass
            time.sleep(1.2)



            try:
                # Cost Price
                cost_price_input = browser.find_element(By.XPATH, '//*[@id="product_cost_price"]')
                cost_price_input.send_keys(cost_price)

                # 勾选
                sync_to_gmc_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="product_synctogmc"]'))
                )
                sync_to_gmc_button.click()

                # # url填写
                # source_url_input = browser.find_element(By.XPATH,
                #                                         '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[1]/div[1]/div[1]/div[4]/div/input')
                # source_url_input.send_keys(source_url)

                # Compare at price
                compare_price_input = browser.find_element(By.XPATH, '//*[@id="product_compare_at_price"]')
                compare_price_input.send_keys(compare_at_price)

                # Tax Category选择
                tax_category = browser.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[1]/div[1]/div[2]/div[18]/div/span/span[1]')
                tax_category.click()
                time.sleep(1.2)
                tax_category_default = browser.find_element(By.XPATH, '/html/body/span/span/span[2]/ul/li[2]')
                tax_category_default.click()
            except:
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "填写基本详细信息失败", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                continue

            try:
                # Cost Currency
                cost_currency_selects = browser.find_element(By.XPATH,
                                                             '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[1]/div[1]/div[2]/div[4]/div/span/span[1]')
                cost_currency_selects.click()
                cost_currency_select = browser.find_element(By.XPATH, '/html/body/span/span/span[2]/ul/li[146]')
                time.sleep(2)
                cost_currency_select.click()
                time.sleep(2)

                # 品牌填写
                Brand = browser.find_element(By.XPATH, '//*[@id="product_main_brand"]')
                Brand.send_keys(brand)

                # 填写重量
                if not item_weight:
                    print(f'-----当前 {asin} 重量 为空-----')
                else:
                    print('item_weight---', item_weight)
                    item_weight_input = browser.find_element(By.XPATH,
                                                             '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[1]/div[1]/div[2]/div[16]/div[1]/div/input')
                    item_weight_input.send_keys(Keys.CONTROL, 'a')
                    item_weight_input.send_keys(get_g2lb(item_weight))

                # 填写长
                if not item_length:
                    print(f'-----当前 {asin} 长 为空-----')
                else:
                    print('item_length---', item_length)
                    item_length_input = browser.find_element(By.XPATH, '//*[@id="product_height"]')
                    item_length_input.send_keys(get_cm2inch(item_length))

                # 填写宽
                if not item_width:
                    print(f'-----当前 {asin} 宽 为空-----')
                else:
                    print('item_width---', item_width)
                    item_width_input = browser.find_element(By.XPATH, '//*[@id="product_width"]')
                    item_width_input.send_keys(get_cm2inch(item_width))

                # 填写高
                if not item_height:
                    print(f'-----当前 {asin} 高 为空-----')
                else:
                    print('item_height---', item_height)
                    item_heigt_input = browser.find_element(By.XPATH, '//*[@id="product_depth"]')
                    item_heigt_input.send_keys(get_cm2inch(item_height))
                
                time.sleep(1.2)
            except:
                print(f'----\033[91m   当前 {asin} 填写 税率--- 失败！！！！   \033[0m -----')

            try:
                # Taxons
                taxons_input = browser.find_element(By.XPATH,
                                                    '//*[@id="product_taxons_field"]/span/span[1]/span/ul/li/input')
                # taxons_input.send_keys(categorie)
                taxons_input.send_keys('toys')
                time.sleep(2)
                taxons_ = browser.find_element(By.XPATH, '//*[@id="select2-product_taxon_ids-results"]/li[1]')
                taxons_.click()
                time.sleep(2)
            except:
                print(f'----\033[91m   当前 {asin} 填写 分类标签 失败！！！！   \033[0m -----')

            try:
                update_button = browser.find_element(By.XPATH,
                                                     '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[2]/button')
                update_button.click()
                time.sleep(3)
            except:
                print(f'----\033[91m   当前 {asin} update 提交失败！！！！   \033[0m -----')
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "更新产品详情提交异常", "fileName": currentProductFileName}, errorRecordsDir)
                continue

            time.sleep(1.2)

            # Short Description
            try:
                single_features_element = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.ID, "cke_84"))
                )
                time.sleep(1.2)
                single_features_element.click()

                time.sleep(0.5)
                iframe2 = browser.find_element(By.XPATH, '//*[@id="cke_2_contents"]/iframe')
                browser.switch_to.frame(iframe2)
                time.sleep(2)
                short_description = browser.find_element(By.XPATH, '/html/body')
                print('single_features---', single_features)
                short_description.send_keys(single_features)
                browser.switch_to.default_content()
                time.sleep(1.2)
            except:
                print(f'----\033[91m   当前 {asin} 短描述填写失败！！！！   \033[0m -----')

            try:
                # description
                # single_features_element = WebDriverWait(browser, 10).until(
                #     EC.element_to_be_clickable((By.ID, "cke_32"))
                # )
                # time.sleep(1.2)
                # single_features_element.click()

                time.sleep(0.5)
                iframe1 = browser.find_element(By.XPATH, '//*[@id="cke_1_contents"]/iframe')
                browser.switch_to.frame(iframe1)
                short_description = browser.find_element(By.XPATH, '/html/body')
                short_description.send_keys(description)
                browser.switch_to.default_content()
                time.sleep(3)
            except:
                print(f'----\033[91m   当前 {asin} 长描述填写失败！！！！   \033[0m -----')


            try:
                update_button = browser.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[2]/button')
                update_button.click()
                time.sleep(3)
            except:
                print(f'----\033[91m   当前 {asin} description update 提交失败！！！！   \033[0m -----')
                # saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "更新产品Description提交异常", "fileName": currentProductFileName}, errorRecordsDir)
                # record_failedNum = record_failedNum + 1
                # continue


            time.sleep(2)
            try:
                # 填充属性数据
                fill_properties(properties)
            except Exception as e:
                print(f"填充属性数据失败: {e}")
                log_msg(log_file, f"填充属性数据失败: {e}")

            try:
                # 点击 Update 按钮
                update_button = browser.find_element(By.XPATH,
                                                     '//button[@type="submit" and contains(text(), "Update")]')
                update_button.click()
                time.sleep(2)
            except:
                print(f'----\033[91m   当前 {asin} update 提交失败！！！！   \033[0m -----')
                log_msg(log_file, f'----\033[91m   当前 {asin} update 提交失败！！！！   \033[0m -----')

            time.sleep(1.2)

            # 上传图片
            try:
                image_button = browser.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/main/div/div[2]/div[2]/aside/ul/li[2]/a')
                image_button.click()

                # 上传图片的方法
                images_button = browser.find_element(By.XPATH,
                                                     '/html/body/div[1]/div/main/div/div[2]/div[1]/div/div/input')
            except:
                print(f'----\033[91m   当前 {asin} 上传图片元素 定位失败！！！！   \033[0m -----')
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "上传图片元素定位异常/失败", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                continue

            try:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
                print(f'上传图片路径---{dir_path}---')
                for dirpath, dirnames, filenames in os.walk(dir_path):
                    for dirname in dirnames:
                        if siteType == 'TK_US':
                            if isVariation == 'True':
                                asinNew = asin + '_' + variationName
                            else:
                                asinNew = asin + '_'
                        else:
                            asinNew = asin
                        asinNew = sanitize_folder_name(asinNew)
                        asinNew = asinNew.strip()

                        if dirname == asinNew:
                            # img_path = dir_path +'\\'+ dirname
                            img_path = os.path.join(dir_path, dirname)

                            pics = Image.split(';')
                            file_count = len([name for name in os.listdir(img_path) if os.path.isfile(os.path.join(img_path, name))])
                            # 需要下载数量和实际需要的图片数量相等的时候才能上传图片
                            if len(pics) == file_count:
                                print('img_path', img_path)
                                for dirpath, dirnames, filenames in os.walk(img_path):
                                    names = sorted(filenames)
                                    for i, filename in enumerate(names):
                                        img_path1 = dirpath +'\\'+ filename
                                        print('img_path1', img_path1)
                                        log_msg(log_file,'img_path', img_path1)
                                        if i < 3:
                                            images_button.send_keys(img_path1)
                                            time.sleep(3)
                                        else:
                                            images_button.send_keys(img_path1)
                            else:
                                record_noPicNum = record_noPicNum + 1
                                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "图片下载数量不完全，跳过上传", "fileName": currentProductFileName}, errorRecordsDir)
                                failedPics.append(asin)
                                failedSkus.append(sku)
                                print(f'-----第{index}行执行时候，图片下载数量不完全，跳过！-----')
                                continue
            except Exception as e:
                print(f'----\033[91m   当前 {asin} 上传图片失败！！！！   \033[0m -----')
                log_msg(log_file, f'----\033[91m   当前 {asin} 上传图片失败！！！！   \033[0m -----')
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "上传图片失败", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                continue

            time.sleep(1.2)
            # 返回到提交表单页面
            browser.back()
            time.sleep(1.2)

            # 修改库存 501
            try:
                add_stock = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div[2]/div[2]/aside/ul/li[5]/a')
                add_stock.click()
                time.sleep(1.2)
                stock = browser.find_element(By.XPATH,
                                            '/html/body/div[1]/div/main/div/div[2]/div[1]/div[1]/div[2]/form/div[1]/div[1]/div/div/input')
                stock.send_keys(Keys.CONTROL, 'a')
                stock.send_keys('50')

                # 点击库存按钮
                add_stock_button = browser.find_element(By.XPATH,
                                                        '/html/body/div[1]/div/main/div/div[2]/div[1]/div[1]/div[2]/form/div[2]/button')
                add_stock_button.click()
                time.sleep(1.2)
                browser.back()
                time.sleep(1.2)
                browser.back()
                time.sleep(1.2)

                update_button = browser.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/main/div/div[2]/div[1]/form/fieldset/div[2]/button')
                update_button.click()
            except:
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "更新库存失败", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
                continue
            time.sleep(1.2)

            # 判断 asin 是否上传成功
            product_button = browser.find_element(By.XPATH, '//*[@id="sidebar-product"]/li[1]')
            product_button.click()
            time.sleep(1.2)

            this_elapsed_time = time.time() - this_start_time
            sku_elements = browser.find_elements(By.XPATH, '//*[@class="sku"]')
            found_element = False
            for element in sku_elements:
                if element.text == sku:
                    found_element = True
                    break

            if found_element:
                print(f'---上传完成：asin:{asin}---第{index}个---本次执行时间{this_elapsed_time}秒')
                log_msg(log_file, f'---上传完成：asin:{asin}---第{index}个---本次执行时间{this_elapsed_time}秒')
                record_successNum = record_successNum + 1
                print(sku)
            else:
                print(f'----\033[91m   未知错误，当前 {asin} 上传失败！！！！   \033[0m -----')
                log_msg(log_file, f'----\033[91m   未知错误，当前 {asin} 上传失败！！！！   \033[0m -----')
                saveFailedRecord({"sku": sku, "source_url": source_url, "isVariation": isVariation, "error": "产品列表中未找到上传产品，可能上传失败", "fileName": currentProductFileName}, errorRecordsDir)
                record_failedNum = record_failedNum + 1
                failedIds.append(asin)
                failedSkus.append(sku)
        except Exception as e:
            print(f'----\033[91m   未知错误，当前 {asin} 上传失败！！！！   \033[0m -----')
            log_msg(log_file,f'----\033[91m   未知错误，当前 {asin} 上传失败！！！！   \033[0m -----')
            record_failedNum = record_failedNum + 1
            count += 1
            print(f'\n-----程序报错第{count}次，请检查网络是否异常！-----')
        finally:
            print(f"length={len(getasins())}")
            print(f"index={index}")

    record_dataTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    failedIds_string = json.dumps(failedIds)
    failedPics_string = json.dumps(failedPics)
    return record_dataTime, record_totalNum, record_startNum, record_processedNum, record_successNum, record_failedNum, record_noPicNum, record_Price150Num, record_duplicateNum, record_fileName, url_cannot_open, failedIds_string, failedPics_string

# 修改配置文件中的 .csv 文件名
def update_config_file(csv_file, processId=''):
    result = False
    if not os.path.exists(config_file):
        print(f"错误: 配置文件 {config_file} 不存在！")
        log_msg(log_file, f"错误: 配置文件 {config_file} 不存在！")
        return
    
    lock = lock_file(config_file)
    if lock:
        with open(config_file, 'r+', encoding='utf-8') as f:   
            lines = f.readlines()
            if len(lines) >= 3:
                lines[2] = csv_file + '\n'
            # if processId!= '':
            if len(lines) >= 9:
                lines[8] = "upLoadData" + processId + '\n'
            # f.writelines([])
            f.write('') 
            f.seek(0)
            f.writelines(lines)
            f.flush()
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
    return result

def do_your_work():
    doThisFirstly()
    
    if not os.path.exists(upload_data_dir):
        print(f"错误: 文件夹 {upload_data_dir} 不存在！")
        log_msg(log_file, f"错误: 文件夹 {upload_data_dir} 不存在！")
        exit(1)
    
    for file in os.listdir(upload_data_dir):
        if not file.endswith('.csv'):
            continue
        # 如果 file 名字以 IBA_DONE3_ 开头，则跳过该文件
        if not file.startswith('IBA_DONE3_'):
            log_msg(log_file, f"文件 {file} 已经上传结束/ 还没处理好需等待，跳过。")
            continue
        
        csv_file = file
        if update_config_file(csv_file, processId):
            file_path = upload_data_dir +'\\'+ csv_file
            log_msg(log_file, f"当前处理的文件是: {file_path}")

            # import GetDataFromAmazon
            # importlib.reload(GetDataFromAmazon)
            from GetDataFromAmazon import getasins, get_row_datas
            try:
                record_dataTime, record_totalNum, record_startNum, record_processedNum, record_successNum, record_failedNum, record_noPicNum, record_Price150Num, record_duplicateNum, record_fileName, url_cannot_open, failedIds_string, failedPics_string = runSelenium()
            except Exception as e:
                print(f'文件数据读取失败 {csv_file} : {e}')
                log_msg(log_file, f'文件数据读取失败 {csv_file} : {e}')
                #更改文件名
                file_path = upload_data_dir +'\\'+ csv_file
                new_file_name = f"IBA_DONE4_ERROR_{csv_file}"
                new_file_path = upload_data_dir +'\\'+ new_file_name
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                os.rename(file_path, new_file_path)  # 重命名文件
                print(f"文件已重命名为: {new_file_name}")
                log_msg(log_file, f"文件已重命名为: {new_file_name}")
                continue
            if url_cannot_open == '1':
                print("浏览器打开页面连续5次失败，程序退出。")
                # log_msg(log_file, "浏览器打开页面连续5次失败，程序退出。")
                break
            log_msg(log_summary_file, f"{record_dataTime}\t{record_totalNum}\t{record_startNum}\t{record_processedNum}\t{record_Price150Num}\t{record_duplicateNum}\t{record_successNum}\t{record_failedNum}\t{record_noPicNum}\t{record_fileName}\t{failedIds_string}\t{failedPics_string}")
            
            # 处理完成后，更新 file_path 的文件名
            file_path = upload_data_dir +'\\'+ csv_file
            new_file_name = f"IBA_DONE4_{csv_file}"
            new_file_path = upload_data_dir +'\\'+ new_file_name
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(file_path, new_file_path)  # 重命名文件
            print(f"文件已重命名为: {new_file_name}")
            log_msg(log_file, f"文件已重命名为: {new_file_name}")

            # 如果 record_totalNum+record_duplicateNum+record_Price150Num == record_successNum，则删除文件
            '''
            if (record_successNum+record_duplicateNum+record_Price150Num) == record_totalNum:
                pathHere = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
                log_msg(log_file, f"文件数据全部处理完成, 删除文件: {file_path},并移动原始文件到untreated/DONE文件夹")
                # 删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"文件已删除: {file_path}")
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                    print(f"文件已删除: {new_file_path}")
                # 删除对应pictures文件夹下的文件夹
                imageFolderName = csv_file[:-4]
                # 如果 csv_file 以 IBA_DONE4_IBA_DONE3_ 开头，则删除 csv_file中的IBA_DONE4_IBA_DONE3_ 开头部分
                if csv_file.startswith('IBA_DONE3_'):
                    imageFolderName = imageFolderName[10:]
                imageFolderPath = pathHere +'\\'+ "pictures" +'\\'+ imageFolderName
                if os.path.exists(imageFolderPath):
                    shutil.rmtree(imageFolderPath)
                
                fileNameInUntreatedFolder = f"IBA_DONE_{imageFolderName}.csv"
                fileNameInUntreatedFolderPath = os.path.join(pathHere, "untreated" +'\\'+ fileNameInUntreatedFolder)
                if os.path.exists(fileNameInUntreatedFolderPath):
                    os.remove(fileNameInUntreatedFolderPath)
                fileNameInUntreatedFolderPath = os.path.join(pathHere, "untreated_a1" +'\\'+ fileNameInUntreatedFolder)
                if os.path.exists(fileNameInUntreatedFolderPath):
                    os.remove(fileNameInUntreatedFolderPath)
                originalFileName = f"IBA_DONE_{imageFolderName}.xlsx"
                originalFilePath = os.path.join(pathHere, "untreated" +'\\'+ originalFileName)
                # if processed folder doesn't exist, create it
                if not (os.path.exists(os.path.join(pathHere, "untreated","DONE"))):
                    os.makedirs(os.path.join(pathHere, "untreated","DONE"))
                # move original file to processed folder
                if os.path.exists(originalFilePath):
                    if os.path.exists(os.path.join(pathHere, "untreated", "DONE" +'\\'+ originalFileName)):
                        os.remove(os.path.join(pathHere, "untreated", "DONE" +'\\'+ originalFileName))
                    shutil.move(originalFilePath, os.path.join(pathHere, "untreated","DONE"))
            '''
        else:
            print(f"错误: 更新配置文件失败！")
            log_msg(log_file, f"错误: 更新配置文件中的文件参数失败！文件名: {csv_file}")



    


if __name__ == '__main__':

    lock_fileA = os.path.join(upload_data_dir, "LOCK4.txt")  # 构建完整的文件路径
    if os.path.exists(lock_fileA):
        log_msg(log_file, f"文件 {lock_fileA} 已存在，程序将退出。")
        exit(0)  # 将 return 替换为 exit(0)
    else:
        try:
            with open(lock_fileA, "w") as f:
                f.write("GetSelenium04 is working.")
                log_msg(log_file, f"创建文件 {lock_fileA} 成功。")
            do_your_work()
        except Exception as e:
                print(f'意外错误: {e}')
        finally:
            if os.path.exists(lock_fileA):
                os.remove(lock_fileA)
                print(f"成功删除了目录 '{upload_data_dir}' 下的 LOCK4.txt 文件。")
                log_msg(log_file, f"成功删除了目录 '{upload_data_dir}' 下的 LOCK4.txt 文件。")
            
            log_msg(log_file, "stepD"+processId+"程序运行结束")
            print("====================== stepD"+processId+"程序运行结束 ======================")
            end_time = time.time()
            # 计算并打印执行时间
            elapsed_time = end_time - start_time
            print(f"执行时间: {elapsed_time}秒")
            sys.exit(0)