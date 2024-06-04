import json
import requests
from bs4 import BeautifulSoup
import boto3
from datetime import datetime


def handler(event, context):
    kategori_url_leri = [
        "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FuUnlHZ0pVVWlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr",
        "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FuUnlLQUFQAQ?hl=tr&gl=TR&ceid=TR%3Atr",
        "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FuUnlHZ0pVVWlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr"
    ]
    kategori_metinleri = {
        "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FuUnlHZ0pVVWlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr": "Eğlence",
        "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FuUnlLQUFQAQ?hl=tr&gl=TR&ceid=TR%3Atr": "Sağlık",
        "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FuUnlHZ0pVVWlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr": "Spor"
    }
    tum_linkler = []
    haber_sirasi = 1

    for i, url in enumerate(kategori_url_leri):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        articles = soup.find_all("article")

        for article in articles:
            link = article.find("a")
            if not link:
                continue

            href = link.get("href")
            if href is None:
                continue

            full_url = f"https://news.google.com{href[1:]}" if href.startswith(
                '.') else href

            parent_div = link.find_parent()
            source = article.find("div", class_="vr1PYe").text.strip() if article.find("div",
                                                                                       class_="vr1PYe") else "Kaynak Belirtilmemiş"
            time = article.find("time", class_="hvbAAd").text.strip() if article and article.find("time",
                                                                                                  class_="hvbAAd") else ""

            # Title bilgisini güncellenen sınıf adı ile al
            title = article.find("a", class_="gPFEn")
            title_text = title.text.strip() if title else article.text.strip()

            kategori_metni = kategori_metinleri.get(url, "Bilinmeyen Kategori")

            link_data = {
                "url": full_url,
                "haber başlığı": kategori_metni,
                "kısa açıklaması": title_text,
                "yayınlanma tarihi": time,
                "haber kaynağı": source,
                "kaçıncı sırada": haber_sirasi
            }
            tum_linkler.append(link_data)
            haber_sirasi += 1

    # Generate JSON Data
    json_data = json.dumps(tum_linkler, ensure_ascii=False, indent=4)

    # Save JSON Data to a File in /tmp directory (Lambda writable directory)
    file_name = f'/tmp/news_links_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(json_data)

    # Assuming AWS credentials are set up via Lambda's execution role
    bucket_name = 'ottoofellow'

    # Upload the File to S3
    s3 = boto3.client('s3')
    s3.upload_file(file_name, 'ottoofellow', file_name.split('/')[-1])

    return {
        'statusCode': 200,
        'body': json.dumps(f'File {file_name.split("/")[-1]} uploaded successfully to {bucket_name}.')
    }
