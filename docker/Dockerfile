FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS builder

ARG BUILDARCH
ARG TARGETARCH
ARG NCBI_DATASETS_VERSION=18.37.0
ARG NCBI_DATASETS_COMMIT=c641ac110f9f4d756c67e678f646bb1b711b1dd3
ARG NCBI_DATASETS_AMD64_SHA256=f553860753712e6628e4f0f45a1388f9ad27e6f9d5d07549d1c87cd208955f4b
ARG NCBI_DATASETS_ARM64_SHA256=1c8784b02d42d99194f2d82a2636377f934ba8f414d1eb848210b39fb9cc6004

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    apt-get -o Acquire::Retries=3 update; \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
        ca-certificates \
        curl \
        python3 \
        unzip; \
    rm -rf /var/lib/apt/lists/*

COPY docker/collect-notices.py docker/notices.lock.json /tmp/notice-input/
COPY docker/public-source/ /tmp/notice-input/public-source/
RUN set -eux; \
    python3 /tmp/notice-input/collect-notices.py \
      --lock /tmp/notice-input/notices.lock.json \
      --source /tmp/notice-input/public-source \
      --cache /tmp/notice-cache \
      --out /opt/ncbi-datasets/share/licenses/third-party --download; \
    install -d /opt/ncbi-datasets/share/licenses/ca-certificates; \
    cp /usr/share/doc/ca-certificates/copyright /opt/ncbi-datasets/share/licenses/ca-certificates/; \
    rm -rf /tmp/notice-input /tmp/notice-cache

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
      printf "build_arch=%s\n" "${BUILDARCH}"; \
      printf "target_arch=%s\n" "${TARGETARCH}"; \
      printf "packaged_commands=datasets,dataformat\n"; \
      printf "dataformat_version_output=undefined (upstream release behavior)\n"; \
      printf "online_service_required=datasets summary/download/rehydrate\n"; \
      printf "offline_local_processing=dataformat tsv/excel/catalog\n"; \
    } > /opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt; \
    rm -rf /tmp/build

FROM busybox:1.37.0-musl@sha256:fc6dddc4c44b1bfe37f41cae8e67d1693828e8f42a91862816d7953e2c9d3f23

ARG BUILDARCH
ARG TARGETARCH

ENV PATH=/opt/ncbi-datasets/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /opt/ncbi-datasets /opt/ncbi-datasets
COPY docker/upstream-LICENSE.md /opt/ncbi-datasets/share/licenses/ncbi-datasets/LICENSE.md
COPY docker/ncbi-datasets-smoke.sh /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh
COPY docker/check-notices.sh /opt/ncbi-datasets/share/testdata/check-notices.sh

RUN set -eux; \
    mkdir -p /usr/local/bin; \
    ln -s /opt/ncbi-datasets/bin/datasets /usr/local/bin/datasets; \
    ln -s /opt/ncbi-datasets/bin/dataformat /usr/local/bin/dataformat; \
    chmod 0755 /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh; \
    chmod 0755 /opt/ncbi-datasets/share/testdata/check-notices.sh; \
    /opt/ncbi-datasets/share/testdata/check-notices.sh; \
    test -n "${BUILDARCH}"; \
    test -n "${TARGETARCH}"; \
    if [ "${BUILDARCH}" = "${TARGETARCH}" ]; then \
      datasets --version 2>&1 | grep -Fx "datasets version: 18.37.0" >/dev/null; \
      dataformat version 2>&1 | grep -Fx "undefined" >/dev/null; \
      datasets --help 2>&1 | grep -F "Data Retrieval Commands" >/dev/null; \
      dataformat --help 2>&1 | grep -F "Formatting Commands" >/dev/null; \
      /opt/ncbi-datasets/share/testdata/ncbi-datasets-smoke.sh buildtime; \
    else \
      test -x /opt/ncbi-datasets/bin/datasets; \
      test -x /opt/ncbi-datasets/bin/dataformat; \
      grep -Fx "build_arch=${BUILDARCH}" /opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt >/dev/null; \
      grep -Fx "target_arch=${TARGETARCH}" /opt/ncbi-datasets/share/doc/ncbi-datasets/source.txt >/dev/null; \
    fi; \
    test -s /etc/ssl/certs/ca-certificates.crt; \
    test -s /opt/ncbi-datasets/share/licenses/ncbi-datasets/LICENSE.md

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=ncbi-datasets
