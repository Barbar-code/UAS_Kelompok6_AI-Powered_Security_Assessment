#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ "${1:-}" == "--yes" ]]; then
  shift
elif [[ $# -eq 0 ]]; then
  read -r -p "Reset menghapus seluruh data DVWA. Ketik RESET untuk melanjutkan: " confirmation
  [[ "$confirmation" == "RESET" ]] || {
    echo "Reset dibatalkan."
    exit 1
  }
else
  echo "Pemakaian: $0 [--yes]"
  exit 2
fi

if [[ $# -ne 0 ]]; then
  echo "Argumen tidak dikenal."
  exit 2
fi

docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.yml down --volumes --remove-orphans
docker compose -f docker-compose.yml up --detach

echo "Lab dimulai ulang. Periksa status dengan: docker compose -f docker-compose.yml ps"
echo "Akses target hanya dari host: http://localhost:8080"
