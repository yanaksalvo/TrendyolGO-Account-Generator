# TrendyolGO-Account-Generator

Bu proje, TrendyolGO hesap oluşturma işlemini otomatikleştirmek için geliştirilmiştir. **Önemli Not:** Bu projede hiçbir şekilde illegal veya yasadışı işlem bulunmamaktadır. Tüm işlemler usulüne uygun şekilde gerçekleştirilmiştir.

## Kurulum ve Kullanım Talimatları

### 1. Python Kurulumu
- Bilgisayarınızda Python yüklü olmalıdır. Projenin düzgün çalışması için uygun bir Python sürümüne sahip olduğunuzdan emin olun (önerilen: Python 3.8 veya üstü).
- Python'u resmi web sitesinden indirebilirsiniz: [Python İndirme](https://www.python.org/downloads/)
- Python'un yüklü olup olmadığını kontrol etmek için terminalde şu komutu çalıştırabilirsiniz:
  ```
  python --version
  ```

### 2. ChromeDriver Kurulumu
- Projenin çalışması için uygun bir **ChromeDriver** sürümüne ihtiyacınız var. Bilgisayarınızın işletim sistemine ve Chrome tarayıcı sürümüne uygun ChromeDriver'ı şu adresten indirebilirsiniz: [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
- Hata almamak için proje klasöründe bulunan `chromedriver.exe` dosyasını kullanabilirsiniz. Ancak, Chrome tarayıcınızın sürümüyle uyumlu olduğundan emin olun.
- İndirdiğiniz ChromeDriver dosyasını proje klasörüne yerleştirin veya sistem PATH'ine ekleyin.

### 3. Gerekli Modüllerin Yüklenmesi
- Proje için gerekli Python modüllerini yüklemek için terminali açın ve proje klasöründe şu komutu çalıştırın:
  ```
  pip install -r requirements.txt
  ```
- Bu komut, projede kullanılan tüm bağımlılıkları otomatik olarak yükleyecektir.

### 4. SMS Aktivasyonu için API Ayarları
- SMS aktivasyonu için [durianrcs.com](https://durianrcs.com) sitesine kayıt olmanız gerekmektedir.
- Kayıt olduktan sonra, siteden aldığınız **API Key** ve **Username** bilgilerini proje dosyasındaki `trendyolgo.py` dosyasının **32. ve 33. satırlarına** ekleyin.
  ```python
  api_key = "YOUR_API_KEY"
  username = "YOUR_USERNAME"
  ```

### 5. Çalıştırma
- Tüm ayarları yaptıktan sonra, proje klasöründe aşağıdaki komutu çalıştırarak script'i başlatın:
  ```
  python trendyolgo.py
  ```
- Script çalışırken herhangi bir müdahalede bulunmayın. Script, aşağıdaki işlemleri otomatik olarak gerçekleştirecektir:
  - E-posta oluşturulması
  - Çerezlerin (cookies) çekilmesi
  - SMS aktivasyonu
  - Trendyol hesabının oluşturulması

### Notlar
- **Posta Kodu:** Trendyol için posta kodu bilgisini gerektiğinde güncelleyebilirsiniz.
- Herhangi bir hata ile karşılaşırsanız, ChromeDriver sürümünün tarayıcınızla uyumlu olduğundan ve tüm modüllerin doğru şekilde yüklendiğinden emin olun.

## İletişim
- Herhangi bir soru veya destek talebi için Telegram üzerinden iletişime geçebilirsiniz: [Telegram @babakonusmazgosterirhepicraat](https://t.me/babakonusmazgosterirhepicraat)

## Lisans
Bu proje [MIT Lisansı](https://opensource.org/licenses/MIT) altında lisanslanmıştır.

## Uyarı
- Bu proje yalnızca eğitim amaçlı geliştirilmiştir ve yasalara uygun şekilde kullanılmalıdır.
- Herhangi bir sorunla karşılaşırsanız, lütfen proje dokümantasyonunu kontrol edin veya destek için iletişime geçin.
