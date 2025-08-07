import requests

api_key = "158bc1531f8c316715082a34e62dfb88"  # O'zingizning kalitingizni qo'ying
url = f"https://api.openweathermap.org/data/2.5/weather?q=Tashkent&appid={api_key}&units=metric"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"Harorat: {data['main']['temp']}°C")
else:
    print(f"Xatolik: {response.status_code} - {response.text}")



import google.generativeai as genai

api_key = 'AIzaSyCVORtht3UZsy3vWfyLt1OEI_sH38ki7tw'  # Get from Google AI Studio

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Salom")
print(response.text)