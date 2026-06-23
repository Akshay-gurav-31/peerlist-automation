import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, subprocess
from datetime import datetime

# ================== CONFIG ==================
POST_URL = ""

# DEDICATED SCRIPT PROFILES (Isolated from normal Chrome to prevent crashes)
BOT_PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_profiles")

PROFILES = [
    "Bot_1",
    "Bot_2",
    "Bot_3",
    "Bot_4"
]
# ===========================================

CHROME_DRIVER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chromedriver-win64", "chromedriver.exe"
)


def kill_chrome():
    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],       capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True)
    time.sleep(1)


def get_driver(profile_name):
    options = uc.ChromeOptions()
    # The script will store its isolated Chrome data in this folder
    options.add_argument(f"--user-data-dir={BOT_PROFILES_DIR}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-session-crashed-bubble")

    driver = uc.Chrome(
        options=options,
        driver_executable_path=CHROME_DRIVER,
        use_subprocess=True,
    )
    driver.set_page_load_timeout(120)
    driver.maximize_window()
    return driver


def like_post(post_url):
    print(f"\n[START] {post_url}")
    print(f"[INFO]  Using dedicated bot profiles. No Chrome crash issues.\n")

    for i, profile in enumerate(PROFILES, 1):
        print(f"\n[{i}/{len(PROFILES)}] >> Profile: {profile}")
        driver = None
        try:
            kill_chrome()
            print("   [OPEN]  Opening Chrome...")
            driver = get_driver(profile)

            print("   [NAV]   Navigating directly to the post...")
            driver.get(post_url)
            
            # Wait for page and JS to fully load
            print("   [WAIT]  Waiting for the page to load (10s)...")
            time.sleep(10)
            
            # Scroll down slightly to ensure the button is visible
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(3)

            clicked = False
            try:
                # Use ActionChains to simulate a real user mouse click
                from selenium.webdriver.common.action_chains import ActionChains
                
                btn = driver.find_element(By.CSS_SELECTOR, 'button[title="Upvote"]')
                
                # Scroll the element to the center of the screen
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                time.sleep(2)
                
                # Move mouse over the button and click
                ActionChains(driver).move_to_element(btn).click().perform()
                print("   [OK]    Upvote clicked (Mouse Action)!")
                clicked = True
            except Exception as e:
                pass

            if not clicked:
                try:
                    # Backup plan (JS MouseEvent dispatch)
                    ok = driver.execute_script("""
                        var btn = document.querySelector('button[title="Upvote"]');
                        if (btn) { 
                            var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
                            btn.dispatchEvent(ev); 
                            return true; 
                        }
                        return false;
                    """)
                    if ok:
                        print("   [OK]    Upvote clicked (Backup JS Event)!")
                        clicked = True
                except:
                    pass

            if not clicked:
                print("   [WARN]  Click failed, please try manually.")
                input("   >> Press Enter after manual like... ")

            print("   [WAIT]  Waiting for 24 seconds after upvoting (as requested)...")
            time.sleep(24)
        except Exception as e:
            print(f"   [ERR]   {str(e)[:150]}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            kill_chrome()

        print(f"   [SAVE]  Profile {profile} saved! Loading the next profile...\n")
        time.sleep(2)

    print("=" * 50)
    print("[DONE] All profiles processed!")
    print("=" * 50)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else POST_URL
    like_post(url)
