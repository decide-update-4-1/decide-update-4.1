import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


from .models import Census
from base import mods
from base.tests import BaseTestCase
from datetime import datetime


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())


class TestCensusTest():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()

    def test_create_census_success(self):
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.driver.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.driver.find_element(By.ID, "id_voting_id").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(now.strftime("%m%d%M%S"))
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys(now.strftime("%m%d%M%S"))
        self.driver.find_element(By.NAME, "_save").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/census/census")

    def test_create_census_empty_error(self):
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.driver.get(self.live_server_url+"/admin/census/census/add")

        self.driver.find_element(By.NAME, "_save").click()

        self.assertTrue(self.driver.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/census/census/add")

    def test_create_census_value_error(self):
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.driver.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.driver.find_element(By.ID, "id_voting_id").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys('64654654654654')
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys('64654654654654')
        self.driver.find_element(By.NAME, "_save").click()

        self.assertTrue(self.driver.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/census/census/add")