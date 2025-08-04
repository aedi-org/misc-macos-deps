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

from aedi.state import BuildState
from aedi.target import base


class AutoconfTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and share/autoconf/autom4te.cfg
    def __init__(self):
        super().__init__('autoconf')
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/autoconf/autoconf-2.72.tar.xz',
            'ba885c1319578d6c94d46e9b0dceb4014caafe2490e437a0dbca3f270a223f5a')


class AutomakeTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and share/automake-1.16/Automake/Config.pm
    def __init__(self):
        super().__init__('automake')
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/automake/automake-1.16.5.tar.xz',
            'f01d58cd6d9d77fbdca9eb4bbd5ead1988228fdb73d6f7a201f5f8d6b118b469')


class BisonTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('bison')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz',
            '9bba0214ccf7f1079c5d59210045227bcf619519840ebfa80cd3849cff5a5bf2')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('doc/bison.1')

    def configure(self, state: BuildState):
        state.options['--enable-relocatable'] = None
        super().configure(state)


class Bzip3Target(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('bzip3')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/kspalaiologos/bzip3/releases/download/1.5.1/bzip3-1.5.1.tar.xz',
            '53b844f9d9fb1d75faa4d3a9d9026017caaf50bb200b320d1685c6506b8f3b37')

    def configure(self, state: BuildState):
        state.options['CMAKE_SKIP_INSTALL_RPATH'] = 'YES'
        super().configure(state)

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        return '' if line.startswith('bindir=') else line


class FFmpegTarget(base.ConfigureMakeDependencyTarget):
    # TODO: fix absolute paths in bin/* and lib/*
    def __init__(self):
        super().__init__('ffmpeg')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz',
            '40973d44970dbc83ef302b0609f2e74982be2d85916dd2ee7472d30678a7abe6')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('doc/ffmpeg.txt')

    def configure(self, state: BuildState):
        state.options['--arch'] = state.architecture()
        super().configure(state)


class GraphvizTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('graphviz')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://gitlab.com/graphviz/graphviz/-/archive/8.1.0/graphviz-8.1.0.tar.bz2',
            'ce8911695752aa2c3929147e3dee016e58aa624d81d7c18dd16f895ae79460de')

    def configure(self, state: BuildState):
        opts = state.options
        opts['enable_ltdl'] = 'NO'
        opts['with_gvedit'] = 'NO'

        super().configure(state)


class LuaTarget(base.MakeTarget):
    def __init__(self):
        super().__init__('lua')

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
    def __init__(self):
        super().__init__('m4')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.xz',
            '63aede5c6d33b6d9b13511cd0be2cac046f2e70fd0a07aa9573a04a82783af96')


class P7ZipTarget(base.CMakeTarget):
    def __init__(self):
        super().__init__('p7zip')
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
    def __init__(self):
        super().__init__('pbzx')
        self.options = ('pbzx.c', '-lxar', '-llzma')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/nrosenstein-stuff/pbzx/archive/refs/tags/v1.0.2.tar.gz',
            '33db3cf9dc70ae704e1bbfba52c984f4c6dbfd0cc4449fa16408910e22b4fd90',
            'pbzx-xar-content')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('pbzx.c')


class Radare2Target(base.MesonStaticTarget):
    def __init__(self):
        super().__init__('radare2')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/radareorg/radare2/releases/download/6.0.0/radare2-6.0.0.tar.xz',
            '5aff30c3ee9578f40a5593d079a60897f90a05b98fca921a9e13202173afaaee')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('man/radare2.1')

    def configure(self, state: BuildState):
        state.set_build_datetime(2025, 7, 30, 2, 23, 6)

        option = state.options
        option['blob'] = 'true'
        option['enable_tests'] = 'false'
        option['enable_r2r'] = 'false'
        option['local'] = 'true'
        option['r2_gittip'] = 'a2bb4f058c410f9ef988f9ce13b37303b9d739e8'
        option['r2_version_commit'] = '33870'  # git rev-list --all --count
        option['static_runtime'] = 'true'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        bin_path = state.install_path / 'bin'
        os.unlink(bin_path / 'r2blob.static')
        os.rename(bin_path / 'r2blob', bin_path / 'radare2')


class RizinTarget(base.MesonTarget):
    def __init__(self):
        super().__init__('rizin')

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
    def __init__(self):
        super().__init__('7zip')
        self.src_root = 'CPP/7zip/Bundles/Alone2'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://7-zip.org/a/7z2500-src.tar.xz',
            'bff9e69b6ca73a5b8715d7623870a39dc90ad6ce1f4d1070685843987af1af9b')

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


class TimemoryTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('timemory')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/NERSC/timemory/archive/refs/tags/v3.2.3.tar.gz',
            'f85f17df6d60ff12745f742b34e7de15a6247123306d29809ba45e9c6fc5b67f')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_STATIC_LIBS'] = 'ON'
        opts['TIMEMORY_BUILD_FORTRAN'] = 'OFF'

        super().configure(state)


class UnrarTarget(base.MakeTarget):
    def __init__(self):
        super().__init__('unrar')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.rarlab.com/rar/unrarsrc-7.1.8.tar.gz',
            '9ec7765a948140758af12ed29e3e47db425df79a9c5cbb71b28769b256a7a014')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('rar.hpp')

    def post_build(self, state: BuildState):
        self.copy_to_bin(state)


class XdeltaTarget(base.ConfigureMakeDependencyTarget):
    # Depends on autoconf, automake, and (optionally) xz
    def __init__(self):
        super().__init__('xdelta')
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
    def __init__(self):
        super().__init__('xz')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/tukaani-project/xz/releases/download/v5.8.1/xz-5.8.1.tar.gz',
            '507825b599356c10dca1cd720c9d0d0c9d5400b9de300af00e4d1ea150795543')

    def configure(self, state: BuildState):
        state.options['BUILD_TESTING'] = 'NO'
        super().configure(state)


class ZipTarget(base.SingleExeCTarget):
    def __init__(self):
        super().__init__('zip')
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
