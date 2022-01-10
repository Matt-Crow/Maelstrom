import argparse



class Options:
    def __init__(self, store, test):
        self.store = store
        self.test = test

    def __str__(self)->str:
        return "\n".join([
            "Command Line Options",
            f'* store: {self.store}',
            f'* test: {self.test}'
        ])

def getOptions():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--store", help="stores enemy and level data", action="store_true")
    parser.add_argument("-t", "--test", help="run Game::test instead of Game::run", action="store_true")
    userInput = parser.parse_args()

    return Options(userInput.store, userInput.test)
