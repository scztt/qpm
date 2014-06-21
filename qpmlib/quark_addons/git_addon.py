import os.path
from pydispatch import dispatcher
from git import Git, Repo

from .. import util
from .. import settings

class GitAddon(object):
    name = 'init'
    default_options = {
        'git': False,
    }

    def __init__(self):
        dispatcher.connect(self.arg_parser, 'qpm.init:arg_parser')
        dispatcher.connect(self.created_quark, 'qpm.init:created_quark')

    def arg_parser(self, sender, parser):
        parser.add_argument('--git', '-g', action='store_true', help='initialize git repo for quark', default=self.default_options['git'])

    def created_quark(self, sender, new_quark):
        options = sender.options

        if self.git_is_installed():
            g = Git(options['path'])
            g.init()

            default_ignore = os.path.join(os.path.dirname(__file__), '..', 'default_gitignore.txt')
            ignore_path = os.path.join(options['path'], '.gitignore')
            with open(ignore_path, 'w') as ignore_file, open(default_ignore, 'r') as default_file:
                ignore_file.write(default_file.read())
                user_ignores = settings.user_gitignore()
                if user_ignores:
                    ignore_file.write('\n#SUPPLIED FROM ~/.qpmignore\n\n')
                    ignore_file.write(user_ignores)

            g.add(new_quark.get_quarkfile_path(options['path']))
            g.commit(m='Created quarkfile.')

            g.add('.gitignore')
            g.commit(m='Created gitignore.')

            g.add('.')
            if Repo(options['path']).is_dirty():
                g.commit(m='Initial commit of existing files.')

            g.tag(options['version'])

        else:
            self.msg(
                'WARNING: Git is not installed. Try http://git-scm.com/ or run the following:\n'
                + '\truby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"; brew install git'
            )

    def git_is_installed(self):
        import git
        version = git.cmd.Git("/").version()
        if version:
            return True

    def init_git(self, interactive=False):
        import git
        r = git.Repo()
        config = r.config_writer('global')
        name = config.get('user', 'name')
        email = config.get('user', 'email')
        return

addon = GitAddon