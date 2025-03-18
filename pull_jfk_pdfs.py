import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from tqdm import tqdm

# URL of the page with all 1,123 PDF links
page_url = "https://www.archives.gov/jfk"  # Replace with the exact URL of the page

# Base domain to convert relative URLs to absolute
base_domain = "https://www.archives.gov"

# Directory to save the downloaded PDFs
download_dir = "jfk_records"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Headers to mimic a browser (helps avoid being blocked)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to get all PDF links from the page
def get_pdf_links():
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all <a> tags with href attributes
    pdf_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Check if the href matches the pattern for JFK release PDFs
        if href.startswith("/files/research/jfk/releases/2025/0318/") and href.endswith(".pdf"):
            # Convert relative URL to absolute
            full_url = base_domain + href
            pdf_links.append(full_url)
    
    return pdf_links

# Function to download a PDF
def download_pdf(pdf_url, save_path):
    try:
        response = requests.get(pdf_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            print(f"Failed to download {pdf_url}: Status code {response.status_code}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")

# Main script
def main():
    # Get all PDF links
    pdf_links = get_pdf_links()
    print(f"Found {len(pdf_links)} PDF links.")
    
    if len(pdf_links) == 0:
        print("No links found. Please check the page URL or the href pattern.")
        return
    
    # Download all PDFs
    for pdf_url in tqdm(pdf_links, desc="Downloading PDFs"):
        # Decode the URL to get a clean filename
        parsed_url = urllib.parse.urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)
        # Decode URL-encoded characters (e.g., %20 to space)
        filename = urllib.parse.unquote(filename)
        save_path = os.path.join(download_dir, filename)
        download_pdf(pdf_url, save_path)

if __name__ == "__main__":
    main()
