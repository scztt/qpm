""" Qpm base controller."""

from cement.core.controller import CementBaseController, expose

class qpmBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'SuperCollider test and installation tool'
        arguments = [
            (['-f', '--foo'], 
             dict(help='the notorious foo option', dest='foo', action='store',
                  metavar='TEXT') ),
            ]

    @expose(hide=True)
    def default(self):
        raise NotImplementedError
