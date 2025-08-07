"""
ESP32 Controller Module
This module handles communication with ESP32 devices for irrigation control.
"""

import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class ESP32Controller:
    """Controller class for ESP32 communication"""
    
    def __init__(self, esp32_ip: str, port: int = 80):
        self.esp32_ip = esp32_ip
        self.port = port
        self.base_url = f"http://{esp32_ip}:{port}"
        
    def send_command(self, endpoint: str, data: Optional[Dict] = None, timeout: int = 10) -> Dict:
        """
        Send command to ESP32 device
        
        Args:
            endpoint (str): API endpoint on ESP32
            data (dict, optional): Data to send
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: Response from ESP32
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            
            if data:
                response = requests.post(url, json=data, timeout=timeout)
            else:
                response = requests.get(url, timeout=timeout)
            
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json() if response.content else {},
                'status_code': response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ESP32 communication error: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }
    
    def start_pump(self, pump_id: int, duration_minutes: int) -> Dict:
        """
        Start water pump
        
        Args:
            pump_id (int): Pump identifier (1-4)
            duration_minutes (int): Duration to run pump
            
        Returns:
            dict: Operation result
        """
        data = {
            'pump_id': pump_id,
            'duration': duration_minutes,
            'action': 'start'
        }
        return self.send_command('pump/control', data)
    
    def stop_pump(self, pump_id: int) -> Dict:
        """
        Stop water pump
        
        Args:
            pump_id (int): Pump identifier (1-4)
            
        Returns:
            dict: Operation result
        """
        data = {
            'pump_id': pump_id,
            'action': 'stop'
        }
        return self.send_command('pump/control', data)
    
    def get_pump_status(self) -> Dict:
        """
        Get status of all pumps
        
        Returns:
            dict: Pump status information
        """
        return self.send_command('pump/status')
    
    def get_sensor_readings(self) -> Dict:
        """
        Get current sensor readings from ESP32
        
        Returns:
            dict: Sensor data
        """
        return self.send_command('sensors/read')
    
    def calibrate_sensor(self, sensor_id: str) -> Dict:
        """
        Calibrate a specific sensor
        
        Args:
            sensor_id (str): Sensor identifier
            
        Returns:
            dict: Calibration result
        """
        data = {'sensor_id': sensor_id}
        return self.send_command('sensors/calibrate', data)
    
    def get_system_info(self) -> Dict:
        """
        Get ESP32 system information
        
        Returns:
            dict: System information
        """
        return self.send_command('system/info')
    
    def reset_system(self) -> Dict:
        """
        Reset ESP32 system
        
        Returns:
            dict: Reset result
        """
        return self.send_command('system/reset', {'action': 'reset'})


class ESP32Manager:
    """Manager class for multiple ESP32 devices"""
    
    def __init__(self):
        self.controllers: Dict[str, ESP32Controller] = {}
        self._load_esp32_devices()
    
    def _load_esp32_devices(self):
        """Load ESP32 device configurations from settings"""
        # In a real implementation, this would load from database or settings
        esp32_devices = [
            {'name': 'main_controller', 'ip': '192.168.1.100'},
            {'name': 'zone_a_controller', 'ip': '192.168.1.101'},
            {'name': 'zone_b_controller', 'ip': '192.168.1.102'},
        ]
        
        for device in esp32_devices:
            self.controllers[device['name']] = ESP32Controller(device['ip'])
    
    def get_controller(self, name: str) -> Optional[ESP32Controller]:
        """Get ESP32 controller by name"""
        return self.controllers.get(name)
    
    def broadcast_command(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Dict]:
        """
        Send command to all ESP32 devices
        
        Args:
            endpoint (str): API endpoint
            data (dict, optional): Data to send
            
        Returns:
            dict: Results from all devices
        """
        results = {}
        for name, controller in self.controllers.items():
            results[name] = controller.send_command(endpoint, data)
        return results
    
    def start_irrigation_zone(self, zone_name: str, pump_id: int, duration_minutes: int) -> Dict:
        """
        Start irrigation in a specific zone
        
        Args:
            zone_name (str): Zone name (matches controller name)
            pump_id (int): Pump identifier
            duration_minutes (int): Duration to run
            
        Returns:
            dict: Operation result
        """
        controller = self.get_controller(zone_name)
        if not controller:
            return {'success': False, 'error': f'Controller {zone_name} not found'}
        
        return controller.start_pump(pump_id, duration_minutes)
    
    def stop_all_irrigation(self) -> Dict[str, Dict]:
        """
        Stop all irrigation pumps
        
        Returns:
            dict: Results from all controllers
        """
        results = {}
        for name, controller in self.controllers.items():
            # Stop all pumps (assuming 4 pumps per controller)
            for pump_id in range(1, 5):
                results[f'{name}_pump_{pump_id}'] = controller.stop_pump(pump_id)
        return results
    
    def get_all_sensor_readings(self) -> Dict[str, Dict]:
        """
        Get sensor readings from all ESP32 devices
        
        Returns:
            dict: Sensor data from all devices
        """
        results = {}
        for name, controller in self.controllers.items():
            results[name] = controller.get_sensor_readings()
        return results
    
    def get_system_health(self) -> Dict[str, Dict]:
        """
        Check health of all ESP32 devices
        
        Returns:
            dict: Health status of all devices
        """
        results = {}
        for name, controller in self.controllers.items():
            try:
                info = controller.get_system_info()
                results[name] = {
                    'online': info['success'],
                    'info': info.get('data', {}),
                    'last_check': None  # Would be timestamp in real implementation
                }
            except Exception as e:
                results[name] = {
                    'online': False,
                    'error': str(e),
                    'last_check': None
                }
        return results


# Global ESP32 manager instance
esp32_manager = ESP32Manager()