# Don tai nguyen Docker Compose cua kien truc cai tien.
# Cach chay (tu thu muc goc cua repo):
#   powershell -ExecutionPolicy Bypass -File infra\cleanup.ps1 -Level 1
# Level 1: dung va xoa container, mang (giu du lieu)
# Level 2: nhu level 1 + xoa volume (MAT du lieu DB va anh san pham)
# Level 3: nhu level 2 + xoa image build local (improved-app01, improved-app02)
param(
  [ValidateSet(1, 2, 3)][int]$Level = 1
)

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$f = "docker-compose.improved.yml"

switch ($Level) {
  1 {
    "Muc 1: dung va xoa container, mang (GIU du lieu)"
    docker compose -f $f down
  }
  2 {
    "Muc 2: xoa them volume dbdata, objdata (MAT du lieu DB va anh san pham)"
    if ((Read-Host "Go YES de xac nhan") -ne "YES") { "Da huy."; exit 1 }
    docker compose -f $f down -v
  }
  3 {
    "Muc 3: muc 2 + xoa image build local (improved-app01, improved-app02)"
    if ((Read-Host "Go YES de xac nhan") -ne "YES") { "Da huy."; exit 1 }
    docker compose -f $f down -v --rmi local
  }
}

"--- Kiem tra tai nguyen con sot ---"
docker ps -a --filter "name=improved-"
docker volume ls --filter "name=improved_"
docker network ls --filter "name=improved_"
docker images "improved-*"
