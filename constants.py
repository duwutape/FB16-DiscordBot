import os

from dotenv import load_dotenv

load_dotenv()

### grauer raum
GR_DEL_SEC = int(os.getenv('GR_DEL_MIN')) * 60

### latex
LATEX_SERVER_URL = 'https://rtex.probablyaweb.site/api/v2'
