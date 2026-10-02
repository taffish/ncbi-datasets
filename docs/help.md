ncbi-datasets 18.38.0-r1

Purpose:
  Query NCBI metadata with datasets; convert existing JSON Lines or package
  metadata to TSV/Excel with dataformat.

Common tasks:
  taf-ncbi-datasets datasets summary genome accession GCF_000001405.40 --as-json-lines > human.jsonl
  taf-ncbi-datasets datasets summary genome accession GCF_000001405.40 --pretty
  taf-ncbi-datasets dataformat tsv genome --inputfile human.jsonl --fields accession,organism-name --force > human.tsv
  taf-ncbi-datasets dataformat tsv genome --package ncbi_dataset.zip --fields accession,organism-name
  taf-ncbi-datasets dataformat excel genome --package ncbi_dataset.zip --outputfile report.xlsx
  taf-ncbi-datasets dataformat tsv sequence --inputfile sequence_data_report.jsonl --template summary --force
  taf-ncbi-datasets dataformat tsv sequence --list-templates

Inputs and outputs:
  Query inputs: an accession/identifier or an upstream-supported identifier list.
  Local inputs: NCBI JSON Lines reports or complete NCBI Datasets zip packages.
  Outputs: JSON/JSONL metadata, selected TSV fields, or an XLSX workbook.
  --pretty is for display; omit it from --as-json-lines input for dataformat.
  Large queries should avoid --pretty because upstream buffers the response.
  For spaces use literal inner quotes: --inputfile "'input with spaces.jsonl'".
  Work in a writable directory. Current-directory files are bound by the wrapper;
  paths elsewhere require an explicit bind. Use new output names to avoid overwrite.

Command mode:
  Include datasets before its subcommands: datasets summary/download/rehydrate.
  Bare "taf-ncbi-datasets summary ..." can try to execute a command named summary.
  Use "taf-ncbi-datasets -- --help" for default-command options, and
  "taf-ncbi-datasets dataformat ..." for the companion formatter.

Network/backend selection:
  summaries, downloads and rehydrate need outbound HTTPS to live NCBI services.
  Formatting existing local reports/packages works offline.
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
  Apptainer (native Linux):
    TAFFISH_CONTAINER_BACKEND=apptainer taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
  On macOS use Docker/Podman, or run the Apptainer wrapper on a Linux host.
  A site policy can still block HTTPS; retry later for service/rate-limit errors.

Read-only shared inputs outside the working directory:
  An administrator may provide a completed package under /srv/ncbi-inputs.
  Keep outputs in your own working directory; do not rehydrate a read-only input.
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS='-v /srv/ncbi-inputs:/inputs:ro' taf-ncbi-datasets dataformat tsv genome --package /inputs/ncbi_dataset.zip
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS='-v /srv/ncbi-inputs:/inputs:ro' taf-ncbi-datasets dataformat tsv genome --package /inputs/ncbi_dataset.zip
  Apptainer:
    TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS='--bind /srv/ncbi-inputs:/inputs:ro' taf-ncbi-datasets dataformat tsv genome --package /inputs/ncbi_dataset.zip

Optional API key:
  Export NCBI_API_KEY privately, then forward it for the selected backend:
  Docker:    TAFFISH_DOCKER_RUN_ARGS='-e NCBI_API_KEY'
  Podman:    TAFFISH_PODMAN_RUN_ARGS='-e NCBI_API_KEY'
  Apptainer: export APPTAINERENV_NCBI_API_KEY="$NCBI_API_KEY"
  Prefix the Docker/Podman command with that assignment; combine it with any bind
  arguments already needed. Never put keys in public logs or shared files.

Immediate notes:
  No database/model installation is required by the CLI. Downloaded packages are
  project inputs, not a snapshot of all NCBI records. Save query/date/checksums.
  A dehydrated package is incomplete: unpack it into a new writable directory,
  then use datasets rehydrate --directory DIR with enough disk space and HTTPS.
  dataformat version prints "undefined" upstream; use datasets --version for identity.

More help:
  taf-ncbi-datasets datasets download --help
  taf-ncbi-datasets dataformat --help
  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/
  https://github.com/taffish/ncbi-datasets

Wrapper options:
  taf-ncbi-datasets --help       Show this TAFFISH help.
  taf-ncbi-datasets --version    Show TAFFISH wrapper version.
  taf-ncbi-datasets --compile    Print the generated wrapper shell.
  taf-ncbi-datasets -- --version Show upstream datasets version.
