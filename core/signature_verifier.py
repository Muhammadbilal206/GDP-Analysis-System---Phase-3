from .functional_core import validate_hash

class AuthWorker:
    def __init__(self, config_data):
        settings = config_data["processing"]["stateless_tasks"]
        if settings["algorithm"] != "pbkdf2_hmac":
            raise ValueError("Configuration error: Algorithm must be pbkdf2_hmac.")
        
        self._key = settings["secret_key"]
        self._iters = settings["iterations"]

    def execute(self, q_in, q_out):
        while True:
            item = q_in.get()
            
            if item is None:
                q_out.put(None)
                break

            is_authentic = validate_hash(
                metric=item["metric_value"],
                expected_hash=item["security_hash"],
                secret=self._key,
                rounds=self._iters
            )

            if not is_authentic:
                item["_dropped"] = True
                
            q_out.put(item)
