from discord import User
from pymongo import MongoClient
from pprint import pprint

class Database:
    def __init__(self):
        client = MongoClient(port=27017)
        self._db = client.business
        self._table = None

    def insert(self, data:dict):
        return self._table.insert_one(data)

    def update(self, id, col, value:dict):
        self._table.update_one({'id' : id}, {'$set': {col: value}})

    def insert_to_list(self, id, col, value):
        new_value = self.find({'id':id})[col]
        new_value.append(value)
        self.update(id, col, new_value)
        
    def delete_all(self, col:str, value):
        self._table.delete_many({col: value})

    def delete_one(self, col:str, value):
        self._table.delete_one({col: value})

    def find(self, filter:dict={}):
        return self._table.find_one(filter)

    def get_all_elements(self, col:str=None, values:list=None):
        if col and values:
            return self._table.find({col: {'$all': values}})
        return self._table.find({})

    def get_first(self, n:int):
        return self._table.aggregate([{'$limit':n}])

    def get_last(self, n:int):
        return self._table.find({'$query': {}, '$orderby': {'$natural' : -1}}).limit(n)
 
    def size(self) -> int:
        return self._table.count_documents({})

    def drop_table(self):
        self._table.drop()


class Users(Database):
    def __init__(self):
        super().__init__()
        self._table = self._db.users

class Test(Database):
    def __init__(self):
        super().__init__()
        self._table = self._db.test

def main():
    def print_top(n, db:Database):
        for elem in db.get_first(5):
            pprint(elem)

    db = Users()

    db.insert({'list':[{'a':1}, {'a':2}]})

    inputs = {'1':print_top, '2':db.drop_table}

    running = True
    while running:

        print('''
    _________ Database __________
    ⎜1. Print frist 5 data       ⎜
    ⎜2. Drop data table          ⎜
    ⎜0. Exit                     ⎜
    ￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣
        ''')

        inp = input('Enter number: ')
        print()

        if inp == '1':
            inputs[inp](5, db)
        elif inp == '2':
            inputs[inp]()
        elif inp == '0':
            running = False


    #b.drop_table()
    #p.drop_table()

    # print(b.size())
    # print(p.size())

    # for element in b.get_all_elements():
    #     #b.add_column(element, {'likes': 0})
    #     print(element.get('likes'))
    #     b.add_column(element, {'likes': 1})

    
    # for element in b.get_all_elements():
    #     pprint(element)
    
    # for e in b.get_first(2):
    #     pprint(e)

    # for e in p.get_first(10):
    #         pprint(e)

    # for e in p.get_first(10):
    #     pprint(e)

if __name__ == '__main__':
    main()





# def group(self, by, ):
#     stargroup=self._table.aggregate([
#     { 
#         '$group':
#             { 
#                 '_id': "$rating",
#                 "count" :  
#                     { 
#                         '$sum' : 1 
#                     }
#             }
#     },
#     {
#         "$sort":  
#             { 
#                 "_id" : -1
#             }
#     }
#     ])