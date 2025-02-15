import os
import re
import pandas as pd

# Define input and output directories
input_dir = "./data"  # Directory containing input file
output_dir = "./output"  # Directory for output file
input_file = os.path.join(input_dir, "Youtubetv82.99.txt")  # Full path for input file
output_file = os.path.join(output_dir, "YoutubeTVChannelList.xls")  # Output file path

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to extract YouTube TV channel names from text
def extract_youtube_tv_channels(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return list(re.findall(r'Button - (.*?) \(all-channels\)', content))  # Extract text between "Button -" and "(all-channels)"

# Extract channel names
channel_names = extract_youtube_tv_channels(input_file)

# Convert to DataFrame
df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

# Save to Excel with formatting
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    df_youtube_tv.to_excel(writer, sheet_name="YouTube TV Channels", index=False)
    worksheet = writer.sheets["YouTube TV Channels"]

    # Freeze the first row
    worksheet.freeze_panes(1, 0)

print(f"Excel file saved at: {output_file}")
