import sys
import subprocess
import pkg_resources
import importlib
import os

req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
try:
    if not os.path.exists(req_file):
        raise FileNotFoundError(f"requirements.txt文件不存在于路径：{req_file}")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
    importlib.reload(pkg_resources)
except subprocess.CalledProcessError as e:
    print(f"依赖安装失败，请手动执行：{sys.executable} -m pip install -r {req_file}")
except FileNotFoundError as e:
    print(str(e))

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
