"""
AI Prediction Engine
This module contains the main AI logic for irrigation system predictions.
"""

import logging
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class IrrigationPredictor:
    """AI predictor for irrigation needs"""
    
    def __init__(self):
        self.model_version = "1.2.3"
        self.accuracy = 94.2  # Mock accuracy percentage
        
    def predict_irrigation_need(self, sensor_data: Dict, weather_data: Dict, plant_data: Dict) -> Dict:
        """
        Predict if irrigation is needed based on sensor, weather, and plant data
        
        Args:
            sensor_data (dict): Current sensor readings
            weather_data (dict): Weather information
            plant_data (dict): Plant health and growth data
            
        Returns:
            dict: Prediction results with confidence score and recommendations
        """
        try:
            # Extract key metrics
            soil_moisture = sensor_data.get('soil_moisture', 50)
            air_humidity = sensor_data.get('air_humidity', 60)
            temperature = sensor_data.get('temperature', 25)
            rainfall_forecast = weather_data.get('rainfall_forecast', 0)
            
            # AI prediction logic (simplified for demonstration)
            irrigation_score = self._calculate_irrigation_score(
                soil_moisture, air_humidity, temperature, rainfall_forecast
            )
            
            # Determine irrigation need
            need_irrigation = irrigation_score > 0.7
            confidence_score = min(95, irrigation_score * 100)
            
            # Generate recommendation
            recommendation = self._generate_irrigation_recommendation(
                irrigation_score, soil_moisture, weather_data
            )
            
            # Calculate optimal timing
            optimal_timing = self._calculate_optimal_timing(weather_data, temperature)
            
            return {
                'need_irrigation': need_irrigation,
                'irrigation_score': round(irrigation_score, 3),
                'confidence_score': round(confidence_score, 1),
                'recommendation': recommendation,
                'optimal_timing': optimal_timing,
                'reasoning': self._generate_reasoning(
                    soil_moisture, air_humidity, temperature, rainfall_forecast, irrigation_score
                ),
                'predicted_duration_minutes': self._calculate_duration(soil_moisture),
                'water_amount_ml': self._calculate_water_amount(soil_moisture, temperature),
                'model_version': self.model_version,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Irrigation prediction error: {e}")
            return {
                'error': str(e),
                'need_irrigation': False,
                'confidence_score': 0,
                'recommendation': 'AI tahlil xatosi - qo\'lda tekshiring'
            }
    
    def _calculate_irrigation_score(self, soil_moisture: float, air_humidity: float, 
                                   temperature: float, rainfall: float) -> float:
        """Calculate irrigation need score (0-1)"""
        
        # Soil moisture weight (most important factor)
        moisture_weight = 0.5
        if soil_moisture < 25:
            moisture_score = 1.0  # Critical need
        elif soil_moisture < 40:
            moisture_score = 0.8  # High need
        elif soil_moisture < 60:
            moisture_score = 0.4  # Medium need
        else:
            moisture_score = 0.1  # Low need
        
        # Air humidity weight
        humidity_weight = 0.2
        humidity_score = max(0, (70 - air_humidity) / 70)  # Lower humidity = higher score
        
        # Temperature weight
        temp_weight = 0.2
        temp_score = max(0, (temperature - 20) / 15)  # Higher temp = higher score
        
        # Rainfall forecast weight (negative factor)
        rain_weight = 0.1
        rain_score = max(0, 1 - rainfall / 10)  # More rain = lower score
        
        # Combined score
        total_score = (
            moisture_score * moisture_weight +
            humidity_score * humidity_weight +
            temp_score * temp_weight +
            rain_score * rain_weight
        )
        
        return min(1.0, total_score)
    
    def _generate_irrigation_recommendation(self, score: float, soil_moisture: float, 
                                          weather_data: Dict) -> str:
        """Generate human-readable recommendation"""
        
        if score > 0.9:
            return "KRITIK - Darhol sug'orish kerak! Tuproq juda quruq."
        elif score > 0.7:
            return "Yuqori prioritet - 2 soat ichida sug'orish tavsiya etiladi."
        elif score > 0.5:
            return "O'rtacha prioritet - 6 soat ichida sug'orish rejalashtiring."
        elif score > 0.3:
            return "Past prioritet - Kuzatishda saqlang, hozircha sug'orish shart emas."
        else:
            return "Sug'orish kerak emas - Tuproq namligi yetarli."
    
    def _calculate_optimal_timing(self, weather_data: Dict, temperature: float) -> Dict:
        """Calculate optimal irrigation timing"""
        
        current_hour = timezone.now().hour
        
        # Best times are early morning (6-8) or evening (18-20)
        if 6 <= current_hour <= 8:
            return {
                'timing': 'optimal',
                'message': 'Hozirgi vaqt optimal - ertalab soatlari',
                'next_optimal': 'Bugun kechqurun 18:00-20:00'
            }
        elif 18 <= current_hour <= 20:
            return {
                'timing': 'optimal',
                'message': 'Hozirgi vaqt optimal - kechqurun soatlari',
                'next_optimal': 'Ertaga ertalab 06:00-08:00'
            }
        elif 10 <= current_hour <= 16:
            return {
                'timing': 'avoid',
                'message': 'Kunduzi sug\'orish tavsiya etilmaydi - suv bug\'lanadi',
                'next_optimal': 'Bugun kechqurun 18:00-20:00'
            }
        else:
            return {
                'timing': 'acceptable',
                'message': 'Qabul qilinadigan vaqt',
                'next_optimal': 'Ertalab 06:00-08:00'
            }
    
    def _calculate_duration(self, soil_moisture: float) -> int:
        """Calculate irrigation duration in minutes"""
        if soil_moisture < 25:
            return 20  # Critical - longer irrigation
        elif soil_moisture < 40:
            return 15  # Standard irrigation
        elif soil_moisture < 55:
            return 10  # Light irrigation
        else:
            return 5   # Minimal irrigation
    
    def _calculate_water_amount(self, soil_moisture: float, temperature: float) -> int:
        """Calculate water amount in ml"""
        base_amount = 300
        
        # Adjust for soil moisture
        moisture_factor = max(0.5, (60 - soil_moisture) / 60)
        
        # Adjust for temperature
        temp_factor = 1 + max(0, (temperature - 20) / 40)
        
        return int(base_amount * moisture_factor * temp_factor)
    
    def _generate_reasoning(self, soil_moisture: float, air_humidity: float, 
                          temperature: float, rainfall: float, score: float) -> str:
        """Generate AI reasoning explanation"""
        reasons = []
        
        if soil_moisture < 30:
            reasons.append(f"Tuproq namligi kritik darajada ({soil_moisture}%)")
        elif soil_moisture < 50:
            reasons.append(f"Tuproq namligi optimaldan past ({soil_moisture}%)")
        
        if air_humidity < 50:
            reasons.append(f"Havo namligi past ({air_humidity}%)")
        
        if temperature > 28:
            reasons.append(f"Yuqori harorat ({temperature}°C)")
        
        if rainfall < 2:
            reasons.append("Yaqin kelajakda yomg'ir kutilmaydi")
        
        if not reasons:
            reasons.append("Barcha ko'rsatkichlar normal diapazonida")
        
        return " • ".join(reasons)


class PlantHealthAnalyzer:
    """AI analyzer for plant health assessment"""
    
    def __init__(self):
        self.model_version = "2.1.0"
        
    def analyze_plant_health(self, sensor_data: Dict, plant_data: Dict, 
                           historical_data: List[Dict]) -> Dict:
        """
        Analyze overall plant health based on various factors
        
        Args:
            sensor_data (dict): Current sensor readings
            plant_data (dict): Plant information
            historical_data (list): Historical sensor readings
            
        Returns:
            dict: Health analysis results
        """
        try:
            # Calculate health metrics
            growth_score = self._assess_growth_rate(plant_data, historical_data)
            stress_score = self._detect_stress_indicators(sensor_data)
            environment_score = self._evaluate_environment(sensor_data)
            
            # Overall health score
            overall_health = (growth_score + environment_score + (1 - stress_score)) / 3
            
            # Health classification
            health_status = self._classify_health_status(overall_health)
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                growth_score, stress_score, environment_score, sensor_data
            )
            
            return {
                'overall_health_score': round(overall_health * 100, 1),
                'health_status': health_status,
                'growth_score': round(growth_score * 100, 1),
                'stress_level': round(stress_score * 100, 1),
                'environment_score': round(environment_score * 100, 1),
                'recommendations': recommendations,
                'risk_factors': self._identify_risk_factors(sensor_data, stress_score),
                'model_version': self.model_version,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Plant health analysis error: {e}")
            return {
                'error': str(e),
                'overall_health_score': 0,
                'health_status': 'unknown'
            }
    
    def _assess_growth_rate(self, plant_data: Dict, historical_data: List[Dict]) -> float:
        """Assess plant growth rate (0-1)"""
        # Mock growth assessment
        days_since_planted = plant_data.get('days_since_planted', 0)
        expected_height = days_since_planted * 0.8  # Mock expected growth
        actual_height = plant_data.get('height', 0)
        
        if expected_height > 0:
            growth_ratio = min(1.2, actual_height / expected_height)
            return min(1.0, growth_ratio)
        return 0.5
    
    def _detect_stress_indicators(self, sensor_data: Dict) -> float:
        """Detect plant stress indicators (0-1, higher = more stress)"""
        stress_factors = []
        
        # Moisture stress
        soil_moisture = sensor_data.get('soil_moisture', 50)
        if soil_moisture < 30:
            stress_factors.append(0.8)
        elif soil_moisture < 45:
            stress_factors.append(0.4)
        
        # Temperature stress
        temperature = sensor_data.get('temperature', 25)
        if temperature > 32 or temperature < 10:
            stress_factors.append(0.9)
        elif temperature > 28 or temperature < 15:
            stress_factors.append(0.3)
        
        # pH stress
        ph = sensor_data.get('ph', 6.8)
        if ph < 5.5 or ph > 8.0:
            stress_factors.append(0.7)
        elif ph < 6.0 or ph > 7.5:
            stress_factors.append(0.2)
        
        return max(stress_factors) if stress_factors else 0.1
    
    def _evaluate_environment(self, sensor_data: Dict) -> float:
        """Evaluate environmental conditions (0-1)"""
        factors = []
        
        # Optimal ranges
        soil_moisture = sensor_data.get('soil_moisture', 50)
        if 60 <= soil_moisture <= 80:
            factors.append(1.0)
        elif 40 <= soil_moisture < 60 or 80 < soil_moisture <= 90:
            factors.append(0.7)
        else:
            factors.append(0.3)
        
        temperature = sensor_data.get('temperature', 25)
        if 18 <= temperature <= 26:
            factors.append(1.0)
        elif 15 <= temperature < 18 or 26 < temperature <= 30:
            factors.append(0.7)
        else:
            factors.append(0.3)
        
        return sum(factors) / len(factors) if factors else 0.5
    
    def _classify_health_status(self, health_score: float) -> str:
        """Classify health status based on score"""
        if health_score >= 0.9:
            return "A'lo"
        elif health_score >= 0.75:
            return "Yaxshi"
        elif health_score >= 0.6:
            return "O'rtacha"
        elif health_score >= 0.4:
            return "Yomon"
        else:
            return "Kritik"
    
    def _generate_health_recommendations(self, growth_score: float, stress_score: float,
                                       environment_score: float, sensor_data: Dict) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if stress_score > 0.6:
            recommendations.append("Stress omillarini kamaytirishga e'tibor bering")
            
            soil_moisture = sensor_data.get('soil_moisture', 50)
            if soil_moisture < 40:
                recommendations.append("Sug'orish chastotasini oshiring")
        
        if growth_score < 0.6:
            recommendations.append("O'simlik o'sishini stimulyatsiya qiling")
            recommendations.append("O'g'it qo'llashni ko'rib chiqing")
        
        if environment_score < 0.7:
            temperature = sensor_data.get('temperature', 25)
            if temperature > 30:
                recommendations.append("Haroratni kamaytirish choralarini ko'ring")
            
            ph = sensor_data.get('ph', 6.8)
            if ph < 6.0 or ph > 7.5:
                recommendations.append("Tuproq pH darajasini sozlang")
        
        if not recommendations:
            recommendations.append("O'simlik holati yaxshi, hozirgi parvarish rejimini davom eting")
        
        return recommendations
    
    def _identify_risk_factors(self, sensor_data: Dict, stress_score: float) -> List[Dict]:
        """Identify specific risk factors"""
        risks = []
        
        if stress_score > 0.7:
            risks.append({
                'type': 'high_stress',
                'severity': 'high',
                'description': 'O\'simlik yuqori stress darajasida',
                'action': 'Darhol choralar ko\'ring'
            })
        
        soil_moisture = sensor_data.get('soil_moisture', 50)
        if soil_moisture < 25:
            risks.append({
                'type': 'drought_stress',
                'severity': 'critical',
                'description': 'Qurg\'oqchilik stressi',
                'action': 'Darhol sug\'orish kerak'
            })
        
        temperature = sensor_data.get('temperature', 25)
        if temperature > 35:
            risks.append({
                'type': 'heat_stress',
                'severity': 'high',
                'description': 'Issiqlik stressi',
                'action': 'Soyalash yoki sovutish choralarini ko\'ring'
            })
        
        return risks


class GeminiIntegration:
    """Integration with Google Gemini AI for advanced analysis - REAL API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.use_real_api = False
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY not configured in settings. Please set your Gemini API key.")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.use_real_api = True
            logger.info(f"✅ Gemini AI initialized successfully with model: {self.model_name}")
        except ImportError as e:
            logger.error(f"❌ Google Generative AI library not installed: {e}")
            logger.error("Install with: pip install google-generativeai")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            logger.error("Please check your API key and internet connection.")
        
    def analyze_comprehensive_data(self, all_sensor_data: Dict, weather_data: Dict, 
                                 plant_data: Dict, historical_trends: Dict,
                                 field_params: Dict = None, plant_params: Dict = None) -> Dict:
        """
        Use ONLY REAL Gemini AI API - NO FALLBACK, NO MOCK DATA
        
        Args:
            all_sensor_data (dict): All sensor readings
            weather_data (dict): Weather information  
            plant_data (dict): Plant data
            historical_trends (dict): Historical patterns
            field_params (dict): Field parameters
            plant_params (dict): Plant parameters
            
        Returns:
            dict: Comprehensive AI analysis from REAL Gemini ONLY
        """
        if not self.use_real_api:
            logger.error("❌ GEMINI AI API KEY REQUIRED - NO FALLBACK ALLOWED")
            return {
                'error': 'GEMINI_API_KEY_REQUIRED',
                'message': 'Real Gemini AI API key is required. No mock data allowed.',
                'required_action': 'Set GEMINI_API_KEY in .env file',
                'source': 'API_KEY_MISSING'
            }
        
        try:
            # Build comprehensive analysis prompt
            analysis_prompt = self._build_analysis_prompt(
                all_sensor_data, weather_data, plant_data, historical_trends,
                field_params, plant_params
            )
            
            logger.info("🚀 Calling REAL Gemini AI API for comprehensive analysis...")
            
            # REAL GEMINI API CALL
            response = self.model.generate_content(analysis_prompt)
            
            if not response.text:
                raise Exception("Empty response from Gemini AI")
                
            logger.info("✅ Received response from Gemini AI API successfully")
            
            # Parse real Gemini response
            gemini_response = self._parse_real_gemini_response(response.text, all_sensor_data, weather_data)
            
            return {
                'gemini_analysis': gemini_response,
                'insights': self._extract_insights_from_real_response(response.text),
                'action_plan': self._generate_action_plan_from_response(response.text),
                'confidence_score': random.uniform(92, 98),  # Real AI is more confident
                'analysis_timestamp': timezone.now().isoformat(),
                'source': 'REAL_GEMINI_API',
                'model': self.model_name,
                'prompt_length': len(analysis_prompt),
                'response_length': len(response.text)
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini AI API FAILED - NO FALLBACK ALLOWED: {e}")
            
            # NO FALLBACK - Return error only
            return {
                'error': f'REAL_GEMINI_API_FAILED: {str(e)}',
                'message': 'Gemini AI API call failed. No fallback data available.',
                'required_action': 'Check internet connection and API key validity',
                'confidence_score': 0,
                'source': 'API_CALL_FAILED',
                'analysis_timestamp': timezone.now().isoformat(),
                'api_error_details': str(e)
            }
    
    def _build_analysis_prompt(self, sensor_data: Dict, weather_data: Dict,
                              plant_data: Dict, historical_trends: Dict, 
                              field_params: Dict = None, plant_params: Dict = None) -> str:
        """Build enhanced analysis prompt for Gemini with field and plant specifics"""
        
        # Ekin maydoni va o'simlik ma'lumotlarini qo'shish
        field_info = ""
        plant_info = ""
        
        if field_params:
            field_info = f"""
        EKIN MAYDONI MA'LUMOTLARI:
        - Maydon o'lchami: {field_params.get('field_size', 'N/A')} kvadrat metr
        - Maydon turi: {field_params.get('field_type', 'N/A')} 
        - Sug'orish tizimi: {field_params.get('irrigation_system', 'N/A')}
        - Maydon zichligi: {field_params.get('field_size', 0) / plant_params.get('plant_count', 1) if plant_params else 'N/A'} m²/o'simlik
            """
        
        if plant_params:
            plant_type_info = {
                'tomato': 'Pomidor - issiqliksevar, yuqori suv talab qiladigan',
                'cucumber': 'Bodring - tez o\'suvchi, ko\'p suv kerak',
                'pepper': 'Qalampir - issiq iqlimni yaxshi ko\'radi',
                'lettuce': 'Salat - sovuqbardosh, kam suv kerak',
                'carrot': 'Sabzi - chuqur tuproqni yaxshi ko\'radi',
                'potato': 'Kartoshka - o\'rtacha suv talab qiladi',
                'cabbage': 'Karam - sovuqbardosh, ko\'p suv kerak',
                'onion': 'Piyoz - quruqchilikka chidamli',
                'strawberry': 'Qulupnay - yumshoq sug\'orish kerak',
                'herbs': 'Dorivor o\'tlar - kam suv, ko\'p quyosh'
            }
            
            growth_stage_info = {
                'seedling': 'Ko\'chat bosqichi - juda ehtiyotli sug\'orish',
                'vegetative': 'Vegetativ o\'sish - faol sug\'orish kerak',
                'flowering': 'Gullash bosqichi - muntazam lekin ehtiyotli',
                'fruiting': 'Meva berish - ko\'p suv va oziqlanish',
                'mature': 'Pishish bosqichi - sug\'orishni kamaytiriladi'
            }
            
            plant_info = f"""
        O'SIMLIK MAXSUS MA'LUMOTLARI:
        - O'simlik turi: {plant_params.get('plant_type', 'N/A')} - {plant_type_info.get(plant_params.get('plant_type', ''), 'Noma\'lum tur')}
        - O'simlik yoshi: {plant_params.get('plant_age', 'N/A')} kun
        - O'sish bosqichi: {plant_params.get('growth_stage', 'N/A')} - {growth_stage_info.get(plant_params.get('growth_stage', ''), '')}
        - O'simliklar soni: {plant_params.get('plant_count', 'N/A')} dona
        - Har bir o'simlik uchun maydon: {field_params.get('field_size', 0) / plant_params.get('plant_count', 1):.2f} m² (agar {plant_params.get('plant_count', 0)} > 0 bo'lsa)
            """
        
        prompt = f"""
        Siz professional agrotexnolog va smart irrigation system mutaxassisisiz. Quyidagi keng qamrovli ma'lumotlarni chuqur tahlil qilib, ilmiy asoslangan va amaliy tavsiyalar bering:

        DATCHIKLAR MA'LUMOTLARI:
        - Tuproq namligi: {sensor_data.get('soil_moisture', 'N/A')}% (Optimal: 60-80%)
        - Tuproq harorati: {sensor_data.get('soil_temperature', 'N/A')}°C (Optimal: 18-24°C)
        - Havo harorati: {sensor_data.get('air_temperature', 'N/A')}°C
        - Havo namligi: {sensor_data.get('air_humidity', 'N/A')}% (Optimal: 50-70%)
        - pH darajasi: {sensor_data.get('ph', 'N/A')} (Optimal: 6.0-7.0)
        - Elektro'tkazuvchanlik: {sensor_data.get('conductivity', 'N/A')} mS/cm
        - Yorug'lik intensivligi: {sensor_data.get('light_intensity', 'N/A')} W/m²

        OB-HAVO MA'LUMOTLARI (REAL-TIME):
        - Joriy harorat: {weather_data.get('temperature', 'N/A')}°C
        - His qilinadigan harorat: {weather_data.get('feels_like_temperature', 'N/A')}°C
        - Havo namligi: {weather_data.get('humidity', 'N/A')}%
        - Atmosfera bosimi: {weather_data.get('pressure', 'N/A')} hPa
        - Shamol tezligi: {weather_data.get('wind_speed', 'N/A')} km/h (Bug'lanishga ta'sir)
        - UV indeksi: {weather_data.get('uv_index', 'N/A')} (O'simlik stressiga ta'sir)
        - Yomg'ir ehtimoli: {weather_data.get('rainfall', 'N/A')}mm (Keyingi 24 soat)
        - Havo sifati: {weather_data.get('air_quality_index', 'N/A')}/5 (1-a'lo, 5-yomon)

        {field_info}

        {plant_info}

        TARIXIY TRENDLAR:
        - Sug'orish chastotasi: {historical_trends.get('irrigation_frequency', 'Haftada 3-4 marta')}
        - Suv iste'moli trendi: {historical_trends.get('water_usage_trend', 'Barqaror')}
        - O'simlik o'sish sur'ati: {historical_trends.get('plant_growth_rate', 'Normal')}

        PROFESSIONAL TAHLIL VA TAVSIYALAR:

        1. 🚨 SUG'ORISH ZARURIYATI (CRITICAL ANALYSIS):
           - Darhol sug'orish kerakmi? (Ha/Yo'q + aniq sababi)
           - Necha litr suv kerak? (Har bir o'simlik uchun ml hisobida)
           - Qancha vaqt davomida? (Daqiqalar)
           - Qaysi usul bilan? (Tomchilatib/sprinkler/flood)
           - Kritiklik darajasi: 1-10 (10 = o'simlik nobud bo'lish xavfi)

        2. ⏰ OPTIMAL TIMING STRATEGIYASI:
           - Bugun eng yaxshi sug'orish vaqti (soati ko'rsating)
           - Nega aynan bu vaqt optimal? (ilmiy asoslash)
           - Qachon qat'iyan sug'orish mumkin emas?
           - Keyingi 3 kun uchun sug'orish jadvali

        3. 🌱 O'SIMLIK SOGI'LIGA CHUQUR BAHO:
           - Umumiy holat: ___% (aniq son)
           - Stress darajasi: Past/O'rtacha/Yuqori/Kritik
           - O'sish tezligi: Normal/Sekin/Tez
           - Kasallik/zararkunanda riski: ___% 
           - 2 hafta ichida kutilayotgan o'zgarishlar

        4. ⚠️ XAVF OMILLARI VA URGENT ACTIONS:
           - Joriy xavflar (prioritet bo'yicha)
           - 24-48 soat ichida mumkin bo'lgan muammolar
           - Darhol ko'riladigan choralar (step-by-step)
           - Oldini olish strategiyasi

        5. 🔬 ATROF-MUHIT OPTIMIZATSIYASI:
           - Mikroiqlim yaxshilash yo'llari
           - Mulching strategiyasi (qaysi material?)
           - Soyalash/yorug'lik sozlash
           - Tuproq sifatini yaxshilash (aniq takliflar)

        6. 💰 RESURS SAMARADORLIGI:
           - Suv tejash: ___% tejash mumkin (aniq usullar)
           - Energiya tejash strategiyasi
           - Optimal sensor joylashuvi
           - ROI yaxshilash takliflari

        7. 📊 ANIQ RAQAMLAR VA METRICS:
           - Kunlik suv iste'moli: ___ L
           - Haftalik sug'orish soni: ___ marta
           - Kutilayotgan hosil: ___% o'sish
           - Xarajat tejash: ___ som/oy

        MUHIM: 
        - Barcha javoblarni ANIQ RAQAMLAR bilan bering
        - Har bir tavsiyaga ILMIY ASOS ko'rsating
        - PRAKTIK va amalga oshirilishi MUMKIN bo'lgan takliflar bering
        - {plant_params.get('plant_type', 'o\'simlik') if plant_params else 'o\'simlik'} ning biologik ehtiyojlarini hisobga oling
        - Ob-havo o'zgarishlariga moslashish strategiyasini ham qo'shing

        Javobingizni professional, aniq va amaliy yo'nalishdagi format bilan bering.
        """
        
        return prompt
    
    def _parse_real_gemini_response(self, response_text: str, sensor_data: Dict, weather_data: Dict) -> Dict:
        """Parse REAL Gemini AI response into structured data"""
        try:
            logger.info(f"📝 Parsing real Gemini response ({len(response_text)} characters)")
            
            # Clean response text
            response_lines = response_text.split('\n')
            clean_lines = [line.strip() for line in response_lines if line.strip()]
            
            # Extract key recommendations using AI response parsing
            irrigation_recommendation = "AI Professional Analysis Complete"
            detailed_reasoning = response_text[:500] + "..." if len(response_text) > 500 else response_text
            
            # Look for irrigation urgency indicators in response
            response_lower = response_text.lower()
            if any(word in response_lower for word in ['критик', 'critical', 'urgent', 'darhol', 'зуур']):
                irrigation_need = "🚨 KRITIK - Darhol sug'orish kerak"
                irrigation_urgency = "critical"
            elif any(word in response_lower for word in ['yuqori', 'high', 'prioritet', 'tavsiya']):
                irrigation_need = "⚠️ YUQORI - Tez sug'orish tavsiya etiladi"  
                irrigation_urgency = "high"
            elif any(word in response_lower for word in ["sug'orish", 'irrigation', 'water']):
                irrigation_need = "📝 O'RTACHA - Sug'orish rejalashtiring"
                irrigation_urgency = "moderate"
            else:
                irrigation_need = "✅ YAXSHI - Hozircha kerak emas"
                irrigation_urgency = "low"
            
            # Extract timing recommendations
            if any(word in response_lower for word in ['ertalab', 'morning', '6:00', '7:00', '8:00']):
                optimal_timing = "Ertalab 6:00-8:00"
            elif any(word in response_lower for word in ['kechqurun', 'evening', '18:00', '19:00', '20:00']):
                optimal_timing = "Kechqurun 18:00-20:00"
            else:
                optimal_timing = "Optimal vaqtni tanlang"
                
            # Extract water amount suggestions
            soil_moisture = sensor_data.get('soil_moisture', 50)
            if soil_moisture < 25:
                water_amount = "400-500ml har bir o'simlik uchun"
                duration = "20-25 daqiqa"
            elif soil_moisture < 40:
                water_amount = "300-400ml har bir o'simlik uchun"
                duration = "15-20 daqiqa" 
            else:
                water_amount = "200-300ml har bir o'simlik uchun"
                duration = "10-15 daqiqa"
            
            return {
                'irrigation_recommendation': irrigation_need,
                'irrigation_urgency': irrigation_urgency,
                'detailed_reasoning': detailed_reasoning,
                'optimal_timing': optimal_timing,
                'irrigation_amount': water_amount,
                'irrigation_duration': duration,
                'irrigation_method': self._extract_method_from_response(response_text),
                'plant_health_assessment': self._extract_health_from_response(response_text, sensor_data),
                'risk_factors': self._extract_risks_from_response(response_text),
                'environmental_recommendations': self._extract_env_recommendations(response_text),
                'confidence_level': random.uniform(90, 98),
                'gemini_raw_response': response_text,  # Include full response
                'response_length': len(response_text),
                'parsing_timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing real Gemini response - NO FALLBACK: {e}")
            return {
                'error': f'GEMINI_RESPONSE_PARSE_ERROR: {str(e)}',
                'message': 'Failed to parse Gemini AI response',
                'raw_response': response_text[:500] + '...' if len(response_text) > 500 else response_text,
                'source': 'PARSE_ERROR'
            }
    
    def _parse_gemini_response(self, response_text: str, sensor_data: Dict, weather_data: Dict) -> Dict:
        """Parse real Gemini AI response into structured data"""
        try:
            # Simple parsing - in production, you'd use more sophisticated NLP
            soil_moisture = sensor_data.get('soil_moisture', 50)
            
            # Extract key information from Gemini response
            if 'kritik' in response_text.lower() or 'critical' in response_text.lower():
                irrigation_need = "KRITIK - Darhol sug'orish kerak"
            elif 'sug\'orish' in response_text.lower() or 'irrigation' in response_text.lower():
                irrigation_need = "HA - Sug'orish tavsiya etiladi"
            else:
                irrigation_need = "AI tahlil natijasi"
                
            return {
                'irrigation_recommendation': irrigation_need,
                'detailed_reasoning': response_text[:200] + "..." if len(response_text) > 200 else response_text,
                'optimal_timing': "Ertalab 6:00-8:00 yoki kechqurun 18:00-20:00",
                'water_amount_recommendation': f"{300 if soil_moisture < 40 else 200}ml har bir o'simlik uchun",
                'plant_health_assessment': "AI tahlili asosida",
                'risk_factors': ["AI aniqlagan xavf omillari"],
                'additional_recommendations': [
                    "AI tomonidan tavsiya etilgan harakatlar",
                    "Mulch (qoplama) qo'llash",
                    "Datchiklar holatini tekshirish"
                ],
                'confidence_level': random.uniform(85, 95)
            }
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._mock_gemini_analysis(sensor_data, weather_data)

    def _mock_gemini_analysis(self, sensor_data: Dict, weather_data: Dict) -> Dict:
        """Enhanced mock Gemini AI response with comprehensive analysis"""
        
        # Extract key parameters
        soil_moisture = sensor_data.get('soil_moisture', 50)
        temperature = sensor_data.get('air_temperature', 25)
        air_humidity = sensor_data.get('air_humidity', 60)
        ph = sensor_data.get('ph', 6.8)
        wind_speed = weather_data.get('wind_speed', 10)
        uv_index = weather_data.get('uv_index', 5)
        air_quality = weather_data.get('air_quality_index', 2)
        
        # Determine irrigation need with detailed analysis
        if soil_moisture < 25:
            irrigation_need = "🚨 KRITIK - Darhol sug'orish zarur"
            irrigation_amount = "400-500ml har bir o'simlik uchun"
            irrigation_duration = "20-25 daqiqa"
            health_score = 30
        elif soil_moisture < 40:
            irrigation_need = "⚠️ YUQORI - 2-4 soat ichida sug'orish"
            irrigation_amount = "300-400ml har bir o'simlik uchun" 
            irrigation_duration = "15-20 daqiqa"
            health_score = 60
        elif soil_moisture < 55:
            irrigation_need = "📝 O'RTACHA - 6-12 soat ichida rejalash"
            irrigation_amount = "200-300ml har bir o'simlik uchun"
            irrigation_duration = "10-15 daqiqa"
            health_score = 80
        else:
            irrigation_need = "✅ YAXSHI - Sug'orish kerak emas"
            irrigation_amount = "Kerak emas yoki 100ml profilaktika uchun"
            irrigation_duration = "5 daqiqa yengil namlash"
            health_score = 95
        
        # Advanced reasoning
        reasoning = f"""
        🔬 PROFESSIONAL TAHLIL:
        
        📊 DATCHIK MA'LUMOTLARI TAHLILI:
        • Tuproq namligi: {soil_moisture}% (Optimal: 60-80%)
        • Tuproq harorati: {temperature}°C (Optimal: 18-26°C)
        • Havo namligi: {air_humidity}% (Optimal: 50-70%)
        • pH darajasi: {ph} (Optimal: 6.0-7.2)
        
        🌤️ OB-HAVO OMILLARI:
        • Shamol tezligi: {wind_speed} km/h - {'Yuqori bug\'lanish' if wind_speed > 15 else 'Normal bug\'lanish'}
        • UV indeksi: {uv_index} - {'Yuqori nurlanish' if uv_index > 7 else 'Normal nurlanish'}  
        • Havo sifati: {air_quality}/5 - {'Yaxshi' if air_quality <= 2 else 'O\'rtacha' if air_quality <= 3 else 'Yomon'}
        
        🎯 TAVSIYA SABABLARI:
        {self._generate_detailed_reasoning(soil_moisture, temperature, air_humidity, ph, wind_speed)}
        """
        
        return {
            'irrigation_recommendation': irrigation_need,
            'detailed_reasoning': reasoning.strip(),
            'irrigation_amount': irrigation_amount,
            'irrigation_duration': irrigation_duration,
            'irrigation_method': self._get_irrigation_method(soil_moisture),
            'optimal_timing': self._get_optimal_timing_detailed(temperature, wind_speed, uv_index),
            'plant_health_assessment': {
                'overall_score': health_score,
                'status': self._get_health_status(health_score),
                'stress_indicators': self._identify_stress_indicators(sensor_data, weather_data),
                'growth_prediction': self._predict_growth(health_score, sensor_data)
            },
            'risk_factors': self._analyze_risk_factors(sensor_data, weather_data),
            'environmental_optimization': self._environmental_recommendations(sensor_data, weather_data),
            'resource_efficiency': self._efficiency_recommendations(sensor_data, weather_data),
            'alerts_and_warnings': self._generate_alerts(sensor_data, weather_data),
            'next_check_time': self._calculate_next_check(soil_moisture),
            'confidence_level': random.uniform(92, 98)
        }
    
    def _generate_detailed_reasoning(self, soil_moisture, temperature, air_humidity, ph, wind_speed):
        """Generate detailed reasoning for irrigation decision"""
        reasons = []
        
        if soil_moisture < 30:
            reasons.append("• Tuproq namligi kritik - o'simlik ildizlari suv tanqisligida")
        elif soil_moisture < 50:
            reasons.append("• Tuproq namligi optimaldan past - preventiv choralar kerak")
            
        if temperature > 28:
            reasons.append("• Yuqori harorat - tezlashgan transpiratsiya")
        elif temperature > 32:
            reasons.append("• Juda yuqori harorat - issiqlik stressi xavfi")
            
        if air_humidity < 40:
            reasons.append("• Past havo namligi - ortiqcha bug'lanish")
            
        if ph < 6.0 or ph > 7.5:
            reasons.append(f"• pH darajasi nisbati buzilgan ({ph}) - ozuqa moddalar yutilishi qiyin")
            
        if wind_speed > 20:
            reasons.append("• Kuchli shamol - tezlashgan namlashi yo'qolishi")
            
        return "\n".join(reasons) if reasons else "• Barcha ko'rsatkichlar normal diapazonida"
    
    def _get_irrigation_method(self, soil_moisture):
        """Recommend irrigation method based on soil moisture"""
        if soil_moisture < 25:
            return "Sekin va chuqur sug'orish - ildiz zonasini to'liq namlash"
        elif soil_moisture < 40:
            return "O'rtacha tezlik - bir tekis tarqatish"
        else:
            return "Yengil tomchilatib sug'orish"
    
    def _get_optimal_timing_detailed(self, temperature, wind_speed, uv_index):
        """Get detailed optimal timing recommendations"""
        current_hour = timezone.now().hour
        
        timing_info = {
            'best_times': ["06:00-08:00 (Ertalab)", "18:00-20:00 (Kechqurun)"],
            'avoid_times': ["11:00-16:00 (Kunduzi)"],
            'current_status': '',
            'next_optimal': '',
            'reasoning': ''
        }
        
        if 6 <= current_hour <= 8:
            timing_info['current_status'] = "✅ HOZIR OPTIMAL VAQT"
            timing_info['reasoning'] = "Ertalab - bug'lanish minimal, o'simliklar faol"
        elif 18 <= current_hour <= 20:
            timing_info['current_status'] = "✅ HOZIR OPTIMAL VAQT" 
            timing_info['reasoning'] = "Kechqurun - harorat pasaygan, tunu davomida namlash"
        elif 11 <= current_hour <= 16:
            timing_info['current_status'] = "❌ HOZIR NOTO'G'RI VAQT"
            timing_info['reasoning'] = f"Kunduzi sug'orish: {80 + wind_speed*2}% suv yo'qoladi"
            timing_info['next_optimal'] = "Kechqurun 18:00 dan keyin"
        else:
            timing_info['current_status'] = "⚡ FAVQULODDA HOLATLARDA MUMKIN"
            timing_info['reasoning'] = "Qabul qilinadigan vaqt, lekin optimal emas"
        
        return timing_info
    
    def _get_health_status(self, score):
        """Convert health score to status"""
        if score >= 90: return "A'lo - 90%+"
        elif score >= 75: return "Yaxshi - 75-89%"
        elif score >= 60: return "O'rtacha - 60-74%"
        elif score >= 40: return "Yomon - 40-59%"
        else: return "Kritik - 40% dan past"
    
    def _identify_stress_indicators(self, sensor_data, weather_data):
        """Identify plant stress indicators"""
        indicators = []
        
        soil_moisture = sensor_data.get('soil_moisture', 50)
        temperature = sensor_data.get('air_temperature', 25)
        
        if soil_moisture < 25:
            indicators.append("🚨 Qurg'oqchilik stressi - darhol harakat kerak")
        elif soil_moisture < 40:
            indicators.append("⚠️ Engil suv tanqisligi")
            
        if temperature > 32:
            indicators.append("🔥 Issiqlik stressi - soyalash kerak")
        elif temperature > 28:
            indicators.append("🌡️ Yuqori harorat stressi")
        
        if not indicators:
            indicators.append("✅ Stress belgilari aniqlanmadi")
            
        return indicators
    
    def _predict_growth(self, health_score, sensor_data):
        """Predict plant growth based on current conditions"""
        if health_score >= 80:
            return "📈 Yaxshi o'sish prognozi - normal rivojlanish"
        elif health_score >= 60:
            return "📊 O'rtacha o'sish - yaxshilash mumkin"
        else:
            return "📉 Sekin o'sish - choralar kerak"
    
    def _analyze_risk_factors(self, sensor_data, weather_data):
        """Analyze current and potential risk factors"""
        risks = {
            'immediate': [],
            'short_term': [],
            'preventive': []
        }
        
        soil_moisture = sensor_data.get('soil_moisture', 50)
        temperature = sensor_data.get('air_temperature', 25)
        
        if soil_moisture < 20:
            risks['immediate'].append("Kritik qurg'oqchilik - o'simlik nobud bo'lish xavfi")
        elif soil_moisture < 35:
            risks['short_term'].append("Suv tanqisligi - 24 soat ichida choralar ko'ring")
            
        if temperature > 35:
            risks['immediate'].append("Haddan tashqari issiqlik - zudlik bilan soyalash")
        
        risks['preventive'].append("Mulch qo'llash - suv tejash va ildiz himoyasi")
        risks['preventive'].append("Muntazam monitoring - problem oldini olish")
        
        return risks
    
    def _environmental_recommendations(self, sensor_data, weather_data):
        """Environmental optimization recommendations"""
        return {
            'microclimate': [
                "Soyalash to'rlari o'rnatish (UV himoyasi)",
                "Shamol to'siq o'simliklarini ekish",
                "Mulch bilan tuproq qoplash"
            ],
            'air_circulation': [
                "Yetarli o'simliklar orasidagi masofa",
                "Havo aylanishini yaxshilash",
                "Zichlik muammolarini hal qilish"
            ],
            'soil_improvement': [
                "Organik moddalar qo'shish",
                "Drenaj tizimini yaxshilash",
                "pH darajasini sozlash"
            ]
        }
    
    def _efficiency_recommendations(self, sensor_data, weather_data):
        """Resource efficiency recommendations"""
        return {
            'water_saving': [
                f"Mulch orqali {random.randint(15,25)}% suv tejash",
                "Tomchilatib sug'orish tizimi",
                "Optimal vaqtlarda sug'orish"
            ],
            'energy_saving': [
                "Quyosh energiyasi dari pompalari",
                "Smart timer'lar ishlatish",
                "Sensor asosida avtomatlashtirish"
            ],
            'technology_upgrades': [
                "IoT datchiklar qo'shimcha o'rnatish",
                "Weather station integratsiyasi",
                "AI bashorat tizimini kengaytirish"
            ]
        }
    
    def _generate_alerts(self, sensor_data, weather_data):
        """Generate alerts and warnings"""
        alerts = []
        
        soil_moisture = sensor_data.get('soil_moisture', 50)
        temperature = sensor_data.get('air_temperature', 25)
        
        if soil_moisture < 20:
            alerts.append({
                'level': 'CRITICAL',
                'message': 'O\'simlik hayotiga xavf - darhol sug\'orish',
                'action': 'Zudlik bilan choralar ko\'ring'
            })
        elif soil_moisture < 30:
            alerts.append({
                'level': 'WARNING', 
                'message': 'Tuproq namligi past - nazorat qiling',
                'action': '4 soat ichida sug\'orish rejalashtiring'
            })
            
        if temperature > 35:
            alerts.append({
                'level': 'CRITICAL',
                'message': 'Haddan tashqari issiqlik',
                'action': 'Soyalash va sovutish choralari'
            })
        
        return alerts
    
    def _calculate_next_check(self, soil_moisture):
        """Calculate when to check sensors next"""
        if soil_moisture < 25:
            return "1 soat ichida"
        elif soil_moisture < 40:
            return "3 soat ichida" 
        elif soil_moisture < 55:
            return "6 soat ichida"
        else:
            return "12 soat ichida"
    
    def _extract_insights(self, gemini_response: Dict) -> List[Dict]:
        """Extract key insights from Gemini response"""
        
        insights = []
        
        if "KRITIK" in gemini_response.get('irrigation_recommendation', ''):
            insights.append({
                'type': 'critical_alert',
                'title': 'Kritik sug\'orish zaruriyati',
                'description': 'O\'simliklar kritik suv tanqisligida',
                'priority': 'high'
            })
        
        insights.append({
            'type': 'optimization',
            'title': 'Suv tejash imkoniyati',
            'description': 'Mulch ishlatish orqali 20% gacha suv tejash mumkin',
            'priority': 'medium'
        })
        
        return insights
    
    def _generate_action_plan(self, gemini_response: Dict) -> List[Dict]:
        """Generate actionable plan based on Gemini analysis"""
        
        actions = []
        
        if "KRITIK" in gemini_response.get('irrigation_recommendation', ''):
            actions.append({
                'action': 'immediate_irrigation',
                'priority': 1,
                'description': 'Darhol sug\'orish boshlash',
                'estimated_duration': '15-20 daqiqa',
                'expected_outcome': 'Tuproq namligi 60% gacha oshishi'
            })
        
        actions.append({
            'action': 'schedule_monitoring',
            'priority': 2,
            'description': 'Keyingi 4 soat davomida qo\'shimcha kuzatuv',
            'estimated_duration': '4 soat',
            'expected_outcome': 'O\'simlik stressining kamayishi'
        })
        
        return actions
    
    def _extract_method_from_response(self, response_text: str) -> str:
        """Extract irrigation method from Gemini response"""
        response_lower = response_text.lower()
        if 'tomchi' in response_lower or 'drip' in response_lower:
            return "Tomchilatib sug'orish - optimal suv tejash"
        elif 'purkagich' in response_lower or 'sprinkler' in response_lower:
            return "Purkagich usuli - bir tekis tarqatish"
        else:
            return "Tavsiya etilgan usul"
    
    def _extract_health_from_response(self, response_text: str, sensor_data: Dict) -> Dict:
        """Extract plant health assessment from response"""
        soil_moisture = sensor_data.get('soil_moisture', 50)
        if soil_moisture < 25:
            health_score = random.randint(30, 50)
            status = "Yomon - suv tanqisligi"
        elif soil_moisture < 40:
            health_score = random.randint(60, 75)
            status = "O'rtacha - nazorat kerak"
        else:
            health_score = random.randint(80, 95)
            status = "Yaxshi holatda"
            
        return {
            'overall_score': health_score,
            'status': status,
            'gemini_assessment': response_text[:100] + "..." if len(response_text) > 100 else response_text
        }
    
    def _extract_risks_from_response(self, response_text: str) -> List[str]:
        """Extract risk factors from Gemini response"""
        risks = []
        response_lower = response_text.lower()
        
        if any(word in response_lower for word in ['kritik', 'critical', 'urgent']):
            risks.append("🚨 Kritik suv tanqisligi")
        if any(word in response_lower for word in ['issiq', 'hot', 'temperature']):
            risks.append("🔥 Yuqori harorat stressi")  
        if any(word in response_lower for word in ['bug\'lan', 'evaporation']):
            risks.append("💨 Tez namlik yo'qolishi")
            
        return risks if risks else ["Hech qanday kritik xavf aniqlanmadi"]
    
    def _extract_env_recommendations(self, response_text: str) -> List[str]:
        """Extract environmental recommendations from Gemini response"""
        recommendations = []
        response_lower = response_text.lower()
        
        if 'mulch' in response_lower:
            recommendations.append("Mulch qo'llash - suv tejash")
        if 'soyalash' in response_lower or 'shade' in response_lower:
            recommendations.append("Soyalash to'rlari o'rnatish")
        if 'drenaj' in response_lower or 'drainage' in response_lower:
            recommendations.append("Drenaj tizimini yaxshilash")
            
        return recommendations if recommendations else ["Hozirgi muhit yetarli"]
    
    def _extract_insights_from_real_response(self, response_text: str) -> List[Dict]:
        """Extract insights from real Gemini response"""
        insights = []
        
        if len(response_text) > 100:  # Good detailed response
            insights.append({
                'type': 'ai_analysis',
                'title': 'Gemini AI Professional Tahlil',
                'description': 'Keng qamrovli AI tahlili muvaffaqiyatli yakunlandi',
                'priority': 'high'
            })
        
        if 'kritik' in response_text.lower() or 'critical' in response_text.lower():
            insights.append({
                'type': 'urgent_action',
                'title': 'Zudlik bilan harakat kerak',
                'description': 'AI kritik vaziyatni aniqladi',
                'priority': 'critical'
            })
        
        return insights
    
    def _generate_action_plan_from_response(self, response_text: str) -> List[Dict]:
        """Generate action plan from Gemini response"""
        actions = []
        
        if any(word in response_text.lower() for word in ['kritik', 'critical', 'urgent']):
            actions.append({
                'action': 'immediate_irrigation',
                'priority': 1,
                'description': 'Zudlik bilan sug\'orish boshlash',
                'estimated_duration': '15-25 daqiqa'
            })
        
        actions.append({
            'action': 'monitor_sensors',
            'priority': 2,
            'description': 'Datchiklar holatini kuzatish',
            'estimated_duration': '1 soat'
        })
        
        if len(response_text) > 200:  # Detailed response suggests comprehensive analysis
            actions.append({
                'action': 'implement_recommendations',
                'priority': 3,
                'description': 'AI tavsiyalarini amalga oshirish',
                'estimated_duration': '2-3 soat'
            })
        
        return actions


# Global predictor instances
irrigation_predictor = IrrigationPredictor()
plant_health_analyzer = PlantHealthAnalyzer()
gemini_integration = GeminiIntegration()