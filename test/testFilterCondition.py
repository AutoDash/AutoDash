#!/usr/bin/env python3
import unittest
from src.data.MetaDataItem import MetaDataItem
from src.data.FilterCondition import FilterCondition, is_string_token, is_number_token

class TestFilterCondition(unittest.TestCase):

    def test_non_string(self):
        self.assertFalse(is_string_token("=="))
        self.assertFalse(is_string_token(""))
        self.assertFalse(is_string_token("0"))
        self.assertFalse(is_string_token("location"))
        self.assertFalse(is_string_token("{}"))
        self.assertFalse(is_string_token("[]"))

    def test_single_quote_string(self):
        self.assertTrue(is_string_token("''"))
        self.assertTrue(is_string_token("'hello'"))
        self.assertTrue(is_string_token("'h\"ello'"))
        self.assertTrue(is_string_token("'h\\'ello'"))
        self.assertTrue(is_string_token("'h\\ello'"))
        self.assertTrue(is_string_token("'hello\\''"))
        
        self.assertFalse(is_string_token("hello"))
        self.assertFalse(is_string_token("'hello"))
        self.assertFalse(is_string_token("hello'"))
        self.assertFalse(is_string_token("'hell'o"))
        self.assertFalse(is_string_token("'h'ello'"))
        self.assertFalse(is_string_token("'h''ello'"))
        self.assertFalse(is_string_token("'hello\\'"))
        
    def test_double_quote_string(self):
        self.assertTrue(is_string_token('""'))
        self.assertTrue(is_string_token('"hello"'))
        self.assertTrue(is_string_token('"h\'ello"'))
        self.assertTrue(is_string_token('"h\\"ello"'))
        self.assertTrue(is_string_token('"h\\ello"'))
        self.assertTrue(is_string_token('"hello\\""'))
        
        self.assertFalse(is_string_token('hello'))
        self.assertFalse(is_string_token('"hello'))
        self.assertFalse(is_string_token('hello"'))
        self.assertFalse(is_string_token('"hell"o'))
        self.assertFalse(is_string_token('"h"ello"'))
        self.assertFalse(is_string_token('"h""ello"'))
        self.assertFalse(is_string_token('"hello\\"'))

    def test_number(self):
        self.assertTrue(is_number_token("0"))
        self.assertTrue(is_number_token("-1"))
        self.assertTrue(is_number_token("1.2"))
        self.assertTrue(is_number_token("-0.234"))
        
        self.assertFalse(is_number_token("str"))
        self.assertFalse(is_number_token("'0'"))
        self.assertFalse(is_number_token('"0"'))
    
    def check_failed_syntax_validation(self, filter_string):
        try:
            FilterCondition(filter_string)
            self.assertFalse(True)
        except SyntaxError:
            pass
            
    def check_failed_type_validation(self, filter_string):
        try:
            FilterCondition(filter_string)
            self.assertFalse(True)
        except TypeError:
            pass
    
    def test_validation(self):
        FilterCondition("location == 'Canada' and collision_type != 'car'")
        FilterCondition("title < 'a' or url > 'Z' or description == 'hello'")
        FilterCondition("1 >= 0 and (2 <= 0 or 7 != 2)")
        
        self.check_failed_syntax_validation("vacation == 'Canada'")
        self.check_failed_syntax_validation("(location == 'Canada'")
        self.check_failed_syntax_validation("location == 'Canada')")
        self.check_failed_syntax_validation(")location = 'Canada'(")
        self.check_failed_syntax_validation("location = 'Cana'da'")
        
        self.check_failed_syntax_validation("location == 'Cana'da' !=")
        
        self.check_failed_type_validation("location >= 4")
        
        
    def test_filtering(self):
        mdi_list = [
            MetaDataItem(1, "Vid1", "c.com", "youtube", "bike", "blank", "China"),
            MetaDataItem(2, "Vid2", "c.com", "youtube", "car", "blank", "Canada"),
            MetaDataItem(3, "Vid3", "c.com", "youtube", "bike", "blank", "Canada"),
            MetaDataItem(4, "Vid4", "c.com", "youtube", "car", "blank", "China"),
            MetaDataItem(5, "Vid5", "c.com", "youtube", "walking", "blank", "Canada")
        ]
        
        fc1 = FilterCondition("location == 'Canada' and collision_type != 'car'")
        lst1 = fc1.filter(mdi_list)
        self.assertEqual(len(lst1), 2)
        self.assertEqual(lst1[0].id, 3)
        self.assertEqual(lst1[1].id, 5)
        
        fc2 = FilterCondition("title == 'Vid1' or title == 'Vid5'")
        lst2 = fc2.filter(mdi_list)
        self.assertEqual(len(lst2), 2)
        self.assertEqual(lst2[0].id, 1)
        self.assertEqual(lst2[1].id, 5)
        
        

if __name__ == '__main__':
    unittest.main()  