import os
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from fake_useragent import UserAgent

class ImageCrawler:
    chrome_header = {'User-Agent' : UserAgent().chrome}
    INVALID_CHARACTERS = r'<>:"/\|?*&'
    IMAGE_EXTENSIONS = [
        '.jpeg', '.jpg', '.png', '.gif', '.tiff', '.psd', '.pdf', '.eps', '.ai', '.indd', '.raw',
    ]

    def __init__(self, buffer_size = 1024, maximum_filename_length = 100):
        self.buffer_size = buffer_size
        self.maximum_filename_length = maximum_filename_length

    @staticmethod
    def is_valid(url):
        """
        이미지의 URL 이 유효한지 확인
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def _image_filename(self, url):
        """
        이미지의 파일 이름을 적절히 처리한 후 반환
        """
        # 이미지 이름을 소문자로 만듦
        filename = url.lower()
        # 파일 이름에 적합하지 않은 문자를 _ 로 치환
        for ch in self.INVALID_CHARACTERS:
            filename = filename.replace(ch, '_')

        for ext in self.IMAGE_EXTENSIONS:
            # 파일이름이 확장자로 잘 끝나면 스킵
            if filename.endswith(ext):
                break
            # 확장자가 파일이름에 존재하는데, 파일이름이 확장자로 끝나지 않으면 확장자를 추가해줌
            if ext in filename and not filename.endswith(ext):
                filename += ext
                break
        else:
            # 확장자가 존재하지 않으면 기본 확장자를 추가
            filename += self.IMAGE_EXTENSIONS[0]
        
        # 파일 이름이 너무 길어지지 않도록 적당히 잘라줌
        name_length = len(filename)
        if name_length > self.maximum_filename_length:
            filename = filename[name_length - self.maximum_filename_length:]

        return filename

    def download_image(self, url, download_path):
        """
        이미지를 `url` 로부터 다운로드받아서 `download_path` 에 저장
        """
        # 저장될 파일의 디렉토리가 존재하지 않으면 생성
        if not os.path.isdir(download_path):
            os.makedirs(download_path)

        filename = self._image_filename(url)
        filepath = os.path.join(download_path, filename)
        # 이미지가 이미 존재하면 스킵
        if os.path.isfile(filepath):
            return

        # 한번에 수신 받지 않고 여러번 나누어서 받음
        response = requests.get(url, headers=self.chrome_header, stream=True)
        with open(filepath, "wb") as f:
            for data in response.iter_content(self.buffer_size):
                f.write(data)

    def get_all_images(self, url):
        """
        웹 페이지의 모든 이미지의 URL 을 반환
        """
        soup = BeautifulSoup(requests.get(url, headers=self.chrome_header).text, "lxml")
        urls = []
        for img in soup.find_all("img"):
            img_url = img.attrs.get("src")
            # img 태그가 src 속성을 가지고 있지 않은 경우 스킵
            if not img_url:
                continue
            # 이미지 URL 을 도메인과 연결
            img_url = urljoin(url, img_url)
            # 이미지의 URL 이 유효하면 리스트에 추가
            if self.is_valid(img_url):
                urls.append(img_url)

        return urls

    def run(self, url, download_path = None):
        imgs = self.get_all_images(url)
        if not download_path:
            download_path = urlparse(url).netloc
        for img in tqdm(imgs, f"{url} 의 이미지를 크롤링 중"):
            self.download_image(img, download_path)