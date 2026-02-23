$ErrorActionPreference='Stop'
$csvPath='D:\backup\笔记\permanent notes 23ffc754-5034-4a8d-8521-4b9579ed5c7d_ExportBlock-15d089fe-be12-4475-a2c7-955bb1038bc9\Permanent Notes 57fba073c9a14e4fbba8a9a736fac97f.csv'
$outDir='D:\Quartz4\content\permanent-notes'

function Sanitize-FileName([string]$name) {
  if ([string]::IsNullOrWhiteSpace($name)) { return 'untitled' }
  $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
  $clean = $name
  foreach ($ch in $invalidChars) {
    $clean = $clean.Replace([string]$ch, '-')
  }
  $clean = $clean -replace '\s+', ' '
  $clean = $clean.Trim().TrimEnd('.')
  if ($clean.Length -gt 110) { $clean = $clean.Substring(0, 110).Trim() }
  if ([string]::IsNullOrWhiteSpace($clean)) { $clean = 'untitled' }
  return $clean
}

function To-YamlString([string]$value) {
  if ($null -eq $value) { return "''" }
  return "'" + ($value -replace "'", "''") + "'"
}

if (-not (Test-Path -LiteralPath $outDir)) {
  New-Item -ItemType Directory -Path $outDir | Out-Null
}
Get-ChildItem -LiteralPath $outDir -Filter '*.md' -File -ErrorAction SilentlyContinue | Remove-Item -Force

$rows = Import-Csv -LiteralPath $csvPath
$nameCount = @{}
$generated = 0

foreach ($row in $rows) {
  $title = [string]$row.Name
  $base = Sanitize-FileName $title

  if ($nameCount.ContainsKey($base)) {
    $nameCount[$base]++
    $fileBase = "$base-$($nameCount[$base])"
  } else {
    $nameCount[$base] = 1
    $fileBase = $base
  }

  $filePath = Join-Path $outDir ($fileBase + '.md')

  $tags = @()
  if (-not [string]::IsNullOrWhiteSpace($row.Tags)) {
    $tags += ($row.Tags -split '[,，]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  }

  $lines = @()
  $lines += '---'
  $lines += "title: $(To-YamlString $title)"
  if (-not [string]::IsNullOrWhiteSpace($row.Created)) { $lines += "created: $(To-YamlString ([string]$row.Created))" }
  if (-not [string]::IsNullOrWhiteSpace($row.modify)) { $lines += "modified: $(To-YamlString ([string]$row.modify))" }
  if (-not [string]::IsNullOrWhiteSpace($row.Type)) { $lines += "type: $(To-YamlString ([string]$row.Type))" }
  if (-not [string]::IsNullOrWhiteSpace($row.URL)) { $lines += "source: $(To-YamlString ([string]$row.URL))" }
  $lines += 'tags:'
  if ($tags.Count -gt 0) {
    $lines += ($tags | ForEach-Object { "  - $(To-YamlString $_)" })
  } else {
    $lines += "  - 'uncategorized'"
  }
  $lines += '---'
  $lines += ''
  if (-not [string]::IsNullOrWhiteSpace($row.Intro)) {
    $lines += [string]$row.Intro
  } else {
    $lines += '_No intro available._'
  }

  Set-Content -LiteralPath $filePath -Value ($lines -join "`r`n") -Encoding UTF8
  $generated++
}

"Generated=$generated"
"MdFiles=$((Get-ChildItem -LiteralPath $outDir -Filter '*.md' -File | Measure-Object).Count)"
Get-ChildItem -LiteralPath $outDir -Filter '*.md' -File | Select-Object -First 8 -ExpandProperty Name
