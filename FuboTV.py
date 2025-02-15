import os
import re
import pandas as pd

# Define file paths
input_dir = './data'
files = {
    "Essential": os.path.join(input_dir, "FuboEssential84.99.txt"),
    "Pro": os.path.join(input_dir, "FuboPro84.99.txt"),
    "Elite": os.path.join(input_dir, "FuboElite94.99.txt")
}

# Function to extract "img title" fields (channel names) from a file
def extract_channel_titles(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return set(re.findall(r'title="([^"]+)"', content))

# Extract channels from each file
channels_elite = extract_channel_titles(files["Elite"])
channels_essential = extract_channel_titles(files["Essential"])
channels_pro = extract_channel_titles(files["Pro"])

# Create a sorted list of all unique channel names (Elite has the most items)
all_channels = sorted(channels_elite)

# Prepare the final data structure
data = []
for channel in all_channels:
    data.append([channel,
                 "✔" if channel in channels_essential else "",  # Essential column
                 "✔" if channel in channels_pro else "",        # Pro column
                 "✔"])                                           # Elite column (always included)

# Create a DataFrame
df_fubo = pd.DataFrame(data, columns=["Channel Name", "Essential", "Pro", "Elite"])

# Define output path
output_dir = "./output"
output_file = os.path.join(output_dir, "FuboTVChannelList.xls")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Save to Excel with formatting
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    df_fubo.to_excel(writer, sheet_name="FuboTV Packages", index=False)
    worksheet = writer.sheets["FuboTV Packages"]
    
    # Freeze the first row
    worksheet.freeze_panes(1, 0)
    
    # Apply sorting only to "Channel Name"
    worksheet.autofilter(0, 0, len(df_fubo), 0)

print(f"Excel file saved at: {output_file}")
