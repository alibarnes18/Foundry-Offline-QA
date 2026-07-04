# Bir Aylık Proje Planı: Microsoft Foundry Local ile Yerel RAG AI Asistanı

**Kaynak:** [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)

> **Not (Azure $100 kredi):** Bu projenin çekirdek mimarisi tamamen yerel (cihaz üzerinde) çalışır — Foundry Local internet bağlantısı gerektirmeden CPU/NPU üzerinde model çalıştırır, bu yüzden $100'lık Azure kredisinin **zorunlu bir maliyeti yoktur**. Krediyi şu opsiyonel yerlerde değerlendirebilirsin: (1) bulutta paylaşımlı bir geliştirme/test VM'i (Azure VM, B2s/B2ms gibi düşük maliyetli bir seri), (2) öğrenci ekiplerinin demo günü için ortak bir App Service / Static Web App üzerinde web arayüzü barındırması, (3) GitHub Actions yerine Azure DevOps/Container Registry ile CI-CD denemesi, (4) ileri seviye öğrenciler için Azure AI Foundry (bulut) ile yerel modelin karşılaştırılması (isteğe bağlı "bulut vs. yerel" karşılaştırma haftası). Aşağıdaki plan, kredi kullanımı için bu opsiyonel eklerle işaretlenmiştir.

---

## Yönetici Özeti

| Faz | Süre | İçerik |
|---|---|---|
| **Faz 1: Temeller** | Hafta 1–2 | RAG temelleri, Foundry Local kurulumu (Windows & macOS), embedding, vektör arama, SQLite, prompt tasarımı |
| **Faz 2: Proje Geliştirme** | Hafta 3–4 | Yerel Q&A asistanının kodlanması: doküman alma (ingestion), retrieval pipeline, Foundry Local üzerinden yerel LLM entegrasyonu |
| **Faz 3: Test & Kapanış** | Hafta 5–6 | Fonksiyonel ve değerlendirme testleri, kapsamlı dokümantasyon, final demo/sunum |

**Amaç:** Bilgisayar mühendisliği alanında yeni başlayan öğrencileri, Microsoft Foundry Local kullanarak çevrimdışı model çıkarımı (offline inference) ve RAG (Retrieval-Augmented Generation) deseniyle yerel bir Q&A/bilgi asistanı inşa ettikleri tam zamanlı, bir aylık bir yaz programında yönlendirmek. Proje, internet bağımlılığı olmadan dokümanlardan soru yanıtlayan yerel bir RAG destek ajanının Microsoft Tech Community örneğinden ilham almaktadır. Programın sonunda her öğrenci takımı, küçük bir doküman koleksiyonu (ör. ders notları, kılavuzlar, SSS) hakkında soruları yerel olarak bilgi alıp büyük dil modeline entegre ederek yanıtlayan, çalışan bir çevrimdışı Q&A chatbot'a sahip olacak.

---

## Proje Genel Bakış & Anahtar Teknolojiler

- **Proje Amacı:** Öğrencinin bilgisayarında tamamen çalışan basit bir chatbot — yerel bir doküman bilgi tabanından ilgili içeriği alıp yerel bir LLM'e besleyerek soruları yanıtlayan, RAG (Retrieval-Augmented Generation) kullanan bir yerel doküman Q&A asistanı. Bu, daha az halüsinasyon ve daha kaynak temelli, doğru yanıtlar sağlar. Asistan, cihaz üzerinde LLM çalışma zamanı sağlayan Microsoft Foundry Local sayesinde tamamen çevrimdışı çalışabilir.

- **Foundry Local nedir?** Büyük dil modellerini kullanıcının cihazında tamamen çalıştırmak için hafif bir çalışma zamanı (runtime) ve SDK sağlayan, optimize edilmiş model kataloğuna sahip uçtan uca bir yerel AI çözümü. Bulut hesabı veya GPU gerekmez — Foundry Local modelleri otomatik indirir/yönetir ve CPU/NPU hızlandırmasıyla çıkarım (inference) yapar, böylece uygulamalar sıfır ağ çağrısıyla yerel, çevrimdışı AI sunabilir.

- **RAG (Retrieval-Augmented Generation):** Bir doküman setinden ilgili bilgiyi **Retrieve** (alma), bu bilgiyle modelin girdi promptunu **Augment** (zenginleştirme), ardından modele yanıtı **Generate** (üretme) yaptırma deseni. Modelin yanıtları böylece kendi verinize dayalı (halüsinasyonu azaltıp kaynak atfı sağlayarak) hale gelir; bu, embedding tabanlı anlamsal arama ile LLM'i birleştirerek yapılır.

- **Embeddings & Vektör Arama:** Metin embedding'leri (anlamı sayısal vektörlerle temsil etme) ve bunları anlamsal benzerlik araması için kullanma. RAG genellikle dokümanları vektörlere çeviren bir embedding modeline dayanır; sorgular da embed edilip vektör benzerliği ölçülerek ilgili dokümanlarla eşleştirilir.

- **Yerel Veri için SQLite:** Doküman metinlerini ve embedding'lerini saklamak için hafif bir yerel veritabanı olarak SQLite kullanılır. SQLite sunucusuz, kendi kendine yeten (tek dosya) bir SQL veritabanıdır ve dünyada en yaygın kullanılan veritabanı motorudur.

- **Prompt Mühendisliği:** Etkili LLM promptları yazmak (özellikle rol talimatları için sistem promptları ve sorgular için kullanıcı promptları) etkili yanıtlar için hayati önem taşır. Modele kaynak belirtme ve emin değilse yanıt vermeme talimatı verme gibi temel teknikler işlenecektir.

- **Proje Mimarisi:** Final uygulama, tüm bileşenleri tek makinede barındıran basit bir mimariye sahip olacak: bir istemci arayüzü (basit bir web UI veya konsol girişi), kullanıcı sorgularını işleyip retrieval & generation'ı orkestre eden bir sunucu/pipeline katmanı, doküman embedding'lerini saklayan bir veri katmanı (SQLite) ve cihaz üzerinde çıkarım yapan bir AI katmanı (Foundry Local LLM).

---

## Proje Dosya Yapısı

Aşağıdaki klasör/dosya yapısı, Hafta 1'de iskelet proje olarak oluşturulur ve Faz 2 boyunca doldurulur. Her takım kendi kopyasını bu şablona göre düzenler.

```
yerel-rag-asistani/
│
├── main.py                  # Giriş noktası — CLI menüsü veya UI başlatıcı
├── requirements.txt         # Bağımlılık listesi (foundry-local-sdk, vb.)
├── .env                     # (opsiyonel) model adı gibi ayarlar; API anahtarı GEREKMEZ
├── README.md                # Faz 3'te doldurulacak proje raporu
│
├── data/
│   ├── raw/                 # Ham kaynak dokümanlar (.txt, .md, .pdf)
│   │   ├── ders_notu_1.txt
│   │   ├── sss.md
│   │   └── kilavuz.pdf
│   └── processed/           # (opsiyonel) chunk'lara bölünmüş ara çıktılar
│
├── db/
│   └── knowledge.db         # SQLite veritabanı (doküman metni + embedding vektörleri)
│
├── src/
│   ├── ingest.py            # Doküman okuma → chunk'lama → embedding → SQLite'a yazma
│   ├── retrieval.py         # get_top_chunks(query) fonksiyonu — kosinüs benzerliği
│   ├── llm.py                # Foundry Local model yükleme + answer_query(question)
│   ├── prompts.py           # Sistem promptu şablonları (tek yerden yönetim için)
│   └── db_utils.py          # SQLite bağlantısı, tablo oluşturma, CRUD yardımcıları
│
├── ui/
│   ├── cli.py                # Seçenek A: konsol arayüzü
│   ├── streamlit_app.py      # Seçenek B: Streamlit arayüzü (opsiyonel)
│   └── web/                  # Seçenek C: HTML+JS arayüzü (opsiyonel)
│       ├── index.html
│       └── app.js
│
└── tests/
    ├── test_queries.json     # Faz 3 test soruları (yanıtlanabilir/yanıtlanamaz)
    └── test_results.md       # Test çıktılarının kaydı
```

**Neden bu yapı?**
- `data/` ile `db/` ayrımı: ham kaynak ile işlenmiş veri birbirinden ayrı kalır, ingestion yeniden çalıştırıldığında karışıklık olmaz.
- `src/` içindeki her dosya tek bir sorumluluğa sahiptir (ingestion, retrieval, LLM, prompt, veritabanı) — bu, hem hata ayıklamayı kolaylaştırır hem de Hafta 1'de öğretilen "fonksiyonlara/modüllere bölme" pratiğini doğrudan uygular.
- `ui/` klasöründe üç seçeneğin de yan yana durması, takımların CLI ile başlayıp zaman kalırsa Streamlit/web'e geçmesini kolaylaştırır.
- `tests/` ayrı tutulur ki Faz 3'teki test süreci kod değişikliği gerektirmeden çalıştırılabilsin.

---

## Neler Kullanacaksın? (Araç ve Teknoloji Listesi)

| Katman | Araç / Teknoloji | Ne işe yarar | Maliyet |
|---|---|---|---|
| **Çalışma ortamı** | Python 3.10+ | Tüm proje dili | Ücretsiz |
| **Kod editörü** | VS Code | Yazma, çalıştırma, hata ayıklama | Ücretsiz |
| **Model çalışma zamanı** | Foundry Local SDK (`foundry-local-sdk`) | Yerel LLM ve embedding modeli çalıştırma | Ücretsiz |
| **Dil modeli** | Phi-3.5 Mini (veya benzeri 3–5B model) | Yanıt üretimi (generation) | Ücretsiz, cihazda çalışır |
| **Embedding modeli** | qwen3-embedding-0.6b (veya Foundry Local kataloğundaki benzeri) | Metni vektöre çevirme | Ücretsiz, cihazda çalışır |
| **Veritabanı** | SQLite (Python'un yerleşik `sqlite3` modülü) | Doküman + embedding saklama | Ücretsiz |
| **Versiyon kontrolü** | Git + GitHub | Kod yedekleme, takım çalışması | Ücretsiz |
| **Arayüz (Seçenek A)** | Python `input()` / `print()` | Konsol tabanlı soru-cevap | Ücretsiz |
| **Arayüz (Seçenek B, opsiyonel)** | Streamlit veya Gradio | Basit web arayüzü | Ücretsiz |
| **Arayüz (Seçenek C, opsiyonel)** | HTML/CSS/JS + Flask | Özel web arayüzü | Ücretsiz |
| **Barındırma (opsiyonel, demo günü)** | Azure App Service / Static Web Apps | UI'yi herkese açık link olarak paylaşma | $100 kredinin küçük bir kısmı |

**Not:** Listede hiçbir ücretli API anahtarı (OpenAI, Azure OpenAI vb.) yoktur — bu, projenin "sıfır internet bağımlılığı" felsefesinin doğal bir sonucudur. $100 Azure kredisi yalnızca yukarıdaki opsiyonel barındırma adımında devreye girer.

---

## Nasıl Kullanacaksın? (Kurulum & Çalıştırma Adımları)

Aşağıdaki adımlar Hafta 1'de bir kez yapılır, sonraki haftalarda sadece `python main.py` ile devam edilir.

1. **Python kurulumunu doğrula**
   ```bash
   python --version   # 3.10 veya üzeri olmalı
   ```

2. **Proje klasörünü oluştur ve sanal ortam kur**
   ```bash
   mkdir yerel-rag-asistani && cd yerel-rag-asistani
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Foundry Local SDK'sını kur**
   ```bash
   pip install foundry-local-sdk
   ```

4. **Foundry Local'i doğrula (Hello Model testi)**
   ```bash
   python -c "from foundry_local import FoundryLocalManager; print('Kurulum OK')"
   ```
   Hata alırsan, resmi "Get started with Foundry Local" kılavuzundaki platform-spesifik adımları (Windows/macOS) tekrar kontrol et.

5. **Dokümanlarını `data/raw/` klasörüne koy** (ders notları, SSS, kılavuzlar — 5–10 kısa doküman yeterli)

6. **Ingestion'ı çalıştır** (dokümanları chunk'lara böler, embedding üretir, SQLite'a yazar)
   ```bash
   python src/ingest.py
   ```

7. **Asistanı başlat**
   ```bash
   python main.py
   ```
   veya Streamlit seçeneği için:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

8. **Test et:** `tests/test_queries.json` içindeki örnek sorularla asistanı dene, yanıtları `tests/test_results.md`'ye kaydet.

9. **(Opsiyonel) Azure'a yayınla:** Streamlit/Flask uygulamasını Azure App Service'e deploy et, demo günü linki paylaş.

---

## Nasıl Öğreneceksin? (Haftalık Öğrenme Yol Haritası)

Bu bölüm, plandaki kaynakları "ne zaman, hangi sırayla okumalı/izlemeliyim" sorusuna yanıt verecek şekilde özetler.

| Hafta | Önce bunu öğren | Sonra bunu yap | Birincil kaynak |
|---|---|---|---|
| **1** | RAG'in ne olduğu ve neden işe yaradığı (retrieve → augment → generate) | Foundry Local'i kur, "Hello Model" testini çalıştır, `main.py` iskeletini oluştur | Tech Community blog yazısı + Microsoft Learn "Get started with Foundry Local" |
| **2** | Embedding nedir, kosinüs benzerliği nasıl çalışır; SQLite temel SQL komutları | Örnek cümlelerle embedding üret, benzerlik hesapla; SQLite'ta tablo oluşturup veri ekle/sorgula | Microsoft Learn "Build a RAG application" (embedding + arama bölümleri) + W3Schools SQL (opsiyonel) |
| **3** | Doküman chunk'lama stratejileri; retrieval fonksiyonunun mantığı | `ingest.py` ve `retrieval.py`'yi yaz, `get_top_chunks()` fonksiyonunu test et | Aynı tutorial'ın `find_relevant()` örnek kodu |
| **4** | Sistem promptu vs. kullanıcı promptu; chat completion API kullanımı | `llm.py`'de `answer_query()` fonksiyonunu yaz, seçtiğin arayüzü (CLI/Streamlit/Web) uygula | Foundry Local Quickstart (chat completions bölümü) |
| **5** | İyi bir test seti nasıl tasarlanır (yanıtlanabilir/yanıtlanamaz sorular) | Test sorularını takım arkadaşlarınla değiştir, sonuçları kaydet, hataları düzelt | Kendi test sürecin — dış kaynağa gerek yok |
| **6** | Net bir README/proje raporu nasıl yazılır; etkili bir demo nasıl sunulur | README'yi tamamla, kodu temizle, demo provası yap | Kendi dokümantasyonun |

**Öğrenme prensibi:** Her hafta önce 30–45 dakikalık bir kaynak okuma/izleme oturumu, ardından doğrudan o kavramı kodlayan bir egzersiz yapılır — yani teori hiçbir zaman tek başına bırakılmaz, aynı oturumda küçük bir kod parçasıyla pekiştirilir. Takıldığın noktada önce ilgili Microsoft Learn sayfasındaki kod örneğine bak, hâlâ takılıyorsan takım arkadaşınla "rubber duck" yöntemiyle (sorunu sesli anlatarak) çöz.

### Mimari Akış

```
Kullanıcı Sorusu
      ↓
Yerel RAG Uygulaması (sunucu + pipeline)
      ↓ (Vektör Arama)
SQLite Vektör Veritabanı (Doküman Embedding'leri)
      ↓ (Alınan Parçalar / Retrieved Chunks)
Zenginleştirilmiş Bağlam (Augmented Context) → Foundry Local LLM (cihaz üzerinde model)
      ↓
Üretilen Yanıt → Kullanıcı
```

Tüm bu akış internet bağlantısı gerektirmeden gerçekleşir.

---

## Faz 1 (Hafta 1–2): Temel Öğrenme

**Hedefler:** RAG ve yerel AI araçları konusunda güçlü bir kavramsal temel oluşturmak. 2. haftanın sonunda öğrenciler RAG'in nasıl çalıştığını anlamalı ve temel teknolojiler ile geliştirme ortamına aşina olmalıdır. Foundry Local hem Windows hem macOS'ta kurulu ve test edilmiş olmalı, örnek bir SQLite veritabanı oluşturulmalı, küçük test programları (embedding üretimi ve vektör benzerlik araması) çalıştırılmış olmalıdır.

### Hafta 1: RAG Kavramı & Yerel AI Kurulumu

**Konular & Etkinlikler:**

- **RAG'e Giriş:** RAG'in çözdüğü problemi açıklayarak başlayın. Basit örnekler kullanın: genel bir LLM'e spesifik bir alan sorusu sorulur (muhtemelen yanlış yanıt verir), ardından RAG'in dış bilgiyi nasıl entegre ederek yanıtları iyileştirdiği anlatılır. RAG'in "retrieve, augment, generate" adımları ve faydaları (daha doğru yanıtlar, azaltılmış halüsinasyon) ele alınır.
  - *Kaynak:* Microsoft Tech Community blog yazısı "Building Your First Local RAG Application with Foundry Local" — giriş ve "What is RAG" bölümü.
  - *Egzersiz:* Q&A rol yapma: Kısa bir doküman/bilgi tabanı (1 sayfa) verin, öğrenciler RAG'i manuel olarak simüle etsin — biri "retriever" (ilgili paragrafı bulan), diğeri "LLM" (bu bilgiyi kullanarak yanıt formüle eden) rolünü üstlensin.

- **Foundry Local'i Anlama & Ortam Kurulumu:** Microsoft Foundry Local'i ve neden bu projenin anahtarı olduğunu tanıtın. LLM'i tamamen çevrimdışı, öğrenci laptoplarında çalıştırabildiğini vurgulayın (bulut gerekmez); desteklenen platformları (Windows/macOS/Linux) belirtin. Ana özellikleri kapsayın: cihaz üzerinde model indirme, donanım hızlandırma (CPU/GPU/NPU otomatik kullanımı), Python için kolay kullanılır SDK.
  - *Kaynak:* Resmi dokümantasyon — "What is Foundry Local?" genel bakış için. Ayrıca Microsoft Learn'ün "Get started with Foundry Local" kılavuzu (Python sekmesini seçin).
  - *Egzersiz:* Her öğrencinin makinesine Foundry Local SDK'sının (en son sürüm) kurulması (hem Windows hem macOS kurulumları test edilerek). Resmi talimatları izleyerek pip ile kurulum (`pip install foundry-local-sdk` veya işletim sistemine özgü varyant). Kurulumu doğrulamak için bir "Hello Model" testi: Foundry Local SDK'sını kullanarak küçük bir model (ör. phi-1.5-mini) yükleyip basit bir tamamlama üreten kısa bir Python betiği yazmak.

- **Temel Python Uygulama Yapısı:** (Gerekirse) Python projesi yapılandırmasını gözden geçirin: net bir giriş noktasıyla `main.py` kullanma (`if __name__ == "__main__": main()`), kodu fonksiyonlara/modüllere bölme, bağımlılıkları `requirements.txt` ile yönetme.
  - *Kaynak:* Microsoft Learn — "Tutorial: Build a RAG application". "Prerequisites" bölümünü ve `main.py` kurulumuyla ilgili kısmı okuyun.
  - *Egzersiz:* İskelet proje oluşturma: RAG asistanı için yeni bir Python proje klasörü başlatın, bir `main.py` dosyası oluşturun ve bir selamlama yazdırarak test edin.

**1. Hafta Sonu Kilometre Taşları:** Tüm öğrencilerin makinelerinde Foundry Local kurulu ve çalışır durumda; `main.py` dosyasına sahip temel bir proje klasörü var; basit bir Foundry Local çıkarımı çalıştırılabiliyor (kurulumu doğrulamak için yerel modelden çıktı alınabiliyor).

### Hafta 2: Temel Teknikler – Embeddings, Vektör Arama & SQLite

**Konular & Etkinlikler:**

- **Embeddings & Vektör Benzerliği:** Metin embedding'leri kavramını tanıtın — anlamsal anlamı yakalayan metnin sayısal vektör temsilleri. Benzer metnin → benzer vektörlere yol açtığını, bunun anlamsal aramayı mümkün kıldığını açıklayın. Embedding'lerin nasıl elde edileceği (özel modeller aracılığıyla) ve benzerliğin nasıl ölçüleceği (ör. kosinüs benzerliği) tartışılır.
  - *Kaynak:* Microsoft Learn — "Tutorial: Build a RAG application", "Generate document embeddings" ve "Search for relevant documents" bölümleri. Foundry Local'in Python SDK'sının dokümanlar için embedding üretmede ve kosinüs benzerliği hesaplayarak benzerlik araması yapmada nasıl kullanılacağını gösterir.
  - *Egzersiz:* Embedding demosu: Küçük bir örnek cümle listesi verin, öğrenciler her cümle için Foundry Local SDK'sını kullanarak embedding üretsin (küçük bir embedding modeli, ör. qwen3-embedding-0.6b ile). Ardından verilen bir sorgu için (o da embed edilerek) benzerlik skorlarını hesaplayıp en iyi eşleşmeyi bulan basit bir döngü kodlasınlar.

- **SQLite ile Embedding Saklama & Sorgulama:** Birkaç bellek içi dokümanın ötesine ölçeklenirken neden bir vektör deposu/veritabanı gerekebileceğini açıklayın. SQLite'ı, kullanım senaryomuz için hızlı, sunucusuz yerel bir veritabanı motoru olarak tanıtın (ayrı sunucu/kurulum gerekmez; tek bir dosya tüm veriyi tutar). Öğrencilerin temel SQL işlemlerini (tablo oluşturma, veri ekleme ve sorgulama) en azından kavramsal olarak anlaması sağlanır.
  - *Kaynak:* "Benefits of SQLite for local storage" (Microsoft Windows App Development dokümantasyonu bölümü). Opsiyonel olarak, başlangıç seviyesi bir SQLite eğitimi (ör. W3Schools SQL Tutorial — üçüncü taraf, açıkça belirtilmiş).
  - *Egzersiz:* SQL sandbox: Öğrenciler sqlite3 komut satırı aracını kurar ya da yerleşik sqlite3 modülüyle basit bir Python betiği kullanarak küçük bir veritabanı (ör. `id`, `content`, `embedding` alanlarına sahip bir `documents` tablosu) oluşturur. Birkaç örnek satır ekleyip, bir id'ye göre kayıt çekme veya metin anahtar kelimesine göre filtreleme sorgusu pratiği yaparlar.

- **Q&A için Temel Prompt Mühendisliği:** Sadece doküman almanın yeterli olmadığını, bilginin modele nasıl sunulduğunun da önemli olduğunu tartışın. Sistem vs. kullanıcı promptları kavramını (Chat Completion API'deki roller) ve modele alınan metni kullanma, bunun ötesinde tahmin yürütmeme talimatı verme tanıtılır. "Bağlamda bilgi bulamazsan bilmediğini söyle" veya "yanıtta her zaman kaynak adlarını dahil et" gibi basit kurallar paylaşılır.
  - *Kaynak:* Microsoft Learn — "Prompt engineering techniques", özellikle prompt oluşturmanın temelleri ve sistem mesajlarının kullanımı.
  - *Egzersiz:* Prompt denemeleri: Halka açık bir web AI'si (ör. Bing Chat veya ChatGPT) kullanarak öğrenciler aynı soruyu ek bağlamla ve bağlamsız sorsunlar (ör. "Sadece bu bilgiyi kullanarak yanıtla: [bir pasaj verin]"). Bağlamın yanıtı nasıl değiştirdiğini gözlemlesinler.

**2. Hafta Sonu Kilometre Taşları:** Öğrenciler RAG, Foundry Local, embedding'ler ve SQLite hakkında çalışma bilgisine sahip. Test amaçlı bir SQLite veritabanı oluşturuldu (ya da en azından doküman ve vektör saklama şeması kavramsal olarak tasarlandı). Python'da embedding'ler üzerinde kosinüs benzerliği hesaplayarak benzer metin alma pratiği yapıldı; model için temel prompt ifade etme anlaşıldı. Tüm uygulamalı geliştirme ön koşulları hazır.

---

## Faz 2 (Hafta 3–4): Proje Geliştirme

**Hedefler:** Yaklaşık 2 hafta boyunca öğrenciler işlevsel bir yerel RAG uygulaması geliştirecek. Öğrendiklerini her bileşeni uygulamaya geçirerek kullanacaklar: doküman alma (ingestion), vektörleştirme, retrieval ve LLM entegrasyonu. Faz 2'nin sonunda her öğrenci (veya takım), yerel doküman deposundan bilgi alıp modeli çağırmadan önce kullanan, çalışan bir çevrimdışı Q&A chatbot'a sahip olacak.

### Hafta 3: Veri Alma (Ingestion) & Retrieval Pipeline

**Konular & Etkinlikler:**

- **Bilgi Tabanını Tasarlama & Veri Hazırlığı:** Q&A asistanı için küçük bir doküman seti belirleyin (ör. eğitmen tarafından sağlanan veya öğrenciler tarafından seçilen 5–10 kısa doküman — teknik makaleler, ürün SSS'leri veya ders notları). Dokümanları parçalara (chunk) bölme stratejileri tartışılır (RAG genellikle pasaj düzeyinde, ör. ~1–3 paragraflık parçalarla çalışır). Öğrenciler bir veri alma betiği uygulayacak:
  1. Dokümanlarını daha küçük pasajlara (chunk) bölmek.
  2. Foundry Local'in embedding modelini kullanarak her parça için bir embedding hesaplamak.
  3. Her parçayı ve embedding vektörünü daha sonra alınmak üzere SQLite'a kaydetmek.
  - *Kaynak:* Microsoft Learn — "Build a RAG application". Bilgi tabanı oluşturma ve embedding üretme bölümlerini izleyin. Tutorial'ın örnek kodu (Python) uyarlanabilir.
  - *Egzersiz:* Ingestion Pipeline'ını kodlama: `main.py` içinde (veya ayrı bir betik/modülde) her öğrenci, her dokümanı açıp bölen (ör. paragraf veya başlıklara göre) ve her parçayı embed eden kod yazar. Python `sqlite3` kütüphanesi kullanılarak her parça (metin ve embedding vektörü) veritabanına eklenir. Basitlik için embedding bir blob ya da metin (JSON serileştirilmiş vektör) olarak saklanabilir. Test: Ingestion çalıştırıldıktan sonra veritabanının beklenen sayıda kayıt içerdiği doğrulanır.

- **Retrieval Fonksiyonunu Oluşturma:** Veri hazır olduğunda, yeni bir kullanıcı sorgusu geldiğinde ilgili parçaları alma mantığını uygulayın. Öğrenciler:
  1. Sorguyu embed eder (aynı embedding modelini kullanarak).
  2. SQLite'ta benzer vektörleri arar — en basit yaklaşım, saklanan tüm embedding'leri çekip Python'da kosinüs benzerliği hesaplamak, ardından en iyi K parçayı seçmektir (küçük N için bu yeterlidir; büyük N için özel vektör veritabanlarının gerekeceği tartışılır).
  3. En iyi parçaları bağlam olarak döndürür.
  - *Kaynak:* Microsoft'un `find_relevant()` tutorial kodu (her doküman için brute-force benzerlik hesaplar, bizim ölçeğimiz için uygundur). Ayrıca Tech Community blog'unun RAG pipeline kararları bölümüne (kaç parça alınacağı vb.) başvurun.
  - *Egzersiz:* Sorgu Retrieval'ını Uygulama & Test Etme: `get_top_chunks(query)` fonksiyonunu kodda uygulayın, SQLite veritabanından kullanıcı sorgusuna göre en alakalı 2–3 parçayı döndürsün. Bu fonksiyonu mevcut veriye karşı birkaç örnek sorguyla test edin.

**3. Hafta Sonu Kilometre Taşları:** Öğrenciler embedding'lere sahip, doldurulmuş bir SQLite doküman veritabanına ve verilen bir sorgu için en alakalı doküman parçalarını bulabilen çalışan bir retrieval fonksiyonuna sahip.

### Hafta 4: LLM Entegrasyonu & Uygulama Montajı

**Konular & Etkinlikler:**

- **Yerel LLM'i Entegre Etme (Foundry Local Chat Model):** Şimdi bu retrieval mekanizmasını yanıt üretmek için bir dil modeline bağlayın. Öğrenciler Foundry Local üzerinden uygun küçük bir LLM (ör. Phi-3.5 Mini veya benzeri 3–5B parametreli model) yükleyip chat tarzı yanıtlar üretmek için kullanacak. Model seçim ödünleşimleri tartışılır: küçük modeller daha hızlı yanıt verir, büyük modeller daha iyi yanıt sağlar — bu programda öğrencilerin hızlı geri bildirim alması için hıza öncelik veriyoruz.
  - *Kaynak:* Foundry Local Quickstart'ın yerel chat completions API kullanımı bölümü (çoklu tur sohbet için). Daha basit bir yol: tek turlu Q&A gibi davranmak.
  - *Egzersiz:* Model Isınması: Öğrenciler program başlangıcında (ingestion sırasında zaten yüklenmediyse) seçtikleri Foundry Local modelini yükleyen kod yazar. Ardından, `get_top_chunks()`'ı kullanarak bağlam alan ve yerel modelin chat API'sini, modele bağlamı kullanarak yanıt verme (bağlam dışı bilgi kullanmama) talimatı veren bir sistem mesajıyla çağıran bir `answer_query(user_question)` fonksiyonu yazarlar.

- **Basit Kullanıcı Arayüzü Oluşturma:** Zaman ve öğrenci becerisine bağlı olarak, Q&A asistanının arayüzünün nasıl çalışacağı için seçenekler sunun:
  - **Seçenek A — CLI:** En basit yol. Öğrenciler konsoldan sorgu girişi isteyebilir, `answer_query(query)`'i çağırıp yanıtı yazdırabilir.
  - **Seçenek B — Streamlit veya Gradio UI (Python):** Görselleştirme için harika. Kullanıcı soru gönderdiğinde `answer_query`'i çağıran minimal bir Streamlit uygulaması sağlayın.
  - **Seçenek C — Temel HTML+JS UI:** (öğrenciler web geliştirme deneyimi isterse) Blog'un yaklaşımını yeniden kullanabilirler: metin kutusu olan statik bir HTML sayfası ve yanıtlar için yerel bir Flask veya Node sunucu endpoint'ini çağıran JavaScript.
  - Seçenek A, zaman çerçevesi içinde tamamlanmayı garanti eder; B/C seçenekleri ileri düzey öğrencilere veya zaman kalırsa 5. hafta için ek hedef olarak sunulabilir.
  - *Kaynak:* Streamlit dokümantasyonu (üçüncü taraf) veya temel bir Flask/Express eğitimi (Seçenek C için).
  - **Azure kredisi notu (opsiyonel):** Seçenek B/C'yi seçen ileri düzey öğrenciler, demo günü için uygulamalarını $100 kredinin bir kısmıyla Azure App Service (Free/Basic tier) veya Azure Static Web Apps üzerinde barındırarak, takım arkadaşlarının/jürinin tarayıcıdan erişebileceği bir link paylaşabilir. Bu adım tamamen isteğe bağlıdır, çünkü temel proje çevrimdışı çalışır.
  - *Egzersiz:* Uygulama Arayüzünü Tamamlama: Seçilen UI'yi uygulayın. CLI için, kullanıcının birden fazla soru sormasına izin vermek üzere `input()` ile döngü kurun. Web UI için tutorial'ı izleyerek minimal UI öğelerini kurun ve backend ile entegre edin. Uçtan uca kapsamlı test edin.

- **Sorumlu Çıktılar Sağlama:** Öğrencilere prompt mühendisliği en iyi pratiklerini hatırlatın: ör. bağlam yetersizse asistanın bilmediğini söylemesi talimatını her zaman dahil etme (yanıt uydurmamak için). Nazik, öz yanıtlar için sistem promptlarını ince ayarlamaya teşvik edin. Zaman elverirse kaynak atıfları uygulatın: ör. her parçayla kısa bir kaynak adı saklayarak, modelin referansla yanıt vermesini sağlama ("Doküman X'e göre...").

**4. Hafta Sonu Kilometre Taşları:** Her takım, kullanıcının sorusunu (seçtikleri arayüz üzerinden) alıp SQLite tabanlı bilgi tabanından alınan içeriği kullanarak yerel LLM tarafından üretilen bir yanıt döndüren, çalışan bir Q&A uygulamasına sahip. Çekirdek proje işlevselliği tamamlandı.

---

## Faz 3 (Hafta 5–6): Test, Değerlendirme & Dokümantasyon

**Hedefler:** Son fazda öğrenciler uygulamalarını iyileştirip test edecek, performans ve doğruluğu değerlendirecek, dokümantasyon ve sunum hazırlayacak. Bu fazın sonunda projeler cilalanmış ve gösterime hazır olmalı.

### Hafta 5: Sistem Testi & Değerlendirme

**Konular & Etkinlikler:**

- **Fonksiyonel Test:** Öğrenciler asistanlarının çeşitli sorgular için (hem yanıtlayabileceği hem yanıtlayamaması gereken sorular) çalıştığından emin olmak için test senaryoları geliştirir. Şunları doğrulamalılar:
  - Yanıt dokümanlarda mevcutsa sistem ilgili bilgiyle bir yanıt döndürüyor.
  - Bilgi eksikse uygun şekilde yanıt veriyor (ör. sistem promptu talimatına göre "Bu bilgiye sahip değilim" geri dönüş mesajı).
  - Uç durumları işliyor (ör. boş sorgu girişi veya çok genel sorular).
  - *Yaklaşım:* Öğrenciler küçük bir Q&A seti derleyebilir (bazıları dokümanlardan yanıtlanabilir, bazıları yanıtlanamaz). Mümkünse "gerçek kullanıcıları" simüle etmek için test sorularını takımlar arasında değiştirin.

- **Performans & Hata Ayıklama:** Her şey yerel olduğundan, yanıt sürelerinin makul olduğunu kontrol edin (küçük modeller için, tipik bir laptop'ta soru başına ~1–3 saniye). Yanıtlar yavaşsa olası optimizasyonları tartışın (ör. daha az parça alma, daha küçük model kullanma, embedding'leri önbelleğe alarak tekrar hesaplamama). Yanlış retrieval sonuçları veya yanıtlardaki formatlama sorunları gibi kalan sorunları öğrencilerin hata ayıklamasına yardımcı olun.

- **Değerlendirme ve İyileştirme:** Öz eleştiri ve iterasyonu teşvik edin. Öğrencilere şu soruları düşündürün: Yanıtlar doğru mu? İyi yazılmış ve öz mü? Kaynaklar belirtiliyor mu (eğer hedeflendiyse)? Değilse yaklaşımlarını nasıl iyileştirebilirler (ör. prompt formatını ayarlama, daha fazla bağlam alma, parça bölmeyi iyileştirme)?

**5. Hafta Ortası Kilometre Taşı:** Test sonuçları dokümante edilmiş — denenen sorguların ve yanıtların doğru/uygun olup olmadığının bir listesi. Öğrenciler eksiklikleri belirlemeli ve son ayarlamaları planlamalıdır.

### Hafta 6 (veya 5. Hafta sonu): Dokümantasyon & Final Sunum

(Mevcut zamana bağlı olarak, dokümantasyon ve sunum hazırlığı 5. haftanın sonuna doğru testle örtüşebilir veya 6. haftaya uzayabilir.)

**Konular & Etkinlikler:**

- **Proje Dokümantasyonu:** Her takım kısa bir Proje Raporu / README yazar: projenin amacı, nasıl çalıştığı, uygulamayı çalıştırma talimatları ve tasarım kararları veya kısıtlamalar. Ortamı kurma ve asistanı kullanma talimatlarını dahil etmeleri sağlanır (bu aynı zamanda anlayışlarını pekiştirir).

- **Kod Temizliği & Yorumlar:** Öğrenciler kodlarını netlik için gözden geçirir. Hata ayıklama yazdırmalarını kaldırmalı, ana bölümleri açıklayan yorumlar eklemeli (ör. retrieval fonksiyonunun ne yaptığı) ve kod stilinin tutarlı olduğundan emin olmalıdırlar. Bu, henüz kullanılmıyorsa versiyon kontrolünden (Git/GitHub) kısaca bahsetmek için iyi bir nokta olabilir.

- **Final Sunum Hazırlığı:** Her grup, programın sonunda yerel RAG asistanlarının kısa bir demosunu ve sunumunu yapacak. Şunları vurgulamalarına rehberlik edin:
  - **Problem Tanımı:** Asistanları hangi senaryoyu veya kullanıcı ihtiyacını hedefliyor?
  - **Anahtar Özellikler/Bileşenler:** RAG'i nasıl kullandıklarını, hangi veri kaynaklarını dahil ettiklerini kısaca anlatın.
  - **Canlı Demo:** Asistanın birkaç örnek soruyu yanıtlamasını gösterin, biri kaynak belirten ya da bilmediğini söyleyen bir örnek dahil olsun (belirsiz sorguları sorumlu şekilde işlediğini kanıtlamak için).
  - **Öğrenilen Dersler:** Üstesinden geldikleri bir veya iki içgörü veya zorluk (ör. "dokümanları doğru bölmenin iyi retrieval sonuçları için kritik olduğunu öğrendik"). Opsiyonel olarak yaratıcı öğeler ekleyin — ör. asistanlarına isim verme veya arayüzü özelleştirme — sunum güvenini ve katılımını artırmak için.

**6. Hafta Sonu Kilometre Taşları:** Tüm takımlar dokümantasyonla (final raporu veya README) tamamlanmış projelere sahip ve sunumlarını/demolarını prova etmiştir. Program, her takımın çalışan yerel RAG asistanını sunduğu ve öğrendiklerini yansıttığı bir demo günüyle sona erer.

---

## Opsiyonel: $100 Azure Kredisinin Değerlendirilmesi

Proje çekirdeği tamamen yerel ve ücretsiz çalıştığı için kredi harcamak **zorunlu değildir**. Yine de bütçeyi şu şekillerde değerlendirebilirsin:

| Kullanım | Açıklama | Tahmini Maliyet |
|---|---|---|
| **Paylaşımlı geliştirme/test VM'i** | Foundry Local'i Linux üzerinde de test etmek isteyen öğrenciler için B2s/B2ms boyutunda bir Azure VM | Saatlik ~$0.02–0.05, ay boyunca kapatıp açarak düşük tutulabilir |
| **Demo günü web barındırma** | Streamlit/Flask UI'yi Azure App Service (Basic tier) veya Static Web Apps üzerinde herkese açık link olarak yayınlama | Aylık ~$13 (B1 tier) veya Static Web Apps ücretsiz katmanı |
| **Bulut vs. yerel karşılaştırma (stretch goal)** | İleri düzey takımlar için, Azure AI Foundry üzerinde aynı modeli (ör. bir bulut LLM endpoint'i) çalıştırıp yerel Foundry Local sonuçlarıyla hız/maliyet/gizlilik açısından karşılaştırma yapan opsiyonel bir mini-rapor | Token bazlı, birkaç dolar |
| **Container Registry / CI-CD denemesi** | Git/GitHub'a ek olarak Azure DevOps pipeline'ları ile basit bir CI kurulumu denemesi (öğrenme amaçlı) | Çoğunlukla ücretsiz katman yeterli |

Bu eklerin hiçbiri zorunlu değildir; plan, kredi kullanılmadan da eksiksiz tamamlanacak şekilde tasarlanmıştır. Kredi kullanmak istersen, en mantıklı seçenek genellikle **demo günü için web UI'nin Azure üzerinde kısa süreliğine barındırılmasıdır** — düşük maliyetli, görünür bir sonuç verir ve öğrencilere temel bulut deploy deneyimi kazandırır.

---

*Bu plan, Microsoft'un resmi rehberliği (kurulum talimatları, tutorial'lar) ile pratik kodlama egzersizlerini birleştirerek öğrencilerin her bileşende kademeli olarak güven ve yetkinlik kazanmasını, ardından bunları final projede entegre etmesini sağlar. Ayın sonunda işlevsel, çevrimdışı bir AI Q&A sistemine ve modern AI uygulamalarının retrieval (arama) ile generation (üretim) yeteneklerini birleştirerek ve yerel olarak çalıştırarak nasıl inşa edilebileceğine dair sağlam bir anlayışa sahip olacaklar.*
