$ErrorActionPreference = 'Stop'
$reportRoot = $PSScriptRoot
Push-Location -LiteralPath $reportRoot
try {
    if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
        throw 'Chua co XeLaTeX. Xem README.md hoac dung goi ZIP tren Overleaf; script khong cai phan mem.'
    }
    New-Item -ItemType Directory -Path 'output' -Force | Out-Null
    if (Get-Command latexmk -ErrorAction SilentlyContinue) {
        & latexmk -xelatex main.tex
        if ($LASTEXITCODE -ne 0) { throw 'LaTeX build failed; inspect output/main.log.' }
    }
    else {
        if (-not (Get-Command biber -ErrorAction SilentlyContinue)) {
            throw 'Biber is required for references.bib. See README.md.'
        }
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=output main.tex
        if ($LASTEXITCODE -ne 0) { throw 'First XeLaTeX pass failed.' }
        & biber --input-directory=output --output-directory=output main
        if ($LASTEXITCODE -ne 0) { throw 'Biber failed.' }
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=output main.tex
        if ($LASTEXITCODE -ne 0) { throw 'Second XeLaTeX pass failed.' }
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=output main.tex
        if ($LASTEXITCODE -ne 0) { throw 'Final XeLaTeX pass failed.' }
    }
    Write-Output 'PDF: output/main.pdf. Inspect all pages and the log before submission.'
}
finally {
    Pop-Location
}
