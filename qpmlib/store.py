import util
from localfile import LocalDataFile
from remotefile import RemoteDataFile
from . import endpoints

import os, os.path, json, stat, time, collections, re, semantic_version

store_location = os.path.expanduser('~/Library/Application Support/SuperCollider/qpm')

base_repo_list = [
    'https://github.com/scztt/qpm/raw/master/sample_repo.json',
    'https://github.com/scztt/qpm/raw/master/sample_repo2.json'
]

repo_name_pattern = '[:/_\.]+'

class QuarkStore:
    @classmethod
    def create_dir(cls, dir):
        if not(os.path.exists(dir)):
            os.makedirs(dir)

    def __init__(self):
        global store_location
        self.repo_list_file = LocalDataFile(os.path.join(store_location, 'QPM Repositories.json'), options={
            'default_data': base_repo_list
        })

        self.repo_files = []
        self.local_repo_file = LocalDataFile(os.path.join(store_location, 'QPM Local Repository.json'), options={
            'default_data': {'_metadata': {
                'description': 'A repo file that tracks all local quarks. A quark is added to this repo when you "qpm init". This is NOT machine-transferrable.'
            }}
        })

        self.repo_cache_dir = os.path.join(store_location, 'Repository Cache')
        self.store_dir = os.path.join(store_location, 'Store')

        self.create_dir(self.repo_cache_dir)
        self.create_dir(self.store_dir)

        self.cache_days = 1
        self.repo_list = None

    def find_package_local(self, package_name, version_spec):
        result = None
        spec = semantic_version.Spec(version_spec)
        versions = self.find_versions_for_package_local(package_name)

        if versions:
            sem_versions = dict()
            for v in versions: sem_versions[semantic_version.Version(v)] = v
            best_match = spec.select(sem_versions)
            if best_match:
                result = os.path.join(self.store_dir, util.safe_name(package_name), sem_versions[best_match])

        return result

    def find_versions_for_package_local(self, package_name):
        result = None

        package_folder = os.path.join(self.store_dir, util.safe_name(package_name))
        if os.path.exists(package_folder):
            ver_folders = os.listdir(package_folder)
            versions = list()
            for version in ver_folders:
                if os.path.isdir(os.path.join(package_folder, version)):
                    try:                    
                        semver = semantic_version.Version(version)
                        versions.append(version)
                    except:
                        print 'Version not parsed correctly: %s' % version

            result = versions

        return result

    def find_package_repo(self, package_name):
        return self.get_package(package_name)

    def fetch_package(self, package_name, version_spec):
        spec = semantic_version.Spec(version_spec)
        package_repo = self.find_package_repo(package_name)

        if package_repo:
            sem_versions = dict()
            for version in package_repo['versions'].keys():
                try:
                    semver = semantic_version.Version(version)
                    sem_versions[semver] = [version, package_repo['versions'][version]]
                except:
                    print 'Version not parsed correctly: %s' % version

            best_match = spec.select(sem_versions.keys())
            if best_match:
                best_match_version = sem_versions[best_match][0]
                best_match_url = sem_versions[best_match][1]
                endpoint = endpoints.make_endpoint(best_match_url)
                if endpoint:
                    if endpoint.verify():
                        local_target = self.package_path(package_name, best_match_version)
                        get_result = endpoint.get_to(local_target)
                        if get_result:
                            print 'cached locally at %s: ' % local_target
                            return local_target
                        else:
                            print 'Endpoint get failed!'
                            return None


    def repo_to_filename(self, repo):
        return re.sub(repo_name_pattern, '-', repo)

    def repo_to_path(self, repo):
        local_file_name = self.repo_to_filename(repo)
        filename = os.path.join(self.repo_cache_dir, local_file_name)
        return filename

    def package_path(self, package_name, version):
        return os.path.join(self.store_dir, util.safe_name(package_name), version)

    def get_repo_files(self):
        if not(self.repo_files): 
            self.update_repos()
            self.repo_files.append(self.local_repo_file)
        return self.repo_files

    def update_repos(self):
        repo_list = self.repo_list_file.get()
        self.repo_files = []
        for repo in repo_list:
            repo_file = RemoteDataFile(repo, self.repo_to_path(repo))
            self.repo_files.append(repo_file)

    def get_package(self, package_name):
        for repo in self.get_repo_files():
            repo_data = repo.get()
            if repo_data.has_key(package_name):
                package = repo_data[package_name]
                print 'package: %s' % package
                return package
        return None

    def get_dependencies(self, package_name, package_version):
        package = self.get_package(package_name)
        return package.get('dependencies', {})

    def collect_dependencies(self, to_collect={}, deps_dict={}):
        while to_collect:
            name, spec = to_collect.popitem()
            versions_set = deps_dict.get(name, set())
            if not(spec in versions_set):
                versions_set.add(spec)
            deps_dict[dep] = versions_set

        return deps_dict

    def collect_packages(self):
        packages = dict()
        repo_list = self.get_repo_files()
        for repo in repo_list:
            repo_data = repo.get()
            for name, package in repo_data.iteritems():
                if package.has_key('versions'):
                    versions = package['versions'].keys()
                    packages[name] = packages.get(name, set())
                    packages[name].update(set(versions)    )

        return packages
