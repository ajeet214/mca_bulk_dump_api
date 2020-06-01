import io
import os
import time
import re
from datetime import datetime
import warnings
from time import sleep
from selenium import webdriver
import pymysql
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from google.cloud import vision
from google.cloud.vision import types
from config import Config
warnings.filterwarnings('ignore')

# Common Regex
cin_regex = "^([L|U]{1})([0-9]{5})([A-Za-z]{2})([0-9]{4})([A-Za-z]{3})([0-9]{6})$"
fcrn_regex = "^([F]{1})([0-9]{5})$"
llpin_regex = "^([A-Za-z]{3})-([0-9]{4})$"
fllpin_regex = "^([F]{1})([A-Za-z]{3})-([0-9]{4})$"


class SignatoryDetails:

    def __init__(self):

        self.conn = pymysql.connect(host=Config.DATABASE_CONFIG['host'],
                                    port=Config.DATABASE_CONFIG['port'],
                                    user=Config.DATABASE_CONFIG['user'],
                                    passwd=Config.DATABASE_CONFIG['password'],
                                    db=Config.DATABASE_CONFIG['database']
                                    )
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS signatorieDetails '
                            '(cin_llpin VARCHAR(50), '
                            'company_type_flag VARCHAR(10), '
                            'created_date VARCHAR(20), '
                            'updated_date VARCHAR(50), '
                            'din_pan VARCHAR(30), '
                            'full_name VARCHAR(100), '
                            'present_residential_address VARCHAR(200), '
                            'designation VARCHAR(100), '
                            'date_of_appointment VARCHAR(50), '
                            'whether_dsc_registered VARCHAR(20), '
                            'expiry_date_of_dsc VARCHAR(20), '
                            'surrendered_din VARCHAR(100), '
                            'id VARCHAR(200) NOT NULL, PRIMARY KEY (id))')

        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"] = "OCR-First-a06746332b80.json"
        self.client = vision.ImageAnnotatorClient()
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        # self.driver = webdriver.Remote(
        #     command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
        #         'port'] + '/wd/hub',
        #     desired_capabilities=options.to_capabilities(),
        # )

    def data_parser(self, cin_llpin):

        if re.match(cin_regex, str(cin_llpin).upper()):
            flag = 'CIN'
        elif re.match(llpin_regex, str(cin_llpin).upper()):
            flag = 'LLPIN'
        else:
            flag = 'REJECT'

        self.driver.find_element_by_xpath('//*[@id="signatoryDetails"]')

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # print(soup.prettify())
        # print(soup.find('table', id='signatoryDetails'))
        all_rows = soup.find('table', id='signatoryDetails').find('tbody').find_all('tr')

        for each_tr in all_rows:
            temp_lst = each_tr.text.split('\n')[1:-1]
            print(temp_lst)

            company_type_flag = flag
            created_date = time.strftime('%Y-%m-%d %H:%M:%S')
            updated_date = time.strftime('%Y-%m-%d %H:%M:%S')

            din_pan = temp_lst[0] if temp_lst[0] != '-' and temp_lst[0] != '' and temp_lst[0] != 'NULL' and temp_lst[
                0] != 'null' else None
            full_name = temp_lst[1] if temp_lst[1] != '-' and temp_lst[1] != '' and temp_lst[1] != 'NULL' and temp_lst[
                1] != 'null' else None
            present_residential_address = temp_lst[2] if temp_lst[2] != '-' and temp_lst[2] != '' and temp_lst[
                2] != 'NULL' and temp_lst[2] != 'null' else None
            designation = temp_lst[3] if temp_lst[3] != '-' and temp_lst[3] != '' and temp_lst[3] != 'NULL' and temp_lst[
                3] != 'null' else None

            if temp_lst[4] != '-' and temp_lst[4] != '' and temp_lst[4] != 'NULL' and temp_lst[4] != 'null':
                d = temp_lst[4]
                date = datetime.strptime(d, "%d/%m/%Y")
                date = datetime.strftime(date, "%Y-%m-%d")
                date_of_appointment = date
            else:
                date_of_appointment = None

            whether_dsc_registered = temp_lst[5] if temp_lst[5] != '-' and temp_lst[5] != '' else None

            if temp_lst[6] != '-' and temp_lst[6] != '' and temp_lst[6] != 'NULL' and temp_lst[6] != 'null':
                d = temp_lst[6]
                date = datetime.strptime(d, "%d/%m/%Y")
                date = datetime.strftime(date, "%Y-%m-%d")
                expiry_date_of_dsc = date
            else:
                expiry_date_of_dsc = None

            surrendered_din = temp_lst[7] if temp_lst[7] != '-' and temp_lst[7] != '' and temp_lst[7] != 'NULL' and \
                                             temp_lst[7] != 'null' else None

            data = self.cursor.execute("select * from signatorieDetails where id=%s",
                                       cin_llpin+company_type_flag+din_pan)
            # print(BeautifulSoup(each_tr, 'html.parser').find_all('td'))
            if data == 0:
                sql = "INSERT INTO signatorieDetails " \
                      "(cin_llpin, company_type_flag, " \
                      "created_date, updated_date, din_pan, full_name, present_residential_address, " \
                      "designation, date_of_appointment, " \
                      "whether_dsc_registered, expiry_date_of_dsc," \
                      "surrendered_din, id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
                val = (cin_llpin, company_type_flag, created_date, updated_date, din_pan, full_name,
                       present_residential_address, designation, date_of_appointment, whether_dsc_registered,
                       expiry_date_of_dsc, surrendered_din, cin_llpin+company_type_flag+din_pan)
    
                self.cursor.execute(sql, val)
            elif data == 1:
                sql = "UPDATE signatorieDetails " \
                      "SET cin_llpin=%s, company_type_flag=%s, " \
                      "updated_date=%s, din_pan=%s, full_name=%s, present_residential_address=%s, " \
                      "designation=%s, date_of_appointment=%s, " \
                      "whether_dsc_registered=%s, expiry_date_of_dsc=%s," \
                      "surrendered_din=%s, id=%s WHERE id=%s"

                val = (cin_llpin, company_type_flag, updated_date, din_pan, full_name,
                       present_residential_address, designation, date_of_appointment, whether_dsc_registered,
                       expiry_date_of_dsc, surrendered_din, cin_llpin+company_type_flag+din_pan, cin_llpin+company_type_flag+din_pan)
                self.cursor.execute(sql, val)

        self.conn.commit()

    @staticmethod
    def captcha_processor(extracted_text):
        processed_txt = extracted_text.replace('!', 'l'). \
            replace('ɔ', 'o').replace(',1', 'n').replace(':', 'r').replace("w'", "w"). \
            replace('/', 'y').replace(' ', '').replace('D', 'b').lower()
        return processed_txt

    def captcha_fetcher(self):

        captcha_image = self.driver.find_element_by_css_selector('#captcha')
        file_path = "../captcha_image.png"
        captcha_image.screenshot(filename=file_path)

        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)
        response = self.client.text_detection(image=image)
        print("unprocessed captcha1: ", response.text_annotations[0].description.split('\n')[0])
        captcha_text = response.text_annotations[1].description
        print("unprocessed captcha2: ", captcha_text)
        processed_text = self.captcha_processor(captcha_text)
        return processed_text

    def scrapper(self, cin_llpin):

        filtered_list = list()
        for i in cin_llpin:
            if re.match(cin_regex, str(i).upper()) or re.match(llpin_regex, str(i).upper()):
                filtered_list.append(i)

        url = 'http://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do'
        self.driver.get(url)
        sleep(1)
        self.driver.find_element_by_xpath('//*[@class="sbinner"]/span[1]/button').click()
        self.driver.find_element_by_xpath('//*[@id="services"]').click()
        # self.driver.get('http://www.mca.gov.in/mcafoportal/showIndexOfCharges.do')
        self.driver.find_element_by_xpath('//*[@id="subnav-view"]/ul/li[4]').click()
        sleep(0.5)

        for each_number in filtered_list:
            print("----------------------------------")
            print('number: ', each_number)

            processed_text = self.captcha_fetcher()
            print("processed captcha2: ", processed_text)

            self.driver.find_element_by_xpath('//*[@id="companyID"]').clear()
            sleep(0.5)
            self.driver.find_element_by_xpath('//*[@id="companyID"]').send_keys(each_number)
            sleep(0.5)
            self.driver.find_element_by_xpath('//*[@id="userEnteredCaptcha"]').send_keys(processed_text)
            self.driver.find_element_by_xpath('//td/input[@type="submit"]').click()
            sleep(0.5)

            try:
                self.data_parser(each_number)
            except NoSuchElementException:

                error_text = self.driver.find_element_by_xpath('//*[@id="overlayCnt"]').text
                if error_text.startswith('Enter valid Letters'):
                    pass
                elif error_text.startswith('CIN/LLPIN must be of the pattern'):
                    print('It is not a valid cin/llp number')
                    self.driver.find_element_by_xpath('//*[@id="msgboxclose"]').click()
                    continue

                msg = True
                while msg:

                    sleep(0.5)
                    self.driver.find_element_by_xpath('//*[@id="msgboxclose"]').click()
                    try:
                        processed_text = self.captcha_fetcher()
                        sleep(0.2)
                        self.driver.find_element_by_xpath('//*[@id="userEnteredCaptcha"]').send_keys(processed_text)
                        self.driver.find_element_by_xpath('//td/input[@type="submit"]').click()
                        # print("trying")
                        try:
                            self.driver.find_element_by_xpath('//*[@id="msgboxclose"]')
                            # print("&&")
                        except NoSuchElementException:
                            msg = False
                    except NoSuchElementException:
                        print("in exception")
                    print(msg)

                sleep(0.5)
                self.data_parser(each_number)
            sleep(1)
        self.driver.close()


if __name__ == '__main__':
    Obj = SignatoryDetails()
    Obj.scrapper(['U27101CT2008PTC020561', 'U51504MH1993PTC251544', 'F01221', 'AAA-9391', 'FZZZ-9998'])
    # Obj.scrapper('U05000APTC111532')    #invalid number
