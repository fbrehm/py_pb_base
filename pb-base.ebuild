# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=5
PYTHON_COMPAT=( python{2_6,2_7,3_2,3_3,3_4} pypy2_0 )

DESCRIPTION="Python modules for common used objects, error classes and functions."
HOMEPAGE="http://git.pb.local/gitweb/?p=python/pb-base;a=summary"
SRC_URI=""
EGIT_REPO_URI="http://git.pb.local/python/pb-base.git"

PB_CATEGORY="dev-python"

inherit git-2 distutils-r1 user versionator

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86"
IUSE="doc nls"

EGIT_BRANCH="master"
EGIT_COMMIT=$(replace_version_separator 3 '-')

DOCS="debian/changelog README.txt"

RDEPEND="
	virtual/python-argparse
	dev-python/configobj
	>=dev-python/pb-logging-0.2.7
	nls? ( virtual/libintl )
"
DEPEND="
	${RDEPEND}
	doc? (	dev-python/epydoc 
			dev-python/docutils
	)
	nls? ( sys-devel/gettext )
"

pkg_setup() {

	elog "Used GIT tag: '${EGIT_COMMIT}'."

	einfo "Start setup package ..."
	distutils-r1_src_prepare
}

src_compile() {
	einfo "Start compiling package ..."
	distutils-r1_src_compile
	if use nls; then
		make -C ${S}/po
	fi
}

src_install() {
	distutils-r1_src_install

	if use doc; then
		einfo "Installing documentation ..."
		dodir "/usr/share/doc/${PF}"
		dodir "/usr/share/doc/${PF}/html"
		dodir "/usr/share/doc/${PF}/pdf"

		einfo "Creating epydoc html documentation"
		epydoc --html -v -o "${ED}/usr/share/doc/${PF}/html" "${S}/pb_base" || ewarn "Could not create epydoc html documentation"
		einfo "Creating epydoc pdf documentation"
		epydoc --pdf -o "${ED}/usr/share/doc/${PF}/pdf" "${S}/pb_base" || ewarn "Could not create epydoc pdf documentation"

	fi

	if use nls; then
		make -C ${S}/po DESTDIR="${ED}" install
	fi

}

# vim: filetype=ebuild ts=4 sw=4
