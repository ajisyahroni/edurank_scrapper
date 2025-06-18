import requests
from lxml import html
import re
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime


# Utility function to extract digits from a string
def extract_digits(text):
    """Extract digits from a string and return as integer, or None if conversion fails."""
    cleaned = re.sub(r'[^\d]', '', text.strip())
    return int(cleaned) if cleaned.isdigit() else None


# Utility function to normalize university name from URL
def get_normalized_university_name(url):
    path = urlparse(url).path 
    slug = path.strip("/").split("/")[-1]
    name = slug.replace("-", " ").title()  
    return name


# Main scraping function
def scrape_university_rank(url):
    # Send GET request and parse HTML
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    tree = html.fromstring(response.content)

    # Extract rankings using XPath
    def extract_rank_data(row):
        rank_xpath = f'//*[@id="content"]/div/main/article/section[1]/table/tbody/tr[{row}]/td/span[2]'
        total_xpath = f'//*[@id="content"]/div/main/article/section[1]/table/tbody/tr[{row}]/td/span[3]'
        rank = extract_digits(tree.xpath(rank_xpath)[0].text_content())
        total = extract_digits(tree.xpath(total_xpath)[0].text_content())
        return rank, total

    # Row mapping: row index in table → rank scope
    scopes = {
        1: "World",
        2: "Asia",
        3: "Indonesia",
        4: "City"
    }

    # Build the data list
    university_name = get_normalized_university_name(url)
    current_year = datetime.now().year
    data = []

    for row, scope in scopes.items():
        rank, total = extract_rank_data(row)
        data.append({
            "university": university_name,
            "year": current_year,
            "scope": scope,
            "rank": rank,
            "total_ranked": total
        })

    return pd.DataFrame(data)
# List of university URLs
urls = [
    'https://edurank.org/uni/muhammadiyah-university-of-surakarta/',
    'https://edurank.org/uni/muhammadiyah-university-of-yogyakarta/',
    'https://edurank.org/uni/ahmad-dahlan-university/'
]

# Collect DataFrames
all_dfs = []
for url in urls:
    try:
        df = scrape_university_rank(url)
        all_dfs.append(df)
        print(f"Scraped: {url}")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

# Combine all DataFrames
combined_df = pd.concat(all_dfs, ignore_index=True)

# Save to CSV
combined_df.to_csv("university_ranks.csv", index=False)
print("All data saved to university_ranks.csv")
