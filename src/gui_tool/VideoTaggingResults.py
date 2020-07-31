class VideoTaggingResults(object):
    def __init__(self):
        self.is_dashcam = None
        self.accident_frame_numbers = None
        self.marked = None
        self.unmark()
        self.additional_tags = {}

    def __str__(self):
        res = "[Marked: {0}][Dashcam: {1}] Accident on frames {2}".format(
            self.marked,
            self.is_dashcam,
            self.accident_frame_numbers)
        return res

    def mark_accident(self, frame_number: int):
        self.marked = True
        self.accident_frame_numbers.append(frame_number)

    def unmark_last(self):
        self.accident_frame_numbers = self.accident_frame_numbers[:-1]

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam

    def unmark(self):
        self.is_dashcam = True
        self.accident_frame_numbers = []
        self.marked = False

    def set_additional_tags(self, tags):
        self.additional_tags = tags