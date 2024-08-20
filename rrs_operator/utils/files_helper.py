import os
from dotenv import load_dotenv
import ipfshttpclient2
import tempfile
import shutil

IPFS_ENDPOINT = os.getenv("IPFS_ENDPOINT")

class FilesHelper:

    @staticmethod
    def create_and_save_file(content: str, path_to_saving_dir: str, file_name: str) -> str:
        """Creates a file with the content and saves to the specific directory and returns file name
        
        :param content: Content to be written to the file
        :param path_to_saving_dir: Path to the directory, where the file will be stored
        :param file_name: Name of the file to create

        :return: Full path to the file
        """

        with open(f"{path_to_saving_dir}/{file_name}", "w") as f:
            f.write(content)
        return f"{path_to_saving_dir}/{file_name}"
    
    @staticmethod
    def create_temp_directory() -> str:
        return tempfile.mkdtemp()
    
    @staticmethod
    def remove_directory(path_to_dir: str) -> None:
        shutil.rmtree(path_to_dir)  
    
    def get_file_from_local_ipfs(self, hash: str) -> str:
        pass

    def _download_file_from_ipfs(self, hash: str) -> str:
        pass

    