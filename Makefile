PKG_NAME := cnf
ARCHIVES = 

include ../common/Makefile.common

update:
	python commandnotfound-list.py | LC_ALL=C sort > commandlist.csv
	! git diff --exit-code  commandlist.csv
	$(MAKE) bumpnogit
	git commit -m "update command list for "`curl "https://download.clearlinux.org/update/version/formatstaging/latest"` -a
	test -n "$(NO_KOJI)" || $(MAKE) koji-nowait
