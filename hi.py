# I don't know very much about this code snippet.
# Just followed the instructions provided by a post on Stackoverflow to avoid getting sync error :-D
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "local_settings.py")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

#python manage.py shell_plus --notebook