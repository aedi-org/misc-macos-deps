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

import glob
import os
import shutil
from pathlib import Path

import aedi.target.base as base
from aedi.state import BuildState


class BrotliTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='brotli'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/google/brotli/archive/refs/tags/v1.0.9.tar.gz',
            'f9e8d81d0405ba66d181529af42a3354f838c939095ff99930da6aa9cdf6fe46')

    def post_build(self, state: BuildState):
        super().post_build(state)

        dylib_pattern = str(state.install_path / 'lib/*.dylib')
        for dylib in glob.iglob(dylib_pattern):
            os.unlink(dylib)

        archive_suffix = '-static.a'
        archive_pattern = str(state.install_path / f'lib/*{archive_suffix}')
        for archive in glob.iglob(archive_pattern):
            no_suffix_name = archive.replace(archive_suffix, '.a')
            os.rename(archive, no_suffix_name)

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return line.replace('-R${libdir} ', '') if line.startswith('Libs:') else line


class Bzip2Target(base.CMakeStaticDependencyTarget):
    def __init__(self, name='bzip2'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz',
            'ab5a03176ee106d3f0fa90e381da478ddae405918153cca248e682cd0c4a2269',
            patches='bzip2-add-cmake')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('bzlib.h')

    def configure(self, state: BuildState):
        opts = state.options
        opts['ENABLE_APP'] = 'NO'
        opts['ENABLE_SHARED_LIB'] = 'NO'
        opts['ENABLE_STATIC_LIB'] = 'YES'
        opts['ENABLE_TESTS'] = 'NO'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        lib_path = state.install_path / 'lib'
        os.rename(lib_path / 'libbz2_static.a', lib_path / 'libbz2.a')

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return '' if line.startswith('bindir=') else line


class ExpatTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='expat'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libexpat/libexpat/releases/download/R_2_4_1/expat-2.4.1.tar.xz',
            'cf032d0dba9b928636548e32b327a2d66b1aab63c4f4a13dd132c2d1d2f2fb6a')

    def configure(self, state: BuildState):
        opts = state.options
        opts['EXPAT_BUILD_EXAMPLES'] = 'NO'
        opts['EXPAT_BUILD_TESTS'] = 'NO'
        opts['EXPAT_BUILD_TOOLS'] = 'NO'

        super().configure(state)


class FfiTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='ffi'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libffi/libffi/releases/download/v3.4.6/libffi-3.4.6.tar.gz',
            'b0dea9df23c863a7a50e825440f3ebffabd65df1497108e5d437747843895a4e')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libffi.pc.in')

    def post_build(self, state: BuildState):
        super().post_build(state)

        for header in ('ffi.h', 'ffitarget.h'):
            self.make_platform_header(state, header)


class FreeImageTarget(base.MakeTarget):
    def __init__(self, name='freeimage'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/freeimage/Source%20Distribution/3.18.0/FreeImage3180.zip',
            'f41379682f9ada94ea7b34fe86bf9ee00935a3147be41b6569c9605a53e438fd',
            patches='freeimage-fix-arm64')

    HEADER_FILE = 'Source/FreeImage.h'

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file(self.HEADER_FILE)

    def configure(self, state: BuildState):
        super().configure(state)

        # These flags are copied from Makefile.gnu
        common_flags = ' -O3 -fPIC -fexceptions -fvisibility=hidden'

        env = state.environment
        env['CFLAGS'] += common_flags + ' -std=gnu89 -Wno-implicit-function-declaration'
        env['CXXFLAGS'] += common_flags + ' -Wno-ctor-dtor-privacy'

        for option in ('-f', 'Makefile.gnu', 'libfreeimage.a'):
            state.options[option] = None

    def post_build(self, state: BuildState):
        include_path = state.install_path / 'include'
        os.makedirs(include_path, exist_ok=True)
        shutil.copy(state.build_path / self.HEADER_FILE, include_path)

        lib_path = state.install_path / 'lib'
        os.makedirs(lib_path, exist_ok=True)
        shutil.copy(state.build_path / 'libfreeimage.a', lib_path)

        self.write_pc_file(state, version='3.18.0', libs='-lfreeimage -lc++')


class GettextTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='gettext'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/gettext/gettext-0.21.tar.xz',
            'd20fcbb537e02dcf1383197ba05bd0734ef7bf5db06bdb241eb69b7d16b73192')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('gettext-runtime')

    def configure(self, state: BuildState):
        opts = state.options
        opts['--enable-csharp'] = 'no'
        opts['--enable-java'] = 'no'
        opts['--enable-libasprintf'] = 'no'

        super().configure(state)


class HighwayTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='highway'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/google/highway/archive/refs/tags/1.0.6.tar.gz',
            'd89664a045a41d822146e787bceeefbf648cc228ce354f347b18f2b419e57207')

    def configure(self, state: BuildState):
        opts = state.options
        opts['HWY_ENABLE_CONTRIB'] = 'NO'
        opts['HWY_ENABLE_EXAMPLES'] = 'NO'
        opts['HWY_ENABLE_TESTS'] = 'NO'

        super().configure(state)


class IconvTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='iconv'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.gnu.org/gnu/libiconv/libiconv-1.17.tar.gz',
            '8f74213b56238c85a50a5329f77e06198771e70dd9a739779f4c02f65d971313')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('include/iconv.h.in')

    def configure(self, state: BuildState):
        state.options['--enable-extra-encodings'] = 'yes'
        super().configure(state)


class IntlTarget(GettextTarget):
    def __init__(self, name='intl'):
        super().__init__(name)

    def configure(self, state: BuildState):
        state.options['--localedir'] = '/usr/local/share/locale'

        # There is no way to configure intl only, do this for the runtime
        self.src_root = 'gettext-runtime'
        super().configure(state)

    def build(self, state: BuildState):
        # Build intl only, avoid complete gettext runtime
        self.src_root += '/intl'
        super().build(state)

    def post_build(self, state: BuildState):
        opts = state.options
        opts['install-exec-am'] = None
        opts['install-nodist_includeHEADERS'] = None

        # Install intl only, avoid complete gettext runtime
        state.build_path /= self.src_root
        self.install(state, state.options)


class JpegTurboTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='jpeg-turbo'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/3.1.0/libjpeg-turbo-3.1.0.tar.gz',
            '9564c72b1dfd1d6fe6274c5f95a8d989b59854575d4bbee44ade7bc17aa9bc93')

    def configure(self, state: BuildState):
        state.options['ENABLE_SHARED'] = 'NO'
        super().configure(state)


class TiffTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='tiff'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://download.osgeo.org/libtiff/tiff-4.3.0.tar.gz',
            '0e46e5acb087ce7d1ac53cf4f56a09b221537fc86dfc5daaad1c2e89e1b37ac8',
            patches='tiff-remove-useless')

    def configure(self, state: BuildState):
        opts = state.options
        opts['cxx'] = 'NO'
        opts['lzma'] = 'YES'

        super().configure(state)

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        version = 'Version:'
        cflags = 'Cflags:'
        libs = 'Libs:'

        if line.startswith(version):
            return version + ' 4.3.0\n'
        elif line.startswith(cflags):
            return cflags + ' -I${includedir}\nRequires.private: libjpeg liblzma libwebp libzstd zlib\n'
        elif line.startswith(libs):
            return libs + ' -L${libdir} -ltiff\n'

        return line


class WxWidgetsTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='wxwidgets'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.5/wxWidgets-3.1.5.tar.bz2',
            'd7b3666de33aa5c10ea41bb9405c40326e1aeb74ee725bb88f90f1d50270a224',
            patches='wxwidgets-library-suffix')

    def configure(self, state: BuildState):
        opts = state.options
        opts['wxBUILD_SHARED'] = 'NO'
        opts['wxUSE_LIBLZMA'] = 'YES'
        opts['wxUSE_LIBSDL'] = 'NO'
        opts['wxUSE_LIBJPEG'] = 'sys'
        opts['wxUSE_LIBPNG'] = 'sys'
        opts['wxUSE_LIBTIFF'] = 'sys'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        # Replace prefix in setup.h
        def patch_setup_h(line: str):
            prefix = '#define wxINSTALL_PREFIX '
            return f'{prefix}"/usr/local"\n' if line.startswith(prefix) else line

        setup_h_path = state.install_path / 'lib/wx/include/osx_cocoa-unicode-static-3.1/wx/setup.h'
        self.update_text_file(setup_h_path, patch_setup_h)

        # Fix a few wx-config entries
        def patch_wx_config(line: str):
            prefix = 'prefix=${input_option_prefix-${this_prefix:-'
            is_cross_func = 'is_cross() '
            is_cross_test = 'is_cross && target='
            output_option_cc = '[ -z "$output_option_cc" '
            output_option_cxx = '[ -z "$output_option_cxx" '
            output_option_ld = '[ -z "$output_option_ld" '
            ldlibs_gl = 'ldlibs_gl='

            if line.startswith(prefix):
                return prefix + '$(cd "${0%/*}/.."; pwd)}}\n'
            elif line.startswith(is_cross_func):
                return is_cross_func + '{ false; }\n'
            elif line.startswith(is_cross_test):
                return is_cross_test + '""\n'
            elif line.startswith(output_option_cc):
                return output_option_cc + '] || echo "gcc"\n'
            elif line.startswith(output_option_cxx):
                return output_option_cxx + '] || echo "g++"\n'
            elif line.startswith(output_option_ld):
                return output_option_ld + '] || echo "g++ -o"\n'
            elif line.startswith(ldlibs_gl):
                return ldlibs_gl + '"-lwx_baseu-3.1 -lwx_osx_cocoau_core-3.1 -framework OpenGL"\n'

            return line

        wx_config_path = state.install_path / 'bin/wx-config'
        self.update_text_file(wx_config_path, patch_wx_config)
