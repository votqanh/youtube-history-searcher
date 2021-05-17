import re
from datetime import datetime
import glob
import json
import os
import zipfile
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import interface
from main import TEMP_FOLDER

foo = True
user = None
s = "Logging you in"


def download(username, password):
    global foo, user, s
    counter = 0

    options = Options()
    options.headless = True

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", TEMP_FOLDER)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/x-zip, "
                                                                "application/x-zip-compressed")

    path = '/Users/anhvo/Downloads/geckodriver'

    # headless browser downloads YT history from Google Takeout
    with webdriver.Firefox(executable_path=path, firefox_profile=fp, options=options) as driver:
        driver.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
        driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()

        # sometimes login page is different - completely different elements
        if '- Google Accounts' not in driver.title:
            print("Unable to download your history. Please try again later.")
            foo = False
            return

        # re-try-catch at exact point exception occurred after 0.1s wait
        # TODO: put all this in a wrapper function to not repeat counter increment
        while True:
            try:
                right = False if counter == 0 else True

                while not right:
                    if counter == 0:
                        driver.find_element_by_xpath('//input[@type="email"]').send_keys(username)
                        counter += 1

                    if counter == 1:
                        driver.find_element_by_id('identifierNext').click()
                        counter += 1

                    inv = '//div[@class="rFrNMe N3Hzgf jjwyfe vHVGub zKHdkd sdJrJc Tyc9J CDELXb k0tWj IYewr"]'
                    right, _, counter = valid(driver, inv, 0, 0)

                right = False if counter == 2 else True

                while not right:
                    if counter == 2:
                        driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
                        counter += 1

                    if counter == 3:
                        driver.find_element_by_id('passwordNext').click()
                        counter += 1

                    inv = '//div[@class="SdBahf VxoKGd Jj6Lae"]'
                    right, password, counter = valid(driver, inv, 1, 2, password)

                if counter == 4:
                    foo = False
                    user = interface.new_search(2)
                    brand = interface.account()
                    foo = True

                    s = "Downloading your history"

                    counter += 1

                if counter == 5:
                    driver.get('https://takeout.google.com/u/0/settings/takeout')
                    if brand:
                        driver.find_element_by_xpath(
                            '/html/body/div[2]/header/div[2]/div[3]/div[1]/div[2]/div/a/img').click()
                        driver.find_element_by_xpath('//a[contains(@class, "gb_Ub gb_8b") and contains(.//div, "Brand '
                                                     'account")]').click()  # brand account takeout
                    counter += 1
                    sleep(1)
                    driver.switch_to.window(driver.window_handles[1])  # switch to new window

                if counter == 6:
                    el = driver.find_element_by_xpath('//*[@id="i6"]/div/div[1]/div[2]/button[2]')
                    driver.execute_script("arguments[0].click();", el)  # deselect all
                    counter += 1

                if counter == 7:
                    el = driver.find_element_by_xpath('//*[contains(@name,"YouTube and YouTube Music")]')
                    driver.implicitly_wait(20)
                    driver.execute_script("arguments[0].click();", el)  # select YT and YT Music
                    counter += 1

                if counter == 8:
                    el = driver.find_element_by_xpath('//div[contains(@class, "gGfIad") and contains(.//div, "Watch '
                                                      'and search history")]/div[2]/div[2]/div/button')
                    driver.execute_script("arguments[0].click();", el)  # select all YT data included

                    el = driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[8]/div/div[2]/span/div[2]/button[2]')
                    driver.execute_script("arguments[0].click();", el)  # deselect all
                    counter += 1

                if counter == 9:
                    driver.implicitly_wait(1)
                    el = driver.find_element_by_id('c1')
                    driver.execute_script("arguments[0].click();", el)  # select history

                    driver.implicitly_wait(1)
                    el = driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[8]/div/div[2]/div[3]/div[2]')
                    driver.execute_script("arguments[0].click();", el)  # click ok
                    counter += 1

                if counter == 10:
                    driver.implicitly_wait(1)
                    el = driver.find_element_by_xpath('//div[(@data-id="youtube")]//div[2]//div[1]//div[1]//button[1]')
                    driver.execute_script("arguments[0].click();", el)  # select format

                    sleep(0.2)

                    driver.implicitly_wait(1)
                    el = driver.find_element_by_xpath('//div[(@data-value="text/html")]')
                    driver.execute_script("arguments[0].click();", el)  # click drop-down menu

                    sleep(0.2)

                    el = driver.find_element_by_xpath('//div[@soy-server-key="5:pZtlf"]//div[2]')
                    driver.execute_script("arguments[0].click();", el)  # click json

                    sleep(0.2)

                    el = driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[2]/div[2]/div[2]/span')
                    driver.execute_script("arguments[0].click();", el)  # click ok
                    counter += 1

                if counter == 11:
                    el = driver.find_element_by_xpath('//*[@id="i6"]/div/div[2]/button')
                    driver.execute_script("arguments[0].click();", el)  # click next step
                    counter += 1

                if counter == 12:
                    el = driver.find_element_by_xpath('//*[@id="i9"]/div/div[2]/button')
                    driver.execute_script("arguments[0].click();", el)  # click create export
                    counter += 1

                    # wait for export to be created
                    sleep(2)

                if counter == 13:
                    url = 'https://takeout.google.com' + \
                          (f'/u/0/b/{[i for i in re.split("https://takeout.google.com/u/0/b/|/", driver.current_url) if i.isnumeric()][0]}' if brand else '') + '/takeout/downloads '
                    driver.get(url)
                    counter += 1

                # if element "Export in progress" exists then wait until it doesn't anymore
                if driver.find_elements_by_xpath('/html/body/c-wiz/c-wiz/div/div[3]/c-wiz/div/div[4]/div[1]/div/div[1]') \
                        and (counter == 14 or counter == 17):
                    while driver.find_elements_by_xpath('/html/body/c-wiz/c-wiz/div/div[3]/c-wiz/div/div[4]/div['
                                                        '1]/div/div[1]'):
                        sleep(1)
                    counter += 1
                elif counter == 14 or counter == 17:
                    counter += 1

                if counter == 15:
                    driver.find_element_by_xpath('/html/body/c-wiz/c-wiz/div/div[3]/c-wiz/div/div[4]/div/table/tbody['
                                                 '1]/tr[1]/td[6]/div/div/a').click()
                    counter += 1

                    sleep(1)

                right = False

                if driver.find_elements_by_xpath('/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div['
                                                 '1]/div/form/span/section/div/div/div[1]') and counter == 16:
                    while not right:
                        driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
                        driver.find_element_by_id('passwordNext').click()
                        right, password, _ = valid(driver, inv, 1, 2, password)

                    counter += 1

                # wait for export if it's exporting
                # this block is only executed once
                if counter == 17:
                    continue

                # wait for zip to finish downloading
                while not any(x.startswith('takeout') for x in os.listdir(TEMP_FOLDER)):
                    sleep(0.5)

                break

            except Exception as e:
                sleep(0.1)
                driver.get_screenshot_as_file('error.png')
                with open('error_log.txt', 'w') as f:
                    f.write(f'{datetime.now().date()}\n')
                    f.write(f'Counter {counter} and stack trace:\n{e}\n\n')

    try:
        list_of_files = glob.glob(TEMP_FOLDER + '/*.zip')
        latest_file = max(list_of_files, key=os.path.getctime)

        with zipfile.ZipFile(latest_file, 'r') as zip_ref:
            zip_ref.extractall(TEMP_FOLDER)
            zip_ref.close()

        os.remove(latest_file)
    except zipfile.BadZipFile:
        print("\rnot a zip                                  ")

    foo = False


def process(duration, time, end, l):
    HISTORY = json.load(open(l[1], "r"))

    videoids = []
    cnt = 0

    TODAY = datetime.now().date()
    start = TODAY if time == 0 else end
    scope = start - duration

    for i, j in enumerate(HISTORY):
        try:
            url = j["titleUrl"]
        except KeyError:
            continue

        date = j["time"][0:10]
        date_time_obj = datetime.strptime(date, '%Y-%m-%d').date()
        b = date_time_obj <= start if start == TODAY else date_time_obj < start
        videoid = url[-11:]

        if b:
            if scope <= date_time_obj:
                if not videoids.count(videoid):
                    videoids.append(videoid)
                    cnt += 1
            else:
                break

    if cnt == 0:
        return 0, scope

    interface.stack.append(f" {cnt} video" + ("s" if cnt > 1 else ""))
    interface.stack.append((videoids, scope))

    return 1,


def valid(driver, inv, num, cnt, pwd=None):
    global foo

    if not driver.find_elements_by_xpath(inv):
        return True, pwd if num == 1 else None, cnt + 2

    foo = False
    st = interface.enter_again(num)
    foo = True

    driver.implicitly_wait(10)
    return False, st, cnt
