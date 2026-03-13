# python şablonunu altyapı olarak alıyoruz
FROM python:3.9-alpine

# çalışma klasörü
WORKDIR /kod

# requirements'i kopyalıyoruz ve kuruyoruz
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# app.py dosyasını /kod klasörüne kopyala
COPY . .

# başlat
CMD ["python", "app.py"]
