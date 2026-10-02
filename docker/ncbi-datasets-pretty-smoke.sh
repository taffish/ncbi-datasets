#!/bin/sh
# 仅 loopback 假 API：不查询 NCBI，也不下载数据；限时监督和精确 PID 清理。
set -eu
tmp=$(mktemp -d /tmp/ncbi-pretty.XXXXXX)
pid=""
cleanup() {
  rc=$?
  trap - EXIT
  if [ "$rc" -ne 0 ]; then
    printf 'pretty probe failed: exit=%s\n' "$rc" >&2
    for log in "$tmp"/*.log; do [ ! -f "$log" ] || tail -n 20 "$log" >&2; done
  fi
  if [ -n "$pid" ]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  rm -rf "$tmp"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$tmp/cgi-bin"
cat > "$tmp/cgi-bin/api" <<'CGI'
#!/bin/sh
printf 'Content-Type: application/json\r\n\r\n'
printf '%s\n' '{"reports":[{"accession":"GCF_000001405.40","organism":{"organism_name":"synthetic organism","tax_id":9606}},{"accession":"GCF_000001635.27","organism":{"organism_name":"synthetic \"mouse\"\\ colony","tax_id":10090}}],"total_count":2}'
CGI
chmod 700 "$tmp/cgi-bin/api"
busybox httpd -f -p 127.0.0.1:18380 -h "$tmp" > "$tmp/httpd.log" 2>&1 &
pid=$!
i=0
until busybox wget -q -O /dev/null http://127.0.0.1:18380/cgi-bin/api; do
  kill -0 "$pid"
  i=$((i+1))
  [ "$i" -lt 50 ]
  sleep 0.1
done
for mode in json jsonl; do
  flag=""
  [ "$mode" != jsonl ] || flag="--as-json-lines"
  datasets summary genome accession GCF_000001405.40 $flag --gateway-url http://127.0.0.1:18380/cgi-bin/api > "$tmp/$mode.raw" 2> "$tmp/$mode.raw.log"
  datasets summary genome accession GCF_000001405.40 $flag --pretty --gateway-url http://127.0.0.1:18380/cgi-bin/api > "$tmp/$mode.pretty" 2> "$tmp/$mode.pretty.log"
  LC_ALL=C busybox awk -f /opt/ncbi-datasets/share/testdata/ncbi-datasets-json-compact.awk "$tmp/$mode.raw" > "$tmp/$mode.raw.compact"
  LC_ALL=C busybox awk -f /opt/ncbi-datasets/share/testdata/ncbi-datasets-json-compact.awk "$tmp/$mode.pretty" > "$tmp/$mode.pretty.compact"
  if ! busybox cmp -s "$tmp/$mode.raw.compact" "$tmp/$mode.pretty.compact"; then
    printf 'pretty probe content mismatch: mode=%s (string whitespace and escapes preserved)\n' "$mode" >&2
    exit 1
  fi
  grep -F '"accession": "GCF_000001405.40"' "$tmp/$mode.pretty" >/dev/null
  grep -F '"accession": "GCF_000001635.27"' "$tmp/$mode.pretty" >/dev/null
  test "$(wc -l < "$tmp/$mode.pretty")" -gt "$(wc -l < "$tmp/$mode.raw")"
done
test "$(wc -l < "$tmp/jsonl.raw")" -eq 2
if datasets summary genome accession --pretty --not-a-real-option > "$tmp/invalid.out" 2> "$tmp/invalid.log"; then
  echo 'unknown option unexpectedly succeeded with --pretty' >&2
  exit 1
fi
grep -F 'unknown flag' "$tmp/invalid.log" >/dev/null
echo 'PASS pretty JSON/JSONL identity, indentation, two records and failure propagation'
