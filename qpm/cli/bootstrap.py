""" Qpm bootstrapping."""
__author__ = 'fsc'

# All built-in application controllers should be imported, and registered
# in this file in the same way as qpmBaseController.

from cement.core import handler
from qpm.cli.controllers.base import qpmBaseController
from core import *
import sclang

def load():
    handler.register(QPMBaseController)
    handler.register(QPMOutput)
    handler.register(sclang.SCLang_Base)
    handler.register(sclang.SCLang_Execute)
    handler.register(sclang.SCLang_ListTests)
    handler.register(sclang.SCLang_RunTest)



