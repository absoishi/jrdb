import os
import sys
import requests
from bs4 import BeautifulSoup
import argparse

def download_files_from_page(url, username, password, download_folder, target_extension):
    # Basic認証でページにアクセス
    response = requests.get(url, auth=(username, password))
    response.raise_for_status()

    # レスポンス内容をBeautifulSoupで解析
    soup = BeautifulSoup(response.content, 'html.parser')

    # 指定された拡張子のリンクを取得
    target_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(target_extension)]

    # ダウンロードフォルダが存在しない場合は作成
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for link in target_links:
        # 絶対URLに変換
        file_url = requests.compat.urljoin(url, link)
        
        # ファイルをダウンロード
        file_response = requests.get(file_url, stream=True, auth=(username, password))
        file_response.raise_for_status()

        # ダウンロードしたファイルを保存
        file_name = os.path.join(download_folder, os.path.basename(link))
        with open(file_name, 'wb') as file:
            for chunk in file_response.iter_content(chunk_size=8192):
                file.write(chunk)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files from a webpage with Basic Auth.')
    parser.add_argument('url', help='The URL of the webpage.')
    parser.add_argument('username', help='Username for Basic Auth.')
    parser.add_argument('password', help='Password for Basic Auth.')
    parser.add_argument('-d', '--download_folder', default='./downloaded_files', help='Directory to save the downloaded files.')
    parser.add_argument('-e', '--extension', default='.lzh', help='Target file extension to download.')

    args = parser.parse_args()
    
    download_files_from_page(args.url, args.username, args.password, args.download_folder, args.extension)
