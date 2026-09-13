#!/usr/bin/env python3
"""固定来源告知收集器；区分许可参考版本与真实链接版本，不生成猜测 SBOM。"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import zipfile

DATAFORMAT_PROVIDERS = frozenset('''
github.com/frankban/quicktest github.com/google/btree github.com/google/go-cmp
github.com/grpc-ecosystem/grpc-gateway/v2 github.com/kr/pretty github.com/kr/text
github.com/mattn/go-isatty github.com/rogpeppe/fastuuid github.com/rogpeppe/go-internal
github.com/shabbyrobe/xmlwriter github.com/spf13/cobra github.com/spf13/pflag
github.com/tealeg/xlsx/v3 google.golang.org/genproto/googleapis/api
google.golang.org/genproto/googleapis/rpc google.golang.org/grpc
google.golang.org/protobuf golang.org/x/net golang.org/x/sys golang.org/x/text
'''.split())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or any(ord(c)<32 for c in name):
        raise ValueError('unsafe archive member: '+name)
    return name


def notice_name(name):
    return bool(re.match(r'(?i)^(licen[sc]e|copying|copyright|notice|authors|patents)([.\-_]|$)',
                         PurePosixPath(name).name))


def zip_contents(data, module, version, expected_h1):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate module archive member')
        prefix = module+'@'+version+'/'
        for name in names:
            safe_name(name)
            if not name.startswith(prefix):
                raise ValueError('module archive prefix mismatch: '+name)
        content = {n:archive.read(n) for n in sorted(names)}
    hashes = ''.join(f'{digest(data)}  {name}\n' for name, data in content.items())
    actual = 'h1:'+base64.b64encode(hashlib.sha256(hashes.encode()).digest()).decode()
    if actual != expected_h1:
        raise ValueError('upstream go.sum mismatch: '+module)
    return content


def validate_lock(lock, source_dir):
    if lock['schema'] != 2 or lock['ncbi_version'] != '18.37.0':
        raise ValueError('unsupported lock identity')
    if lock['binary_sbom_complete'] is not False:
        raise ValueError('cannot claim complete binary SBOM')
    refs = lock['dataformat_notice_references']
    if len(refs) != len(DATAFORMAT_PROVIDERS) or {m['module'] for m in refs} != DATAFORMAT_PROVIDERS:
        raise ValueError('dataformat provider inventory differs from independent binary audit')
    for m in refs:
        if m['runtime_version'] is not None:
            raise ValueError('notice reference is not evidence of linked runtime version')
        if not m['license_history'] or not m['notices'] or not m['go_sum'].startswith('h1:'):
            raise ValueError('missing dataformat notice/history/checksum evidence')
        if m['license_family'] not in ('MIT', 'BSD-3-Clause', 'Apache-2.0',
                                       'BSD-3-Clause AND MIT', 'Apache-2.0 AND BSD-3-Clause'):
            raise ValueError('reference-only coverage cannot satisfy an unreviewed license obligation')
    required_base = {'source-busybox', 'source-build-recipes', 'notice-source',
                     'permissive-notice-reference', 'public-domain-notice-reference', 'notice'}
    if {x['kind'] for x in lock['base_sources']} != required_base:
        raise ValueError('base source/notice coverage missing')
    base_names={'busybox-1.37.0.tar.bz2','docker-library-busybox-amd64.tar.gz',
                'docker-library-busybox-arm64.tar.gz','getconf.c','musl-1.2.5.tar.gz',
                'tzdata2025b.tar.gz','buildroot-COPYING','psmithuk-xlsx-LICENSE',
                'buildroot-system__device_table.txt','buildroot-system__skeleton__etc__group',
                'buildroot-system__skeleton__etc__passwd','buildroot-system__skeleton__etc__shadow'}
    if len(lock['base_sources'])!=len(base_names) or {x['archive'] for x in lock['base_sources']}!=base_names:
        raise ValueError('base source inventory incomplete or duplicated')
    for name in ('go.mod','go.sum'):
        if digest((source_dir/name).read_bytes()) != lock['public_'+name.replace('.','_')+'_sha256']:
            raise ValueError('public source lock changed: '+name)
    required = set(re.findall(r'^\s+([^\s]+) (v[^\s]+)',(source_dir/'go.mod').read_text(),re.M))
    listed = [(m['module'],m['source_version']) for m in lock['modules']]
    if len(listed) != len(set(listed)) or set(listed) != required:
        raise ValueError('module inventory differs from pinned public go.mod')
    sums = {(a,b):c for a,b,c in (l.split() for l in (source_dir/'go.sum').read_text().splitlines())}
    for m in lock['modules']:
        if m['go_sum'] != sums[(m['module'],m['source_version'])]:
            raise ValueError('lock differs from upstream go.sum')


def collect(lock_path, source_dir, cache, destination, download):
    lock = json.loads(lock_path.read_text())
    validate_lock(lock, source_dir)
    # 不覆盖既有证据/半成品；失败由调用方保留并选择新的目标目录。
    destination.mkdir(parents=True, exist_ok=False)
    cache.mkdir(parents=True, exist_ok=True)
    inventory = []

    def put(name, data, source):
        path = destination/safe_name(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise ValueError('duplicate destination: '+name)
        path.write_bytes(data)
        path.chmod(0o644)
        inventory.append(dict(path=name,sha256=digest(data),source=source))

    def fetch(item):
        name = safe_name(item['archive'])
        if '/' in name:
            raise ValueError('archive cache name must be a basename')
        path = cache/name
        if not path.exists():
            if not download:
                raise ValueError('missing cached source: '+name)
            subprocess.run(['curl','--retry','5','--retry-all-errors','-fsSL',item['url'],'-o',str(path)],check=True)
        data = path.read_bytes()
        if digest(data) != item['sha256']:
            raise ValueError('source archive SHA256 mismatch: '+name)
        return data

    put('notices.lock.json',lock_path.read_bytes(),'TAFFISH notice-source inventory; not a binary SBOM')
    for name in ('notice-review.md', 'binary-providers.json'):
        data=(source_dir/name).read_bytes()
        if digest(data) != lock['review_files'][name]:
            raise ValueError('review evidence changed: '+name)
        put(name,data,'TAFFISH release-specific notice review')
    for name in ('go.mod','go.sum'):
        put('public-datasets/'+name,(source_dir/name).read_bytes(),
            'https://github.com/ncbi/datasets/blob/'+lock['ncbi_commit']+'/client/apps/public/Datasets/v2/'+name)
    for module in lock['modules']:
        if module['module'] == 'bou.ke/monkey':
            # 声明在公开 go.mod 中，但没有公开源码 import/两架构二进制链接证据。
            # 其 LICENSE 不授予使用权限；不能因为列在依赖锁中就打包它的源码。
            # 只保留我们自己的来源/排除记录，不下载、执行或复制该模块内容。
            put('excluded/bou.ke__monkey.txt',
                ('module=bou.ke/monkey\nsource_version=v1.0.2\n'
                 'included_in_notice_or_source_payload=false\n'
                 'reason=license grants no use permission; no import or linked-package evidence in audited NCBI binaries\n'
                 'license_url=https://github.com/bouk/monkey/blob/v1.0.2/LICENSE.md\n').encode(),
                'TAFFISH exclusion record; not third-party source or license text')
            continue
        data = fetch(module)
        files = zip_contents(data,module['module'],module['source_version'],module['go_sum'])
        selected = sorted(n for n in files if notice_name(n))
        if not selected or selected != sorted(module['notices']):
            raise ValueError('notice membership changed: '+module['module'])
        label = module['module'].replace('/','__')+'@'+module['source_version']
        for name in selected:
            prefix = module['module']+'@'+module['source_version']+'/'
            put('modules/'+label+'/'+name[len(prefix):],files[name],module['url']+'#'+name)
        # 原样保存全部公开模块源码（含文件头和 MPL 对应源码），不只保存根 LICENSE。
        # 含 test-only/非目标平台代码，是保守来源集合，不冒充实际链接模块 SBOM。
        put('sources/'+module['archive'],data,module['url'])
    for module in lock['dataformat_notice_references']:
        data=fetch(module)
        version=module['notice_source_version']
        files=zip_contents(data,module['module'],version,module['go_sum'])
        selected=sorted(n for n in files if notice_name(n))
        if selected != sorted(module['notices']):
            raise ValueError('dataformat notice membership changed: '+module['module'])
        prefix=module['module']+'@'+version+'/'
        label=module['module'].replace('/','__')
        for name in selected:
            put('dataformat/'+label+'/'+name[len(prefix):],files[name],module['url']+'#'+name)
        put('dataformat/'+label+'/copyright-fragments.txt',copyright_fragments(files),module['url'])
        # 参考源码保留原始文件头/嵌入许可；不是私有 dataformat 的对应源码或实际版本证明。
        put('reference-sources/'+module['archive'],data,module['url'])
        seen=set()
        for history in module['license_history']:
            if history['sha256'] in seen:
                continue
            seen.add(history['sha256'])
            item=dict(history,archive='history-'+history['sha256']+'.txt')
            put('dataformat/'+label+'/history/'+history['sha256']+'.txt',fetch(item),history['url'])
    for item in lock['base_sources']:
        data=fetch(item)
        if item['kind']=='source-busybox':
            put('base/sources/'+item['archive'],data,item['url'])
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:*') as archive:
                for member in archive.getmembers():
                    if member.isfile() and notice_name(member.name):
                        put('base/busybox/'+safe_name(member.name),archive.extractfile(member).read(),item['url']+'#'+member.name)
        elif item['kind']=='source-build-recipes':
            # 官方仓库还包含其它架构的 rootfs tar；只保留本基础镜像使用的构建脚本和补丁。
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
                found=[]
                for member in archive.getmembers():
                    rel=member.name.split('/',1)[-1]
                    if member.isfile() and rel in item['members']:
                        found.append(rel)
                        put('base/recipes/'+item['architecture']+'/'+safe_name(rel),archive.extractfile(member).read(),item['url']+'#'+member.name)
                if sorted(found)!=sorted(item['members']):
                    raise ValueError('base build recipe or patch missing')
        elif item['kind'] in ('permissive-notice-reference','public-domain-notice-reference'):
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
                found=[]
                for member in archive.getmembers():
                    if member.isfile() and notice_name(member.name):
                        found.append(member.name)
                        put('base/'+item['archive']+'/'+safe_name(member.name),archive.extractfile(member).read(),item['url']+'#'+member.name)
                if not found:raise ValueError('base reference has no notice')
            if item['kind']=='permissive-notice-reference':
                put('base/reference-sources/'+item['archive'],data,item['url'])
        else:
            put('base/'+item['archive'],data,item['url'])
    go = lock['go']
    go_data=fetch(go)
    # 标准库内还有 Sun/第三方文件级告知；完整原始来源不是可丢弃下载 cache。
    put('go-runtime/sources/'+go['archive'],go_data,go['url'])
    with tarfile.open(fileobj=io.BytesIO(go_data),mode='r:gz') as archive:
        selected = [m for m in archive.getmembers() if m.isfile() and notice_name(m.name)]
        if not any(m.name=='go/LICENSE' for m in selected):
            raise ValueError('Go runtime license missing')
        for member in selected:
            put('go-runtime/'+safe_name(member.name),archive.extractfile(member).read(),go['url']+'#'+member.name)
    state = ('coverage=audited-provider-notices-and-required-source-materials\n'
             'notice_obligations_review=complete-for-audited-components\n'
             'binary_sbom_complete=false\n'
             'dataformat_dependency_versions=unknown-not-claimed\n'
             'source_archives_include_test_and_non_target_platform_code=true\n')
    put('coverage.txt',state.encode(),'TAFFISH explicit review state')
    put('inventory.json',(json.dumps(inventory,indent=2)+'\n').encode(),'TAFFISH collected file provenance')
    sums = ''.join(f"{i['sha256']}  {i['path']}\n" for i in inventory)
    (destination/'SHA256SUMS').write_text(sums)
    print(f'[OK] {len(lock["modules"])} public source declarations, 20 dataformat providers, runtime notices; {len(inventory)} files; binary SBOM not claimed')


def copyright_fragments(files):
    """原文保留含版权/许可的注释块；完整参考 ZIP 另存，避免依靠启发式丢失原文。"""
    blocks={}
    for name,data in sorted(files.items()):
        if not name.endswith(('.go','.c','.h','.s','.proto')):
            continue
        content=data.decode('utf-8',errors='replace')
        for match in re.finditer(r'/\*[\s\S]*?\*/|(?m:^\s*//[^\n]*(?:\n|$))+',content):
            block=match.group()
            if re.search(r'(?i)copyright|SPDX-License-Identifier|Permission is hereby granted',block):
                blocks.setdefault(block,[]).append(name)
    return ('Notice-source reference only; see notices.lock.json. Original text follows.\n\n'+
            '\n\n'.join('Source files: '+', '.join(names)+'\n'+block for block,names in blocks.items())+'\n').encode()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--download',action='store_true')
    a = p.parse_args()
    collect(a.lock,a.source,a.cache,a.out,a.download)
