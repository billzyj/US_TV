import os
import re
import pandas as pd

# Define input and output directories
input_dir = "./data"  # Directory containing input file
output_dir = "./output"  # Directory for output file
input_file = os.path.join(input_dir, "HuluTV.txt")  # Full path for input file
output_file = os.path.join(output_dir, "HuluTVChannelList.xls")  # Output file path

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to extract Hulu channel names from "aria-label" attributes
def extract_hulu_channels(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return list(re.findall(r'aria-label="([^"]+)"', content))  # Keep original order

# Extract channel names
channel_names = extract_hulu_channels(input_file)

# Create a DataFrame to store channel names and category indicators
df_hulu = pd.DataFrame({"Channel Name": channel_names})

# Save to Excel with formatting
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    df_hulu.to_excel(writer, sheet_name="HuluTV Channels", index=False)
    worksheet = writer.sheets["HuluTV Channels"]

    # Apply formatting
    bold_format = writer.book.add_format({"bold": True})  # Define bold format

    # Freeze the first row
    worksheet.freeze_panes(1, 0)

    # Loop through rows to detect categories and apply bold formatting
    for row_num, channel in enumerate(df_hulu["Channel Name"], start=1):
        if channel.startswith("List "):  # If the channel name starts with "List ..."
            worksheet.write(row_num, 0, channel, bold_format)  # Apply bold formatting

print(f"Excel file saved at: {output_file}")
