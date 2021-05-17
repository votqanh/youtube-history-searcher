import datetime
import inspect
import os
import sys
import threading
from getpass import getpass
from itertools import cycle
from time import sleep
from time import time as ti

import enquiries
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import history
import video
from main import TEMP_FOLDER

stack = []
foo = None
w = None
st = None


class Font:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def welcome():
    for _ in range(3):
        print("\033[A                                             \033[A")
    print(Font.BOLD + "Welcome to DEJA                                                           " + Font.END)
    print("                                                                   ")
    print("Search any English word or phrase however far back in your YouTube history! If the transcript is "
          "available, of course :)\n")
    print(Font.BLUE + "COMMAND + DOUBLE CLICK" + Font.END + " to quickly open links.\n")


def path():
    DEFAULT = TEMP_FOLDER + "/Takeout/YouTube and YouTube Music/history/watch-history.json"
    OPTIONS = ["OK", "I don't have such file"]
    PATH_COMPLETER = WordCompleter(['/Users/anhvo/Downloads/brand test/Takeout/YouTube and YouTube '
                                    'Music/history/watch-history.json',
                                    TEMP_FOLDER + '/', 'Downloads/', 'Takeout/', 'YouTube and YouTube '
                                                                                 'Music/history/watch-history.json'])

    print()
    local = enquiries.confirm("Have you downloaded your most recent YouTube history?")

    if local:
        p = prompt("Please enter the absolute path to this file: \t", completer=PATH_COMPLETER)
        while True:
            # check if file is .json before trying to open it
            while not p.endswith('.json'):
                exist = enquiries.choose("File must be in json format. Try again. ", OPTIONS)

                if exist != "OK":
                    return False, DEFAULT
                else:
                    p = prompt("My file path:\t", completer=PATH_COMPLETER)

            try:
                open(p, 'r')
                break
            except FileNotFoundError:
                exist = enquiries.choose("File not found. Try again.", OPTIONS)

                if exist != "OK":
                    return False, DEFAULT
                else:
                    p = prompt("My file path:\t", completer=PATH_COMPLETER)

        return local, p
    return local, DEFAULT


def new_search(req, new_line=None):
    res = []

    if req == 2:
        if new_line:
            print("\r                                           \n", end='')
        else:
            print("\r", end='')

        search = input("Which word/phrase do you want to search?\t")
        res.append(search)

    OPTIONS2 = ['Entire history', 'Custom range']
    choice = enquiries.choose("I want to search:", OPTIONS2)

    # TODO: there's a better way to do this: discard 'time'
    if choice == 'Entire history':
        duration = datetime.timedelta(days=100_000)
    else:
        s = enquiries.freetext("How many days in the past do you want to search?\t")
        while True:
            try:
                duration = datetime.timedelta(days=int(s))
                break
            except ValueError:
                s = enquiries.freetext("Enter a NUMBER for days\t")

    res.append(duration)
    return res


def login():
    print("Sign in")
    print("Use your Google Account\n")
    print(Font.RED + "Your credentials will " + Font.BOLD + "not" + Font.END, end=' ')
    print(Font.RED + "be stored anywhere." + Font.END)

    username = input("\nEmail or phone:\t")
    password = getpass("Password:\t")

    # clear login fields
    for _ in range(4):
        print("\033[A                                                    \033[A")

    return username, password


def enter_again(num):
    if num != 0:
        un = input("\rEnter a valid email or phone number")
        print("\033[A                             \033[A")
        return un
    else:
        pw = getpass("\rWrong password. Try again.\t")
        print("\033[A                             \033[A")
        return pw


def loading(f, a, b, s=None, c=None):
    global st, w, foo
    foo = True

    RES = ['|', '/', '-', '\\']
    spin = cycle(RES)
    nextelem = next(spin)

    frame = inspect.currentframe()
    args = inspect.getargvalues(frame)
    M = args.locals['f'].__name__ == 'main'
    DL = args.locals['f'].__name__ == 'download'

    args_list = [a, b]

    if M:
        args_list.append(c)

    T = threading.Thread(target=f, args=(*args_list,))
    T.setDaemon(True)
    T.start()

    while T.is_alive():
        if DL:
            foo = history.foo
        while foo:
            if DL:
                if not history.foo:
                    break
                s = history.s

            st = s

            while M:
                if not stack or not isinstance(stack[0], str):
                    sleep(0.1)
                else:
                    break

            if M:
                st += stack[0]

            thiselem, nextelem = nextelem, next(spin)
            sys.stdout.write(f'\r{st} {nextelem} ')
            sys.stdout.flush()
            T.join(0.2)

    while w is None and not DL:
        sleep(0.1)

    if w == 503:
        sys.stdout.write('\r                           \n')
    else:
        sys.stdout.write('\rDone!                      \n')


def print_unavailable(un):
    if un:
        print()
        print("\rWe couldn't check these videos because their transcripts aren't available :( :")
        for i, j in enumerate(un):
            print(f"youtube.com/watch?v={j}")
        un.clear()
    print()


def print_not_found(u, stat, num):
    global foo

    more = "more " if num else ""

    print_unavailable(u)
    foo = False
    print("\033[A                             \033[A")
    print('\n')
    try_again = enquiries.confirm(stat[:3] + more + stat[-28:])
    foo = True

    return try_again


def search_scope(time, duration, no_more):
    global foo

    foo = False
    c = 0
    STR = "No more videos. " if no_more else ""

    OPTIONS = ['Try a different keyword', 'Expand the scope']
    response = enquiries.choose(STR + "Pick an option", OPTIONS)

    if response == 'Try a different keyword':
        res = new_search(2)
        time = 0
    else:
        while True:
            dummy = new_search(1)[0] - duration

            if not str(dummy).startswith('-'):
                # clear "SCOPE..."
                for _ in range(c):
                    print("\033[A                                                                      \033[A")
                break
            else:
                print("SCOPE HAS TO BE LARGER THAN WHAT YOU STARTED OUT WITH. Try again.")
                c += 1

        res = dummy
        time += 1

    foo = True

    # res is duration or duration and search
    return time, res


# TODO: split this function into mini-functions
def main(search, duration, l):
    global foo, stack, w, st
    unavailable = []
    STATUS = "No matches found. Search again?"
    time = 0
    end = None
    w = 200

    # foo alternates between false and true to pause loading animation

    while True:
        start = ti()
        j = history.process(duration, time, end, l)

        if j[0] == 0:
            print("\rNo videos to search!     ")
            foo = False
            duration = new_search(1)[0]
            foo = True
            print("\033[A                              \033[A")
            end = j[1]
            time += 1
        else:
            j = stack[-1]
            videoids, end = j[0], j[1]

            # reset cnt for no (more) matches found every new search
            re = [0]

            for i, videoid in enumerate(videoids):
                # update number of videos
                stack.pop(0)
                if "Searching" in st:
                    st = st[0:9]
                stack.insert(0, f" {len(videoids) - i} video" + ("s" if len(videoids) - i > 1 else ""))

                cont = None
                try_again = None

                # re[-1] is always cnt
                re = video.check_transcript(videoid, search, re[-1])

                # no internet
                if re[0] == 503:
                    print(Font.RED + "\nNo Internet. Please connect to a network and try again." + Font.END)
                    print(re[-1])
                    foo = False
                    w = re[0]
                    return

                # transcript unavailable
                if re[0] == 404:
                    unavailable.append(videoid)
                    if i != len(videoids) - 1:
                        continue
                    # redirect downstream
                    else:
                        re[0] = False

                # print match and unavailable list
                if re[0]:
                    print(f"\rTime elapsed: {ti() - start}                      ")
                    foo = False
                    print('\r                           \n', end='')
                    print(Font.BOLD + '\rFound!' + Font.END)
                    print(re[2], Font.BLUE + Font.UNDERLINE + re[1] + Font.END)
                    print_unavailable(unavailable)
                    cont = enquiries.confirm("Continue?")
                    foo = True

                else:
                    if i == len(videoids) - 1:
                        print("\033[A                             \033[A")
                        try_again = print_not_found(unavailable, STATUS, re[-1])
                    else:
                        continue

                # break out of M loop and foo loop:
                if not cont and not try_again:
                    stack = [None]
                    foo = False
                    return

                elif cont:
                    if len(videoids) - i != 1:
                        continue
                    else:
                        time, res = search_scope(time, duration, True)
                        search, duration = (*res,) if isinstance(res, list) else (search, res)

                else:
                    time, res = search_scope(time, duration, False)
                    search, duration = (*res,) if isinstance(res, list) else (search, res)

                stack.clear()


def account():
    brand = enquiries.confirm("Do you have a YouTube channel?")
    return brand


if __name__ == '__main__':
    login()
