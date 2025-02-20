from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
from urllib.parse import quote_plus

# ✅ Excel dosyasının olup olmadığını kontrol et
file_path = "numaralar.xlsx"
if not os.path.exists(file_path):
    print(f"❌ HATA: '{file_path}' dosyası bulunamadı! Lütfen proje klasöründe olduğundan emin olun.")
    exit()

print(f"✅ '{file_path}' dosyası bulundu, işlem başlıyor...\n")

# ✅ Chrome profili ve driver yolu
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--user-data-dir=/Users/mesuthan/Library/Application Support/Google/Chrome")
chrome_options.add_argument("--profile-directory=Default")

# ✅ ChromeDriver başlat
service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# ✅ WhatsApp Web aç ve QR kodu bekle
driver.get("https://web.whatsapp.com")

try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="QR kod"]'))
    )
    input("📌 Lütfen QR kodu telefonunuzla tarayın ve Enter'a basın...")
except:
    print("📌 QR kod bulunamadı, WhatsApp Web zaten açık olabilir.")

print("✅ WhatsApp Web yüklendi!\n")

# ✅ Excel dosyasını oku
df = pd.read_excel(file_path, engine="openpyxl")

# Mesajları hızlı bir şekilde göndermek için for döngüsü
for index, row in df.iterrows():
    number = str(row["Telefon Numarası"]).strip()
    message = str(row["Mesaj"]).strip()

    # ✅ Numara başında + yoksa ekleyelim (Türkiye ve Suudi Arabistan için)
    if not number.startswith("+"):
        if number.startswith("966"):  # Suudi Arabistan numaraları
            number = "+" + number
        elif number.startswith("5"):  # Türkiye için 5 ile başlayan numaralar
            number = "+90" + number
        else:
            print(f"⚠ Hatalı numara formatı atlandı: {number}")
            continue

    # ✅ Mesajı URL'ye uygun hale getir
    encoded_message = quote_plus(message)

    # ✅ WhatsApp URL oluştur
    whatsapp_url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_message}"

    try:
        # ✅ WhatsApp URL'yi aç ve mesaj kutusunun yüklenmesini bekle
        driver.get(whatsapp_url)

        # Mesaj kutusunun yüklenmesini bekle
        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )

        # ✅ Mesaj kutusuna yaz ve gönder
        message_box.click()
        time.sleep(1)  # Mesaj kutusunun tam açılması için bekleyelim
        message_box.send_keys(message)

        # ✅ Gönder butonunu bul ve tıkla
        send_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]'))
        )
        send_button.click()

        print(f"✅ Mesaj gönderildi: {number}")

        # ✅ Mesajın gönderildiğini ve görüldüğünü kontrol et
        # Görülme işaretinin (✓✓) görünmesini bekle
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-testid="msg-checkmark"]'))
        )
        print(f"✅ Mesaj görüldü: {number}")

        # Kısa bekleme, engellemeyi önlemek için
        time.sleep(2)

    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {number} - Hata: {str(e)}")

print("🎉 Tüm mesajlar gönderildi!")
driver.quit()
