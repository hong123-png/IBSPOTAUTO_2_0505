import pandas as pd
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from openai import OpenAI
import nest_asyncio
import re
import chardet
import logging
import requests
import datetime
from globalFunctions import log_msg
import sys
from fileArrangeCenter import fileArrangeCenterBetweenBC

processId = ''

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__))+'\\log\\', 'stepB'+processId+now+'.log')  # 日志文件路径
print("====================== stepB"+processId+"程序开始运行 ======================")
log_msg(log_file, "stepB"+processId+"程序开始运行")

# 解决 RuntimeError: Event loop is closed 问题
nest_asyncio.apply()

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 数据文件夹路径
file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'untreated'+processId)  # 修改为 'untreated' 文件夹

# 父级目录路径，用于其他文件
parent_dir = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录的父级

# UpLoadData 文件夹路径
upload_dir = os.path.join(parent_dir, 'UpLoadData')
os.makedirs(upload_dir, exist_ok=True)  # 创建 UpLoadData 文件夹（如果不存在）



# 获取文件编码
def get_file_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        return result['encoding']

# 从 URL 获取 HTML 内容
async def fetch(session, url):
    """从 URL 获取 HTML 内容"""
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        logging.warning(f"Invalid URL: {url}")
        return None
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to retrieve content from URL: {url}, Error: {e}")
        return None
    
# 处理每一行数据
async def process_row(index, value, session, df, t_siteType):
    """处理每一行数据"""
    if pd.isna(value) or not isinstance(value, str) or not value.strip():
        logging.warning(f"Skipping empty or invalid URL at index {index}")
        df.at[index, 'ShortDescriptionUpdated'] = ""
        return
    if(t_siteType == 'ebay'):
        html_content = await fetch(session, value)
        if not html_content:
            df.at[index, 'ShortDescriptionUpdated'] = ""
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # 删除所有出现的 "eBay"（不区分大小写）以及 "money-back guarantee" 和 "free shipping"
        text = re.sub(r'\b(ebay|money[-\s]back\s+guarantee|free\s+shipping)\b', '', text, flags=re.IGNORECASE)

        # 使用 OpenAI API 进行文本生成
        # try:
        #     response = client.chat.completions.create(
        #         model="deepseek-chat",
        #         messages=[
        #             {"role": "system",
        #              "content": "As an e-commerce sales copywriter, please create 5 bullet-point descriptions containing key listing features for the following product information in the following format: [Brief key features] Short text, just text, no pictures or emoticons or special symbols."},
        #             {"role": "user", "content": text},
        #         ],
        #         stream=False
        #     )
        #     completion = response.choices[0].message.content
        # 使用 OpenAI API 进行文本生成

        # 使用本地ollma进行文本生成 
        try:
            response = requests.post(
                url="http://127.0.0.1:11434/api/chat",
                json={
                    "model": "deepseek-r1:1.5b",
                    "messages": [
                        {"role": "system",
                        "content": "As an e-commerce sales copywriter, please create a 5-point description of the following product information with key listing features in the following format: [Brief key features] Short text;"
                                    "Only give 5 points of description, no other unnecessary words;"
                                    "Don't repeat"},
                        {"role": "user", "content": text},
                    ],
                    "stream": False
                }
                # proxies = {"http": None, "https": None}# 禁用代理
            )
            response.raise_for_status()  # 检查 HTTP 请求是否成功
            data = response.json()
            '''logging.info(f"DeepSeek API response: {data}")  # 打印 API 响应'''

            # 从响应中提取生成的答案内容
            completion = data.get("message", {}).get("content", "")
            # if not completion:
            #     logging.warning(f"Empty response from DeepSeek API for index {index}")
            #     df.at[index, 'ShortDescriptionUpdated'] = ""
            #     return

            # 去除 <think></think> 中的内容
            completion = re.sub(r'<think>.*?</think>', '', completion, flags=re.DOTALL).strip()

            # 使用正则表达式替换每行开头的部分
            updated_value = re.sub(r'\*\*(.*?)\*\*', r'[\1]', completion)

            df.at[index, 'ShortDescriptionUpdated'] = updated_value
            logging.info(f"Index: {index}, Updated Value: {updated_value}")
        except Exception as e:
            logging.error(f"Error processing row {index}: {e}")
            df.at[index, 'ShortDescriptionUpdated'] = ""
    elif(t_siteType == 'Tiktok'):
        df.at[index, 'ShortDescriptionUpdated'] = value
    else:
        pass

# 主函数，处理所有行
async def process_file(file_path):
    """处理单个 CSV 文件"""
    # 如果文件大小为 0，跳过该文件
    if os.path.getsize(file_path) == 0:
        logging.info(f"文件 {file_path} 大小为 0，跳过该文件")
        log_msg(log_file, f"文件 {file_path} 大小为 0，跳过该文件")
        return
    
    # 检测文件编码
    file_encoding = get_file_encoding(file_path)
    logging.info(f"检测到的文件编码: {file_encoding}")

    # 使用检测到的编码读取文件
    try:
        df = pd.read_csv(file_path, encoding=file_encoding)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')

    # 确保 'ShortDescriptionUpdated' 列存在
    if 'ShortDescriptionUpdated' not in df.columns:
        df['ShortDescriptionUpdated'] = ""

    # 检查每一行的siteType并更新ShortDescriptionUpdated 处理Amazon数据
    try:
        # 遍历每一行数据
        for index in range(len(df)):
            # 直接从DataFrame中获取siteType
            siteType = df.at[index, 'siteType'] if 'siteType' in df.columns else 'Amazon'

            # 获取所有feature列的数据
            single_features = []
            if siteType == 'Amazon':
                for i in range(1, 11):  # 检查Feature 1到Feature 10
                    feature_col = f'Description & Features: Feature {i}'
                    if feature_col in df.columns:
                        feature_value = df.at[index, feature_col]
                        if pd.notna(feature_value) and feature_value.strip():
                            single_features.append(feature_value)

                # 格式化feature列表
                single_features2 = [f"{s}\n" if i != len(single_features) - 1 else s for i, s in
                                    enumerate(single_features)]
                single_features_str = ''.join(single_features2)

                logging.info(f"处理第 {index + 1} 行，siteType: {siteType}")
                logging.info(f"处理第 {index + 1} 行，single_features: {single_features_str}")

                # 直接使用single_features更新ShortDescriptionUpdated
                df.at[index, 'ShortDescriptionUpdated'] = single_features_str
                logging.info(f"第 {index + 1} 行是Amazon商品，已更新ShortDescriptionUpdated")
                logging.info(f"更新后的值: {df.at[index, 'ShortDescriptionUpdated']}")

    except Exception as e:
        logging.error(f"检查siteType时出错: {e}")
        logging.error(f"错误详情: {str(e)}")

    #处理非Amazon数据
    if 'ShortDescription' in df.columns:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, value in df['ShortDescription'].items():
                url = df.loc[index, 'url']  # 使用 .loc 通过索引和列名获取对应的 url
                if url.startswith("https://shop.tiktok.com") or url.startswith("http://shop.tiktok.com"):  # 如果 url 开头是 http:// 或 https://，则进行处理
                    t_SiteType = 'Tiktok'
                elif url.startswith("https://www.ebay.com") or url.startswith("http://www.ebay.com"):  # 如果 url 开头是 http:// 或 https://，则进行处理
                    t_SiteType = 'ebay'
                else:
                    continue
                ttt = df.loc[index, 'ShortDescriptionUpdated']
                if isinstance(ttt, str) and ttt.strip():
                    continue  # 如果 ShortDescriptionUpdated 列存在且值不为空，则跳过
                tasks.append(process_row(index, value, session, df, t_SiteType))
            # 分批处理任务，每批 6 个
            for i in range(0, len(tasks), 6):
                batch = tasks[i:i + 6]
                await asyncio.gather(*batch)
                logging.info(f"Processed batch {i // 6 + 1}")
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        logging.info("文件中没有ShortDescription列，跳过处理")

    # 保存文件到父级目录的 UpLoadData 文件夹
    processed_file_name = f"{os.path.basename(file_path)}"
    upload_dir = fileArrangeCenterBetweenBC()
    processed_file_path = os.path.join(upload_dir, processed_file_name)
    df.to_csv(processed_file_path, index=False, encoding='utf-8-sig')
    logging.info(f"文件保存完成: {processed_file_path}")
    log_msg(log_file, f"文件保存完成: {processed_file_path}")

    # 处理完成后，更新 file_path 的文件名
    renamed_file_path = os.path.join(file_dir, f"IBA_DONE_{os.path.basename(file_path)}")
    if os.path.exists(renamed_file_path):
        os.remove(renamed_file_path)
    os.rename(file_path, os.path.join(file_dir, f"IBA_DONE_{os.path.basename(file_path)}"))
    logging.info(f"文件已重命名为: IBA_DONE_{os.path.basename(file_path)}")
    log_msg(log_file, f"文件已重命名为: IBA_DONE_{os.path.basename(file_path)}")



# 批量处理所有文件
async def process_files():

    lock_fileA = os.path.join(file_dir, "LOCK2.txt")  # 构建完整的文件路径
    if os.path.exists(lock_fileA):
        log_msg(log_file, f"文件夹 {os.path.basename(os.path.normpath(file_dir))} 中存在 LOCK2.txt 文件，程序退出！")
        exit(0)  # 将 return 替换为 exit(0)
    else:
        try:
            # 创建文件
            with open(lock_fileA, "w") as f:
                f.write("updateEbayDesOllama02 is working.") 
                log_msg(log_file, f"创建文件: {lock_fileA}")
    
            # 获取目录中所有 CSV 文件
            csv_files = [f for f in os.listdir(file_dir) if f.endswith('.csv')]

            temp_count = 0
            for file_name in csv_files:
                # 如果文件名以 'IBA_DONE_' 开头，跳过该文件
                if file_name.startswith('IBA_DONE_'):
                    logging.info(f"跳过已处理文件: {file_name}")
                    log_msg(log_file, f"跳过已处理文件: {file_name}")
                    continue

                file_path = os.path.join(file_dir, file_name)

                logging.info(f"开始处理文件: {file_path}")
                log_msg(log_file, f"开始处理文件: {file_path}")
                await process_file(file_path)
                temp_count += 1
        finally:
            # 删除文件
            if os.path.exists(lock_fileA):
                os.remove(lock_fileA)
                print(f"成功删除了目录 '{file_dir}' 下的 LOCK2.txt 文件。")
                log_msg(log_file, f"成功删除了目录 '{os.path.basename(os.path.normpath(file_dir))}' 下的 LOCK2.txt 文件。")
            log_msg(log_file, "stepB"+processId+"程序运行结束")
            print("====================== stepB"+processId+"程序运行结束 ======================")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(process_files())
    sys.exit(0)

