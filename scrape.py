from firecrawl import Firecrawl
from dotenv import load_dotenv
import os

load_dotenv()

def Scrape():
    """
    Main function to scrape websites using Firecrawl and save the content as markdown files.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY environment variable not set.")
        return

    firecrawl = Firecrawl(api_key=api_key)

    urls_to_scrape = [
      "https://dgt.com.br",
      "https://dgt.com.br/ouvidoria",
      "https://dgt.com.br/compare",
      "https://dgt.com.br/videomonitoramento",
      "https://dgt.com.br/contato",
      "https://dgt.com.br/bridgefy",
      "https://dgt.com.br/smart-school",
      "https://dgt.com.br/smart-traffic",
      "https://dgt.com.br/smart-building",
      "https://dgt.com.br/smart-health",
      "https://dgt.com.br/smart-enviro",
      "https://dgt.com.br/smart-places"
    ]

    try:
        print(f"Starting batch scrape for {len(urls_to_scrape)} URLs...")
        job = firecrawl.batch_scrape(
            urls_to_scrape,
            formats=["markdown"],
            poll_interval=2,
            wait_timeout=120
        )

        if not job or not job.data:
            print("Scraping job did not return any data.")
            return

        print("Scraping completed. Saving files...")
        for item in job.data:
            if item and item.markdown and hasattr(item, 'metadata') and hasattr(item.metadata, 'og_url'):
                url = item.metadata.og_url
                filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
                os.makedirs("ScrapedData", exist_ok=True)
                with open(f"ScrapedData/{filename}.md", "w", encoding="utf-8") as f:
                    f.write(item.markdown)
                print(f"  - Saved {url} to ScrapedData/{filename}.md")
    except Exception as e:
        print(f"An error occurred during the scraping process: {e}")

if __name__ == "__main__":
    Scrape()