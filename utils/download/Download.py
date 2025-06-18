import os
import threading
import requests

class Downloader:
    def __init__(self, url, filename=None, num_threads=4):
        self.url = url
        self.num_threads = num_threads
        self.filename = filename or self.url.split('/')[-1]
        self.filesize = int(requests.head(url).headers['Content-Length'])
        self.part_files = [f"{self.filename}.part{i}" for i in range(self.num_threads)]
        self.downloaded_sizes = [0] * self.num_threads
        self.lock = threading.Lock()

    def download_part(self, start, end, index):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(self.url, headers=headers, stream=True)
        with open(self.part_files[index], 'wb') as f:
            for chunk in response.iter_content(chunk_size=self.chunk_select(self.filesize)):
                if chunk:
                    f.write(chunk)
                    with self.lock:
                        self.downloaded_sizes[index] += len(chunk)

    def combine_parts(self):
        with open(self.filename, 'wb') as output:
            for part_file in self.part_files:
                with open(part_file, 'rb') as pf:
                    output.write(pf.read())
                os.remove(part_file)

    def download(self):
        part_size = self.filesize // self.num_threads
        threads = []

        for i in range(self.num_threads):
            start = i * part_size
            end = self.filesize - 1 if i == self.num_threads - 1 else (start + part_size - 1)
            t = threading.Thread(target=self.download_part, args=(start, end, i))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.combine_parts()
        self.log("✅ Download complete:", self.filename)

    def perCentdownload(self) -> float:
        with self.lock:
            total_downloaded = sum(self.downloaded_sizes)
        return (total_downloaded / self.filesize) * 100

    def log(self, *x):
        pass

    def chunk_select(self, size: int | float) -> int:
        MB = 1024 * 1024
        if size >= 1024 * MB:         # ≥ 1GB
            return 1048576            # 1MB
        elif size >= 300 * MB:        # ~300MB - 1GB
            return 262144             # 256KB
        elif size >= 100 * MB:        # ~100MB - 300MB
            return 65536              # 64KB
        else:
            return 8192               # 8KB
