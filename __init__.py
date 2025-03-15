import sys
import subprocess
import pkg_resources
import importlib

try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', "requirements.txt"])
    importlib.reload(pkg_resources)
except subprocess.CalledProcessError as e:
    print(f"依赖安装失败，请手动执行：{sys.executable} -m pip install funasr transformers")

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
