class CloudSheetsBase:
    def find(self, filter):
        raise NotImplementedError

    def find_one(self, filter):
        raise NotImplementedError

    def insert_one(self, record):
        raise NotImplementedError

    def insert_many(self, records):
        raise NotImplementedError

    def replace_one(self, filter, replacement):
        raise NotImplementedError

    def update_one(self, filter, update):
        raise NotImplementedError

    def update_many(self, filter, update):
        raise NotImplementedError

    def delete_one(self, filter):
        raise NotImplementedError

    def delete_many(self, filter):
        raise NotImplementedError

    def count_records(self, filter):
        raise NotImplementedError
