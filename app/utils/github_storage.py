import os
import base64
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubStorage:
    """
    Almacena datos en GitHub cuando el filesystem no es persistente (Vercel)
    """

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPO", "Juanlucuenca/daily-scrapper")
        self.branch = "main"
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"

    def update_csv_on_github(self, file_path: str, content: str, message: str):
        """
        Actualiza un archivo CSV en GitHub
        """
        if not self.token:
            logger.warning("GITHUB_TOKEN not set, skipping GitHub update")
            return False

        try:
            url = f"{self.base_url}/{file_path}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Obtener SHA del archivo actual
            response = requests.get(url, headers=headers, params={"ref": self.branch})
            sha = response.json().get("sha") if response.status_code == 200 else None

            # Preparar contenido
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')

            # Actualizar archivo
            data = {
                "message": message,
                "content": content_base64,
                "branch": self.branch
            }

            if sha:
                data["sha"] = sha

            response = requests.put(url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                logger.info(f"Successfully updated {file_path} on GitHub")
                return True
            else:
                logger.error(f"Failed to update GitHub: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error updating GitHub: {e}")
            return False
