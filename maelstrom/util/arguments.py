import argparse



class Options:
    def __init__(self, debug, noCls, store, test):
        self.debug = debug
        self.noCls = noCls
        self.store = store
        self.test = test

    def __str__(self)->str:
        return "\n".join([
            "Command Line Options",
            f'* debug: {self.debug}',
            f'* noCls: {self.noCls}',
            f'* store: {self.store}',
            f'* test: {self.test}'
        ])

def getOptions():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="log debug information. Best combined with -n", action="store_true")
    parser.add_argument("-n", "--no-cls", help="turn off clearing the terminal each screen", action="store_true")
    parser.add_argument("-s", "--store", help="stores enemy and level data", action="store_true")
    parser.add_argument("-t", "--test", help="run Game::test instead of Game::run", action="store_true")
    userInput = parser.parse_args()
    print(userInput)
    return Options(
        userInput.debug,
        userInput.no_cls,
        userInput.store,
        userInput.test
    )

