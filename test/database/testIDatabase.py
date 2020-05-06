#!/usr/bin/env python3
import unittest
from src.database.iDatabase import iDatabase

class TestIDatabase(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()