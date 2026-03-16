import hashlib
from typing import Dict, Any


class SignatureVerifier:
    def __init__(self, config: Dict, input_queue, output_queue):
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue
        
        stateless_config = config.get("processing", {}).get("stateless_tasks", {})
        self.secret_key = stateless_config.get("secret_key")
        self.iterations = stateless_config.get("iterations", 100000)
        self.algorithm = stateless_config.get("algorithm", "pbkdf2_hmac")
    
    def _verify_signature(self, raw_value: float, provided_signature: str) -> bool:
        try:
            rounded_value = round(raw_value, 2)
            raw_value_str = str(rounded_value)
            
            password_bytes = self.secret_key.encode('utf-8')
            salt_bytes = raw_value_str.encode('utf-8')
            
            expected_hash = hashlib.pbkdf2_hmac(
                hash_name='sha256',
                password=password_bytes,
                salt=salt_bytes,
                iterations=self.iterations
            )
            expected_signature = expected_hash.hex()
            
            return expected_signature == provided_signature
        
        except Exception as e:
            print(f"[SignatureVerifier] Verification error: {e}")
            return False
    
    def run(self):
        verified_count = 0
        dropped_count = 0
        
        try:
            print(f"[SignatureVerifier] Starting verification worker")
            
            while True:
                data_packet = self.input_queue.get()
                
                if data_packet is None:
                    break
                
                raw_value = data_packet.get("metric_value")
                provided_signature = data_packet.get("security_hash")
                
                if raw_value is not None and provided_signature:
                    if self._verify_signature(raw_value, provided_signature):
                        self.output_queue.put(data_packet)
                        verified_count += 1
                    else:
                        dropped_count += 1
                        if dropped_count % 50 == 0:
                            print(f"[SignatureVerifier] Dropped {dropped_count} invalid packets")
        
        except Exception as e:
            print(f"[SignatureVerifier] Error: {e}")
        
        finally:
            print(f"[SignatureVerifier] ✓ Completed. Verified: {verified_count}, Dropped: {dropped_count}")
            self.output_queue.put(None)
