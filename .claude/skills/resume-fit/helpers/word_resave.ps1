param(
    [Parameter(Mandatory)][string]$DocxPath,
    [switch]$Convert
)
# Open a .docx in a private Word instance and save it, so Word writes its own
# app properties and statistics. Optionally upgrades out of Compatibility Mode.
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open((Resolve-Path $DocxPath).Path, $false, $false, $false)
    try {
        $before = $doc.CompatibilityMode
        if ($Convert -and $before -lt 15) { $doc.Convert() }
        $doc.Save()
        [pscustomobject]@{ compat_before = $before; compat_after = $doc.CompatibilityMode } | ConvertTo-Json -Compress
    } finally {
        $doc.Close($false)
    }
} finally {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
