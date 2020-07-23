import os
from dotenv import load_dotenv

# Populate os.environ with variables from test.env
env_path = os.path.join(os.path.dirname(__file__),
                        "test.env")
load_dotenv(verbose=True,
            dotenv_path=env_path)

# With the pre-populated environment, load the example settings
from example_settings import *  # noqa: F401, F403

