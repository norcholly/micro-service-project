Bir CI/CD Anatomisi

Bu repository, manuel ve geleneksel sistem yönetimi süreçlerinin oluşturduğu darboğazları aşmak amacıyla sıfırdan tasarlanmış bir **DevOps Capstone Projesidir**. 

Proje kapsamında; kodun yazılmasından canlıya alınmasına, mikroservislerin ayrıştırılmasından sistem metriklerinin görselleştirilmesine kadar tüm süreçler kurumsal **"Infrastructure as Code" (Kod Olarak Altyapı)** standartlarıyla uçtan uca otomatize edilmiştir.

---

## 🏗️ Sistem Mimarisi ve Veri Akışı

Bu sistem, geliştiricinin GitHub'a yaptığı ilk push işleminden, son kullanıcının tarayıcısında görüntülediği analitik ekranına kadar uzanan tam otonom bir veri akışına sahiptir. Kod değişiklikleri Jenkins CI/CD pipeline tarafından algılanıp Docker imajlarına dönüştürülür ve kesintisiz bir şekilde Kubernetes (K3s) kümesine dağıtılır. Eş zamanlı olarak, küme içindeki Prometheus sensörleri uygulama metriklerini toplayarak Grafana üzerinden canlı gösterge panellerine yansıtır.

---

## 🛠️ Temel Katmanlar ve Teknolojik Kararlar

### 1. Konteynerizasyon ve Mikroservis Ayrışımı (Docker)
Uygulama katmanı ("stateless" Python/Flask servisi) ile veri katmanı ("stateful" Redis in-memory veri deposu) birbirinden tamamen izole edilmiştir. Bu "decoupling" stratejisi, web servisinin veri kaybı yaşanmadan yatayda bağımsız olarak ölçeklenebilmesine olanak tanır. Tüm bağımlılıklar deterministik bir `Dockerfile` ile paketlenmiştir.

### 2. Otonom Orkestrasyon ve Sıfır Kesinti (Kubernetes / K3s)
Sistemin istenen durumu (Desired State) K3s ile güvence altına alınmıştır.
* **Kube-DNS:** Servisler arası iletişim, ephemeral IP adreslerine bağımlı kalmadan doğrudan servis isimleri üzerinden sağlanmıştır.
* **Rolling Update:** Yeni imajlar sahaya sürülürken, eski pod'lar trafiği kesmeden yenileriyle değiştirilerek "Zero-Downtime Deployment" elde edilmiştir.
* **Fault Tolerance:** Olası bir veritabanı kesintisinde uygulamanın çökmesini engellemek için kod seviyesinde "Retry" (Yeniden Deneme) kalkanları inşa edilmiştir.

### 3. Sürekli Entegrasyon ve Dağıtım (Jenkins Pipeline)
Geliştirme sürecini insan hatalarından arındırmak için `Jenkinsfile` ile 4 aşamalı bir Declarative Pipeline kurulmuştur:
1. **Checkout:** Ana dala (main branch) gelen yeni kodlar çekilir.
2. **Build & Tagging:** Statik etiketler yerine `${env.BUILD_NUMBER}` kullanılarak her imaja benzersiz bir versiyon ID'si atanır. Bu mimari, anında geri dönüş (Rollback) imkanı sağlar.
3. **Push:** Docker Hub kimlik bilgileri ve Kubeconfig yetki belgeleri Jenkins Credentials Vault içinde şifrelenerek saklanır.
4. **Deploy:** Kubernetes API'sine güvenli bir şekilde erişilerek yeni versiyon otonom olarak sahaya sürülür.

### 4. Gözlemlenebilirlik ve Analitik (Prometheus & Grafana)
Sistemi kör uçuşundan çıkarmak adına, Flask uygulamasının kalbine bir **Prometheus Exporter** entegre edilmiştir. Saniyedeki HTTP istek sayıları, gecikme süreleri (latency) ve hata oranları `/metrics` uç noktasından dışarı yayınlanır. Zaman serisi veritabanı olan Prometheus bu ham verileri toplar ve Grafana entegrasyonu sayesinde anlık, eyleme dönüştürülebilir sistem sağlığı panelleri oluşturulur.

