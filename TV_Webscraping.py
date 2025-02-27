from src.DirecTV import scrape_directv
from src.DirecTV_Stream import scrape_directv_stream
from src.FuboTV import scrape_fubo_tv
from src.HuluTV import scrape_hulu_tv
from src.SlingTV import scrape_sling_tv
from src.YoutubeTV import scrape_youtube_tv


if __name__ == "__main__":
    scrape_directv('gui')
    #scrape_directv_stream()
    #scrape_fubo_tv()
    #scrape_hulu_tv()
    #scrape_sling_tv()
    #scrape_youtube_tv()