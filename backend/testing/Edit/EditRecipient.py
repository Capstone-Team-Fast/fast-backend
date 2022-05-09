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
        driver.get("http://localhost:3000/driverDetail/25")
        driver.find_element_by_link_text("Return").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td[5]/a[2]").click()
        driver.find_element_by_name("first_name").click()
        driver.find_element_by_name("first_name").clear()
        driver.find_element_by_name("first_name").send_keys("Audiee")
        driver.find_element_by_name("last_name").click()
        driver.find_element_by_name("last_name").clear()
        driver.find_element_by_name("last_name").send_keys("Haylette")
        driver.find_element_by_id("formGridPhone").click()
        driver.find_element_by_id("formGridPhone").clear()
        driver.find_element_by_id("formGridPhone").send_keys("402-827-0991")
        driver.find_element_by_id("address").click()
        driver.find_element_by_id("address").clear()
        driver.find_element_by_id("address").send_keys("9028 Burt St")
        driver.find_element_by_id("room_number").click()
        driver.find_element_by_xpath("//div[@id='formGridCheckbox']/div[6]/label").click()
        driver.find_element_by_name("comments").click()
        driver.find_element_by_name("comments").clear()
        driver.find_element_by_name("comments").send_keys("This is a note.")
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/form/button").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/form/a/button").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td[5]/a").click()
        # self.assertEqual("Audiee", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td[2]").text)
        # self.assertEqual("Haylette", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td[3]").text)
        # self.assertEqual("402-827-0991", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td[4]").text)
        # self.assertEqual("9028 Burt St", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[3]/table/tbody/tr/td").text)
        # self.assertEqual("German", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[4]/table/tbody/tr/td[5]").text)
        # self.assertEqual("This is a note.", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[5]/table/tbody/tr/td").text)
    
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
