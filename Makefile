
# GIT 
GIT_VERSION="$(shell git describe --abbrev=4 --dirty --always --tags)"
#
CFLAGS+= -DFIRMWARE_VERSION=\"$(GIT_VERSION)\"
#
#


DIRS=sflash

all: 
	@for d in ${DIRS}; do \
	   ${MAKE} -C $$d ;\
	done

clean:
	@for d in ${DIRS}; do \
	   ${MAKE} -C $$d clean ;\
	done

