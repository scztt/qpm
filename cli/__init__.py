import core

def run(args):
	app = core.QPMApp(output_handler=core.QPMOutput)
	try:
		app.setup()
		app.run()
	finally:
		app.close()