"""Qpm main application entry point."""

import traceback
import sys
from cement.core import foundation, backend
from cement.core.exc import FrameworkError, CaughtSignal
from qpm.core.app import *
from qpm.core.exc import *
from .. import settings

global_app = None

class qpmTestApp(QPMApp):
    """A test app that is better suited for testing."""
    class Meta:
        argv = []
        config_files = []

def main():
    if os.environ.get('QPM_DEBUG') != '0':
        sys.argv += ['--debug']

    global global_app
    global_app = QPMApp(output_handler=QPMOutput, config_defaults=settings.defaults)
    try:
        global_app.setup()
        global_app.run()
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
        global_app.close()

if __name__ == '__main__':
    main()
