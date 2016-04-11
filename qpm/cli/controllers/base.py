""" Qpm base controller."""
import os
from cement.core.controller import CementBaseController, expose

class SCLang_Base(CementBaseController):
    class Meta:
        label = 'sc'
        description = 'SuperCollider test and installation tool'
        stacked_on = 'base'
        stacked_type = 'embedded'
        description = 'do things with sclang'

    @expose(hide=True)
    def default(self):
        raise NotImplementedError

class SCLang_AbstractBase(CementBaseController):
    class Meta:
        stacked_on = 'sc'
        stacked_type = 'nested'
        base_arguments = [
            (['-p', '--path'], dict(default=os.getcwd(), help='Path to supercollider installation or config.yaml')),
            (['-i', '--include'], dict(default=[], nargs='*', help='Path to include in ClassLib')),
            (['-e', '--exclude'], dict(default=[], nargs='*', help='Path to exclude in ClassLib')),
			(['-o', '--print-output'], {
				'action': 'store_true',
				'help': 'print output of sclang'
			})
        ]

    def _collect(self):
        (arguments, commands) = super(SCLang_AbstractBase, self)._collect()
        return (arguments + self._meta.base_arguments, commands)