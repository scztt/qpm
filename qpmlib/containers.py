import collections

def tree():
    return collections.defaultdict(tree)

def result_object():
    obj = tree()
    obj['completed'] = False
    obj['success'] = False
    obj['reason'] = None
    obj['messages'] = list()
    return obj

