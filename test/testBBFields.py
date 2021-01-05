#!/usr/bin/env python3
import unittest
from src.data.BBFields import BBFields, BBox


class TestBBFields(unittest.TestCase):
    def _sample_bbField(self):
        return BBFields.from_json({
            "objects": [{
                "id": 1,
                "has_collision": True,
                "class": "car",
                "bboxes": [(0, 1, 2, 3, 4), (1, 5, 6, 7, 8)]
            }, {
                "id": 2,
                "has_collision": False,
                "class": "truck",
                "bboxes": [(0, 11, 12, 13, 14), (1, 15, 16, 17, 18)]
            }],
            "collision_locations": [1, 2, 3],
            "resolution": (360, 360)
        })

    def test_from_json(self):
        fields = self._sample_bbField()
        self.assertListEqual(fields.collision_locations, [1, 2, 3])
        self.assertTupleEqual(fields.resolution, (360, 360))
        self.assertEqual(len(fields.objects), 2)

        o1 = fields.objects[1]
        self.assertEqual(o1.id, 1)
        self.assertEqual(o1.has_collision, True)
        self.assertEqual(o1.obj_class, "car")

        self.assertEqual(o1.bboxes[0], BBox(0, 1, 2, 3, 4))
        self.assertEqual(o1.bboxes[1], BBox(1, 5, 6, 7, 8))

        o2 = fields.objects[2]
        self.assertEqual(o2.id, 2)
        self.assertEqual(o2.has_collision, False)
        self.assertEqual(o2.obj_class, "truck")

        self.assertEqual(o2.bboxes[0], BBox(0, 11, 12, 13, 14))
        self.assertEqual(o2.bboxes[1], BBox(1, 15, 16, 17, 18))

    def test_map(self):
        fields = self._sample_bbField()
        fields.map_boxes(lambda box: box.scale(2, 2))
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 2, 4, 6, 8))
        self.assertEqual(fields.get_bbox(1, 1), BBox(1, 10, 12, 14, 16))
        self.assertEqual(fields.get_bbox(2, 0), BBox(0, 22, 24, 26, 28))
        self.assertEqual(fields.get_bbox(2, 1), BBox(1, 30, 32, 34, 36))

    def test_map_remove(self):
        fields = self._sample_bbField()
        fields.map_boxes(lambda box: box if box.frame == 0 else None)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 1, 2, 3, 4))
        self.assertEqual(fields.get_bbox(1, 1), None)
        self.assertEqual(fields.get_bbox(2, 0), BBox(0, 11, 12, 13, 14))
        self.assertEqual(fields.get_bbox(2, 1), None)

    def test_higher_res(self):
        fields = self._sample_bbField()
        fields.set_resolution((720, 720))

        o1 = fields.objects[1]
        self.assertEqual(o1.bboxes[0], BBox(0, 2, 4, 6, 8))
        self.assertEqual(o1.bboxes[1], BBox(1, 10, 12, 14, 16))

    def test_lower_res(self):
        fields = self._sample_bbField()
        fields.set_resolution((180, 180))

        o2 = fields.objects[2]
        self.assertEqual(o2.bboxes[0], BBox(0, 11, 12, 13, 14))
        self.assertEqual(o2.bboxes[1], BBox(1, 15, 16, 17, 18))
        self.assertEqual(fields.get_bbox(2, 0), BBox(0, 5, 6, 6, 7))
        self.assertEqual(fields.get_bbox(2, 1), BBox(1, 7, 8, 8, 9))

    def test_set_bbox(self):
        fields = self._sample_bbField()
        fields.set_bbox(1, 0, 21, 22, 23, 24)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 21, 22, 23, 24))

    def test_set_bbox_lower_res(self):
        fields = self._sample_bbField()
        fields.set_resolution((180, 180))
        fields.set_bbox(1, 0, 21, 22, 23, 24)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 21, 22, 23, 24))

    def test_set_bbox_higher_res(self):
        fields = self._sample_bbField()
        fields.set_resolution((720, 720))
        fields.set_bbox(1, 0, 21, 22, 23, 24)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 21, 22, 23, 24))

    def test_clone(self):
        fields = self._sample_bbField()
        clone = fields.clone()
        clone.objects[1].bboxes[1].x1 = 1
        self.assertEqual(fields.objects[1].bboxes[1].x1, 5)
        self.assertEqual(clone.objects[1].bboxes[1].x1, 1)
        fields.objects[1].bboxes[1].x1 = 2
        self.assertEqual(fields.objects[1].bboxes[1].x1, 2)
        self.assertEqual(clone.objects[1].bboxes[1].x1, 1)
        del fields.objects[2]
        self.assertIsNotNone(clone.objects[2])
        self.assertFalse(2 in fields.objects)

    def test_crop_range(self):
        fields = self._sample_bbField()
        fields.crop_range(0, 1)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 1, 2, 3, 4))
        self.assertEqual(fields.get_bbox(1, 1), None)

    def test_crop_and_clone(self):
        fields = self._sample_bbField()
        fields_2 = fields.clone()
        fields_2.crop_range(0, 1)
        self.assertEqual(fields_2.get_bbox(1, 0), BBox(0, 1, 2, 3, 4))
        self.assertEqual(fields_2.get_bbox(1, 1), None)
        self.assertEqual(fields.get_bbox(1, 0), BBox(0, 1, 2, 3, 4))
        self.assertEqual(fields.get_bbox(1, 1), BBox(1, 5, 6, 7, 8))


if __name__ == '__main__':
    unittest.main()
