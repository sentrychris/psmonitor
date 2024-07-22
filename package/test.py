import os
import sys

print(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..')))