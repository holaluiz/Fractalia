param([Parameter(Mandatory)][string]$Url, [Parameter(Mandatory)][string]$Name)
# Saves a (short-lived, pre-signed) itch.io CDN URL to Quaternius\_zips\<Name>.zip
$dir = Join-Path $PSScriptRoot "_zips"
New-Item -ItemType Directory -Force $dir | Out-Null
$out = Join-Path $dir "$Name.zip"
$client = New-Object System.Net.WebClient
$client.DownloadFile($Url, $out)
"{0}: {1:N1} MB" -f $Name, ((Get-Item -LiteralPath $out).Length / 1MB)
