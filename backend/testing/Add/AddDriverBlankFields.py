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
        driver.find_element_by_link_text("Add New").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("first_name").click()
        driver.find_element_by_name("first_name").clear()
        driver.find_element_by_name("first_name").send_keys("wiz")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("last_name").click()
        driver.find_element_by_name("last_name").clear()
        driver.find_element_by_name("last_name").send_keys("khalifa")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("formGridPhone").click()
        driver.find_element_by_id("formGridPhone").clear()
        driver.find_element_by_id("formGridPhone").send_keys("402-000-0000")
        driver.find_element_by_id("formGridStatus").click()
        Select(driver.find_element_by_id("formGridStatus")).select_by_visible_text("Volunteer")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("formGridCapacity").click()
        driver.find_element_by_id("formGridCapacity").clear()
        driver.find_element_by_id("formGridCapacity").send_keys("3")
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/form/div[3]/div[4]/label").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div/form/div[4]/div[4]/label").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_link_text("ISC Driver and Recipient Data").click()
        driver.find_element_by_id("search").click()
        driver.find_element_by_id("search").clear()
        driver.find_element_by_id("search").send_keys("wiz")
        # self.assertEqual("wiz", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td").text)
        # self.assertEqual("khalifa", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td[2]").text)
        # self.assertEqual("402-000-0000", driver.find_element_by_xpath("//div[@id='root']/div/div/div/div[2]/table/tbody/tr/td[3]").text)
    
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
