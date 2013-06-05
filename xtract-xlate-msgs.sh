#!/bin/bash

pot_file="py_pb_base1.pot"
output_dir="po"
pkg_version="0.4.10"
src_dir="pb_base"

cd $(dirname $0)

xgettext --output="${pot_file}" \
        --output-dir="${output_dir}" \
        --language="Python" \
        --join-existing \
        --add-comments \
        --keyword=_ \
        --keyword=__ \
        --force-po \
        --indent \
        --add-location \
        --width=85 \
        --sort-by-file \
        --package-name="profitbricks-python-base" \
        --package-version="${pkg_version}" \
        --msgid-bugs-address=frank.brehm@profitbricks.com \
        $(find "${src_dir}" -type f -name '*.py' | sort)



# vim: ts=4 et
