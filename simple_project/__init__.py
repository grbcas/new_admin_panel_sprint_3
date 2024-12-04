from __future__ import absolute_import, unicode_literals
import sys
import os
from pathlib import Path
import django

# Set the default settings module
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
root_project_path = Path(__file__).parent.parent
sys.path.append(str(root_project_path))

os.environ.get('DJANGO_SETTINGS_MODULE')

# Initialize Django
django.setup()
