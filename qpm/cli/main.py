"""Qpm main application entry point."""

from cement.core import foundation, backend
from cement.core.exc import FrameworkError, CaughtSignal
from qpm.core.app import *
from qpm.core.exc import *

class qpmTestApp(QPMApp):
    """A test app that is better suited for testing."""
    class Meta:
        argv = []
        config_files = []
        
def main():
    app = QPMApp()
    try:
        app.setup()
        app.run()
    except qpmError as e:
        print(e)
    except FrameworkError as e:
        print(e)
    except CaughtSignal as e:
        print(e)
    finally:
        app.close()
    
if __name__ == '__main__':
    main()