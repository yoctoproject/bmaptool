#!/bin/bash
# Build a single noarch RPM for an offline CentOS 7.6 host which provides the
# system Python 3.6 (python3-3.6.8).
#
# Usage (on a CentOS 7 machine with rpm-build installed):
#
#     packaging/el7/build-rpm.sh [rpmbuild-topdir]
#
# The resulting RPM is printed at the end, normally:
#     $HOME/rpmbuild/RPMS/noarch/bmaptool-3.9.0-1.el7.noarch.rpm

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TOP=${1:-$HOME/rpmbuild}
SPEC="$ROOT/packaging/el7/bmaptool.spec"
VERSION=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$ROOT/src/bmaptool/__init__.py")
SPEC_VERSION=$(awk '/^Version:/{print $2}' "$SPEC")

if [ -z "$VERSION" ]; then
    echo "error: cannot determine version from src/bmaptool/__init__.py" >&2
    exit 1
fi

if [ "$VERSION" != "$SPEC_VERSION" ]; then
    echo "error: spec version ($SPEC_VERSION) != source version ($VERSION)" >&2
    exit 1
fi

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "error: rpmbuild not found (install the rpm-build package)" >&2
    exit 1
fi

mkdir -p "$TOP"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
rm -f "$TOP/SOURCES/bmaptool-$VERSION.tar.gz"

tar -C "$ROOT" -czf "$TOP/SOURCES/bmaptool-$VERSION.tar.gz" \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='*.pyo' \
    --transform "s,^,bmaptool-$VERSION/," \
    LICENSE README.md CHANGELOG.md docs packaging src

rpmbuild --define "_topdir $TOP" -bb "$SPEC"

echo
echo "built:"
find "$TOP/RPMS" -name '*.rpm' -print
