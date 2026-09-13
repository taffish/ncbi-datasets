# ncbi-datasets

`ncbi-datasets` packages the official [NCBI Datasets CLI](https://github.com/ncbi/datasets)
for TAFFISH. It fixes the client binaries, not the contents of NCBI's live services.

Package identity:

- command: `taf-ncbi-datasets`; kind: `tool`
- version: `18.37.0-r1`; image: `ghcr.io/taffish/ncbi-datasets:18.37.0-r1`
- default command: `datasets`; companion: `dataformat`
- native platforms: `linux/amd64`, `linux/arm64`
- packaging license: Apache-2.0; NCBI code: Public Domain / United States Government Work

## What This App Packages

The two unmodified official Linux binaries query/download selected NCBI data
packages, rehydrate dehydrated packages, and format local metadata as TSV or
XLSX. `dataformat catalog` also inspects package inventories.
[Upstream v18.37.0](https://github.com/ncbi/datasets/releases/tag/v18.37.0) corrects
type-material filtering and includes service maintenance. No new executable or
local model/database was added. The app does not modify upstream algorithms.

## Scope and Container Contents

The app exposes the official CLI command surface, sequence-report templates,
catalog extraction and optional API-key support. Static Go binaries run in a
BusyBox musl image with CA certificates, NCBI's notice, provenance, known
third-party notices/source archives and synthetic smoke fixtures. No Conda,
Python, compiler, database or model is bundled in the final runtime.

Official archives contain only `datasets` and `dataformat`. Official installation
instructions and public build targets do not supply a local GUI, optional GUI
extra or desktop companion. NCBI's hosted web portal is a separate external
service, not a bundled local GUI. XLSX is a file output, not a spreadsheet app.
No GPU, service port or display setup is required.

## Install and Use

Install with the normal TAFFISH Hub command after this candidate is published.
The pinned install command is `taf install ncbi-datasets 18.37.0-r1`.
Maintainers can run `taf check` and `taf build` in the source checkout;
installed users run the wrapper directly:

```sh
taf-ncbi-datasets -- --help
taf-ncbi-datasets -- --version
taf-ncbi-datasets datasets summary genome accession GCF_000001405.40 --as-json-lines > human.jsonl
taf-ncbi-datasets dataformat tsv genome --inputfile human.jsonl --fields accession,organism-name --force > human.tsv
taf-ncbi-datasets dataformat excel genome --inputfile human.jsonl --fields accession,organism-name --force --outputfile human.xlsx
taf-ncbi-datasets dataformat tsv sequence --list-templates
```

For existing packages use `--package ncbi_dataset.zip` instead of `--inputfile`.
Use a new output directory/name: downloads and workbook commands can overwrite
files. `--force` controls dataformat's type-check prompt, not installation safety.

## Command Mode

`summary`, `download` and `rehydrate` are subcommands, not executables. Include
`datasets` explicitly. `taf-ncbi-datasets -- summary ...` does not reliably bypass
automatic command mode. `--` is appropriate for option-leading arguments like
`--help`. The entrypoint remains a two-line container tag plus `datasets ::*ARGV*::`.

## Inputs and Outputs

| Input | Purpose | Output |
| --- | --- | --- |
| Explicit identifiers or query lists | Live NCBI requests | JSON/JSONL or selected zip package |
| Complete NCBI package | Local metadata/catalog extraction | TSV, XLSX, catalog |
| NCBI JSON Lines report | Local field/template conversion | TSV or XLSX |

Packages normally include metadata and an inventory below `ncbi_dataset/data/`.
Dehydrated packages omit payload files. Unpack into a new writable host directory
before `datasets rehydrate --directory DIR`; directory existence is not proof
of completion. Keep query, retrieval date, checksums and logs with saved results.

## Resources and Shared Inputs

Resource classification: **project-specific query results/input artifacts**, not
a CLI-installed database/model or selectable family required for inference. The
smallest reusable artifact is a selected completed package or saved JSONL report,
with its query, retrieval date, inventory and checksum. The client does not
discover or require a site-wide reference root. `dataformat` does not implicitly
download a database/model when processing local input.

A database installer, automatic resource discovery, `DB_PATH`/`MODEL_PATH`
override and auto-mount are N/A for this runtime dependency contract. This is not
based on catalog evolution or merely having an upstream downloader: the files
are explicit project inputs/outputs. Any downstream app using them as a managed
reference must define its own fixed resource contract.

The upstream downloader validates package structure and normally member
checksums, but writes the selected output directly. It is not an atomic shared
installer, and supplies no TAFFISH lock/ready manifest or site idempotence promise.
Interrupted downloads/rehydration must not be promoted as complete. Do not skip
member validation for a package that will be shared as complete.

An administrator can acquire and validate a selected package once, retain its
inventory/query/date/checksum, and expose a versioned snapshot below
`/srv/ncbi-inputs/`. Give intended users read/traverse access but not write access.
Users bind it read-only and write results in their own directories. Personal
archives work the same way. Rehydrate only a separate writable copy. The app does
not silently select/update/mirror an entire collection. Tiny shared-input tests
prove permissions and mounts, not production installation or scientific validity.

Software permission does not determine rights in downloaded records. Follow
[NCBI's data policies](https://www.ncbi.nlm.nih.gov/home/about/policies/) and
record-specific attribution/usage conditions before sharing or redistribution.
No downloaded biological data or API key is embedded in the image.

## Backend Usage and Capability Matrix

Select `TAFFISH_CONTAINER_BACKEND=docker`, `podman` or `apptainer`. All use the
same CLI arguments. Apptainer requires native Linux; on macOS use Docker/Podman
Linux VMs or a Linux server. Site policy may restrict networking or binds.

| Capability | Docker | Podman | Apptainer |
| --- | --- | --- | --- |
| NCBI HTTPS | Default engine network | Default engine network | Host/site network |
| Offline formatting | `TAFFISH_DOCKER_RUN_ARGS='--network none'` | `TAFFISH_PODMAN_RUN_ARGS='--network none'` | `TAFFISH_APPTAINER_RUN_ARGS='--net --network none'` where permitted |
| Read-only input | `TAFFISH_DOCKER_RUN_ARGS='-v /srv/ncbi-inputs:/inputs:ro'` | `TAFFISH_PODMAN_RUN_ARGS='-v /srv/ncbi-inputs:/inputs:ro'` | `TAFFISH_APPTAINER_RUN_ARGS='--bind /srv/ncbi-inputs:/inputs:ro'` |
| Optional exported API key | `TAFFISH_DOCKER_RUN_ARGS='-e NCBI_API_KEY'` | `TAFFISH_PODMAN_RUN_ARGS='-e NCBI_API_KEY'` | `APPTAINERENV_NCBI_API_KEY` |

Prefix the wrapper command with those assignments; combine network/bind/key
arguments when needed. For example:

```sh
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS='--network none -v /srv/ncbi-inputs:/inputs:ro' taf-ncbi-datasets dataformat tsv genome --package /inputs/ncbi_dataset.zip > report.tsv
```

Help includes all three shortest bind forms. Inputs remain read-only and the
current directory is the writable output location. No `VOLUME`, writable SIF
overlay, runtime `chmod` or root privileges are required. API-key tests use a
dummy value; no real credential is required or recorded.

## Reproducibility and Build Design

- tag: `v18.37.0`; commit: `c641ac110f9f4d756c67e678f646bb1b711b1dd3`
- amd64 archive SHA256: `f553860753712e6628e4f0f45a1388f9ad27e6f9d5d07549d1c87cd208955f4b`
- arm64 archive SHA256: `1c8784b02d42d99194f2d82a2636377f934ba8f414d1eb848210b39fb9cc6004`
- BusyBox `1.37.0-musl` final base and Debian builder are digest-pinned in Dockerfile
- context: app root, `docker build -f docker/Dockerfile .`, matching canonical Action

Per-platform provenance: `/opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt`.
Official binaries stay unmodified. Build-only tools and downloads do not enter
the final image. Native build self-checks use exact identity, ordinary help and
tiny non-rendering TSV transformations. Cross-builds check files/provenance
without executing target binaries; native runtime evidence is a separate gate.

`datasets --version` reports exactly `datasets version: 18.37.0`. Official
`dataformat version` still prints `undefined`; its identity is tied to the same
verified archive. The wrapper does not manufacture a version string.

## Testing and Candidate Boundary

Independent offline smoke covers commands, versions/provenance, ordinary help,
synthetic genome/sequence metadata to TSV, XLSX zip integrity/contents, and
malformed-input failure. Each command uses fresh `/tmp` scratch and no remote
query or biological sequence. Full build/backend/wrapper receipts are maintained
in Hub maintainer evidence outside the immutable app snapshot. Production
downloads, rate-limit behavior and scientific correctness are not proved here.

The notice review now covers the 20 observed external `dataformat` providers,
the pinned public `datasets` dependency declarations, Go runtime/vendor notices,
and base-runtime distribution materials. Source-path and DWARF evidence is bound
to the four official binary hashes. Original library notices, historical
copyright variants, file-level attributions and applicable source archives are
retained. In particular, gRPC NOTICE, XLSX's embedded attributions, pre-rename
grpc-gateway notices, and the available MPL module sources are included.

This is a **notice-obligation review, not a complete binary SBOM**. Official Go
build-info module tables are empty. `dataformat` notice-source references are
explicitly separate from its unknown linked versions; they must not be used to
claim exact dependency versions or determine vulnerability status. The observed
libraries' permissive notice requirements can be addressed without requiring
NCBI to publish all private application source or reply to a request first.
Any subsequently identified component or concrete unmet obligation requires
renewed review. The unlicensed `bou.ke/monkey` source is excluded: it is a public
module declaration without NCBI imports or observed binary linkage.

The new notice-bearing images passed native amd64/arm64 builds, 154 exact smoke
checks (22 items on seven normal/read-only/SIF routes), 76 real-wrapper checks,
44 notice-integrity positive/negative probes, 22 collector unit tests and four
error-code/diagnostic regressions. Docker and Podman passed normal and read-only
root checks on native amd64; Apptainer passed with an actual read-only amd64 SIF.
Native arm64 passed Podman normal/read-only and wrapper checks. Docker arm64 and
Apptainer arm64 were not separately validated: both evidence axes are covered,
with no app-specific runtime arguments, GUI/GPU or architecture-coupled mounts.

Final image IDs: amd64 `1359ab34…` (118,405,483 bytes), arm64 `52f07198…`
(117,461,945 bytes); amd64 SIF SHA256 `cda06866…`. About 73 MiB is retained
notice/source material, including original Go and library archives. These are
intentional distribution materials, not disposable download caches. Builder
Python, compilers and temporary download directories are absent from runtime.
Historical failed and partial-notice receipts remain in Hub maintainer evidence;
they are not relabelled as validation of these new images. Live production
downloads and complete scientific workflows remain outside these offline tests.

## Troubleshooting

- Subcommand missing: name `datasets` explicitly after the wrapper.
- Input missing: use a current-directory file or an explicit parent-directory bind.
- Read-only filesystem: write outputs in a writable working directory; do not
  rehydrate shared input or modify image installation paths.
- Invalid package: inspect transfer logs and use a newly completed, verified
  package; dehydrated archives are not complete downloads.
- Network/rate-limit error: follow site and NCBI service guidance. An API key
  does not guarantee access; do not expose it in logs or shared files.

## License and Citation

Packaging is Apache-2.0. NCBI's Public Domain notice text is retained at
`/opt/ncbi-datasets/share/licenses/ncbi-datasets/LICENSE.md`. The reviewed notice
bundle is under `/opt/ncbi-datasets/share/licenses/third-party/`; its lock records
source URLs, versions, SHA256 and upstream go.sum, and its inventory records
retained file paths/hashes. `sources/` contains the original public module ZIPs;
users may extract the relevant MPL-2.0 source and use it under that license.
The bundle's source versions are **not claims about dataformat's linked versions**.
`dataformat/` holds readable current/historical notices and copyright fragments;
`reference-sources/` retains their unmodified source references. `go-runtime/`
includes Go 1.23.4 sources and notices. `base/sources/` and `base/recipes/` retain
BusyBox 1.37.0 sources and the official base build scripts/configuration/patches;
musl, getconf, Buildroot and UTC timezone notices are included as applicable.
`notice-review.md` explains the release-specific reasoning and source boundaries.
`coverage.txt` records the audited notice review and `binary_sbom_complete=false`.
`/opt/ncbi-datasets/share/testdata/check-notices.sh` validates retained-file
integrity, including a separately pinned checksum-list hash and rejection of
missing, extra or symlinked files. It is not a legal certification. The copied
CA-certificate package notice is retained separately. External Go libraries,
source-reference materials and the base runtime keep their own terms.

O'Leary NA et al. *Exploring and retrieving sequence and metadata for species
across the tree of life with NCBI Datasets*. Scientific Data. 2024;11:732.
[doi:10.1038/s41597-024-03571-y](https://doi.org/10.1038/s41597-024-03571-y).

Further help: [CLI manual](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/),
[package reference](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/data-packages/),
[API keys](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/api-keys/).
