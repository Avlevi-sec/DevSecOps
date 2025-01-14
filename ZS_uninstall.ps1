[Environment]::SetEnvironmentVariable('ZSCALER_PASSWORD', 'password', [System.EnvironmentVariableTarget]::User)
Start-Process -FilePath "C:\Program Files\Zscaler\ZSAInstaller\uninstall.exe" -ArgumentList "--mode unattended"
