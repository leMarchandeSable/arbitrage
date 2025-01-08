import os
import pandas as pd


class DatabaseManager:
    """
    A class to handle all interactions with the CSV database.
    """
    def __init__(self, path: str):
        self.path = path
        self.data = self._load_database()

    def _load_database(self) -> pd:
        # Check if the CSV file exists
        if os.path.exists(self.path):
            return pd.read_csv(self.path)
        return pd.DataFrame()

    def add_instance(self, instance: dict):
        self.data = pd.concat([self.data, pd.DataFrame([instance])], ignore_index=True)

    def save_database(self):
        self.data.drop_duplicates(inplace=True)  # Remove duplicates before saving
        self.data.to_csv(self.path, index=False)

    def get_data(self):
        return self.data

    def show_data(self):
        print(self.data.head)


if __name__ == "__main__":
    a = DatabaseManager("test.csv")
    a.add_instance({'a':2, 'b': "rez"})
    a.save_database()
    a.show_data()

