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
        driver.get("http://localhost:3000/routing")
        driver.find_element_by_id("formGridDeliveryLimit").click()
        driver.find_element_by_id("formGridDeliveryLimit").clear()
        driver.find_element_by_id("formGridDeliveryLimit").send_keys("10")
        driver.find_element_by_id("formGridDurationLimit").clear()
        driver.find_element_by_id("formGridDurationLimit").send_keys("4")
        driver.find_element_by_id("formGridDeparture").click()
        driver.find_element_by_id("search_input").click()
        driver.find_element_by_xpath("//div[@id='multiselectContainerReact']/div[2]/ul/li").click()
        driver.find_element_by_id("search_input").click()
        driver.find_element_by_xpath("//div[@id='multiselectContainerReact']/div[2]/ul/li[2]").click()
        driver.find_element_by_xpath("//div[@id='multiselectContainerReact']/div").click()
        driver.find_element_by_xpath("//div[@id='multiselectContainerReact']/div[2]/ul/li[3]").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        #ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
        # self.assertEqual("No address could be geocoded.", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div/div/div/div").text)
        # self.assertEqual("NO_LOCATIONS_ASSIGNED", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div/div[2]/div/div/div").text)
    
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
