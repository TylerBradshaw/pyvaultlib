"""
Provides functionality to dynamically construct and evaluate secret naming conventions
based on the calling application's context and a defined configuration scope. This enables
secure, scoped retrieval of Azure Key Vault secrets using a consistent pattern.

Designed to support multi-application environments with fine-grained secret segregation.
"""
import os
import inspect

def get_calling_app_name():
    """
    Inspects the call stack to determine the calling application's filename.

    Returns:
        str: Name of the calling application (without extension). If undetectable, returns 'unknown_app'.
    """
    for frame_info in inspect.stack():
        filename = frame_info.filename
        if "pyvaultlib" not in filename:
            return os.path.splitext(os.path.basename(filename))[0]
    return "unknown_app"  # fallback

class SecretManager:
    """
    Handles secret name prefixing and filtering for Azure Key Vault based on the calling application and config scope.

    Attributes:
        config_scope (str): Logical group name (e.g. 'PRD', 'AzureDbSettings').
        prefix (str): Constructed as '{AppName}-{ConfigScope}--' to match secret names.

    Methods:
        load(secret_properties): Determines if a given secret belongs to this manager's scope.
        get_value(secret): Extracts the value if the secret matches the manager's scope.
    """

    def __init__(self, config_scope: str = None):
        """
        Initializes the secret manager with a prefix based on the calling application and provided scope.

        Args:
            config_scope (str): Logical category for secrets.

        Raises:
            ValueError: If no configuration scope is defined.
        """
        project_prefix = get_calling_app_name()
        self.config_scope = config_scope

        if not self.config_scope:
            raise ValueError("Configuration scope must be set (e.g., AzureDbSettings, FTPserverSettings, PRD).")

        self.prefix = f"{project_prefix}-{self.config_scope}--"

    def load(self, secret_properties):
        """
        Checks if the given secret's name starts with the expected prefix.

        Args:
            secret_properties: Azure secret metadata object with a 'name' attribute.

        Returns:
            bool: True if the secret should be managed by this instance.
        """
        return secret_properties.name.startswith(self.prefix)

    def get_value(self, secret):
        """
        Returns the secret's value if it matches the expected prefix.

        Args:
            secret: Azure secret object with 'name' and 'value'.

        Returns:
            Optional[str]: The secret value if valid, else None.
        """
        if secret.name.startswith(self.prefix):
            return secret.value
        return None
