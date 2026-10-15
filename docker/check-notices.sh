#!/bin/sh
# 校验经过独立审查的固定材料集；完整性校验不冒充法律保证或完整 SBOM。
set -eu
trap 'status=$?; if [ "$status" -ne 0 ]; then printf "[FAIL] notice-integrity exit=%s\n" "$status" >&2; fi' 0
root=${1:-/opt/ncbi-datasets/share/licenses/third-party}
cd "$root"
printf '%s\n' '472d3d0bfe04c41d169ee638797ffdd6646feac0411df5214f1ab76688ffb4bf  SHA256SUMS' | sha256sum -c - >/dev/null
sha256sum -c SHA256SUMS >/dev/null
test "$(find . -type f | wc -l)" -eq 215
test -z "$(find . -type l)"
grep -Fx 'notice_obligations_review=complete-for-audited-components' coverage.txt >/dev/null
grep -Fx 'binary_sbom_complete=false' coverage.txt >/dev/null
test ! -e sources/bou.ke__monkey@v1.0.2.zip
test ! -e modules/bou.ke__monkey@v1.0.2
printf '%s\n' '[OK] audited notice/source materials intact; no complete binary SBOM claim'
