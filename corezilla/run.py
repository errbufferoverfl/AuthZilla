# -*- coding: utf-8 -*-
"""Create an application instance."""
import os

from corezilla.app import create_app
from corezilla.config.default import Configuration  # Production configuration
from corezilla.config.dev import DevConfiguration  # Development configuration

# Check the current environment using the FLASK_ENV environment variable
env = os.getenv('FLASK_ENV', 'production')  # Default to 'production' if FLASK_ENV is not set

if env == 'development':
    print("Booting Flask app using development configuration.")
    CONFIG = DevConfiguration()
else:
    print("Booting Flask app using production configuration.")
    CONFIG = Configuration()

app = create_app(CONFIG)

if __name__ == '__main__':
    app.run()
