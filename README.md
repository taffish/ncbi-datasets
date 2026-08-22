# ncbi-datasets

`ncbi-datasets` packages the official
[NCBI Datasets](https://github.com/ncbi/datasets) command-line tools for
TAFFISH. It provides reproducible access to NCBI metadata and data packages
without installing the CLI on the host.

Package identity:

- name: `ncbi-datasets`
- command: `taf-ncbi-datasets`
- kind: `tool`
- version: `18.36.0-r1`
- container image: `ghcr.io/taffish/ncbi-datasets:18.36.0-r1`
- default upstream command: `datasets`
- companion command: `dataformat`
- datasets runtime version: `18.36.0`
- dataformat version output: `undefined` (upstream behavior)
- TAFFISH app license: Apache-2.0
- upstream license: Public Domain / United States Government Work
- upstream release: `v18.36.0`

## What This App Packages

The image installs the two official `v18.36.0` Linux release binaries:

- `datasets` queries NCBI metadata, downloads gene, genome, taxonomy, and virus
  data packages, and rehydrates dehydrated packages.
- `dataformat` converts NCBI JSON Lines reports or package metadata into TSV or
  Excel workbooks and can inspect data package catalogs.

Upstream 18.36.0 is a maintenance release focused on service performance and
reliability. Its client changes tolerate missing optional genome-download
summary fields and preserve taxonomy query labels more reliably, including for
numeric and merged taxon IDs. It does not add a release executable or a new
command-line dependency.

The packaged interface continues to include the sequence data-report plumbing
introduced in 18.35.0 and the corresponding `dataformat tsv sequence`
formatter with `summary` and `summary-no-query` templates.

The release archives are selected by container architecture and verified using
the SHA-256 digests published by GitHub. The binaries are statically linked and
kept unmodified. The final image adds only a minimal shell runtime, CA
certificates, upstream license text, provenance, and tiny offline test data.

## Scope

This app supports:

- metadata summaries by gene, genome, taxonomy, and virus identifiers
- sequence, annotation, and metadata data package downloads
- accession lists and standard upstream filters
- all-file gene and virus genome downloads via `--include all`
- dehydrated package creation and network rehydration
- JSON Lines metadata conversion to selected TSV fields
- sequence data-report conversion with the `summary` templates
- Excel workbook output
- data package catalog inspection
- optional NCBI API keys
- native `linux/amd64` and `linux/arm64` images

This app does not mirror NCBI databases, freeze remote records, bypass NCBI
rate limits, or bundle downloaded biological data.

Upstream also provides the hosted NCBI Datasets web interface. It is an
NCBI-operated external service, not an optional local GUI, plugin, or companion
binary in the CLI release archives, so it is outside this command-line app.

## Container Contents

- `datasets`: official NCBI Datasets CLI
- `dataformat`: official NCBI metadata formatter
- CA certificate bundle for outbound HTTPS
- BusyBox shell and basic file utilities
- upstream Public Domain notice and build provenance

No Conda, Python, compiler, source tree, biological database, or package cache
is retained in the final image.

## Usage

Show upstream help and version:

```sh
taf-ncbi-datasets -- --help
taf-ncbi-datasets -- --version
```

Summarize a genome accession as JSON:

```sh
taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
```

Return JSON Lines and format selected fields as TSV:

```sh
taf-ncbi-datasets datasets summary genome accession GCF_000001405.40 \
  --as-json-lines \
  | taf-ncbi-datasets dataformat tsv genome \
      --force \
      --fields accession,organism-name,assminfo-name
```

Download an E. coli genome package:

```sh
taf-ncbi-datasets datasets download genome accession GCF_000005845.2 \
  --include genome,gff3,protein \
  --filename ecoli.zip
```

Download every available file type for a gene or virus genome request:

```sh
taf-ncbi-datasets datasets download gene gene-id 672 \
  --include all --filename gene-all.zip

taf-ncbi-datasets datasets download virus genome taxon sars-cov-2 \
  --include all --filename virus-all.zip
```

Create TSV or Excel metadata from that package:

```sh
taf-ncbi-datasets dataformat tsv genome \
  --package ecoli.zip \
  --fields accession,organism-name,assminfo-name \
  > ecoli.tsv

taf-ncbi-datasets dataformat excel genome \
  --package ecoli.zip \
  --fields accession,organism-name,assminfo-name \
  --outputfile ecoli.xlsx
```

Format an existing sequence data report with the interface added in 18.35.0:

```sh
taf-ncbi-datasets dataformat tsv sequence \
  --inputfile sequence_data_report.jsonl \
  --template summary \
  --force \
  > sequences.tsv

taf-ncbi-datasets dataformat tsv sequence --list-templates
```

For a large genome set, request a dehydrated package, unpack it on the host,
and rehydrate its data files:

```sh
taf-ncbi-datasets datasets download genome taxon "Escherichia coli" \
  --dehydrated \
  --filename ecoli-dehydrated.zip

unzip ecoli-dehydrated.zip -d ecoli-dehydrated

taf-ncbi-datasets datasets rehydrate --directory ecoli-dehydrated
```

## Command Mode

The default command is `datasets`, but its words `summary`, `download`, and
`rehydrate` are subcommands while TAFFISH command mode treats a non-option
first argument as an executable name. Use the explicit executable form:

```sh
taf-ncbi-datasets datasets summary genome taxon human
```

Do not rely on bare `taf-ncbi-datasets summary ...` or
`taf-ncbi-datasets -- summary ...`; either form may ask command mode to run an
executable named `summary`. The separator remains correct for option-leading
arguments to the default command, such as `taf-ncbi-datasets -- --version`.

The companion executable is intentionally exposed through automatic command
mode:

```sh
taf-ncbi-datasets dataformat tsv genome --package ncbi_dataset.zip
```

## Inputs and Outputs

| Input | Meaning | Typical output |
| --- | --- | --- |
| accession, taxon, BioProject, gene ID/symbol | remote NCBI query identifiers | JSON/JSONL summary or data package zip |
| `--inputfile FILE` | newline-delimited query identifiers | summary or package for the listed records |
| NCBI Datasets package zip | downloaded package with metadata and selected files | TSV, XLSX, or catalog output |
| NCBI JSON Lines report | local metadata report | selected TSV fields or XLSX workbook |

Download contents depend on the domain and `--include` selection. NCBI data
packages normally store data under `ncbi_dataset/data/` and include metadata
and a package catalog.

## Network, API Keys, and Data

`datasets summary`, `datasets download`, and `datasets rehydrate` communicate
with live NCBI services over HTTPS. Their results can change as NCBI records,
schemas, and services evolve; the TAFFISH image fixes the client, not the
remote database snapshot.

`dataformat` can operate offline after a package or JSON Lines report is
available locally. No separate database installation or mount is needed.

NCBI currently documents a default rate limit of 5 requests per second and 10
requests per second with an API key. An API key is optional and is never
embedded in this image. Either pass it explicitly:

```sh
taf-ncbi-datasets datasets summary genome accession GCF_000001405.40 \
  --api-key "$NCBI_API_KEY"
```

or pass the host environment variable through the selected backend:

```sh
export NCBI_API_KEY="your-key"
TAFFISH_DOCKER_RUN_ARGS="-e NCBI_API_KEY" \
  taf-ncbi-datasets datasets summary genome accession GCF_000001405.40
```

For Podman, use `TAFFISH_PODMAN_RUN_ARGS="-e NCBI_API_KEY"`.

Large downloads require suitable disk space and network bandwidth. Use
`--dehydrated` plus `rehydrate` when recommended by NCBI, and follow NCBI
service policies and any terms attached to the retrieved records.

## Platform and Image Design

The image is native on both declared Linux architectures:

- `linux/amd64` uses `linux-amd64.cli.package.zip`
- `linux/arm64` uses `linux-arm64.cli.package.zip`

Both are official `v18.36.0` assets. Their exact archive digests, build
architecture, and selected target architecture are recorded at
`/opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt`.

The official binaries are statically linked Go executables. They are left
unstripped to preserve the distributed upstream artifacts. A minimal BusyBox
final stage and copied CA bundle avoid retaining a package manager or build
toolchain. On a native build, Dockerfile self-checks run exact identity, normal
help, and lightweight TSV/sequence transformations. During an amd64-hosted
arm64 cross-build, the Dockerfile verifies executable files and provenance
without executing target binaries under QEMU; the full per-platform runtime
smoke remains an independent release gate.

## Upstream Version Quirk

`datasets --version` reports `datasets version: 18.36.0`. The official
`dataformat` binary distributed in the same release currently prints
`undefined` for `dataformat version`; this is an upstream release behavior
also reported by upstream users, not a TAFFISH wrapper substitution.

The app therefore binds `dataformat` through the official release archive
digest, tag, commit, bundled provenance, command surface, and real TSV/XLSX
functional tests. TAFFISH does not patch or wrap the binary merely to rewrite
its version string.

## Reproducibility

- upstream repository: <https://github.com/ncbi/datasets>
- upstream release:
  <https://github.com/ncbi/datasets/releases/tag/v18.36.0>
- official CLI manual:
  <https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/>
- data package reference:
  <https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/data-packages/>
- API key guide:
  <https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/api-keys/>
- upstream commit: `09ab6707e79b198d5d939c82b4cd5ea6c1aa757d`
- Linux amd64 archive SHA-256:
  `32003304f61e70ebeb58b09a69ea1cef6f4f159683ced7eba063fcb8bb16f0ea`
- Linux arm64 archive SHA-256:
  `2af3b1d473b337ca276ed1db0c8493c630b34aca0b886ccfd6e8502287661abb`

## Testing

Independent offline smoke cases verify:

- exact `datasets` version and release provenance
- the known upstream `dataformat version` output
- genome/taxonomy summary, download, rehydrate, TSV, and Excel help surfaces
- the sequence formatter help surface and available template names
- a real local JSON Lines to TSV conversion with exact fields and values
- a real local sequence JSON Lines to summary TSV conversion
- a real local JSON Lines to XLSX conversion with output signature checks
- CA certificates and upstream license presence

The Dockerfile uses the architecture-aware build-time split described above;
the complete independent runtime smoke runs on each declared architecture.
Smoke never contacts NCBI, so Hub indexing remains deterministic and
offline-safe.

Development integration testing may additionally perform a tiny live NCBI
summary. That validates the current service path and TLS setup, but it cannot
be a reproducible index smoke and does not establish production-scale download
performance or scientific correctness of remote records.

## License and Citation

TAFFISH app packaging is Apache-2.0. Upstream NCBI Datasets is a United States
Government Work distributed under its Public Domain notice, retained in the
image. Retrieved NCBI records may have their own attribution or usage
considerations.

Research using NCBI Datasets should cite:

O'Leary NA et al. Exploring and retrieving sequence and metadata for species
across the tree of life with NCBI Datasets. *Scientific Data*.
2024;11:732. doi:
[`10.1038/s41597-024-03571-y`](https://doi.org/10.1038/s41597-024-03571-y).
