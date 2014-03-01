import argparse
import settings, qpm, containers, collections

class GenericAction:
    default_options = {}
    name = 'none'

    message_levels = [
        'error',
        'warning',
        'normal'
        'log',
    ]
    Message = collections.namedtuple('Message', ['level', 'message'])
    print_messages = True
    message_level = 0

    @classmethod 
    def get_default_options(cls):
        return settings.load_user_defaults([cls.name], {}, cls.default_options)

    @classmethod
    def fill_default_options(cls, options):
        default_options = cls.get_default_options()
        result_options = default_options.copy()
        settings.dict_add_recursive(options, result_options)
        return result_options

    @classmethod
    def cmd_line_to_options(cls, cmd_line):
        parser = cls.get_arg_parser()
        parsed = parser.parse_args(cmd_line);

        #return cls.fill_default_options(parsed)
        return vars(parsed)

    @classmethod
    def get_arg_parser(cls):
        return argparse.ArgumentParser()

    @classmethod
    def do(cls, options):
        action = cls(options)
        result = action.do()
        return result

    def __init__(self, options):
        self.options = self.fill_default_options(options)
        self.do_validation()

        self.result = containers.tree()
        self.result['completed'] = False
        self.result['success'] = False
        self.result['reason'] = None
        self.result['messages'] = list()

    def msg(self, string, level='log'):
        m = self.Message(level, string)
        self.result['messages'].append(m)

    def print_messages(self, level='log'):
        for msg in self.result['messages']:
            if msg.level <= self.message_levels.index(level):
                print '%s: %s' % (msg.level, msg.message)

    def do(self):
        pass    

    def do_validation(self):
        self.options['quark_path'] = qpm.validate_path(self.options['quark_path'])
        return True

    def get_result(self):
        return self.result
