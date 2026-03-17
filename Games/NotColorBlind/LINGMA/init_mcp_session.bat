off
powershell
-Command
Invoke-WebRequest -Uri 'http://localhost:8080/' -Method 'POST' -Headers @{'^Content-Type^'='application/json'} -Body '{\
jsonrpc\:\2.0\,\id\:1,\method\:\initialize\,\params\:{\protocolVersion\:\2024-11-05\,\capabilities\:{},\clientInfo\:{\name\:\PowerShell\,\version\:\1.0.0\}}}' -UseBasicParsing
