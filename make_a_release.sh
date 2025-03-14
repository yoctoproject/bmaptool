#!/bin/sh -euf
#
# Copyright (c) 2012-2013 Intel, Inc.
# License: GPLv2
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# This script automates the process of releasing the bmaptool project. The
# idea is that it should be enough to run this script with few parameters and
# the release is ready.

#
# This script is supposed to be executed in the root of the bmaptool
# project's source code tree.

PROG="make_a_release.sh"

fatal() {
        printf "Error: %s\n" "$1" >&2
        exit 1
}

usage() {
        cat <<EOF
Usage: ${0##*/} <new_ver> <outdir>

<new_ver>  - new bmaptool version to make in X.Y.Z format
EOF
        exit 0
}

ask_question() {
	local question=$1

	while true; do
		printf "%s\n" "$question (yes/no)?"
		IFS= read answer
		if [ "$answer" = "yes" ]; then
			printf "%s\n" "Very good!"
			return
		elif [ "$answer" = "no" ]; then
			printf "%s\n" "Please, do that!"
			exit 1
		else
			printf "%s\n" "Please, answer \"yes\" or \"no\""
		fi
	done
}

format_changelog() {
	local logfile="$1"; shift
	local pfx1="$1"; shift
	local pfx2="$1"; shift
	local pfx_len="$(printf "%s" "$pfx1" | wc -c)"
	local width="$((80-$pfx_len))"

	while IFS= read -r line; do
		printf "%s\n" "$line" | fold -s -w "$width" | \
			sed -e "1 s/^/$pfx1/" | sed -e "1! s/^/$pfx2/" | \
			sed -e "s/[\t ]\+$//"
	done < "$logfile"
}

[ $# -eq 0 ] && usage
[ $# -eq 1 ] || fatal "insufficient or too many arguments"

new_ver="$1"; shift

# Validate the new version
printf "%s" "$new_ver" | egrep -q -x '[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+' ||
        fatal "please, provide new version in X.Y.Z format"

# Make sure the git index is up-to-date
[ -z "$(git status --porcelain)" ] || fatal "git index is not up-to-date"

# Remind the maintainer about various important things
ask_question "Did you update the man page"
ask_question "Did you update tests: test-data and oldcodebase"

# Change the version in the 'bmaptool/CLI.py' file
sed -i -e "s/^VERSION = \"[0-9]\+\.[0-9]\+\.[0-9]\+\"$/VERSION = \"$new_ver\"/" src/bmaptool/CLI.py
# Sed the version in the RPM spec file
sed -i -e "s/^Version: [0-9]\+\.[0-9]\+\.[0-9]\+$/Version: $new_ver/" packaging/bmaptool.spec
# Remove the "rc_num" macro from the RPM spec file to make sure we do not have
# the "-rcX" part in the release version
sed -i -e '/^%define[[:blank:]]\+rc_num[[:blank:]]\+[[:digit:]]\+[[:blank:]]*$/d' packaging/bmaptool.spec
# update man page title line (.TH)
export MANVERSTR="\"bmaptool $new_ver\""
export MANDATE="\"$(date +"%B %Y")\""
sed -i -e "s/\.TH.*$/\.TH BMAPTOOL \"1\" $MANDATE $MANVERSTR \"User Commands\"/g" docs/man1/bmaptool.1

# Ask the maintainer for changelog lines
logfile="$(mktemp -t "$PROG.XXXX")"
cat > "$logfile" <<EOF
# Please, provide changelog lines for the RPM and Deb packages.
# Please, use one line per changelog entry, lines will be wrapped
# automatically.
# Lines starting with the "#" symbol will be removed.
EOF

if [ -z "${EDITOR+x}" ]; then
	EDITOR="vim"
fi
"$EDITOR" "$logfile"

# Remove comments and blank lines
sed -i -e '/^#.*$/d' -e'/^$/d' "$logfile"

# Prepare Debian changelog
deblogfile="$(mktemp -t "$PROG.XXXX")"
printf "%s\n\n" "bmaptool ($new_ver) unstable; urgency=low" > "$deblogfile"
format_changelog "$logfile" "  * " "    " >> "$deblogfile"
printf "\n%s\n\n" " -- Trevor Woerner <twoerner@gmail.com> $(date -R)" >> "$deblogfile"
cat debian/changelog >> "$deblogfile"
mv "$deblogfile" debian/changelog

# Prepare RPM changelog
rpmlogfile="$(mktemp -t "$PROG.XXXX")"
printf "%s\n" "$(date --utc) - Trevor Woerner <twoerner@gmail.com> ${new_ver}-1" > "$rpmlogfile"
format_changelog "$logfile" "- " "  " >> "$rpmlogfile"
printf "\n"  >> "$rpmlogfile"
cat packaging/bmaptool.changes >> "$rpmlogfile"
mv "$rpmlogfile" packaging/bmaptool.changes

rm "$logfile"

# Commit the changes
git commit -a -s -m "Release version $new_ver"

outdir="."
tag_name="v$new_ver"
release_name="bmaptool-$new_ver"

# Get the name of the release branch corresponding to this version
release_branch="release-$(printf "%s" "$new_ver" | sed -e 's/\(.*\)\..*/\1.0/')"

cat <<EOF
To finish the release:
  1. Push this change as a PR for review
  2. Make a release named '$new_ver' in GitHub after the PR merges
EOF
