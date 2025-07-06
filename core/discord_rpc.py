from pypresence import Presence
import time
import logging

class DiscordRPC:
    def __init__(self):
        self.client_id = '1390945769879506984'
        self.RPC = None
        self.start_time = int(time.time())
        self.connected = False

    def connect(self):
        try:
            self.RPC = Presence(self.client_id)
            self.RPC.connect()
            self.connected = True
            logging.info("Discord RPC connected successfully")
        except Exception as e:
            logging.error(f"Discord RPC connection failed: {str(e)}")
            self.connected = False

    def update_presence(self, state="In Launcher", details="EternityGlow"):
        if not self.connected:
            return

        try:
            self.RPC.update(
                state=state,
                details=details,
                start=self.start_time,
                large_image="menu-background2x",
                large_text="EternityGlow Launcher",
                small_image="osu",  # Optional: kleines Bild
                small_text="osu! Client",
                buttons=[{"label": "Download", "url": "https://eternityglow.de"}]
            )
        except Exception as e:
            logging.error(f"Discord RPC update failed: {str(e)}")

    def close(self):
        if self.connected:
            try:
                self.RPC.close()
                logging.info("Discord RPC disconnected")
            except Exception as e:
                logging.error(f"Discord RPC disconnect failed: {str(e)}")