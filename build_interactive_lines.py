import os
import re
import html
import json

ROOT_DIR = r"c:\Users\navne\StudioProjects\Compose-demo"

def read_file(rel_path):
    full_path = os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

print("Building line-by-line master suite...")

