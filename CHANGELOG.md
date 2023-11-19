# Changelog


## (unreleased)

### New

* Update to debian packaging files from packages.debian.org. [Stephen L Arnold]

  * remove setuptools_scm toml feature and bump build-system requires
  * note setuptools versions greater than 59 are only available for
    py37 and higher while minimum required for setuptools_scm is 61
    while setuptools_scm 8 is also too high for py37
  * make sure debian control file depends on python3-setuptools-scm
    because it gets parsed by deb-helper scripts
  * workaround bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1003252
    in debian rules
  * fix even more typos and remove superflous MANIFEST.in file
  * make sure debian pkg workflow gets a compliant tag version

* Update GH workflows to build some artifacts and make a release. [Stephen L Arnold]

  * bump debian package deps to python3 only, add new deps

* Switch to setuptools/pep517 packaging, cleanup tests and imports. [Stephen L Arnold]

  * prefer setuptools over poetry, simple is better than overkill
  * prefer pytest as test runner instead of nose/unittest, mark slow tests
  * remove superfluous files, move tool configs to pyproject.toml
  * add tox file with development workflows (no pre-commit just yet)

### Changes

* Cleanup some debian build cruft. [Stephen L Arnold]

* Swap out pytest plugin for conftest.py instead, fix deb pkg files. [Stephen L Arnold]

### Fixes

* Fallback to Ubuntu 20.04 for now to get python 3.6. [Stephen L Arnold]

  * update workflows for now to use 20.04 instead of latest
  * remove windows for now and use brew on Macos
  * skip linux-only tests on mac or windows
  * cleanup more imports and env typos

* Replace insecure XML parser with defusedxml.parse. [Stephen L Arnold]

  * add bandit tox env and fix one class of security warning
  * needs a lot more sec cleanup, mainly subprocess and assert calls


## v3.7 (2023-11-18)

### Other

* Release version 3.7. [Artem Bityutskiy]

* Pyproject.toml: Move nose from dependencies to dev-dependencies. [Simon McVittie]

  This is only needed when running the build-time tests, and is not needed
  for ordinary use of the tool.

* Unnecessary shebangs. [Ali Erdinc Koroglu]

* Release version 3.7. [Artem Bityutskiy]

* Prepare for release version 3.7. [Artem Bityutskiy]

* Make_a_release.sh: remove a couple of out of date questions. [Artem Bityutskiy]

* Make_a_release.sh: adjust to master branch rename. [Artem Bityutskiy]

* CHANGELOG.md: remove junk whitespace. [Artem Bityutskiy]

* BmapCreate: a couple of spelling fixes. [Artem Bityutskiy]

* Merge pull request #115 from chrthi-work/feature/silence-warnings. [Niklas Kunz]

  Fix some unnecessary warnings, update i/o scheduler

* BmapCopy: Improve sysfs setting. [Christian Thießen]

  When running as non-root, do not emit warnings when sysfs files already
  have the correct values.
  If they don't, suggest a udev rule to enable working as non-root without
  warnings permanently.
  Apply a single context manager class to both sysfs attributes to reduce
  code duplication.

* Ssh: Disable forwardings. [Christian Thießen]

  When port forwardings are configured in the ssh config and a parallel
  ssh session with the same sever is already open, ssh will print error
  messages. Do the same as scp to prevent them and pass the
  ClearAllForwardings option to the ssh client.
  Do the same for X11 forwardings.

* Fix failures when .netrc is not present. [Joshua Watt]

  If the user doesn't have a .netrc file, bmaptool would fail. Fix this so
  that missing or incorrectly formatted .netrc files are not fatal

* Add .netrc support. [Joshua Watt]

  Adds support for getting the username and password from ~/.netrc if it's
  not specified in the URL.

* Add gpg as a dependency. [Joshua Watt]

  GPG is required to verify signatures

* Use Poetry to create command alias. [Joshua Watt]

  Uses poetry to create the CLI command. Poetry will add the command to
  PATH which means that using the symlink shim in the test suite is no
  longer necessary (and it didn't work anyway because the module name in
  pyproject.toml was wrong).

* Ci: Run test suite. [Joshua Watt]

  Runs the test suite as part of github actions

* Tests: Move signature files to subdirectory. [Joshua Watt]

  The compat test suite does a directory listing to get the bmap files
  that should be checked. This was discovering the signature files, which
  aren't valid bmap files and this caused the test to fail.

  Fix this by moving the signatures to a subdirectory so that the compat
  test doesn't see them anymore.

* Tests: Quieten test suite. [Joshua Watt]

  Quites down the test suite so that output is only shown if something
  goes wrong to help make it easier to figure out what is wrong when
  something fails

* Tests: Add clearsign test. [Joshua Watt]

  Adds a test to ensure that the CLI can accept a clearsigned bmap file

* Ci: Fix poetry install. [Joshua Watt]

  Fixes the installation of poetry to use the updated method

* Add properly formatted changelog. [Niklas Kunz]

  The new changelog uses the format of https://keepachangelog.com/en/1.0.0/.

* Fix the poetry installation in the CI workflow. [Niklas Kunz]

* Correctly format remaining test in legacy tests. [Niklas Kunz]

* Add `black` as development dependency and use it in Actions workflow. [Niklas Kunz]

* Move __main__.py into bmaptools module. [Niklas Kunz]

* Fix minor Markdown formatting issues. [Niklas Kunz]

* Merge pull request #109 from mntns/gh-actions. [Niklas Kunz]

  Add basic GitHub Actions workflow

* Add code checking step using black to workflow. [Niklas Kunz]

* Create basic GitHub Actions workflow. [Niklas Kunz]

* Move LICENSE to project root. [Niklas Kunz]

* Adjust vim headers to text width of 88 (following black) [Niklas Kunz]

* README.md: add a note about us looking for a maintainer. [Artem Bityutskiy]

  Plus remove a couple of trailing newlines.

* Format all Python code with `black` [Niklas Kunz]

* Improve README structure, make markdown more consistent. [Niklas Kunz]

* Move README.md into project root, provide example (#102) [Niklas Kunz]

* Add poetry manifest. [Niklas Kunz]

* Use gpg instead of gpgme module, implement test cases. [Benedikt Wildenhain]

* Merge pull request #99 from mntns/master. [Artem Bityutskiy]

  Add basic copying from stdin

* Add info about stdion copying to manpage. [Niklas Kunz]

* Add basic stdin read. [Niklas Kunz]

* Merge pull request #98 from zxcv1884/master. [Artem Bityutskiy]

  Fix _psplash_pipe part was skipped when _progress_file is null

* Fix _psplash_pipe part was skipped when _progress_file is null. [Jason]

* Merge pull request #96 from zxcv1884/master. [Artem Bityutskiy]

  Fix path parameter passing error of set_psplash_pipe function

* Fix path parameter passing error of set_psplash_pipe function. [Jason]

* Merge pull request #94 from scardracs/master. [Artem Bityutskiy]

  move COPYING to docs/COPYING

* Fix typo. [Marco Scardovi]

* Move TODO.md to docs/TODO.md. [Marco Scardovi]

* Move COPYING to docs/COPYING COPYING is a docs so it should be placed in the right subfolder, to make everything ordered. [Marco Scardovi]

* Merge pull request #90 from scardracs/master. [Artem Bityutskiy]

  Update README.md

* Update README.md. [Marco Scardovi]

* Merge pull request #89 from smcv/mock-imports. [Simon McVittie]

  tests: Fix import pattern for mock objects

* Tests: Fix import pattern for mock objects. [Simon McVittie]

  The legacy mock module contains a mock.mock submodule, but unittest.mock
  does not contain a redundant unittest.mock.mock. This bug was masked by
  the transparent fallback to the legacy mock module.

  The actual test only uses mock.patch(), so we can simplify by just
  importing the one member that we need.

* Merge pull request #88 from smcv/zstd-interactive. [Simon McVittie]

  tests: Pass -c -k options to zstd, too

* Tests: Pass -c -k options to zstd, too. [Simon McVittie]

  Otherwise we get interactive prompts during testing, like this:

      zstd: /*stdin*\: unexpected end of file
      zstd: /*stdin*\: unexpected end of file
      zstd: /*stdin*\: unexpected end of file
      zstd: /*stdin*\: unexpected end of file
      zstd: .../.pybuild/cpython3_3.9/build/4Khole_idts5mgb.img.zst already exists; overwrite (y/n) ?

* Merge pull request #87 from smcv/test-deps. [Simon McVittie]

  Use Python standard library in preference to external modules

* Tests: Try to use TemporaryDirectory from Python standard library. [Simon McVittie]

  This avoids an unnecessary external dependency with Python >= 3.2.

* Tests: Use unittest.mock from Python standard library if possible. [Simon McVittie]

  This avoids an unnecessary external dependency when using Python >= 3.3.

* Merge pull request #85 from vrubiolo/vrubiolo. [Artem Bityutskiy]

* Doc: move documentation to Markdown. [Vincent Rubiolo]

  This moves the documentation to the Markdown format for easy reading.

* Merge pull request #83 from dedekind/tests_fixes. [Artem Bityutskiy]

  Fix tests.

* Travis-ci config: update python versions. [Artem Bityutskiy]

* Travic-ci config: add test dependencies. [Artem Bityutskiy]

  We use 'mock' and 'backports.tempfile' in tests now, add these dependencies.

* Tests: fix test_bmap_helpers on non-ZFS. [Artem Bityutskiy]

  One test failed when running with on a system that does not have ZFS.

* TransRead: hide useless message. [Artem Bityutskiy]

  The previous patch (stop using 'subprocess.PIPE') addes a side-effect -
  now we see 'tar' the following tar message:

  tar: Removing leading `/' from member names'

  This patch gets rid of them.

* Do not use subprocess pipe. [Artem Bityutskiy]

  We use the 'subprocess' module for running external processes, and in
  few places we create sub-processes with the 'stderr=subprocess.PIPE'
  argument. Howerver, we never read from the pipe, which means that it may
  get filled and block the external program. This is dangerous and may
  lead to deadlock situations.

  This patch fixes the issue by removing the argument. If we do not read
  sub-process's 'stderr', it is OK for it to inherit it from the main
  program, so the error message will just go to bmaptool's standare error
  stream.

* TransRead: kill subprocesses. [Artem Bityutskiy]

  Kill and wait for subprocesses when destroying TransRead objects. This
  gets rid of the following warning (observed when running self-tests):

  /usr/lib64/python3.9/subprocess.py:1048: ResourceWarning: subprocess 140912 is still running
    _warn("subprocess %s is still running" % self.pid,

* Merge pull request #80 from smcv/psplash-pipe-docs. [Simon McVittie]

  Improve documentation of --psplash-pipe

* Expand documentation of --psplash-pipe to specify what is reported. [Simon McVittie]

* Correct parameter name when documenting --psplash-pipe in the man page. [Simon McVittie]


## v3.6 (2021-02-02)

### Other

* Release version 3.6. [Artem Bityutskiy]

* Add v3.6 release notes. [Artem Bityutskiy]

* Merge pull request #63 from agherzan/psplash. [Artem Bityutskiy]

  bmaptool: Implement flag to interact with psplash progress

* Bmaptool: Implement flag to interact with psplash progress. [Andrei Gherzan]

  This flag is implemented as a best effort to avoid breaking the
  writing functionality when psplash is not available. For example when
  bmap is used during boot where psplash might or might not be available.

* Merge pull request #70 from dellgreen/dpg/67/addZFSCompatibilityCheck. [Artem Bityutskiy]

  zfs file system compatibility checks added. #67

* Zfs file system compatibility checks added. #67. [Dell Green]

* Merge pull request #72 from dellgreen/dpg/67/addTestRequirementsFile. [Artem Bityutskiy]

  add test requirements file to capture dependencies required by test files

* Add test requirements file to capture dependencies required by test files. [Dell Green]

* Merge pull request #71 from dellgreen/dpg/67/gitignoreVscode. [Artem Bityutskiy]

  gitignore vscode related temp user files

* Gitignore vscode related temp user files. [Dell Green]

* Merge pull request #61 from sjoerdsimons/close-read-thread-on-execption. [Artem Bityutskiy]

  Always close the decompressor stdin

* Always close the decompressor stdin. [Sjoerd Simons]

  If the TransRead read thread for some reason hits an exception (e.g. the
  http connection got reset) the standard input from the decompressor
  should still be closed otherwise bmaptool will just block without ever
  detecting the read thread exploded.

* Merge pull request #69 from dedekind/fix-test-warning. [Artem Bityutskiy]

  tests: fix a couple of warnings

* Tests: fix a couple of warnings. [Artem Bityutskiy]

* Merge pull request #66 from dellgreen/dpg/65/zfsSeekHole. [Artem Bityutskiy]

  readme updated with information on ZFS compatibility. #65

* Readme updated with information on ZFS compatibility. #65. [Dell Green]

* Merge pull request #64 from MyleneJ/master. [Artem Bityutskiy]

  bmaptool: CLI: Fail when copying a bmap file

* Update CLI.py. [Artem Bityutskiy]

* Bmaptool: CLI: Fail when copying a bmap file. [Mylène Josserand]

  The current behavior is that if the user copies the bmap file
  by mistake, it prints a warning but it will copy the bmap file
  to the block device.

  Exemple:

  $ echo "test" > in
  $ bmaptool create in -o in.bmap
  $ bmaptool copy in.bmap out
  $ cat out
  <?xml version="1.0" ?>
  <!-- This file contains the block map for an image file, which is basically
       a list of useful (mapped) block numbers in the image file. In other words,
  ...

  Set the message as an error instead of a warning and update
  its content to be more explicit.

  Fixes f67fa08 ("bmaptool: do not fail when copying a bmap file")

* Merge pull request #60 from akiernan/master. [Artem Bityutskiy]

  bmaptool: Add zstd compression

* Bmaptool: Add zstd compression. [Alex Kiernan]

* Merge pull request #59 from smcv/skip-tests-on-fuse. [Simon McVittie]

  test_api_base: Skip test if filesystem is unsuitable

* Test_api_base: Skip test if filesystem is unsuitable. [Simon McVittie]

  When run on disorderfs (an artificial FUSE filesystem used by the
  Reproducible Builds project to detect filesystem order dependencies),
  we cannot map the file to detect holes. The same is likely to be true
  for other simple FUSE filesystems.

* Merge pull request #58 from smcv/57-stopiteration. [Simon McVittie]

* Filemap: catch StopIteration from next(iterator) [Simon McVittie]

  In Python >= 3.7, if code in a generator raises StopIteration, it is
  transformed into a RuntimeError instead of terminating the generator
  gracefully.


## v3.5 (2018-08-23)

### Other

* Release version 3.5. [Artem Bityutskiy]

* Merge pull request #54 from dedekind/prepare-for-3.5. [Artem Bityutskiy]

  Prepare for 3.5

* Make_a_release: remove out of date pieces. [Artem Bityutskiy]

  Remove things related to signed tarball (we do not do it anylonger),
  the 'devel' branch and tizen.

* Make_a_release: do not ask about tizen.org docs update. [Artem Bityutskiy]

* Bmaptool: do not mention Tizen in the man page. [Artem Bityutskiy]

* README: add docs from tizen.org. [Artem Bityutskiy]

  The Tizen IVI project did not see any visible changes for several years and it
  is probably going nowhere. We do not know for how long 'tizen.org' is going to
  host the old bmap-tools docs, so let's move it here.

  This is a simple copypaste with little formatting effort.

* README: update the doc. [Artem Bityutskiy]

  Remove ancient Tizen and infradead.org stuff.

* Document the 'contrib' subdirectory. [Artem Bityutskiy]

* Rename examples to contrib. [Artem Bityutskiy]

  I think it is common name for a project directory to store contributions that
  are kind of "on their own" - project maintainers to not really worry about this
  stuff and do not really maintain or test.

* RELEASE_NOTES: add bmap-tools v3.5 notes. [Artem Bityutskiy]

* Make_a_release: check local tree earlier. [Artem Bityutskiy]

  This script is supposed to semi-automate the process of making a new project
  relase. Among other things, it check that the local project copy does not have
  uncommitted changes. Let's do this check earlier, before walking the maintainer
  through the trouble of answering various questions.

* Upade development process. [Artem Bityutskiy]

  The hole idea with devel is out of date and we do not use it. We use the github
  process now and the project is too small for a separate 'devel' branch. We use
  the github process nowadays.

  Let's update the READ me file and the 'make_a_release.sh' script.

* Merge pull request #56 from ribalda/fix#55. [Artem Bityutskiy]

* BmapCopy: Do not show a warning if noop io scheduder is not available. [Ricardo Ribalda Delgado]

  New Linux Multi-Queue Block IO Queueing Mechanism does not have a noop
  scheduler, which result in an error when trying to set the io scheduler.

  Also according to the linux-blk maintainers:

  """
  don't change the default io scheduler as none, which shouldn't
  work well for slow disk, such as non-SSD.
  """

  So, this patch basically does not bother the user if noop is not
  available following this rationale :

  If noop is not available is because the kernel is using multi queue
  and then we should not change the io scheduler.

* Merge pull request #53 from iotbzh/master. [Artem Bityutskiy]

  Use python2 rpm macro for spec file

* Use python2 rpm macro for spec file. [Ronan Le Martret]

  * %__python is Prohibited, use %__python2 instead.
     See: https://fedoraproject.org/wiki/Packaging:Python
   * %__python is broken on fedora Rawhide.
   * %__python2 macro is provides by python2-rpm-macros.

* Merge pull request #52 from lsandoval/fix-empty-args-v2. [Artem Bityutskiy]

  bmaptools/CLI.py: Print help in case of no arguments

* Bmaptools/CLI.py: Print help in case of no arguments. [Leonardo Sandoval]

  Avoids the run-time exception on systems with python3 as the default
  python version (python2 requires a subparser so it fails on empty args):

      $ bmaptool
      Traceback (most recent call last):
        File "/usr/bin/bmaptool", line 11, in <module>
          load_entry_point('bmap-tools==3.4', 'console_scripts', 'bmaptool')()
        File "/usr/lib/python3.6/site-packages/bmaptools/CLI.py", line 715, in main
          args.func(args)
      AttributeError: 'Namespace' object has no attribute 'func'

  Suggested by: Simon McVittie [https://github.com/intel/bmap-tools/pull/51#issuecomment-398161212]

* Merge pull request #48 from dedekind/add-error_out. [Artem Bityutskiy]

  Print traceback when errorring out

* BmapCopy: add a couple of helpful debugging messages. [Artem Bityutskiy]

* Bmaptool: print traceback in case of failure. [Artem Bityutskiy]

  It is very hard to diagnos problems when there is no traceback. Lets stop hiding it and actually
  print it in case of any error. First print the traceback, then the error message - this way
  non-developers will first pay attention to the error message at the end, and develperes will have
  useful traceback when the bug report is filed.

  This patch introduces the "error_out" helper which prints the traceback, then the error message, and
  then terminate the program. Here is how an artificially ingected error in the reader thread look
  like without this patch:

  $ bmaptool copy https://xyz/image.raw ~/tmp/file
  bmaptool: ERROR: injected error

  And after this patch:

  $ bmaptool copy https://xyz/image.raw ~/tmp/file
  Traceback (most recent call last):
    File "/home/abityuts/git/bmap-tools/bmaptools/CLI.py", line 487, in copy_command
      writer.copy(False, not args.no_verify)
    File "/home/abityuts/git/bmap-tools/bmaptools/BmapCopy.py", line 581, in copy
      reraise(exc_info[0], exc_info[1], exc_info[2])
    File "/home/abityuts/git/bmap-tools/bmaptools/BmapCopy.py", line 495, in _get_data
      raise Error("injected error")

  bmaptool: ERROR: injected error

  In the latter case we clearly see where the problem is.

* Merge pull request #49 from dedekind/fix-url-uncompress. [Artem Bityutskiy]

* TransRead: cosmetic: liburl->urllib. [Artem Bityutskiy]

  Let's spell the library name as "urllib2" consistently.

* TransRead: unbreak reading compressed file from an URL. [Artem Bityutskiy]

  This patch fixes a regression introduced by commit 6343239fb2487c309c9573ee35e7832b08753180 -
  reading a compressed file from an URL stopped working. Apparently urllib's file-like objects do have
  a 'fileno', but reading from it gives EOF immediately. So lets use 'is_url' to make a decision about
  whether we create a reader thread or not.

* Merge pull request #47 from dedekind/fix-python3-seek. [Artem Bityutskiy]

  Fix python3 seek

* TransRead: handle absence of seek() better. [Artem Bityutskiy]

  The urllib2 file-like objects did not have 'seek()' python2 and we
  emulated it by reading and discarding the data. But in python3 the
  file-like objects to have the 'seek()' method, which raises an
  exception:

  $ python3 ./bmaptool copy https://xxx/image.raw ~/tmp/file
  Traceback (most recent call last):
    File "./bmaptool", line 11, in <module>
      sys.exit(main())
    File "/home/abityuts/git/bmap-tools/bmaptools/CLI.py", line 715, in main
      args.func(args)
    File "/home/abityuts/git/bmap-tools/bmaptools/CLI.py", line 477, in copy_command
      writer.copy(False, not args.no_verify)
    File "/home/abityuts/git/bmap-tools/bmaptools/BmapCopy.py", line 584, in copy
      raise exc_info[1].with_traceback(exc_info[2])
    File "/home/abityuts/git/bmap-tools/bmaptools/BmapCopy.py", line 503, in _get_data
      self._f_image.seek(first * self.block_size)
    File "/home/abityuts/git/bmap-tools/bmaptools/TransRead.py", line 587, in seek
      self._f_objs[-1].seek(offset, whence)
  io.UnsupportedOperation: seek

  This patch fixes the problem by intercepting the exception and fallig-back
  to emulated seek().

  This patch is an improved version of a patch from Ricardo Ribalda Delgado
  (ribalda in github). It basically implements what Simon McVittie (smcv in github)
  suggested in a review message.

* TransRead: rename _force_fake_seek to _fake_seek. [Artem Bityutskiy]

  The "_force" part does not really add value and makes the name unnecessary long.

* Merge pull request #46 from dedekind/fix-shutil_copy. [Artem Bityutskiy]

  Fix copying bmap and signature files

* CLI: python3: Fix copying images from URLs. [Ricardo Ribalda Delgado]

  When copying an image from a remote host we first create a temporary copy
  of the bmap and signature files locally. Because Python 3 distinguishes
  between (Unicode) text strings and byte sequences, we have to be
  consistent about copying from a binary file to a binary file: writing
  byte sequences to a text file is no longer allowed.

  This patch fixes the following crash:

      ```
      sudo bmaptool copy  http://****.com/qtec/europa/images/qt5022/qimage-dev-qt5022.wic  /dev/sdb
      bmaptool: info: discovered bmap file 'http://tftp.qtec.com/qtec/europa/images/qt5022/qimage-dev-qt5022.wic.bmap'
      Traceback (most recent call last):
        File "/usr/bin/bmaptool", line 11, in <module>
          sys.exit(main())
        File "/usr/lib/python3/dist-packages/bmaptools/CLI.py", line 715, in main
          args.func(args)
        File "/usr/lib/python3/dist-packages/bmaptools/CLI.py", line 423, in copy_command
          open_files(args)
        File "/usr/lib/python3/dist-packages/bmaptools/CLI.py", line 365, in open_files
          (bmap_obj, bmap_path) = find_and_open_bmap(args)
        File "/usr/lib/python3/dist-packages/bmaptools/CLI.py", line 335, in find_and_open_bmap
          shutil.copyfileobj(bmap_obj, tmp_obj)
        File "/usr/lib/python3.6/shutil.py", line 82, in copyfileobj
          fdst.write(buf)
        File "/usr/lib/python3.6/tempfile.py", line 622, in func_wrapper
          return func(*args, **kwargs)
      TypeError: write() argument must be str, not bytes
      ```

  [Commit message amended by Artem Bityutskiy]

* Merge pull request #45 from dedekind/fix-with_traceback. [Artem Bityutskiy]

  Fix with traceback

* Simplify python 2/3 compatibility handling. [Artem Bityutskiy]

  Let's rely on some of the goodies of the 'six' module instead of
  sprinkling "if sys.version" statements around.

* Fix python2 compatibility. [Artem Bityutskiy]

  The tool was originally written for python2, then was converted to python3.
  Part of the conversion was usin 'with_traceback()', which does not exist
  in python2. When reading a corrupted image, bmaptool fails like this under
  python2:

  [abityuts@abityuts-desk bmap-tools (master)]$ python2.7 ./bmaptool copy ~/tmp/bmap/image.raw.bz2 ~/tmp/file
  bmaptool: info: discovered bmap file '/home/abityuts/tmp/bmap/image.raw.bmap'
  bmaptool: info: block map format version 2.0
  bmaptool: info: 250000 blocks of size 4096 (976.6 MiB), mapped 125 blocks (500.0 KiB or 0.1%)
  bmaptool: info: copying image 'image.raw.bz2' to file 'file' using bmap file 'image.raw.bmap'
  bmaptool: info: 100% copied
  Traceback (most recent call last):
    File "./bmaptool", line 11, in <module>
      sys.exit(main())
    File "/home/abityuts/git/bmap-tools/bmaptools/CLI.py", line 715, in main
      args.func(args)
    File "/home/abityuts/git/bmap-tools/bmaptools/CLI.py", line 477, in copy_command
      writer.copy(False, not args.no_verify)
    File "/home/abityuts/git/bmap-tools/bmaptools/BmapCopy.py", line 584, in copy
      raise exc_info[1].with_traceback(exc_info[2])
  AttributeError: 'Error' object has no attribute 'with_traceback'

  This patch fixes the problem.

  This patch started using the 'six' module which makes compatibility easier
  support.

* Merge pull request #44 from dedekind/cleanup-1. [Artem Bityutskiy]

* BmapHelpers: consmetic rearrangements. [Artem Bityutskiy]

  Let's be consistent and put the module comment before imports.
  Remove junk newlines.

* Merge pull request #40 from lurch/minimal_example. [Artem Bityutskiy]

  Add minimal bmap-parsing example

* Add minimal bmap-parsing example. [Andrew Scheller]

* Merge pull request #39 from lurch/patch-1. [Artem Bityutskiy]

  Fix type of caught exception

* Fix type of caught exception. [Andrew Scheller]

  See #31

* Merge pull request #36 from lurch/patch-1. [Artem Bityutskiy]

  Fix filename typo

* Fix filename typo. [Andrew Scheller]

* Merge pull request #37 from lurch/patch-2. [Artem Bityutskiy]

  Fix comment from FIBMAP to FIEMAP

* Fix comment from FIBMAP to FIEMAP. [Andrew Scheller]

* Merge pull request #33 from iotbzh/master. [Alexander D. Kanevskiy]

  Update packaging

* Update spec file packaging. [Ronan]

  - Change URL for github source.
   - Update build dependency.

* Fix debian packaging. [Ronan]

  - Since bmaptool file is a symlink (80c6f9), we don't want to
     package it.
   - the file /usr/bin/bmaptool, will be auto gen.
    Doc about automatic script creation:
    http://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation

* Merge pull request #35 from kad/errno. [Alexander D. Kanevskiy]

  Fix errno usage

* Fix errno usage. [Alexander D. Kanevskiy]

  Instead of os.errno.* it should be used as errno.*

* BmapHelpers.py: fix [Errno 25] Inappropriate ioctl for device (#30) [tcler.yin]

  * BmapHelpers.py: fix [Errno 25] Inappropriate ioctl for device

  see detail:
   https://github.com/01org/bmap-tools/issues/29


## v3.4 (2017-09-04)

### Other

* Update release notes, preparation for 3.4 release. [Alexander Kanevskiy]

* Merge pull request #27 from bartosh/master. [Alexander D. Kanevskiy]

  Ported to Python3. Fixes #14

* Port to Python3: add python3 targets to .travis.yml. [Ed Bartosh]

  Added supported Python 3 versions to the Travis CI configuration.

* Port to Python3: mention supported Python versions in setup.py. [Ed Bartosh]

  Added classifiers for supported Python versions 2.7 and 3.

* Port to Python3: fix small incompatibilities. [Ed Bartosh]

  Replaced xrange->range, iter.next -> next(iter),
  print -> print() etc to make the code working in
  both Python2  and Python3.

* Port to Python3: use string type for SUPPORTED_BMAP_VERSION. [Ed Bartosh]

  Current code used text and int types for SUPPORTED_BMAP_VERSION
  variable. Generally it's not good to mix data types like that,
  but it worked in Python 2. However, it breaks in Python 3 when
  trying to compare integer and string variables.

  Used strings for all SUPPORTED_BMAP_VERSION variables to fix
  this issue and make the code working in Python2 and Python3.

* Port to Python3: fix raising exceptions. [Ed Bartosh]

  Changed the code that raises exceptions with traceback
  using old syntax that's not supported in Python3:
      raise extype, exobj, traceback

  Used new syntax instead:
      raise exobj.with_traceback(traceback)

* Port to Python3: fix UnsupportedOperation exception. [Ed Bartosh]

  Current bmaptool code assumes that if object has 'fileno'
  method it can be safely called and passed to isatty function
  to test if object is assiciated with a tty device.
  Unfortunately this approach doesn't work in Python3 and
  causes exception "UnsupportedOperation: fileno" for StringIO
  objects.

  Used isatty method of the file object to fix this.

* Port to Python3: use binary data for file operations. [Ed Bartosh]

  Python3 uses text and binary data instead of Unicode and
  8-bit strings. The code that writes binary data to files
  has to be changed significantly to work for Python2 and
  Python3.

  Encoded strings before writing to binary files. Used
  struct module to correctly write bytes to binary files.
  Converted string literals to binary literals.

* Port to Python3: use floor division operator. [Ed Bartosh]

  In Python3 division operator / was changed from integer(floor)
  division to floating point division. This breaks bmaptools code
  that uses division operator and expects integer result.

  Used floor(integer) division operator // as it works in both
  Python3 and Python2 and has the same meaning.

* Port to Python3: fix module imports. [Ed Bartosh]

  Queue, thread, urlparse, httplib and urllib modules
  were renamed or moved in Python3.

  Imported modules using 'import <module> as' to make the code
  works in both Python2 and Python3.

* README: fix git URL (#26) [Diego Rondini]

* TransRead: Fix differentiating between local files and urllib (#22) [sjoerd-ccu]

  Commit 6343239fb was meant to take a different code path for urllib
  downloads and local files, however the check to differentiate between
  the two as broken as it turns out urllib objects also have fileno
  attributes.

  Fix this by specifically checking the object type and only then take the
  direct codepath. This resolved bmaptool copy failing when using urls
  instead of local files.

* Add support for lz4 compression in .lz4, .tar.lz4 and .tlz4 files. [Mike Kazantsev]

* Travis CI: switch to Ubuntu 14.04 and use optional compressors. [Alexander D. Kanevskiy]

* BmapHelpers: re-factor imports of modules (#19) [Alexander D. Kanevskiy]

  Unify import of all used imports in this file.

* Merge pull request #18 from kad/feature-unzip. [Alexander D. Kanevskiy]

* TransRead: support zip compressed images. [Alexander D. Kanevskiy]

  Some projects ship images compressed with zip, for cross OS
  compatibility. Support read from such archives, assuming that
  image is the first file in that archive. This is same assumption
  as in case of tar.gz format.

  Closes #10

* Merge pull request #16 from kad/feature-zero-bsize. [Alexander D. Kanevskiy]

  get_block_size: if we can't get from ioctl, try from os.stat()

* Get_block_size: if we can't get from ioctl, try from os.stat() [Alexander D. Kanevskiy]

  Under some conditions, ioctl FIGETBSZ can't return real value.
  We can try to use fallback via os.stat() to get block size.

  Closes #15

* Cleanup code formatting according to recommendations in PEP8. [Alexander D. Kanevskiy]

* Merge pull request #13 from kad/feature-travis-xfs-tests. [Alexander D. Kanevskiy]

  XFS support: hint filesystem about expected maximum size of image file

* XFS support: hint filesystem about expected maximum size of image file. [Alexander D. Kanevskiy]

  XFS has feature about speculative pre-allocation of blocks based on
  amount information written in the end of open file. In case of sparse
  files it might lead to more mapped blocks than really expected.
  Thus, truncate to desired size destination file as early as possible
  and then write blocks that should be mapped the middle of it.

  Closes #6

* Merge pull request #12 from kad/feature-coverage. [Alexander D. Kanevskiy]

  travis-ci: Use of codecov.io service

* Travis-ci: Use codecov.io service for displaying coverage reports. [Alexander D. Kanevskiy]

* Merge pull request #11 from kad/feature-isatty. [Alexander D. Kanevskiy]

* CLI: display progress indicator only on tty devices. [Alexander D. Kanevskiy]

  It doesn't make sense to display progress indicator if tool invoked
  from scripts.

  Closes #8

* Merge branch 'feature-console_scripts' into devel. [Alexander D. Kanevskiy]

  Closes #2

* Bmaptool: add symlink to __main__.py wrapper for compatibility. [Alexander D. Kanevskiy]

  Old habits do not die easily, thus add bmaptool symlink in top project
  directory, so tool can be easily invoked during development phase.

* CLI: small PEP8 cleanups. [Alexander D. Kanevskiy]

* __main__.py: wrapper to invoke CLI interface from zipapp. [Alexander D. Kanevskiy]

* Bmaptool: use console_scripts to invoke cli interface to the library. [Alexander D. Kanevskiy]

  Now command line interface is part of the library and uses
  setuptools mechanism console_scripts to distribute and invoke
  CLI interface

* .gitignore: add standard Python ignores. [Alexander D. Kanevskiy]

* TransRead: try to have the child process read the compressed file directly. [Simon McVittie]

  I've had problems with the read thread not terminating when expected
  and the main thread blocking in join() as a result. This simplifies
  the situation significantly: the read thread is only used when we're
  using urllib to download a file.

* Initial travis-ci support. [Alexander D. Kanevskiy]

  At the moment, bmaptool has limitations on environments where it
  can run. For Travis CI it would mean Python 2.6/2.7 as well as
  non-container environment, due to XFS specifics.

* Packaging: do not requires pigz in case of Tizen. [Gui Chen]

  pigz is not available in Tizen so remove to correct it

* Debian: fix changelog formatting. [Artem Bityutskiy]

* Bmaptool: remove extra white-spaces. [Artem Bityutskiy]

  Just a clean-up to comply with one of python PEPs.

* Bmap-tools: do not use term "subcommand" [Artem Bityutskiy]

  Just call them "commands" instead, which is cleaner.

* Bmaptools: silence false pylint warning. [Artem Bityutskiy]

* Bmap-tools: add vim defaults. [Artem Bityutskiy]

  ... to be extra-nice to vim users.

* Bmap-tools: make header comments consistent. [Artem Bityutskiy]

  ... and update the date in the Copyright statement.

* Bmaptool: rework logging. [Artem Bityutskiy]

  Let's use logging the right way, instead of passing the 'log' object around,
  just configure the root logger in 'bmapt-tool', and create per-module loggers,
  which will inherit the root logger's settings.

* TODO: add another work item. [Artem Bityutskiy]

* Bmaptool: remove documentation duplication. [Artem Bityutskiy]

  We now have bmaptool documentation in the web, and in the man page. No need to
  duplicate it in the doc string, simply because it may easily get out of date
  and inconsistent with the other documentation. So simply refer to the web site
  in the doc string. Also, use the docstring in the help output.

* Packaging: install the COPYING license file. [Artem Bityutskiy]

* Packaging: fix Fedora RPM dependency. [Artem Bityutskiy]

  This patch fixes a problem with the following symptom:

  $ sudo yum update python
  Loaded plugins: langpacks, refresh-packagekit
  Resolving Dependencies
  --> Running transaction check
  ---> Package python.x86_64 0:2.7.5-9.fc20 will be updated
  ---> Package python.x86_64 0:2.7.5-11.fc20 will be an update
  --> Processing Dependency: python-libs(x86-64) = 2.7.5-11.fc20 for package: python-2.7.5-11.fc20.x86_64
  --> Running transaction check
  ---> Package python-libs.x86_64 0:2.7.5-9.fc20 will be updated
  ---> Package python-libs.x86_64 0:2.7.5-11.fc20 will be an update
  --> Processing Dependency: /bin/python for package: bmap-tools-3.2-1.15.1.noarch
  --> Finished Dependency Resolution
  Error: Package: bmap-tools-3.2-1.15.1.noarch (@tools)
             Requires: /bin/python
             Removing: python-2.7.5-9.fc20.x86_64 (@fedora)
                 Not found
             Updated By: python-2.7.5-11.fc20.x86_64 (updates)
                 Not found
   You could try using --skip-broken to work around the problem
   You could try running: rpm -Va --nofiles --nodigest

  This happened on a Fedora system, which had the bmap-tools package installed,
  and where I tried to update the python package.

  The RPM build logs had this:
  Requires(rpmlib): rpmlib(CompressedFileNames) <= 3.0.4-1 rpmlib(FileDigests) <= 4.6.0-1 rpmlib(PartialHardlinkSets) <= 4.0.4-1 rpmlib(PayloadFilesHavePrefix) <= 4.0-1
  Requires: /bin/python python(abi) = 2.7

  So there was a "/bin/python" requirement.

  The theory is that "python.x86_64 0:2.7.5-9.fc20" had "Provides: /bin/python",
  but this line was removed in "python.x86_64 0:2.7.5-11.fc20". But I did not
  check this theory.

  And the other theory is that rpm build picks "/bin/python" instead of
  "/usr/bin/python" simply because "/bin" goes first in the PATH environment
  variable in the build root environment.

  Fedora says that the right way to call 'setpu.py' is

  %{__python} setup.py

  see https://fedoraproject.org/wiki/Packaging:Python,
  and this is what this patch does.

* TODO: add another item. [Artem Bityutskiy]

* Packaging: remove useless 'changelog' section from the spec file. [Artem Bityutskiy]

* Packaging: harmonize package description. [Artem Bityutskiy]

  We have various packaging meta-data with package description. Let's make sure
  it is the same everywhere: deb, rpm, python egg.

* Man: remove useless .RE. [Artem Bityutskiy]

  Remove useless '.RE' which does not have any visible effect.

* Man: mention the mailing list address in man page. [Artem Bityutskiy]

* Man: document the --debug option in the man page. [Artem Bityutskiy]

* Packaging: remove lzma dependency. [Artem Bityutskiy]

  We do not need python-lzma anymore, so remove the dependency.

* Man pages: update bmaptool version number. [Artem Bityutskiy]

  ... also use correct man section number "1" instead of "17".
  ... also add a TODO entry which will remind me to automate this.

* Bmaptool: ament commentaries. [Artem Bityutskiy]

  This is a minor change where I just amend few commentaries.

* Make_a_release.sh: also suggest to push to tizen.org. [Artem Bityutskiy]

  Now we also have a repository at tizen.org, remind about the fact that we need
  to push there too.


## v3.2 (2014-02-19)

### Other

* Release version 3.2. [Artem Bityutskiy]

* Make_a_release.sh: remove the rc_num macro. [Artem Bityutskiy]

  The previous release could be an -rc release. And we have to remove the
  'rc_num' macro before doing the final release, otherwise the RPM will have
  an '-rcX' version suffix.

* Bump the version to 3.2-rc2. [Artem Bityutskiy]

* TransRead: make the reader thread to be a daemon. [Artem Bityutskiy]

  Mark the reader thread as "daemon", which means that when the main script
  exits, the thread will be just killed instead of blocking the entire script.
  This change makes bmaptool exit immediately on Ctrl-C. Without this change,
  bmaptool is blocked for some times because the reader thread is blocked,
  because it is reading data via a very slow link. It is fine to just kill it in
  this case, instead of waiting.

* RELEASE_NOTES: add a note about speed improvement. [Artem Bityutskiy]

* Packaging: bump version number to 3.2-rc1. [Artem Bityutskiy]

* TODO: remove an irrelevant item. [Artem Bityutskiy]

  We re-wrote the decompressing code and this item became irrelevant.

* Man: write about new supported compressors. [Artem Bityutskiy]

  And re-structure the text a bit to make it more readable.

* RELEASE_NOTES: write 3.2 release notes some more. [Artem Bityutskiy]

  Tell about new compressors support, re-structure, make the text nicer.

* Tests: cosmetic imports re-arranging. [Artem Bityutskiy]

  Just arrange the imports at the beginning of the files so that they would look
  the same in all the tests. Just for consistency.

* Test_api_base: use external programs for compression. [Artem Bityutskiy]

  Stop using internal python modules for compressing test files, and just like we
  did in the previous commit, use external programs for this.

* TransRead: re-write decompress logic. [Artem Bityutskiy]

  This is a relatively big change which completerly re-writes the decompression
  logic of this module. I did not split this change on many smaller changes,
  since this is difficult to do, and I am trying to optimize my time usage. Yes,
  bad explanation, but honest :-) But the diff is not that big anyway!

  At the moment, TransRead tries to use various python tools for decompressing:
  the 'bz2', 'tarfile', and 'zlib' modules. For 'xz', we are using the 'lzma'
  module from backports, which is not present everywhere, e.g., OpenSuse does not
  have it.

  This worked relatively well, until I got these bug-reports and requrests:
  Out-of-memory failure: https://bugs.tizen.org/jira/browse/TIVI-2388
  pbzip2 support request: https://bugs.tizen.org/jira/browse/DEVT-141
  lzo support request: https://bugs.tizen.org/jira/browse/DEVT-140

  The first is very difficult to fix. We already pass only 128 bytes of data to
  the bz2 decompressor. Makin it smaller would probably help, but would probably
  fail on a system with even less memory. I tried to handle the MemoryError
  exceptions, but the bz2 decompressor objects becomes unusable after the
  MemoryError exception.

  Then pbzip2 - the standard python 2.x 'bz2' library just does not support
  multiple streams. I tried to use the 'bz2file' backport from python 3.x, but it
  is really not very user-friendly, since users need to install it from PyPI.

  Then 'lzo' support is absent in python 2.x. There is the 'python-lzo' package
  in some distros providing the lzo functionality, but it is again, not available
  in OpenSuse.

  So I figured that this is too much of the trubles and tried to dump all the
  decompression cruft and just use the standard Linux tools for that: bzip2,
  gzip, xz, lzop, and tar. Just piple the data from the input file to the
  decompressor program's stdin, and read the uncompressed data from its stdout.
  And this worked perfectly. And became faster. And the out-of-memory problems
  seemed to go away. And both pbzip2 and lzo became supported. And the amount of
  code became less.

  So I've just decided to go this way and this patch does exactly that.

  This patch also adds several standard, but rarely used extensions: .tbz2, .tbz,
  .tb2, and .txz, as aliases for 'tar.bz2' and 'tar.xz'.

* Packaging: add compressors dependencies. [Artem Bityutskiy]

  Add a bunch of dependencies: bzip2, gzip, tar, lzo, xz, pbzip2, pigz. This is a
  preparation to the next change where we'll re-write the TransRead module and
  start using external tools for decompression.

* TransRead: use a 1M buffer size for the ssh pipe. [Artem Bityutskiy]

  Set buffer size for the SSH pipe to be 1M. Frankly, I am not 100% sure if this
  matters, it looks like it makes reading the file over ssh a bit faster.

* BmapHelpers: add program_is_available. [Artem Bityutskiy]

  This patch adds the 'program_is_available()' helper function which checks if an
  external program is available in the PATH. Also make TransRead use this helper.

* Test_api_base: do not seek TransRead objects back. [Artem Bityutskiy]

  The TransRead objects are not suppoesed to be seek'ed back. This happen to work
  for non-compressed files, but would fail for compressed files.

* Test_api_base: remove unused import. [Artem Bityutskiy]

  Pylint noticed this:
  W: 33, 0: Unused import random (unused-import)

* Tests: rename a couple of test classes. [Artem Bityutskiy]

  This is a cosmetic change.

  Most of the tests were started by copying the 'test_api_base', and the main
  class was not re-named from 'TestCreateCopy' to something else. Let's do this
  now.

* Man page: mention SEEK_HOLE. [Artem Bityutskiy]

  Mention that we fall-back to SEEK_HOLE when FIEMAP is not supported.

* RELEASE_NOTES: write about pbzip2 support. [Artem Bityutskiy]

* Bmaptool: handle TransRead errors. [Artem Bityutskiy]

  Catch both BmapCopy and TransRead module errors since they all contain
  a user-friendly error message.

* TransRead: provide user-friendly error message for pbzip2. [Artem Bityutskiy]

  If the bz2 file is a multi-stream archive and the 'bz2file' library was not
  found, we cannot read the file and just fail with a scary traceback. This patch
  adds a nice user-friendly message which suggests what to do in this case.

* TransRead: add pbzip2 support. [Artem Bityutskiy]

  This patch adds support for multi-stream bz2 files (creted with pbzip2).
  Unfortunately, the standard python 2.7 'bz2' module does not support it, so we
  use the 'bz2file' module from PyPI.

  'bz2file' may not be present in the system, in which case we fall-back to the
  standard python 2.7 'bz2' module. As a bonus, 'bz2file' is a little bit faster
  than 'bz2' even for single-stream archives.

* TransRead: remove useless check. [Artem Bityutskiy]

  The _CompressedFile class is designed to work with compressed files, and it
  makes no sense to use it for uncompress files. So let's assume that the
  decompression function is always present and remove the useless
  "if self._decompress_func" check.

* TransRead: remove code duplication. [Artem Bityutskiy]

  We had some amount of duplicated code related to opening a tar file - introduce
  a '_open_tarfile()' helper function for this instead.

  On top of this, stop using 'tarfile' modules for opening 'tar.gz' and 'tar.bz2'
  files since for some reasons this is a lot slower than using the
  '_CompressedFile' module, like we do for 'tar.xz' files.

* Bmaptool: assume that bmap and asc files are not compressed. [Artem Bityutskiy]

  Remove useless 'is_compressed' check for bmap and asc files which are never
  compressed, since compression is currently detected by file extention, so .bmap
  and .asc extentions always correspond to an uncompressed file.

* TransRead: store compression type name. [Artem Bityutskiy]

  Introduce an 'compression_type' attribute and store the compression format
  there. This will be needed in the next patches, where we will add 'pbzip2'
  support. Also, remove the 'is_compressed' attribute sinc this is the same as
  'compression_type == "none"'.

* BmapCreate: catch exception from the Filemap module. [Artem Bityutskiy]

  The 'Filemap' module can raise exceptions in case of errors. Let's catch them
  and re-raise as 'BmapCreate.Error' exceptions. This will make 'bmaptool' catch
  them too and print a nice error message.

* RELEASE_NOTES: start release notes for v3.2. [Artem Bityutskiy]

  Starte preparing bmapt-tools-3.2 release notes and describe the tmpfs and
  SEEK_HOLE support there.

* Filemap: move _lseek out of the class. [Artem Bityutskiy]

  Pylint suggested that the 'FilemapSeek._lseek()' would better be an independent
  function. Let's do this and move it out of the FilemapSeek class.

* BmapCreate: fix and tidy-up bmap file formatting. [Artem Bityutskiy]

  We generated bogus commentary for files with zero mapped block:

	<!-- Count of mapped blocks: 0 bytes or 0.0%0.0    -->
          <MappedBlocksCount> 0   </MappedBlocksCount>

  and this patch fixes it. On top of this, we put too many white-spaces
  in the <MappedBlocksCount> because we used wrong variable to calculate
  the maximum amount of spaces. Fix this as well.

* Filemap: add debugging facility. [Artem Bityutskiy]

  Add the 'log' parameter to the Filemap* classes to allow passing the logger
  object where the debugging prints will go. This is similar to what we have in
  the BmapCopy module. Also add the same parameter to 'BmapCreate' and make sure
  that 'bmaptool' passes its logger to 'BmapCreate', which then passes it to
  'Filemap*' objects, where we use it for debugging.

  This makes sure that '--debug' triggers debugging messages from 'Filemap*'
  ojects.

* Make all classes to be of new style. [Artem Bityutskiy]

  Pylint nowadays prints something like this when it sees old-style classes:

  C: 41, 0: Old-style class defined. (old-style-class)

  Let's fix it globally by making all our classes to be of new style.

* TODO: remove the SEEK_HOLE entry. [Artem Bityutskiy]

  because it is done.

* Tests: amend commentaries. [Artem Bityutskiy]

  Now we do support tmpfs, since we have the FiemapSeek class which works on
  tmpfs, so correct commentaries.

* Test_filemap: improve the test. [Artem Bityutskiy]

  The test did not cover the 'block_is_mapped()' and 'block_is_unmapped()'
  methods of the Filemap module - improve this. Also, test both 'FilemapFiemap'
  and 'FilemapSeek' classes.

  On top of this, do not fail if the kernel of the file-system does not support
  FIEMAP or SEEK_HOLE.

* Filemap: implement ugly heuristics for SEEK_HOLE. [Artem Bityutskiy]

  Old kernels do not have real SEEK_HOLE support, but instead, provide a stub
  implementation which just returns EOF. And there seem to be no easy way to find
  out whether the implementation is real or fake. But we need to know this,
  because it is crucial for use since we won't get the block map with fake
  SEEK_HOLE implementation.

  This patch implements an ugly test which appends a hole to the image file,
  tests whether SEEK_HOLE is fake or not, and then truncats the image file back
  to the original size.

* Filemap: distinguish the "not supported" error. [Artem Bityutskiy]

  Introduce a new exception type (ErrorNotSupp) in order to distinguish the
  situation when FIEMAP or SEEK_HOLE is not supported by the system.

* Filemap: implement the FilemapSeek class. [Artem Bityutskiy]

* Filemap: introduce a FilemapSeek class. [Artem Bityutskiy]

  This patch introduce a so far dummy FilemapSeek class which sill be an
  alternative to FilemapFiemap. It also introduces the 'Filemap' function which
  automatically selects which class will be used for getting block map. The
  FIEMAP method is preferred as it is supposedly faster (at least for large
  enough files).

  This patch also converts all places where we creant an instance of 'Fiemap'
  class to use the 'Filemap' function.

* Filemap: introduce base class. [Artem Bityutskiy]

  We are going to introduce another class which uses the 'SEEK_HOLE' mechanism
  for getting file block map, and some of the 'class Fiemap' functionality is
  going to be the same in both. Let's separate that common functionality into a
  separate '_FilemapBase' class which other classes will inherit.

  The '_FilemapBase' class also defines the methods child classes have to
  implement and documents them.

* Filemap: simplify the FIEMAP failure error path. [Artem Bityutskiy]

  Simplify the FIEMAP ioctl error handling by removing the 'looks like your
  kernel does not support FIEMAP' note. I've recently got a bug report from the
  field where people hit this error, and that line not was not actually appended
  to the error message because the error code was something like ENOTSUPP. And
  the error was anyway very clear and readable.

  So let's just remove that part and simplify the code.

* Filemap: remove useless constants and a parameter. [Artem Bityutskiy]

  This patch simplifies the Fiemap class API and removes the 'buf_size'
  constructor parameter because it is useless. The default 256K value is good
  enough. Remove a couple of related constants along with this for the same
  reason.

* Rename Fiemap.py to Filemap.py. [Artem Bityutskiy]

  The FIEMAP ioctl is not supported by tmpfs, so currently bmaptool fails to
  create the bmap file when the file resides on tmpfs. This is unfortunate.

  However, tmpfs supports 'SEEK_HOLE' which we can use instead of FIEMAP.

  This patch is a preparation for adding 'SEEK_HOLE' support. Namely, we re-name
  the Fiemap.py module to Filemap.py, where we'll support both FIEMAP and
  SEEK_HOLE. Variables which contain 'fiemap' are also re-named so that they now
  contain 'filemap' instead.

* Update TODO list. [Artem Bityutskiy]

* Make_a_release: remove TODOs. [Artem Bityutskiy]

  One is done, the other one is not needed so far, so let's kill that. Also, we
  have a separate TODO file which should be used instead.

* Make_a_release: do not forget to push the devel branch out. [Artem Bityutskiy]

  The script assumes that the devel branch is pushed out, but this is not
  necessarily the case. Teach 'make_a_release' script reminding about pushing the
  devel branch too.


## v3.1 (2013-11-07)

### Other

* Release version 3.1. [Artem Bityutskiy]

* Docs: update the README file. [Artem Bityutskiy]

* Docs: add v3.1 release notes Signed-off-by: Artem Bityutskiy <artem.bityutskiy@intel.com> [Artem Bityutskiy]

* TODO: add another entry. [Artem Bityutskiy]

* Silence all uninteresting pylint recommendations. [Artem Bityutskiy]

  Pylint produces many recommendations, but sometimes they are not very
  interesting and I am not planning to change the code to fulfill them. For all
  such cases, let's silence them. There are also a couple of false-positive
  warnings like 'unable to import backports', silence them too.

* Tests/oldcodebase: disable all pylint warnings. [Artem Bityutskiy]

  This is old code, and we are not goint to fix any warnings there, and we are
  not going to modify these files, so let's just silence pylint for these old
  files.

* Make_a_release: remind about updating the compat test. [Artem Bityutskiy]

* TODO: remove the complete items. [Artem Bityutskiy]

* Test_compat: improve backward compatibility test. [Artem Bityutskiy]

  Currently 'test_compat' verifies that BmapCopy handles all the older bmap file
  formats. This patch adds a check that older BmapCopy implementations are able
  to handle all the compatible bmap file formats.

  The reason for this test is that I once screwed it up with version 1.4: it had
  incompatible changes, and older versions of BmapCopy crash with 1.4. If I had
  this test-suite, I would add the new bmap format file to 'tests/test-data', and
  the mistake would be caought right away.

* Tests: add old code-base. [Artem Bityutskiy]

  I am going to add a test which verifies that older BmapCopy work fine with
  newer compatible bmap formats, as well as newer BmapCopy works fine with all
  the older bmap formats.

  This patch simply add a copy of various BmapCopy versions.

* TODO: update the todo list. [Artem Bityutskiy]

* Test_compat: new test for checking backward-compatibility. [Artem Bityutskiy]

  This test makes sure that BmapCopy works fine with all the previous bmap file
  formats.

* Tests: add test data. [Artem Bityutskiy]

  Add a randomly-generated test image and bmap files of different formats. The
  intention is to add a test case which verifies backward-compatibility.

* Test_api_base: move a couple of functions to helpers.py. [Artem Bityutskiy]

  Move '_copy_and_verify_image()' and  '_calculate_chksum()' to the helpers.py
  file since I am going to use them in the new unit test which I am about to add.
  Remove the leading underscore since these functions become usable from outside.
  Move some necessary module imports to helpers.py too.

* Test_api_base: rename _copy_image. [Artem Bityutskiy]

  This function copies and verifies, so let's call it '_copy_and_verify_image()'.

* Test_api_base: use file name in _copy_image (3) [Artem Bityutskiy]

  This is a minor clean-up which changes the '_copy_image()' so that it expects
  the bmap file to be a path and does not allow for file-like objects. This is
  cleaner than seeking the file-like object in this function, which changes the
  object state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Test_api_base: use file name in _copy_image (2) [Artem Bityutskiy]

  This is a minor clean-up which changes the '_copy_image()' so that it expects
  the image to be a path and does not allow for file-like objects. This is
  cleaner than seeking the file-like object in this function, which changes the
  object state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Test_api_base: use file name in _do_test. [Artem Bityutskiy]

  This is a minor clean-up which changes the '_do_test()' so that it expects the
  image to be a path and does not allow for file-like objects. This is cleaner
  than seeking the file-like object in this function, which changes the object
  state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Test_api_base: use file name in _generate_compressed_files. [Artem Bityutskiy]

  This is a minor clean-up which changes the '_generate_compressed_files()' so
  that it expects the image to be a path and does not allow for file-like
  objects. This is cleaner than seeking the file-like object in this function,
  which changes the object state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Test_api_base: use file name in _calculate_chksum. [Artem Bityutskiy]

  This is a minor clean-up which changes the '_calculate_chksum()' so that it
  expects the image to be a path and does not allow for file-like objects. This
  is cleaner than seeking the file-like object in this function, which changes
  the object state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Test_api_base: use image name in _copy_image. [Artem Bityutskiy]

  This is a minor clean-up which changes the '_copy_image()' so that it expects
  the image to be a path and does not allow for file-like objects. This is
  cleaner than seeking the file-like object in this function, which changes the
  object state.

  This change is rather mechanical, and this is actually a preparation for the
  upcoming changes, where I am going to make '_copy_image()' and some other
  function generic, and then use them in a new test which I am going to add.

* Tests: add proper license header to all tests. [Artem Bityutskiy]

* BmapCopy: handle bmap format version 2.0. [Artem Bityutskiy]

  This patch makes BmapCopy handle bmap format version 2.0, which is identical to
  format 1.4. Format 1.4 was released by a mistake. Format 1.4 makes bmaptool
  v2.x crash because it has incompatible changes. This is unfurtunate, sorry for
  this.

* BmapCreate: fix bmap file format version. [Artem Bityutskiy]

  By a mistake, I've made bmap file format version to be 1.4, while is should
  really have been 2.0, because there were incompatible changes. Fix this.

* BmapCopy: verify versions in a single function. [Artem Bityutskiy]

  This patch is a minor clean-up and a preparation to the upcoming changes. It
  makes sure that all the differences between various bmap format version are
  handled in the '_parse_bmap()' method, and we do not have to worry about the
  format differences later on.

* TODO: add some more entries. [Artem Bityutskiy]


## v3.0 (2013-10-02)

### Other

* Release version 3.0. [Artem Bityutskiy]

* Bmaptool: warn if destination file is suspecious. [Artem Bityutskiy]

  Warn a user if he/she writes to a file under /dev, but it is not a special
  device file, but just a regular file. This should improve user-friendliness.

* BmapCreate: make sha256 to be the default. [Artem Bityutskiy]

* BmapCopy: add a couple of debug messages. [Artem Bityutskiy]

  Add a couple of useful debug messages to BmapCopy.

  Also, do not print the progress indicator when debugging is on.

* BmapCopy: rename _logger to _log. [Artem Bityutskiy]

  This patch renames the _logger class attribute to "_log". The reason is to make
  logging statements shorter. Besides, we use "log" in bmaptool, so this also
  brings a bit more consistency.

  Do the same change also in TransRead.

* Bmaptool: prefix debug messages with time-stamp. [Artem Bityutskiy]

  This patch makes the debug messages to be prefixed with time-stamp, as well as
  the module name and line number. The time-stamp is highlighted with green
  color.

  This patch introduces a custom formatter class in order to be able to format
  debug and other loglevls differently.

* BmapCopy: increase the batch queue length. [Artem Bityutskiy]

  BmapCopy reads and writes from different threads to exploit parallelizm. There
  is a "batch queue" where the reader supply 1MiB buffers and the writer consumes
  them. The length of the queue is 6 for block devices and 2 for files. This
  patch makes it to be 6 everywhere since 2 is rather short.

* Bmaptool: introduce --debug option. [Artem Bityutskiy]

  We often need to print debugging information, let's add a --debug option for
  this.

* Bmaptool: fix --nobmap case. [Artem Bityutskiy]

  One of the previous commits introduced the NamedFile class and broke the
  --nobmap case, because we created a NamedFile object even when f_bmap was None.
  This patch fixes the problem.

* Bmaptool: print warning messages even with --quiet. [Artem Bityutskiy]

  When the --quiet option is used, we print only error messages, and warnings
  are suppressed. However, it is a good idea to print warnings even with --quiet,
  since they usually tell about problems users should better know about.

* Bmaptool: remove junk argument. [Artem Bityutskiy]

  This patch remove unneeded junk argument from the BmapBdevCopy constructor
  invocation and fixes this issue:

  Traceback (most recent call last):
    File "./bmaptool", line 684, in <module>
      sys.exit(main())
    File "./bmaptool", line 668, in main
      args.func(args, log)
    File "./bmaptool", line 434, in copy_command
      image_size, logger=log)

* TransRead: correct bad English one of the messages. [Artem Bityutskiy]

* Make_a_release.sh: misc little changes. [Artem Bityutskiy]

  Require that the release is made in the devel branch. Amend the instructions
  that we print. Remove trailing white-spaces from the changelog.

* RELEASE_NOTES: add 3.0 release notes. [Artem Bityutskiy]

* TransRead: support .gizp extension. [Artem Bityutskiy]

  We support GnuZip files, but only look at the .gz extension, and forget about
  .gzip extension. This patch fixes the situation.

* Tests: do not mark the entry point as static. [Artem Bityutskiy]

  Remove the @staticmethod decorator, because old unittest module on Centos6 does
  not recognize static entry points and does not execute tests.

* Tests: add a Centos 6 work-around. [Artem Bityutskiy]

  Centos 6 is very old, and it has old unittest library, and the newer one which
  we need is called 'unittest2' there. This patch adds the corresponding
  work-around to make our tests pass in Centos 6.

* Packaging: add missing dependencies. [Artem Bityutskiy]

* TransRead: don't parse URL twice in case of ssh proto. [Andy Shevchenko]

  _open_url() method already parses the URL. Let's use it instead of doing
  parsing second time.

* Make_a_release.sh: various improvements. [Artem Bityutskiy]

  This patch makes several improvements in the make_a_release.sh.

  * Ask the maintainer tough questions about whether the docs were updated
  * Automatically update the RPM and Debian changelog files
  * Automatically increase version number in various places

* BmapCreate: remove a dot in bmap file comment. [Artem Bityutskiy]

  To be consistent with other commentaries, lets not put the dot at the end of
  the one-line comment.

* TODO: update the file to reflect the current state. [Artem Bityutskiy]

* BmapCopy: improve XML parsing error message. [Artem Bityutskiy]

  When BmapCopy fails to parse the XML file, it prints something like this:

  bmaptool: ERROR: cannot parse the bmap file '/home/dedekind/tmp/Fedora-19-i386-CHECKSUM' which should be a proper XML file: not well-formed (invalid token): line 1, column 1

  (yes, I deliberately fed bmaptool a bogus file)

  The problem is that sometimes we actually modify the bmap file a bit before
  parsing. For example, we do this when the bmap file is signed with a clearsign
  OpenPGP signature.

  This means that the line number does not match the file name we print. This
  patch improves the situation by providing the bogus line number and a bit of
  the context in the exception error message.

* Bmaptool: override bmap path. [Artem Bityutskiy]

  Sometimes we create temporary files for the bmap file object, and the 'name'
  attribute of the object contains the temporary file path in these cases. Then
  we pass the bmap file object to, say, BmapCreate module, which uses the 'name'
  attribute in various error messages. This, for example, leads to the following
  confusing error message:

  bmaptool: ERROR: cannot parse the bmap file '/tmp/tmpUkoTxA' which should be a proper XML file

  It is a lot nicer to print the original path instead of the temporary path.
  Let's do this with help of the 'NamedFile' class that we have. It helps
  substituting the 'name' attribute with something we want the user to see.

* Docs: update bmaptool's man pages. [Artem Bityutskiy]

  Add information about new options, and more.

* Setup.py: automatically detect version number. [Artem Bityutskiy]

  We currently duplicate the project version number in bmaptool and setup.py
  files. Let's get rid of the duplication and have setup.py parse the bmaptool
  file and fetch the version number.

* TODO: remove an entry about checking zeroes. [Artem Bityutskiy]

  I think I will not implement this because it makes little sense. Drop the
  unmapped areas anyway, why would we care checking their contents? What for?

* Fiemap: synchronize the file before invoking the ioctl. [Artem Bityutskiy]

  Early FIEMAP implementations had many bugs related to cached dirty data. And
  this is why it is safer to synchronize the file before invoking FIEMAP for it.
  Let's start using the 'FIEMAP_FLAG_SYNC' FIEMAP ioctl flag which does exactly
  that.

* TODO: update the list. [Artem Bityutskiy]

  Remove the item about GPG signatures support, add a reminder about updating the
  man pages with the GPG and hash functions information.

* Bmaptool: implement GPG signature verification. [Artem Bityutskiy]

  This is a feature which was requested by the Fedora communitiy.

  Both clearsign and detached GPG signatures are supported. The signature file
  auto-discovery is supported (similar to bmap file auto-discovery).

  More user-facing information will be added to the man page a bit later.

  We add the following command-line options:
      1. --bmap-sig option for specifying the detached signature file path
      2. --no-sig-verify option for making bmaptool avoid verifying the clearsign
         signature and avoid signature file auto-discovery

* Bmaptool: disallow simultaneous --bmap and --nobmap. [Artem Bityutskiy]

  Do not allow users to use --bmap and --nobmap at the same time since it makes
  no sense.

* Bmaptool: cleanups. [Artem Bityutskiy]

  This function improves the commentaries and renames several functions. The
  renames are about removing the 'copy_command_' prefix from function names,
  because it is not very readable and we do not use it consistently anyway.

* Bmaptool: do not fail when copying a bmap file. [Artem Bityutskiy]

  It is possible that the user copies the bmapfile itself using 'bmaptool copy'.
  Most probably this is just by a mistake. In this case bmaptool just fails,
  since it discovers the bmap file, and it does not match the "image" (where the
  image is the same bmap file).

  This patch teaches bmaptool to handle this case by dropping the discoverd bmap
  file if its path is the same as the image path.

* Fiemap: fix failure for zero-sized files. [Artem Bityutskiy]

  The Fiemap module fails for zero-sized file with these symptoms:

  Traceback (most recent call last):
    File "./bmaptool", line 561, in <module>
      sys.exit(main())
    File "./bmaptool", line 545, in main
      args.func(args, log)
    File "./bmaptool", line 419, in create_command
      creator = BmapCreate.BmapCreate(args.image, output, "sha256")
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/BmapCreate.py", line 163, in __init__
      self.fiemap = Fiemap.Fiemap(self._f_image)
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/Fiemap.py", line 120, in __init__
      self.block_is_mapped(0)
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/Fiemap.py", line 175, in block_is_mapped
      struct_fiemap = self._invoke_fiemap(block, 1)
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/Fiemap.py", line 149, in _invoke_fiemap
      % (block, self.blocks_cnt))

  This patch fixes the issue.

* Bmaptool: start using sha256 when creating bmap file. [Artem Bityutskiy]

  Switch from using SHA1 to SHA256 for the 'bmaptool create' command.

  Basically, this is what the Fedora community requested, with a reference to
  this:

  http://csrc.nist.gov/groups/ST/hash/policy_2006.html

* TODO: remove sha256 entry. [Artem Bityutskiy]

* BmapCreate: implement arbitrary hash type support. [Artem Bityutskiy]

  Instead of just supporting SHA1 hash functions type, support arbitrary hash
  function type. Well, actually "arbitrary" means any hash function supported by
  the "hashlib" python module.

  In particular, we are interested to switch from SHA1 to SHA256.

  Unfortunately, this is a format change, since format version 1.3 guaranteed
  that checksum is always SHA1. This is why this patch also increases the format
  version to 1.4.

* BmapCopy: support arbitrary checksum types. [Artem Bityutskiy]

  This patch makes BmapCopy support bmap format version 1.4 which allows for
  and arbitrary checksum type, not only SHA1. We are, particularly, interested in
  SHA256 support.

* Test_api_base: use sha256 instead of sha1. [Artem Bityutskiy]

  Well, this does not matter in this case at all, but I am going to switch to
  SHA256 in BmapCreate, so changing the tests just for consistency.

* Bmaptools: preparations to switch to sha256. [Artem Bityutskiy]

  In all places where it does not matter which exactly checksum we calculate,
  substitute 'sha1' with 'chksum'. This is a preparation for the further change
  where we will switch from using SHA1 checksums to using SHA256 checksums.

* TransRead: remove local caching functionality. [Artem Bityutskiy]

  Remove the local caching functionality of the TransRead module. This
  functionality does not really belong to the module, and it only makes things
  more complex. It is better to either make users of TransRead to locally cache
  remote files, or create a small wrapper over TransRead for these purposes.

  Since currently there is only one user of this functionality, we just implement
  local caching in bmaptool directly.

* TODO: add another item. [Artem Bityutskiy]

* TransRead: improve user experience. [Artem Bityutskiy]

  This patch solves the following problem.

  1. I forgot to define the proxy.
  2. I run bmaptool, it blocks, and several minutes later it fails with an error
     like "Connection timed out"

  I would instead like it to tell me that something is going wrong much earlier,
  why should I wait for several minutes?

  This patch improves the way we open URLs. Now instead of using the default
  (usually long) timeout, we first try with a short timeout, and if we cannot
  open the URL, we print user a warning, and then try to open with the default
  timeout. The user may press Ctrl-C once he/she sees the warning, or start
  checking the connectivity.

* TransRead: accept the logger object. [Artem Bityutskiy]

  In order to improve user experience, I would like to print warnings when we
  cannot open the URL for some time. This requires the TransRead object to accept
  the logger object, or take the global one.

* TransRead: handle the urllib2.URLError exception. [Artem Bityutskiy]

  When opening an URL with urllib2, handle the URLError exceptions too.

  This patch adds a new "except" statement instead of adding the exception object
  to the existing array. The reason is that in the next commit we will need to
  handle the urllib2.URLError exceptions a bit differently.

  This patch also refactors the code a tiny bit as a preparation to the next
  commit.


## v2.6 (2013-09-11)

### Other

* TODO: add another comment. [Artem Bityutskiy]

* Release version 2.6. [Artem Bityutskiy]

* Make_a_release.sh: add few more reminders. [Artem Bityutskiy]

* TODO: add more entries. [Artem Bityutskiy]

* README: document the make_a_release.sh script. [Artem Bityutskiy]

* Add the TODO list. [Artem Bityutskiy]

* TransRead: do not cache local uncompressed files. [Artem Bityutskiy]

  When the file is already local and uncompressed, do not create a temporary copy
  of it when 'local' is True.

  On top of this, re-use own __init__ function to re-open the local copy of the
  remote/compressed file.

* Tests: cover .xz files too. [Artem Bityutskiy]

* TransRead: store all file descriptors in a list. [Artem Bityutskiy]

  This patch improves readability and does not do any functional changes.

  In the TransRead module we have chains of file-like objects, every next element
  of the chain is based on the previous one. And we store each element of the
  chain in own variable like 'self._file_obj3', which is a bit ugly. Let's
  introduce a 'self._f_objs' list, and just append there, and the last element is
  always the final "transparent read" file descriptor.

* Packaging: remove unneeded files. [Artem Bityutskiy]

  I cannot really explain why these files were needed, but they are not needed
  anymore, according to Ed Bartosh. So removing them with pleasure.

* RELEASE_NOTES: add changelog for release 2.6. [Artem Bityutskiy]

  Strictly speaking I've added a feature, so 2.6 is not just a bug-fix release,
  but the feature is rather small and does not deserve a new major release.

* TransRead: uncompress 'tar.xz' files on-the-fly. [Artem Bityutskiy]

* TransRead: uncompress .xz files on-the-fly. [Artem Bityutskiy]

* TransRead: close all the files. [Artem Bityutskiy]

  Although CPython reference-counts objects and destroys them when they are no
  longer used, it is still good practice to close all the opened files
  explicitly, especially if we are talking about a library.

  TransRead did not explicitely close the tar file object, and this patch fixes
  this.

  Additionally, add few useful commentaries.

* BmapCopy: fix a typo in error message. [Artem Bityutskiy]

  ... add a missing whitespace.

* Bmaptools: put __init__ first. [Artem Bityutskiy]

  It is just a common convention to put __init__ at the very beginning of the
  class. And let's also put then the __del__ function to be the second.

  So this patch does not do any functional modifications, just re-structuring.

* Debian: add a dependency to python-lzma. [Artem Bityutskiy]

  We'll soon need it in order to support .xz files.

* Packaging: add pyliblzma for Fedora dependencies. [Artem Bityutskiy]

* Packaging: remove tabs and extra white-spaces. [Artem Bityutskiy]

  Put one white-space after every keyword and do not try to align things, and
  also do not use tabs. I think I saw this recommendation is the Fedore guide or
  something, but not 100% sure. But at least this makes it easier to change the
  spec file.

* Make_a_release.sh: use git send-email. [Artem Bityutskiy]

  Use git send-email instead of mutt, since the mutt command we had does not
  really work, and I am unable to find out how to make it work.

  Additinally, inform about where to find packages for various distributions.


## v2.5 (2013-08-09)

### Other

* Release version 2.5. [Artem Bityutskiy]

* Make_a_release.sh: a script for cutting releases. [Artem Bityutskiy]

  Not complete, but a good start anyway. Intended to be used by me.

* Packaging: improve the summary text in RPM packaging. [Artem Bityutskiy]

* Packaging: use opensuse_bs macro. [Artem Bityutskiy]

  The <CI_CNT>.<B_CNT> trick is OBS-specific, so wrap it with the 'opensuse_bs'
  macro.

* README: add more information for opensource community. [Artem Bityutskiy]

  Plus some minor re-structuring.

* Remove junk back-slashes. [Artem Bityutskiy]

  In Python we don't need the line-continuation "\" inside (), [], {}.

  Suggested by Simon McVittie <simon.mcvittie@collabora.co.uk>.

* Bmap-tools: make one-line comments comply with PEP257. [Artem Bityutskiy]

* Bmap-tools: do not use extra spaces to comply with PEP8. [Artem Bityutskiy]

  Apparently in python it is preferrable to avoid white-spaces when specifying
  the default values.

* Debian: switch to debhelper 9. [Simon McVittie]

  Debhelper 9 "compatibility level" is what's currently recommended.
  Debian 7 and Ubuntu 12.04 both have a suitable debhelper version.

  At the Debhelper 7 or 8 "compatibility level" we would have used
  the deprecated python-support helper tool, whereas Debhelper 9 does
  not have a default Python packaging tool: choose dh_python2, part
  of the Debian/Ubuntu 'python' package since before Ubuntu 12.04
  and currently the recommended option. This needs a dependency on
  python-all (>= 2.7) so do that.

  In the process, switch the XS-Python-Version field from the deprecated
  keyword 'current' to ">= 2.7" (the recommended syntax),
  and remove the deprecated XB-Python-Version field.

* Remove stdeb-generated boilerplate from debian/rules. [Simon McVittie]

  This particular package doesn't contain any compiled code, let alone
  f2py, so there's no point in doing strange things with compiler/linker
  flags. If we gain any C code later, respecting the CFLAGS etc. is
  recommended anyway, to pick up "hardening" flags.

* Debian/control: depend on python-setuptools instead of -distribute. [Simon McVittie]

  python-setuptools is the module we actually import, and
  python-distribute has been merged into python-setuptools upstream.

* Debian/control: move to Section: utils. [Simon McVittie]

  Packages that are primarily a command-line tool, like git-buildpackage
  or offlineimap, usually go in the Section for that tool rather than
  Section: python. If this package ends up primarily acting like a library,
  it should produce a python-bmaptools package in Section: python,
  but that doesn't seem necessary or appropriate until it has
  third-party users.

* Put proper GPL declarations on the source files. [Simon McVittie]

  This is GPL best-practice. I have assumed that this package is
  intentionally placed under the GPL version 2 only (like Linux or
  ConnMan), and not dual- or multiple-licensed under the GPL version 2
  "or any later version" (like BlueZ).

  As a result, the wording used is similar to what is recommended in
  the GPL v2, but modified to omit the "or later" clause.

* BmapCopy: fix-up a commentary. [Artem Bityutskiy]

  Wrap a very long line which appeared after PEP8-nization.

* Use machine-readable format for debian/copyright. [Simon McVittie]

* Bmap-tools.spec: improve commentaries about Centos6 and argparse. [Artem Bityutskiy]

  The previous comment was a bit confusing.

* Debian/control: wrap and sort lists of (Build-)Depends. [Simon McVittie]

  This minimizes VCS diff/conflicts when they change.

* Rpm-packaging: improve the description. [Artem Bityutskiy]

  Improve the tool description for rpm packages.

* Debian/control: add a longer Description. [Simon McVittie]

  This paragraph from the bmaptool documentation on tizen.org matches
  what Debian packages typically have in their Description. The original
  description didn't really indicate why you would prefer bmaptool over
  alternatives like dd.

* BmapCopy: correct logged warning. [Simon McVittie]

* Tests: also comply with PEP8 for multiline comments. [Artem Bityutskiy]

* Bmaptool: use PEP8 commenting style. [Artem Bityutskiy]

  No functional changes, just amend multiline comments to match PEP8's
  recommendation.

* BmapCopy: downgrade inability to set sysfs parameters to a warning. [Simon McVittie]

  On distributions where unprivileged users can write to removable
  USB disks, this allows such a disk to be written with bmaptool
  (albeit with non-optimal performance) without being root.

  Artem: got some more explanations from Simon McVittie
  <simon.mcvittie@collabora.co.uk> about why we don't just add a special
  case for EPERM/EACCESS:

  """
  > On 28/06/13 12:47, Artem Bityutskiy wrote:
  > For a library, requiring the user to have a logger object is probably
  > not the nicest thing. And usually libraries do not print error messages,
  > they throw exceptions instead.

  I made the logger optional: if the caller doesn't supply one, BmapCopy
  will use logging.getLogger(__name__), i.e. the logger named
  "bmaptools.BmapCopy", which appears to be best-practice for Python
  logging. (You could use it for debug-logging too, if you wanted to.)

  Having logger=None cause logging to be suppressed, instead of using the
  logging module's defaults (which are to print 'No handlers could be
  found for logger "foo.bar"' the first time you use it, and not log
  anything...) would also be fine.

  Libraries throw exceptions if they couldn't do what you asked, but I
  think there's some room for a middle ground between "no, I can't" and
  silent success.
  """

  Fair enough, I think.

  Hoewver, I massged the patch a bit and improved the warnings to make
  them a bit more user-friendly and give users the idea what is the
  consequence of the warning.

* BmapCopy: have a Logger object. [Simon McVittie]

  Artem: In some situations we may want inform about various happenings, see the
  next patch for example. So let's teach the BmapCopy class to accept a 'logger'
  object.

* Debianisation: change versioning. [Artem Bityutskiy]

  Simon McVittie <simon.mcvittie@collabora.co.uk> requested this:

  "In Debian packaging it's conventional for version numbers like "2.4-1"
  to be the Debian package, and if derivatives need to fork it, they use a
  version like "2.4-1ubuntu1" (or "2.4-0ubuntu1" if they package something
  that isn't in Debian yet). You've been using version numbers like 2.4-1
  as upstream versions, so for now I'll have to act like a derivative
  distribution and use 2.4-1debian1 or something."

  So let's become a "native" package in order to make live of derivative
  distributions easier.

* BmapCreate: fix a typo in the bmap file comments. [Artem Bityutskiy]

  zeoro -> zero

* BmapCopy: remove a left-over comment. [Artem Bityutskiy]

* Fix debian/changelog syntax. [Simon McVittie]

  dpkg-source requires two spaces between the closing ">" around the
  email address and the first letter of the date.

* Add COPYING, a copy of the GPL v2. [Simon McVittie]

  This makes it considerably more straightforward for distributors
  to comply with the GPL's requirement to accompany the package with
  a copy of its license.

* Release version 2.4. [Artem Bityutskiy]

* Docs: update man pages. [Artem Bityutskiy]

* TransRead: amend commentaries. [Artem Bityutskiy]

  Update and fix spelling in several commentaries. No functional changes.

* RELEASE_NOTES: add a record for release 2.4. [Artem Bityutskiy]

* TransRead: add support for ssh:// URLs. [Artem Bityutskiy]

  This patch adds support for flashing from an SSH source. I need this
  functionality, for example, when I build images on a remote host, but flash
  them locally, and I want bmaptool to read the image directly from the SSH
  host.

  Unfortunately, liburl2 does not support ssh:// URLs, and there seem to be no
  standard python libraries for such URLs. There is a "paramiko" python module,
  but it is not a standard part of python, and not at least Tizen does not have
  it, so I do not want to use it.

  Thus, I use the system 'ssh' tool directly. Note, the paramiko module actually
  does the same.

  Both password and key authentication types are supported. In order to use
  password authentication, the password has to be passed via URL:

  bmaptool copy ssh://user:pass@host:path destination

  If the URL does not contain a password, we assume key-based authentication is
  configured.

* TransFile: introduce "_force_fake_seek" attribute. [Artem Bityutskiy]

  TransFile object provide read interface to compressed and/or remote files.
  TransFile objects also allow seeking files forward. When the file happens to be
  a local uncompressed file, seeking is done using the native 'seek()' method.
  Otherwise, we emulate this by just reading the required amount of bytes from the
  file and discarding the data.

  The way we detect whether we can seek using the native method or not is that we
  call 'hasattr(file_obj, "seek")', and if the file object has the "seek()"
  method, we use it.

  However, there are situations when a files have the "seek()" method, but it is
  not really usable. For example, stdout.

  This patch introduces an internal attribute named "_force_fake_seek", which
  will force fake seek implementation for such file objects.

  We do not need this change right now, but will need it soon. So this is just a
  preparation for the coming changes.

* RELEASE_NOTES: improve 2.3 release notes. [Artem Bityutskiy]

* Release version 2.3. [Artem Bityutskiy]

* Docs: update release notes for release 2.3. [Artem Bityutskiy]

* BmapCopy: verify bmap file checksum. [Artem Bityutskiy]

  If bmap file format is greater than 1.3, verify its integrity by checking the
  SHA1 checksum.

* BmapCreate: generate bmap file checksum. [Artem Bityutskiy]

  I got a bug report recently and the investigation showed that it is caused by
  corrupted bmap file. Once the user re-downloaded the bmap file, the problem
  was solved.

  This patch tries to improve robustness by protecting the bmap file with SHA1
  checksum. At the very end we calculate the SHA1 checksum of the entire bmap
  file with the in-file SHA1 value = all zeroes, and put the result to the bmap
  file.

  In order to verify the checksum, we will have to substitute the SHA1 checksum
  with all zeroes again and calculate SHA1 of the file.

* TransRead: fix pylint warning. [Artem Bityutskiy]

  Remove an unused module.

* BmapCreate: enable scalability optimization. [Artem Bityutskiy]

  This patch changes the layout of the bmap file a little bit. Before this
  change, we wrote the mapped blocks count at the very end, because we only knew
  at the very end.

  In BmapCopy we need to know the amount of mapped blocks before we start
  copying, and this forces us to read entire bmap file to find out the amount of
  mapped blocks. This is not an issue when bmap file is small, but if it gets a
  lot bigger, this becomes a lot slower.

  In this patch, we change bmap file layout a little bit and now we put the
  mapped block cound at the beginning of the bmap file. This makes it possible to
  parse it more effeciently. This also makes it more human readable.

* TransRead: implement local caching. [Artem Bityutskiy]

  Teach TransRead to cache remote and compressed files with local uncompressed
  files, which makes it possible to use operations like mmap and so on. This
  patch adds a 'local' parameter to the TransRead constructor which is 'False' by
  default, and when it is 'True', TransRead creates a local copy of the back-end
  file.

* TransRead: allow reading entire file. [Artem Bityutskiy]

  The 'read()' method of python file objects does not require the user specifying
  the size, and allows for negative size as well. In this case it just reads
  entire file. Ament TransRead to also follow this convention.

* Bmaptools: amend commentaries about file-like objects. [Artem Bityutskiy]

  In some places we require true file objects, i.e., they should be backed by
  real files. However, comments just tell about file-like objects. Amend the
  comments.

* BmapCopy: improve error message. [Artem Bityutskiy]

* BmapCopy: provide bmap version major and minor numbers. [Artem Bityutskiy]

  Besides providing the full string version, provide also the major and minor
  components of the version as ingegers. This is going to be useful soon.

* Bmaptool: do not feed stdout to BmapCreate. [Artem Bityutskiy]

  We are going to modify BmapCreate to support bmap file checksum. And we'll have
  to seek the bmap file. However, the problem is that bmaptool may feed
  BmapCreate with stdout which is not seekable.

  This patch changes bmaptool and makes it create a temporary file when the user
  does not specify the output file, give it to BmapCreate, and then print the
  contents of the file to stdout. We use the 'NamedTemporaryFile' python method
  which automatically removes the file when the program crashes or is interrupted
  with Ctrl-C.

* Bmaptool: assign user-friendly names to file objects. [Artem Bityutskiy]

  Just like many things in python, BmapCopy assumes that file-like objects'
  'name' attribute contains something user-frienly. And this is the case in most
  of the cases, except one case. If the file object was created using
  'os.fdopen()', the name will be '<fdopen>', instead of something user-friendly.
  And bmaptool uses 'os.fdopen()' when opening block devices, because we need to
  use special open flags. This results in poor error messages like this:

  bmaptool: ERROR: wrote 187980 blocks from image
	  'ivi-wayland-tizen-2.0a_20130501.1-sdb.raw.bz2' to '<fdopen>' ...

  And the problem is that you cannot change the name - it is a read-only
  attribute. This problem will probably be resolved in python 3, but not in 2.x,
  see http://bugs.python.org/issue1625576

  This patch works-around the problem by creating own simple dummy class which
  overrides the name.

* Tests: do not truncate too far. [Artem Bityutskiy]

  This patch changes the '_create_random_sparse_file()' function behavier a
  little and teaches it to not truncate files too far. For example, if we
  asked '_create_random_sparse_file()' to create an 8193 bytes sparse file,
  it could do the following:

  1. Map the first 4KiB block
  2. Map the second 4KiB block
  3. Truncate to 12KiB
  4. And at the end truncate to 8183 bytes

  This worked fine on ext4 - we ended up with a file with 2 first blocks mapped
  and an unmapped block at the end. However, on btrfs this leads to a file with
  all 3 blocks mapped (I assume 1 block = 4KiB). And this is not a bug, this is
  just how btrfs allocates blocks and we cannot, generally speaking, make any
  assumptions about the allocation algorithms.

  This patch changes '_create_random_sparse_file()' and makes it avoid truncating
  files too far. Namely, we will truncate only to the end of the last block.

  Now the tests pass on btrfs (kernel version 3.8.6).

* Release version 2.2. [Artem Bityutskiy]

* RELEASE_NOTES: amendments and prepare for release 2.2. [Artem Bityutskiy]

  Create own section for release 2.1, and start preparing for release 2.2 by
  describing the 2.2 changes.

* TransRead: support URLs with user name and password. [Artem Bityutskiy]

  Markus Lehtonen reported that bmaptool does not support URLs which contain user
  name and password, e.g., https://marquiz:qwerty@server.com/nice.image.bz2.

  This patch adds the corresponding support. What we do is we first parse the URL
  and try to figure out if it contains user name and password, and if it does,
  open the URL with a specially build opener which supports authentication.

* TransRead: handle more exceptions. [Artem Bityutskiy]

  Handle a couple of exceptions from httplib which may be caused by incorrect
  URL. Just catch them, and re-raise with a more understandable error message.
  The TransRead user will catch it and exit nicely, without a scary stackdupm
  like this:

  Traceback (most recent call last):
    File "./bmaptool", line 389, in <module>
      sys.exit(main())
    File "./bmaptool", line 373, in main
      args.func(args, log)
    File "./bmaptool", line 154, in copy_command
      copy_command_open_all(args, log)
    File "./bmaptool", line 109, in copy_command_open_all
      image_obj = TransRead.TransRead(args.image)
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/TransRead.py", line 232, in __init__
      self._open_url(filepath)
    File "/mnt/bigssd/dedekind/work/tizen/git/bmap-tools/bmaptools/TransRead.py", line 210, in _open_url
      self._file_obj = opener.open(url)
    File "/usr/lib64/python2.7/urllib2.py", line 400, in open
      response = self._open(req, data)
    File "/usr/lib64/python2.7/urllib2.py", line 418, in _open
      '_open', req)
    File "/usr/lib64/python2.7/urllib2.py", line 378, in _call_chain
      result = func(*args)
    File "/usr/lib64/python2.7/urllib2.py", line 1215, in https_open
      return self.do_open(httplib.HTTPSConnection, req)
    File "/usr/lib64/python2.7/urllib2.py", line 1174, in do_open
      h.request(req.get_method(), req.get_selector(), req.data, headers)
    File "/usr/lib64/python2.7/httplib.py", line 958, in request
      self._send_request(method, url, body, headers)
    File "/usr/lib64/python2.7/httplib.py", line 992, in _send_request
      self.endheaders(body)
    File "/usr/lib64/python2.7/httplib.py", line 954, in endheaders
      self._send_output(message_body)
    File "/usr/lib64/python2.7/httplib.py", line 814, in _send_output
      self.send(msg)
    File "/usr/lib64/python2.7/httplib.py", line 776, in send
      self.connect()
    File "/usr/lib64/python2.7/httplib.py", line 1160, in connect
      self._tunnel()
    File "/usr/lib64/python2.7/httplib.py", line 741, in _tunnel
      (version, code, message) = response._read_status()
    File "/usr/lib64/python2.7/httplib.py", line 371, in _read_status
      raise BadStatusLine(line)
  httplib.BadStatusLine: ''

* TransRead: introduce a helper for opening URLs. [Artem Bityutskiy]

  Indroduce an '_open_url()' helper method which opens an URL. This helper will
  be useful soon, because we are going to make the URL opening a bit more
  complex.

* TransRead: relocate the close method. [Artem Bityutskiy]

  This is a minor change which relocates the 'close' method to a different place,
  in order to keep all the file methods together.

* README: minor typo fix. [Artem Bityutskiy]

* Packaging: correct dependencies for Centos6. [Artem Bityutskiy]

  Centos6 uses python 2.6 which does not have the argparse module that we use.
  However, there is a possibility to add the argparse module by installing the
  'python-argparse' package which is available from 3rd party Centos6
  repositories. Thus, add the corresponding dependency for Centos6.

* Test_fiemap: fix pylint warning. [Artem Bityutskiy]

  Using builtins like 'filter()' is discouraged nowadays, and pylint generates
  this warning:

  W: 46,22:_check_ranges: Used builtin function 'filter'

  Use a generator expression instead of the 'filter' built-in.

* BmapCopy: disable a flals pylint warning. [Artem Bityutskiy]

  Silence this one:
  W:275,0: Anomalous backslash in string: '\0'. String constant might be missing an r prefix.

* BmapCopy: fix writitng to a dm-zero device. [Artem Bityutskiy]

  Dm-zero devices expose "none" in their '/sys/block/<disk>/queue/scheduler' file
  and there is no current scheduler. Our code was assuming there is always the
  current scheduler in brackets (e.g., "noop deadline [cfq]"), which lead to a
  crash when writing to a dm-zero device:

  Traceback (most recent call last):
    File "./bmaptool", line 389, in <module>
      sys.exit(main())
    File "./bmaptool", line 373, in main
      args.func(args, log)
    File "./bmaptool", line 192, in copy_command
      writer.copy(False, not args.no_verify)
    File "/mnt/bigssd/dedekind/work/tizen/tools/git/bmap-tools/bmaptools/BmapCopy.py", line 578, in copy
      self._tune_block_device()
    File "/mnt/bigssd/dedekind/work/tizen/tools/git/bmap-tools/bmaptools/BmapCopy.py", line 535, in _tune_block_device
      self._old_scheduler_value = match.group(1)

* TransRead: limit the amount of bytes we read at a time. [Artem Bityutskiy]

  In the function which implements fake seek forward we first calculate the
  amount of bytes we have to read from the file to seek forward to the requisted
  position, and then read that data in one go. However, the seek may be really
  far forward, and we'll end up reading really a lot of data in one go, which
  leads to high memory consumption.

  This patch fixes the issue by limiting the amount of data we read in one go to
  1MiB.

* Bmaptool: print useful information in sace of MemoryError. [Artem Bityutskiy]

  Catch the MemoryError exception which means that the script ran out of memory
  and print useful debugging information in this case (/proc/meminfo and
  /proc/self/status).

* Bmaptool: silence few false pylint warnings. [Artem Bityutskiy]

  W:339,0: Anomalous backslash in string: '\0'. String constant might be missing an r prefix.
  W:340,0: Anomalous backslash in string: '\0'. String constant might be missing an r prefix.
  W:341,0: Anomalous backslash in string: '\0'. String constant might be missing an r prefix.

* Bmaptool: remove an unused variable. [Artem Bityutskiy]

* Bmaptool: minor white-space cleanup. [Artem Bityutskiy]

* Really release version 2.1. [Artem Bityutskiy]

* Release version 2.1. [Artem Bityutskiy]

* Tests: make tests work in Fedora 18. [Artem Bityutskiy]

  The tests create many temporary files and run FIEMAP on them. However, in
  Fedora 18 the '/tmp' is tmpfs which does not support FIEMAP, so 'nosetests'
  fails. Let's use the current directory for the tests instead.

* TransRead: fix out of memory issues with bzip2 files. [Artem Bityutskiy]

  This commit fixes a 'bmaptool copy' problem with the following symptom:

  Traceback (most recent call last):
    File "./bmaptool", line 372, in <module>
      sys.exit(main())
    File "./bmaptool", line 369, in main
      args.func(args, setup_logger(loglevel))
    File "./bmaptool", line 191, in copy_command
      writer.copy(False, not args.no_verify)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/BmapCopy.py", line 580, in copy
      BmapCopy.copy(self, sync, verify)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/BmapCopy.py", line 368, in _get_data
      self._f_image.seek(first * self.block_size)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/TransRead.py", line 247, in seek
      self._transfile_obj.seek(offset, whence)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/TransRead.py", line 69, in seek
      self._pos = _fake_seek_forward(self, self._pos, offset, whence)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/TransRead.py", line 33, in _fake_seek_forward
      buf = file_obj.read(to_read)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/TransRead.py", line 102, in read
      data = self._read_from_buffer(size)
    File "/opt/home/root/bmap/bmap-tools-2.0/bmaptools/TransRead.py", line 81, in _read_from_buffer
      data = self._buffer[self._buffer_pos:self._buffer_pos + length]
  MemoryError

  The reason is that bmaptool runs out of memory when copying a bzip2-compressed
  file which has large chunks of zeroes.

  I experimented a bit with a 4GiB file full of zeroes and compressed with bzip2.
  The memory consumption of 'bmaptool copy' was about 1.4GiB! The reason is that
  we read 128KiB of compressed input and decompress them in one go, which results
  in a huge output array. The situation with gzip2 is similar, but less severe.

  This patch adds a 'chunk_size' parameter to the '_CompressedFile' class
  constructor which we can use to limit the maximum amount of data we decompress
  at a time. For .bz2 files I found 128bytes to be reasonable, and for gzip files
  the default 128KiB seems to be just fine.

* TransRead: minor nicification. [Artem Bityutskiy]

  The 'decompress_func' argument of the '_CompressedFile' class constructor is
  optional, so make it be 'None' by default.

* RELEASE_NOTES: tell that map page was added. [Artem Bityutskiy]

* Packaging: add man pages. [Artem Bityutskiy]

* Remove the TODO file. [Artem Bityutskiy]

  .. as it is empty now.

* Add bmaptool man page. [Artem Bityutskiy]

* Docs: move documentation to a separate sub-directory. [Artem Bityutskiy]

* RELEASE_NOTES: a minor fix. [Artem Bityutskiy]

* Release version 2.0. [Artem Bityutskiy]

* TransRead: fix a MemoryError issu. [Artem Bityutskiy]

  Sometimes we run out of memory in TransRead.py, as it was reported by
  Dawei Wu <daweix.wu@intel.com>. I believe the problem is that we read too much
  of compressed data at a time. If the data contain all zeroes, they are
  decompressed into a huge buffer.

* TransRead: fix corner case in the fake seek function. [Artem Bityutskiy]

  When seeking beyond the file, the fake seek function returned incorrect value.
  Fix this.

* Pre-release version 2.0-rc5. [Artem Bityutskiy]

* TODO: remove an entry about locking. [Artem Bityutskiy]

  Let's add it when/if it is really needed.

* BmapCopy: restore the block device settings. [Artem Bityutskiy]

  Always restore the block device settings at the end.

* BmapCopy: fail if an optimization did not work. [Artem Bityutskiy]

  Instead of hiding failures when we are enabling optimizations - fail. This way
  we'll at least notice them.

* BmapCopy: do not check for os.path.exists exceptions. [Artem Bityutskiy]

  It is very unlikely that it fails, but if it does, we'll just have an unhandled
  exception, which is fine in this case.

* README: minor amendments. [Artem Bityutskiy]

* Pre-release 2.0-rc4. [Artem Bityutskiy]

* Bmaptool: improve --nobmap error message. [Artem Bityutskiy]

* Bmaptool: fix flashing without bmap. [Artem Bityutskiy]

  The auto-discovery function was buggy and returned a junk bmap file name if no
  bmap files was found.

* Pre-release 2.0-rc3. [Artem Bityutskiy]

* TransRead: catch ValueError exceptions. [Artem Bityutskiy]

  Sometimes urllib2 throws ValueError exceptions when it cannot open a local
  file. Catch it as well.

* Pre-release 2.0-rc2. [Artem Bityutskiy]

* Bmaptool: slight readability imporovement. [Artem Bityutskiy]

  Full paths may be very long, so print only basenames in the informational
  messages.

* Bmaptool: add image_size parameter to BmapBdevCopy constructor. [Mikko Ylinen]

  Align BmapBdevCopy class contructor parameters with BmapCopy
  class consturctor parameters.

* Bmaptool: print auto-discovered bmap file correctly. [Artem Bityutskiy]

  When the bmapfile was auto-discovered, we did not print its name correctly.

* Pre-release 2.0-rc1. [Artem Bityutskiy]

* BmapCopy: implement progress wheel. [Artem Bityutskiy]

  .. for the cases when the image size is not known.

* Bmaptool: do not discover bmap if --nobmap was given. [Artem Bityutskiy]

* RELEASE_NOTES: prepare 2.0-rc1 release notes. [Artem Bityutskiy]

* TODO: remove a done entry. [Artem Bityutskiy]

* Bmaptool: do not print progress bar when --quiet was used. [Artem Bityutskiy]

* Bmaptool: provied a link to the docs in help output. [Artem Bityutskiy]

* TransRead: fix opening URLs. [Artem Bityutskiy]

  Proxy did not work.

* Bmaptool: implement automatic bmap file discovery. [Artem Bityutskiy]

* TODO: add another item. [Artem Bityutskiy]

* BmapCopy: small documentation improvements. [Artem Bityutskiy]

* TransRead: fix few pylint warnings. [Artem Bityutskiy]

* TransRead: improve comments a bit. [Artem Bityutskiy]

* Test_api_base: test urllib2 as well. [Artem Bityutskiy]

  Prepend "file:" to file names sometimes to make all the I/O go through urllib2.

* TransRead: cleanup fake seek. [Artem Bityutskiy]

  Instead of patching objects run-time, just add seek() and tell() methods
  to classes we need to support and use a helper '_fake_seek_forward()' function
  from there. This is cleaner.

* BmapCopy: make error message more verbose. [Artem Bityutskiy]

  Print all file names in case of short read/write error.

* BmapCopy: print file name as well. [Artem Bityutskiy]

  When printing about SHA1 mismatch, also print the image file name.

* TransRead: switch to stream tar decompression. [Artem Bityutskiy]

  Unfortunatelly we lose the check for amount of members, because it is not
  compatible with stream extraction as it generates random seeks.

* TransRead: switch to CompressedFile for gzip compression. [Artem Bityutskiy]

  Switch to use the '_CompressedFile' class for gzip files as well. The benefit
  is that it does not require 'seek()' in the underlying file object, which
  urllib2 does not provide.

* TransRead: get rid of the __getattr__ method. [Artem Bityutskiy]

  The TransRead class implements very limited file-like objects. It is safer
  to explicitely specify all the methods it supports, instead of defaulting
  to the methods of the underlying 'transfile_obj'.

* TransRead: generalize the Bzip2Read class. [Artem Bityutskiy]

  Turn it into a '_CompressedFile' class which can transparently decompress any
  compressed file-like object granted there is the 'decompress(buffer)' function
  available.

* TODO: add another entry. [Artem Bityutskiy]

* Test_api_base: use stdout for progress bar. [Artem Bityutskiy]

  Because otherwise the output is visible when runnint nosetest without -s.

* TransRead: code re-arrangement. [Artem Bityutskiy]

  Move class Error a little bit up.

* TransRead: implement better fake seek method. [Artem Bityutskiy]

  Implement a generic '_add_fake_seek()' function which adds fake seek support to
  any file-like object.

  Also add support of URLs - open them using urllib2.

* Test_api_base: add an extra assertion. [Artem Bityutskiy]

* Tests: helpers: remove unnecessary truncation. [Artem Bityutskiy]

* Test_base_api: generate uncompressed files as well. [Artem Bityutskiy]

  Improve the '_generate_compressed_files()' and make it generate uncompressed
  vesion of the file as well.

* Test_api_base: rework the test to match the changed API. [Artem Bityutskiy]

  BmapCopy does not accept paths anymore - amend the tests.

* BmapCopy: drop the file opening functionality. [Artem Bityutskiy]

  The BmapCopy class is getting too large and specialized. Improve the situation
  by changing the API and removing the file opening functionality. Now it
  requires file-like objects all the time. The bmaptool, in turn, now opens the
  files itself.

* TransRead: implement the 'name' attribute. [Artem Bityutskiy]

  The standare attribute for the file name in file objects is 'name', not
  'fullpath' - rename it.

* BmapCopy: document that BmapCopy objects are one-time usable. [Artem Bityutskiy]

* TransRead: implement reading from file object. [Artem Bityutskiy]

  This patch changes the way we open the file: instead of opening by name, open
  it by its file object. This is not needed right now, but one of the next
  patches will implement reading from an URL, in which case we'll have to be able
  to read and decompress from a urlib file-object. In other words, this is a
  preparations.

  The good thing is that both tarfile and gzip modules allow to open by file
  objects. However, the bad news is that bzip2 module does not support this.
  This is why we implement the '_Bzip2Read' class which is a simple wrapper over
  bzip2's 'stream decompressor': we just read from the back-end file-like object,
  stream the data trhough the bzip2 decompressor, and provide to the caller.

* BmapCopy: add a /dev/null quirk. [Artem Bityutskiy]

  It is sometimes useful to copy to /dev/null, e.g., for benchmarking. Hoever,
  the /dev/null character device does not support 'fsync()', so bmaptool dies.

  Intorduce a quirk for this situation.

* TransRead: improve file size detection. [Artem Bityutskiy]

  In case of a tar archive, we know the file size for 'TarInfo'. Propagate it to
  the users via our 'size' attribute.

* TODO: add an entry about improving the progress bar. [Artem Bityutskiy]

* BmapCopy: make object one-time usable. [Artem Bityutskiy]

  Make the 'BmapCopy' objects usable only once, just like many other
  complex objects like Bzip2File.

  The reason for this is that it is too complex to make them re-usable,
  because this requires seeking image file and the destination file to the
  beginning, and not all files are easily seekable.

  In fact, some files are not seekable at all. So remove the unneeded
  complexity.

* TransRead: introduce a TransRead module. [Artem Bityutskiy]

  Separate out the transparent file reading functionality to a module.
  We'll add reading from an URL soon, so the module will become more complex.

* Test_api_base: include set_image_size testing. [Artem Bityutskiy]

  Improve test coverage by also testing the 'set_image_size()' interface of
  'BmapCopy'.

* Tests: helpers: change generate_test_files's interface a bit. [Artem Bityutskiy]

  Improve the API of the 'generate_test_files()' helper and teach it to return
  file size. This allow testing the 'BmapCopy' module a bit better in the next
  patch.

  Also propagate the size to the 'do_test()' method of the 'test_api_base' test.

* BmapCopy.py: allow users setting image size. [Artem Bityutskiy]

  The user sometimes knows the size of compressed image, so let him/her set it
  in order to enable the progress bar.

  This patch essentially changes an internal method to a pulic method.

* TODO: add another improvement idea. [Artem Bityutskiy]

* Bmaptool: disable pylint recommendation. [Artem Bityutskiy]

  Disable the 'too many statements' recommendation.

* Bmaptool: refuse copying without bmap by default. [Artem Bityutskiy]

  Allow copying without bmap only when the --nobmap. This way users will for
  sure notice when they copy without bmap.

* TODO: add few new ideas to the list. [Artem Bityutskiy]

* TODO: remove an entry about magic sequences. [Artem Bityutskiy]

  I've tried this, it is not really eassy to do. For example, for tar.bz2
  and .bz2 the magic sequence is the same. Lets' leave it as it is.

* README: master branch points to the latest release. [Artem Bityutskiy]

  Update the documentaion and tell that the master branch points to the latest
  release, not pre-release.

* Bmaptool: improve warning message. [Artem Bityutskiy]

  The tool tries to be generic and it is better to use word "copying" instead of
  "flashing".

* Test_api_base: use progress indicator sometimes. [Artem Bityutskiy]

  Increase test coverage by using the progress indicator or the BmapCopy class
  sometimes.

* BmapCopy: implement progress inicator. [Artem Bityutskiy]

  I got a feature request from users to implement a progress bar in order to
  show that the process is alive. This commit implements it.

  I add a possibility to configure the BmapCopy class to print the progress
  indicator to a user-defined file object with a user-defined pattern.

* Bmaptool: make warnings and errors more visible. [Artem Bityutskiy]

  People usually do not read docs and forget to use the --bmap option, and then
  wonder why flashing is not fast enough. bmaptool prints some kind of warning
  in this case, but it is not visible enough. Make it to be more visible:

  1. Change the message to say that flashing will be slow.
  2. Make the warning/error prefix to use capital letters.
  3. Make the output to be coloured.

  This should hopefully draw more attention and people will notice warnings
  and errors more easily.

* TODO: add an entry about progress indicator. [Artem Bityutskiy]

* Packaging: remove an internal URL. [Artem Bityutskiy]

* Release bmap-tools version 1.0. [Artem Bityutskiy]

* RELEASE_NOTES: turn into 1.0 notes. [Artem Bityutskiy]

  I am going to make release 1.0, and there are no differences between 1.0-rc7
  and 1.0, so let's turn rc7 release notes into 1.0 release notes.

* TODO: add an entry about a man page. [Artem Bityutskiy]

* Test_fiemap: silence a pylint recommendation. [Artem Bityutskiy]

* Spelling fixes. [Artem Bityutskiy]

  Fix a number of mis-spelled words in comments. No functional changes.

* TODO: remove an item about temporary files. [Artem Bityutskiy]

  Well, we just do nt have them, so this item is useless. We only have them in
  tests, and they get deleted on Ctrl-C because we use the NamedTemporaryFile
  python function which deletes the files on close.

* Pre-release 1.0-rc7. [Artem Bityutskiy]

* Plug RELEASE_NOTES to debian packages. [Artem Bityutskiy]

* Plug RELEASE notes to RPM packages. [Artem Bityutskiy]

* Limit nosetests coverage to the bmap-tools project. [Artem Bityutskiy]

  ... otherwise various libraries like 'bzip2' are included.

* README: add more information. [Artem Bityutskiy]

  Add information about branches, releases, versioning, author, and the credits.

* Amend comments: do not be confused about generators and iterators. [Artem Bityutskiy]

  Iterators and generators are not the same things. Generators is a more narrow
  concept. Generators are functions which yield elements.

  Fix up commentaries where I mixed these terms. Call all my functions with
  'yield' - generators. Also, prefer saying 'generator yields' to 'generators
  generates' just to be more clear about what I am trying to say.

  Fix a couple misspelled words and confusing sentences while on it.

  No functional changes.

* Add RELEASE_NOTES. [Artem Bityutskiy]

  Not wired to the packaging so far - it needs some more work.

* Add a small README file. [Artem Bityutskiy]

* Test_fiemap: implement a test for part of the file. [Artem Bityutskiy]

  Test no only the entire file, but also parts of the file.

* Fiemap: fix get_(un)mapped_ranges for file parts. [Artem Bityutskiy]

  The functions worked incorrectly when the ranges were requested for part of the
  file. Fix this.

* Test_fiemap: code re-structuring. [Artem Bityutskiy]

  This patch re-structures the _do_test() function of the 'test_fiemap' unit
  test. The re-structuring is needed because I am going to extend the test and
  verify the 'get_(un)mapped_ranges()' finctions fro parts of the file, not only
  for the entire file. Without the re-structuring there will be a lot of code
  duplication.

  So, this patch introduces a '_check_ranges()' helper function which verifies
  the 'get_(un)mapped_ranges()' function for a given range of blocks.

  Additinally, to make the code look uniform, this patch renames all the 'holes'
  list variables into 'unmapped', to match the existing 'mapped' list.

* Test_fiemap: test with different buffer sizes. [Artem Bityutskiy]

  Test the 'Fiemap' class with several different buffer sizes.

* Fiemap: amend things about the default buffer size. [Artem Bityutskiy]

  Introduce a constant for the default buffer size.
  Change the constructor interface - now None 'buf_size' means the default
  buffer size, which is a nicer interface.

* Test_fiemap: increase maximum file size to 16MiB. [Artem Bityutskiy]

  The default 4MiB are probably too few because the internal ext4 extent size
  seems to be 2MiB, so 4MiB are just 2 extents.

* Fiemap.py: implement new get_mapped_ranges. [Artem Bityutskiy]

  Use full power of the FIEMAP ioctl and call it for large areas of the file,
  instead of doing it block-after-block. This version is several times faster
  than the old version.

  The 'get_unmapped_ranges()' generator is build on top of 'get_mapped_ranges()'.

* Tests: helpers: mark create_random_sparse_file as local. [Artem Bityutskiy]

  Mark the 'create_random_sparse_file()' function as local by addin a leading
  '_'.

* Test_api_base: correct tar.bz2 files extension. [Artem Bityutskiy]

  This is just a copy-paste error - we gave .tar.bz2 files a '.tar.gz' extension.

* Tests: helpers: do not always write entire blocks. [Artem Bityutskiy]

  In 'create_random_sparse_file()', when we have decided to map a block, we
  always fill it entirely (write 4096 bytes). However, filling only part of this
  block from a random offset withing a block is more realistic.

* Tests: helpers: a small nicification. [Artem Bityutskiy]

  getrandbits(1) is a bit more clever than randint(0, 1). Also, remove useless
  bool().

* Tests: helpers: use less random data. [Artem Bityutskiy]

  We do not need really random data in the files we generate - this only slows
  the tests down a lot. Let's fill the files with semi-random data instead - just
  pick a random byte and fill large regions with this byt. This also make
  compression work faster, and it is good enough for our purposes.

  Besides, this allows to reproduce tests by setting a known seed, which does not
  work with os.urandom.

* Fiemap: fix internal buffer size calculations. [Artem Bityutskiy]

  ... I used 'buf_size' instead of 'self._buf_size' by a mistake.

* Fiemap: lower the default buffer size. [Artem Bityutskiy]

  The default 1MiB buffer is a bit too large, make it 256KiB.

* Fiemap: introduce a constant for minimum buffer size. [Artem Bityutskiy]

* Suppress few pylint recommendations. [Artem Bityutskiy]

* Tests: helpers: generate fully-mapped files as well. [Artem Bityutskiy]

  Improve tests coverage by generating fully-mapped files as well.

* Test_fiemap: add Fiemap module unit test. [Artem Bityutskiy]

* Tests: helpers: fix holes area for a 4097 bytes file. [Artem Bityutskiy]

  ... should be (0, 1), not (0, 0).

* Tests: helpers: teach generate_test_files to return mapped areas. [Artem Bityutskiy]

  This is a preparation to the Fiemap test. In the Fiemap module we have 2
  functions: get_mapped_ranges() and get_unmapped_ranges(). And to test both of
  them it is convenient to have 2 lists from the
  'tests.helpers.generate_test_files()' function: mapped list and unmapped list.

  Thus, teach 'tests.helpers.generate_test_files()' to also generate the list of
  mapped areas, not only the holes.

* Test_api_base: test .tar.gz and .tar.bz2 compression. [Artem Bityutskiy]

  This actually revealed a bug...

* BmapCopy: fix tar.gz compression support. [Artem Bityutskiy]

  This is a nasty bug - I used 'if' instead of 'elif' ... Thanks to
  'test_api_base' for revealing it.

* Tests: add a possibility to avoid tmp files deletion. [Artem Bityutskiy]

  This is needed for debugging purposes. When there are issues, it is very handy
  to be able to leave the temporary files and then investigate them. Do lets add
  a simple way to do this. In the future, this may become a test parameter.

* Tests: introduce a possibility to change the directory for tmp files. [Artem Bityutskiy]

  The default temporary directory is choosen by 'NamedTemporaryFile' and it is
  usually '/tmp'. However, for debugging purposes it is nice to sometimes change
  that to a different directory. In the future, this may be a test parameter.

* Tests: assign better names to temporary files. [Artem Bityutskiy]

  When creating temporary files, add prefixes and suffixes which make it easy to
  understand what is the file. This makes debugging a lot easier, although the
  code becomes a bit more complex.

* TODO: add an entry about compression types detection. [Artem Bityutskiy]

* Tests: helpers: move compress_test_file to test_api_base.py. [Artem Bityutskiy]

  The 'compress_test_file()' function is only used by 'test_api_base' and I am
  not planning any other tests which would need it. So let's move it to that
  file.

  While on this, also rename the function to '_generate_compressed_files()',
  which is more consistent with the other iterator we have:
  'generate_test_files()'.

* Test_api_base: make compare_holes local. [Artem Bityutskiy]

  The 'compare_holes()' function is only used in this test, so it is cleaner to
  add a leading '_' to the name to show that it is a local function.

* Test_api_base: also test compressed files. [Artem Bityutskiy]

* Tests: helpers: create a compression iterator. [Artem Bityutskiy]

  Create an iterator which compresses a file to different format. Not used
  so far.

* BmapCopy: fix image size validation. [Artem Bityutskiy]

  ... which did not work correctly because it should only be run for uncompressed
  images in __init__, as well as for any images when there is no bmap.

* Test_api_base: compare files using sha1. [Artem Bityutskiy]

  Instead of comparing files all the time using 'filecmp', calculate
  sha1 of the image once and compare it to the copies.

  This will be needed soon in order to implement compressed files testing - the
  'filecmp' module does not accept file-like objects, only file names, so you
  cannot feed it a compressed image.

* Test_api_base: move _do_test() out of the test class. [Artem Bityutskiy]

  It really does not need to be there. Let the class be just a minimum
  for nosetests to be happy.

* Tests: helpers: improve generate_test_files. [Artem Bityutskiy]

  Make 'generate_test_files()' generate more files - files consisting of a single
  hole with different sizes, and randomly generated sparse files of different
  sizes.

* Tests: move images generation to helpers.py. [Artem Bityutskiy]

  Introduce a common iterator in helpers.py which generates test images.
  The iterator will be used in the fiemap test as well. I will also add more
  interesting files to the iterator soon.

* Tests: rename test_helpers.py into helpers.py. [Artem Bityutskiy]

  ... in order to prevent nostests to try to run functions from this file.

* Test_api_base: run the test for more than one file. [Artem Bityutskiy]

  Instead of running the test of one file of 64MiB, run it 3 times for files of
  the following sizes:

  1. 8MiB
  2. 8MiB + 1 byte
  3. 8MiB - 1 byte

  This gives better coverage.

* Test_api_base: re-structure the test some more. [Artem Bityutskiy]

  Kill the 'setUp()' and 'tearDown()' methods and open/close the temporary files
  in '_do_test()' instead. This works better for me because I will call
  '_do_test()' many times and it is simpler when it starts with new temporary
  files every time, rather than teach it cleaning-up the old ones.

* BmapCopy: validate image size. [Artem Bityutskiy]

  Add some validation of image size - when we have the bmap, bmake sure that real
  image size is the same as image size from the bmap.

* BmapCopy: bugfix: handle unaligned files properly. [Artem Bityutskiy]

  When the image size is not aligned to the block size, we made an aligned copy
  anyway, which is wrong, because the copy has to have the same length as the
  image. This patch fixes the issue.

* TODO: add a reminder about testing compressed files. [Artem Bityutskiy]

* BmapCopy: simplify the code a bit. [Artem Bityutskiy]

  Stop returning 'length' in '_get_data()', because it is redundant and identical
  to 'end - start + 1'.

  Also add another assertion to improve robustness.

* Test_api_base: re-structure the test a bit. [Artem Bityutskiy]

  I want to run the test for various different files, not just for one file.
  Re-structure the test to allow this:

  1. Rename the old 'test' function to '_do_test()'
  2. Make the '_f_image' attribute to be an argument of '_do_test()'. So
     'self._f_image' is renamed to 'f_image'.
  3. Introduce a new 'test()' function which creates the file file to test
     and invokes '_do_test()'. Later this function will run '_do_test()' for
     more than one file.

* Test_helpers: generate file of correct length. [Artem Bityutskiy]

  The 'create_random_sparse_file()' alwasy generates files of the length aligned
  to block size, even when the requested size is unaligned. Fix this by adding a
  truncation at the end.

* Test_api_base: saner temprorary file creation. [Artem Bityutskiy]

  Instead of using the low-level mkstemp - use the NamedTemporaryFile function
  instead. It removes the temporary files on close.

* Tests: create a separate module for helper functions. [Artem Bityutskiy]

  I am going to add a test for the Fiemap module, and it will need the
  'create_random_sparse_file()' function from the base API test. Therefor, move
  this function to a separate 'test_helpers.py' module which will be shared
  across tests.

  Additionally, remove the holes verification from 'create_random_sparse_file()'
  - the test which I will add soon verifies holes separately.

  Also change the egging to exclude the tests.

* Fiemap: introduce a separate helper for invoking FIEMAP. [Artem Bityutskiy]

  Introduce a '_invoke_fiemap' helper function which hides all the cruft related
  to the FIEMAP ioctl invocation.

* Fiemap: introduce 'buf_size' parameter for __init__ [Artem Bityutskiy]

  We are going to use full power of FIEMAP. It requires an array where it will
  place the block map on output. Generally, big arrays are good because fiemap
  will be called less times, which is good for performance.

  Make the default to be a 1MiB buffer, and allocate it in the constructur
  for further use.

* Fiemap: more input arguments validation. [Artem Bityutskiy]

  Validate the input argument of 'block_is_mapped()'.

* Fiemap: validate the input arguments. [Artem Bityutskiy]

  Validate the input arguments for 'get_mapped_ranges()' and
  'get_unmapped_ranges()' - they should be positive and should not go beyond file
  size.

* Fiemap: fix error message. [Artem Bityutskiy]

  Fix a typo in one of the error messages: s/FIBMAP/FIEMAP/

* Fiemap: introduce constants. [Artem Bityutskiy]

  Introduce constants for various FIEMAP-related stuff like format strings for C
  structures, their sizes, and the ioctl number. First of all, this is just
  nicer. But more importantly, we'll soon introduce another function which will
  use these constants as well.

* BmapCopy.py: remove few useless initializations. [Artem Bityutskiy]

  We initialize these variables right after setting them to None, which is
  probably an overkill, remove the None assignment.

* BmapCopy: disable a couple of pylint recommendations. [Artem Bityutskiy]

* BmapCopy: use "_" prefix for private variables. [Artem Bityutskiy]

* Test_api_base: improve the test. [Artem Bityutskiy]

  Not only compare that the destination file has the same contens as the source
  file, but also make sure they have identical holes. This improves the test.

* Fiemap: improve the API. [Artem Bityutskiy]

  Improve the API and allow to specify the area of the file to generate ranges
  for, so that it would be possible to generate ranges only for part of the file.

* Test_api_base: fix the test. [Artem Bityutskiy]

  The test apparently was half-broken because:

  1. It did not check results of 'filecmp'.
  2. It did not seek the bmap file descriptor so the bmap comparison did not
     work.

* BmapCopy: bugfix: make destination file to be of the same size. [Artem Bityutskiy]

  When we copy to a regular file using bmap, and the image has holes at the end,
  the resulting copy does not contain these holes and its size is shorter.

  Fix this bug by truncating the destination file to the image size at the end.

* Test_api_base: add a Fiemap module check. [Artem Bityutskiy]

  This patch improves tesst coverage by checking the sparse file. Namely,
  when we create the random  sparse file, we remember where the holes are. Then
  we make sure that Fiemap reports absolutely the same holes.

* BmapCreate: separate out the FIEMAP functionality. [Artem Bityutskiy]

  Create a separate class for the FIEMAP ioctl API. I do this because
  I am going to use full power of FIEMAP and the code will become a lot
  more complex, so it is nicer to have it separate.

  Besides, we need a stand-alone FIEMAP API for testing.

* Bmap API: remove useless 'bmap' prefix. [Artem Bityutskiy]

  The 'BmapCopy' and 'BmapCreate' modules provide a set of useful attributes like
  block size, blocks count, mapped blocks count, etc. All these attributes start
  with a 'bmap_' prefix, which is useless and makes the code less readable.

  Remove the 'bmap_' prefix.

* BmapCreate: handle flush() exception. [Artem Bityutskiy]

  We handle file.flush() exceptions for the image, but not for bmap. This is
  inconsistent. Let's handle them for both.

* BmapCreate: simplify the exception class. [Artem Bityutskiy]

  Once we removed the FIBMAP support, we do not need the 'errno' attribute in the
  exception class - no one uses it. Let's kill it to have the code simpler and
  more clear, as well as less error-prone.

* BmapCreate.py: simplify the module by killing FIBMAP support. [Artem Bityutskiy]

  We do not need to support FIBMAP because FIEMAP is a lot better and does not
  require root privileges. FIEMAP is supported since 2008's kernel version
  2.6.28.

  Thus, kill the FIBMAP ioctl support and remove a lot of cruft.

* Pre-release version 0.6. [Artem Bityutskiy]

  Also change the date in the debian changelog for the 0.5 release - I forgot
  to update it.

* BmapCopy.py: fix a bug when copying without bmap. [Artem Bityutskiy]

  Fix a regression introduced in version 0.5: when copying without bmap the
  script fails with the following error:

  AttributeError: BmapCopy instance has no attribute '_f_bmap'

  This is because we never define this attribute when there is no bmap, but still
  use it. The fix is:

  1. Define all attributes in the __init__ constructor.
  2. Always check if _f_bmap is not None before using it.

  While on it, do a minor space clean-up.

* Tests: test_api_base: test copying without bmap as well. [Artem Bityutskiy]

  Improve the test a little by:
   1. Calling the 'copy' function with the first 'sync' argument being 'True' as
      well
   2. Adding another pass which tests file copying without bmap.

  This discovered a bug, actually, which will be fixed in the next commit.

* Pre-release version 0.5. [Artem Bityutskiy]

* Tests: add the base functionality test. [Artem Bityutskiy]

* BmapCreate: fix and silence pylint warnings. [Artem Bityutskiy]

  Fix several pylint warnings and silence a couple.

* BmapCopy.py: fix and silence pylint warnings. [Artem Bityutskiy]

  Fix a couple of pylint warnings and silence one.

* BmapCopy.py: flush the destination file on exit. [Artem Bityutskiy]

  Always flush the destination file on exit to make sure that if the user
  opens the same file by path - he/she sees all the data.

* BmapCopy.py: open the destination file for writing. [Artem Bityutskiy]

  Open the destination file in write-only mode, because we only write to
  this file, and never read from.

* Bmaptool: open the destination file in binary mode. [Artem Bityutskiy]

  This is just a small correction - the destination file is a binary file,
  so open it in binary mode.

* BmapCreate.py: support file-like objects. [Artem Bityutskiy]

  It is very useful give BmapCreate file-like objects instead of file paths, and
  this is exactly what this patch implements.

* BmapCreate.py: stop using logger for the bmap output. [Artem Bityutskiy]

  It is an overkill to use a logger object to output the bmap, and it is also
  rather difficult for the users. Instead, make 'BmapCreate' accept a file-like
  object for the output, not a logger object.

* BmapCopy.py: support file-like objects. [Artem Bityutskiy]

  It is very useful give BmapCopy file-like objects instead of file paths, and
  this is exactly what this patch implements.

* TODO: add an entry about interruptions. [Artem Bityutskiy]

* BmapCreate: remove useless seek. [Artem Bityutskiy]

  We do not need to seek the image to the beginning because we do not care
  about the file position - we do not read of write the file.

* BmapCopy.py: fix incorrect assignment. [Artem Bityutskiy]

  This patch fixes the following bug:

* BmapHelpers.py: introduce a 'get_block_size()' function. [Artem Bityutskiy]

  Move the piece of code which finds out block size from 'BmapCreate.py'
  to 'BmapHelpers.py' - we need this code in tests as well.

* BmapCopy.py: save and restore block device settings. [Artem Bityutskiy]

  We change block device settings to improve I/O speed (e.g., switch to the
  'noop' I/O scheduler). This patch also teaches the BmapCopy module to restore
  the settings when the copying is done.

* BmapCopy.py: make blkdev optimization work for partitions as wall. [Artem Bityutskiy]

  If we are writing to something like /dev/sdc1 instead of /dev/sdc, we should
  go one level up in the sysfs hierarchy to access the block device configuration
  files like 'scheduler'.

* Pre-release version 0.4. [Artem Bityutskiy]

* BmapCopy.py: write without bmap the same way as with bmap. [Artem Bityutskiy]

  Unify the code paths for the situations when we have bmap and when we do not
  have it.

* BmapCreate: generate more readable bmap. [Artem Bityutskiy]

  When the blocks rage consists of a single block (say 18282), write it
  in form of <>18282</> instead of less readable <>18282-18282</> form.
  'bmaptool copy' supports both.

* BmapCopy.py: fix another pylint complaint. [Artem Bityutskiy]

* BmapCreate.py: remove too long lines. [Artem Bityutskiy]

  Pylint complains a lot about long lines, which is fixed by this patch.

* BmapCopy.py: handle exceptions from the reader thread. [Artem Bityutskiy]

  Use the batch queue to pass exceptions from the reader thread to the main
  thread in case of errors, and raise the exceptions from the reader thread.

* BmapCopy: implement threaded reader. [Artem Bityutskiy]

  Read the data from a separate thread. This does not change the performance
  measurably in case of uncompressed images, but does improve writing speed in
  case of compressed images - Tizen.bz2 image flashing drops from 2m13s to
  1m43s.

* BmapCopy.py: implement an iterator for reading the image. [Artem Bityutskiy]

  Implement a '_get_batches()' iterator which reads batches of data from
  the image file.

* BmapCopy.py: introduce a helper iterator. [Artem Bityutskiy]

  The '_copy_data()' function is a bit ugly and large. Simplify it by introducing
  an iterator which splits the entire blocks range on smaller batch ranges, and
  we do actual I/O in these small batches.

* BmapCopy.py: move chunk_size to the class level. [Artem Bityutskiy]

  We use 'chunk_size' variable in several places and hard-code it to various
  values. Clean this up by introducing class-level variables for size of the
  I/O operations we do. Call them 'batch_blocks' and 'batch_bytes' for the
  I/O batch size in blocks and bytes.

* BmapCopy.py: introduce a iterator for blocks ranges. [Artem Bityutskiy]

  Add a 'get_block_ranges()' iterator function which parses the bmap
  file and returns block ranges. This makes the code a bit nicer and
  modular.

* Bmaptool: fix a print. [Artem Bityutskiy]

  We write to regular files too, not only to block devices, fix the
  message correspondingly.

* Fix a number of pylint warnings. [Artem Bityutskiy]

* Bmaptool: pre-release version 0.3. [Artem Bityutskiy]

* BmapCopy.py: synchronize periodically. [Artem Bityutskiy]

  Do not let the kernel cache too much data and run fsync() periodically. This
  should impreve the Ctrl-C handling and terminate the program faster. So this
  is mostly for the sake of user-friendliness, although it hurts write speed
  a little bit.

  Based on the idea of Patrick Ohly <patrick.ohly@intel.com>.

* BmapCopy: move a local variable to the class level. [Artem Bityutskiy]

  Move the 'blocks_written' local variable from the 'copy()' method to the
  class lever. We'll need it in one of the next patches in other methods to find
  out how much blocks has already been written.

* Bmaptool: remove stale attribute reference. [Artem Bityutskiy]

  We do not have the 'writer.target_is_block_device' attribute anymore, remove
  it.

* Add the TODO file to store the TODO list. [Artem Bityutskiy]

* Bmaptool: fix flashing speed calculation. [Artem Bityutskiy]

  We write 'mapped_size' amount of data, not the entire image, so use the correct
  variable when calculating the flashing speed.

* Debian packaging: add python 2.7 dependency. [Artem Bityutskiy]

* BmapCopy.py: fix exeptions handling in bdev optimization. [Artem Bityutskiy]

  The 'open()' function throws IOError exceptions, not OSError. Fix our
  exception handling.

* BmapCreate.py: remove junk white-space. [Artem Bityutskiy]

  We do not need a white-space after 'sha1' attribute.

* BmapCreate.py: fix a brown-paperbag bug. [Artem Bityutskiy]

  We did not seek the image file, so BmapCreate calculated SHA1 incorrectly.
  Fix this.

* Pre-release version 0.2. [Artem Bityutskiy]

* BmapCopy: renames to "copy" [Artem Bityutskiy]

  Rename the write() method to copy() because it matches the class name and the
  idea. Similarly, rename several variables and change 'write' to 'copy' in few
  comments.

* BmapCopy: amend comments. [Artem Bityutskiy]

  After all the rework - go through all the commentaries and docstrings and amend
  them to match the current state of art.

* BmapCopy: move block device tuning to BmapBdevCopy. [Artem Bityutskiy]

  This seems to be the final piece of code which has to be moved. Now
  BmapCopy is really independent of the destination file type.

* BmapCopy: move block device capacity check to BmapBdevCopy. [Artem Bityutskiy]

* BmapBdevCopy: move block device opening. [Artem Bityutskiy]

  Start moving the block device - specific stuff to the BmapBdevCopy class.
  Move the open funcion first.

* BmapCopy: rename 'bdev_path' to 'dest_path' [Artem Bityutskiy]

  Similarly to the previous commits - rename the path attribute to 'dest_path',
  because the destination does not have to be a block device.

* BmapCopy: rename 'f_bdev' to 'f_dest' [Artem Bityutskiy]

  Just like we did in bmaptools - our destination file may be anything,
  not only block device, so use 'f_dest' for the name.

* Bmaptool: distinguish between block devices and regular file. [Artem Bityutskiy]

  Teach bmaptool to distinguish between block devices and regular files and
  use the specialized version of 'BmapCopy' in case of block devices. The
  specialized version will be implemented in the 'BmapBdevCopy' class, which
  is just a copy of the base class so far.

* Bmaptool: rename the bdev argument to dest. [Artem Bityutskiy]

  Sinc the 'bmaptool copy' command is not only for block device, naming
  the destination file 'bdev' is a bad idea. Let's name it 'dest' instead,
  which stands for 'destination' and has the same length as 'bdev', so that
  renaming is simple.

* Rename BmapFlash to BmapCopy. [Artem Bityutskiy]

  Rename the module file name and the class name. There is a lot more to rename
  and this is just the first step.

* BmapCreate: amend comments. [Artem Bityutskiy]

  Just refresh the comments and change the identation style in docstrigs to
  something I like more nowadays.

* Rename bmap to bmaptool. [Artem Bityutskiy]

  The word 'bmap' is already reserved for the bmap file, it is bad idea to use
  it for the tool. Let's call the tool 'bmaptool' instead.

* BmapFlash: fix a bunch of pylint complaints. [Artem Bityutskiy]

* BmapCreate: fix function name. [Artem Bityutskiy]

  Function name was mis-spelled, fix it.

* Bmap: remove useless warning. [Artem Bityutskiy]

  No need to print a warning when copying to a regualr file, it makes little
  sense and useless.

* Bmap: rename flash to copy. [Artem Bityutskiy]

  Rename the 'flash' command to 'copy' command. Indeed, we just copy data from
  the image to a destination file, which may be a block device or something else.
  So let's use better naming.

* Bmap: amend comments. [Artem Bityutskiy]

  This patch changes commentaries and few messages we print.

  I have a lot of changes planned, and the biggest is that I want to rename
  the 'flash' command to 'copy' command. This commit is a preparation for
  this change.

* Bmap: correct Ctrl-C message. [Artem Bityutskiy]

  The long synching we warn the user about happens only for block devices
  and does not happen for regualr files. So warn only if we are writing to
  a block device. Also, correct the warning spelling a bit.

* BmapFlash: spelling fixes. [Artem Bityutskiy]

* BmapCreate: spelling fixes. [Artem Bityutskiy]

* Bmap: a couple of spelling fixes. [Artem Bityutskiy]

* Fix pylint warning. [Artem Bityutskiy]

  Too long line...

* Implement sub-commands support. [Artem Bityutskiy]

  Remove separate 'bmap-creator' and 'bmap-flasher' tools and instead, implement
  a single 'bmap' tool with 'create' and 'flash' subcommands.

* Rename API classes. [Artem Bityutskiy]

  Change API class names from BmapCreator/BmapFlasher to BmapCreate/BmapFlash.
  I plan to get rid of 'bmap-creator' and 'bmap-flasher' and instead, have
  a single 'bmap' tool with sub-commands: bmap create and bmap flash.

* Rename API modules. [Artem Bityutskiy]

  I am planning to switch to 'bmap [flash|create]' sub-commands, and this
  patch is a preparation which renames API modules to match the new scheme.

* Release version 0.1.1. [Artem Bityutskiy]

* Packaging: correct dependency. [Artem Bityutskiy]

  Although xml.etree is part of python, Fedora and OpenSuse provide this
  module in separate packages. Add the corresponding packaging requirements.

* Bmap-flasher: act on KeyboardInterrupt. [Artem Bityutskiy]

  When one pressess Ctrl-C, the program hands for several minutes and does
  not exit. The reason is that the kernel synchronized the block device on
  the last close.

  Let's at least print a message to the user and tell that there is no need
  to worry.

* Bmap-flasher: kill the --no-sync option. [Artem Bityutskiy]

  The kernel sychronizes block devices on close automatically (in case of
  the last reference becomes 0), so --no-sync does not work anyway.

* BmapFlasher: improve flashing speed. [Artem Bityutskiy]

  Improve flashing speed by switching to the 'noop' I/O scheduler for the block
  device we are flashing to. This gives ~20% write speed imporvement.

  Also limit the write buffering in order make the flashing - we do not need that
  and we better leave the memory for other applications.

* BmapFlasher: error out if the image does not fit the block device. [Artem Bityutskiy]

  I've got a bug report that the flasher tries to flash even if the block device
  is too small. Let's fix this.

* BmapFlasher: provide a target_is_block_device attribute. [Artem Bityutskiy]

  Which is useful for bmap-flasher, because it does not have find this out
  itslelf.

  Note, this is rather bad approach, and later I'll introduce a base class
  for flashing anywhere and a child class for flashing to block devices.

* BmapFlasher: check that the image file is a regular file. [Artem Bityutskiy]

* BmapFlasher: do not postpone size initialization for uncompressed images. [Artem Bityutskiy]

  When we are flashing images without bmap, we cannot initialize various
  size-related attributes until we flash the image if the image is compressed.
  However, we can do this for uncompressed images.

* BmapFlasher: separate sizes initialization to a function. [Artem Bityutskiy]

  We will need this function in the next patch, so this is just a preparation.

* BmapFlasher: open the block device in write-only mode. [Artem Bityutskiy]

  ... we do not need the read access.

* Bmap-flasher: fix a typo in the warning message. [Artem Bityutskiy]

* Bmap-flasher: change order of arguments. [Artem Bityutskiy]

  bmap-flasher <src> <dest> is more intuitive than bmap-flasher <dst> <src>.

* BmapHelpers: handle small sizes correctly. [Artem Bityutskiy]

  Make sure we provide sane human-readable size for small sizes like 1 byte or 10
  bytes. With this change, for sizes less than 512 we'll print X bytes, while for
  larger sized we'll print 0.YKiB.

* Bmap-creator: print a warning if no holes found. [Artem Bityutskiy]

  Probably this means that the image file was not handled correctly and holes
  were expanded.

* Flasher: rename 'total_size' [Artem Bityutskiy]

  There is inconsistenty between the flasher and creator - we use 'total_size' in
  flasher to describe the image size, while we use 'image_size' in the creator
  for the same. Let's use the same terminology everywhere, so kill 'total_size'
  and use 'image_size' everywhere.

* Teach Creator and Flasher modules to provide human sizes. [Artem Bityutskiy]

  Which we can use in the comman-line tools, which is quite handy.

* BmapCreator: implement FIEMAP support. [Artem Bityutskiy]

  It does not require root, unlike FIBMAP.

* BmapCreator: synchronize the image file before generating bmap. [Artem Bityutskiy]

  To make sure the block map is correct.

* Packaging: make myself to be the maintainer. [Artem Bityutskiy]

  I guess I am the package maintainer, not Ed, while I am happy to have
  Ed as the maintainer of the packaging stuff :-). However, the contents
  of the package is maintained by me.

* Add initial version of bmap-creator and BmapCreator. [Artem Bityutskiy]

* Introduce BmapHelpers.py. [Artem Bityutskiy]

  This module will contain shared helper functions.

* Repackaged pythonic way. [Ed Bartosh]

  As this package has been splitted to script and API it makes sense to
  utilize proper Python packaging( so called Python Egg) using setuptools
  functionality. This change does exactly that. All building and installation
  is done using setup.py.

  Debian and RPM packaging has been updated accordingly.

* Bmap-flasher: clean-up help text. [Artem Bityutskiy]

  argparse starts help text with a small letter and does not put the dot at the
  end (see -h and --version). Do the same for all the other options for
  consistency.

* Keep modules in bmaptools sub-directory. [Artem Bityutskiy]

* Bmap-flasher: imrove docs some more and have less duplication. [Artem Bityutskiy]

  Add some more documentation and use own docstring for 'bmap-flasher -h',
  instead of duplicating the text.

* BmapFlasher: improve the documentation some more. [Artem Bityutskiy]

* BmapFlasher: provide a list of supported image formats. [Artem Bityutskiy]

* BmapFlasher: move constant to the module level. [Artem Bityutskiy]

  The maximum supported bmap version is actually a module-level attribute, not a
  class-level attribute - move it to the module level.

* Bmap-flasher: improve documentation a little bit. [Artem Bityutskiy]

* BmapFlasher.py: remove undefined variable. [Artem Bityutskiy]

  Kill the left-over from old dayse when all the code was in 'bmap-flasher' and
  we had 'args' variable.

* Bmap-flasher: implement --version option. [Artem Bityutskiy]

* Bmap-flasher: print flashing speed. [Artem Bityutskiy]

* Bmap-flasher: move API to a separate module. [Artem Bityutskiy]

* Bmap-flasher: use logger instead of plain print. [Artem Bityutskiy]

  And implement the --quiet option at the same time.

  Also, kill the 'fatal()' helper.

* Bmap-flasher: add another TODO entry. [Artem Bityutskiy]

* Bmap-flasher: add a several TODO entries. [Artem Bityutskiy]

  Just in order to not forget to look at them.

* Bmap-flasher: print time in human-readable form. [Artem Bityutskiy]

* Bmap-flasher: improve errors handling. [Artem Bityutskiy]

  Print a nice error message when the the user by a mistake gives us a non-XML
  file instead of a proper bmap XML file.

* Packaged for deb and rpm distros. [Ed Bartosh]

  Debian packaging is in debian/ directory, rpm packaging and Makefile to
  use by otctools automatic testing system is in packaging/ directory.

* Initial version of bmap-flasher. [Artem Bityutskiy]

* Initial empty repository. [Eduard Bartosh]


