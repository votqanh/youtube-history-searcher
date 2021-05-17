Youtube History Searcher

This python application allows you to search for an English word or phrase in your YouTube history. Since the Youtube history search engine is limited to the video's metadata and cannot search its content, this program is the perfect tool to help you find the video you have been looking for.

Requirements:

  - Geckodriver latest release
  - Firefox latest release


Installation:

- After installing Geckodriver, please edit the path to geckodriver on line 35 history.py (e.g. /Users/myname/Downloads/geckodriver)

- Please go to Google > Profile > Manage Your Google Account > Security (https://myaccount.google.com/security) and turn off 2-Step Verification. Then, scroll down to Less secure app access and turn it on. This will allow our bot to retrieve your watch history.


Note:

Current version only available to Mac users. It is also assumed that you have a Youtube brand account. This application currently does not support normal accounts.

To download your history automatically, you must enter your Google email and password. You could check the source code to verify that this information is not stored anywhere.

You also have the option to manually download your history from Google Takeout via (https://takeout.google.com/settings/takeout?pli=1). The data must be in json format. You can then enter the path to this file when prompted.

If the application is unable to download your history (i.e. won't stop loading), please manually download your data.


Developer's Note:

Since the Youtube Data API (v3) deprecated watch history, there has been no 100% reliable way to access it. This application uses a selenium-based headless browser to fetch your watch history via Google Takeout.