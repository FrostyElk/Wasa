"""
 WarFallen Server Administration
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import os
import sys

from app import create_app

sys.path.append(os.path.dirname(__name__))

# For Elastic Beanstalk
application = create_app()

if __name__ == '__main__':
    application.run()
