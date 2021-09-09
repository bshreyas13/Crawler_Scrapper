## LinkedIn Crawler/Scraper

Platform and Packages used are as listed below.
Python3 is a pre-requisite. The following packages will be required as well:
1. time
2. BeautifulSoup ( pip install BeautifulSoup4)
3. selenium (pip install selenium)
4. re
5. json

Chorme Driver will also be required. 
Download chromedriver here : https://chromedriver.chromium.org/

Once Downloaded place chromedriver.exe in the working directory of the script.

Now the script can be run from the command line (after naviagting to the working directory) as shown below

```shell
python3 LinkedIn_Scrapper.py -u "your username" -p "your password" -sq "First and last name + other query for serach"

```
example:
 
```shell
python3 LinkedIn_Scrapper.py -u xyz@gmail.com -p abc123 -sq "Shreyas Bhat virginia tech"

```
Handle -u / --username is the LinkedIn username.
Handle -p / --password is the LinkedIn password.
Handle -sq / --search query requires First name Last Name and an additional identifier.
All three arguments are required.

Note:

The script output messes up the postiion and description when there are multiple positions under the same company. 
This has to do with the way the html tags are organized in this case and will be handled in furture versions.




