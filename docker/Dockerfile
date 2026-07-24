FROM debian:bookworm-slim AS builder

ARG TARGETARCH
ARG NCBI_DATASETS_VERSION=18.33.1
ARG NCBI_DATASETS_COMMIT=a8bc1f5599cd15c2cfb4c975cdfb151c26e2310f
ARG NCBI_DATASETS_AMD64_SHA256=d32e0b6646e80274c07dae88eb5231c254cc6df1d96c46e9372424f7a8d64e68
ARG NCBI_DATASETS_ARM64_SHA256=5d46da87b6206004a30e17ab35c89cf2090a655f4f117f85e69f4ef7f8e93d57

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    apt-get -o Acquire::Retries=3 update; \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
        ca-certificates \
        curl \
        unzip; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) \
        asset="linux-amd64.cli.package.zip"; \
        asset_sha256="${NCBI_DATASETS_AMD64_SHA256}" \
        ;; \
      arm64) \
        asset="linux-arm64.cli.package.zip"; \
        asset_sha256="${NCBI_DATASETS_ARM64_SHA256}" \
        ;; \
      *) \
        echo "unsupported TARGETARCH: ${TARGETARCH}" >&2; \
        exit 1 \
        ;; \
    esac; \
    asset_url="https://github.com/ncbi/datasets/releases/download/v${NCBI_DATASETS_VERSION}/${asset}"; \
    curl --retry 5 --retry-delay 2 --retry-all-errors -fsSL "${asset_url}" -o cli.package.zip; \
    echo "${asset_sha256}  cli.package.zip" | sha256sum -c -; \
    unzip -q cli.package.zip; \
    test -s datasets; \
    test -s dataformat; \
    install -d /opt/ncbi-datasets/bin /opt/ncbi-datasets/share/doc/ncbi-datasets; \
    install -m 0755 datasets dataformat /opt/ncbi-datasets/bin/; \
    { \
      printf "upstream_name=NCBI Datasets\n"; \
      printf "upstream_repo=https://github.com/ncbi/datasets\n"; \
      printf "upstream_version=%s\n" "${NCBI_DATASETS_VERSION}"; \
      printf "upstream_tag=v%s\n" "${NCBI_DATASETS_VERSION}"; \
      printf "upstream_commit=%s\n" "${NCBI_DATASETS_COMMIT}"; \
      printf "release_asset=%s\n" "${asset}"; \
      printf "release_asset_url=%s\n" "${asset_url}"; \
      printf "release_asset_sha256=%s\n" "${asset_sha256}"; \
      printf "linux_amd64_asset_sha256=%s\n" "${NCBI_DATASETS_AMD64_SHA256}"; \
      printf "linux_arm64_asset_sha256=%s\n" "${NCBI_DATASETS_ARM64_SHA256}"; \
      printf "target_arch=%s\n" "${TARGETARCH}"; \
      printf "packaged_commands=datasets,dataformat\n"; \
      printf "dataformat_version_output=undefined (upstream release behavior)\n"; \
      printf "online_service_required=datasets summary/download/rehydrate\n"; \
      printf "offline_local_processing=dataformat tsv/excel/catalog\n"; \
    } > /opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt; \
    rm -rf /tmp/build

FROM busybox:1.37.0-musl

ENV PATH=/opt/ncbi-datasets/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /opt/ncbi-datasets /opt/ncbi-datasets
COPY docker/upstream-LICENSE.md /opt/ncbi-datasets/share/licenses/ncbi-datasets/LICENSE.md
COPY docker/ncbi-datasets-smoke.sh /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh

RUN set -eux; \
    mkdir -p /usr/local/bin; \
    ln -s /opt/ncbi-datasets/bin/datasets /usr/local/bin/datasets; \
    ln -s /opt/ncbi-datasets/bin/dataformat /usr/local/bin/dataformat; \
    chmod 0755 /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh; \
    datasets --version 2>&1 | grep -Fx "datasets version: 18.33.1" >/dev/null; \
    dataformat version 2>&1 | grep -Fx "undefined" >/dev/null; \
    datasets --help 2>&1 | grep -F "Data Retrieval Commands" >/dev/null; \
    datasets summary genome accession --help 2>&1 | grep -F -- "--as-json-lines" >/dev/null; \
    datasets download genome accession --help 2>&1 | grep -F -- "--dehydrated" >/dev/null; \
    datasets rehydrate --help 2>&1 | grep -F -- "--directory" >/dev/null; \
    dataformat --help 2>&1 | grep -F "Formatting Commands" >/dev/null; \
    dataformat tsv genome --help 2>&1 | grep -F -- "--fields" >/dev/null; \
    dataformat excel genome --help 2>&1 | grep -F -- "--outputfile" >/dev/null; \
    /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh all; \
    test -s /etc/ssl/certs/ca-certificates.crt; \
    test -s /opt/ncbi-datasets/share/licenses/ncbi-datasets/LICENSE.md

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=ncbi-datasets
