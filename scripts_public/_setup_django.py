"""
@summary: setup django 环境，便于独立脚本调用django模型等相关对象
"""
import os
import platform
import sys

import django


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, BASE_DIR)
# sys.path.insert(0, os.path.join(BASE_DIR, 'v3'))

if platform.system() == 'Linux':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReserveDownloadSignleBackend.settings")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReserveDownloadSignleBackend.settings")

django.setup()
