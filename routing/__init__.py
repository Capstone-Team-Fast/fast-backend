import os
import sys

working_dir = os.path.abspath(os.path.join('..'))
parent = os.path.dirname(working_dir)

if parent not in sys.path:
    sys.path.append(parent)

for s in ['backend', 'backend\\models']:
    p = os.path.join(parent, s)
    if p not in sys.path:
        sys.path.append(p)
