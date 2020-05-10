import sys

import blessed

from task_runner.runner import Runner
from FLIR.dataset_toolkit.lib.run_tasks_support.load_json import load_json
from FLIR.dataset_toolkit.lib.run_tasks_support.common import add_define_environment_task, add_define_config_task, report_task, parse_args


t = blessed.Terminal()


#  """ Runs the task graph for executing a performance test """
def performance_test(env_vars, config_vars, cache=None):

    if cache is None:
        cache = dict()
    print(t.bold_white("Load config: {}".format(config_vars["config"])))
    task_runner_config = load_json(config_vars["config"])

    # Parse command-line and auto-generate tasks for setting up the environment variables and cli-config
    add_define_environment_task(task_runner_config, env_vars)
    add_define_config_task(task_runner_config, config_vars)

    print(t.bold_white("Parse task graph"))
    runner = Runner(task_runner_config)

    print(t.bold_white("Execute task graph"))
    print("{t.bold_white_on_blue}[{}]{t.normal}{t.bold_white} {}".format(
        task_runner_config.get("name", "Performance Test"), task_runner_config.get("description", ""), t=t))
    status = runner.execute(pre_execute_fn=report_task, cache=cache)

    return status


def main(argv):
    env_vars, config_vars = parse_args()
    return performance_test(env_vars, config_vars)


if __name__ == "__main__":
    main(sys.argv[1:])
    # On any failure, an exception is raised, and the system exit.
    # Otherwise, considers that it ran correctly and return 0.
    sys.exit(0)
