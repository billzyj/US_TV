import os
import re
import pandas as pd

# Define input folder and output file
input_folder = "./data"
output_folder = "./output"
output_file = os.path.join(output_folder, "FuboTVChannelList.xls")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Function to extract "img title" fields from a file
def extract_channel_titles(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return re.findall(r'title="([^"]+)"', content)

# List of input files (modify as needed)
input_files = [
    "FuboEssential84.99.txt",
    "FuboPro84.99.txt",
    "FuboElite94.99.txt"
]

# Create a Pandas Excel writer
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    for file_name in input_files:
        file_path = os.path.join(input_folder, file_name)
        if os.path.exists(file_path):
            channels = extract_channel_titles(file_path)
            df = pd.DataFrame(channels, columns=["Channel Name"])
            sheet_name = os.path.splitext(file_name)[0]  # Sheet name from file name
            df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Excel file saved: {output_file}")
