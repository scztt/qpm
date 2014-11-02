__author__ = 'fsc'
from core import *
import sclang

handler.register(QPMTestBaseController)
handler.register(QPMOutput)
handler.register(sclang.SCLang_Base)
handler.register(sclang.SCLang_Execute)
handler.register(sclang.SCLang_ListTests)
handler.register(sclang.SCLang_RunTest)
