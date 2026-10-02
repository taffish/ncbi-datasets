#!/bin/sh
set -eu

mode="${1:-all}"
tmp=""
cleanup() {
  if [ -n "$tmp" ]; then rm -rf "$tmp"; fi
}
finish() {
  status=$?
  trap - EXIT
  if [ "$status" -ne 0 ]; then
    printf 'ncbi-datasets smoke failed: stage=%s exit=%s\n' "$mode" "$status" >&2
    if [ -n "$tmp" ]; then
      for log in "$tmp"/*.log "$tmp"/report.tsv; do
        if [ -f "$log" ]; then tail -n 20 "$log" >&2; fi
      done
    fi
  fi
  cleanup
  exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# 每个功能 smoke 同时检查本版固定告知材料；完整性检查不冒充完整二进制 SBOM。
/opt/ncbi-datasets/share/testdata/check-notices.sh >/dev/null

new_tmp() {
  tmp="$(mktemp -d /tmp/taf-ncbi-datasets.XXXXXX)"
}

write_genome_report() {
  output="$1"
  printf '%s\n' \
    '{"accession":"GCF_TAFFISH.1","organism":{"organismName":"TAFFISH test organism","taxId":424242}}' \
    > "$output"
}

write_sequence_report() {
  output="$1"
  printf '%s\n' \
    '{"query":["NC_TAFFISH.1"],"sequence":{"accession":"NC_TAFFISH.1","organismName":"TAFFISH test organism","length":1234,"updateDate":"2026-08-10","databaseProvider":"RefSeq","description":"TAFFISH sequence","taxId":424242,"bioprojectAccession":"PRJNA_TAFFISH"}}' \
    > "$output"
}

run_tsv() {
  new_tmp
  write_genome_report "$tmp/assembly_data_report.jsonl"
  dataformat tsv genome \
    --force \
    --inputfile "$tmp/assembly_data_report.jsonl" \
    --fields accession,organism-name,organism-tax-id \
    > "$tmp/report.tsv"
  test "$(sed -n '1p' "$tmp/report.tsv")" = \
    "Assembly Accession	Organism Name	Organism Taxonomic ID"
  test "$(sed -n '2p' "$tmp/report.tsv")" = \
    "GCF_TAFFISH.1	TAFFISH test organism	424242"
  test "$(wc -l < "$tmp/report.tsv" | tr -d ' ')" = "2"
  rm -rf "$tmp"
}

run_sequence() {
  new_tmp
  write_sequence_report "$tmp/sequence_data_report.jsonl"
  dataformat tsv sequence \
    --force \
    --template summary \
    --inputfile "$tmp/sequence_data_report.jsonl" \
    > "$tmp/report.tsv"
  test "$(sed -n '1p' "$tmp/report.tsv")" = \
    "Query	Accession	Tax Id	Tax name	Length	Units	Molecule Type	Provider	Description	Bioproject"
  test "$(wc -l < "$tmp/report.tsv" | tr -d ' ')" = "2"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f1)" = "NC_TAFFISH.1"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f2)" = "NC_TAFFISH.1"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f3)" = "424242"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f4)" = "TAFFISH test organism"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f5)" = "1234"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f8)" = "RefSeq"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f9)" = "TAFFISH sequence"
  test "$(sed -n '2p' "$tmp/report.tsv" | cut -f10)" = "PRJNA_TAFFISH"
  rm -rf "$tmp"
}

run_excel() {
  new_tmp
  write_genome_report "$tmp/assembly_data_report.jsonl"
  dataformat excel genome \
    --force \
    --inputfile "$tmp/assembly_data_report.jsonl" \
    --fields accession,organism-name,organism-tax-id \
    --outputfile "$tmp/report.xlsx" \
    > "$tmp/dataformat.log"
  test -s "$tmp/report.xlsx"
  test "$(head -c 2 "$tmp/report.xlsx")" = "PK"
  unzip -t "$tmp/report.xlsx" > "$tmp/zip-test.log"
  unzip -p "$tmp/report.xlsx" xl/sharedStrings.xml > "$tmp/strings.xml"
  grep -F 'GCF_TAFFISH.1' "$tmp/strings.xml" >/dev/null
  grep -F 'TAFFISH test organism' "$tmp/strings.xml" >/dev/null
  grep -F "saved Excel workbook" "$tmp/dataformat.log" >/dev/null
  rm -rf "$tmp"
}

run_invalid() {
  new_tmp
  printf '%s\n' '{invalid json}' > "$tmp/bad.jsonl"
  if dataformat tsv genome --force --inputfile "$tmp/bad.jsonl" \
      > "$tmp/out.tsv" 2> "$tmp/error.log"; then
    echo 'invalid JSON unexpectedly accepted' >&2
    exit 1
  fi
  test -s "$tmp/error.log"
  grep -Ei 'error|invalid|unexpected' "$tmp/error.log" >/dev/null
  cat "$tmp/error.log" >&2
  rm -rf "$tmp"
}

case "$mode" in
  tsv)
    run_tsv
    ;;
  excel)
    run_excel
    ;;
  sequence)
    run_sequence
    ;;
  invalid)
    run_invalid
    ;;
  buildtime)
    run_tsv
    run_sequence
    ;;
  all)
    run_tsv
    run_sequence
    run_excel
    run_invalid
    ;;
  *)
    echo "unknown ncbi-datasets smoke mode: $mode" >&2
    exit 2
    ;;
esac
