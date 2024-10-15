import os
import requests
import subprocess
import urllib.parse
import sys

# 强制使用 UTF-8 编码来避免处理非ASCII字符时的问题
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# URL解码函数
def decode_url_filename(url):
    # 从URL获取文件名并解码
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)
    decoded_filename = urllib.parse.unquote(filename)  # 确保解码为UTF-8字符
    return decoded_filename

# 流式下载文件函数
def download_file(url, download_path):
    # 解码后的文件名
    filename = decode_url_filename(url)
    filepath = os.path.join(download_path, filename)

    # 使用流式传输下载文件
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"文件已下载: {filepath}")
        return filepath
    else:
        raise Exception(f"下载失败，状态码: {response.status_code}")

# 解压 RAR 文件函数
def extract_rar(rar_file, extract_to):
    # 创建解压目录
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # 使用 UTF-8 编码执行命令
    try:
        result = subprocess.run(['unrar', 'x', '-y', rar_file, extract_to], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"解压成功: {rar_file}")
            # 解压成功后删除原始 RAR 文件
            os.remove(rar_file)
            print(f"已删除原始压缩文件: {rar_file}")
        else:
            print(f"解压失败: {result.stderr}")
            raise Exception("解压失败")
    except UnicodeEncodeError as e:
        print(f"编码错误: {e}")
        raise

# 压缩为 RAR 分卷文件函数
def create_rar(source_dir, output_dir, filename):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{filename}.part1.rar")

    # 切换到 source_dir 目录下并压缩内容，确保压缩包中不包含绝对路径
    original_cwd = os.getcwd()  # 记录当前工作目录
    os.chdir(source_dir)  # 切换到要压缩的目录

    # 调用 rar 命令进行分卷压缩，添加10%的恢复记录，分卷大小为2000M
    rar_command = [
        'rar', 'a', '-r', '-rr10p', '-v2000m', os.path.join(output_dir, f"{filename}.part"), './'
    ]

    try:
        result = subprocess.run(rar_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"成功压缩: {output_file}")
        else:
            print(f"压缩失败: {result.stderr}")
            raise Exception("压缩失败")
    finally:
        os.chdir(original_cwd)  # 压缩完后切换回原来的工作目录

# 主函数
def main():
    # 路径设置
    download_dir = '/root/vnbackup/rar/'
    extract_dir_base = '/root/vnbackup/extract/'
    output_dir = '/root/vnbackup/output/'

    # 创建所需目录
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not os.path.exists(extract_dir_base):
        os.makedirs(extract_dir_base)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 获取下载链接
        url = input("请输入文件下载链接: ")
        
        # 下载文件
        rar_file = download_file(url, download_dir)
        filename, extension = os.path.splitext(os.path.basename(rar_file))

        # 解压文件
        extract_dir = os.path.join(extract_dir_base, filename)
        extract_rar(rar_file, extract_dir)

        # 压缩解压后的文件夹
        create_rar(extract_dir, output_dir, filename)

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
