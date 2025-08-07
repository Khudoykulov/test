#!/usr/bin/env python
"""
AI Irrigation System Setup Script
Bu skript tizimni avtomatik sozlaydi va ishga tushiradi.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Buyruqni ishga tushirish va natijasini ko'rsatish"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} muvaffaqiyatli bajarildi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} xato: {e}")
        print(f"Xato tafsiloti: {e.stdout}\n{e.stderr}")
        return False

def check_python_version():
    """Python versiyasini tekshirish"""
    print("🐍 Python versiyasini tekshirish...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ kerak. Sizning versiyangiz:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python versiyasi yaxshi: {version.major}.{version.minor}")
    return True

def create_virtual_environment():
    """Virtual environment yaratish"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("📁 Virtual environment allaqachon mavjud")
        return True
    
    return run_command("python -m venv venv", "Virtual environment yaratish")

def activate_virtual_environment():
    """Virtual environment faollashtirish uchun yo'riqnoma"""
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Linux/Mac
        activate_script = "source venv/bin/activate"
    
    print(f"📝 Virtual environment faollashtirish uchun quyidagi buyruqni ishga tushiring:")
    print(f"   {activate_script}")
    return True

def install_dependencies():
    """Bog'lamlarni o'rnatish"""
    pip_command = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    return run_command(f"{pip_command} install -r requirements.txt", "Python bog'lamlarini o'rnatish")

def setup_environment_file():
    """Environment faylini sozlash"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("📁 .env fayl allaqachon mavjud")
        return True
    
    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✅ .env fayl yaratildi (.env.example dan)")
        print("⚠️  Iltimos, .env faylida API kalitlarini to'ldiring:")
        print("   - OPENWEATHER_API_KEY")
        print("   - GEMINI_API_KEY")
        return True
    else:
        print("❌ .env.example fayl topilmadi")
        return False

def run_migrations():
    """Django migrationslarini ishga tushirish"""
    python_command = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    
    success = True
    success &= run_command(f"{python_command} manage.py makemigrations", "Migrations yaratish")
    success &= run_command(f"{python_command} manage.py migrate", "Ma'lumotlar bazasini sozlash")
    
    return success

def create_sample_data():
    """Namuna ma'lumotlarini yaratish"""
    python_command = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    
    print("📊 Namuna ma'lumotlarini yaratish...")
    # Django shell orqali sample data yaratish
    django_shell_commands = """
from django.core.management import execute_from_command_line
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

# Import models
from sensor.models import *
from plant.models import *
from ai_engine.models import *

print("Namuna ma'lumotlari yaratilmoqda...")
print("Bu API endpointlar orqali amalga oshiriladi.")
"""
    
    return True

def print_success_message():
    """Muvaffaqiyat xabarini ko'rsatish"""
    print("\n" + "="*60)
    print("🎉 AI SUGH'ORISH TIZIMI MUVAFFAQIYATLI O'RNATILDI!")
    print("="*60)
    print("\n📋 KEYINGI QADAMLAR:")
    print("1. Virtual environment faollashtiring:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. API kalitlarini sozlang (.env faylida):")
    print("   - OpenWeatherMap API kaliti")
    print("   - Google Gemini AI API kaliti")
    
    print("\n3. Serverni ishga tushiring:")
    print("   python manage.py runserver")
    
    print("\n4. Dashboard ochish:")
    print("   http://localhost:8000")
    
    print("\n5. Admin panel (ixtiyoriy):")
    print("   Superuser yaratish: python manage.py createsuperuser")
    print("   Admin panel: http://localhost:8000/admin")
    
    print("\n📚 QOSHHIMCHA MALUMOTLAR:")
    print("   - README.md faylini o'qing")
    print("   - API dokumentatsiya: http://localhost:8000/api/")
    
    print("\n🔧 YORDAM:")
    print("   - Muammolar bo'lsa issue yaratishingiz mumkin")
    print("   - Test ma'lumotlar uchun: Dashboard → Generate Sample Data")
    print("="*60)

def main():
    """Asosiy setup funktsiya"""
    print("🚀 AI Sugh'orish Tizimi O'rnatish Boshlandi")
    print("="*50)
    
    steps = [
        ("Python versiyasini tekshirish", check_python_version),
        ("Virtual environment yaratish", create_virtual_environment),
        ("Environment fayl sozlash", setup_environment_file),
        ("Bog'lamlarni o'rnatish", install_dependencies),
        ("Ma'lumotlar bazasi sozlash", run_migrations),
        ("Namuna ma'lumotlar tayyorlash", create_sample_data),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        if not step_function():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ Quyidagi qadamlar muvaffaqiyatsiz bo'ldi:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nIltimos, xatolarni hal qilib, qaytadan urinib ko'ring.")
        return False
    else:
        print_success_message()
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup jarayoni bekor qilindi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        sys.exit(1)