#!/bin/sh
set -eu

mode="${1:-all}"

write_genome_report() {
  output="$1"
  printf '%s\n' \
    '{"accession":"GCF_TAFFISH.1","organism":{"organismName":"TAFFISH test organism","taxId":424242}}' \
    > "$output"
}

run_tsv() {
  tmp="/tmp/taf-ncbi-datasets-tsv"
  rm -rf "$tmp"
  mkdir -p "$tmp"
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

run_excel() {
  tmp="/tmp/taf-ncbi-datasets-excel"
  rm -rf "$tmp"
  mkdir -p "$tmp"
  write_genome_report "$tmp/assembly_data_report.jsonl"
  dataformat excel genome \
    --force \
    --inputfile "$tmp/assembly_data_report.jsonl" \
    --fields accession,organism-name,organism-tax-id \
    --outputfile "$tmp/report.xlsx" \
    > "$tmp/dataformat.log"
  test -s "$tmp/report.xlsx"
  test "$(head -c 2 "$tmp/report.xlsx")" = "PK"
  grep -F "saved Excel workbook" "$tmp/dataformat.log" >/dev/null
  rm -rf "$tmp"
}

case "$mode" in
  tsv)
    run_tsv
    ;;
  excel)
    run_excel
    ;;
  all)
    run_tsv
    run_excel
    ;;
  *)
    echo "unknown ncbi-datasets smoke mode: $mode" >&2
    exit 2
    ;;
esac
