ncbi-datasets 18.33.1-r1

Purpose:
  Query and download NCBI gene, genome, taxonomy, and virus data packages with
  datasets, then convert NCBI JSON Lines metadata to TSV or Excel with
  dataformat.

Usage:
  taf-ncbi-datasets -- --help
  taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
  taf-ncbi-datasets dataformat tsv genome --package ncbi_dataset.zip

Common workflows:
  taf-ncbi-datasets datasets summary genome taxon "Escherichia coli"
  taf-ncbi-datasets datasets download genome accession GCF_000005845.2 \
    --include genome,gff3,protein --filename ecoli.zip
  taf-ncbi-datasets dataformat tsv genome --package ecoli.zip \
    --fields accession,organism-name,assminfo-name
  taf-ncbi-datasets dataformat excel genome --package ecoli.zip \
    --outputfile ecoli.xlsx

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
  An API key is optional. Pass it with --api-key or pass NCBI_API_KEY into the
  container with TAFFISH_DOCKER_RUN_ARGS="-e NCBI_API_KEY" or the equivalent
  Podman setting. Keys and downloaded data are not embedded in the image.

Platform and resources:
  Native linux/amd64 and linux/arm64 images use official release binaries.
  The image contains CA certificates but no biological database or reference
  data. Runtime storage and transfer depend on the requested NCBI package.

Boundaries:
  NCBI service availability, rate limits, data licenses, and record contents
  remain external to this app.
  The official dataformat 18.33.1 binary prints "undefined" for its version
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
