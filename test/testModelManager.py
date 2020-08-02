#!/usr/bin/env python3
import unittest
from src.service import ModelManager
import tensorflow as tf

class TestModelManager(unittest.TestCase):

    def save_a_model_and_get_it(self):
        # Simple XOR keras
        model = tf.keras.Sequential()
        model.add(tf.keras.Dense(2))
        model.train(
            [[0, 1], [1, 0], [1, 1], [0, 0]],
            [1, 1, 0, 0])
        ModelManager.save_model("XORtest", model)
        self.assertEqual(ModelManager.get_model("XORtest"), model)

if __name__ == '__main__':
    unittest.main()
