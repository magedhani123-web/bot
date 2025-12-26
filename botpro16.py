import time
import random
import os
import shutil
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- [ الإعدادات الأساسية ] ---
SEARCH_KEYWORDS = "وش الحلم اللي حققته" 
VIDEO_ID = "MrKhyV4Gcog"
DIRECT_URL = f"https://youtube.com/shorts/{VIDEO_ID}"
TOR_PROXY = "socks5://127.0.0.1:9050"

# --- [ مكتبة الأنظمة الشاملة ] ---
DEVICES = [
    # الهواتف (أندرويد و iOS)
    {"name": "Samsung S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) Chrome/119.0.0.0 Mobile", "plat": "Linux armv8l", "gpu": "Adreno 740", "w": 360, "h": 800},
    {"name": "iPhone 15 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/605.1", "plat": "iPhone", "gpu": "Apple GPU", "w": 393, "h": 852},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) Chrome/115.0.0.0 Mobile", "plat": "Linux aarch64", "gpu": "Mali-G710", "w": 412, "h": 915},
    {"name": "Xiaomi 13 Pro", "ua": "Mozilla/5.0 (Linux; Android 13; 2210132G) Chrome/118.0.0.0 Mobile", "plat": "Linux armv8l", "gpu": "Adreno 730", "w": 393, "h": 873},
    {"name": "Oppo Reno 10", "ua": "Mozilla/5.0 (Linux; Android 13; CPH2521) Chrome/116.0.0.0 Mobile", "plat": "Linux armv8l", "gpu": "Mali-G610", "w": 360, "h": 800},
    {"name": "iPad Pro", "ua": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 Safari/605.1", "plat": "MacIntel", "gpu": "Apple GPU", "w": 1024, "h": 1366},
    
    # الكمبيوترات (ويندوز، ماك، لينكس)
    {"name": "Windows 11 (Edge)", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edg/120.0.0.0", "plat": "Win32", "gpu": "NVIDIA RTX 4090", "w": 1920, "h": 1080},
    {"name": "MacBook Air (M2)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/121.0.0.0", "plat": "MacIntel", "gpu": "Apple M2", "w": 1440, "h": 900},
    {"name": "Linux Desktop (Ubuntu)", "ua": "Mozilla/5.0 (X11; Linux x86_64) Chrome/119.0.0.0", "plat": "Linux x86_64", "gpu": "AMD Radeon RX 6700", "w": 1366, "h": 768}
]

def get_current_ip():
    proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    try: return requests.get('https://api.ipify.org', proxies=proxies, timeout=10).text
    except: return "Unknown"

def inject_ultra_stealth(driver, dev):
    """تزييف الهوية والمنطقة الزمنية والحساسات"""
    tz = random.choice(['America/New_York', 'Europe/Paris', 'Asia/Dubai', 'Asia/Riyadh', 'Europe/London'])
    js = f"""
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
    Object.defineProperty(Intl.DateTimeFormat().resolvedOptions(), 'timeZone', {{value: '{tz}'}});
    
    // تزييف البطارية
    navigator.getBattery = () => Promise.resolve({{charging: true, level: {random.uniform(0.6, 0.9)}}});

    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37446) return '{dev["gpu"]}';
        return getParam.apply(this, arguments);
    }};
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})

def run_imperial_session(count):
    dev = random.choice(DEVICES)
    print(f"\n--- 👑 الجلسة {count} | الجهاز: {dev['name']} ---")
    print(f"🌍 IP: {get_current_ip()}")

    options = uc.ChromeOptions()
    p_dir = os.path.abspath(f"imperial_session_{random.randint(1000, 9999)}")
    options.add_argument(f'--user-data-dir={p_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={dev['w']},{dev['h']}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        inject_ultra_stealth(driver, dev)
        wait = WebDriverWait(driver, 25)

        # 1. الدخول عبر البحث
        driver.get("https://www.youtube.com")
        time.sleep(5)
        try:
            agree = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Agree') or contains(@aria-label, 'موافق')]")
            if agree: agree[0].click()
            
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in SEARCH_KEYWORDS:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{VIDEO_ID}')]"))).click()
        except: driver.get(DIRECT_URL)

        # 2. المشاهدة مع تغيير السرعة العشوائي
        video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        driver.execute_script("arguments[0].play();", video)
        
        # ميزة تغيير السرعة
        random_speed = random.choice([0.75, 1.0, 1.25, 1.5])
        driver.execute_script(f"arguments[0].playbackRate = {random_speed};", video)
        print(f"⚡ السرعة الحالية: {random_speed}x")

        watch_time = random.randint(65, 95)
        print(f"📺 مشاهدة جارية لـ {watch_time} ثانية...")
        
        # حركات بشرية (Scroll)
        time.sleep(watch_time // 2)
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 600)});")
        
        # إعادة السرعة للطبيعية في منتصف المشاهدة
        time.sleep(5)
        driver.execute_script("arguments[0].playbackRate = 1.0;", video)

        # 3. التفاعل (لايك ومشاركة)
        if random.random() < 0.55:
            try:
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[contains(@aria-label, 'like') or contains(@aria-label, 'إعجاب')]"))
                print("👍 لايك")
                time.sleep(2)
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Share') or contains(@aria-label, 'مشاركة')]"))
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                print("🔗 مشاركة")
            except: pass

        print(f"✅ اكتملت المهمة.")

    except Exception as e:
        print(f"❌ خطأ: {str(e)[:50]}")
    finally:
        driver.quit()
        if p_dir: shutil.rmtree(p_dir, ignore_errors=True)

if __name__ == "__main__":
    os.system("pkill -f chrome")
    for i in range(500): # عدد الجلسات
        run_imperial_session(i + 1)
        time.sleep(random.randint(20, 45))
