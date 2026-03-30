import os
import logging
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. Configuração de Logging Profissional
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def bootstrap_env() -> bool:
    """Localiza e carrega o arquivo .env dentro da pasta config/."""
    root_dir = Path(__file__).resolve().parent.parent
    env_path = root_dir / 'config' / '.env'

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f"Configurações carregadas de: {env_path}")
        return True
    
    logging.error(f"Arquivo .env não encontrado em: {env_path}")
    return False

def create_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """
    Cria uma sessão HTTP com estratégia de reiteração automática.
    - retries: número de tentativas.
    - backoff_factor: multiplicador para o tempo de espera.
    - status_forcelist: códigos HTTP que disparam o retry.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_weather_data(api_key: str) -> dict:
    """Faz a requisição com Retry e guarda os dados na pasta data/."""
    # URL formatada corretamente (Sao+Paulo ou Sao%20Paulo)
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Sao+Paulo,BR&units=metric&appid={api_key}"
    
    session = create_retry_session()
    
    try:
        logging.info("Iniciando requisição à API do OpenWeather...")
        response = session.get(url, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        
        # Definição do caminho de saída absoluto
        root_dir = Path(__file__).resolve().parent.parent
        output_path = root_dir / 'data' / 'weather_data.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logging.info(f"Sucesso! Dados persistidos em: {output_path}")
        return data

    except requests.exceptions.HTTPError as e:
        logging.error(f"Erro HTTP (verifique a API Key ou limites): {e}")
    except requests.exceptions.ConnectionError:
        logging.error("Erro de conexão. Verifique a internet.")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
    
    return {}

if __name__ == "__main__":
    if bootstrap_env():
        key = os.getenv('OPENWEATHER_API_KEY')
        if key:
            extract_weather_data(key)
        else:
            logging.error("Variável OPENWEATHER_API_KEY ausente no .env")