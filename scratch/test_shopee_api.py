import undetected_chromedriver as uc
import time
import json

def main():
    print("Membuka browser...")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    
    try:
        driver.get("https://shopee.co.id")
        print("Silakan login/verifikasi di browser...")
        input("Tekan ENTER setelah selesai login...")
        
        # Test call API for newest=0 (page 0)
        match_id = "11043253" # Perawatan Wajah subcategory ID
        limit = 60
        offset = 0
        
        script = f"""
        return fetch("https://shopee.co.id/api/v4/search/search_items?by=relevancy&limit={limit}&match_id={match_id}&newest={offset}&order=desc&page_type=search&scenario=PAGE_OTHERS&version=5")
            .then(r => r.json())
            .catch(e => null);
        """
        print("Mengambil data API page 0...")
        data = driver.execute_script(script)
        
        if data and "items" in data and data["items"]:
            items = data["items"]
            print(f"Berhasil mengambil {len(items)} items!")
            first_item = items[0]
            print("\n--- SAMPLE ITEM ---")
            print(json.dumps(first_item, indent=2))
        else:
            print("Gagal mengambil data atau data kosong:", data)
            
    finally:
        input("Tekan ENTER untuk menutup browser...")
        driver.quit()

if __name__ == "__main__":
    main()
