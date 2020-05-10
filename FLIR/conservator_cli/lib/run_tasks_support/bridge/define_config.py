import os
from datetime import datetime

import blessed

from FLIR.dataset_toolkit.lib.run_tasks_support import path_manip

t = blessed.Terminal()


def setup_environment(task=None, **kwargs):
    for k, v in sorted(kwargs["env"].items()):
        print(t.bold_black("{:>30}: {}".format(k, v)))
        os.environ[k] = v


""" Emits a 'config_out' dictionary. Any input posargs must be incoming dictionaries, and they will
be applied in-order to override the config_out values.
@param include_datetime: If True, include keys and values for "%Y", "%y", "%m", "%d", "%H", "%M", "%S" based on curren time.
"""


def define_config(*posargs, config_out={}, include_datetime=False, task=None):

    # Override config values
    for posarg in posargs:
        if not isinstance(posarg, dict):
            raise Exception("In 'define_config' got a positional argument that is not a dictionary. Check inputs. arg={}".format(posarg))
        config_out.update(posarg)

    # Create pattern values for datetime
    if include_datetime:
        now = datetime.now()
        for pattern in ["%Y", "%y", "%m", "%d", "%H", "%M", "%S"]:
            config_out[pattern] = now.strftime(pattern)
        config_out["hash"] = "0x{}".format(os.urandom(2).hex())

    # Interpolate strings in config.
    for i in range(len(config_out)):
        for k, v in config_out.items():
            if isinstance(v, str):
                config_out[k] = v.format(**config_out)

    # Expand environment variables
    config_out = path_manip.json_expandvars(config_out)

    print(t.bold_black(str(config_out)))
    return config_out


exports = [setup_environment, define_config]
