import argparse
import json
import os
import pandas as pd
from src.DirecTV import scrape_directv
from src.DirecTV_Stream import scrape_directv_stream
from src.FuboTV import scrape_fubo_tv
from src.HuluTV import scrape_hulu_tv
from src.SlingTV import scrape_sling_tv
from src.YoutubeTV import scrape_youtube_tv
from src.DishTV import scrape_dishtv
from src.WebDriverUtils import OUTPUT_DIR, LOGGER, parallel_scrape, write_to_excel, write_to_csv

DATA_FILE = "./data/channels.csv"

# Map of scraper names to their functions
SCRAPERS = {
    'directv': scrape_directv,
    'directvstream': scrape_directv_stream,
    'dish': scrape_dishtv,
    'fubo': scrape_fubo_tv,
    'sling': scrape_sling_tv,
    'hulu': scrape_hulu_tv,
    'youtube': scrape_youtube_tv
}

def get_channel_alias(input_file):
    """Load alias mapping from CSV, ensuring that the first column is the canonical name."""
    alias_df = pd.read_csv(input_file)
    channel_aliases = {}

    for _, row in alias_df.iterrows():
        canonical_name = row.iloc[0].strip().lower()  # Use first column as canonical name
        aliases = [alias.strip().lower() for alias in row.dropna() if alias.strip()]  # Remove empty strings
        for alias in aliases:
            channel_aliases[alias] = canonical_name  # Map alias to canonical name

    LOGGER.info(f"Loaded {len(channel_aliases)} channel aliases")
    return channel_aliases

def normalize_channel_name(channel_name, channel_aliases):
    """Normalize and map channel names using alias mapping."""
    if isinstance(channel_name, dict):
        channel_name = list(channel_name.keys())[0]  # Get the first key if it's a dict
    channel_name = str(channel_name).strip().lower()
    normalized = channel_aliases.get(channel_name, channel_name)
    return normalized

def generate_summary_excel(results, output_format="excel"):
    """
    Generates a summary file consolidating TV channels across different providers.

    Parameters:
        results: Dictionary containing results from each scraper
        output_format: Output format, either 'excel' or 'csv'
    """
    LOGGER.info("Generating consolidated channel list...")
    channel_aliases = get_channel_alias(DATA_FILE)
    
    # Collect all unique channel names
    all_channels = set()
    
    # Process each provider's results
    for provider, result in results.items():
        if not result:
            continue
            
        try:
            if provider in ['directv', 'directvstream']:
                if isinstance(result, tuple) and len(result) == 2:
                    channels, _ = result
                    for ch in channels:
                        if isinstance(ch, (list, tuple)) and len(ch) > 0:
                            all_channels.add(normalize_channel_name(ch[0], channel_aliases))
                        else:
                            LOGGER.warning(f"Invalid channel format for {provider}: {ch}")
                else:
                    LOGGER.warning(f"Invalid result format for {provider}: {result}")
                    
            elif provider in ['dish', 'fubo', 'sling']:
                if isinstance(result, tuple) and len(result) == 2:
                    channels, _ = result
                    if isinstance(channels, dict):
                        all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in channels.keys()})
                    else:
                        LOGGER.warning(f"Invalid channels format for {provider}: {channels}")
                else:
                    LOGGER.warning(f"Invalid result format for {provider}: {result}")
                    
            else:  # hulu, youtube
                if isinstance(result, (list, set)):
                    all_channels.update({normalize_channel_name(ch, channel_aliases) for ch in result})
                else:
                    LOGGER.warning(f"Invalid channels format for {provider}: {result}")
                    
        except Exception as e:
            LOGGER.error(f"Error processing {provider} results: {str(e)}")
            continue

    LOGGER.info(f"Found {len(all_channels)} unique channels")
    
    # Initialize DataFrame with channels as rows
    summary_df = pd.DataFrame({"Channel": sorted(all_channels)})
    
    # Process each provider's data
    for provider, result in results.items():
        if not result:
            continue
            
        if provider == 'directv':
            channels, plans = result
            # Add channel numbers
            number_map = {normalize_channel_name(ch[0], channel_aliases): ch[1] for ch in channels}
            summary_df["DirecTV Channel Number"] = summary_df["Channel"].map(number_map)
            # Add plan availability
            for i, plan in enumerate(plans):
                plan_map = {normalize_channel_name(ch[0], channel_aliases): ch[i+2] for ch in channels}
                summary_df[f"DirecTV - {plan}"] = summary_df["Channel"].map(plan_map)
                
        elif provider == 'directvstream':
            channels, plans = result
            # Add channel numbers
            number_map = {normalize_channel_name(ch[0], channel_aliases): ch[1] for ch in channels}
            summary_df["DirecTV Stream Channel Number"] = summary_df["Channel"].map(number_map)
            # Add plan availability
            for i, plan in enumerate(plans):
                plan_map = {normalize_channel_name(ch[0], channel_aliases): ch[i+2] for ch in channels}
                summary_df[f"DirecTV Stream - {plan}"] = summary_df["Channel"].map(plan_map)
                
        elif provider in ['dish', 'fubo', 'sling']:
            channels, plans = result
            for plan in plans:
                summary_df[f"{provider.title()} - {plan}"] = summary_df["Channel"].map(
                    lambda x: "✔️" if any(
                        normalize_channel_name(alias, channel_aliases) in channels and 
                        channels[normalize_channel_name(alias, channel_aliases)].get(plan) == "✔️"
                        for alias in [x] + [k for k, v in channel_aliases.items() if v == x]
                    ) else ""
                )
                
        else:  # hulu, youtube
            channels = result
            summary_df[provider.title()] = summary_df["Channel"].map(
                lambda x: "✔️" if any(
                    normalize_channel_name(alias, channel_aliases) in channels
                    for alias in [x] + [k for k, v in channel_aliases.items() if v == x]
                ) else ""
            )

    # Fill missing values with empty strings
    summary_df.fillna("", inplace=True)

    # Save to Excel or CSV
    output_path = os.path.join(OUTPUT_DIR, "Summary_TV_Channels")
    if output_format == "excel":
        if write_to_excel(summary_df, output_path, sheet_name="TV Channels Summary", index=False):
            LOGGER.info(f"Summary Excel file generated: {output_path}.xlsx")
        else:
            LOGGER.error("Failed to generate Excel summary file")
    else:
        write_to_csv(summary_df, output_path + ".csv", index=False)
        LOGGER.info(f"Summary CSV file generated: {output_path}.csv")

def run_scrapers(mode, providers=None):
    """
    Run specified scrapers or all scrapers if none specified.
    
    Parameters:
        mode: WebDriver mode ('headless' or 'gui')
        providers: List of provider names to scrape, or None for all providers
    """
    if providers:
        # Run only specified scrapers
        scrapers = [(SCRAPERS[provider], mode) for provider in providers if provider in SCRAPERS]
    else:
        # Run all scrapers
        scrapers = [(scraper, mode) for scraper in SCRAPERS.values()]
    
    # Run scrapers in parallel and collect results
    results = parallel_scrape(scrapers)
    
    LOGGER.info(f"{len(results)} TV Providers Results returned.")
    # Create results dictionary
    results_dict = {}
    for i, (provider, _) in enumerate(scrapers):
        results_dict[provider.__name__.replace('scrape_', '').replace('_tv', '')] = results[i]
    LOGGER.info(f"Results Dictionary generated.")
    return results_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TV Channel Web Scraper")
    parser.add_argument('--mode', choices=['headless', 'gui'], default='headless', 
                      help='WebDriver mode: headless or gui (default: headless)')
    parser.add_argument('--output', choices=['excel', 'csv'], default='excel',
                      help='Output format: excel or csv (default: excel)')
    parser.add_argument('--providers', nargs='+', choices=list(SCRAPERS.keys()),
                      help='Specific providers to scrape (default: all providers)')
    args = parser.parse_args()

    try:
        # Run scrapers
        results = run_scrapers(args.mode, args.providers)
        
        # Generate summary file
        generate_summary_excel(results, args.output)
        
    except Exception as e:
        LOGGER.error(f"Error running scrapers: {e}")
        raise