import os
import pandas as pd
from src.DirecTV import scrape_directv
from src.DirecTV_Stream import scrape_directv_stream
from src.FuboTV import scrape_fubo_tv
from src.HuluTV import scrape_hulu_tv
from src.SlingTV import scrape_sling_tv
from src.YoutubeTV import scrape_youtube_tv
from src.DishTV import scrape_dishtv
from src.WebDriverUtils import OUTPUT_DIR, LOGGER, write_to_excel

DATA_FILE = "./data/channels.csv"

def get_channel_alias(input_file):
    """Load alias mapping from CSV, ensuring that the first column is the canonical name."""
    alias_df = pd.read_csv(input_file)
    channel_aliases = {}

    for _, row in alias_df.iterrows():
        canonical_name = row.iloc[0].strip().lower()  # Use first column as canonical name
        aliases = [alias.strip().lower() for alias in row.dropna() if alias.strip()]  # Remove empty strings
        for alias in aliases:
            channel_aliases[alias] = canonical_name  # Map alias to canonical name

    LOGGER.info("Loaded channel aliases")
    return channel_aliases

def normalize_channel_name(channel_name, channel_aliases):
    """Normalize and map channel names using alias mapping."""
    channel_name = channel_name.strip().lower()
    return channel_aliases.get(channel_name, channel_name)  # Return canonical name if alias exists

def generate_summary_excel(directv_channels, directvstream_channels, dish_channels, fubo_channels,
                           hulu_channels, sling_channels, youtube_channels, 
                           directv_plans, directvstream_plans, dish_plans, fubo_plans, sling_plans):
    """
    Generates an Excel file consolidating TV channels across different providers.

    :param directv_channels: List from scrape_directv() -> [["Channel Name", "Channel Number"] + plans]
    :param directvstream_channels: List from scrape_directv_stream() -> [["Channel Name", "Channel Number"] + plans]
    :param dish_channels: Dict from scrape_dishtv() -> {channel_name: {plan_name: "✔"}}
    :param fubo_channels: Dict from scrape_fubo_tv() -> {channel_name: {plan_name: "✔"}}
    :param hulu_channels: List from scrape_hulu_tv() -> [channel_name1, channel_name2, ...]
    :param sling_channels: Dict from scrape_sling_tv() -> {channel_name: {plan_name: "✔"}}
    :param youtube_channels: List from scrape_youtube_tv() -> [channel_name1, channel_name2, ...]

    :param directv_plans: List of DirecTV plan names
    :param directvstream_plans: List of DirecTV Stream plan names
    :param dish_plans: List of DishTV plan names
    :param fubo_plans: List of FuboTV plan names
    :param sling_plans: List of SlingTV plan names
    """

    LOGGER.info("Generating consolidated channel list...")
    channel_aliases = get_channel_alias(DATA_FILE)

     # Collect all unique channel names
    all_channels = set()

    for ch in directv_channels + directvstream_channels:
        all_channels.add(normalize_channel_name(ch[0], channel_aliases))

    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in dish_channels.keys()})
    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in fubo_channels.keys()})
    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in sling_channels.keys()})
    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in hulu_channels})
    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in youtube_channels})


    # Initialize DataFrame with channels as rows
    summary_df = pd.DataFrame({"Channel": sorted(all_channels)})

    # Add DirecTV Channel Numbers
    directv_number_map = {normalize_channel_name(ch[0], channel_aliases): ch[1] for ch in directv_channels}
    summary_df["DirecTV Channel Number"] = summary_df["Channel"].map(directv_number_map)

    # Add DirecTV plan availability immediately after channel number
    for i, plan in enumerate(directv_plans):
        directv_plan_map = {normalize_channel_name(ch[0], channel_aliases): ch[i+2] for ch in directv_channels}  # +2 because 0=Name, 1=Number
        summary_df[f"DirecTV - {plan}"] = summary_df["Channel"].map(directv_plan_map)

    # Add DirecTV Stream Channel Numbers
    directvstream_number_map = {normalize_channel_name(ch[0], channel_aliases): ch[1] for ch in directvstream_channels}
    summary_df["DirecTV Stream Channel Number"] = summary_df["Channel"].map(directvstream_number_map)

    # Add DirecTV Stream plan availability immediately after channel number
    for i, plan in enumerate(directvstream_plans):
        directvstream_plan_map = {normalize_channel_name(ch[0], channel_aliases): ch[i+2] for ch in directvstream_channels}  # +2 because 0=Name, 1=Number
        summary_df[f"DirecTV Stream - {plan}"] = summary_df["Channel"].map(directvstream_plan_map)

    # Function to merge provider-specific data
    def merge_provider_data(provider_channels, provider_name, plan_list):
        """Merge provider-specific channel data into the summary."""
        provider_channels = {normalize_channel_name(k, channel_aliases): v for k, v in provider_channels.items()}  # Normalize keys

        for plan in plan_list:
            summary_df[f"{provider_name} - {plan}"] = summary_df["Channel"].map(
                lambda x: "✔️" if any(
                    provider_channels.get(normalize_channel_name(alias, channel_aliases), {}).get(plan, "") in ["✔️", "✔"]
                    for alias in channel_aliases.get(x, [x] if isinstance(channel_aliases.get(x, [x]), list) else [channel_aliases.get(x, [x])])
                ) else ""
            )

    # Merge multi-plan providers
    merge_provider_data(dish_channels, "DishTV", dish_plans)
    merge_provider_data(fubo_channels, "FuboTV", fubo_plans)
    merge_provider_data(sling_channels, "SlingTV", sling_plans)

    # Mark Hulu and YouTube TV as single-plan providers
    summary_df["HuluTV"] = summary_df["Channel"].apply(lambda x: "✔️" if normalize_channel_name(x, channel_aliases) in {normalize_channel_name(ch, channel_aliases) for ch in hulu_channels} else "")
    summary_df["YouTubeTV"] = summary_df["Channel"].apply(lambda x: "✔️" if normalize_channel_name(x, channel_aliases) in {normalize_channel_name(ch, channel_aliases) for ch in youtube_channels} else "")

    # Fill missing values with empty strings
    summary_df.fillna("", inplace=True)

    # Save to Excel
    output_path = os.path.join(OUTPUT_DIR, "Summary_TV_Channels.xlsx")
    write_to_excel(summary_df, output_path, sheet_name="TV Channels Summary", index=False)


if __name__ == "__main__":
     # Run scrapers and collect data
    directv_channels, directv_plans = scrape_directv("")
    directvstream_channels, directvstream_plans = scrape_directv_stream("")
    dish_channels, dish_plans = scrape_dishtv()
    fubo_channels, fubo_plans = scrape_fubo_tv("")
    sling_channels, sling_plans = scrape_sling_tv()
    hulu_channels = scrape_hulu_tv()
    youtube_channels = scrape_youtube_tv()

    # Generate the summary Excel
    generate_summary_excel(directv_channels, directvstream_channels, dish_channels, fubo_channels,
                            hulu_channels, sling_channels, youtube_channels,
                            directv_plans, directvstream_plans, dish_plans, fubo_plans, sling_plans)
