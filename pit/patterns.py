"""
This file contains regex patterns
"""
import re

XY = re.compile(r'^(?P<x>[-+]?((\d*\.\d+)|(\d+))) (?P<y>[-+]?((\d*\.\d+)|(\d+)))$')  # pattern to search X Y
