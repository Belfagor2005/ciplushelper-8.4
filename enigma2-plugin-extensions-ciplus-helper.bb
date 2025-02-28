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

SRC_URI = "git://github.com/Belfagor2005/ciplushelper-8.4.git;protocol=https;branch=master"

RDEPENDS_${PN} = "libc libdl glibc"
PACKAGE_ARCH = "${MACHINE_ARCH}"
S = "${WORKDIR}/git"

BINARIES_DIR = "${S}/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper_bin"
FILES_${PN} = "/usr/*"

do_install() {
    cp -rp ${S}/usr* ${D}/
    
    if d.getVar('TARGET_ARCH') == 'armv7a':
        install -m 0755 ${BINARIES_DIR}/arm/ciplushelper ${D}${bindir}
    elif d.getVar('TARGET_ARCH') == 'mipsel32':
        install -m 0755 ${BINARIES_DIR}/mipsel32/ciplushelper ${D}${bindir}
    else
        bb.warn("Architecture %s not explicitly handled." % d.getVar('TARGET_ARCH'))
    fi
}

