"""Qpm main application entry point."""

import traceback
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
        traceback.print_exc()
        print(e)
    except FrameworkError as e:
        traceback.print_exc()
        print(e)
    except CaughtSignal as e:
        traceback.print_exc()
        print(e)
    except Exception as e:
        print(e)
    finally:
        app.close()

if __name__ == '__main__':
    main()
