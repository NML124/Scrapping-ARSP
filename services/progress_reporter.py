from tqdm import tqdm

class ProgressReporter:
    def __init__(self, total, initial=0, desc=""):
        self.progress_bar = tqdm(total=total, initial=initial, desc=desc, unit="enterprise")
    def update(self, n=1):
        self.progress_bar.update(n)
    def close(self):
        self.progress_bar.close()