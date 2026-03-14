import redis
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)

# uygulamanın tüm trafiğini otomatik ölçecek
metrics = PrometheusMetrics(app)

# redis veritabanına bağlanacak (kubernetes'teki redis servisini arar)
redis_host = os.environ.get('REDIS_HOST', 'redis')

# host olarak IP adresi değil, veritabanını yazıyoruz
cache = redis.Redis(host=redis_host, port=6379)

# statik bilgi (etiket) ekleyelim
metrics.info('app_info', 'Mikro Servis Projesi', version='1.0.0')

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except Exception as exc:
            if retries == 0:
                raise exc
            retries -= 1
            import time
            time.sleep(0.5)

@app.route('/')
def hello():
    # ziyaret sayısını Redis'ten al ve 1 artır
    count = get_hit_count()
    return f"""
	<h1>Bu web sitesine {count} kez giris yapildi.</h1><br>
	<p>Bu mimari, "stateless" (durumsuz) bir web servisi ile "stateful" (durumlu) bir in-memory veri <br>
	deposunun birbirinden izole edildiği temel bir mikroservis yapısıdır. İstemciden (tarayıcıdan) gelen <br>
	HTTP istekleri, ana makinenin (host) 8000 portuna ulaşır ve Docker Compose tarafından oluşturulan <br>
	özel köprü ağı (bridge network) üzerinden Flask tabanlı web konteynerinin 5000 portuna yönlendirilir. <br>
	Web servisi, uygulama durumunu (state) kendi belleğinde tutmak yerine, aynı izole ağ içinde yer alan <br>
	ve Docker'ın dahili DNS çözünürlüğü sayesinde doğrudan servis adıyla erişebildiği Redis konteynerine <br>
	(6379 portuna) iletir. Redis, anahtar-değer (key-value) eşleşmesindeki sayacı artırıp sonucu döndürdükten <br>
	sonra web servisi bu veriyi işleyerek istemciye sunar. Uygulama katmanı ile veri katmanının bu şekilde <br>
	ayrıştırılması (decoupling), web servisinin yatayda bağımsız olarak ölçeklenebilmesine (horizontal scaling) <br>
	olanak tanır.</p>
	"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
