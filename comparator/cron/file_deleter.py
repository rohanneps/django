import os, time

# crontab -e in terminal
# */1 * * * * $HOME/comparator/comparator/cron/cron.sh (save)

# monitor cron
# && curl -sm 30 k.wdt.io/<email>/<cron-name>?c=0_0_*_*_*
now = time.time ()


def delete_file (path):
    for file in os.listdir (path):

        file = os.path.join (path, file)
        # print file
        file_old = is_file_old (file)

        # if file
        if os.path.isfile (file):

            if file_old:
                os.remove(file)
                
        # if directory
        elif os.path.isdir (file):
            delete_file(file)
            if file_old:
                os.rmdir (file)
            else:
                delete_file (file)


def is_file_old (file):
    if os.stat (file).st_mtime < now - 7 * 86400:
        return True
    else:
        return False


if __name__ == '__main__':
    # import_file_dir = MEDIA_ROOT
    # output_file_dir = OUTPUT_ROOT

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    import_file_dir = os.path.join(BASE_DIR,'media')
    output_file_dir = os.path.join(BASE_DIR,'Comparator_Output')


    os.system("echo '{}' | sudo chmod -R 777 {}".format('',import_file_dir))
    # checking uploaded file dir for deletion
    delete_file (import_file_dir)
    # checking output file dir for deletion
    delete_file (output_file_dir)
