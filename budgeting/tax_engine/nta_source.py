import requests
from bs4 import BeautifulSoup


def fetch_nta_page(url):
    """
    Download an official NTA webpage and return its text.
    """

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    # NTA pages may use Japanese character encodings.
    # Use the encoding detected by the response when available.
    if not response.encoding or response.encoding.lower() == "iso-8859-1":
        response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove things we don't need
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text("\n", strip=True)

    return text