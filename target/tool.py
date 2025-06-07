#
#    Module to build miscellaneous libraries and tools for macOS
#    Copyright (C) 2020-2025 Alexey Lysiuk
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import subprocess
from pathlib import Path

import aedi.target.base as base
from aedi.state import BuildState


class AutoconfTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and share/autoconf/autom4te.cfg
    def __init__(self, name='autoconf'):
        super().__init__(name)
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/autoconf/autoconf-2.72.tar.xz',
            'ba885c1319578d6c94d46e9b0dceb4014caafe2490e437a0dbca3f270a223f5a')


class AutomakeTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and share/automake-1.16/Automake/Config.pm
    def __init__(self, name='automake'):
        super().__init__(name)
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/automake/automake-1.16.5.tar.xz',
            'f01d58cd6d9d77fbdca9eb4bbd5ead1988228fdb73d6f7a201f5f8d6b118b469')


class Bzip3Target(base.CMakeStaticDependencyTarget):
    def __init__(self, name='bzip3'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/kspalaiologos/bzip3/releases/download/1.5.1/bzip3-1.5.1.tar.xz',
            '53b844f9d9fb1d75faa4d3a9d9026017caaf50bb200b320d1685c6506b8f3b37')

    def configure(self, state: BuildState):
        state.options['CMAKE_SKIP_INSTALL_RPATH'] = 'YES'
        super().configure(state)

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return '' if line.startswith('bindir=') else line


class FFmpegTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and lib/*
    def __init__(self, name='ffmpeg'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz',
            '40973d44970dbc83ef302b0609f2e74982be2d85916dd2ee7472d30678a7abe6')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('doc/ffmpeg.txt')

    def configure(self, state: BuildState):
        state.options['--arch'] = state.architecture()
        super().configure(state)


class LuaTarget(base.MakeTarget):
    def __init__(self, name='lua'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.lua.org/ftp/lua-5.4.8.tar.gz',
            '4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('src/lua.h')

    def post_build(self, state: BuildState):
        opts = state.options
        opts['install'] = None
        opts['INSTALL_TOP'] = state.install_path

        self.install(state, state.options)


class M4Target(base.ConfigureMakeDependencyTarget):
    def __init__(self, name='m4'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.xz',
            '63aede5c6d33b6d9b13511cd0be2cac046f2e70fd0a07aa9573a04a82783af96')


class P7ZipTarget(base.CMakeTarget):
    def __init__(self, name='p7zip'):
        super().__init__(name)
        self.src_root = 'CPP/7zip/CMAKE/7za'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/p7zip-project/p7zip/archive/refs/tags/v17.04.tar.gz',
            'ea029a2e21d2d6ad0a156f6679bd66836204aa78148a4c5e498fe682e77127ef')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('CPP/7zip/CMAKE/CMakeLists.txt') \
            and state.has_source_file('C/fast-lzma2/fast-lzma2.h')

    def post_build(self, state: BuildState):
        self.copy_to_bin(state, '7za')


class PbzxTarget(base.SingleExeCTarget):
    def __init__(self, name='pbzx'):
        super().__init__(name)
        self.options = ('pbzx.c', '-lxar', '-llzma')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/nrosenstein-stuff/pbzx/archive/refs/tags/v1.0.2.tar.gz',
            '33db3cf9dc70ae704e1bbfba52c984f4c6dbfd0cc4449fa16408910e22b4fd90',
            'pbzx-xar-content')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('pbzx.c')


class Radare2Target(base.MesonTarget):
    def __init__(self, name='radare2'):
        super().__init__(name)
        self.configure_prefix = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/radareorg/radare2/releases/download/5.9.8/radare2-5.9.8.tar.xz',
            'de061db6089cc1321ba9062b8aa9a0adaaa7a4d25128aab37a2a44e71a939829')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('man/radare2.1')

    def configure(self, state: BuildState):
        option = state.options
        option['blob'] = 'true'
        option['enable_tests'] = 'false'
        option['enable_r2r'] = 'false'
        option['local'] = 'true'
        option['r2_gittip'] = 'ea7f0356519884715cf1d5fba16042bac72b2df5'
        option['r2_version_commit'] = '1'
        option['static_runtime'] = 'true'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        bin_path = state.install_path / 'bin'
        os.unlink(bin_path / 'r2blob.static')
        os.rename(bin_path / 'r2blob', bin_path / 'radare2')


class RizinTarget(base.MesonTarget):
    def __init__(self, name='rizin'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/rizinorg/rizin/releases/download/v0.8.1/rizin-src-v0.8.1.tar.xz',
            'ef2b1e6525d7dc36ac43525b956749c1cca07bf17c1fed8b66402d82010a4ec2')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('binrz/man/rizin.1')

    def configure(self, state: BuildState):
        option = state.options
        option['blob'] = 'true'
        option['enable_tests'] = 'false'
        option['enable_rz_test'] = 'false'
        option['local'] = 'enabled'
        option['portable'] = 'true'

        super().configure(state)


class SevenZipTarget(base.MakeTarget):
    def __init__(self, name='7zip'):
        super().__init__(name)
        self.src_root = 'CPP/7zip/Bundles/Alone2'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://7-zip.org/a/7z2409-src.tar.xz',
            '49c05169f49572c1128453579af1632a952409ced028259381dac30726b6133a')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('CPP/7zip/cmpl_mac_arm64.mak')

    def build(self, state: BuildState):
        environment = state.environment
        mak_suffix = self._arch_suffix(state)

        opts = state.options
        opts['-f'] = None
        opts[f'../../cmpl_mac_{mak_suffix}.mak'] = None
        opts['CFLAGS_BASE_LIST'] = environment['CFLAGS'] + ' -Wno-switch-default -c'
        opts['LDFLAGS_STATIC_2'] = environment['LDFLAGS']

        super().build(state)

    def post_build(self, state: BuildState):
        build_suffix = self._arch_suffix(state)
        self.copy_to_bin(state, f'{self.src_root}/b/m_{build_suffix}/7zz', '7zz')

    @staticmethod
    def _arch_suffix(state: BuildState):
        arch = state.architecture()
        return 'x64' if arch == 'x86_64' else arch


class UnrarTarget(base.MakeTarget):
    def __init__(self, name='unrar'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.rarlab.com/rar/unrarsrc-6.2.12.tar.gz',
            'a008b5f949bca9bb4ffa1bebbfc8b3c14b89df10a10354809b845232d5f582e5')

    def configure(self, state: BuildState):
        # Value of CXXFLAGS variable from makefile with '-std=c++11' command line argument added
        state.options['CXXFLAGS'] = '-std=c++11 -O2 -Wno-logical-op-parentheses -Wno-switch -Wno-dangling-else'

        super().configure(state)

    def post_build(self, state: BuildState):
        self.copy_to_bin(state)

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('rar.hpp')


class XdeltaTarget(base.ConfigureMakeDependencyTarget):
    # Depends on autoconf, automake, and (optionally) xz
    def __init__(self, name='xdelta'):
        super().__init__(name)
        self.src_root = 'xdelta3'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/jmacd/xdelta/archive/refs/tags/v3.1.0.tar.gz',
            '7515cf5378fca287a57f4e2fee1094aabc79569cfe60d91e06021a8fd7bae29d')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('xdelta3/xdelta3.h')

    def configure(self, state: BuildState):
        # Invoke MakeTarget.configure() explicitly to create symlinks needed for autoconf
        base.MakeTarget.configure(self, state)

        # Generate configure script with autoconf
        work_path = state.build_path / self.src_root
        subprocess.run(('autoreconf', '--install'), check=True, cwd=work_path, env=state.environment)

        # Run generated configure script
        super().configure(state)


class XzTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='xz'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/tukaani-project/xz/releases/download/v5.6.3/xz-5.6.3.tar.xz',
            'db0590629b6f0fa36e74aea5f9731dc6f8df068ce7b7bafa45301832a5eebc3a')

    def configure(self, state: BuildState):
        options = state.options
        options['BUILD_TESTING'] += 'NO'
        # Dependencies of libintl are not pulled automatically
        options['CMAKE_EXE_LINKER_FLAGS'] += '-framework CoreFoundation -liconv'

        super().configure(state)


class ZipTarget(base.SingleExeCTarget):
    def __init__(self, name='zip'):
        super().__init__(name)
        self.options = (
            '-I.', '-DUNIX', '-DBZIP2_SUPPORT', '-DLARGE_FILE_SUPPORT', '-DUNICODE_SUPPORT',
            '-DHAVE_DIRENT_H', '-DHAVE_TERMIOS_H', '-lbz2',
            'crc32.c', 'crypt.c', 'deflate.c', 'fileio.c', 'globals.c', 'trees.c',
            'ttyio.c', 'unix/unix.c', 'util.c', 'zip.c', 'zipfile.c', 'zipup.c',
        )

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/infozip/Zip%203.x%20%28latest%29/3.0/zip30.tar.gz',
            'f0e8bb1f9b7eb0b01285495a2699df3a4b766784c1765a8f1aeedf63c0806369',
            patches='zip-fix-misc')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('zip.h')
