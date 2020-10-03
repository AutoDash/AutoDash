import json
import os.path as path

class ListCasheManager(object):
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.data = []
        self.retrieve()

    def __get_file_name(self):
        return path.join(path.dirname(path.abspath(__file__)), "store_" + self.name + ".cache")

    def retrieve(self):
        file_name = self.__get_file_name()
        if not path.isfile(file_name):
            with open(file_name, "w") as file:
                json.dump(self.data, file)

        with open(self.__get_file_name(), "r") as file:
            data = json.load(file)

        self.data = data
        return data

    def __store(self):
        file_name = self.__get_file_name()
        with open(file_name, "w") as file:
            json.dump(self.data, file)

    def insert(self, value):
        if value in self.data:
            self.__remove_element(value)
        self.data.append(value)
        if len(self.data) > self.capacity:
            self.data = self.data[-self.capacity:]
        self.__store()

    def __remove_element(self, value):
        for i, v in enumerate(self.data):
            if v == value:
                del self.data[i]
                return

if __name__ == "__main__":
    m = ListCasheManager("test", capacity=3)
    for i in [1,2,3,2,3,4,3,4,5]:
        m.insert(i)
        print(m.retrieve())

















