"""
Provides a Windows-based certificate retrieval utility that integrates with Azure Identity
by exporting a certificate from the local user certificate store and generating a
CertificateCredential object for authenticating to Azure services.

Intended for secure, automated service authentication in enterprise environments.
"""
import os
import subprocess
import tempfile
from azure.identity import CertificateCredential

class WindowsCertCredential:
    """
    Securely retrieves a certificate by thumbprint from the Windows Certificate Store,
    exports it to a temporary .pfx using PowerShell, and creates an Azure CertificateCredential.

    Attributes:
        tenant_id (str): Azure Active Directory tenant ID.
        client_id (str): Azure App Registration client ID.
        thumbprint (str): Certificate thumbprint in Windows Cert Store.
        password (str): Optional password to protect the exported .pfx.
        credential (CertificateCredential): Azure credential object used for authentication.

    Methods:
        cleanup(): Deletes the temporary .pfx certificate file after use.
    """

    def __init__(self, tenant_id: str, client_id: str, thumbprint: str, password: str = ""):
        """
        Initializes the certificate credential wrapper.

        Args:
            tenant_id (str): Azure AD tenant ID.
            client_id (str): Azure AD App client ID.
            thumbprint (str): Thumbprint of the local certificate.
            password (str, optional): Optional password for PFX export. Defaults to "".
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.thumbprint = thumbprint.replace(" ", "")
        self.password = password
        self._pfx_path = self._export_cert_with_powershell()
        self.credential = self._create_credential()

    def _export_cert_with_powershell(self) -> str:
        """
        Uses PowerShell to export a certificate by thumbprint to a temporary .pfx file.

        Returns:
            str: Path to the temporary exported .pfx file.

        Raises:
            RuntimeError: If PowerShell fails to export the certificate.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pfx")
        temp_file.close()

        ps_script = f'''
        $thumb = "{self.thumbprint}"
        $path = "{temp_file.name}"
        $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{$_.Thumbprint -eq $thumb}}
        if ($cert -eq $null) {{
            throw "Certificate not found."
        }}
        $bytes = $cert.Export("PFX", "{self.password}")
        [System.IO.File]::WriteAllBytes($path, $bytes)
        '''

        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"PowerShell export failed:\n{result.stderr.strip()}")

        return temp_file.name

    def _create_credential(self) -> CertificateCredential:
        """
        Creates an Azure CertificateCredential using the exported .pfx file.

        Returns:
            CertificateCredential: Credential object for authenticating with Azure services.
        """
        return CertificateCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            certificate_path=self._pfx_path,
            password=self.password if self.password else None
        )

    def cleanup(self):
        """
        Deletes the temporary .pfx file created during credential setup.
        Logs the deletion path.
        """
        if self._pfx_path and os.path.exists(self._pfx_path):
            os.remove(self._pfx_path)
            print(f"Cleaned up: {self._pfx_path}")
