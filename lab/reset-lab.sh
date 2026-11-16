#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Reset environment dengan menghapus volume & container lama.
docker compose down -v --remove-orphans

docker compose up -d

echo "Lab DVWA berhasil di-reset. Akses target melalui http://localhost:8080"
