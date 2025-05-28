# pyvault-utility

A secure utility for accessing Azure Key Vault secrets using certificate authentication from the Windows Certificate Store.

## Features

- Uses certificate thumbprints to retrieve certs from Windows CurrentUser store
- Exports certs on-the-fly and cleans them up
- Filters secrets by project name as a prefix
- Compatible with all Azure SDK for Python apps

## Installation

Install locally in editable mode:

```
git clone https://your-company-url/pyvault-utility.git
cd pyvault-utility
pip install -e 
```
## Environment Variables

| Variable               | Description                                    |
|------------------------|------------------------------------------------|
| `KEYVAULT_TENANT_ID`   | Azure AD Tenant ID                             |
| `KEYVAULT_CLIENT_ID`   | App Registration Client ID                     |
| `KEYVAULT_THUMBPRINT`  | Certificate thumbprint from Windows cert store |
| `KEYVAULT_NAME`        | Name of Azure Key Vault                        |
| `KEYVAULT_CERT_PASSWORD` | (Optional) Password used when exporting PFX     |


## Usage

```
from main.key_vault_service import KeyVaultService

with KeyVaultService() as kv:
    secret = kv.get_secret("MySecret")
    print("Secret:", secret)
```
## Example Secret Naming
- Secrets must be prefixed using your project folder name: `<projectName>-<configScope>--<secretName>`
Only these secrets will be loaded by this utility.

Examples:
- `myapp-AzureDbSettings--ConnectionString`
- `billingApp-FTPserverSettings--Host`
- `siteX-PRD--KeyVaultUri`

The `projectName` is automatically derived from the root folder name.
The `configScope` can be passed in code or set via the environment variable `KEYVAULT_CONFIG_SCOPE`.

## Cleanup
Temporary certificate files are deleted automatically after use.



---
