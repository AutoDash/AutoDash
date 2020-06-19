#!/usr/bin/env python3
import unittest
from src.service.ModelManager import ModelManager
import tensorflow as tf

class TestModelManager(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.manager = ModelManager()

    def can_print(self):
        with self.assertLogs():
            print(self.manager)

    def save_a_model_and_get_it(self):
        # Simple XOR keras
        model = tf.keras.Sequential()
        model.add(tf.keras.Dense(2))
        model.train(
            [[0, 1], [1, 0], [1, 1], [0, 0]],
            [1, 1, 0, 0])
        self.manager.save_model("XORtest", model)
        self.assertEqual(self.manager.get_model("XORtest"), model)

if __name__ == '__main__':
    unittest.main()
