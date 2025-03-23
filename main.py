"""
图片智能重命名工具
功能：使用百度AI接口识别当前目录下的图片内容，并自动重命名为描述性文件名
作者：RhoPaper        网站：rhopaper.top
注意事项：需提前申请百度AI的API Key和Secret Key，本demo内Key仅供演示！
--------------------
重要！本项目遵循MIT开源协议，转载、改编请注明原作者！
"""

# 导入标准库
import os        # 文件系统操作
import re        # 正则表达式处理
import base64    # 图片Base64编码
import requests  # HTTP请求库

# 百度AI服务认证配置（重要！需自行申请）
API_KEY = 'HRBDD6qfBERbqTdyS2M79CZZ'    # 百度AI应用的API Key
SECRET_KEY = 'AHQ1zuvSyUPSG5qlIUhknuMbBpOlCq4L'  # 百度AI应用的Secret Key

def get_access_token():
    """
    获取百度AI服务的访问令牌
    实现原理：通过API Key和Secret Key获取OAuth2.0的access_token
    返回：字符串形式的access_token（有效期通常为1个月）
    """
    # 构造获取token的URL（包含客户端凭证）
    url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}'
    # 发送GET请求并解析JSON响应
    return requests.get(url).json().get('access_token')

def rename_images():
    """
    主处理函数：遍历目录→识别图片→重命名文件
    流程：
    1. 获取访问令牌
    2. 遍历当前目录所有文件
    3. 筛选图片文件进行识别
    4. 处理文件名并重命名
    """
    # 获取百度API访问凭证
    access_token = get_access_token()
    # 百度图像识别接口地址（高级版通用物体识别）
    url = 'https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general'
    
    # 遍历当前目录下的所有文件（不包含子目录）
    for filename in os.listdir('.'):
        # 判断是否为文件且是支持的图片格式（不区分大小写）
        if os.path.isfile(filename) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            try:
                # 读取图片文件并进行Base64编码
                with open(filename, 'rb') as f:  # 以二进制模式读取文件
                    image = base64.b64encode(f.read()).decode()  # 双重编码：bytes→base64 bytes→utf8字符串
                
                # 发送POST请求到百度API（表单格式）
                response = requests.post(
                    url,
                    headers={'Content-Type':'application/x-www-form-urlencoded'},  # 设置表单头
                    data={
                        'access_token': access_token,  # 访问令牌
                        'image': image               # 图片Base64数据
                    }).json()  # 直接解析返回的JSON数据
                
                # 处理API返回结果
                if 'result' in response:
                    # 从结果中选取置信度最高的标签（按score排序取最大值）
                    best_tag = max(response['result'], key=lambda x:x['score'])['keyword']
                    
                    # 清理非法字符并截断（适配Windows/Linux/Mac的文件命名规范）
                    clean_name = re.sub(r'[\\/:*?"<>|]', '', best_tag)[:10].strip()  # 去除特殊字符+截断前10字符
                    
                    # 构建新文件名（保留原扩展名）
                    ext = os.path.splitext(filename)[1]  # 获取文件扩展名（包含点，如.jpg）
                    new_name = f"{clean_name}{ext}"
                    
                    # 处理重名冲突：如果文件已存在，追加序号
                    count = 1
                    while os.path.exists(new_name):
                        new_name = f"{clean_name}_{count}{ext}"
                        count += 1
                    
                    # 执行重命名操作
                    os.rename(filename, new_name)
                    print(f'重命名成功: {filename} -> {new_name}')
                    
            except Exception as e:
                # 异常处理：打印错误信息但程序继续运行
                print(f'处理文件 {filename} 时出错: {str(e)}')

if __name__ == '__main__':
    """程序入口：直接调用主处理函数"""
    rename_images()