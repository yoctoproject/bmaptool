Name:           bmaptool
Version:        3.9.0
Release:        11.el7
Summary:        Tools for creating and using block maps (bmap)
License:        GPLv2
URL:            https://github.com/yoctoproject/bmaptool
BuildArch:      noarch
Source0:        %{name}-%{version}.tar.gz

# The package is not installed under a versioned site-packages directory, so
# rpm's byte-compilation helper would otherwise default to Python 2.  Point it
# at Python 3; Python 3.9+ will ignore the 3.6 .pyc files and use the sources.
%global __python /usr/bin/python3

# Do not let rpmbuild generate a "python(abi) = 3.6" dependency (which would
# pin the package to the build host's Python).  Require a lower bound instead,
# so Python 3.6, 3.9 and newer all satisfy it.
AutoReqProv:    no
Requires:       python(abi) >= 3.6

%description
bmaptool is a generic tool for creating block maps (bmap) for a file and
copying files using the block map.  It can skip the mapped-only (sparse)
parts of an image, which makes flashing large raw images to block devices
faster and safer than dd.

It also provides 'bmap-send' to send an image and its bmap file to a remote
host over scp/ssh, and 'bmaptool verify' to verify an image or block device
against a bmap file.

%prep
%setup -q

%build
# Pure Python package, nothing to build.

%install
rm -rf %{buildroot}
install -d %{buildroot}/usr/lib/bmaptool
cp -a src/bmaptool %{buildroot}/usr/lib/bmaptool/
find %{buildroot}/usr/lib/bmaptool/bmaptool \
    -name '__pycache__' -type d -prune -exec rm -rf {} +
find %{buildroot}/usr/lib/bmaptool/bmaptool \
    -name '*.pyc' -delete

install -D -m 0755 packaging/el7/bmaptool %{buildroot}%{_bindir}/bmaptool
install -D -m 0755 packaging/el7/bmap-send %{buildroot}%{_bindir}/bmap-send
install -D -m 0644 docs/man1/bmaptool.1 \
    %{buildroot}%{_mandir}/man1/bmaptool.1
install -D -m 0644 docs/man1/bmap-send.1 \
    %{buildroot}%{_mandir}/man1/bmap-send.1

%pre
if ! command -v python3 >/dev/null 2>&1; then
    echo "warning: bmaptool requires Python 3.6 or newer, but 'python3' was not found" >&2
fi

%files
%license LICENSE
%doc README.md CHANGELOG.md
/usr/lib/bmaptool/bmaptool
%{_bindir}/bmaptool
%{_bindir}/bmap-send
%{_mandir}/man1/bmaptool.1*
%{_mandir}/man1/bmap-send.1*

%changelog
* Wed Nov 11 2026 bmaptool packager <nobody@example.com> - 3.9.0-11
- bmap-send: send only the mapped ranges by default; add --full,
  --zero-holes and --remote-python
- Update the bmap-send man page and README

* Mon Nov 09 2026 bmaptool packager <nobody@example.com> - 3.9.0-9
- Move the RPM packaging files under packaging/el7/ (no functional change)
- Keep the built RPMs and their changelog under packaging/el7/rpms/

* Mon Nov 09 2026 bmaptool packager <nobody@example.com> - 3.9.0-8
- Sync with upstream: use the upstream BmapVerify/BmapSend implementation,
  range splitting, mtime checks and repair scripts
- Require "python(abi) >= 3.6" again (explicit lower bound, AutoReqProv off)
- Keep the Python 3.6/3.9 compatible launcher and /usr/lib/bmaptool layout

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-7
- Use "#!/usr/bin/env python3" in the launchers, so a Python 3 which is not
  installed as /usr/bin/python3 (for example a source build) is found via PATH

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-6
- Drop the hard Python dependency: RPM only sees python(abi) when Python was
  installed from RPM, so the package could not be installed on hosts whose
  Python was built from source even when its version was suitable
- Add a non-fatal %pre check for the "python3" interpreter

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-5
- Require "python(abi) >= 3.6" instead of the "python3" package name, so any
  Python 3.6+ interpreter provided by RPM (including 3.9) satisfies it
  without pinning the exact ABI version

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-4
- Install the Python package into /usr/lib/bmaptool and add that directory to
  sys.path in the launcher, so the RPM works with Python 3.6 and newer
  (for example 3.9) instead of only the build host's Python 3.6
- Do not generate a python(abi) dependency, which pinned the package to the
  Python version used on the build host

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-3
- Add "bmaptool verify BMAP" to verify an image or a block device against a
  bmap file; the image path is inferred by removing the ".bmap" suffix
- Verification reads only the mapped ranges and is multi-threaded
  (-j/--jobs, default 4), with sha256/sha512/blake2b support

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-2
- Add the bmap-send wrapper: send only the mapped blocks over SSH
- bmap-send accepts the sha512/blake2b checksums produced by --checksum-type
- bmap-send uses shlex.quote on Python 3 while staying Python 2.7 compatible

* Fri Nov 06 2026 bmaptool packager <nobody@example.com> - 3.9.0-1
- Package bmaptool 3.9.0 for offline CentOS 7.6 with the system Python 3.6
- Add parallel checksum calculation (-j/--jobs) for bmap creation
- Add --checksum-type auto|sha256|sha512|blake2b (auto prefers sha256 when
  the CPU advertises SHA acceleration, sha512 otherwise)
