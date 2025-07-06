import requests
from requests.exceptions import RequestException
from config import GITHUB_TOKEN, REPO
import logging

logger = logging.getLogger(__name__)

def check_update(current_version: str) -> str | None:
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["tag_name"] != current_version:
            return data["assets"][0]["browser_download_url"]
        return None
    except RequestException as e:  # Spezifischerer Fehler
        logger.error(f"Update check failed (Network): {str(e)}")
    except (KeyError, IndexError) as e:
        logger.error(f"Update check failed (Invalid API response): {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during update check: {str(e)}")
    return None