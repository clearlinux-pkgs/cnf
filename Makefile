PKG_NAME := cnf
ARCHIVES = 

include ../common/Makefile.common

update:
	python commandnotfound-list.py > commandlist.csv~
	LC_ALL=C sort commandlist.csv~ > commandlist.csv
	! git diff --exit-code commandlist.csv
	rm -f commandlist.csv~
	$(MAKE) bumpnogit
	latest=`curl -sSf "https://download.clearlinux.org/update/version/formatstaging/latest"`; \
	if [ -z "$$latest" ]; then exit 1; fi; \
	git commit -m "update command list for $$latest" -a
	test -n "$(NO_KOJI)" || $(MAKE) koji-nowait
