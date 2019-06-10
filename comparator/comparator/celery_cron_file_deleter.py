from __future__ import absolute_import
import os, time
from celery import Celery
from django.conf import settings
from celery.decorators import task
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comparator.settings')
app = Celery('comparator')

LINUX_SERVER_PASSWD='d@ta$e'
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

now = time.time ()

def delete_file (path):
    for file in os.listdir (path):
        file = os.path.join (path, file)
        file_old = is_file_old (file)
        if os.path.isfile (file):
            if file_old:
                os.remove (file)
        elif os.path.isdir (file):
            if len(os.listdir (file)) and file_old:
                delete_file (file)
                if len(os.listdir (file)) == 0 and file_old:
                    os.rmdir(file)
            elif file_old:
                os.rmdir(file)


def is_file_old (file):
    if os.stat (file).st_mtime < now - 7 * 86400:
        return True
    else:
        return False


@task(name='tasks.file_deleter')
def file_deleter():
    import_file_dir = settings.MEDIA_ROOT
    output_file_dir = settings.OUTPUT_ROOT

    # changing the permission for the folders
    os.system("echo '{}' | sudo chmod -R 777 {}".format(LINUX_SERVER_PASSWD,import_file_dir))

    # checking uploaded file dir for deletion
    delete_file (import_file_dir)
    # checking output file dir for deletion
    delete_file (output_file_dir)