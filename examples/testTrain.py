"""An example of splitting exported images into training and test folders"""
from ..woodwork import utils
import pprint
pp = pprint.PrettyPrinter(indent=4)
pprint = pp.pprint

drive = utils.Drive()

folders = drive.list_folders()

pprint(folders)

# files = drive.get_all_files("HansenSamples")

# print(f"Found {len(files)} files")

drive.create_test_and_train("HansenSamples", test_ratio=0.2)