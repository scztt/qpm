from util import sort_versions
from semantic_version import Spec, Version
from localfile import LocalDataFile

class Package:
    def __init__(self, data):
        self.data = data

    def versions(self):
        return self.data['versions'].keys()

    def latest_version(self):
        sorted_versions = sort_versions(self.versions())
        return sorted_versions[-1]

    def dependencies(self, version=None):
        if (not(version)):
            version = self.latest_version()

        return self.data['versions'][version].get('dependencies', dict())

    def find_matches(self, spec):
        pass



