# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed

## [3.9.0]

- copy: add `--removable-device`, `--keyring` and `--fingerprint` options
- Respect query part of the url when operating on the path
- support FTP authentication
- rework GPG tests

## [3.8.0]

- Move project to yoctoproject
- Maintainers change from Artem Bityutskiy (Thank you!) to Trevor Woerner, Joshua Watt, Tim Orling
- Consolidate name as 'bmaptool'

## [3.7.0]
### Added
- Use GitHub Actions for CI (#109)
- Add `poetry` for dependency management and `black` for code formatting (#104)
- Add functionality for copying from standard input (#99)
### Changed
- Switch from gpg to gpgme module (#103)

## [3.6.0]

1. Improve ZFS compatibility.
2. Added the 'zstd' compression type support.
3. Add '--psplash-pipe' option for interacting with psplash.

## [3.5.0]

1. Fixed copying of compressed files from URLs, it was a regression introduced
   in bmap-tools 3.4.
2. Python 3.x support fixes and improvements.
3. RPM packaging fixes.
4. Improved help and error messages.

## [3.4.0]

1. bmap-tools has now new home: https://github.com/01org/bmap-tools

2. Python 3.x support: bmap-tools now compatible with Python 3.3+

3. bmaptool now can be shipped as standalone application.
   See PEP441 (zipapp) for implementation details.

4. ZIP archives now supported. Similar to tar.* archives, image must be
   first file in archive.

5. LZ4 compression now supported. Files with the following extensions are
   recognized as LZ4-compressed: ".lz4", ".tar.lz4" and ".tlz4".

6. Fixed copying images on XFS file system where predictive caching lead
   to more blocks to be mapped than needed.

7. Fixed detection of block size on file systems that do not report it
   correctly via ioctl FIGETBSZ.

## [3.2.0]

1. Multi-stream bzip2 archives are now supported. These are usually created
   with the 'pbzip2' compressor.

2. LZO archives are now supported too. Files with the following extensions are
   recognized as LZO-compressed: ".lzo", ".tar.lzo", ".tzo".

3. Make 'bmaptool create' (and hence, the BmapCreate module) work with the
   "tmpfs" file-system. Tmpfs does not, unfortunately, support the "FIEMAP"
   ioctl, but it supports the "SEEK_HOLE" option of the "lseek" system call,
   which is now used for finding where the holes are. However, this works only
   with Linux kernels of version 3.8 or higher.

   Generally, "FIEMAP" is faster than "SEEK_HOLE" for large files, so we always
   try to start with using FIEMAP, and if it is not supported, we fall-back to
   using "SEEK_HOLE". Therefore, the "Fiemap" module was re-named to "Filemap",
   since it is now supports more than just the FIEMAP ioctl.

   Unfortunately, our "SEEK_HOLE" method requires the directory where the image
   resides to be accessible for writing, because in current implementation we
   need to create a temporary file there for a short time. The temporary file
   is used to detect whether tmpfs really supports SEEK_HOLE, or the system
   just fakes it by always returning EOF (this is what happens in pre-3.8
   kernels).

4. Decompression should now require less memory, which should fix
   out-of-memory problems reported by some users recently. Namely, users
   reported that decompressing large bz2-compressed sparse files caused
   out-of-memory situation on machines with 2GB RAM. This should be fixed now.

5. Reading and decompressing is now faster because we now use more parallelism:
   reading the data form the source URL is done in separate thread,
   decompressing happens in a separate process too. My measurement with Tizen
   IVI images from 'tizen.org' showed 10% read speed improvement, but this
   depends a lot on where the bottle-neck is: the USB stick, the network, or
   the CPU load.
   
## [3.1.0]

This bug-fix release is about fixing a small screw-up in version 3.0, where we
introduced incompatible bmap format changes, but did not properly increase the
bmap format version number. Instead of making it to be version 2.0, we made it
to be version 1.4. The result is that bmap-tools v2.x crash with those
1.4-formatted bmap files.

This release changes the bmap format version from 1.4 to 2.0 in order to
lessen the versioning screw-up. Increased major bmap format version number will
make sure that older bmap-tools fail with a readable error message, instead of
crashing.

Thus, the situation as follows:
  * bmap-tools v2.x: handle bmap format versions 1.0-1.3, crash with 1.4, and
                     nicely exit with 2.0
  * bmap-tools v3.0: handles all 1.x bmap format versions, exits nicely with 2.0
  * bmap-tools v3.1: handles all bmap format versions
  
## [3.0.0]

1. Switch from using SHA1 checksums in the bmap file to SHA256. This required
   bmap format change. The new format version is 1.4. BmapCopy (and thus,
   bmaptool supports all the older versions too). Now it is possible to use any
   hash functions for checksumming, not only SHA256, but SHA256 is the default
   for BmapCreate.

2. Support OpenPGP (AKA gpg) signatures for the bmap file. From now on the bmap
   file can be signed with gpg, in which case bmaptool verifies the bmap file
   signature. If the signature is bad, bmaptool exits with an error message.
   The verification can be disabled with the --no-sig-verify option.

   Both detached and "in-band" clearsign signatures are supported. Bmaptool
   automatically discovers detached signatures by checking ".sig" and ".asc"
   files.

3. The Fiemap module (and thus, bmaptool) now always synchronizes the image
   before scanning it for mapped areas. This is done by using the
   "FIEMAP_FLAG_SYNC" flag of the FIEMAP ioctl.

   The reason for synchronizing the file is bugs in early implementations of
   FIEMAP in the kernel and file-systems, and synchronizing the image is a
   known way to work around the bugs.
   
## [2.6.0]

### Added

- On-the-fly decompression support for '.xz' and '.tar.xz' files.

## [2.5.0]

1. bmaptool (or more precisely, the BmapCopy class) has an optimization where
   we switch to the "noop" I/O scheduler when writing directly to block
   devices. We also lessen the allowed amount of dirty data for this block
   device in order to create less memory pressure on the system. These tweaks
   are done by touching the corresponding sysfs files of the block device. The
   old bmaptool behavior was that it failed when it could not modify these
   files. However, there are systems where users can write to some block
   devices (USB sticks, for example), but they do not have permissions to
   change the sysfs files, and bmaptool did not work for normal users on such
   systems. In version 2.5 we change the behavior and do not fail anymore if we
   do not have enough permissions for changing sysfs files, simply because this
   is an optimization, although a quite important one. However, we do print a
   warning message.
2. Many improvements and fixes in the Debian packaging, which should make it
   simpler for distributions to package bmap-tools.
   
## 2.4.0

1. Add SSH URLs support. These URLs start with "ssh://" and have the following
   format: ssh://user:password@host:path, where
   * user - user name (optional)
   * password - the password (optional)
   * host - hostname
   * path - path to the image file on the remote host

   If the password was given in the URL, bmaptool will use password-based SSH
   authentication, otherwise key-based SSH authentication will be used.
   
## 2.3.0

1. Add bmap file SHA1 checksum into the bmap file itself in order to improve
   robustness of bmaptool. Now we verify bmap file integrity before using it,
   and if it is corrupted or incomplete, we should be able to detect this.

   The reason for this change was a bug report from a user who somehow ended
   up with a corrupted bmap file and experienced weird issues.

   This also means that manual changes the bmap file will end up with a SHA1
   mismatch failure. In order to prevent the failure, one has to update the bmap
   file's SHA1 by putting all ASCII "0" symbols (should be 40 zeroes) to the
   "BmapFileSHA1" tag, then generating SHA1 of the resulting file, and then
   put the calculated real SHA1 back to the "BmapFileSHA1" tag.

   In the future, if needed, we can create a "bmaptool checksum" command which
   could update SHA1s in the bmap file.

2. Re-structure the bmap file layout and put information about mapped blocks
   count at the beginning of the bmap XML file, not after the block map table.
   This will make it possible to optimize bmap file parsing in the future. This
   also makes the bmap file a little bit more human-readable.

2. Make the test-suite work on btrfs.

## 2.2.0

1. Made bmaptool understand URLs which include user name and password
   (the format is: https://user:password@server.com)
   
## 2.1.0

1. Fixed the out of memory problems when copying .bz2 files.
2. Added CentOS 6 support in packaging.

## 2.0.0

There are several user-visible changes in 'bmaptool copy':

1. In order to copy an image without bmap, the user now has to explicitly
   specify the "--nobmap" option. In v1.0 this was not necessary. The reason
   for this change is that users forget to use --bmap and do not realize that
   they are copying entire the image. IOW, this is a usability improvement.

2. The bmap file auto-discovery feature has been added. Now when the user does
   not specify the bmap file using the --bmap option, 'bmaptool copy' will try
   to find it at the same place where the image resides. It will look for files
   with a similar base name and ".bmap" extension. This should make it easier
   to use bmaptool.

3. 'bmaptool copy' now can open remote files, so it is not necessary to
   download the images anymore, and you can specify the URL to bmaptool. For
   example:

   bmaptool copy download.tizen.org/snapshots/ivi/.../ivi-2.0.raw.bz2

   The tool will automatically discover the bmap file, read from the image from
   the 'download.tizen.org' server, decompress it on-the-fly, and copy to the
   target file/device. The proxy is supported via the standard environment
   variables like 'http_proxy', 'https_proxy', 'no_proxy', etc.

4. Now 'bmaptool' prints the progress while copying. This improves usability
   as well: copying may take minutes, and it is nice to let the user know how
   much has already been copied.

5. Warnings and errors are high-lighted using yellow and red labels now.

6. Added bmaptool man page.

'bmaptool create' has no changes comparing to release v1.0.

## 1.0.0

The first bmap-tools release. All the planned features are implemented,
automated tests are implemented. We provide nice API modules for bmap creation
('BmapCreate.py') and copying with bmap ('BmapCopy.py'). The 'Fiemap.py' API
module provides python API to the FIEMAP Linux ioctl.

The 'bmaptool' command-line tool is a basically a small wrapper over the
API modules. It implements the 'create' and 'copy' sub-commands, which
allow creating bmap for a given file and copying a file to another file
or to a block device using bmap.

The 'bmaptools copy' command (and thus, 'BmapCopy.py' module) support
accept compressed files and transparently de-compress them. The following
compression types are supported: .bz2, .gz, .tar.bz2, .tar.gz.

The original user of this project is Tizen IVI where the OS images are
sparse 2.6GiB files which are distributed as .bz2 file. Since the images
are only 40% full, the .bz2 file weights about 300MiB. Tizen IVI uses the
'BmapCreate.py' API module to generate the bmap file for the 2.6GiB images
(before the image was compressed, because once it is compressed with bzip2,
the information about holes gets lost). Then the bmap file is distributed
together with the .bz2 image. And Tizen IVI users are able to flash the
images to USB stick using the following command:

 $ bmaptool copy --bmap image.bmap image.bz2 /dev/usb_stick

This command decompresses the image (image.bz2) on-the-fly, and copies all
the mapped blocks (listed in 'image.bmap') to the USB stick (the
'/dev/usb_stick' block device).

This is a lot faster than the old method:

 $ bzcat image.bz2 | dd of=/dev/usb_stick

Additionally, 'bmaptool copy' verifies the image - the bmap stores SHA1
checksums for all mapped regions.

However, bmap-tools may be useful for other projects as well - it is generic
and just implements the idea of fast block-based flashing (as opposed to
file-based flashing). Block-based flashing has a lot of benefits.

The 'BmapCopy.py' module implements a couple of important optimization when
copying to block device:
  1. Switch the block device I/O scheduler to 'Noop', which is a lot faster
     than 'CFQ' for sequential writes.
  2. Limits the amount of memory which the kernel uses for buffering, in
     order to have less impact on the overall system performance.
  3. Reads in a separate thread, which is a lot faster when copying compressed
     images, because we read/uncompress/verify SHA1 in parallel to writing
     to a potentially slow block device.

We support bmap format versioning. The current format is 1.2. The minor version
number must not break backward compatibility, while the major numbers indicates
some incompatibility.

[Unreleased]: https://github.com/intel/bmap-tools/compare/v3.6..HEAD
[3.6.0]: https://github.com/intel/bmap-tools/releases/tag/v3.6
[3.5.0]: https://github.com/intel/bmap-tools/releases/tag/v3.5
[3.4.0]: https://github.com/intel/bmap-tools/releases/tag/v3.4
[3.2.0]: https://github.com/intel/bmap-tools/releases/tag/v3.2
[3.1.0]: https://github.com/intel/bmap-tools/releases/tag/v3.1
[3.0.0]: https://github.com/intel/bmap-tools/releases/tag/v3.0
[2.6.0]: https://github.com/intel/bmap-tools/releases/tag/v2.6
[2.5.0]: https://github.com/intel/bmap-tools/releases/tag/v2.5
