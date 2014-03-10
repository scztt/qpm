__author__ = 'fsc'
from semantic_version import Spec, Version
import logging
import time
from functools import partial
logging.basicConfig()

class FailedRequirement(Exception):
    def __init__(self, msg):
        self.msg = msg

class State(object):
    def __init__(self, requirements, selected, current_requirement, possibilities, depth):
        self.requirements = requirements
        self.selected = selected
        self.current_requirement = current_requirement
        self.possibilities = possibilities
        self.depth = depth
        self.name = self.current_requirement.name

    def name(self):
        return self.requirement['name']

class Repository(object):
    def __init__(self, data):
        self.data = data

    def get_versions(self, package):
        version_nums = self.data[package].keys()
        return map(lambda v: PackageVersion(package, v), version_nums)

    def get_dependencies(self, package_version):
        name = package_version.name
        version_num = package_version.version_string
        deps_data = self.data[name][version_num]
        return map(lambda d: PackageRequirement(d['name'], d['spec']), deps_data.values())

class PackageRequirement(object):
    def __init__(self, name, spec):
        self.name = name
        self.spec_string = spec
        self.spec = Spec(spec)
        self.required_by = []

    def match(self, version):
        return self.spec.match(version.version)

    def filter(self, versions):
        return filter(lambda v: self.spec.match(v.version), versions)

    def __repr__(self):
        return '"%s" %s' % (self.name, self.spec)

class PackageVersion(object):
    def __init__(self, name, version):
        self.name = name
        self.version_string = version
        self.version = Version.coerce(version)

    def __repr__(self):
        return '%s-%s' % (self.name, self.version)

class SimpleStrategy(object):
    def __init__(self):
        self.conservative = True
        self.avoid_prerelease = False

    def _order_version(self, a, b):
        cmp = a.version.__cmp__(b.version)
        if self.conservative:
            return -cmp
        else:
            return cmp

    def _should_include_version(self, ver):
        if self.avoid_prerelease and ver.version.prerelease:
            return False
        else:
            return True

    def filter_versions(self, requirement, version_list):
        version_list = filter(lambda v: self._should_include_version(v), version_list)
        return version_list

    def sort_versions(self, requirement, version_list):
        version_list = sorted(version_list, cmp=self._order_version)
        return version_list

class PackageResolver(object):
    def __init__(self, requirements, repo, strategy=SimpleStrategy()):
        self.initial_requirements = requirements
        self.repo = repo
        self.strategy = strategy
        self.logger = logging.getLogger('PackageResolver')
        self.logger.setLevel(logging.INFO)

    def resolve(self):
        self.start_time = time.time()
        self.states = []
        self.selected = dict()
        self.requirements = list(self.initial_requirements)
        self.errors = dict()
        self.depth = 0

        while self.requirements:
            current_req = self.requirements.pop(0)
            self.logger.info('Resolving: %s (%s requirements remaining)' % (current_req, len(self.requirements)))

            existing = self.selected.get(current_req.name)
            if existing:
                # We've already selected a version for this package
                if current_req.match(existing):
                    self.logger.info('%s compatible with current version %s' % (current_req, existing))
                    if self.errors.get(current_req.name):
                        del self.errors[current_req.name]

                else:
                    self.logger.info('%s conflicts with existing version %s' % (current_req, existing))
                    self.errors[current_req.name] = [existing.version, current_req.spec]

                    if current_req.required_by:
                        parent = current_req.required_by[-1]
                    else:
                        parent = None

                    parent_state = self.find_state(parent)
                    if parent_state and parent_state.possibilities:
                        # parent of current requirement has other possibilities, so try this
                        parent = self.handle_conflict(current_req)
                    else:
                        # try to handle by stepping back both the current requirement and the existing requirement
                        parent = self.handle_conflict(current_req, existing.required_by[-1])

                    if parent:
                        self.resolve_conflict(parent)
                    else:
                        raise FailedRequirement(self.states[-1])

            else:
                # We haven't yet selected a version for this package, so lets do it.
                versions = self.repo.get_versions(current_req.name)
                compatible_versions_spec = list(current_req.filter(versions))

                compatible_versions = self.strategy.filter_versions(current_req, compatible_versions_spec)
                compatible_versions = self.strategy.sort_versions(current_req, compatible_versions)

                if not(compatible_versions):
                    self.logger.error('No compatible versions for %s %s.' % (len(compatible_versions), current_req.name))
                    if compatible_versions_spec:
                        self.logger.error('The following matching versions were found but skipped because of package selection options: %s' % compatible_versions_spec)

                    if not(current_req.required_by):
                        raise Exception('Can\'t match a top level package. Try upgrading to a newer version.')
                    else:
                        self.errors[current_req.name] = [None, current_req]
                        parent = self.handle_conflict(current_req, self.states)
                        self.resolve_conflict(parent)
                else:
                    self.logger.info('Found %s versions for %s that match spec.' % (len(compatible_versions), current_req.name))

                    state = State(list(self.requirements), dict(self.selected), current_req, compatible_versions, self.depth)
                    self.states.append(state)
                    selected_version = state.possibilities.pop()
                    self.select_package(selected_version, current_req)

        self.finish_time = time.time()
        self.total_time = self.finish_time - self.start_time

    def select_package(self, package_version, current_req):
        self.logger.info('Selecting version %s' % package_version)
        package_version.required_by = list(current_req.required_by) + [current_req]
        self.selected[package_version.name] = package_version

        dependencies = self.repo.get_dependencies(package_version)
        self.logger.info('Adding dependencies for package %s: %s' % (package_version, dependencies))
        for dep in dependencies:
            dep.required_by = list(current_req.required_by) + [current_req]
            dep.depth = self.depth + 1
            self.requirements.append(dep)

    def handle_conflict(self, current_req_initial, existing_req_initial=None):
        current_req = current_req_initial
        existing_req = existing_req_initial

        while current_req or existing_req:

            # If there were other possible version choices in either the current or the already selected
            # package, return one of those
            current_req_state = self.find_state(current_req)
            existing_req_state = self.find_state(existing_req)
            if current_req_state and current_req_state.possibilities:
                return current_req
            if existing_req_state and existing_req_state.possibilities:
                return existing_req

            # If not, we need to walk one level back up the requirements chain and check again
            if current_req and current_req.required_by:
                current_req = current_req.required_by[-1]
            else:
                current_req = None

            if existing_req and existing_req.required_by:
                existing_req = existing_req.required_by[-1]
            else:
                existing_req = None
        raise Exception('Requirement for %s and existing requirement %s conflict, and no possible resolution can be found.' % (current_req, existing_req))

    def find_state(self, requirement):
        if requirement:
            for state in self.states:
                if requirement.name == state.name:
                    return state
        return None

    def reset_state(self, state):
        if not(state): raise Exception('Null state!')

        # roll states stack back to this state
        while self.states:
            if self.states.pop() == state:
                break

        self.requirements = list(state.requirements)
        self.selected = dict(state.selected)
        self.depth = state.depth

    def resolve_conflict(self, requirement):
        conflicting_state = self.find_state(requirement)
        self.logger.info('Rewinding to conflict state %s to find a new dependency resolution.' % conflicting_state)

        if conflicting_state and conflicting_state.possibilities:
            self.reset_state(conflicting_state)
            selected_version = conflicting_state.possibilities.pop()
            current_requirement = conflicting_state.current_requirement
            self.select_package(selected_version, current_requirement)

            # If state has other possible versions remaining, keep it around
            if conflicting_state.possibilities:
                self.states.append(conflicting_state)
        else:
            raise FailedRequirement()

    def rewind_to_conflicting_state(self, conflicting_requirement):
        if conflicting_requirement:
            while self.states:
                state = self.states.pop()
                if conflicting_requirement.name == state.name:
                    return state
        raise Exception('failed to rewind? bad.')

if __name__ == '__main__':
    # some testing shit
    import random
    random.seed(13)

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
                'c': {'name': 'c', 'spec': '>=1'},
            },
            '1': {
                'b': {'name': 'b', 'spec': '<=1'},
                'c': {'name': 'c', 'spec': '<=1'},
            }
        },
        'b': {
            '1.0.0-b1': {
                'c': {'name': 'c', 'spec': '>=1'},
            },
            '2': {
                'c': {'name': 'c', 'spec': '>=2'},
            },
            '1': {
                'c': {'name': 'c', 'spec': '>=1'},
            }
        },
        'c': {
            '2': {
                'a': {'name': 'a', 'spec': '<2'},
                'b': {'name': 'b', 'spec': '<2'},
                'no-install': {'name': 'no-install', 'spec': '>=0'}
            },
            '1': {
                'a': {'name': 'a', 'spec': '>=1'},
                'b': {'name': 'b', 'spec': '>=1'},
            }
        },
        'no-install': { '1': {} }
    }

    print package_deps
    base_reqs = [
        PackageRequirement('Jenine', '>=0.3')
    ]

    strategy = SimpleStrategy()
    strategy.avoid_prerelease = False
    strategy.conservative = True
    pr = PackageResolver(base_reqs, Repository(package_deps), strategy)
    pr.resolve()
    selected = pr.selected
    for key, val in selected.items():
        print '%s: %s' % (key, val)


