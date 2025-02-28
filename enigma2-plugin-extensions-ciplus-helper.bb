SUMMARY = "Lululla"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "proprietary"

require conf/license/license-gplv2.inc

inherit gitpkgv

SRCREV = "${AUTOREV}"
PV = "1.0+git${SRCPV}"
PKGV = "1.0+git${GITPKGV}"
VER = "1.0"
PR = "r0"
S = "${WORKDIR}/git"
SRC_URI = "git://github.com/Belfagor2005/ciplushelper-8.4.git;protocol=https;branch=master"


BINARIES_DIR = "${S}/ciplushelper_bin"
FILES_${PN} = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/*"
# RDEPENDS_${PN} += "glibc"

# RDEPENDS_${PN} = "libc glibc"
# FILES_${PN} = "/usr/* "
IMAGE_INSTALL_append = "libsdl2-2.0-dev glibc"

do_install() {

    cp -rp ${S}/usr* ${D}/
    
    if [ "${TARGET_ARCH}" = "armv7a" ]; then
        if [ -f ${BINARIES_DIR}/arm/ciplushelper ]; then
            install -m 0755 ${BINARIES_DIR}/arm/ciplushelper ${D}${bindir}
        else
            echo "ARM binary not found"
        fi
    elif [ "${TARGET_ARCH}" = "mipsel32" ]; then
        if [ -f ${BINARIES_DIR}/mipsel32/ciplushelper ]; then
            install -m 0755 ${BINARIES_DIR}/mipsel32/ciplushelper ${D}${bindir}
        else
            echo "MIPS binary not found"
        fi
    else
        echo "Architecture ${TARGET_ARCH} not explicitly handled."
    fi
}
