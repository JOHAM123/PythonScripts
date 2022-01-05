
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                                                               #
#                                                  URL GRABBER                                                                  #
#   1. Change path of chrome driver at line 14                                                                                  #
#   2. Copy below code and Run in CMD                                                                                           #
#   python url_grabber.py "https://www.ielove.co.jp/kodate/theme/k_shinchiku/" "https://www.ielove.co.jp/kodate/theme/k_chuko/" #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from selenium import webdriver
import csv
import sys
import mysql.connector

CHROME_DRIVER_PATH = "chromedriver.exe"
INITIAL_URL = "https://www.ielove.co.jp/"
CSV_FILE_PATH = 'city_url_list.csv'
CITY_FIELDS = ['city_name', 'city_url']
CSV_FIELD_NAMES = ["id", "provider", "kind",
                   "prefecture", "city", "name", "city_map_id"]
PREFECTURE_XPATH = "//*[@id='main']/div[4]/ul/dl/li/a"
CITY_XPATH = "//*[@class='reccomend bx city']/ul/li/a"
CITY_MAP_QUERY = "SELECT id FROM CITY_MAP where city_id in (SELECT id FROM CITIES where city_name = %s )"
CITY_MAP_INSERT_QUERY = "INSERT INTO QUERY_PARAMETERS (provider, kind, prefecture, city, name, city_map_id) VALUES(%s, %s, %s, %s, %s, %s); "
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="db_name"
)


def fetch_by_city_name(name):
    result = "0"
    cursor = mydb.cursor(buffered=True, dictionary=True)
    cursor.execute(CITY_MAP_QUERY, (name,))
    record = cursor.fetchone()
    if record is not None:
        result = record['id']
    cursor.close()
    return result


# def store_to_db(data):
#     cursor = mydb.cursor(buffered=True, dictionary=True)
#     cursor.execute(
#         CITY_MAP_INSERT_QUERY, (
#             data[CSV_FIELD_NAMES[1]],
#             data[CSV_FIELD_NAMES[2]],
#             data[CSV_FIELD_NAMES[3]],
#             data[CSV_FIELD_NAMES[4]],
#             data[CSV_FIELD_NAMES[5]],
#             data[CSV_FIELD_NAMES[6]],
#         ))

#     cursor.close()


def set_browser_driver():
    driver = webdriver.Chrome(
        executable_path=CHROME_DRIVER_PATH)
    return driver


def open_url(browser, url):

    handles = browser.window_handles
    new_browser_tab = browser.window_handles[len(handles) - 1]
    browser.switch_to.window(new_browser_tab)
    browser.get(url)
    browser.execute_script("window.open()")
    return browser


def fetch_url_list(url, url_list):

    driver = set_browser_driver()
    url_list = search_by_prefecture(url, driver, url_list)
    return url_list


def search_by_prefecture(url, browser, url_list):

    pref_url_list = fetch_url_by_xpath(browser, url, PREFECTURE_XPATH)

    for pref_url in pref_url_list:
        url_list = search_by_city(pref_url['url'], browser, url_list)

    return url_list


def search_by_city(url, browser, url_list):

    city_url_list = fetch_url_by_xpath(browser, url, CITY_XPATH)

    for city in city_url_list:
        url_list.append(
            {
                CITY_FIELDS[0]: city['name'].split(' ')[0],
                CITY_FIELDS[1]: city['url']
            })
    return url_list


def fetch_url_by_xpath(browser, url, path):
    _result = []
    browser = open_url(browser, url)

    element_list = browser.find_elements_by_xpath(path)

    for elem in element_list:
        _result.append(
            {"name": str(elem.text), "url": str(elem.get_attribute("href"))})

    browser.close()
    return _result


def write_csv(write_data):
    with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELD_NAMES)
        writer.writeheader()
        try:
            for item in write_data:
                data_items = {}
                for key in CSV_FIELD_NAMES:
                    data_items.update({str(key): item[str(key)]})
                # store_to_db(data_items)
                writer.writerow(data_items)
            print("write successfully")
        except Exception as e:
            print("Field names not matched", e)


def split_url(url):

    split_url = url.split('/')
    provider = '/'.join(split_url[:3]) + '/'
    kind = split_url[3] + '/'
    prefecture = '/'.join(split_url[4:])
    return provider, kind, prefecture


def convert_to_csv_format(data):
    data_items = []
    for index, item in enumerate(data):
        provider, kind, prefecture = split_url(item["city_url"])
        city_name = item["city_name"]
        city_map_id = fetch_by_city_name(city_name)
        data_items.append(
            {
                CSV_FIELD_NAMES[0]: index,
                CSV_FIELD_NAMES[1]: provider,
                CSV_FIELD_NAMES[2]: kind,
                CSV_FIELD_NAMES[3]: prefecture,
                CSV_FIELD_NAMES[4]: "null",
                CSV_FIELD_NAMES[5]: city_name,
                CSV_FIELD_NAMES[6]: city_map_id

            })
    return data_items


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print("The first parameter url must required.")
    else:
        url_list = []
        for url in sys.argv[1:]:
            url_list = fetch_url_list(url, url_list)
        data = convert_to_csv_format(url_list)
        write_csv(data)
