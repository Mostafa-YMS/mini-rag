import os
import re

from fastapi import UploadFile

from .BaseController import BaseController
from .ProjectController import ProjectController


class FileController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile, max_size: int):
        if max_size is not None and file.size > max_size * 1024 * 1024:
            return False

        return True

    def generate_file_path(self, file_name: str, project_id: str):
        unique_name = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_name = self.__get_clean_file_name(file_name=file_name)
        file_path = os.path.join(project_path, f"{unique_name}_{cleaned_name}")

        if os.path.exists(file_path):
            return self.generate_file_name(file_name=file_name, project_id=project_id)

        return file_path, f"{unique_name}_{cleaned_name}"

    def __get_clean_file_name(self, file_name: str):
        cleaned_name = re.sub(r"[^\w.]", "", file_name.strip())
        cleaned_name = cleaned_name.replace(" ", "_")
        return cleaned_name
