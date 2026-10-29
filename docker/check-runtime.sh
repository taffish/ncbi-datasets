#!/bin/sh
# Match the complete runtime string only after checking the original exit code.
set -eu
check() {
  expected=$1
  shift
  if actual=$("$@" 2>&1); then
    :
  else
    status=$?
    printf '[FAIL] runtime-identity command=%s exit=%s\n' "$1" "$status" >&2
    printf '%s\n' "$actual" | tail -n 20 >&2
    exit "$status"
  fi
  if [ "$actual" != "$expected" ]; then
    printf '[FAIL] runtime-identity command=%s unexpected-output\n' "$1" >&2
    printf '%s\n' "$actual" | tail -n 20 >&2
    exit 1
  fi
}
check 'datasets version: 18.40.0' datasets --version
check 'undefined' dataformat version
printf '%s\n' '[OK] runtime identity: datasets 18.40.0; official dataformat undefined'
