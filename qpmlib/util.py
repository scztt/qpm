from semantic_version import Version, Spec

def is_mac():
    return True

def is_win():
    return False

def is_lin():
    return False

def safe_name(package_name):
    return package_name

def ask(question, validator=None):
    result = None
    while not(result):
        result = raw_input(question + '\n')
        if validator:
            result = validator(result)
    return result

def to_spec(spec_string):
    spec_string = spec_string.replace('~', '>=')
    try:
        spec = Spec(spec_string)
    except:
        spec = Spec('==' + spec_string)
    return spec


def sort_versions(versions):
    sem_version_map = dict()
    for v in versions:
        sem_version_map[Version.coerce(v)] = v

    sorted_sem_versions = sorted(sem_version_map.keys())
    return map(lambda v: sem_version_map[v], sorted_sem_versions)

def select_versions(spec, versions):
    spec = to_spec(spec)

    sem_version_map = dict()
    for v in versions:
        sem_version_map[Version.coerce(v)] = v

    selected_version = spec.select(sem_version_map.keys())
    return sem_version_map[selected_version]
