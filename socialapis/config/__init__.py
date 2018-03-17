from socialapis.config.tokens import *
import os
from google.cloud import language
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.join(BASE_DIR,"config","msrcosmos_apikey.json")
client = language.LanguageServiceClient()
