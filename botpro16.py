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

# --- [ 1. إعدادات القناة والفيديوهات ] ---
MY_VIDEOS = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# قائمة المصادر الوهمية (لجعل الزيارة تبدو قادمة من مواقع تواصل)
REFERRERS = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.instagram.com/",
    "https://www.bing.com/"
]

TOR_PROXY = "socks5://127.0.0.1:9050"

# --- [ 2. مكتبة الأجهزة ] ---
DEVICES = [
    {"name": "Samsung S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) Chrome/119.0.0.0 Mobile", "plat": "Linux armv8l", "w": 360, "h": 800},
    {"name": "Windows 11 (Chrome)", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080},
    {"name": "MacBook Air M2", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900},
    {"name": "iPhone 14 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/605.1", "plat": "iPhone", "w": 393, "h": 852}
]

def renew_tor_ip():
    """محاولة لتجديد IP الخاص بـ Tor لتقليل الحظر"""
    print("🔄 جاري طلب هوية جديدة من Tor...")
    os.system("sudo killall -HUP tor") # أمر إعادة تحميل Tor في لينكس
    time.sleep(5)

def get_current_ip():
    proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    try: return requests.get('https://api.ipify.org', proxies=proxies, timeout=10).text
    except: return "Unknown"

def inject_stealth(driver, dev):
    """إخفاء الأتمتة"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
        """
    })

def handle_popups(driver):
    """التعامل مع الموافقات والنوافذ المنبثقة"""
    try:
        # زر الموافقة على الكوكيز
        btn = driver.find_element(By.XPATH, "//button[contains(., 'Accept') or contains(., 'Agree') or contains(., 'موافق')]")
        btn.click()
        print("🍪 تم قبول الكوكيز.")
    except: pass

    # محاولة إغلاق أي نافذة منبثقة عشوائية
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except: pass

def run_session(count):
    dev = random.choice(DEVICES)
    video = random.choice(MY_VIDEOS)
    referrer = random.choice(REFERRERS)
    
    # تجديد IP كل 5 جلسات
    if count % 5 == 0:
        renew_tor_ip()

    print(f"\n--- 🚀 الجلسة {count} | {dev['name']} ---")
    print(f"🌍 IP: {get_current_ip()} | 🔗 المصدر: {referrer}")

    options = uc.ChromeOptions()
    p_dir = os.path.abspath(f"profile_{count}")
    
    options.add_argument(f'--user-data-dir={p_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--mute-audio') # كتم الصوت لتوفير الموارد
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        inject_stealth(driver, dev)
        wait = WebDriverWait(driver, 25)

        # 1. تزييف المصدر (Referrer Spoofing)
        # نقوم بفتح المصدر أولاً ثم الانتقال لليوتيوب
        driver.get(referrer)
        time.sleep(2)

        # 2. الانتقال للفيديو
        video_url = f"https://www.youtube.com/watch?v={video['id']}"
        driver.execute_script(f"window.location.href = '{video_url}';")
        
        # الانتظار حتى تحميل الفيديو
        time.sleep(5)
        handle_popups(driver)

        # التحقق من كشف البوت
        if "confirm you're not a bot" in driver.page_source.lower():
            print("⚠️ تم كشف البوت! تخطي...")
            return

        # 3. تقليل الجودة إجبارياً (مهم جداً للـ Cloud Shell)
        try:
            driver.execute_script("document.querySelector('video').style.display = 'block';")
            # نحاول ضبط الجودة للأقل
            driver.execute_script("""
                var vid = document.querySelector('video');
                if(vid) { 
                    vid.pause();
                    vid.currentTime = 0; 
                    vid.play(); 
                }
            """)
            # ملاحظة: يوتيوب يغير الـ API باستمرار، لكن تقليل حمل الصفحة يساعد
        except: pass

        print(f"📺 مشاهدة: {video['keywords']}")
        
        # 4. محاكاة المشاهدة البشرية
        duration = random.randint(60, 120)
        start_time = time.time()
        
        while time.time() - start_time < duration:
            time.sleep(random.randint(5, 15))
            # سكرول عشوائي
            driver.execute_script(f"window.scrollBy(0, {random.choice([100, 200, -100])});")
            
            # تحريك الماوس (وهمي) إذا لم يكن موبايل
            if "Win" in dev['plat'] or "Mac" in dev['plat']:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)

        print(f"✅ تمت المشاهدة ({duration}ث).")

    except Exception as e:
        print(f"❌ خطأ: {str(e)[:50]}")
    finally:
        if driver: driver.quit()
        if os.path.exists(p_dir): shutil.rmtree(p_dir, ignore_errors=True)

if __name__ == "__main__":
    os.system("pkill -f chrome")
    # محاولة تشغيل Tor إذا لم يكن يعمل
    os.system("nohup tor > /dev/null 2>&1 &") 
    time.sleep(3)
    
    for i in range(1, 1000):
        run_session(i)
        sleep_time = random.randint(30, 60)
        print(f"💤 استراحة {sleep_time}ث...")
        time.sleep(sleep_time)
