__author__ = 'fsc'
import util
from semantic_version import Spec, Version
#from store import QuarkStore
from collections import defaultdict
from collections import namedtuple

global package_deps, errors
package_deps = None
errors = dict()
deps_for = dict()

class State(object):
    def __init__(self, reqs, selected, requirement, possibilities, depth):
        self.reqs = reqs
        self.selected = selected
        self.requirement = requirement
        self.possibilities = possibilities
        self.depth = depth
        self.name = self.requirement['name']

    def name(self):
        return self.requirement['name']

class FailedRequirement(Exception):
    def __init__(self, msg):
        self.msg = msg


def resolve(requirements, selected):
    global errors
    states = []
    depth = 0

    while requirements:
        current_requirement = requirements.pop(0)
        current_requirement['required_by'] = current_requirement.get('required_by', [])
        current_name = current_requirement['name']
        current_spec = current_requirement['spec']
        depth = len(current_requirement['required_by'])

        print (depth * '  ') + 'Resolving: %s %s' % (current_name, current_spec)
        existing = selected.get(current_name)

        if existing:
            if Spec(current_spec).match(Version.coerce(existing['version'])):
                # compatible with current selected version, so use this...
                if errors.get(current_name):
                    del errors[current_name]

                print (depth * '  ') + 'Using existing: %s-%s' % (current_name, existing['version'])
            else:
                print (depth * '  ') + 'Requirement %s %s conflicts with existing version %s-%s' % (current_name, current_spec, existing['name'], existing['version'])
                # NOT compatible with current selected version
                errors[current_name] = [existing['version'], current_spec]

                if current_requirement['required_by']:
                    parent = current_requirement['required_by'][-1]
                else:
                    parent = None

                if not(other_possible(parent, states)):
                    if existing['required_by']:
                        parent = handle_conflict(current_requirement, states, existing['required_by'][-1])
                    else:
                        parent = handle_conflict(current_requirement, states)

                if not(parent):
                    raise FailedRequirement(current_name)
                else:
                    requirements, selected, depth = resolve_conflict(parent, states)
        else:
            string_versions = package_deps[current_name].keys()
            version_map = dict()
            for v in string_versions: version_map[Version.coerce(v)] = v
            matching_versions = Spec(current_spec).filter(version_map.keys())
            matching_versions = map(lambda v: version_map[v], matching_versions)

            if not(matching_versions):
                print (depth * '  ') + 'No versions matching %s found for %s' % (current_spec, current_name)

                if not(current_requirement.get('required_by')):
                    # root level package failure - this is bad!
                    raise 'Root level package not found!'
                else:
                    errors[current_name] = [None, current_requirement]
                    parent = handle_conflict(current_requirement, states)
                    reqs, selected, depth = resolve_conflict(parent, states)
            else:
                # okay, some matching versions
                state = State(list(requirements), dict(selected), current_requirement, matching_versions, depth)
                states.append(state)
                possible_version = {
                    'name': current_name,
                    'version': state.possibilities.pop()
                }
                select_package(requirements, selected, possible_version, current_requirement)

    for package in selected.values():
        print "%s-%s" % (package['name'], package['version'])

def select_package(reqs, selected, selected_version, current_requirement):
    print '  Selecting %s-%s' % (selected_version['name'], selected_version['version'])
    selected_version['required_by'] = list(current_requirement['required_by'])
    selected_version['required_by'].append(current_requirement)
    selected[selected_version['name']] = selected_version

    dependencies = package_deps[selected_version['name']][selected_version['version']]
    print '  Adding dependencies for selected package: %s' % map(lambda d: '%s %s' % (d['name'], d['spec']), dependencies.values())
    for d in dependencies.values():
        d['required_by'] = list(current_requirement['required_by'])
        d['required_by'].append(current_requirement)
        reqs.append(d)

def handle_conflict(current, states, existing=None):
    print 'Handling conflict for requirement %s, %s' % (current['name'], current['spec'])

    while current or existing:
        current_state = find_state(current, states)
        existing_state = find_state(existing, states)

        if current_state and current_state.possibilities:
            return current
        if existing_state and existing_state.possibilities:
            return existing

        if existing:
            if existing['required_by']:
                existing = existing['required_by'][-1]
            else:
                print 'Conflict percolated to root!'
                print 'current: %s' % current
                print 'states: %s' % states
                print 'existing: %s' % existing
                raise "!!!"
        if current:
            if current['required_by']:
                current = current['required_by'][-1]
            else:
                print 'Conflict percolated to root!'
                print 'current: %s' % current
                print 'states: %s' % states
                print 'existing: %s' % existing
                raise '!!!'

def find_state(current, states):
    for state in states:
        if current and current['name'] == state.name:
            return state

def find_conflict_state(conflict, states):
    if conflict:
        while states:
            state = states.pop()
            if conflict['name'] == state.name:
                return state

def resolve_for_conflict(state):
    if not(state) or not(state.possibilities):
        raise FailedRequirement()

    reqs, selected, depth = list(state.reqs), dict(state.selected), state.depth
    requirement = state.requirement
    possible = {
        'name': state.name,
        'version': state.possibilities.pop()
    }
    print 'Choosing %s-%s to resolve conflict.' % (possible['name'], possible['version'])
    select_package(reqs, selected, possible, requirement)
    return reqs, selected, depth

def resolve_conflict(current, states):
    # Find the state where the conflict has occurred
    state = find_conflict_state(current, states)
    print ('Source of conflict %s-%s: %s' % (current['name'], current['spec'], state))

    # Resolve the conflicts by rewinding the state
    # when the conflicted gem was selected
    reqs, selected, depth = resolve_for_conflict(state)

    # Keep the state around if it still has other possibilities
    if state.possibilities:
        states.append(state)
    clear_search_cache()

    return reqs, selected, depth

def other_possible(conflict, states):
    if not(conflict): return None

    state = filter(lambda s: s.name == conflict['name'], states)
    if state:
        return state[0].possibilities
    else:
        return None

def clear_search_cache():
    global deps_for
    deps_for = dict()

if __name__ == '__main__':
    # some testing shit
    import random
    random.seed(134533)

    versions = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6']
    packages = [ 'Joaquin', 'Jenine', 'Portia', 'Micki', 'Jone', 'Wilfred', 'Fredericka', 'Deanne', 'Dolly', 'Joeann']
    package_deps = dict()
    for package in packages:
        package_deps[package] = dict()
        available_versions = list(versions)
        for i in range(0, 6):
            ver = random.choice(available_versions)
            available_versions.remove(ver)
            package_deps[package][ver] = dict()
            available_packages = list(packages)
            for i in range(0, random.randrange(2, 5)):
                pack = random.choice(available_packages)
                available_packages.remove(pack)
                package_deps[package][ver][pack] = {
                    'name': pack,
                    'spec': '>=' + str(random.choice(versions))
                }
    package_deps2 = {
        'a': {
            '2': {
                'b': {'name': 'b', 'spec': '>=2'},
                'c': {'name': 'c', 'spec': '>=2'},
            },
            '1': {
                'b': {'name': 'b', 'spec': '<=1'},
                'c': {'name': 'c', 'spec': '<=1'},
            }
        },
        'b': {
            '2': {
                'c': {'name': 'c', 'spec': '>=2'},
            },
            '1': {
                'c': {'name': 'c', 'spec': '>=1'},
            }
        },
        'c': {
            '2': {
                'a': {'name': 'a', 'spec': '<=2'},
                'b': {'name': 'b', 'spec': '>=2'},
            },
            '1': {
                'a': {'name': 'a', 'spec': '>=1'},
                'b': {'name': 'b', 'spec': '>=1'},
            }
        },
    }

    print package_deps
    base_reqs = [
        {'name': 'Wilfred', 'spec': '<=1'}
    ]

    resolve(base_reqs, {})

