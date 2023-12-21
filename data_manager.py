import pandas as pd


class DataManager():

    def __init__(self, db_filename):

        self.database = pd.read_excel(db_filename)