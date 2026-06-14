import time
import random
import pandas as pd
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.makedirs("data", exist_ok=True)

# ── Konfigurasi ───────────────────────────────────────────
KEYWORDS = [
    "serum lokal indonesia",
    "moisturizer lokal indonesia"
    # "sunscreen lokal indonesia",
    # "skincare somethinc",
    # "skincare avoskin",
    # "skincare wardah",
    # "skincare npure",
    # "skincare ms glow",
]

TARGET_PRODUK = 200   # mulai dari 200 dulu, bisa ditambah
DELAY_MIN     = 2.0
DELAY_MAX     = 4.0


def delay():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def buat_driver():
    """Buat Chrome driver dengan setting anti-deteksi."""
    options = uc.ChromeOptions()
    
    # Jangan pakai headless dulu agar lebih mudah debug
    # options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = uc.Chrome(options=options)
    return driver


def scroll_halaman(driver, kali=3):
    """Scroll ke bawah agar produk ter-load."""
    for _ in range(kali):
        driver.execute_script("window.scrollBy(0, 800)")
        time.sleep(1.5)


def ambil_produk_dari_halaman(driver) -> list:
    """Ambil semua produk yang tampil di halaman pencarian dengan selector cadangan."""
    produk_list = []
    
    # Coba beberapa selector umum untuk item hasil pencarian Shopee
    selectors = [
        "div[data-sqe='item']",
        "div.shopee-search-item-result__item",
        "li.shopee-search-item-result__item",
        "[class*='shopee-search-item-result']",
        "a[href*='/product/']"
    ]
    
    items = []
    for selector in selectors:
        try:
            # Tunggu produk muncul
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            items = driver.find_elements(By.CSS_SELECTOR, selector)
            if items:
                break
        except:
            continue
            
    if not items:
        print("    ✗ Produk tidak ditemukan di halaman ini")
        return []

    for item in items:
        try:
            # Nama produk
            nama = ""
            for name_sel in ["[data-sqe='name']", "div[class*='ellipsis']", "div[class*='name']", "div[class*='title']"]:
                try:
                    nama = item.find_element(By.CSS_SELECTOR, name_sel).text.strip()
                    if nama:
                        break
                except:
                    continue

            if not nama:
                continue

            # Harga
            harga = ""
            for price_sel in ["[data-sqe='price']", "span[class*='price']", "div[class*='price']", "[class*='Price']"]:
                try:
                    harga = item.find_element(By.CSS_SELECTOR, price_sel).text.strip()
                    if harga:
                        break
                except:
                    continue

            # Rating
            rating = ""
            for rating_sel in ["span[class*='rating']", "div[class*='rating']", "[class*='Rating']"]:
                try:
                    rating = item.find_element(By.CSS_SELECTOR, rating_sel).text.strip()
                    if rating:
                        break
                except:
                    continue

            # Terjual
            terjual = ""
            for sold_sel in ["[data-sqe='sold']", "div[class*='sold']", "[class*='Sold']", "[class*='sold']"]:
                try:
                    terjual = item.find_element(By.CSS_SELECTOR, sold_sel).text.strip()
                    if terjual:
                        break
                except:
                    continue

            # Link produk
            link = ""
            try:
                if item.tag_name == "a":
                    link = item.get_attribute("href")
                else:
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = ""

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
        ulasan_elements = []
        review_selectors = [
            "div[data-cmtid]",
            "div.shopee-product-comment-list > div",
            "div.shopee-product-rating",
            "div[class*='shopee-product-rating']",
            "div[class*='product-rating']",
            "div[class*='comment']"
        ]
        
        for selector in review_selectors:
            try:
                ulasan_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if ulasan_elements:
                    break
            except:
                continue

        if not ulasan_elements:
            return []

        for u in ulasan_elements[:8]:   # max 8 ulasan per produk
            try:
                # Ambil teks ulasan
                teks = ""
                text_selectors = [
                    "div.YNedDV",
                    "div[class*='YNedDV']",
                    "div.meQyXP",
                    "div[class*='item-content']",
                    "div[class*='content']",
                    "div[class*='rating__main']",
                    "div[class*='comment']",
                    "div.shopee-product-rating__main"
                ]
                for text_sel in text_selectors:
                    try:
                        teks = u.find_element(By.CSS_SELECTOR, text_sel).text.strip()
                        if teks:
                            break
                    except:
                        continue

                # Ambil jumlah bintang
                bintang = 0
                star_selectors = [
                    "svg.icon-rating-solid",
                    "svg[class*='icon-rating-solid']",
                    "svg[class*='filled']",
                    "svg[class*='star']",
                    "div[class*='star']"
                ]
                for star_sel in star_selectors:
                    try:
                        stars = u.find_elements(By.CSS_SELECTOR, star_sel)
                        if stars:
                            bintang = len(stars)
                            break
                    except:
                        continue

                if teks and len(teks) > 5:
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
        
        # Jeda agar user bisa login terlebih dahulu
        print("\n" + "=" * 60)
        print(" SILAKAN LOGIN / SELESAIKAN VERIFIKASI DI BROWSER CHROME SEKARANG")
        print(" Setelah selesai login dan masuk ke beranda Shopee,")
        print(" kembali ke terminal ini dan tekan ENTER untuk mulai scraping.")
        print("=" * 60 + "\n")
        input("Tekan ENTER setelah Anda selesai login...")

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
