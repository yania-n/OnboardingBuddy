import os, sys, json, sqlite3, uuid, re, hashlib
from pathlib import Path

def write_f(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + '', encoding='utf-8')
    print('Wrote', path)

print('Builder running...')