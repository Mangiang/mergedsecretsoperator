from datetime import datetime
from kubernetes import client, config

def get_now():
    t = datetime.now()
    s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
    return s[:-3]

def print_info(msg: str, context:str, obj: str = None):
    print(f"[{get_now()}] {context}\t[INFO\t] {f'[{obj}] ' if obj else ''}{msg}")

def get_namespace(meta: dict) -> str:
    return meta['namespace'] if meta['namespace'] else 'default'