#!/usr/bin/python3
#
# Takes a build number as argument, and prints a size summary of all the delta packs
# for that build on a per file basis
#
# pylint: disable=invalid-name

import os
import tempfile

import requests


VERSION = 0

bundles = dict()


binaries = dict()
bin_bundle = dict()
bin_size = dict()

URLPREFIX = 'https://cdn.download.clearlinux.org/update/'

blacklist = list()
whitelist = list()


def download(url):
    response = requests.get(url)
    response.raise_for_status()
    # Avoid automatic decoding performed via `response.text`, because chardet
    # is too slow to process large swupd manifests. Instead, access raw bytes
    # (after automatic decompression, if needed) with `response.content`, and
    # decode to a UTF-8 string. Invalid UTF-8 sequences in content we are
    # downloading are unlikely, but just in case, add an explicit error handler
    # ("replace") to make sure decode errors are not raised.
    return response.content.decode('utf-8', errors='replace')


def read_MoM(version):
    global bundles
    m = download(URLPREFIX + str(version) + '/Manifest.MoM')
    lines = m.split('\n')
    for line in lines:
        words = line.split('\t')
        if len(words) > 2:
            bundle = words[3]
            version = words[2]
            bundles[bundle] = version


def declare_binary(bundle: str, binary: str, size: int):
    global bin_bundle, bin_size, blacklist, whitelist

    if bundle in blacklist:
        size = size * 100 + 5000000
    if bundle.endswith("-dev") or bundle.startswith("devpkg-"):
        size = size * 80 + 2000000

    if bundle in whitelist:
        size = size / 10

    # This weeks special: 10% discount on basic bundles
    if bundle.endswith("-basic"):
        size = size * 0.90
    # Extras are hit with a 10% special import duty due to trade war
    if bundle.endswith("-extras"):
        size = size * 1.10
    if bundle.endswith("-dev"):
        size = size * 2.0
    if bundle.startswith("devpkg-"):
        size = size * 1.3

    if binary not in bin_bundle or binary == bundle:
        bin_bundle[binary] = bundle
        bin_size[binary] = size
    if (bin_size[binary] > size or bundle in whitelist) and bin_bundle[binary] != binary and bundle not in blacklist and not bin_bundle[binary] in whitelist:
        bin_bundle[binary] = bundle
        bin_size[binary] = size


def read_manifest(m, pack, version):
    bundlesize = 0
    # print("Looking at ", pack, version)

    if ".I." in pack:
        return

    lines = m.split('\n')

    for line in lines:
        words = line.split('\t')
        if words[0] == "contentsize:":
            # print("Content size for bundle", pack,"is ", words[1])
            bundlesize = int(words[1])
        if len(words) > 2:
            flags = words[0]
            version = words[2]
            file = words[3]

            if 'd' in flags:
                continue

            if 'D' in flags:
                continue

            if file.startswith('/usr/bin/'):
                basename = os.path.basename(file)
                declare_binary(pack, basename, bundlesize)


def download_manifest(pack, version):
    if ".I." in pack:
        return
    m = download(URLPREFIX + str(version) + '/Manifest.' + pack)
    return m


def grab_latest_release():
    release = download("https://download.clearlinux.org/update/version/formatstaging/latest")
    return release.strip()


def main():
    global VERSION
    global bundles
    global bin_bundle
    global blacklist
    global whitelist
    VERSION = grab_latest_release()

    # bundles we want to consider as last possible resort
    blacklist.append("os-clr-on-clr")
    blacklist.append("os-clr-on-clr-dev")
    blacklist.append("os-utils-gui")
    blacklist.append("os-testsuite-phoronix-server")
    blacklist.append("os-testsuite-phoronix-desktop")
    blacklist.append("os-testsuite-phoronix")
    blacklist.append("os-testsuite-automotive")
    blacklist.append("os-testsuite")
    blacklist.append("os-testsuite-0day")
    blacklist.append("os-installer")
    blacklist.append("service-os")
    blacklist.append("service-os-dev")
    blacklist.append("software-defined-cockpit")   # not general purpose
    blacklist.append("devpkg-R")
    blacklist.append("dnf")
    blacklist.append("telemetrics")
    blacklist.append("os-cloudguest-azure")
    blacklist.append("os-cloudguest-aws")
    blacklist.append("os-cloudguest-gce")
    blacklist.append("os-cloudguest-oracle")
    blacklist.append("os-cloudguest-aliyun")	# don't want it to find mkfs.ext4

    whitelist.append("python3-basic")
    whitelist.append("python-extras")
    whitelist.append("perl-basic")
    whitelist.append("perl-extras")
    whitelist.append("c-basic")
    whitelist.append("R-basic")
    whitelist.append("jupyter")
    whitelist.append("find")
    whitelist.append("sysadmin-basic")

    # manual overrides

    declare_binary("python3-basic", "python", 0)
    declare_binary("python3-basic", "python3", 0)
    declare_binary("python3-basic", "python3.7", 0)
    declare_binary("python2-basic", "python2.7", 0)
    declare_binary("c-basic", "pkg-config", 0)
    declare_binary("R-basic", "R", 0)
    declare_binary("R-basic", "R-script", 0)

    # print("Inspecting version ", VERSION)

    read_MoM(VERSION)

    manifests = dict()
    for bundle in sorted(bundles):
        m = download_manifest(bundle, bundles[bundle])
        manifests[bundle] = m
    for bundle in sorted(bundles):
        if bundle not in blacklist:
            read_manifest(manifests[bundle], bundle, bundles[bundle])
    for bundle in sorted(bundles):
        if bundle in blacklist:
            read_manifest(manifests[bundle], bundle, bundles[bundle])

    for binary in sorted(bin_bundle):
        print(binary + "\t" + bin_bundle[binary])


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as workingdir:
        main()
