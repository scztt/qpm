from cement.core import handler, controller
from core import *


def run(args):
	app = QPMApp(output_handler=QPMOutput)
	try:
		app.setup()
		app.run()
	finally:
		app.close()