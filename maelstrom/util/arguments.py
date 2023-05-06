import argparse
from maelstrom.util.config import Config, set_global_config

def parse_args():
    """
    Parses command-line arguments, then sets the global config accordingly
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="log debug information. Best combined with -n", action="store_true")
    parser.add_argument("-n", "--no-cls", help="turn off clearing the terminal each screen", action="store_true")
    parser.add_argument("-s", "--store", help="stores enemy and level data", action="store_true")
    parser.add_argument("-t", "--test", help="run Game::test instead of Game::run", action="store_true")
    user_input = parser.parse_args()
    set_global_config(Config(
        debug = user_input.debug,
        keep_output = user_input.no_cls,
        store = user_input.store,
        test = user_input.test
    ))