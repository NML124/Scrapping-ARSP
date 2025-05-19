import os
import pickle

class PersistenceManager:
    def __init__(self, progress_file, temp_csv_file):
        self.progress_file = progress_file
        self.temp_csv_file = temp_csv_file

    def load_progress(self):
        progress_file =self.progress_file
        if os.path.exists(progress_file):
            with open(progress_file, 'rb') as f:
                return pickle.load(f)
        return {'links': [], 'data': [], 'scraped_links': []}
    
    def save_progress(self, links, data, scraped_links):
        file_to_save = self.progress_file
        with open(file_to_save, 'wb') as f:
            pickle.dump({'links': links, 'data': data, 'scraped_links': list(scraped_links)}, f)

    def append_to_temp_csv(self, enterprise):
        with open(self.temp_csv_file, 'a', encoding='utf-8') as file:
            file.write("\\".join(enterprise[:9]) + "\n")

    def save_to_csv(self, data, filename):
        with open(filename, 'w', encoding="utf-8") as file:
            for enterprise in data:
                file.write("\\".join(enterprise[:9]) + "\n")
        if os.path.exists(self.temp_csv_file):
            os.remove(self.temp_csv_file)
