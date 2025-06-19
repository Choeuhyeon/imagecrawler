from .imagecrawler import ImageCrawler
from urllib.parse import urlparse
import argparse

parser = argparse.ArgumentParser(description="웹 페이지의 이미지를 크롤링합니다.")
parser.add_argument("url", help="크롤링할 웹 페이지의 URL")
parser.add_argument("—path", "-p", help="이미지가 다운로드 될 경로")

args = parser.parse_args()
path = args.path

if not path:
    # 다운로드 경로를 설정해주지 않으면 도메인 이름을 다운로드 경로로 설정
    path = urlparse(args.url).netloc

ImageCrawler().run(args.url, path)