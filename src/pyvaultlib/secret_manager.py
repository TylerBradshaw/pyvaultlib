import os
import inspect

def get_calling_app_name():
    # Walk up the stack to find the first frame outside pyvaultlib
    for frame_info in inspect.stack():
        filename = frame_info.filename
        if "pyvaultlib" not in filename:
            return os.path.splitext(os.path.basename(filename))[0]
    return "unknown_app"  # fallback

class SecretManager:
    def __init__(self, config_scope: str = None):
        project_prefix = get_calling_app_name()

        self.config_scope = config_scope or os.getenv("KEYVAULT_CONFIG_SCOPE", "").strip()

        if not self.config_scope:
            raise ValueError("Configuration scope must be set (e.g., AzureDbSettings, FTPserverSettings, PRD).")

        self.prefix = f"{project_prefix}-{self.config_scope}--"

    def load(self, secret_properties):
        return secret_properties.name.startswith(self.prefix)

    def get_value(self, secret):
        if secret.name.startswith(self.prefix):
            return secret.value
        return None