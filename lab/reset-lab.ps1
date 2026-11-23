param(
    [switch]$ConfirmReset
)

$ErrorActionPreference = 'Stop'
$composeFile = Join-Path $PSScriptRoot 'docker-compose.yml'

if (-not $ConfirmReset) {
    $confirmation = Read-Host 'Reset menghapus seluruh data DVWA. Ketik RESET untuk melanjutkan'
    if ($confirmation -cne 'RESET') {
        Write-Output 'Reset dibatalkan.'
        return
    }
}

docker compose -f $composeFile config --quiet
if ($LASTEXITCODE -ne 0) {
    throw "Validasi Docker Compose gagal (kode $LASTEXITCODE)."
}

docker compose -f $composeFile down --volumes --remove-orphans
if ($LASTEXITCODE -ne 0) {
    throw "Penghentian lab gagal (kode $LASTEXITCODE)."
}

docker compose -f $composeFile up --detach
if ($LASTEXITCODE -ne 0) {
    throw "Lab gagal dijalankan kembali (kode $LASTEXITCODE)."
}

Write-Output 'Lab dimulai ulang. Periksa status dengan docker compose ps.'
Write-Output 'Akses target hanya dari host: http://localhost:8080'
