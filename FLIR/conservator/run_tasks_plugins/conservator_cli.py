from FLIR.conservator.cli import main


def conservator_cli(cmd_class, cmd_name, args=(), log="INFO", task=None):
    cli_cmd = [cmd_class, cmd_name] + list(args)
    result = main(cli_cmd, standalone_mode=False)
    print("RESULT:", result)
    return result


exports = [conservator_cli]
