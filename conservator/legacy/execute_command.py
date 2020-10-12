import subprocess


def execute_command(args=[], silent=False, cwd=None, abort_on_failure=False, env=None):
    # Run command
    cmd_str = " ".join(args)
    print(cmd_str)
    stdout = stderr = [None, subprocess.PIPE][silent]
    status = subprocess.run(args, cwd=cwd, stdout=stdout, stderr=stderr, env=env).returncode

    # Report possible error
    if status != 0 and abort_on_failure:
        raise Exception("execute_command failed: {}".format(" ".join(cmd_str)))

    return status
