"""Qpm main application entry point."""

from cement.core import foundation, backend
from cement.core.exc import FrameworkError, CaughtSignal
from qpm.core import exc

class qpmApp(foundation.CementApp):
    class Meta:
        bootstrap = 'qpm.cli.bootstrap'
        label = 'qpm'

class qpmTestApp(qpmApp):
    """A test app that is better suited for testing."""
    class Meta:
        argv = []
        config_files = []
        
def main():
    app = qpmApp()
    try:
        app.setup()
        app.run()
    except exc.qpmError as e:
        print(e)
    except FrameworkError as e:
        print(e)
    except CaughtSignal as e:
        print(e)
    finally:
        app.close()
    
if __name__ == '__main__':
    main()