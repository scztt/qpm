from cement.utils import test

from test_class import QPMAppTest

class UnitTestCases(test.CementTestCase):
	app_class = QPMAppTest

	def test_app_launch(self):
		self.app = QPMAppTest(argv=['sc', 'execute', '   "Hello world";   ', '--path', '/Users/fsc/Documents/_code/SuperCollider-qt-compilation/build-qt5-current/INSTALL/SuperCollider/SuperCollider.app/Contents/MacOS/sclang'])
		self.app.setup()
		self.app.run()
		data, output = self.app.last_rendered

		self.eq(data['result'], 'Hello world')