import random
from typing import Dict, Optional

class ProxyManager:
    def __init__(self, proxy_list: list):
        self.proxy_list = proxy_list

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        try:
            if not self.proxy_list:
                print("Warning: No proxies available")
                return None
                
            proxy = random.choice(self.proxy_list)
            credentials, host_port = proxy.split("@")
            username, password = credentials.split(":")
            host, port = host_port.split(":")
            
            return {
                "http": f"http://{username}:{password}@{host}:{port}",
                "https": f"http://{username}:{password}@{host}:{port}"
            }
        except Exception as e:
            print(f"Error getting proxy: {str(e)}")
            return None