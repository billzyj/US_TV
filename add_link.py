import pandas as pd
import urllib.parse

# Load the Excel file
file_path = "Sorted_DIRECTV_Channel_Lineup.xlsx"  # Update with your file path
xls = pd.ExcelFile(file_path)

# Read the sheets into DataFrames
df_sheet1 = pd.read_excel(xls, sheet_name="Channel Lineup")
df_sheet2 = pd.read_excel(xls, sheet_name="Basic Channel List")

# Function to generate Wikipedia hyperlinks
def generate_wikipedia_link(channel_name):
    base_url = "https://en.wikipedia.org/wiki/"
    encoded_name = urllib.parse.quote(str(channel_name).replace(" ", "_"))
    return f'=HYPERLINK("{base_url}{encoded_name}", "{channel_name}")'

# Apply the hyperlink function to the "Channel Name" column in both sheets
df_sheet1["Channel_Name"] = df_sheet1["Channel_Name"].apply(generate_wikipedia_link)
df_sheet2["Channel_Name"] = df_sheet2["Channel_Name"].apply(generate_wikipedia_link)

# Save the updated DataFrames with hyperlinks
output_path = "Hyperlinked_DIRECTV_Channel_Lineup.xlsx"

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    # Write first sheet with hyperlinks
    df_sheet1.to_excel(writer, sheet_name="Channel Lineup", index=False)
    worksheet1 = writer.sheets["Channel Lineup"]
    worksheet1.freeze_panes(1, 0)  # Freeze the first row
    worksheet1.autofilter(0, 0, len(df_sheet1), len(df_sheet1.columns) - 1)  # Add sorting

    # Write second sheet with hyperlinks
    df_sheet2.to_excel(writer, sheet_name="Basic Channel List", index=False)
    worksheet2 = writer.sheets["Basic Channel List"]
    worksheet2.freeze_panes(1, 0)  # Freeze the first row
    worksheet2.autofilter(0, 0, len(df_sheet2), len(df_sheet2.columns) - 1)  # Add sorting

print(f"Hyperlinked Excel file saved as {output_path}")
