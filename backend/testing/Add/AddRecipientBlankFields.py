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
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div/div/div/div[3]/a").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("first_name").click()
        driver.find_element_by_name("first_name").clear()
        driver.find_element_by_name("first_name").send_keys("chris")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("last_name").click()
        driver.find_element_by_name("last_name").clear()
        driver.find_element_by_name("last_name").send_keys("rock")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("formGridPhone").clear()
        driver.find_element_by_id("formGridPhone").send_keys("402-000-0000")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("quantity").clear()
        driver.find_element_by_name("quantity").send_keys("3")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("address").clear()
        driver.find_element_by_id("address").send_keys("1234 Main St")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("city").clear()
        driver.find_element_by_id("city").send_keys("omaha")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("state").click()
        Select(driver.find_element_by_id("state")).select_by_visible_text("NE")
        driver.find_element_by_id("zipcode").click()
        driver.find_element_by_id("zipcode").clear()
        driver.find_element_by_id("zipcode").send_keys("68104")
        driver.find_element_by_xpath("//div[@id='formGridCheckbox']/div").click()
        driver.find_element_by_xpath("//div[@id='formGridCheckbox']/div[2]/label").click()
        driver.find_element_by_xpath("//div[@id='formGridCheckbox']/div[3]/label").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div/div/div/div[2]/div/input").click()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div/div/div/div[2]/div/input").clear()
        driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div/div/div/div[2]/div/input").send_keys("chri")
        # self.assertEqual("chris", driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td").text)
        # self.assertEqual("rock", driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td[2]").text)
        # self.assertEqual("3", driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td[3]").text)
        # self.assertEqual("1234 Main St", driver.find_element_by_xpath("//div[@id='root']/div/div/div[2]/div[2]/table/tbody/tr/td[4]").text)
    
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
