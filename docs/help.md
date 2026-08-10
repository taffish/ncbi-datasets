ncbi-datasets 18.35.0-r1

Purpose:
  Query/download NCBI data packages with datasets, then convert NCBI JSON
  Lines metadata to TSV or Excel with dataformat.

Usage:
  taf-ncbi-datasets -- --help
  taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
  taf-ncbi-datasets dataformat tsv genome --package ncbi_dataset.zip

Common workflows:
  taf-ncbi-datasets datasets summary genome taxon "Escherichia coli"
  taf-ncbi-datasets datasets download genome accession GCF_000005845.2 \
    --include genome,gff3,protein --filename ecoli.zip
  taf-ncbi-datasets datasets download gene gene-id 672 --include all
  taf-ncbi-datasets dataformat tsv genome --package ecoli.zip \
    --fields accession,organism-name,assminfo-name
  taf-ncbi-datasets dataformat excel genome --package ecoli.zip \
    --outputfile ecoli.xlsx
  taf-ncbi-datasets dataformat tsv sequence \
    --inputfile sequence_data_report.jsonl --template summary --force

Packaged commands:
  datasets     Query metadata, download data packages, and rehydrate packages.
  dataformat   Convert package metadata to TSV or Excel and inspect catalogs.

Command-mode note:
  summary, download, and rehydrate are datasets subcommands, not executables.
  Use "taf-ncbi-datasets datasets summary ...".
  Bare "taf-ncbi-datasets summary ..." and the form with "-- summary" may ask
  command mode to run an executable named summary.
  Use "taf-ncbi-datasets dataformat ..." for the companion command.

Upstream help and version:
  taf-ncbi-datasets -- --help
  taf-ncbi-datasets -- --version
  taf-ncbi-datasets datasets summary --help
  taf-ncbi-datasets datasets download --help
  taf-ncbi-datasets dataformat --help

Inputs:
  Accessions, taxon names/IDs, BioProject IDs, gene symbols/IDs, or input lists.
  NCBI Datasets zip packages and JSON Lines data reports for dataformat.

Key outputs:
  JSON or JSON Lines metadata summaries.
  Zip data packages containing selected sequences, annotations, and reports.
  TSV tables or XLSX workbooks generated from NCBI metadata.

Large downloads:
  Use datasets download ... --dehydrated for large genome sets, unpack the zip,
  then run datasets rehydrate --directory DIR. Download and rehydrate require
  outbound HTTPS and enough local disk space.

Network and API keys:
  datasets summary, download, and rehydrate use live NCBI services.
  dataformat can process existing local reports and packages offline.
  Pass a key with --api-key or forward NCBI_API_KEY using TAFFISH Docker/Podman
  runtime arguments. Keys and downloaded data are not embedded in the image.

Platform and resources:
  Native linux/amd64 and linux/arm64 images use official release binaries.
  The image contains CA certificates but no biological database or reference
  data. Runtime storage and transfer depend on the requested NCBI package.

Boundaries:
  NCBI service availability, rate limits, data licenses, and record contents
  remain external to this app.
  Version 18.35.0 adds dataformat tsv sequence with summary templates and
  sequence report metadata such as update date.
  The official dataformat 18.35.0 binary prints "undefined" for its version
  command. Package identity is pinned by the official archive checksums,
  datasets --version, release tag, commit, and functional dataformat tests.
  Offline smoke does not contact NCBI or validate production-scale downloads.
Detailed documentation:
  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/
  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/data-packages/
  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/api-keys/
  https://github.com/ncbi/datasets

Wrapper options:
  taf-ncbi-datasets --help       Show this TAFFISH help.
  taf-ncbi-datasets --version    Show TAFFISH wrapper version.
  taf-ncbi-datasets --compile    Compile the TAFFISH wrapper.
  taf-ncbi-datasets -- --help    Pass options to the default datasets command.

Citation:
  O'Leary NA et al. Scientific Data. 2024;11:732.
  doi:10.1038/s41597-024-03571-y
