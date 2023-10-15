import os
import csv

# Define the directory where the image and annotation files are located
data_dir = 'MangoDataset/train/new'



# Create a list to store the pairs of image and annotation file paths
file_pairs = []

# # Iterate through the files in the data directory
# for root, _, files in os.walk(data_dir):
#     for file in files:
#         if file.endswith('.jpg'):
#             image_file = os.path.join(root, file)
#             # Check if a corresponding annotation file (e.g., .txt) exists
#             annotation_file = os.path.join(root, file.replace('.jpg', '.txt'))
#             if os.path.exists(annotation_file):
#                 file_pairs.append((image_file, annotation_file))

# # Define the path for the output CSV file
# output_csv_file = 'MangoDataset/train/output.csv'

# # Write the file pairs to a CSV file
# with open(output_csv_file, mode='w', newline='') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     for image_path, annotation_path in file_pairs:
#         csv_writer.writerow([image_path, annotation_path])


folder_path=data_dir = 'MangoDataset/train/labels'
# List all .txt files in the folder
txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]

# Define the path for the output CSV file
output_csv_file = 'MangoDataset/train/train.csv'

# Write the list of .txt files to a CSV file
with open(output_csv_file, mode='w', newline='', encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["File Name"])  # Write a header row if needed
    for txt_file in txt_files:
        csv_writer.writerow([txt_file])