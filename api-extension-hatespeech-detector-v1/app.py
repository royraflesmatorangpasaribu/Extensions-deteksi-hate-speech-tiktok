from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from tiktokcomment import TiktokComment
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
import re
import string
import json
import requests
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from fastapi import FastAPI
from loguru import logger
import nltk
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
import os
from datetime import datetime
from pydantic import BaseModel
nltk.download('punkt')  # Tambahkan ini untuk mengunduh data


# Konfigurasi loguru
logger.add(sink="sys.stdout", level="INFO")  # Tambahkan ini di file utama

app = FastAPI()

logger.info("Server is starting and loguru is initialized.")  # Tes untuk memastikan log ini muncul

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi objek TiktokComment
tiktok_scraper = TiktokComment()

# Memuat normalization_dict dari URL eksternal
url = 'https://raw.githubusercontent.com/royraflesmatorangpasaribu/model-hate-speech/refs/heads/main/normalization_dict.json'
def load_normalization_dict(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            normalization_dict = json.loads(response.text)
            return normalization_dict
    except Exception as e:
        logger.error(f"Error loading normalization dictionary: {e}")
        return {}

normalization_dict = load_normalization_dict(url)

class ScrapeRequest(BaseModel):
    id_comment: str

# Fungsi untuk membersihkan data
def clean_text(text):
    text = re.sub(r'[{}]'.format(string.punctuation), ' ', text)  # Hapus tanda baca
    text = re.sub(r'[^\w\s]', '', text)  # Hapus simbol non-alfanumerik
    text = re.sub(r'[0-9]+', '', text)  # Hapus angka
    emoticon_pattern = re.compile("[" 
        u"\U0001F600-\U0001F64F"  # emotikon wajah
        u"\U0001F300-\U0001F5FF"  # simbol & ikon
        u"\U0001F680-\U0001F6FF"  # transportasi & simbol
        u"\U0001F1E0-\U0001F1FF"  # bendera
        "]+", flags=re.UNICODE)
    text = emoticon_pattern.sub(r'', text)  # Hapus emotikon
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebih
    return text

# Fungsi case folding
def case_folding(text):
    return text.lower()

# Fungsi normalisasi teks
def normalize_text(text):
    words = text.split()
    normalized_words = [normalization_dict.get(word, word) for word in words]
    return ' '.join(normalized_words)

# Fungsi tokenisasi
def tokenize(text):
    return word_tokenize(text)

# Fungsi penghapusan stopwords
def stopwords_removal(tokens):
    # ranks.nl stopwords indonesian list
    stop_words = set([
        "ada", "adanya", "adalah", "adapun", "agak", "agaknya", "agar", "akan", "akankah", "akhirnya",
        "aku", "akulah", "amat", "amatlah", "anda", "andalah", "antar", "diantaranya", "antara", "antaranya",
        "diantara", "apa", "apaan", "mengapa", "apabila", "apakah", "apalagi", "apatah", "atau", "ataukah",
        "ataupun", "bagai", "bagaikan", "sebagai", "sebagainya", "bagaimana", "bagaimanapun", "sebagaimana",
        "bagaimanakah", "bagi", "bahkan", "bahwa", "bahwasanya", "sebaliknya", "banyak", "sebanyak",
        "beberapa", "seberapa", "begini", "beginian", "beginikah", "beginilah", "sebegini", "begitu", "begitukah",
        "begitulah", "begitupun", "sebegitu", "belum", "belumlah", "sebelum", "sebelumnya", "sebenarnya", "berapa",
        "berapakah", "berapalah", "berapapun", "betulkah", "sebetulnya", "biasa", "biasanya", "bila", "bilakah",
        "bisa", "bisakah", "sebisanya", "boleh", "bolehkah", "bolehlah", "buat", "bukan", "bukankah", "bukanlah",
        "bukannya", "cuma", "percuma", "dahulu", "dalam", "dan", "dapat", "dari", "daripada", "dekat", "demi",
        "demikian", "demikianlah", "sedemikian", "dengan", "depan", "di", "dia", "dialah", "dini", "diri", "dirinya",
        "terdiri", "dong", "dulu", "enggak", "enggaknya", "entah", "entahlah", "terhadap", "terhadapnya", "hal",
        "hampir", "hanya", "hanyalah", "harus", "haruslah", "harusnya", "seharusnya", "hendak", "hendaklah",
        "hendaknya", "hingga", "sehingga", "ia", "ialah", "ibarat", "ingin", "inginkah", "inginkan", "ini", "inikah",
        "inilah", "itu", "itukah", "itulah", "jangan", "jangankan", "janganlah", "jika", "jikalau", "juga", "justru",
        "kala", "kalau", "kalaulah", "kalaupun", "kalian", "kami", "kamilah", "kamu", "kamulah", "kan", "kapan",
        "kapankah", "kapanpun", "dikarenakan", "karena", "karenanya", "ke", "kecil", "kemudian", "kenapa", "kepada",
        "kepadanya", "ketika", "seketika", "khususnya", "kini", "kinilah", "kiranya", "sekiranya", "kita", "kitalah",
        "kok", "lagi", "lagian", "selagi", "lah", "lain", "lainnya", "melainkan", "selaku", "lalu", "melalui",
        "terlalu", "lama", "lamanya", "selama", "selama", "selamanya", "lebih", "terlebih", "bermacam", "macam",
        "semacam", "maka", "makanya", "makin", "malah", "malahan", "mampu", "mampukah", "mana", "manakala", "manalagi",
        "masih", "masihkah", "semasih", "masing", "mau", "maupun", "semaunya", "memang", "mereka", "merekalah", "meski",
        "meskipun", "semula", "mungkin", "mungkinkah", "nah", "namun", "nanti", "nantinya", "nyaris", "oleh", "olehnya",
        "seorang", "seseorang", "pada", "padanya", "padahal", "paling", "sepanjang", "pantas", "sepantasnya",
        "sepantasnyalah", "para", "pasti", "pastilah", "per", "pernah", "pula", "pun", "merupakan", "rupanya", "serupa",
        "saat", "saatnya", "sesaat", "saja", "sajalah", "saling", "bersama", "sama", "sesama", "sambil", "sampai",
        "sana", "sangat", "sangatlah", "saya", "sayalah", "se", "sebab", "sebabnya", "sebuah", "tersebut", "tersebutlah",
        "sedang", "sedangkan", "sedikit", "sedikitnya", "segala", "segalanya", "segera", "sesegera", "sejak", "sejenak",
        "sekali", "sekalian", "sekalipun", "sesekali", "sekaligus", "sekarang", "sekarang", "sekitar", "sekitarnya",
        "sela", "selain", "selalu", "seluruh", "seluruhnya", "semakin", "sementara", "sempat", "semua", "semuanya",
        "sendiri", "sendirinya", "seolah", "seperti", "sepertinya", "sering", "seringnya", "serta", "siapa", "siapakah",
        "siapapun", "disini", "disinilah", "sini", "sinilah", "sesuatu", "sesuatunya", "suatu", "sesudah", "sesudahnya",
        "sudah", "sudahkah", "sudahlah", "supaya", "tadi", "tadinya", "tak", "tanpa", "setelah", "telah", "tentang",
        "tentu", "tentulah", "tentunya", "tertentu", "seterusnya", "tapi", "tetapi", "setiap", "tiap", "setidaknya",
        "tidak", "tidakkah", "tidaklah", "toh", "waduh", "wah", "wahai", "sewaktu", "walau", "walaupun", "wong",
        "yaitu", "yakni", "yang"
    ])

    # Filter tokens
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

# Fungsi menggabungkan token menjadi kalimat
def to_sentence(tokens):
    return ' '.join(tokens)

# Muat TfidfVectorizer yang sudah dilatih
with open('tfidf_vectorizer_model_lima.pkl', 'rb') as file:
    tfidf = pickle.load(file)
    

import numpy as np

# Fungsi utama preprocessing
def preprocess_comment(text):
    logger.info(f"Text before cleaning: {text}")
    text = clean_text(text)
    text = case_folding(text)
    text = normalize_text(text)
    tokens = tokenize(text)
    tokens = stopwords_removal(tokens)
    final_text = to_sentence(tokens)
    logger.info(f"Final preprocessed text: {final_text}")
    
    # Gunakan TfidfVectorizer yang sudah dilatih untuk transformasi
    vectorizer_text = tfidf.transform([final_text])
    
    # Konversi vectorizer_text ke array numpy dan pastikan bentuknya (1, 1000)
    vectorizer_text_array = vectorizer_text.toarray()
    logger.info(f"Vectorized text (numpy array): {vectorizer_text_array.shape}")
    
    return final_text, vectorizer_text_array  # Return dalam bentuk array numpy 
 
# ada komentar asli
def extract_comments_and_replies(comments: List[Any]) -> List[Dict[str, Any]]:
    seen_comments = set()  # Set untuk menyimpan komentar yang unik
    records = []

    with open('naive_bayes_model_lima.pkl', 'rb') as m:
        model = pickle.load(m)

    for comment in comments: 
        if comment.comment not in seen_comments:
            seen_comments.add(comment.comment)  # Tambahkan ke set jika belum ada
            original_text = comment.comment  # Simpan komentar asli
            preprocessed_text, vector = preprocess_comment(original_text)

            # Pastikan bahwa prediksi dilakukan pada array yang berbentuk (1, 1000)
            if preprocessed_text:
                predict = model.predict(vector)  # Prediksi kelas
                predict_proba = model.predict_proba(vector)  # Probabilitas prediksi
                # Ambil probabilitas sesuai kelas yang diprediksi
                probability = predict_proba[0][predict[0]]
                
                if predict == 0:
                    main_comment = {
                        "original_comment": original_text,  # Komentar asli
                        "processed_comment": preprocessed_text,  # Komentar setelah diproses
                        "prediksi": int(predict[0]),  # Pastikan hasil prediksi diubah ke integer
                        "predict_proba": probability  # Ambil probabilitas kelas yang diprediksi
                    }
                    records.append(main_comment)

        # Lakukan proses yang sama untuk replies
        replies = getattr(comment, "replies", [])
        for reply in replies:
            if reply.comment not in seen_comments:
                seen_comments.add(reply.comment)
                original_reply_text = reply.comment  # Simpan komentar asli
                preprocessed_reply_text, vector_reply = preprocess_comment(original_reply_text)

                if preprocessed_reply_text:
                    predict_reply = model.predict(vector_reply)
                    predict_proba_reply = model.predict_proba(vector_reply)
                    # Ambil probabilitas sesuai kelas yang diprediksi
                    probability_reply = predict_proba_reply[0][predict_reply[0]]

                    if predict_reply == 0:
                        reply_data = {
                            "original_comment": original_reply_text,  # Komentar asli
                            "processed_comment": preprocessed_reply_text,  # Komentar setelah diproses
                            "prediksi": int(predict_reply[0]),
                            "predict_proba": probability_reply  # Ambil probabilitas kelas yang diprediksi
                        }
                        records.append(reply_data)

    return records

    
@app.post("/scrape-comments")
async def scrape_comments(request: ScrapeRequest):
    try:
        # Tambahkan log untuk memeriksa request data
        logger.info(f"Request data: {request}")
        id_comment = request.id_comment
        logger.info(f"Scraping comment ID: {id_comment}")

        raw_data = tiktok_scraper(id_comment=id_comment)

        if not raw_data or not raw_data.comments:
            raise HTTPException(status_code=404, detail="Tidak ada komentar ditemukan")

        formatted_comments = extract_comments_and_replies(raw_data.comments)

        return {"comments": formatted_comments}

    except Exception as e:
        logger.error(f"Error saat melakukan scraping komentar: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil komentar")  

class ValidationRequest(BaseModel):
    comment_text: str
    is_like: int  # 1 for like, 0 for dislike
    timestamp: str

@app.post("/validate-comment")
def validate_comment(request: ValidationRequest):
    try:
        # Format data untuk disimpan
        data = {
            "comment_text": request.comment_text,
            "is_like": request.is_like,
            "timestamp": request.timestamp,
        }

        # Simpan data ke file CSV
        file_path = "user_validations.csv"
        file_exists = os.path.isfile(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["comment_text", "is_like", "timestamp"])
            if not file_exists:
                writer.writeheader()  # Tulis header jika file belum ada
            writer.writerow(data)

        return {"message": "Validation saved successfully."}

    except Exception as e:
        logger.error(f"Error saving validation: {e}")
        raise HTTPException(status_code=500, detail="Failed to save validation.")