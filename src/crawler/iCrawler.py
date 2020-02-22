from abc import ABC, abstractmethod
import MetaDataItem

class iCrawler(ABC):
    def __init__(self):
        super().__init__

    @abstractmethod
    async def next_downloadable(self) -> MetaDataItem:
        pass

    #helper method to publish item to firebase
    def publish_firebase(self, item:MetaDataItem):
        pass
