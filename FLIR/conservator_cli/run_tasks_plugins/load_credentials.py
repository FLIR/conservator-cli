import os
from argparse import Namespace 
import json

import blessed

t = blessed.Terminal()

def load_credentials(cred_filename, task=None):
    with open(cred_filename, "r") as cred_f:
        cred_dict = json.load(cred_f)
    return Namespace(**cred_dict)

exports = [load_credentials]
