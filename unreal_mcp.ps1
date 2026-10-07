param([string]$Method = 'tools/list', [string]$ParamsFile = '')
$ErrorActionPreference = 'Stop'
$headers = @{Accept='application/json, text/event-stream'; 'MCP-Protocol-Version'='2025-11-25'}
$init = @{jsonrpc='2.0';id=1;method='initialize';params=@{protocolVersion='2025-11-25';capabilities=@{};clientInfo=@{name='codex-animation';version='1.0'}}} | ConvertTo-Json -Depth 10 -Compress
$initialized = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/mcp' -Method POST -ContentType 'application/json' -Headers $headers -Body $init -TimeoutSec 15
$headers['Mcp-Session-Id'] = $initialized.Headers['Mcp-Session-Id'][0]
$params = @{}
if ($ParamsFile) { $params = Get-Content -LiteralPath $ParamsFile -Raw | ConvertFrom-Json -AsHashtable }
$body = @{jsonrpc='2.0'; id=2; method=$Method; params=$params} | ConvertTo-Json -Depth 80 -Compress
$reply = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/mcp' -Method POST -ContentType 'application/json' -Headers $headers -Body $body -TimeoutSec 180
$reply.Content
