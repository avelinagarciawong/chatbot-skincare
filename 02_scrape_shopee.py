import time
import random
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

os.makedirs("data", exist_ok=True)

# ── Konfigurasi ───────────────────────────────────────────
KEYWORDS = [
    "serum lokal indonesia",
    "moisturizer lokal indonesia", 
    "sunscreen lokal indonesia",
    "skincare somethinc",
    "skincare avoskin",
    "skincare wardah",
    "skincare npure",
    "skincare ms glow",
]

TARGET_PRODUK = 200   # mulai dari 200 dulu, bisa ditambah
DELAY_MIN     = 2.0
DELAY_MAX     = 4.0


def delay():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def buat_driver():
    """Buat Chrome driver dengan setting anti-deteksi."""
    options = Options()
    
    # Jangan pakai headless dulu agar lebih mudah debug
    # options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def scroll_halaman(driver, kali=3):
    """Scroll ke bawah agar produk ter-load."""
    for _ in range(kali):
        driver.execute_script("window.scrollBy(0, 800)")
        time.sleep(1.5)


def ambil_produk_dari_halaman(driver) -> list:
    """Ambil semua produk yang tampil di halaman pencarian."""
    produk_list = []
    
    try:
        # Tunggu produk muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.shopee-search-item-result__item")
            )
        )
    except:
        print("    ✗ Produk tidak ditemukan di halaman ini")
        return []

    items = driver.find_elements(
        By.CSS_SELECTOR, "div.shopee-search-item-result__item"
    )

    for item in items:
        try:
            # Nama produk
            nama = item.find_element(
                By.CSS_SELECTOR, "div[class*='ellipsis']"
            ).text.strip()

            # Harga
            try:
                harga = item.find_element(
                    By.CSS_SELECTOR, "span[class*='price']"
                ).text.strip()
            except:
                harga = ""

            # Rating
            try:
                rating = item.find_element(
                    By.CSS_SELECTOR, "span[class*='rating']"
                ).text.strip()
            except:
                rating = ""

            # Terjual
            try:
                terjual = item.find_element(
                    By.CSS_SELECTOR, "div[class*='sold']"
                ).text.strip()
            except:
                terjual = ""

            # Link produk
            try:
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = ""

            if nama:
                produk_list.append({
                    "nama_produk": nama,
                    "harga":       harga,
                    "rating":      rating,
                    "terjual":     terjual,
                    "link":        link,
                    "scraped_at":  datetime.now().isoformat(),
                    "sumber":      "shopee",
                })

        except Exception:
            continue

    return produk_list


def ambil_ulasan_produk(driver, link: str, nama_produk: str) -> list:
    """Buka halaman produk dan ambil ulasannya."""
    ulasan_list = []

    try:
        driver.get(link)
        delay()
        scroll_halaman(driver, kali=5)

        # Cari section ulasan
        try:
            ulasan_elements = driver.find_elements(
                By.CSS_SELECTOR, "div[class*='shopee-product-rating']"
            )
        except:
            return []

        for u in ulasan_elements[:8]:   # max 8 ulasan per produk
            try:
                teks = u.find_element(
                    By.CSS_SELECTOR, "div[class*='item-content']"
                ).text.strip()

                try:
                    bintang = len(u.find_elements(
                        By.CSS_SELECTOR, "svg[class*='filled']"
                    ))
                except:
                    bintang = 0

                if teks and len(teks) > 10:
                    ulasan_list.append({
                        "nama_produk":  nama_produk,
                        "teks_ulasan":  teks,
                        "rating":       bintang,
                        "sumber":       "shopee",
                        "scraped_at":   datetime.now().isoformat(),
                    })
            except:
                continue

    except Exception as e:
        print(f"    ✗ Error ambil ulasan: {e}")

    return ulasan_list


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  SHOPEE SELENIUM SCRAPER")
    print("=" * 55)
    print(f"  Target  : {TARGET_PRODUK} produk")
    print(f"  Browser : Chrome akan terbuka otomatis\n")

    driver = buat_driver()
    semua_produk = []
    semua_ulasan = []
    produk_seen  = set()

    try:
        # Buka Shopee dulu agar dapat cookies
        print("[*] Membuka Shopee...")
        driver.get("https://shopee.co.id")
        delay()

        for keyword in KEYWORDS:
            if len(semua_produk) >= TARGET_PRODUK:
                break

            print(f"\n🔍  Keyword: '{keyword}'")

            # Navigasi ke halaman pencarian
            url_search = (
                f"https://shopee.co.id/search?keyword="
                f"{keyword.replace(' ', '%20')}"
            )
            driver.get(url_search)
            delay()
            scroll_halaman(driver, kali=5)

            # Ambil produk dari halaman ini
            produk_halaman = ambil_produk_dari_halaman(driver)
            print(f"    {len(produk_halaman)} produk ditemukan")

            for produk in produk_halaman:
                if len(semua_produk) >= TARGET_PRODUK:
                    break

                nama = produk["nama_produk"]
                if nama in produk_seen:
                    continue

                produk_seen.add(nama)
                semua_produk.append(produk)

                # Ambil ulasan kalau ada link
                if produk.get("link"):
                    ulasan = ambil_ulasan_produk(
                        driver, produk["link"], nama
                    )
                    semua_ulasan.extend(ulasan)
                    print(f"    ✓ {nama[:40]}... → {len(ulasan)} ulasan")

                delay()

                # Simpan progress setiap 10 produk
                if len(semua_produk) % 10 == 0:
                    pd.DataFrame(semua_produk).to_csv(
                        "data/raw_shopee_produk.csv", index=False)
                    pd.DataFrame(semua_ulasan).to_csv(
                        "data/raw_shopee_ulasan.csv", index=False)
                    print(f"\n  💾 Progress: {len(semua_produk)} produk, "
                          f"{len(semua_ulasan)} ulasan tersimpan\n")

    except KeyboardInterrupt:
        print("\n\n  ⚠ Dihentikan manual — menyimpan data...")

    finally:
        driver.quit()

        # Simpan final
        df_produk = pd.DataFrame(semua_produk)
        df_ulasan = pd.DataFrame(semua_ulasan)

        df_produk.to_csv("data/raw_shopee_produk.csv", index=False)
        df_ulasan.to_csv("data/raw_shopee_ulasan.csv", index=False)

        print("\n" + "=" * 55)
        print(f"  ✓ Produk : {len(df_produk)} → data/raw_shopee_produk.csv")
        print(f"  ✓ Ulasan : {len(df_ulasan)} → data/raw_shopee_ulasan.csv")
        print("=" * 55)


if __name__ == "__main__":
    main()
