from bs4 import BeautifulSoup
import os

html_file = "data/debug_html/halaman_2.html"
html = open(html_file, encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

# Check if there is "Login" or "Masuk" button in header
login_buttons = [a for a in soup.find_all("a") if "login" in a.get("href", "").lower() or "masuk" in a.get_text().lower()]
print("Login links/buttons found:", len(login_buttons))
for btn in login_buttons:
    print("  - Link:", btn.get("href"), "Text:", btn.get_text().strip())

# Check for search bar value or page title
title = soup.find("title")
print("Page Title:", title.get_text().strip() if title else "No Title")
