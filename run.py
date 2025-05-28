from pyvaultlib.key_vault_service import KeyVaultService

with KeyVaultService("utility") as service:
    secret = service.get_secret("MySecret")
    print("Secret:", secret)