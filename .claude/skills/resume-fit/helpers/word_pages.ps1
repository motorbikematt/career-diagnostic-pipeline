param(
    [Parameter(Mandatory)][string]$DocxPath,
    [string]$PdfPath
)
# Measure a .docx in Microsoft Word (read-only; never saves the document).
# Emits one JSON object: page count, the last line's distance from the top of
# the last page (points), the page height, and the bottom margin. Optionally
# exports a PDF through Word's own exporter (ExportAsFixedFormat, format 17).
# Called by word_pages.py; usable on its own from PowerShell.
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open((Resolve-Path $DocxPath).Path, $false, $true)
    try {
        $doc.Repaginate()
        # Collapse to the last character: Information(3) reports the page where
        # a range ENDS and Information(6) its vertical position from page top.
        $end = $doc.Range($doc.Content.End - 1, $doc.Content.End - 1)
        $setup = $doc.PageSetup
        if ($PdfPath) { $doc.ExportAsFixedFormat($PdfPath, 17) }
        [pscustomobject]@{
            pages          = $doc.ComputeStatistics(2)
            last_line_top  = [math]::Round($end.Information(6), 1)
            page_height    = $setup.PageHeight
            bottom_margin  = $setup.BottomMargin
            pdf            = $PdfPath
        } | ConvertTo-Json -Compress
    } finally {
        $doc.Close($false)
    }
} finally {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
