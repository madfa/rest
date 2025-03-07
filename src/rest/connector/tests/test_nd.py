#!/bin/env python
""" Unit tests for ND rest.connector """

import os
import unittest
from requests.models import Response
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from pyats.topology import loader

from rest.connector import Rest
HERE = os.path.dirname(__file__)


class test_rest_connector(unittest.TestCase):

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['nd']
        # Always mock logging
        mock_logger = patch(
            "rest.connector.libs.nd.implementation.log"
        )
        self.mock_logger: MagicMock = mock_logger.start()
        self.addCleanup(mock_logger.stop)

    def test_init(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.device, self.device)

        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.execute())
        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.configure())

    def test_connection(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            req().post.return_value = resp
            connection.connect()
            self.assertEqual(connection.connected, True)
            connection.connect()
            self.assertEqual(connection.connected, True)

        # Now disconnect
        with patch('requests.Session') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_connection_wrong_code(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = [404, 404, 404]
            req().post.return_value = resp

            with self.assertRaises(ConnectionError):
                connection.connect(retry_wait=1)

        self.assertEqual(connection.connected, False)

        # Now disconnect
        with patch('requests.Session') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.post(api_url='temp', payload={'payload':'something'})

    def test_post_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            req().post.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.post(api_url='temp', payload={'payload':'something'})
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_connected_wrong_status(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.post(api_url='temp', payload={'payload':'something'})
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            connection.post(api_url='temp', payload={'payload':'something'},
                            expected_status_code=300)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_connected_wrong_status_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.post(api_url='temp', payload={'payload':'something'},
                                expected_status_code=400)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_put_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.put(api_url='temp', payload={'payload':'something'})

    def test_put_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            req().post.return_value = resp
            req().put.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.put(api_url='temp', payload={'payload':'something'})
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_put_connected_wrong_status(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().put.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.put(api_url='temp', payload={'payload':'something'})
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_put_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().put.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            connection.put(api_url='temp', payload={'payload':'something'},
                           expected_status_code=300)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_put_connected_wrong_status_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().put.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.put(api_url='temp', payload={'payload':'something'},
                               expected_status_code=400)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.get(api_url='temp')

    def test_get_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            req().post.return_value = resp
            req().get.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.get(api_url='temp')
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_connected_wrong_status(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.get(api_url='temp')
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            connection.get(api_url='temp', expected_status_code=300)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_connected_wrong_status_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().get.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.get(api_url='temp', expected_status_code=400)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_delete_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.delete(api_url='temp')

    def test_delete_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            req().post.return_value = resp
            req().delete.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.delete(api_url='temp')
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_delete_connected_wrong_status(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:

            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().delete.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.delete(api_url='temp')
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_delete_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().delete.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})
            connection.delete(api_url='temp', expected_status_code=300)
            self.assertEqual(connection.connected, True)
            connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_delete_connected_wrong_status_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.Session') as req:
            resp = Response()
            resp.status_code = 200
            resp2 = Response()
            resp2.status_code = 300
            req().delete.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(RequestException):
                connection.delete(api_url='temp', expected_status_code=400)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)


if __name__ == '__main__':
    unittest.main()