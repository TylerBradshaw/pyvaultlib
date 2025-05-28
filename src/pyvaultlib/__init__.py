"""
The pyvaultlib package is a secure utility for retrieving scoped secrets from
Azure Key Vault using certificate-based authentication. It includes modules for certificate
retrieval from the Windows Certificate Store, dynamic secret prefixing, and credentialed
Key Vault access.

Modules:
    - certificate_util: Handles Windows certificate export and Azure credential creation.
    - key_vault_service: Main interface for scoped secret retrieval via Key Vault.
    - secret_manager: Constructs and filters secret names based on app context and config scope.
"""
__all__ = ["certificate_util", "key_vault_service", "secret_manager"]

from . import certificate_util
from . import key_vault_service
from . import  secret_manager