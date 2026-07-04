# 1 Haftalık Yoğun Plan: Yerel RAG AI Asistanı

> **Kime göre yazıldı:** Next.js / Supabase / Tailwind deneyimi olan, Python'a geçiş yapan biri. Günde **6–8 saat** çalışma varsayılmıştır. SQL, API entegrasyonu ve proje dosya yapısı konularında sıfırdan başlamıyorsun — bu yüzden 6 haftalık plan 7 güne sığıyor.

---

## Ön Hazırlık (Başlamadan Önce — 1 saat)

Aşağıdakileri önceden hazırla, ilk güne temiz başla:

```bash
# 1. Python versiyonunu kontrol et (3.10+ olmalı)
python --version

# 2. VS Code'da Python extension kurulu mu kontrol et
# Extensions → "Python" (Microsoft) → Install

# 3. Git reposunu oluştur
mkdir yerel-rag-asistani && cd yerel-rag-asistani
git init
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Temel bağımlılıkları kur
pip install foundry-local-sdk streamlit python-dotenv
pip freeze > requirements.txt
```

**Doküman seç:** `data/raw/` klasörüne 5–8 kısa `.txt` veya `.md` dosyası koy. Ders notları, SSS, kılavuz — ne olursa. Her dosya ~300–500 kelime olsun (çok uzun olmasın, ilk seferinde chunk mantığını basit tut).

---

## Pazartesi — Foundry Local Kurulum & Hello Model

**Hedef:** Foundry Local çalışıyor, ilk model çıktısını gördün, proje iskeleti hazır.

**Sabah (3 saat) — Kurulum & Anlama**

Önce şu blog yazısını oku (30 dk):
> https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968

Sonra resmi "Get started" kılavuzunu aç, Python sekmesini seç, adımları uygula:
> https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started

```bash
# Foundry Local'in CLI'sını test et
foundry model list        # mevcut modelleri göster
foundry model download phi-3.5-mini   # LLM modeli indir (~2–4 GB, zaman alır)
foundry model download qwen3-embedding-0.6b  # embedding modeli indir (~600 MB)
```

> ⚠️ **Model indirme uzun sürebilir.** İndirirken aşağıdaki dosya yapısını oluştur.

**Dosya yapısını oluştur:**

```
yerel-rag-asistani/
├── main.py
├── requirements.txt
├── .env
├── data/
│   └── raw/          ← dokümanlarını buraya koy
├── db/               ← knowledge.db buraya oluşacak
├── src/
│   ├── __init__.py
│   ├── ingest.py
│   ├── retrieval.py
│   ├── llm.py
│   ├── prompts.py
│   └── db_utils.py
└── ui/
    └── streamlit_app.py
```

```bash
# Klasörleri tek komutla oluştur
mkdir -p data/raw db src ui
touch main.py .env src/__init__.py src/ingest.py src/retrieval.py src/llm.py src/prompts.py src/db_utils.py ui/streamlit_app.py
```

**Öğleden sonra (3 saat) — Hello Model testi**

`src/llm.py` dosyasına yaz:

```python
from foundry_local import FoundryLocalManager

# Model alias — Foundry Local alias sistemi kullanır
MODEL_ALIAS = "phi-3.5-mini"
EMBEDDING_ALIAS = "qwen3-embedding-0.6b"

def get_manager():
    """Foundry Local manager'ı başlat ve modeli yükle."""
    manager = FoundryLocalManager(model_alias=MODEL_ALIAS)
    return manager

def test_hello():
    """Modelin çalıştığını doğrula."""
    manager = get_manager()
    client = manager.get_client()  # OpenAI-uyumlu client döner

    response = client.chat.completions.create(
        model=manager.get_model_info(MODEL_ALIAS).id,
        messages=[
            {"role": "user", "content": "Merhaba! Tek cümleyle kendini tanıt."}
        ]
    )
    print("Model yanıtı:", response.choices[0].message.content)

if __name__ == "__main__":
    test_hello()
```

```bash
python src/llm.py
# Çıktıda modelin bir şey yazdığını görürsen Pazartesi tamamdır.
```

**Akşam (1 saat) — RAG'i kavra**

Microsoft Learn'deki şu sayfayı oku, sadece ilk 3 bölüm yeterli:
> https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/tutorials/tutorial-build-rag-application

**Pazartesi sonu checkpoint:**
- [ ] `foundry model list` çalışıyor
- [ ] Phi-3.5 Mini ve qwen3-embedding-0.6b indirildi
- [ ] `python src/llm.py` bir yanıt yazdırdı
- [ ] Dosya yapısı oluşturuldu

---

## Salı — Embedding & SQLite

**Hedef:** Bir cümleyi vektöre çevirebiliyorsun, SQLite'a yazıp okuyabiliyorsun.

**Sabah (3 saat) — Embedding üretimi**

`src/db_utils.py` dosyasına yaz:

```python
import sqlite3
import json
import os

DB_PATH = "db/knowledge.db"

def get_connection():
    os.makedirs("db", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Doküman ve embedding tablosunu oluştur."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            source  TEXT NOT NULL,        -- hangi dosyadan geldiği
            chunk   TEXT NOT NULL,        -- paragraf metni
            embedding TEXT NOT NULL       -- JSON serileştirilmiş vektör
        )
    """)
    conn.commit()
    conn.close()
    print("Tablo oluşturuldu.")

def insert_chunk(source: str, chunk: str, embedding: list):
    conn = get_connection()
    conn.execute(
        "INSERT INTO documents (source, chunk, embedding) VALUES (?, ?, ?)",
        (source, chunk, json.dumps(embedding))
    )
    conn.commit()
    conn.close()

def get_all_chunks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT id, source, chunk, embedding FROM documents").fetchall()
    conn.close()
    return [
        {"id": r[0], "source": r[1], "chunk": r[2], "embedding": json.loads(r[3])}
        for r in rows
    ]

def clear_db():
    conn = get_connection()
    conn.execute("DELETE FROM documents")
    conn.commit()
    conn.close()
    print("Veritabanı temizlendi.")

if __name__ == "__main__":
    create_tables()
    # Test: sahte bir kayıt ekle
    insert_chunk("test.txt", "Bu bir test cümlesidir.", [0.1, 0.2, 0.3])
    rows = get_all_chunks()
    print(f"Kayıt sayısı: {len(rows)}")
    print("İlk kayıt chunk:", rows[0]["chunk"])
    clear_db()
```

```bash
python src/db_utils.py
# "Tablo oluşturuldu" ve "Kayıt sayısı: 1" görmeli
```

**Öğleden sonra (3 saat) — Embedding üretimi**

`src/llm.py` dosyasına embedding fonksiyonunu ekle:

```python
def get_embedding(text: str, manager) -> list[float]:
    """Bir metni embedding vektörüne çevir."""
    client = manager.get_client()
    response = client.embeddings.create(
        model=manager.get_model_info(EMBEDDING_ALIAS).id,
        input=text
    )
    return response.data[0].embedding

def test_embedding():
    manager = get_manager()
    vec = get_embedding("Yapay zeka nedir?", manager)
    print(f"Vektör boyutu: {len(vec)}")   # ~768 veya 1024 bekle
    print(f"İlk 5 değer: {vec[:5]}")

if __name__ == "__main__":
    test_hello()
    test_embedding()
```

**Akşam (1 saat) — Kosinüs benzerliği**

`src/retrieval.py` içine benzerlik fonksiyonunu yaz (henüz search yok, sadece matematik):

```python
import math

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """İki vektör arasındaki kosinüs benzerliğini hesapla (−1 ile 1 arası)."""
    dot    = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

if __name__ == "__main__":
    # Basit test: aynı vektör → benzerlik 1.0 olmalı
    v = [0.1, 0.5, 0.3, 0.9]
    print(cosine_similarity(v, v))          # 1.0
    print(cosine_similarity(v, [0]*4))      # 0.0
```

**Salı sonu checkpoint:**
- [ ] `python src/db_utils.py` hata vermeden çalışıyor
- [ ] `python src/llm.py` embedding vektörü üretiyor (boyut 768+)
- [ ] `python src/retrieval.py` 1.0 yazdırıyor

---

## Çarşamba — Ingestion Pipeline

**Hedef:** `data/raw/` içindeki dokümanlar chunk'lanıp embed edildi, SQLite dolu.

**Sabah (2 saat) — Chunk stratejisi**

`src/ingest.py` dosyasına yaz:

```python
import os
from src.db_utils import create_tables, insert_chunk, clear_db, get_all_chunks
from src.llm import get_manager, get_embedding

DATA_DIR = "data/raw"
CHUNK_SIZE = 400        # karakter bazında maksimum chunk boyutu
CHUNK_OVERLAP = 50      # ardışık chunk'lar arasında örtüşme (bağlam kaybını önler)

def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def split_into_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Metni örtüşen chunk'lara böl.
    Önce paragraflara, sonra gerekirse karakter boyutuna göre böler.
    """
    # Önce paragraflara ayır (boş satır = paragraf sınırı)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) <= size:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
                # Overlap: bir önceki chunk'un sonunu bir sonrakine taşı
                current = current[-overlap:] + "\n\n" + para
            else:
                # Tek paragraf size'dan büyükse zorla böl
                for i in range(0, len(para), size - overlap):
                    chunks.append(para[i:i + size])
                current = ""

    if current:
        chunks.append(current)

    return chunks

def ingest_all():
    """data/raw/ klasöründeki tüm .txt ve .md dosyalarını işle."""
    create_tables()
    clear_db()   # her çalıştırmada sıfırdan başla

    manager = get_manager()
    files = [f for f in os.listdir(DATA_DIR) if f.endswith((".txt", ".md"))]

    if not files:
        print(f"UYARI: {DATA_DIR} klasöründe .txt veya .md dosyası bulunamadı!")
        return

    total_chunks = 0
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        text = read_file(filepath)
        chunks = split_into_chunks(text)

        print(f"\n📄 {filename} → {len(chunks)} chunk")
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk, manager)
            insert_chunk(source=filename, chunk=chunk, embedding=embedding)
            print(f"   chunk {i+1}/{len(chunks)} embedding'lendi ({len(chunk)} karakter)")
            total_chunks += 1

    all_rows = get_all_chunks()
    print(f"\n✅ Ingestion tamamlandı. Toplam {total_chunks} chunk SQLite'a yazıldı.")
    print(f"   Veritabanı: db/knowledge.db ({len(all_rows)} kayıt)")

if __name__ == "__main__":
    ingest_all()
```

```bash
python src/ingest.py
# Her dosya için chunk sayısını ve embedding ilerlemeyi görmeli
```

**Öğleden sonra (2 saat) — Sorun çıkarsa debug et**

Sık karşılaşılan sorunlar:

| Hata | Çözüm |
|---|---|
| `ModuleNotFoundError: foundry_local` | `pip install foundry-local-sdk` tekrar çalıştır |
| `Model not found` | `foundry model list` ile doğru alias'ı kontrol et |
| `UnicodeDecodeError` | Dosyayı UTF-8 olarak kaydet (VS Code → sağ alt köşe → UTF-8) |
| Embedding çok yavaş | Normal — CPU'da ~1–3 sn/chunk. 50 chunk için ~2 dk bekle |

**Akşam (1 saat) — Veritabanını doğrula**

```bash
# SQLite CLI ile veriyi gör
sqlite3 db/knowledge.db

# İçinde şunu çalıştır:
SELECT id, source, substr(chunk, 1, 80) as preview FROM documents LIMIT 10;
SELECT COUNT(*) as toplam FROM documents;
.quit
```

Beklenen çıktı: kayıtların listelendiğini ve toplam chunk sayısını görürsün.

**Çarşamba sonu checkpoint:**
- [ ] `python src/ingest.py` hata vermeden tamamlandı
- [ ] SQLite'ta en az 10+ kayıt var
- [ ] `sqlite3 db/knowledge.db` ile kayıtları gözle doğruladın

---

## Perşembe — Retrieval + LLM → Uçtan Uca Pipeline

**Hedef:** Bir soru soruyorsun, ilgili chunk'lar geliyor, model yanıt üretiyor. Hepsi yerel.

**Sabah (3 saat) — Retrieval fonksiyonu**

`src/retrieval.py` dosyasını tamamla:

```python
import math
from src.db_utils import get_all_chunks
from src.llm import get_embedding, get_manager

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot    = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def get_top_chunks(query: str, manager, top_k: int = 3) -> list[dict]:
    """
    Kullanıcı sorgusuna en yakın top_k chunk'ı döndür.
    Dönen her item: {source, chunk, score}
    """
    query_embedding = get_embedding(query, manager)
    all_chunks = get_all_chunks()

    # Her chunk için benzerlik skoru hesapla
    scored = []
    for row in all_chunks:
        score = cosine_similarity(query_embedding, row["embedding"])
        scored.append({
            "source": row["source"],
            "chunk":  row["chunk"],
            "score":  score
        })

    # Skora göre sırala, en iyi top_k'yı döndür
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

if __name__ == "__main__":
    manager = get_manager()
    results = get_top_chunks("Yapay zeka nasıl çalışır?", manager, top_k=3)
    for i, r in enumerate(results):
        print(f"\n--- Sonuç {i+1} (skor: {r['score']:.4f}) ---")
        print(f"Kaynak: {r['source']}")
        print(r['chunk'][:200])
```

```bash
python src/retrieval.py
# 3 chunk ve skorlarını görmelisin
```

**Öğleden sonra (3 saat) — LLM entegrasyonu**

`src/prompts.py` dosyasına yaz:

```python
SYSTEM_PROMPT = """Sen yardımcı bir asistansın. Yalnızca sana verilen bağlam bilgisini kullanarak yanıt ver.
Bağlamda cevap bulamazsan "Bu konuda elimde bilgi yok." de — asla tahmin yürütme.
Yanıtlarında hangi kaynaktan bilgi aldığını belirt: örneğin "(Kaynak: dosya_adi.txt)".
Türkçe yaz, kısa ve öz ol."""

def build_prompt(context_chunks: list[dict], user_question: str) -> list[dict]:
    """Chat completion API için mesaj listesi oluştur."""
    # Chunk'ları birleştir, kaynak bilgisini ekle
    context_text = "\n\n".join(
        f"[Kaynak: {c['source']}]\n{c['chunk']}"
        for c in context_chunks
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Bağlam:\n{context_text}\n\nSoru: {user_question}"}
    ]
```

`src/llm.py` dosyasına `answer_query` fonksiyonunu ekle:

```python
from src.prompts import build_prompt
from src.retrieval import get_top_chunks

def answer_query(user_question: str, manager, top_k: int = 3) -> dict:
    """
    Kullanıcı sorusuna RAG pipeline ile yanıt üret.
    Döndürür: {answer, sources, chunks}
    """
    # 1. Retrieve — ilgili chunk'ları bul
    top_chunks = get_top_chunks(user_question, manager, top_k=top_k)

    # 2. Augment — prompt oluştur
    messages = build_prompt(top_chunks, user_question)

    # 3. Generate — modeli çağır
    client  = manager.get_client()
    model_id = manager.get_model_info(MODEL_ALIAS).id

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=0.3,   # daha tutarlı yanıt için düşük tutuldu
        max_tokens=512
    )

    answer  = response.choices[0].message.content
    sources = list({c["source"] for c in top_chunks})

    return {"answer": answer, "sources": sources, "chunks": top_chunks}
```

**Akşam (1 saat) — Uçtan uca test**

`main.py` dosyasına yaz:

```python
from src.llm import get_manager, answer_query

def main():
    print("🤖 Yerel RAG Asistanı başlatılıyor...")
    manager = get_manager()
    print("✅ Model hazır. Çıkmak için 'q' yaz.\n")

    while True:
        soru = input("Sorun: ").strip()
        if soru.lower() in ("q", "quit", "çık"):
            break
        if not soru:
            continue

        sonuc = answer_query(soru, manager)
        print(f"\n💬 Yanıt:\n{sonuc['answer']}")
        print(f"\n📚 Kaynaklar: {', '.join(sonuc['sources'])}")
        print("-" * 60 + "\n")

if __name__ == "__main__":
    main()
```

```bash
python main.py
# Gerçek soru sor, yanıt ve kaynak görüyor musun kontrol et
```

**Perşembe sonu checkpoint:**
- [ ] `python src/retrieval.py` alakalı chunk'ları döndürüyor (skora bak)
- [ ] `python main.py` konsolda soru-cevap çalışıyor
- [ ] Cevabın sonunda kaynak dosya adı yazıyor

---

## Cuma — Streamlit UI & Testler

**Hedef:** Tarayıcıdan çalışan bir arayüz var, temel testler tamamlandı.

**Sabah (3 saat) — Streamlit UI**

`ui/streamlit_app.py` dosyasına yaz:

```python
import streamlit as st
from src.llm import get_manager, answer_query

st.set_page_config(page_title="Yerel RAG Asistanı", page_icon="🤖")
st.title("🤖 Yerel RAG Asistanı")
st.caption("Foundry Local + SQLite — tamamen çevrimdışı çalışır")

# Manager'ı bir kez yükle (Streamlit session state kullan)
if "manager" not in st.session_state:
    with st.spinner("Model yükleniyor..."):
        st.session_state.manager = get_manager()

# Sohbet geçmişi
if "history" not in st.session_state:
    st.session_state.history = []

# Geçmiş mesajları göster
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Yeni soru
if soru := st.chat_input("Sorunuzu yazın..."):
    # Kullanıcı mesajını ekle
    st.session_state.history.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.write(soru)

    # Yanıt üret
    with st.chat_message("assistant"):
        with st.spinner("Yanıt üretiliyor..."):
            sonuc = answer_query(soru, st.session_state.manager)

        st.write(sonuc["answer"])

        # Kaynak chunk'ları expander'da göster
        with st.expander(f"📚 Kaynaklar ({', '.join(sonuc['sources'])})"):
            for i, chunk in enumerate(sonuc["chunks"]):
                st.markdown(f"**{chunk['source']}** (skor: {chunk['score']:.3f})")
                st.text(chunk["chunk"][:300] + "...")
                if i < len(sonuc["chunks"]) - 1:
                    st.divider()

    # Asistan yanıtını geçmişe ekle
    st.session_state.history.append({
        "role": "assistant",
        "content": sonuc["answer"]
    })
```

```bash
streamlit run ui/streamlit_app.py
# Tarayıcı otomatik açılır: http://localhost:8501
```

**Öğleden sonra (2 saat) — Test senaryoları**

`tests/test_queries.json` dosyasını oluştur:

```json
[
  {
    "soru": "DOKÜMANLARINLA İLGİLİ BİR SORU YAZ",
    "beklenen": "yanıtlanabilir",
    "not": "dokümanın ilk paragrafında geçiyor"
  },
  {
    "soru": "BAŞKA BİR SORU",
    "beklenen": "yanıtlanabilir",
    "not": "ikinci dosyada var"
  },
  {
    "soru": "Türkiye'nin başkenti neresidir?",
    "beklenen": "yanıtlanamaz",
    "not": "dokümanlarda geçmiyor, 'bilgi yok' demeli"
  },
  {
    "soru": "",
    "beklenen": "boş girdi",
    "not": "uygulama çökmemeli"
  }
]
```

Her soruyu UI üzerinden dene, sonuçları `tests/test_results.md` dosyasına kaydet:

```markdown
# Test Sonuçları

| Soru | Beklenen | Gerçek Çıktı | Geçti mi? |
|---|---|---|---|
| ... | yanıtlanabilir | doğru yanıt + kaynak | ✅ |
| ... | yanıtlanamaz | "bilgi yok" dedi | ✅ |
| (boş) | çökmemeli | sessizce geçti | ✅ |
```

**Akşam (1 saat) — Son düzeltmeler**

Yaygın sorunlar ve çözümleri:

| Sorun | Nerede düzelt |
|---|---|
| Yanlış chunk geliyor | `ingest.py`'de `CHUNK_SIZE` küçült (400 → 250) ve ingestion'ı yeniden çalıştır |
| Model "bilmiyorum" diyor ama dokümanında var | `get_top_chunks()` içinde `top_k` değerini 3 → 5 yap |
| Yanıt çok uzun | `prompts.py`'de "kısa ve öz ol" vurgusunu artır, `max_tokens` değerini düşür |
| Türkçe karakterler bozuk | Dosyaları UTF-8 olarak kaydet |

**Cuma sonu checkpoint:**
- [ ] Streamlit UI tarayıcıda açılıyor ve soru-cevap çalışıyor
- [ ] Kaynak expander'ı chunk'ları gösteriyor
- [ ] En az 4 test sorusu çalıştırıldı, sonuçlar kayıt altında

---

## Cumartesi — Azure AI Foundry Karşılaştırması (Opsiyonel)

**Hedef:** Aynı soruyu hem yerel hem bulutta çalıştır, farkı ölç.

> Bu adım tamamen isteğe bağlıdır. Atlayabilirsin.

**Kurulum (2 saat):**

1. [portal.azure.com](https://portal.azure.com) → **Azure AI Foundry** → yeni proje oluştur
2. **Model Catalog** → **Phi-3.5-mini-instruct** → **Deploy** → endpoint URL + API key al
3. `.env` dosyasına ekle:
   ```
   AZURE_ENDPOINT=https://...inference.ai.azure.com/...
   AZURE_API_KEY=sk-...
   ```

4. `src/llm.py` dosyasına bulut fonksiyonu ekle:

```python
import os, requests
from dotenv import load_dotenv
load_dotenv()

def answer_query_cloud(user_question: str, context_chunks: list[dict]) -> dict:
    """Aynı soruyu Azure AI Foundry endpoint'i ile yanıtla."""
    from src.prompts import build_prompt
    import time

    messages = build_prompt(context_chunks, user_question)
    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv("AZURE_API_KEY")
    }
    body = {
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 512
    }

    start = time.time()
    response = requests.post(os.getenv("AZURE_ENDPOINT"), json=body, headers=headers)
    elapsed = time.time() - start

    return {
        "answer":  response.json()["choices"][0]["message"]["content"],
        "elapsed": round(elapsed, 2)
    }
```

**Karşılaştırma betiği (1 saat):**

```python
# compare.py — kök klasöre koy
import time
from src.llm import get_manager, get_top_chunks, answer_query, answer_query_cloud

TEST_SORULARI = [
    "DOKÜMANLARINDAN BİR SORU",
    "BAŞKA BİR SORU",
]

manager = get_manager()

print(f"{'SORU':<40} {'YEREL (sn)':<12} {'BULUT (sn)':<12}")
print("-" * 70)

for soru in TEST_SORULARI:
    chunks = get_top_chunks(soru, manager)

    # Yerel
    t0 = time.time()
    yerel = answer_query(soru, manager)
    yerel_sure = round(time.time() - t0, 2)

    # Bulut
    bulut = answer_query_cloud(soru, chunks)

    print(f"{soru[:38]:<40} {yerel_sure:<12} {bulut['elapsed']:<12}")
    print(f"  Yerel : {yerel['answer'][:100]}")
    print(f"  Bulut : {bulut['answer'][:100]}")
    print()
```

```bash
python compare.py
```

Sonuçları `tests/test_results.md`'ye ekle.

**Cumartesi sonu checkpoint:**
- [ ] Azure AI Foundry endpoint'i çalışıyor (opsiyonel)
- [ ] Yerel vs. bulut yanıt süresi karşılaştırması yapıldı (opsiyonel)

---

## Pazar — README, Temizlik & Demo

**Hedef:** Proje paylaşılabilir, demo hazır, kod temiz.

**Sabah (2 saat) — README yaz**

`README.md` dosyasına yaz:

```markdown
# Yerel RAG AI Asistanı

Microsoft Foundry Local + SQLite kullanarak tamamen çevrimdışı çalışan bir Q&A chatbotu.

## Nasıl çalışır?

1. Dokümanlar chunk'lara bölünür ve embedding vektörlerine dönüştürülür → SQLite'a yazılır
2. Kullanıcı soru sorduğunda, soru da embed edilir → en yakın chunk'lar bulunur
3. Bulunan chunk'lar + soru → Phi-3.5 Mini modeline gönderilir → yanıt üretilir
4. Hiçbir adımda internet bağlantısı kullanılmaz

## Kurulum

\`\`\`bash
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
foundry model download phi-3.5-mini
foundry model download qwen3-embedding-0.6b
\`\`\`

## Kullanım

\`\`\`bash
# 1. Dokümanları data/raw/ klasörüne koy (.txt veya .md)
# 2. Ingestion yap
python src/ingest.py

# 3a. Konsol arayüzü
python main.py

# 3b. Web arayüzü
streamlit run ui/streamlit_app.py
\`\`\`

## Teknolojiler

| Katman | Teknoloji |
|---|---|
| Model çalışma zamanı | Microsoft Foundry Local |
| LLM | Phi-3.5 Mini (cihazda çalışır) |
| Embedding | qwen3-embedding-0.6b |
| Veritabanı | SQLite |
| UI | Streamlit |

## Test sonuçları

Bkz. `tests/test_results.md`
```

**Öğleden sonra (2 saat) — Kod temizliği**

- [ ] Tüm `print()` debug satırlarını kaldır veya yorum satırı yap
- [ ] Her fonksiyona kısaca ne yaptığını açıklayan docstring ekle
- [ ] `requirements.txt`'i güncelle: `pip freeze > requirements.txt`
- [ ] `.env` dosyasını `.gitignore`'a ekle (API anahtarlarını GitHub'a göndermemek için)
- [ ] Son bir kez `python src/ingest.py` → `python main.py` → `streamlit run ui/streamlit_app.py` çalıştır, hepsi sorunsuz açılıyor mu?

**Akşam (1 saat) — Demo provası**

Demo sırasında şunları göster:
1. `streamlit run ui/streamlit_app.py` komutuyla uygulamayı başlat
2. Dokümanda olan bir soruyu sor → doğru yanıt + kaynak
3. Dokümanda olmayan bir soruyu sor → "bilgi yok" yanıtı
4. Kaynak expander'ını aç → chunk'ları göster
5. (Varsa) `compare.py` ile yerel vs. bulut karşılaştırmasını göster

---

## Özet Tablo

| Gün | Ne yaptın | Dosya |
|---|---|---|
| Pazartesi | Kurulum, Hello Model | `src/llm.py` |
| Salı | Embedding, SQLite, kosinüs benzerliği | `src/db_utils.py`, `src/retrieval.py` |
| Çarşamba | Ingestion pipeline | `src/ingest.py` |
| Perşembe | Retrieval + LLM → uçtan uca pipeline | `src/retrieval.py`, `src/llm.py`, `main.py` |
| Cuma | Streamlit UI + testler | `ui/streamlit_app.py`, `tests/` |
| Cumartesi | Azure karşılaştırması (opsiyonel) | `compare.py` |
| Pazar | README, temizlik, demo | `README.md` |

---

## Hızlı Referans — Sık Kullanılan Komutlar

```bash
# Sanal ortamı aktive et
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Bağımlılıkları kur
pip install -r requirements.txt

# Model listesi
foundry model list

# Modeli indir
foundry model download phi-3.5-mini
foundry model download qwen3-embedding-0.6b

# Ingestion (dokümanlar değiştiğinde yeniden çalıştır)
python src/ingest.py

# Konsol arayüzü
python main.py

# Web arayüzü
streamlit run ui/streamlit_app.py

# SQLite'a bak
sqlite3 db/knowledge.db "SELECT COUNT(*) FROM documents;"

# Azure karşılaştırması (opsiyonel)
python compare.py
```
