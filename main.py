import os
import shutil
from traceback import print_exc

import history
import interface

l = False,

current_dir = os.getcwd()
TEMP_FOLDER = current_dir + '/deja/temp'


def main():
    global l

    interface.welcome()

    l = interface.path()

    # create deja directory
    DEJA_FOLDER = current_dir + '/deja'
    if not os.path.exists(DEJA_FOLDER):
        os.mkdir(DEJA_FOLDER)

    if not l[0]:
        user = interface.login()
        if not os.path.exists(TEMP_FOLDER):
            os.mkdir(TEMP_FOLDER)
        interface.loading(history.download, user[0], user[1])
        user = history.user
    else:
        user = interface.new_search(2, True)
    interface.loading(f=interface.main, a=user[0], b=user[1], c=l, s="Searching")

    if not l[0]:
        shutil.rmtree(TEMP_FOLDER)

    if interface.w is 200:
        print("\nThank you for using Deja. Have a wonderful day!\n")


if __name__ == "__main__":
    try:
        main()
    except:
        if not l[0]:
            shutil.rmtree(TEMP_FOLDER)
        print_exc()
