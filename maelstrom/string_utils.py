def entab(original) -> str:
    nl = "\n" # not allowed to have '\' in f string
    tab = "\t"
    return f'{tab}{original.replace(nl, nl + tab)}'

def length_of_longest(strs: list) -> int:
    if len(strs) == 0:
        return 0
    return max([len(str(s)) for s in strs])
