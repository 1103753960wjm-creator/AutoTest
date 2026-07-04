param(
    [string]$Root = (Resolve-Path ".").Path,
    [switch]$Help
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

if ($Help) {
    Write-Output "TestHub P0 rule check"
    Write-Output "Usage: powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1"
    Write-Output "Note: reads files as UTF-8 and scans high-risk patterns."
    exit 0
}

$issues = New-Object System.Collections.Generic.List[object]

function Add-Issue {
    param(
        [string]$Rule,
        [string]$File,
        [int]$Line,
        [string]$Message
    )

    $issues.Add([PSCustomObject]@{
        Rule = $Rule
        File = $File
        Line = $Line
        Message = $Message
    }) | Out-Null
}

function Get-TextFiles {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }

    Get-ChildItem -LiteralPath $Path -Recurse -File -Include *.js,*.vue,*.ts,*.md -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "\\node_modules\\" -and
            $_.FullName -notmatch "\\dist\\" -and
            $_.FullName -notmatch "\\build\\"
        }
}

function Get-LineNumber {
    param(
        [string]$Text,
        [int]$Index
    )

    if ($Index -le 0) {
        return 1
    }

    return (($Text.Substring(0, $Index) -split "`n").Count)
}

function Get-RelativePathCompat {
    param(
        [string]$BasePath,
        [string]$FullPath
    )

    $base = (Resolve-Path -LiteralPath $BasePath).Path.TrimEnd("\", "/")
    $full = (Resolve-Path -LiteralPath $FullPath).Path
    if ($full.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $full.Substring($base.Length).TrimStart("\", "/")
    }
    return $full
}

$frontendSrc = Join-Path $Root "frontend/src"
$frontendViews = Join-Path $Root "frontend/src/views"
$allFrontendFiles = @(Get-TextFiles -Path $frontendSrc)
$viewFiles = @(Get-TextFiles -Path $frontendViews)

foreach ($file in $allFrontendFiles) {
    $relative = Get-RelativePathCompat -BasePath $Root -FullPath $file.FullName
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    $lines = $content -split "`r?`n"

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        $isAuthNavigationFallback = $relative -eq "frontend\src\utils\authNavigation.js"
        if (-not $isAuthNavigationFallback -and $line -match "window\.location\.reload|window\.location\.href|window\.location\.assign") {
            Add-Issue -Rule "NO_BROWSER_NAVIGATION_FALLBACK" -File $relative -Line ($i + 1) -Message $line.Trim()
        }

        if ($line -cmatch "import\s+.*\bxlsx\b|from\s+['""][^'""]*\bxlsx\b[^'""]*['""]|require\(\s*['""][^'""]*\bxlsx\b|\bXLSX\b") {
            Add-Issue -Rule "NO_XLSX" -File $relative -Line ($i + 1) -Message $line.Trim()
        }

        if ($line -match "/api-testing/api-requests|/api-testing/executions/|collections/search") {
            Add-Issue -Rule "NO_LEGACY_API_TESTING_PATH" -File $relative -Line ($i + 1) -Message $line.Trim()
        }
    }
}

foreach ($file in $viewFiles) {
    $relative = Get-RelativePathCompat -BasePath $Root -FullPath $file.FullName
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    $lines = $content -split "`r?`n"
    $isApiTestingView = $relative -like "frontend\src\views\api-testing\*"

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        if ($isApiTestingView -and $line -match "from\s+['""]@/utils/api['""]|import\s+api\s+from\s+['""]@/utils/api['""]") {
            Add-Issue -Rule "NO_VIEW_DIRECT_UTILS_API_IMPORT" -File $relative -Line ($i + 1) -Message $line.Trim()
        }

        if ($line -match "功能开发中|暂未实现|featureInDevelopment|clearNotImplemented|assertionDeveloping") {
            Add-Issue -Rule "NO_FAKE_P0_ENTRY" -File $relative -Line ($i + 1) -Message $line.Trim()
        }
    }

    $formMatches = [regex]::Matches($content, "<(el-form|form)(?=[\s>])(?<attrs>[\s\S]*?)>", "IgnoreCase")
    foreach ($match in $formMatches) {
        $tag = $match.Groups[1].Value
        $attrs = $match.Groups["attrs"].Value
        if ($attrs -notmatch "@submit\.prevent") {
            Add-Issue -Rule "FORM_REQUIRES_SUBMIT_PREVENT" -File $relative -Line (Get-LineNumber -Text $content -Index $match.Index) -Message "<$tag> missing @submit.prevent"
        }
    }

    $buttonMatches = [regex]::Matches($content, "<button\b(?<attrs>[\s\S]*?)>", "IgnoreCase")
    foreach ($match in $buttonMatches) {
        $attrs = $match.Groups["attrs"].Value
        if ($attrs -notmatch "\btype\s*=") {
            Add-Issue -Rule "BUTTON_REQUIRES_TYPE" -File $relative -Line (Get-LineNumber -Text $content -Index $match.Index) -Message "<button> missing type"
        }
    }
}

if ($issues.Count -gt 0) {
    Write-Output "Rule check failed. Issue count: $($issues.Count)"
    foreach ($issue in $issues) {
        Write-Output ("[{0}] {1}:{2} {3}" -f $issue.Rule, $issue.File, $issue.Line, $issue.Message)
    }
    exit 1
}

Write-Output "Rule check passed: no P0 redline hits."
