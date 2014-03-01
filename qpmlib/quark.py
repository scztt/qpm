import qpm
import os, os.path, json, collections, stat

import settings

quark_file_name = "quark.json"

def get_quarkfile_path(base_path):
    return os.path.join(base_path, quark_file_name)

def get_existing_quark(pathname):
    quark_file = get_quarkfile_path(pathname)
    if os.path.exists(quark_file):
        return Quark(pathname)
    else:
        return None

class Quark:
    default_options = {
        'read_only': False
    }

    def __init__(self, path, options={}):
        self.options = settings.load_user_defaults('Quark', options, self.default_options)

        self.path = path
        self.read_only = self.options['read_only']
        self.quarkfile_path = os.path.join(path, quark_file_name)
        self.checkout_quarkfile()

    def checkout_quarkfile(self):
        if not(os.path.exists(self.quarkfile_path)):
            f = open(self.quarkfile_path, 'w')
            f.write('{}')
            f.close()

        self.load()

    def checkin_quarkfile(self):
        self.save()

    def set_read_only(self, read_only):
        if self.read_only != read_only:
            self.read_only = read_only
            if self.read_only:
                self.set_write_permissions(False)
            else:
                self.set_write_permissions(True)

    def set_write_permissions(self, value):
        # stat.S_IWRITE
        pass

    def load(self):
        with open(self.quarkfile_path, 'r') as f:
            settings = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
            if not(settings): settings = collections.OrderedDict()

            self.name = settings.get('name')
            self.version = settings.get('version')
            self.sc_version = settings.get('sc_version')
            self.ide = settings.get('ide')
            self.dependencies = settings.get('dependencies', collections.OrderedDict())
            self.author = settings.get('author')
            self.email = settings.get('email')

    def save(self):
        with open(self.quarkfile_path, 'w') as f:
            settings = collections.OrderedDict()

            settings['name'] = self.name
            settings['version'] = self.version
            settings['sc_version'] = self.sc_version
            settings['ide'] = self.ide
            settings['dependencies'] = self.dependencies
            settings['author'] = self.author
            settings['email'] = self.email

            f.write(json.dumps(settings, indent=2))

    def add_dependency(self, name, version):
        self.dependencies[name] = version

    def get_dependencies(self):
        return self.dependencies

    def list_installed(self):
        pass

    def is_installed(self, package):
        pass






