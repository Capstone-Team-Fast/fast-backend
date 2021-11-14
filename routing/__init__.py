import os
import sys

from backend import settings

cwd = os.getcwd()
sys.path.insert(0, cwd)
for path in os.listdir():
    p = os.path.join(cwd, path)
    if path[0] != '.' and p not in sys.path:
        sys.path.insert(0, p)

for path in sys.path:
    print(path)

print('BASE DIR', settings.BASE_DIR)
