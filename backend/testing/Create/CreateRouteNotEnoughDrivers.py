# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class CreateRouteNotEnoughDrivers(unittest.TestCase):
    def setUp(self):
        s = Service('../chromedriver.exe')
        self.driver = webdriver.Chrome(service=s)
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_create_route_not_enough_drivers(self):
        driver = self.driver
        driver.get("http://localhost:3000/routing")
        driver.find_element_by_id("search_input").click()
        driver.find_element_by_xpath("//div[@id='multiselectContainerReact']/div[2]/ul/li").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Recipients'])[1]/following::div[3]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Recipients'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Recipients'])[1]/following::div[3]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Glen Plane (Quantity: 3)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("//div[2]/form/div/div/input").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Audiee Haylette (Quantity: 2)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("//div[2]/form/div/div/input").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Vonny Luce (Quantity: 10)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Recipients'])[1]/following::div[3]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Tallie Blumson (Quantity: 8)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("//div[2]/form/div/div/input").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Tallie Blumson (Quantity: 8)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("//div[2]/form/div/div/input").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Geraldine Clitheroe (Quantity: 2)'])[1]/following::li[1]").click()
        driver.find_element_by_xpath("//html").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        #ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
    
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
