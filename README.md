# AI Sug'orish Tizimi (AI Irrigation System)

Ushbu loyiha AI asosida ishlaydigan aqlli sug'orish tizimi bo'lib, Django backend va JavaScript frontend bilan ishlaydi. Tizim datchiklar ma'lumotlarini tahlil qilib, optimal sug'orish vaqti va miqdorini aniqlaydi.

## Xususiyatlari

### 🌱 Asosiy Imkoniyatlar
- **Real vaqt monitoringi**: Tuproq namligi, harorat, havo namligi kabi parametrlarni kuzatuv
- **AI tahlili**: Gemini AI orqali chuqur tahlil va tavsiyalar
- **Avtomatik sug'orish**: AI bashoratiga asoslangan avtomatik sug'orish tizimi
- **Ob-havo integratsiyasi**: OpenWeatherMap API orqali ob-havo ma'lumotlari
- **Professional dashboard**: Real vaqt ma'lumotlari bilan zamonaviy interfeys
- **Qo'lda boshqaruv**: Manual rejimda tizimni boshqarish imkoniyati

### 🔧 Texnologiyalar
- **Backend**: Django 4.2, Django REST Framework
- **AI**: Google Gemini AI API
- **Ob-havo**: OpenWeatherMap API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Ma'lumotlar bazasi**: SQLite (rivojlantirish uchun)
- **API**: RESTful API architecture

### 📊 Dashboard Sahifalari
1. **Dashboard**: Asosiy ma'lumotlar va real vaqt monitoringi
2. **Ob-havo**: Kengaytirilgan ob-havo tahlili va prognozi
3. **Datchilar**: Barcha datchilar holati va statistika
4. **AI Tahlil**: AI asosidagi chuqur tahlil va tavsiyalar
5. **Boshqaruv**: Tizimni qo'lda boshqarish paneli

## O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.8+
- pip (Python package manager)
- Git

### 2. Loyihani Klonlash
```bash
git clone <repository-url>
cd testapp
```

### 3. Virtual Environment Yaratish
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Bog'lamlarni O'rnatish
```bash
pip install -r requirements.txt
```

### 5. Environment Variables
`.env` faylini sozlang (`.env.example` dan nusxa oling):

```bash
cp .env.example .env
```

`.env` faylida quyidagi parametrlarni to'ldiring:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
OPENWEATHER_API_KEY=your-openweathermap-api-key
GEMINI_API_KEY=your-google-gemini-api-key
```

### 6. Ma'lumotlar Bazasini Tayyorlash
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Serverni Ishga Tushirish
```bash
python manage.py runserver
```

Dashboard: http://localhost:8000

## API Endpointlari

### Asosiy API Yo'llari

#### Datchilar API (`/api/sensor/`)
- `GET /api/sensor/sensors/` - Barcha datchilar ro'yxati
- `GET /api/sensor/readings/` - Datchik o'qishlari
- `GET /api/sensor/weather/` - Ob-havo ma'lumotlari
- `GET /api/sensor/dashboard/` - Dashboard uchun to'liq ma'lumotlar
- `POST /api/sensor/generate-sample-data/` - Test ma'lumotlari yaratish

#### O'simliklar API (`/api/plant/`)
- `GET /api/plant/plants/` - O'simliklar ro'yxati
- `GET /api/plant/irrigation-events/` - Sug'orish hodisalari
- `GET /api/plant/irrigation-summary/` - Sug'orish xulosasi
- `POST /api/plant/trigger-irrigation/` - Qo'lda sug'orish boshlash

#### Boshqaruv API (`/api/controller/`)
- `POST /api/controller/start-irrigation/` - Sug'orishni boshlash
- `POST /api/controller/stop-irrigation/` - Sug'orishni to'xtatish
- `GET /api/controller/irrigation-status/` - Tizim holati
- `POST /api/controller/emergency-stop/` - Favqulodda to'xtatish

#### AI API (`/api/ai/`)
- `POST /api/ai/analyze-irrigation/` - Sug'orish tahlili
- `POST /api/ai/comprehensive-analysis/` - To'liq AI tahlil
- `GET /api/ai/insights/` - AI xulosalari

## Tizim Arxitekturasi

```
project/
├── manage.py                 # Django asosiy fayl
├── requirements.txt          # Python bog'lamlari
├── .env                     # Environment variables
├── project/                 # Asosiy sozlamalar
│   ├── settings.py          # Django sozlamalari
│   ├── urls.py             # Asosiy URL routing
│   └── wsgi.py             # WSGI konfiguratsiya
├── sensor/                  # Datchilar aplikatsiyasi
│   ├── models.py           # Ma'lumotlar modellari
│   ├── views.py            # API views
│   ├── urls.py             # URL routing
│   └── serializers.py      # API serializers
├── plant/                   # O'simliklar aplikatsiyasi
│   ├── models.py           # O'simlik modellari
│   └── views.py            # O'simlik API
├── controller/              # Boshqaruv aplikatsiyasi
│   ├── views.py            # Boshqaruv API
│   └── esp_controller.py   # ESP32 aloqa
├── ai_engine/              # AI aplikatsiyasi
│   ├── models.py           # AI modellari
│   ├── views.py            # AI API
│   └── predictors.py       # AI algoritmlar
└── dashboard/              # Dashboard aplikatsiyasi
    ├── views.py            # Dashboard API
    ├── urls.py             # Dashboard routing
    └── templates/          # HTML templates
        └── dashboard/
            └── index.html  # Asosiy dashboard
```

## API Kalitlari Olish

### OpenWeatherMap API
1. https://openweathermap.org saytiga ro'yxatdan o'ting
2. API kalitini oling
3. `.env` fayliga qo'shing

### Google Gemini AI API
1. https://ai.google.dev saytiga kiring
2. API kalitini yarating
3. `.env` fayliga qo'shing

## Xususiyatlarni Sozlash

### Datchik Parametrlari
`project/settings.py` faylida:
```python
IRRIGATION_SETTINGS = {
    'CRITICAL_SOIL_MOISTURE': 25,    # Kritik namlik (%)
    'WARNING_SOIL_MOISTURE': 40,     # Ogohlantirish namlik (%)
    'OPTIMAL_SOIL_MOISTURE': 70,     # Optimal namlik (%)
    'DEFAULT_IRRIGATION_DURATION': 18, # Standart davomiyligi (daqiqa)
    'SENSOR_UPDATE_INTERVAL': 120,   # Yangilanish oralig'i (soniya)
}
```

## Testlash

### Test Ma'lumotlarini Yaratish
```bash
# Django shell orqali
python manage.py shell

# Yoki API orqali
curl -X POST http://localhost:8000/api/sensor/generate-sample-data/
curl -X POST http://localhost:8000/api/plant/create-sample-plants/
```

### AI Tahlil Testi
Dashboard → AI Tahlil sahifasida "🔍 AI Tahlil Bajarish" tugmasini bosing.

## Muammolarni Hal Qilish

### Ma'lumotlar Bazasi Muammolari
```bash
# Ma'lumotlar bazasini qayta yaratish
python manage.py flush
python manage.py migrate
```

### API Kalitlari Muammolari
- `.env` fayl mavjudligini tekshiring
- API kalitlari to'g'riligini tekshiring
- Internet aloqasini tekshiring

### Frontend Muammolari
- Browser konsole (F12) tekshiring
- API endpointlari ishlayotganini tekshiring
- CORS sozlamalarini tekshiring

## Rivojlantirish

### Yangi Datchik Qo'shish
1. `sensor/models.py` da yangi `SensorType` yarating
2. Migration yarating va ishga tushiring
3. `sensor/views.py` da kerakli logikani qo'shing

### Yangi AI Algoritm Qo'shish
1. `ai_engine/predictors.py` da yangi klass yarating
2. `ai_engine/views.py` da API endpoint qo'shing
3. Frontend da foydalanish uchun JavaScript qo'shing

## Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## Yordam

Savollar yoki muammolar bo'lsa, issue yaratishingiz yoki bog'lanishingiz mumkin.

---

**Izoh**: Bu tizim demo maqsadlarda yaratilgan bo'lib, haqiqiy ishlab chiqarish muhitida qo'shimcha xavfsizlik va optimizatsiya choralari qo'llanishi kerak.