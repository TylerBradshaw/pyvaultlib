import os
import logging
from azure.keyvault.secrets import SecretClient
from .certificate_util import WindowsCertCredential
from .secret_manager import SecretManager

class KeyVaultService:
    def __init__(self, config_scope: str = None):
        tenant_id = self._try_get_env("KEYVAULT_TENANT_ID")
        client_id = self._try_get_env("KEYVAULT_CLIENT_ID")
        thumbprint = self._try_get_env("KEYVAULT_THUMBPRINT")
        vault_name = self._try_get_env("KEYVAULT_NAME")
        password = self._try_get_env("KEYVAULT_CERT_PASSWORD", allow_empty=True)

        if not all([tenant_id, client_id, thumbprint, vault_name]):
            raise Exception("Missing Key Vault configuration settings.")

        self._cert_wrapper = WindowsCertCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            thumbprint=thumbprint,
            password=password or ""
        )

        self.secret_client = SecretClient(
            vault_url=f"https://{vault_name}.vault.azure.net",
            credential=self._cert_wrapper.credential
        )
        self.secret_manager = SecretManager(config_scope=config_scope)

    def _try_get_env(self, var, allow_empty=False):
        value = os.getenv(var)
        if value is None:
            logging.warning(f"[WARN] Env var '{var}' is NULL.")
        elif value == "" and not allow_empty:
            logging.warning(f"[WARN] Env var '{var}' is EMPTY.")
        return value

    def cleanup(self):
        if hasattr(self, "_cert_wrapper"):
            self._cert_wrapper.cleanup()

    def get_secret(self, secret_name: str):
        full_name = self.secret_manager.prefix + secret_name
        logging.info(f"Requesting Secret: {full_name}")
        try:
            secret = self.secret_client.get_secret(full_name)
            if self.secret_manager.load(secret.properties):
                return self.secret_manager.get_value(secret)
        except Exception as ex:
            logging.error(f"Failed to retrieve secret: {ex}")
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
