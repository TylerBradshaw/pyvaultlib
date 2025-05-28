# pyvaultlib

A secure Python utility for retrieving Azure Key Vault secrets using certificate-based authentication from the Windows Certificate Store. Designed for enterprise scenarios where environment isolation and scoped secret management are critical.

## Features

- 🔐 Certificate-based auth using local user certificate store (thumbprint-based lookup)
- ⚙️ Auto-exports .pfx files from Windows certificates on-the-fly
- 🧼 Cleans up sensitive files automatically after use
- 🏷️ Applies scoped secret prefixes using calling app and configuration scope
- ✅ Compatible with the Azure SDK for Python (`azure.identity`, `azure.keyvault.secrets`)
- 📦 Easy integration with multi-environment applications

## Installation

Install locally in editable mode:

```
git clone https://your-company-url/pyvaultlib.git
cd pyvaultlib
pip install -e .
```

## Package Modules

- `certificate_util`: Handles certificate lookup, export, and creation of `CertificateCredential`
- `key_vault_service`: High-level class for securely accessing scoped Key Vault secrets
- `secret_manager`: Infers calling app name and builds prefix-based secret filters

## Environment Variables

| Variable                   | Description                                                         | Required |
|----------------------------|---------------------------------------------------------------------|----------|
| `KEYVAULT_TENANT_ID`       | Azure AD Tenant ID                                                  | ✅       |
| `KEYVAULT_CLIENT_ID`       | App Registration Client ID                                          | ✅       |
| `KEYVAULT_THUMBPRINT`      | Certificate thumbprint from Windows CurrentUser cert store          | ✅       |
| `KEYVAULT_NAME`            | Azure Key Vault name (e.g., `your-keyvault`)                        | ✅       |
| `KEYVAULT_CERT_PASSWORD`   | (Optional) Password for exporting the certificate to .pfx           | ❌       |




## Usage Example

```
from pyvaultlib.key_vault_service import KeyVaultService

with KeyVaultService(config_scope="AzureDbSettings") as kv:
    conn_string = kv.get_secret("ConnectionString")
    print("DB Connection:", conn_string)
```

## Secret Naming Convention

Secrets must follow this pattern to be accessible:

```
<projectName>-<configScope>--<secretName>
```

- `projectName`: Automatically derived from the calling application (filename).
- `configScope`: Passed in code.

### Examples

| Application    | Config Scope        | Secret Name         | Full Secret ID                          |
|----------------|---------------------|----------------------|------------------------------------------|
| `myapp`        | `AzureDbSettings`   | `ConnectionString`   | `myapp-AzureDbSettings--ConnectionString` |
| `billingApp`   | `FTPserverSettings` | `Host`               | `billingApp-FTPserverSettings--Host`     |
| `siteX`        | `PRD`               | `KeyVaultUri`        | `siteX-PRD--KeyVaultUri`                 |

Only secrets matching this format will be returned.

## Certificate Handling

Certificates are:
- Retrieved from the **Windows CurrentUser** store using the given thumbprint
- Exported to `.pfx` format using PowerShell
- Deleted automatically after the session via context management

---