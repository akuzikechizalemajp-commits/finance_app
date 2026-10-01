from nta_source import fetch_nta_page


url = "https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm"

text = fetch_nta_page(url)

print("NTA page downloaded successfully!")
print()
print("First 2000 characters:")
print(text[:2000])