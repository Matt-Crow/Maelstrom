
def list_extend(my_list: list[any], *args):
    """
    Returns a shallow copy of the first list with shallow copies of args at the end.
    """
    result = list(my_list)
    result.extend(args)
    return result
