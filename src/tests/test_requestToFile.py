#!/usr/bin/env python

import unittest
import os
from src.requestToFile import RequestToFile


class RequestToFileTests(unittest.TestCase):

    def setUp(self):
        self.emptyInitialization = RequestToFile()
        self.objectInitialization = RequestToFile(
            {
                'url': 'url',
                'username': 'username',
                'password': 'password'
            })
        self.configFileInitialization = RequestToFile().initFromConfigFile(
            os.path.join(os.path.dirname(__file__), 'sample.ini'))

    def test_emptyInitIsCorrect(self):
        self.assertEqual(self.emptyInitialization.url, None)
        self.assertEqual(self.emptyInitialization.username, None)
        self.assertEqual(self.emptyInitialization.password,  None)

    def test_objectInitializationIsCorrect(self):
        self.assertEqual(self.objectInitialization.url, 'url')
        self.assertEqual(self.objectInitialization.username, 'username')
        self.assertEqual(self.objectInitialization.password,  'password')

    def test_configFileInitializationIsCorrect(self):
        self.assertEqual(self.configFileInitialization.url,
                         'http://127.0.0.1:9999/main')
        self.assertEqual(self.configFileInitialization.username, 'user')
        self.assertEqual(
            self.configFileInitialization.password,  'secretpassword')

    def test_isJSON_true(self):
        json_data = """{ "employees" : [
            { "firstName":"John" , "lastName":"Doe" },
            { "firstName":"Anna" , "lastName":"Smith" },
            { "firstName":"Peter" , "lastName":"Jones" }]}"""
        self.assertTrue(RequestToFile().isJSON(json_data), "Is not valid JSON")

    def test_isJSON_false(self):
        json_data = """{ "employees" : [
            { "firstName":"John" , "lastName":"Doe" },
            { "firstName":"Anna" , "lastName":"Smith" },
            """
        self.assertFalse(RequestToFile().isJSON(json_data), "Is valid JSON")

    def test_isXML_true(self):
        xml_data = """
             <record>
             <player_birthday>1979-09-23</player_birthday>
             <player_name>Orene Aii</player_name>
             <player_team>Blues</player_team>
             <player_id>453</player_id>
             <player_height>170</player_height>
             <player_position>FW</player_position>
             <player_weight>75</player_weight>
             </record>"""
        self.assertTrue(RequestToFile().isXML(xml_data))

    def test_isXML_false(self):
        xml_data = """
         <record>
         <player_birthday>1979-09-23</player_birthday>
         <player_name>Orene Aii</player_name>
         <player_team>Blues</player_team>
         <player_id>453</player_id>
         <player_height>170</player_height>
         <player_position>F&W</player_position>
         <player_weight>75</player_weight>
         </record>"""
        self.assertFalse(RequestToFile().isXML(xml_data))

    def test_areBothListsPopulated_true(self):
        list1 = [1, 2]
        list2 = [1, 2]
        self.assertTrue(RequestToFile().areBothListsPopulated(list1, list2))

    def test_areBothListsPopulated_false(self):
        list1 = [1, 2]
        list2 = []
        self.assertFalse(RequestToFile().areBothListsPopulated(list1, list2))


if __name__ == '__main__':
    unittest.main()
