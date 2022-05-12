# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class UntitledTestCase(unittest.TestCase):
    def setUp(self):
        s = Service('../chromedriver.exe')
        self.driver = webdriver.Chrome(service=s)
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_untitled_test_case(self):
        driver = self.driver
        driver.get("http://localhost:3000/data")
        driver.find_element_by_id("formFile").click()
        driver.find_element_by_id("formFile").clear()
        driver.find_element_by_id("formFile").send_keys("C:\\fakepath\\Drivers.xlsx")
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[4]/div[2]/div/div/button").click()
        driver.find_element_by_id("search").click()
        driver.find_element_by_id("search").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("john")
        # self.assertEqual("John", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("jane")
        # self.assertEqual("Jane", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr[2]/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("alex")
        # self.assertEqual("Alexander", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("rahu")
        # self.assertEqual("Rahul", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("martin")
        # self.assertEqual("Martin", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div/div[2]/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("mark")
        # self.assertEqual("Mark", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("sha")
        # self.assertEqual("Shaine", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("thurst")
        # self.assertEqual("Thurston", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("ro")
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("ryan")
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div/div[2]/div").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
