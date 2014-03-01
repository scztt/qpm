import os.path

class Package:
    def __init__(self, path):
        self.root_path = path
        self.quark_file = LocalDataFile(path, 'quark.json', options={'create': False})

    def get_dependencies(self):
        dependencies = 

