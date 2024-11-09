# config.py
import tomli
import os
from typing import Dict

def load_config() -> Dict[str, str]:
    # Load from file
    try:
        with open('config.toml', 'rb') as f:
            config = tomli.load(f)
    except:
        config = {}
    
    # Override with environment variables if they exist
    if os.getenv('TBC_API_URL'): config['api']['url'] = os.getenv('TBC_API_URL')
    if os.getenv('TBC_API_JWT'): config['api']['jwt'] = os.getenv('TBC_API_JWT')
    if os.getenv('TBC_API_ACT_AS'): config['api']['act_as'] = os.getenv('TBC_API_ACT_AS')
    
    return config

# Load once at module level
config = load_config()
API_URL = config['api']['url']
JWT = config['api']['jwt']
ACT_AS = config['api']['act_as']