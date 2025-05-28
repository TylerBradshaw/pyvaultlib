"""
Provides a high-level interface to access Azure Key Vault secrets using a certificate-based
authentication mechanism. Integrates with the Windows certificate store and utilizes a scoped
naming convention to simplify secure secret retrieval in multi-application environments.

This module is the main entry point for external callers needing credentialed access to Azure Key Vault.
"""
import os
import logging
from azure.keyvault.secrets import SecretClient
from .certificate_util import WindowsCertCredential
from .secret_manager import SecretManager

class KeyVaultService:
    """
    Provides certificate-based authentication to Azure Key Vault and retrieves secrets
    using naming conventions scoped by application and configuration category.

    Attributes:
        secret_client (SecretClient): Azure Key Vault client for secret operations.
        secret_manager (SecretManager): Handles prefixing and filtering of secrets.

    Methods:
        get_secret(secret_name: str) -> Optional[str]: Fetches a scoped secret by name.
        cleanup(): Cleans up temporary certificate resources.
    """

    def __init__(self, config_scope: str = None):
        """
        Initializes the KeyVaultService using environment variables for credentials.

        Args:
            config_scope (str): Secret category identifier, e.g. "PRD", "DbSettings".

        Raises:
            Exception: If any required environment variable is missing.
        """
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
        """
        Attempts to retrieve an environment variable, logs if missing or empty.

        Args:
            var (str): Name of the environment variable.
            allow_empty (bool): If False, warns on empty values.

        Returns:
            Optional[str]: The environment variable's value, or None if unset.
        """
        value = os.getenv(var)
        if value is None:
            logging.warning(f"[WARN] Env var '{var}' is NULL.")
        elif value == "" and not allow_empty:
            logging.warning(f"[WARN] Env var '{var}' is EMPTY.")
        return value

    def cleanup(self):
        """
        Releases temporary resources created for certificate-based auth.
        """
        if hasattr(self, "_cert_wrapper"):
            self._cert_wrapper.cleanup()

    def get_secret(self, secret_name: str):
        """
        Retrieves a secret from Azure Key Vault using the scoped prefix.

        Args:
            secret_name (str): The simple name of the secret (without prefix).

        Returns:
            Optional[str]: The value of the secret, or None if not found or unauthorized.
        """
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
        """Enables use of KeyVaultService in a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures cleanup when exiting a context manager block."""
        self.cleanup()
