import requests
import time
import random
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TrendyolAccountBot:
    def __init__(self):

        self.sms_config = {
            "base_url": "https://api.durianrcs.com/out/ext_api",
            "username": "",
            "api_key": "",
        }

        self.emailfake_driver = None
        self.trendyol_driver = None

        self.setup_emailfake_driver()

        self.stats = {"success_count": 0, "failed_count": 0, "total_attempts": 0}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.instant_save_file = f"trendyol_accounts_{timestamp}.txt"

    def get_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        return chrome_options

    def get_chromedriver_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

        if not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver bulunamadı: {chromedriver_path}")
            logger.error("Lütfen chromedriver.exe dosyasını bot ile aynı klasöre koyun")
            raise FileNotFoundError(f"ChromeDriver bulunamadı: {chromedriver_path}")

        return chromedriver_path

    def setup_emailfake_driver(self):
        try:
            logger.info("EmailFake tarayıcısı başlatılıyor...")

            chrome_options = self.get_chrome_options()
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--window-position=0,0")

            chromedriver_path = self.get_chromedriver_path()
            service = Service(chromedriver_path)

            self.emailfake_driver = webdriver.Chrome(
                service=service, options=chrome_options
            )
            self.emailfake_driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            self.emailfake_wait = WebDriverWait(self.emailfake_driver, 20)

            logger.info("EmailFake tarayıcısı başarıyla başlatıldı")

        except Exception as e:
            logger.error(f"EmailFake tarayıcısı başlatılırken hata: {e}")
            raise

    def setup_trendyol_driver(self):
        try:
            logger.info("TrendyolGO tarayıcısı başlatılıyor...")

            chrome_options = self.get_chrome_options()
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--window-position=820,0")

            chromedriver_path = self.get_chromedriver_path()
            service = Service(chromedriver_path)

            self.trendyol_driver = webdriver.Chrome(
                service=service, options=chrome_options
            )
            self.trendyol_driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            self.trendyol_wait = WebDriverWait(self.trendyol_driver, 30)  # 20'den 30'a çıkarıldı

            logger.info("TrendyolGO tarayıcısı başarıyla başlatıldı")

        except Exception as e:
            logger.error(f"TrendyolGO tarayıcısı başlatılırken hata: {e}")
            raise

    def is_emailfake_alive(self):
        try:
            if self.emailfake_driver:
                self.emailfake_driver.current_url
                return True
            return False
        except Exception:
            return False

    def is_trendyol_alive(self):
        try:
            if self.trendyol_driver:
                self.trendyol_driver.current_url
                return True
            return False
        except Exception:
            return False

    def ensure_emailfake_session(self):
        if not self.is_emailfake_alive():
            logger.warning("EmailFake session sonlandı, yeniden başlatılıyor...")
            try:
                self.setup_emailfake_driver()
            except Exception as e:
                logger.error(f"EmailFake session yeniden başlatma hatası: {e}")
                raise

    def ensure_trendyol_session(self):
        if not self.is_trendyol_alive():
            logger.warning("TrendyolGO session sonlandı, yeniden başlatılıyor...")
            try:
                self.setup_trendyol_driver()
            except Exception as e:
                logger.error(f"TrendyolGO session yeniden başlatma hatası: {e}")
                raise

    def get_phone_number(self, pid, max_retries=100000):
        try:
            url = f"{self.sms_config['base_url']}/getMobile"
            params = {
                "name": self.sms_config["username"],
                "ApiKey": self.sms_config["api_key"],
                "cuy": "tr",
                "pid": pid,
                "num": 1,
                "noblack": 0,
                "serial": 2,
            }

            for retry in range(max_retries):
                logger.info(
                    f"Türk telefon numarası alınıyor... Deneme {retry + 1}/{max_retries}"
                )
                response = requests.get(url, params=params, timeout=30)
                data = response.json()

                if data.get("code") == 200:
                    phone_number = data.get("data", "")
                    logger.info(f"Türk telefon numarası alındı: {phone_number}")
                    return phone_number
                elif data.get("code") == 906:
                    logger.warning(
                        f"Türk numara listesi boş, 30 saniye bekleniyor... ({retry + 1}/{max_retries})"
                    )
                    if retry < max_retries - 1:
                        time.sleep(30)
                    else:
                        logger.error(
                            "Maksimum deneme sayısına ulaşıldı, Türk numara alınamadı"
                        )
                        return None
                else:
                    logger.error(
                        f"Türk numara alma hatası: {data.get('msg', 'Bilinmeyen hata')}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Türk numara alma isteğinde hata: {e}")
            return None

    def get_sms_code(self, phone_number, pid, max_attempts=12, wait_time=10):
        try:
            url = f"{self.sms_config['base_url']}/getMsg"
            params = {
                "name": self.sms_config["username"],
                "ApiKey": self.sms_config["api_key"],
                "pn": phone_number,
                "pid": pid,
                "serial": 2,
            }

            logger.info(f"SMS kodu bekleniyor: {phone_number}")

            for attempt in range(max_attempts):
                response = requests.get(url, params=params, timeout=30)
                data = response.json()

                if data.get("code") == 200:
                    sms_code = data.get("data", "")
                    logger.info(f"SMS kodu alındı: {sms_code}")
                    return sms_code
                elif data.get("code") == 908:
                    logger.info(
                        f"SMS bekleniyor... Deneme {attempt + 1}/{max_attempts}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"SMS alma hatası: {data.get('msg', 'Bilinmeyen hata')}"
                    )
                    break

            logger.warning("SMS kodu alınamadı, zaman aşımı")
            return None

        except Exception as e:
            logger.error(f"SMS kodu alma isteğinde hata: {e}")
            return None

    def release_phone_number(self, phone_number, pid):
        try:
            url = f"{self.sms_config['base_url']}/passMobile"
            params = {
                "name": self.sms_config["username"],
                "ApiKey": self.sms_config["api_key"],
                "pn": phone_number,
                "pid": pid,
                "serial": 2,
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if data.get("code") == 200:
                logger.info(f"Numara başarıyla serbest bırakıldı: {phone_number}")
                return True
            else:
                logger.error(
                    f"Numara serbest bırakma hatası: {data.get('msg', 'Bilinmeyen hata')}"
                )
                return False

        except Exception as e:
            logger.error(f"Numara serbest bırakma isteğinde hata: {e}")
            return False

    def setup_emailfake_initial(self, domain):
        try:
            logger.info("EmailFake sitesine gidiliyor...")
            self.emailfake_driver.get("https://emailfake.com/")
            time.sleep(3)

            domain_input = self.emailfake_wait.until(
                EC.presence_of_element_located((By.ID, "domainName2"))
            )

            domain_input.click()
            time.sleep(0.5)

            current_domain = domain_input.get_attribute("value")
            logger.info(f"Mevcut domain değeri: {current_domain}")

            self.emailfake_driver.execute_script(
                """
                arguments[0].focus();
                arguments[0].value = '';
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
                domain_input,
                domain,
            )

            time.sleep(1)

            final_domain = domain_input.get_attribute("value")
            logger.info(f"Domain ayarlandı: {final_domain}")

            if final_domain != domain:
                logger.warning(
                    f"Domain beklenen değer değil! Beklenen: {domain}, Mevcut: {final_domain}"
                )

                domain_input.clear()
                time.sleep(0.3)
                domain_input.send_keys(domain)
                time.sleep(0.5)
                final_check = domain_input.get_attribute("value")
                logger.info(f"İkinci deneme sonucu: {final_check}")

            logger.info(f"Domain ayarlandı: {domain} (henüz Enter basılmadı)")

            logger.info("EmailFake hazırlandı")
            return True

        except Exception as e:
            logger.error(f"EmailFake hazırlanmasında hata: {e}")
            return False

    def create_email_with_username(self, username):
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                logger.info(f"Email oluşturma deneme {retry + 1}/{max_retries}: {username}")
                
                self.ensure_emailfake_session()
                
                # Sayfayı yenile
                self.emailfake_driver.refresh()
                time.sleep(4)
                
                # Username input'unu her seferinde yeniden bul
                username_input = self.emailfake_wait.until(
                    EC.element_to_be_clickable((By.ID, "userName"))
                )
                
                try:
                    # JavaScript ile doldur
                    self.emailfake_driver.execute_script(
                        """
                        arguments[0].focus();
                        arguments[0].value = '';
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                        username_input,
                        username,
                    )
                    logger.info(f"Username JavaScript ile girildi: {username}")
                except Exception as e:
                    logger.warning(f"JavaScript girişi başarısız, normal yöntem: {e}")
                    # Element'i yeniden bul (stale olabilir)
                    username_input = self.emailfake_driver.find_element(By.ID, "userName")
                    username_input.clear()
                    username_input.send_keys(username)
                
                time.sleep(1.5)
                
                # Enter'a bas - element'i yeniden bul
                try:
                    username_input.send_keys("\n")
                except:
                    # Stale olmuşsa yeniden bul
                    username_input = self.emailfake_driver.find_element(By.ID, "userName")
                    username_input.send_keys("\n")
                
                time.sleep(4)
                
                # Email elementini bul
                email_element = self.emailfake_wait.until(
                    EC.presence_of_element_located((By.ID, "email_ch_text"))
                )
                current_email = email_element.text
                
                if current_email and "@" in current_email:
                    logger.info(f"Email başarıyla oluşturuldu: {current_email}")
                    return current_email
                else:
                    logger.warning(f"Email oluşturulamadı veya geçersiz: {current_email}")
                    if retry < max_retries - 1:
                        time.sleep(2)
                        continue
                
            except Exception as e:
                logger.warning(f"Email oluşturma deneme {retry + 1} hatası: {e}")
                
                if retry < max_retries - 1:
                    logger.info(f"Deneme {retry + 1} başarısız, {retry + 2}. deneme yapılıyor...")
                    time.sleep(3)
                    continue
                else:
                    logger.error(f"Email oluşturma {max_retries} denemede başarısız oldu")
                    return None
        
        return None

    def get_verification_code_from_email(self, max_attempts=30, wait_time=10):
        try:
            logger.info("Email doğrulama kodu bekleniyor...")

            for attempt in range(max_attempts):
                try:

                    self.emailfake_driver.refresh()
                    time.sleep(2)

                    emails = self.emailfake_driver.find_elements(By.CLASS_NAME, "e7m")

                    for email in emails:
                        if "Trendyol GO" in email.text and "KOD:" in email.text:

                            logger.info(f"Email içeriği: {email.text}")

                            patterns = [
                                r"KOD:\s*(\d{6})(?!\d)",
                                r"KOD\s*:\s*(\d{6})(?!\d)",
                                r"KOD\s+(\d{6})(?!\d)",
                                r"(?<!\d)(\d{6})(?!\d)",
                                r"(?<!\d)(\d{5})(?!\d)",
                                r"(?<!\d)(\d{4})(?!\d)",
                            ]

                            verification_code = None
                            for pattern in patterns:
                                matches = re.findall(pattern, email.text)
                                if matches:

                                    for match in matches:
                                        if len(match) >= 4 and len(match) <= 6:

                                            if not (
                                                len(match) == 4
                                                and match.startswith("20")
                                            ):
                                                verification_code = match
                                                logger.info(
                                                    f"Doğrulama kodu bulundu (pattern: {pattern}): {verification_code}"
                                                )
                                                break
                                    if verification_code:
                                        break

                            if verification_code:
                                return verification_code

                    logger.info(
                        f"Doğrulama kodu bekleniyor... Deneme {attempt + 1}/{max_attempts}"
                    )
                    time.sleep(wait_time)

                except Exception as e:
                    logger.warning(f"Email kontrol edilirken hata: {e}")
                    time.sleep(wait_time)

            logger.warning("Email doğrulama kodu bulunamadı")
            return None

        except Exception as e:
            logger.error(f"Email doğrulama kodu alma hatası: {e}")
            return None

    def check_email_error(self):
        """Trendyol'da email hata mesajını kontrol eder"""
        try:
            # Türkçe hata mesajını ara
            error_selectors = [
                "//div[contains(text(), 'Bu e-posta adresi kullanılamaz')]",
                "//div[contains(text(), 'bu e-posta adresi kullanılamaz')]",
                "//div[contains(text(), 'BU E-POSTA ADRESİ KULLANILAMAZ')]",
                "//span[contains(text(), 'Bu e-posta adresi kullanılamaz')]",
                "//p[contains(text(), 'Bu e-posta adresi kullanılamaz')]",
                "div.body-2-regular:contains('Bu e-posta adresi kullanılamaz')",
                "[class*='alert'], [class*='error'], [class*='warning']",
                "[role='alert']"
            ]
            
            for selector in error_selectors:
                try:
                    if selector.startswith('//'):
                        error_element = WebDriverWait(self.trendyol_driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        error_element = WebDriverWait(self.trendyol_driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    
                    if error_element and error_element.is_displayed():
                        error_text = error_element.text.lower()
                        if "e-posta adresi kullanılamaz" in error_text or "email" in error_text:
                            logger.warning(f"Email hata mesajı bulundu: {error_element.text}")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Email hata kontrolü sırasında hata: {e}")
            return False
    
    def increment_email_number(self, email):
        """Email sonundaki sayıyı artırır (mehmet2@domain.com -> mehmet3@domain.com)"""
        try:
            import re
            
            # Email'i username ve domain olarak ayır
            username, domain = email.split('@', 1)
            
            # Username sonundaki sayıyı bul
            match = re.search(r'(\d+)$', username)
            
            if match:
                # Mevcut sayıyı al ve artır
                current_number = int(match.group(1))
                new_number = current_number + 1
                
                # Eski sayıyı yeni sayı ile değiştir
                new_username = re.sub(r'\d+$', str(new_number), username)
            else:
                # Eğer sayı yoksa 2 ekle
                new_username = username + '2'
            
            new_email = f"{new_username}@{domain}"
            logger.info(f"Email güncellendi: {email} -> {new_email}")
            return new_email, new_username
            
        except Exception as e:
            logger.error(f"Email numara artırma hatası: {e}")
            return email, None
    
    def register_on_trendyol(self, email, password, max_email_attempts=5):
        """Trendyol'a kayıt ol - email hata durumunda otomatik düzeltir"""
        current_email = email
        current_username = email.split('@')[0]
        
        for attempt in range(max_email_attempts):
            try:
                logger.info(f"TrendyolGO kayıt denemesi {attempt + 1}/{max_email_attempts} - Email: {current_email}")
                
                if not self.is_trendyol_alive():
                    self.setup_trendyol_driver()

                logger.info("TrendyolGO kayıt sayfasına gidiliyor...")
                self.trendyol_driver.get("https://tgoyemek.com/uyelik")
                time.sleep(5)

                try:
                    close_buttons = self.trendyol_driver.find_elements(
                        By.CSS_SELECTOR,
                        "[class*='close'], [class*='dismiss'], button[aria-label*='close'], button[aria-label*='Close']",
                    )
                    for btn in close_buttons:
                        try:
                            if btn.is_displayed():
                                btn.click()
                                time.sleep(1)
                                logger.info("Overlay kapatıldı")
                        except:
                            pass
                except:
                    pass

                email_input = self.trendyol_wait.until(
                    EC.presence_of_element_located((By.ID, "email"))
                )

                self.trendyol_driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    email_input,
                )
                email_input.click()
                time.sleep(0.5)
                email_input.clear()
                time.sleep(0.3)

                for char in current_email:
                    email_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))

                logger.info(f"Email insan gibi yazıldı: {current_email}")
                time.sleep(1)

                password_input = self.trendyol_wait.until(
                    EC.presence_of_element_located((By.ID, "password"))
                )

                self.trendyol_driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    password_input,
                )
                password_input.click()
                time.sleep(0.5)
                password_input.clear()
                time.sleep(0.3)

                for char in password:
                    password_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))

                logger.info("Şifre insan gibi yazıldı")
                time.sleep(1)

                try:
                    current_email_value = email_input.get_attribute("value")
                    current_password_value = password_input.get_attribute("value")
                    logger.info(f"Email alanı kontrolü: {current_email_value}")
                    logger.info(
                        f"Şifre alanı kontrolü: {'*' * len(current_password_value) if current_password_value else 'BOŞ!'}"
                    )

                    if not current_email_value:
                        logger.warning("Email alanı boş, insan gibi tekrar dolduruluyor...")
                        email_input.click()
                        time.sleep(0.3)
                        email_input.clear()
                        time.sleep(0.2)
                        for char in current_email:
                            email_input.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))
                        time.sleep(0.5)

                    if not current_password_value:
                        logger.warning("Şifre alanı boş, insan gibi tekrar dolduruluyor...")
                        password_input.click()
                        time.sleep(0.3)
                        password_input.clear()
                        time.sleep(0.2)
                        for char in password:
                            password_input.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))
                        time.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Alan kontrolü sırasında hata: {e}")

                checkboxes = [
                    "conditionOfMembershipApproved",
                    "marketingEmailsAuthorized",
                    "protectionOfPersonalDataApproved",
                ]

                for checkbox_id in checkboxes:
                    try:
                        try:
                            checkbox = self.trendyol_driver.find_element(By.ID, checkbox_id)
                            if not checkbox.is_selected():
                                label = self.trendyol_driver.find_element(
                                    By.CSS_SELECTOR, f"label[for='{checkbox_id}']"
                                )
                                self.trendyol_driver.execute_script(
                                    "arguments[0].click();", label
                                )
                                logger.info(f"Checkbox {checkbox_id}: Label'a tıklandı")
                            else:
                                logger.info(f"Checkbox {checkbox_id}: Zaten seçili")
                        except Exception as e1:
                            logger.warning(
                                f"Normal checkbox yöntemi başarısız ({checkbox_id}): {e1}"
                            )

                            checkbox_checked = self.trendyol_driver.execute_script(
                                """
                                var checkbox = document.getElementById(arguments[0]);
                                if (checkbox && !checkbox.checked) {
                                    checkbox.checked = true;
                                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                                    return 'checked';
                                }
                                return checkbox ? 'already_checked' : 'not_found';
                            """,
                                checkbox_id,
                            )
                            logger.info(
                                f"Checkbox {checkbox_id}: JavaScript sonucu: {checkbox_checked}"
                            )

                        time.sleep(0.5)

                    except Exception as e:
                        logger.warning(f"Checkbox işaretleme hatası ({checkbox_id}): {e}")

                time.sleep(1)

                for field_attempt in range(3):
                    final_email = email_input.get_attribute("value")
                    final_password = password_input.get_attribute("value")

                    logger.info(f"DENEME {field_attempt + 1} - Email: {final_email}")
                    logger.info(
                        f"DENEME {field_attempt + 1} - Şifre: {'Dolu' if final_password else 'BOŞ!'}"
                    )

                    fields_filled = True

                    if not final_email:
                        logger.warning(
                            f"DENEME {field_attempt + 1}: Email alanı boş, insan gibi yeniden dolduruluyor..."
                        )
                        email_input.click()
                        time.sleep(0.3)
                        email_input.clear()
                        time.sleep(0.2)
                        for char in current_email:
                            email_input.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))
                        fields_filled = False
                        time.sleep(0.5)

                    if not final_password:
                        logger.warning(
                            f"DENEME {field_attempt + 1}: Şifre alanı boş, insan gibi yeniden dolduruluyor..."
                        )
                        password_input.click()
                        time.sleep(0.3)
                        password_input.clear()
                        time.sleep(0.2)
                        for char in password:
                            password_input.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))
                        fields_filled = False
                        time.sleep(0.5)

                    if fields_filled:
                        logger.info(
                            f"DENEME {field_attempt + 1}: Tüm alanlar dolu, devam ediliyor"
                        )
                        break
                    else:
                        logger.warning(
                            f"DENEME {field_attempt + 1}: Alanlar yeniden dolduruldu, kontrol ediliyor..."
                        )
                        time.sleep(1)
                else:
                    logger.error("3 denemede de alanlar doldurulamıyor!")
                    return False, None, None

                logger.info("Üye ol butonunu arıyor...")
                register_btn = self.trendyol_wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )

                pre_click_email = email_input.get_attribute("value")
                pre_click_password = password_input.get_attribute("value")
                logger.info(f"BUTTON ÖNCESİ - Email: {pre_click_email}")
                logger.info(
                    f"BUTTON ÖNCESİ - Şifre: {'Dolu' if pre_click_password else 'BOŞ!'}"
                )

                if not pre_click_email:
                    logger.warning(
                        "SON UYARI: Email boş, button'dan önce son kez dolduruluyor!"
                    )
                    self.trendyol_driver.execute_script(
                        """
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    """,
                        email_input,
                        current_email,
                    )

                if not pre_click_password:
                    logger.warning(
                        "SON UYARI: Şifre boş, button'dan önce son kez dolduruluyor!"
                    )
                    self.trendyol_driver.execute_script(
                        """
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    """,
                        password_input,
                        password,
                    )

                time.sleep(1)
                logger.info("Üye ol butonuna tıklanıyor...")

                self.trendyol_driver.execute_script(
                    """
                    // Alan değerlerini sakla
                    var emailValue = arguments[1];
                    var passwordValue = arguments[2];

                    // Butona tıkla
                    arguments[0].click();

                    // Hemen ardından alanları tekrar kontrol et ve gerekirse doldur
                    setTimeout(function() {
                        var emailField = document.getElementById('email');
                        var passwordField = document.getElementById('password');

                        if (emailField && !emailField.value) {
                            emailField.value = emailValue;
                            emailField.dispatchEvent(new Event('input', { bubbles: true }));
                        }

                        if (passwordField && !passwordField.value) {
                            passwordField.value = passwordValue;
                            passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }, 100);
                """,
                    register_btn,
                    current_email,
                    password,
                )

                logger.info("Üye ol butonuna tıklandı!")
                time.sleep(2)

                post_click_email = email_input.get_attribute("value")
                post_click_password = password_input.get_attribute("value")
                logger.info(f"BUTTON SONRASI - Email: {post_click_email}")
                logger.info(
                    f"BUTTON SONRASI - Şifre: {'Dolu' if post_click_password else 'BOŞ!'}"
                )

                # Email hata kontrolü yap (5 saniye bekle)
                time.sleep(5)
                
                if self.check_email_error():
                    logger.warning(f"🚫 Email hatası tespit edildi: {current_email}")
                    
                    if attempt < max_email_attempts - 1:
                        # Email'i güncelle
                        current_email, current_username = self.increment_email_number(current_email)
                        logger.info(f"🔄 Yeni email ile deneme yapılacak: {current_email}")
                        
                        # Kısa bekleme ve devam et
                        time.sleep(3)
                        continue
                    else:
                        logger.error(f"❌ Maksimum email denemesi ({max_email_attempts}) aşıldı")
                        return False, None, None
                else:
                    logger.info(f"✅ Email başarılı, devam ediliyor: {current_email}")
                    # Başarılı kayıt, yeni email bilgilerini döndür
                    return True, current_email, current_username

            except Exception as e:
                logger.error(f"TrendyolGO kayıt denemesi {attempt + 1} hatası: {e}")
                if attempt < max_email_attempts - 1:
                    logger.info(f"Deneme {attempt + 1} başarısız, tekrar denenecek...")
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"Tüm email denemeleri başarısız oldu")
                    return False, None, None
        
        # Tüm denemeler başarısız
        logger.error(f"❌ {max_email_attempts} email denemesinin tümü başarısız")
        return False, None, None

    def verify_email_on_trendyol(self, verification_code):
        try:
            logger.info("Email doğrulama dialogu bekleniyor...")
            time.sleep(3)

            selectors = [
                "input[id=':r3:']",
                "input[placeholder=' ']",
                "div[role='dialog'] input",
                "input[id*=':r']",
                "input[type='text']:not([name])",
                "input[id*='verification'], input[id*='code']",
                "input.peer",
            ]

            code_input = None
            for selector in selectors:
                try:
                    code_input = self.trendyol_wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Doğrulama inputu bulundu: {selector}")
                    break
                except Exception:
                    continue

            if not code_input:
                logger.error("Doğrulama kodu input'u bulunamadı")
                return False

            time.sleep(3)

            try:
                self.trendyol_driver.execute_script(
                    """
                    // Tüm overlay ve modal elementleri gizle
                    var overlays = document.querySelectorAll('[id*="radix"], [class*="overlay"], [class*="modal"], h2[class*="title"]');
                    overlays.forEach(function(el) {
                        if (el && el.style) {
                            el.style.zIndex = '-1';
                            el.style.position = 'relative';
                        }
                    });

                    // Sayfayı yukarı kaydır
                    window.scrollTo(0, 0);
                """
                )
                time.sleep(1)
                logger.info("Overlay'ler temizlendi")
            except Exception as e:
                logger.warning(f"Overlay temizleme hatası: {e}")

            try:
                logger.info("Doğrulama kodu insan gibi yazılıyor...")

                self.trendyol_driver.execute_script(
                    """
                    // Dialog'un pozisyonunu sabitle
                    var dialog = document.querySelector('[role="dialog"]');
                    if (dialog) {
                        dialog.style.position = 'fixed';
                        dialog.style.top = '50%';
                        dialog.style.left = '50%';
                        dialog.style.transform = 'translate(-50%, -50%)';
                        dialog.style.zIndex = '9999';
                    }

                    // Input'a odaklan ama sayfayı kaydırma
                    arguments[0].focus();
                    arguments[0].value = '';
                """,
                    code_input,
                )
                time.sleep(0.5)

                for i, char in enumerate(verification_code):
                    code_input.send_keys(char)

                    typing_delay = random.uniform(0.08, 0.18)
                    time.sleep(typing_delay)

                    if i > 0 and i % 2 == 0:
                        pause_chance = random.random()
                        if pause_chance < 0.3:
                            time.sleep(random.uniform(0.1, 0.3))

                time.sleep(0.5)
                entered_value = code_input.get_attribute("value")
                logger.info(f"Doğrulama kodu insan gibi yazıldı: {verification_code}")
                logger.info(f"Girilen değer kontrolü: {entered_value}")

                if entered_value != verification_code:
                    logger.warning(
                        f"Kod uyuşmuyor! Beklenen: {verification_code}, Girilen: {entered_value}"
                    )

                    self.trendyol_driver.execute_script(
                        "arguments[0].value = '';", code_input
                    )
                    time.sleep(0.3)
                    for char in verification_code:
                        code_input.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.12))

            except Exception as e:
                logger.warning(f"JavaScript girişi başarısız, alternatif yöntem: {e}")

                try:

                    self.trendyol_driver.execute_script(
                        "arguments[0].value = '';", code_input
                    )
                    time.sleep(0.3)

                    for char in verification_code:
                        self.trendyol_driver.execute_script(
                            "arguments[0].value += arguments[1];", code_input, char
                        )
                        time.sleep(0.1)

                    self.trendyol_driver.execute_script(
                        """
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                        code_input,
                    )

                    logger.info(
                        f"Doğrulama kodu alternatif yöntemle girildi: {verification_code}"
                    )

                except Exception as e2:
                    logger.error(f"Tüm giriş yöntemleri başarısız: {e2}")
                    return False

            time.sleep(1)

            button_selectors = [
                "button.bg-primary[class*='title-3-bold']",
                "//button[contains(text(), 'Onayla')]",
                "button[class*='bg-primary'][class*='flex-1']",
                "div[role='dialog'] button:last-child",
                "button[type='submit']",
            ]

            confirm_btn = None
            for btn_selector in button_selectors:
                try:
                    if btn_selector.startswith("//"):
                        confirm_btn = self.trendyol_wait.until(
                            EC.element_to_be_clickable((By.XPATH, btn_selector))
                        )
                    else:
                        confirm_btn = self.trendyol_wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, btn_selector))
                        )
                    logger.info(f"Onayla butonu bulundu: {btn_selector}")
                    break
                except Exception:
                    continue

            if not confirm_btn:
                logger.error("Onayla butonu bulunamadı")
                return False

            try:
                self.trendyol_driver.execute_script(
                    "arguments[0].click();", confirm_btn
                )
                logger.info("Onayla butonuna tıklandı")
            except Exception as e:
                logger.warning(
                    f"JavaScript tıklama başarısız, normal tıklama deneniyor: {e}"
                )
                confirm_btn.click()

            time.sleep(3)

            return True

        except Exception as e:
            logger.error(f"Email doğrulama hatası: {e}")
            return False

    def fill_address_info(self, phone_number):
        try:
            logger.info("Adres bilgileri dolduruluyor...")

            time.sleep(3)
            
            # Çerez kabul etme butonunu kontrol et ve tıkla
            try:
                logger.info("Çerez kabul etme butonu aranıyor...")
                cookie_selectors = [
                    "//button[contains(text(), 'Kabul Et')]",
                    "//button[contains(text(), 'Kabul et')]", 
                    "//button[contains(text(), 'KABUL ET')]",
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'Onayla')]",
                    "button[id*='cookie'], button[class*='cookie']",
                    "button[class*='accept'], button[class*='approve']"
                ]
                
                cookie_btn = None
                for selector in cookie_selectors:
                    try:
                        if selector.startswith('//'):
                            cookie_btn = WebDriverWait(self.trendyol_driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            cookie_btn = WebDriverWait(self.trendyol_driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        logger.info(f"Çerez kabul butonu bulundu: {selector}")
                        break
                    except:
                        continue
                
                if cookie_btn:
                    self.trendyol_driver.execute_script("arguments[0].click();", cookie_btn)
                    logger.info("Çerez kabul butonuna tıklandı")
                    time.sleep(3)
                else:
                    logger.info("Çerez kabul butonu bulunamadı veya gerekli değil")
                    
            except Exception as e:
                logger.info(f"Çerez kontrolü atlandı: {e}")

            # Adres arama alanına 86043 insan gibi yaz
            logger.info("Adres arama alanına 86043 insan gibi yazılıyor...")
            
            # Çoklu selector ile adres input'unu bul
            address_selectors = [
                "input[placeholder*='Mahalle']",
                "input[placeholder*='sokak']", 
                "input[placeholder*='cadde']",
                "input[placeholder*='adres']",
                "input[placeholder*='konum']",
                "input[placeholder*='ara']",
                "input[type='text'][placeholder*='Ara']",
                "input[type='text'][placeholder*='ara']",
                "input[name*='address']",
                "input[name*='search']",
                "input[id*='address']",
                "input[id*='search']",
                "input[class*='address']",
                "input[class*='search']",
                "input[type='text']:not([name='name']):not([name='surname']):not([name='phone'])",
                "input[type='search']"
            ]
            
            address_input = None
            for selector in address_selectors:
                try:
                    logger.info(f"Adres input aranyor: {selector}")
                    address_input = WebDriverWait(self.trendyol_driver, 8).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Adres input bulundu: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Selector {selector} başarısız: {str(e)[:100]}...")
                    continue
            
            if not address_input:
                # Debug bilgisi - sayfanın mevcut durumunu kontrol et
                try:
                    current_url = self.trendyol_driver.current_url
                    logger.error(f"Mevcut sayfa URL: {current_url}")
                    
                    # Sayfadaki tüm input elementlerini listele
                    all_inputs = self.trendyol_driver.find_elements(By.TAG_NAME, "input")
                    logger.error(f"Sayfada toplam {len(all_inputs)} input elementi var:")
                    
                    for i, inp in enumerate(all_inputs[:10]):  # İlk 10 input'u göster
                        try:
                            placeholder = inp.get_attribute("placeholder") or "placeholder yok"
                            name = inp.get_attribute("name") or "name yok"
                            input_type = inp.get_attribute("type") or "type yok"
                            input_id = inp.get_attribute("id") or "id yok"
                            logger.error(f"Input {i+1}: placeholder='{placeholder}', name='{name}', type='{input_type}', id='{input_id}'")
                        except:
                            logger.error(f"Input {i+1}: bilgi alınamadı")
                            
                    # Sayfa screenshot'u al (opsiyonel)
                    try:
                        screenshot_path = f"adres_sayfa_hata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        self.trendyol_driver.save_screenshot(screenshot_path)
                        logger.error(f"Screenshot kaydedildi: {screenshot_path}")
                    except:
                        logger.warning("Screenshot alınamadı")
                        
                except Exception as debug_e:
                    logger.error(f"Debug bilgisi alınamadı: {debug_e}")
                    
                logger.error("Hiçbir adres input selector'ı çalışmadı")
                return False

            # İnsan gibi yazma - önce alanı temizle
            address_input.click()
            time.sleep(0.5)
            address_input.clear()
            time.sleep(0.3)
            
            # "86043" karakterlerini tek tek yaz (insan gibi)
            for char in "86043":
                address_input.send_keys(char)
                time.sleep(random.uniform(0.08, 0.18))  

            time.sleep(1)
            
            # Boşluk ekle (arama sonuçlarını tetiklemek için)
            address_input.send_keys(" ")
            time.sleep(2)
            
            # Enter tuşuna bas
            address_input.send_keys("\n")

            logger.info("86043 insan gibi yazıldı, boşluk eklendi ve Enter'a basıldı")
            
            # Arama sonuçlarının yüklenmesini bekle (API cevabı için daha uzun süre)
            logger.info("Arama sonuçları bekleniyor...")
            time.sleep(15)  # Artırıldı: 10'dan 15'e

            # Çoklu deneme ile 'Bu Konumu Kullan' butonunu ara
            max_button_attempts = 3
            use_location_btn = None
            
            for attempt in range(max_button_attempts):
                logger.info(f"'Bu Konumu Kullan' butonu aranıyor... Deneme {attempt + 1}/{max_button_attempts}")
                
                use_location_selectors = [
                    "//button[contains(text(), 'Bu Konumu Kullan')]",
                    "//button[contains(text(), 'Bu konumu kullan')]",
                    "//button[contains(text(), 'BU KONUMU KULLAN')]",
                    "//span[contains(text(), 'Bu Konumu Kullan')]/parent::button",
                    "//span[contains(text(), 'Bu konumu kullan')]/parent::button",
                    "//div[contains(text(), 'Bu Konumu Kullan')]/parent::button",
                    "//button[contains(@class, 'primary') and contains(text(), 'Kullan')]",
                    "//button[contains(@class, 'primary') and contains(text(), 'konum')]",
                    "button[type='submit']",
                    "button.bg-primary",
                    "button[class*='primary']",
                    "button[class*='btn-primary']",
                    "button[class*='submit']",
                    "input[type='submit']",
                    "div[role='button'][class*='primary']",
                    "[data-testid*='location'], [data-testid*='submit']",
                    "button:contains('Kullan')",
                    "button:contains('Onayla')",
                    "button:contains('Devam')"
                ]
    
                for selector in use_location_selectors:
                    try:
                        wait_time = 8 if attempt == 0 else 12  # İlk denemede 8sn, sonra 12sn
                        if selector.startswith("//"):
                            use_location_btn = WebDriverWait(self.trendyol_driver, wait_time).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            use_location_btn = WebDriverWait(self.trendyol_driver, wait_time).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        logger.info(f"'Bu Konumu Kullan' butonu bulundu: {selector}")
                        break
                    except Exception as e:
                        logger.warning(f"Selector {selector} başarısız: {str(e)[:50]}...")
                        continue
                
                if use_location_btn:
                    break
                    
                # Eğer buton bulunamadıysa, sayfa yenileme ve tekrar arama yap
                if attempt < max_button_attempts - 1:
                    logger.warning(f"Deneme {attempt + 1} başarısız, sayfa yenileniyor ve tekrar arama yapılıyor...")
                    self.trendyol_driver.refresh()
                    time.sleep(5)
                    
                    # Adres alanını tekrar bul ve 86043'u yaz
                    try:
                        address_input = None
                        for selector in address_selectors:
                            try:
                                address_input = WebDriverWait(self.trendyol_driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                                break
                            except:
                                continue
                                
                        if address_input:
                            address_input.click()
                            time.sleep(0.5)
                            address_input.clear()
                            address_input.send_keys("86043 ")
                            address_input.send_keys("\n")
                            logger.info("Sayfa yenilendi, 86043 tekrar yazıldı")
                            time.sleep(15)
                        else:
                            logger.warning("Sayfa yeniledikten sonra adres alanı bulunamadı")
                            
                    except Exception as refresh_e:
                        logger.warning(f"Sayfa yenileme sonrası arama hatası: {refresh_e}")

            if not use_location_btn:
                # Debug bilgisi - sayfadaki tüm butonları listele
                try:
                    logger.error("'Bu Konumu Kullan' butonu tüm denemelerde bulunamadı")
                    logger.error("Debug bilgisi - Sayfadaki butonlar:")
                    
                    all_buttons = self.trendyol_driver.find_elements(By.TAG_NAME, "button")
                    for i, btn in enumerate(all_buttons[:10]):  # İlk 10 butonu göster
                        try:
                            btn_text = btn.text or "metin yok"
                            btn_class = btn.get_attribute("class") or "class yok"
                            btn_type = btn.get_attribute("type") or "type yok"
                            btn_id = btn.get_attribute("id") or "id yok"
                            logger.error(f"Buton {i+1}: text='{btn_text}', class='{btn_class[:50]}', type='{btn_type}', id='{btn_id}'")
                        except:
                            logger.error(f"Buton {i+1}: bilgi alınamadı")
                    
                    # Sayfanın mevcut durumunu kontrol et
                    current_url = self.trendyol_driver.current_url
                    page_title = self.trendyol_driver.title
                    logger.error(f"Mevcut sayfa URL: {current_url}")
                    logger.error(f"Sayfa başlığı: {page_title}")
                    
                    # Son çare: herhangi bir tıklanabilir primary buton ara
                    logger.info("Son çare: herhangi bir primary buton aranıyor...")
                    fallback_selectors = [
                        "button.bg-primary:first-of-type",
                        "button[class*='primary']:first-of-type", 
                        "div[role='button'][class*='primary']:first-of-type",
                        "button[type='submit']:first-of-type",
                        "input[type='submit']:first-of-type",
                        "*[onclick*='submit'], *[onclick*='continue'], *[onclick*='next']"
                    ]
                    
                    for selector in fallback_selectors:
                        try:
                            fallback_btn = WebDriverWait(self.trendyol_driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            logger.info(f"Son çare buton bulundu: {selector}")
                            use_location_btn = fallback_btn
                            break
                        except:
                            continue
                    
                    if not use_location_btn:
                        # Screenshot al
                        try:
                            screenshot_path = f"buton_hata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            self.trendyol_driver.save_screenshot(screenshot_path)
                            logger.error(f"Screenshot kaydedildi: {screenshot_path}")
                        except:
                            logger.warning("Screenshot alınamadı")
                            
                        return False
                        
                except Exception as debug_e:
                    logger.error(f"Debug bilgisi hatası: {debug_e}")
                    return False

            self.trendyol_driver.execute_script(
                "arguments[0].click();", use_location_btn
            )
            logger.info("'Bu Konumu Kullan' butonuna tıklandı")
            time.sleep(3)

            logger.info("Form alanları insan gibi dolduruluyor...")
            
            # Helper fonksiyonlar
            def find_form_field(field_name, primary_selectors, fallback_selectors=None):
                """Form alanını birden çok selector ile bulmaya çalışan helper"""
                all_selectors = primary_selectors + (fallback_selectors or [])
                
                for selector in all_selectors:
                    try:
                        element = WebDriverWait(self.trendyol_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR if not selector.startswith('//') else By.XPATH, selector))
                        )
                        logger.info(f"{field_name} alanı bulundu: {selector}")
                        return element
                    except:
                        continue
                        
                logger.warning(f"{field_name} alanı hiçbir selector ile bulunamadı")
                return None
                        
            def human_type_field(field_element, text, field_name):
                """Alanı insan gibi doldur"""
                try:
                    field_element.click()
                    time.sleep(0.3)
                    field_element.clear()
                    time.sleep(0.2)
                    for char in text:
                        field_element.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    logger.info(f"{field_name}: {text} insan gibi yazıldı")
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    logger.warning(f"{field_name} doldurma hatası: {e}")
                    return False

            # Form alanlarını doldur - geliştirilmiş selector'larla
            
            # Bina No
            bina_no_input = find_form_field(
                "Bina No", 
                ["input[name='apartmentNumber']"],
                ["input[placeholder*='bina']", "input[placeholder*='apartman']", "input[id*='apartment']", "input[id*='building']"]
            )
            if bina_no_input:
                human_type_field(bina_no_input, "0", "Bina No")
                
            # Kat
            floor_input = find_form_field(
                "Kat",
                ["input[name='floor']"], 
                ["input[placeholder*='kat']", "input[id*='floor']"]
            )
            if floor_input:
                human_type_field(floor_input, "0", "Kat")
                
            # Kapı No
            door_input = find_form_field(
                "Kapı No",
                ["input[name='doorNumber']"],
                ["input[placeholder*='kapı']", "input[placeholder*='door']", "input[id*='door']"]
            )
            if door_input:
                human_type_field(door_input, "0", "Kapı No")
                
            # Adres Adı
            address_name_input = find_form_field(
                "Adres Adı",
                ["input[name='addressName']"],
                ["input[placeholder*='adres ad']", "input[placeholder*='başlık']", "input[id*='addressName']", "input[id*='title']"]
            )
            if address_name_input:
                human_type_field(address_name_input, "evim", "Adres Adı")
                
            # İsim  
            name_input = find_form_field(
                "İsim",
                ["input[name='name']"],
                ["input[placeholder*='ad']", "input[placeholder*='ısim']", "input[id*='name']", "input[id*='firstName']"]
            )
            if name_input:
                human_type_field(name_input, "Murat", "İsim")
                
            # Soyisim
            surname_input = find_form_field(
                "Soyisim",
                ["input[name='surname']"],
                ["input[placeholder*='soyad']", "input[placeholder*='soyisim']", "input[id*='surname']", "input[id*='lastName']"]
            )
            if surname_input:
                human_type_field(surname_input, "Can", "Soyisim")
                
            # Telefon numarası
            phone_input = find_form_field(
                "Telefon",
                ["input[name='phone']"],
                ["input[placeholder*='telefon']", "input[placeholder*='phone']", "input[id*='phone']", "input[type='tel']"]
            )
            if phone_input:
                # Türkiye formatına dönüştür (+90 kaldır)
                clean_phone = phone_number.replace("+90", "").replace("+", "")
                human_type_field(phone_input, clean_phone, "Telefon")

            time.sleep(2)

            # Kaydet butonu - geliştirilmiş selector'lar
            logger.info("'Kaydet' butonu aranıyor...")
            save_selectors = [
                "//button[contains(text(), 'Kaydet')]",
                "//button[contains(text(), 'KAYDET')]",
                "//button[contains(text(), 'kaydet')]",
                "//button[contains(text(), 'Save')]",
                "//button[contains(text(), 'Onayla')]",
                "//button[contains(text(), 'Devam')]",
                "button[form='address-form']",
                "button[type='submit'].bg-primary",
                "button[type='submit']",
                "button.bg-primary",
                "button[class*='primary']",
                "button[class*='save']",
                "button[class*='submit']",
                "input[type='submit']",
                "form button:last-child",
                "div:last-child button"
            ]

            save_btn = None
            for selector in save_selectors:
                try:
                    logger.info(f"Kaydet butonu deneniyor: {selector}")
                    if selector.startswith('//'):
                        save_btn = WebDriverWait(self.trendyol_driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        save_btn = WebDriverWait(self.trendyol_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    logger.info(f"'Kaydet' butonu bulundu: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Kaydet selector {selector} başarısız: {str(e)[:50]}...")
                    continue

            if not save_btn:
                logger.error("'Kaydet' butonu hiçbir selector ile bulunamadı")
                return False

            # Kaydet butonuna tıkla
            self.trendyol_driver.execute_script("arguments[0].click();", save_btn)
            logger.info("'Kaydet' butonuna tıklandı")
            time.sleep(3)

            logger.info("Adres bilgileri başarıyla dolduruldu")
            return True

        except Exception as e:
            logger.error(f"Adres bilgileri doldurma hatası: {e}")
            import traceback

            logger.error(f"Hata detayları: {traceback.format_exc()}")
            return False

    def verify_phone_on_trendyol(self, sms_code):
        try:
            logger.info("Telefon doğrulama dialogu bekleniyor...")
            time.sleep(3)

            sms_input = self.trendyol_wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='number']"))
            )
            sms_input.clear()
            sms_input.send_keys(sms_code)
            time.sleep(1)

            confirm_btn = self.trendyol_wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@type='submit' and contains(text(), 'Onayla')]",
                    )
                )
            )
            self.trendyol_driver.execute_script("arguments[0].click();", confirm_btn)
            time.sleep(3)

            return True

        except Exception as e:
            logger.error(f"Telefon doğrulama hatası: {e}")
            return False

    def create_single_account(
        self, prefix, domain, password, pid, account_number, is_first_account=False
    ):
        try:

            self.ensure_emailfake_session()

            self.stats["total_attempts"] += 1
            username = f"{prefix}{account_number}"
            logger.info(f"\n=== Hesap {account_number} oluşturuluyor: {username} ===")

            # Her hesap için EmailFake tarayıcısını tamamen kapat ve yeniden aç (stale element sorununu çözmek için)
            try:
                logger.info("🔄 EmailFake tarayıcısı tamamen yenileniyor (stale element fix)...")
                if self.emailfake_driver:
                    self.emailfake_driver.quit()
                    self.emailfake_driver = None
                time.sleep(3)
                self.setup_emailfake_driver()  
                time.sleep(3)
                logger.info("✅ EmailFake tarayıcısı başarıyla yenilendi")
            except Exception as e:
                logger.warning(f"EmailFake tarayıcı yenileme hatası: {e}")
                # Hata durumunda yine de devam et
            
            # EmailFake'ı hazırla ve email oluştur
            logger.info(f"EmailFake domain ayarlanıyor: {domain}")
            if not self.setup_emailfake_initial(domain):
                logger.error("EmailFake hazırlanamadı")
                return None
            
            # Username ile email oluştur
            email = self.create_email_with_username(username)

            if not email:
                logger.error("Email oluşturulamadı")
                return None

            phone_number = None
            for phone_attempt in range(3):
                phone_number = self.get_phone_number(pid)
                if phone_number:
                    break
                logger.warning(
                    f"Telefon numarası alınamadı, deneme {phone_attempt + 1}/3"
                )
                time.sleep(30)

            if not phone_number:
                logger.error("Telefon numarası alınamadı")
                return None

            # Trendyol'a kayıt ol (email hata kontrolü ile)
            registration_result = self.register_on_trendyol(email, password)
            
            # Sonuçları kontrol et
            if isinstance(registration_result, tuple):
                success, final_email, final_username = registration_result
                if not success:
                    logger.error("Trendyol kayıt başarısız")
                    self.release_phone_number(phone_number, pid)
                    
                    # Trendyol tarayıcısını kapat
                    try:
                        if self.trendyol_driver:
                            self.trendyol_driver.quit()
                            self.trendyol_driver = None
                            logger.info("Trendyol kayıt hatası nedeniyle TrendyolGO tarayıcısı kapatıldı")
                    except Exception as e:
                        logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                    
                    # 300-310 saniye bekle
                    wait_time = random.randint(300, 310)
                    logger.info(f"⏱️ Trendyol kayıt hatası nedeniyle {wait_time} saniye bekleniyor...")
                    time.sleep(wait_time)
                    return None
                else:
                    # Email değişti mi kontrol et
                    if final_email != email:
                        logger.info(f"🔄 Email güncellendi: {email} -> {final_email}")
                        
                        # EmailFake'te yeni email oluştur
                        logger.info(f"EmailFake'te yeni email oluşturuluyor: {final_username}")
                        
                        # EmailFake tarayıcısını yenile
                        try:
                            logger.info("🔄 EmailFake tarayıcısı yeniden başlatılıyor (email değişikliği için)...")
                            if self.emailfake_driver:
                                self.emailfake_driver.quit()
                                self.emailfake_driver = None
                            time.sleep(3)
                            self.setup_emailfake_driver()  
                            time.sleep(3)
                            
                            # Domain ayarla ve yeni email oluştur
                            if not self.setup_emailfake_initial(domain):
                                logger.error("EmailFake yeniden hazırlanamadı")
                                # Email değişse bile devam etmeye çalış
                            else:
                                new_email = self.create_email_with_username(final_username)
                                if new_email:
                                    email = new_email  # Güncellenen email'i kullan
                                    logger.info(f"✅ EmailFake'te yeni email oluşturuldu: {email}")
                                else:
                                    logger.warning("EmailFake'te yeni email oluşturulamadı, eski email ile devam ediliyor")
                                    email = final_email  # En azından güncellenen email'i kullan
                        except Exception as e:
                            logger.warning(f"EmailFake yenileme hatası: {e}")
                            email = final_email  # En azından güncellenen email'i kullan
                    else:
                        email = final_email  # Aynı email
            else:
                # Eski format uyumluluğu (sadece boolean döndürürse)
                if not registration_result:
                    logger.error("Trendyol kayıt başarısız (eski format)")
                    self.release_phone_number(phone_number, pid)
                    
                    # Trendyol tarayıcısını kapat
                    try:
                        if self.trendyol_driver:
                            self.trendyol_driver.quit()
                            self.trendyol_driver = None
                            logger.info("Trendyol kayıt hatası nedeniyle TrendyolGO tarayıcısı kapatıldı")
                    except Exception as e:
                        logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                    
                    # 300-310 saniye bekle
                    wait_time = random.randint(300, 310)
                    logger.info(f"⏱️ Trendyol kayıt hatası nedeniyle {wait_time} saniye bekleniyor...")
                    time.sleep(wait_time)
                    return None

            verification_code = self.get_verification_code_from_email()

            if not verification_code:
                logger.error("Email doğrulama kodu alınamadı")
                self.release_phone_number(phone_number, pid)
                
                # Trendyol tarayıcısını kapat
                try:
                    if self.trendyol_driver:
                        self.trendyol_driver.quit()
                        self.trendyol_driver = None
                        logger.info("Email kod alamama nedeniyle TrendyolGO tarayıcısı kapatıldı")
                except Exception as e:
                    logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                
                # 300-310 saniye bekle
                wait_time = random.randint(300, 310)
                logger.info(f"⏱️ Email kod alamama nedeniyle {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                return None

            if not self.verify_email_on_trendyol(verification_code):
                logger.error("Email doğrulama başarısız")
                self.release_phone_number(phone_number, pid)
                
                # Trendyol tarayıcısını kapat
                try:
                    if self.trendyol_driver:
                        self.trendyol_driver.quit()
                        self.trendyol_driver = None
                        logger.info("Email doğrulama hatası nedeniyle TrendyolGO tarayıcısı kapatıldı")
                except Exception as e:
                    logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                
                # 300-310 saniye bekle
                wait_time = random.randint(300, 310)
                logger.info(f"⏱️ Email doğrulama hatası nedeniyle {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                return None

            if not self.fill_address_info(phone_number):
                logger.error("Adres bilgileri doldurma başarısız")
                self.release_phone_number(phone_number, pid)
                
                # Trendyol tarayıcısını kapat
                try:
                    if self.trendyol_driver:
                        self.trendyol_driver.quit()
                        self.trendyol_driver = None
                        logger.info("Adres doldurma hatası nedeniyle TrendyolGO tarayıcısı kapatıldı")
                except Exception as e:
                    logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                
                # 300-310 saniye bekle
                wait_time = random.randint(300, 310)
                logger.info(f"⏱️ Adres doldurma hatası nedeniyle {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                return None

            sms_code = self.get_sms_code(phone_number, pid)
            if not sms_code:
                logger.error("SMS kodu alınamadı, yeni numara deneniyor...")
                self.release_phone_number(phone_number, pid)
                
                # Trendyol tarayıcısını kapat
                try:
                    if self.trendyol_driver:
                        self.trendyol_driver.quit()
                        self.trendyol_driver = None
                        logger.info("SMS alamama nedeniyle TrendyolGO tarayıcısı kapatıldı")
                except Exception as e:
                    logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                
                # 300-310 saniye bekle
                wait_time = random.randint(300, 310)
                logger.info(f"⏱️ SMS alamama nedeniyle {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)

                return self.create_single_account(
                    prefix,
                    domain,
                    password,
                    pid,
                    account_number,
                    is_first_account=False,
                )

            if not self.verify_phone_on_trendyol(sms_code):
                logger.error("Telefon doğrulama başarısız")
                self.release_phone_number(phone_number, pid)
                
                # Trendyol tarayıcısını kapat
                try:
                    if self.trendyol_driver:
                        self.trendyol_driver.quit()
                        self.trendyol_driver = None
                        logger.info("Telefon doğrulama hatası nedeniyle TrendyolGO tarayıcısı kapatıldı")
                except Exception as e:
                    logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")
                
                # 300-310 saniye bekle
                wait_time = random.randint(300, 310)
                logger.info(f"⏱️ Telefon doğrulama hatası nedeniyle {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                return None

            self.release_phone_number(phone_number, pid)

            try:
                if self.trendyol_driver:
                    self.trendyol_driver.quit()
                    self.trendyol_driver = None
                    logger.info("TrendyolGO tarayıcısı kapatıldı")
            except Exception as e:
                logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")

            self.stats["success_count"] += 1
            logger.info(f"✅ Hesap başarıyla oluşturuldu: {email}")
            
            # Hesabı anlık olarak kaydet
            account_info = f"{email}:{password}"
            self.save_account_instantly(account_info)

            return account_info

        except Exception as e:
            logger.error(f"Hesap oluşturma hatası: {e}")

            try:

                if self.trendyol_driver:
                    self.trendyol_driver.quit()
                    self.trendyol_driver = None
                    logger.info("Temizlik: TrendyolGO tarayıcısı kapatıldı")

                if "phone_number" in locals() and phone_number:
                    self.release_phone_number(phone_number, pid)
            except Exception as cleanup_error:
                logger.warning(f"Temizlik sırasında hata: {cleanup_error}")

            self.stats["failed_count"] += 1
            return None

    def create_multiple_accounts(self, prefix, domain, password, pid, count):
        created_accounts = []

        logger.info(f"\n🚀 {count} adet hesap oluşturma işlemi başlıyor...")
        logger.info(f"Önek: {prefix}")
        logger.info(f"Domain: {domain}")
        logger.info(f"PID: {pid}")

        for i in range(1, count + 1):
            try:
                logger.info(f"\n--- {i}/{count} hesap oluşturuluyor ---")

                is_first = i == 1
                account = self.create_single_account(
                    prefix, domain, password, pid, i, is_first_account=is_first
                )

                if account:
                    created_accounts.append(account)
                    logger.info(f"✅ Başarılı: {len(created_accounts)}/{count}")
                else:
                    logger.error(f"❌ Hesap {i} oluşturulamadı")

                if i < count:
                    time.sleep(random.randint(300, 310))

            except KeyboardInterrupt:
                logger.info("\n⚠️  İşlem kullanıcı tarafından durduruldu")
                break
            except Exception as e:
                logger.error(f"Genel hata: {e}")
                continue

        return created_accounts

    def save_account_instantly(self, account):

        try:
            with open(self.instant_save_file, "a", encoding="utf-8") as f:
                f.write(f"{account}\n")
            logger.info(f"💾 Hesap anlık kaydedildi: {account}")
            return True
        except Exception as e:
            logger.error(f"Anlık kaydetme hatası: {e}")
            return False

    def save_accounts_to_file(self, accounts, filename="trendyol_accounts.txt"):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trendyol_accounts_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                for account in accounts:
                    f.write(f"{account}\n")

            logger.info(f"📁 {len(accounts)} hesap {filename} dosyasına kaydedildi")
            return filename

        except Exception as e:
            logger.error(f"Dosya kaydetme hatası: {e}")
            return None

    def close(self):
        try:
            if self.emailfake_driver:
                self.emailfake_driver.quit()
                logger.info("🔒 EmailFake tarayıcısı kapatıldı")
        except Exception as e:
            logger.warning(f"EmailFake tarayıcısı kapama hatası: {e}")

        try:
            if self.trendyol_driver:
                self.trendyol_driver.quit()
                logger.info("🔒 TrendyolGO tarayıcısı kapatıldı")
        except Exception as e:
            logger.warning(f"TrendyolGO tarayıcısı kapama hatası: {e}")

        logger.info("🔒 Bot başarıyla kapatıldı")


def main():
    print("🤖 TrendyolGO Otomatik Hesap Oluşturucu")
    print("=" * 50)

    try:
        prefix = input("📧 Email öneki girin (örn: mehmet): ").strip()
        if not prefix:
            print("❌ Email öneki gereklidir!")
            return

        domain = input("🌐 Domain girin (örn: boranora.com): ").strip()
        if not domain:
            print("❌ Domain gereklidir!")
            return

        password = input("🔐 Şifre girin: ").strip()
        if not password:
            print("❌ Şifre gereklidir!")
            return

        pid = input("📱 PID değerini girin: ").strip()
        if not pid:
            print("❌ PID değeri gereklidir!")
            return

        count = int(input("📊 Kaç adet hesap oluşturmak istiyorsunuz: ").strip())
        if count <= 0:
            print("❌ Hesap sayısı 1'den büyük olmalıdır!")
            return

    except ValueError:
        print("❌ Geçersiz hesap sayısı!")
        return
    except KeyboardInterrupt:
        print("\n⚠️  İşlem iptal edildi")
        return

    bot = None
    try:
        print("\n🔄 Bot başlatılıyor...")
        bot = TrendyolAccountBot()

        accounts = bot.create_multiple_accounts(prefix, domain, password, pid, count)

        print(f"\n📊 İşlem Tamamlandı!")
        print(f"✅ Başarılı: {bot.stats['success_count']}")
        print(f"❌ Başarısız: {bot.stats['failed_count']}")
        print(f"📈 Toplam: {bot.stats['total_attempts']}")
        
        # Anlık kaydetme dosyasını göster
        if bot.stats['success_count'] > 0:
            print(f"💾 Anlık kaydetme dosyası: {bot.instant_save_file}")

        if accounts:
            filename = bot.save_accounts_to_file(accounts)
            if filename:
                print(f"📁 Hesaplar {filename} dosyasına kaydedildi")
                print("\n✨ Oluşturulan Hesaplar:")
                for account in accounts:
                    print(f"  📧 {account}")
        else:
            print("❌ Hiçbir hesap oluşturulamadı")

    except KeyboardInterrupt:
        print("\n⚠️  İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Ana program hatası: {e}")
        print(f"❌ Hata: {e}")
    finally:
        if bot:
            bot.close()


if __name__ == "__main__":
    main()
