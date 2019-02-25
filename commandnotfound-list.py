#!/usr/bin/python3
#
# Takes a build number as argument, and prints a size summary of all the delta packs
# for that build on a per file basis
#
# pylint: disable=invalid-name

import sys
import tempfile
import subprocess
import requests
import os

VERSION = 0

bundles = dict()


binaries = dict()
bin_bundle = dict()
bin_size = dict()

URLPREFIX = 'https://cdn.download.clearlinux.org/update/'

blacklist = list()
whitelist = list()


def read_MoM(version):
    global bundles
    m = requests.get(URLPREFIX + str(version) + '/Manifest.MoM')
    response = m.text.split('\n')
    for line in response:
        words = line.split('\t')
        if len(words) > 2:
            bundle = words[3]
            version = words[2]
            bundles[bundle] = version



def declare_binary(bundle : str, binary : str, size : int):
    global bin_bundle, bin_size, blacklist, whitelist
    
    if bundle in blacklist:
        size = size * 100 + 5000000
    if "-dev" in bundle or "devpkg-" in bundle:
        size = size * 80 + 2000000
        
    if bundle in whitelist:
        size = size / 10
        
    # This weeks special: 10% discount on basic bundles 
    if "-basic" in bundle:
        size = size * 0.90
    
    if not binary in bin_bundle or binary == bundle:
        bin_bundle[binary] = bundle
        bin_size[binary] = size
    else:
        if (bin_size[binary] > size or bundle in whitelist) and bin_bundle[binary] != binary and bundle not in blacklist:
            bin_bundle[binary] = bundle
            bin_size[binary] = size
            


def read_manifest(pack, version):
    bundlesize = 0    
#    print("Looking at ", pack, version)

    if ".I." in pack:
        return

    m = requests.get(URLPREFIX + str(version) + '/Manifest.' + pack)

    for line in m.text.split('\n'):
        words = line.split('\t')
        if words[0] == "contentsize:":
#            print("Content size for bundle", pack,"is ", words[1])
            bundlesize = int(words[1])
        if len(words) > 2:
            flags = words[0]
            hash = words[1]
            version = words[2]
            file = words[3]
            
            if 'd' in flags:
                continue
                
            if '/usr/bin/' in file and '/usr/share/' not in file:
                basename = os.path.basename(file)
                declare_binary(pack, basename, bundlesize)
            
#            if '/usr/bin/python2' in file and pack not in python2:
#                python2.append(pack)
                
            

def grab_latest_release():
    response = requests.get("https://download.clearlinux.org/update/version/formatstaging/latest")
        
    html = response.text.strip()
    return html


def main():
    global VERSION
    global bundles
    global bin_bundle
    global blacklist
    global whitelist
    VERSION = grab_latest_release()
    count = 0
    
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
    
    whitelist.append("python3-basic")
    whitelist.append("python-extras")
    whitelist.append("perl-basic")
    whitelist.append("perl-extras")
    whitelist.append("c-basic")
    whitelist.append("R-basic")
    whitelist.append("jupyter")
    whitelist.append("sysadmin-basic")
    
    # manual overrides
    
    declare_binary("python3-basic", "python", 0)
    declare_binary("python3-basic", "python3", 0)
    declare_binary("python3-basic", "python3.7", 0)
    declare_binary("python2-basic", "python2.7", 0)
    declare_binary("c-basic", "pkg-config", 0)
    declare_binary("R-basic", "R", 0)
    declare_binary("R-basic", "R-script", 0)

#    print("Inspecting version ", VERSION)

    read_MoM(VERSION)

    for bundle in bundles:
        if bundle not in blacklist:
            read_manifest(bundle, bundles[bundle])
    for bundle in bundles:
        if bundle in blacklist:
            read_manifest(bundle, bundles[bundle])


    for binary in bin_bundle:
        if bin_bundle[binary] != 'os-core':
            print(binary + "\t" + bin_bundle[binary])
    

if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as workingdir:
        main()
 