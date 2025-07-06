from PyQt6.QtCore import QThread, pyqtSignal
import requests

class PlayerCountThread(QThread):
    update_signal = pyqtSignal(str)
    
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
        self._running = True
        
    def run(self):
        while self._running:
            self.fetch_player_count()
            self.msleep(5000)
            
    def fetch_player_count(self):
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                count = response.json().get('count', '--')
                self.update_signal.emit(str(count))
        except Exception:
            self.update_signal.emit('--')
            
    def stop(self):
        self._running = False
        self.wait()