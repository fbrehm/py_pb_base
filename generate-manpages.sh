#!/bin/bash

BASE_DIR="$(dirname "$0")"
cd "${BASE_DIR}"

MAN_DIR="man"
if [[ ! -d "${MAN_DIR}" ]] ; then
    echo "MAN_DIR '${MAN_DIR}' does not exists." >&2
    exit 5
fi

AUTHORS_INI="manpage-includes/authors.ini"
if [[ ! -f "${AUTHORS_INI}" ]] ; then
    echo "File '${AUTHORS_INI}' does not exists." >&2
    exit 6
fi

echo
echo "Generating man pages in '${MAN_DIR}' ..."
echo

for token in "crc64" ; do

    script="bin/${token}"
    manpage="man/${token}.1"
    title=$( echo "${token}" | tr '[:lower:]' '[:upper:]' )
    name_ini="manpage-includes/name-${token}.ini"

    if [[ ! -x "${script}" ]] ; then
        echo "Script '${script}' does not exists." >&2
        exit 7
    fi

    if [[ ! -f "${name_ini}" ]] ; then
        echo "File '${name_ini}' does not exists." >&2
        exit 8
    fi

    echo "  * ${manpage}"

    help2man --no-discard-stderr --no-info \
            --include="${AUTHORS_INI}" \
            --include="${name_ini}" \
            --manual="${title}" \
            --section=1 \
            "${script}" > "${manpage}"

done

echo

exit 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
