import subprocess

if __name__ == "__main__":
    import sys
    import os
    import time

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from microdrop_utils.broker_server_helpers import dramatiq_workers, redis_server_context

    # Need to run with a dramatiq broker context since app requires plugins that use dramatiq
    with redis_server_context():

        while True:
            time.sleep(0.001)