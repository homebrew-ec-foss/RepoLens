import os
from collections import defaultdict

CONFIG = {"debug": True, "max_retries": 3}

def fetch_data(url, retries=3):
    for attempt in range(retries):
        try:
            return _make_request(url)
        except ConnectionError as e:
            print(f"Attempt {attempt} failed: {e}")
    return None

def _make_request(url):
    if not url.startswith("http"):
        raise ValueError("Invalid URL")
    return {"status": 200, "url": url}

class DataProcessor:
    def __init__(self, source, transform=None):
        self.source = source
        self.transform = transform or (lambda x: x)
        self.cache = defaultdict(list)

    @property
    def is_ready(self):
        return self.source is not None

    def process(self, items):
        results = [self.transform(item) for item in items if item is not None]
        self.cache["processed"].extend(results)
        return results

    def summary(self):
        return {
            "total": len(self.cache["processed"]),
            "config": CONFIG,
        }

async def run_pipeline(urls):
    processor = DataProcessor(source="api", transform=str.upper)
    data = [fetch_data(u) for u in urls]
    return processor.process(data)

if __name__ == "__main__":
    result = run_pipeline(["http://a.com", "http://b.com"])
    print(result)