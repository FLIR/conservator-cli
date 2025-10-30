from FLIR.conservator.cli import main


def conservator_cli(cmd, args=(), log="INFO", task=None):
    log_arg = "--log=" + log
    cli_cmd = [log_arg, cmd] + list(args)
    result = main(cli_cmd, standalone_mode=False)
    print("RESULT:", result)
    return result


exports = [conservator_cli]
