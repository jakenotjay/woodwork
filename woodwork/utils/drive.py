from typing import List, Dict, Any, Optional, Union
from ..auth.drive import authenticate_drive
from random import random

class Drive:
    """Drive API methods"""
    service = None

    def __init__(self, service: Optional[Any] = None):
        """Initializes the Drive class.
        
        Args:
            service (optional): The authenticated service object.
        
        Returns:
            None
        """
        if service == None:
            service = authenticate_drive()

        self.service = service

    def list_folders(self, folder_name: str = None, parent_folder: str = None) -> List[Dict[str, Any]]:
        """Lists all folders in the user's Google Drive.

        Args:
            folder_name (optional): The name of the folder to list.
            parent_folder (optional): The name of the parent folder to list folders from.
        
        Returns:
            A list of dictionaries containing folder information.
        """
        query = "mimeType='application/vnd.google-apps.folder'"

        # filter for specific folder name
        if folder_name != None:
            query += f" and name='{folder_name}'"

        # filter for folders within a parent folder
        if parent_folder != None:
            folder_id = self.get_folder_id(parent_folder)
            if folder_id == None:
                return []

            query += f" and '{folder_id}' in parents"

        results = self.service.files().list(
            q=query,
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])

        return items

    def get_folder_id(self, folder_name: str) -> Union[str, None]:
        """Gets the ID of a folder in the user's Google Drive.
        
        Args:
            folder_name: The name of the folder to get the ID from.
        
        Returns:
            The ID of the folder or None if the folder doesn't exist
        """
        folders = self.list_folders(folder_name=folder_name)

        for folder in folders:
            if folder['name'] == folder_name:
                return folder['id']

        return None

    def list_files(self, folder_name: Optional[str] = None, nextPageToken: Optional[str] = None, pageSize: int = 100) -> List[Dict[str, Any]]:
        """Returns the first 10 files in a folder.
        
        Args:
            folder_name (optional): The name of the folder to list files from.
            nextPageToken (optional): The token to get the next page of files.
        
        Returns:
            A list of dictionaries containing file information.
        """
        query = None
        if folder_name != None:
            folder_id = self.get_folder_id(folder_name)
            if folder_id == None:
                return []

            query = f"mimeType!='application/vnd.google-apps.folder' and '{folder_id}' in parents"

        results = None

        if nextPageToken == None:
            results = self.service.files().list(
                q=query,
                pageSize=pageSize,
                fields="nextPageToken, incompleteSearch, files(id, name, parents)"
            ).execute()
        else:
            results = self.service.files().list(
                q=query,
                pageSize=pageSize,
                pageToken=nextPageToken,
                fields="nextPageToken, incompleteSearch, files(id, name, parents)"
            ).execute()

        return {
            'files': results.get('files', []),
            'incompleteSearch': results.get('incompleteSearch', False),
            'nextPageToken': results.get('nextPageToken', None)
        }

    def get_all_files(self, folder_name: str) -> List[Dict[str, Any]]:
        """Gets all files in a folder.
        
        Args:
            folder_name: The name of the folder to get files from.
        
        Returns:
            A list of dictionaries containing file information.
        """
        folder_id = self.get_folder_id(folder_name)
        if folder_id == None:
            return []

        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=100,
            fields="nextPageToken, files(id, name), incompleteSearch"
        ).execute()

        incompleteSearch = results.get('incompleteSearch', False)
        pageToken = results.get('nextPageToken', None)
        files = results.get('files', [])

        while incompleteSearch == True or pageToken != None:
            print("Getting more files...")
            print(f"Current files length is {len(files)}")
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=1000,
                pageToken=pageToken,
                fields="nextPageToken, files(id, name), incompleteSearch"
            ).execute()

            incompleteSearch = results.get('incompleteSearch', False)
            pageToken = results.get('nextPageToken', None)
            files += results.get('files', [])

        return files

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Creates a folder in the user's Google Drive.
        
        Args:
            folder_name: The name of the folder to create.
            parent_folder_id (optional): The ID of the parent folder to create the folder in.
        
        Returns:
            The ID of the created folder.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id != None:
            file_metadata['parents'] = [parent_folder_id]

        file = self.service.files().create(body=file_metadata, fields='id').execute()

        return file.get('id')

    def move_file(self, file_id: str, folder_id: str, previous_parent_ids: List[str] = None) -> None:
        """Moves a file to a folder.
        
        Args:
            file_id: The ID of the file to move.
            folder_id: The ID of the folder to move the file to.
        
        Returns:
            None
        """
        if previous_parent_ids is None or len(previous_parent_ids) == 0:
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parent_ids = file.get('parents', [])
            
        # removeParents takes a comma-separated list of parent IDs
        previous_parent_ids = ",".join(previous_parent_ids)

        file = self.service.files().update(fileId=file_id, addParents=folder_id, removeParents=previous_parent_ids, fields='id, parents').execute()

    def create_test_and_train(self, parent_folder: str, test_folder: str = "test", train_folder: str = "train", test_ratio: float = 0.2) -> None:
        """Creates a test and train folder in a parent folder, moving all files in parent folder based on the test_ratio.
        
        Args:
            parent_folder: The name of the parent folder to create the test and train folders in.
            test_folder (optional): The name of the test folder.
            train_folder (optional): The name of the train folder.
            test_ratio (optional): The ratio of the test folder to the train folder.
        
        Returns:
            None
        """
        parent_folder_id = self.get_folder_id(parent_folder)
        if parent_folder_id == None:
            return

        test_folder_id = self.get_folder_id(test_folder)
        if test_folder_id == None:
            test_folder_id = self.create_folder(test_folder, parent_folder_id)

        train_folder_id = self.get_folder_id(train_folder)
        if train_folder_id == None:
            train_folder_id = self.create_folder(train_folder, parent_folder_id)

        print("Getting files...")
        list_response = self.list_files(folder_name=parent_folder)
        files = list_response['files']
        incompleteSearch = list_response['incompleteSearch']
        nextPageToken = list_response['nextPageToken']

        # TODO: Multi-thread this
        def move_files(files: List[Dict[str, Any]]) -> None:
            print(f"Moving {len(files)} files...")
            i = 0
            for file in files:
                i += 1
                random_number = random()
                if random_number < test_ratio:
                    print(f"Moving file {i} to test folder...")
                    self.move_file(file['id'], test_folder_id, file['parents'])
                else:
                    print(f"Moving file {i} to train folder...")
                    self.move_file(file['id'], train_folder_id, file['parents'])

        move_files(files)

        while incompleteSearch == True or nextPageToken != None:
            print("Getting more files...")
            list_response = self.list_files(folder_name=parent_folder, nextPageToken=nextPageToken)
            files = list_response['files']
            incompleteSearch = list_response['incompleteSearch']
            nextPageToken = list_response['nextPageToken']

            move_files(files)