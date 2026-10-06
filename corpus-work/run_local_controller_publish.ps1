param(
    [Parameter(Mandatory=$true)][string]$Batch,
    [string]$HostAlias = 'Yupeng-orx',
    [string]$Owner = 'local-controller-01a10a85',
    [int]$Generation = 1,
    [string]$Cache = (Join-Path (Split-Path $PSScriptRoot -Parent) 'publication-cache'),
    [string]$Relay = (Join-Path (Split-Path $PSScriptRoot -Parent) 'relay.git')
)
$ErrorActionPreference = 'Stop'
python -B (Join-Path $PSScriptRoot 'controller_publish_pipeline.py') publish-batch --host $HostAlias --batch $Batch --owner $Owner --generation $Generation --cache $Cache --relay $Relay
if ($LASTEXITCODE -ne 0) { throw 'Publication retained for resume; inspect stage failure receipt.' }
