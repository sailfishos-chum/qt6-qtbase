%global qt_version 6.8.3

# Disable automatic .la file removal
%global __brp_remove_la_files %nil
%global rpm_macros_dir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_qt6_sysconfdir}/rpm; echo $d)

# Do not check any files in %%{_qt6_plugindir}/platformthemes/ for requires.
# Those themes are there for platform integration. If the required libraries are
# not there, the platform to integrate with isn't either. Then Qt will just
# silently ignore the plugin that fails to load. Thus, there is no need to let
# RPM drag in gtk3 as a dependency for the GTK+3 dialog support.
%global __requires_exclude_from ^%{_qt6_plugindir}/platformthemes/.*$
# filter plugin provides
%global __provides_exclude_from ^%{_qt6_plugindir}/.*\\.so$


%bcond_with vulkan

Name:    qt6-qtbase
Summary: Qt6 - QtBase components
Version: 6.8.3
Release: 0%{?dist}

License: LGPL-3.0-only OR GPL-3.0-only WITH Qt-GPL-exception-1.0
Url:     http://qt-project.org/
Source0: %{name}-%{version}.tar.bz2
Source1: qtlogging.ini
# macros
Source10: macros.qt6-qtbase

Patch1:  qtbase-CMake-Install-objects-files-into-ARCHDATADIR.patch
Patch2:  qtbase-use-only-major-minor-for-private-api-tag.patch

Patch10: 0010-disable-arm32-pixman-simd.patch

# namespace QT_VERSION_CHECK to workaround major/minor being pre-defined (#1396755)
Patch50: qtbase-version-check.patch

# drop -O3 and make -O2 by default
Patch54: qtbase-cxxflag.patch

# upstream patches
Patch100: CVE-2025-3512-qtbase-6.8.patch
Patch101: CVE-2025-4211-qtbase-6.8.patch
Patch102: CVE-2025-5455-qtbase-6.8.patch


BuildRequires: cmake
BuildRequires: ninja
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: findutils
BuildRequires: libjpeg-devel
BuildRequires: libmng-devel
BuildRequires: libtiff-devel
BuildRequires: pkgconfig(libzstd)
BuildRequires: pkgconfig(mtdev)
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(dbus-1)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(fontconfig)
#BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(glib-2.0)
#BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(libproxy-1.0)
BuildRequires: pkgconfig(libsctp)
## xcb-sm
#BuildRequires: pkgconfig(ice) pkgconfig(sm)
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(libudev)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(libpulse) pkgconfig(libpulse-mainloop-glib)

BuildRequires: pkgconfig(xkbcommon)

%if %{with vulkan}
BuildRequires: vulkan-headers
%endif

BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(gbm)
BuildRequires: pkgconfig(glesv2)
BuildRequires: wayland-devel
BuildRequires: pkgconfig(sqlite3) >= 3.7
BuildRequires: pkgconfig(harfbuzz) >= 0.9.42
BuildRequires: pkgconfig(icu-i18n)
BuildRequires: pkgconfig(libpcre2-16) >= 10.20

#BuildRequires: pkgconfig(xcb-xkb)
#BuildRequires: pkgconfig(xcb) pkgconfig(xcb-glx) pkgconfig(xcb-icccm) pkgconfig(xcb-image) pkgconfig(xcb-keysyms) pkgconfig(xcb-renderutil) pkgconfig(xcb-cursor)
BuildRequires: pkgconfig(zlib)
BuildRequires: perl
#BuildRequires: perl-generators
BuildRequires: python3-base
BuildRequires: qt6-rpm-macros

BuildRequires: pkgconfig(libsystemd)


Requires: %{name}-common = %{version}-%{release}


%description
Qt is a software toolkit for developing applications.

This package contains base tools, like string, xml, and network
handling.

%package common
Summary: Common files for Qt6
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
%description common
%{summary}.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-gui%{?_isa}
Requires: libEGL-devel
Requires: pkgconfig(glesv2)
Requires: pkgconfig(xkbcommon)
Requires: qt6-rpm-macros
Requires: clang >= 3.7.0
%description devel
%{summary}.

%package private-devel
Summary: Development files for %{name} private APIs
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description private-devel
%{summary}.

%package static
Summary: Static library files for %{name}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
Requires: pkgconfig(fontconfig)
Requires: pkgconfig(glib-2.0)
Requires: pkgconfig(xkbcommon)
Requires: pkgconfig(zlib)

%description static
%{summary}.

# debating whether to do 1 subpkg per library or not -- rex
%package gui
Summary: Qt6 GUI-related libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Recommends: mesa-dri-drivers%{?_isa}
Recommends: qt6-qtwayland%{?_isa}
Recommends: qt6-qttranslations
%description gui
Qt6 libraries used for drawing widgets and OpenGL items.


%prep
%autosetup -n %{name}-%{version}/upstream -p1

# move some bundled libs to ensure they're not accidentally used
pushd src/3rdparty
mkdir UNUSED
mv harfbuzz-ng freetype libjpeg libpng sqlite zlib UNUSED/
popd

%build

touch .git

%cmake_qt6 \
 -DQT_FEATURE_accessibility=ON \
 -DQT_FEATURE_fontconfig=ON \
 -DQT_FEATURE_glib=ON \
 \
 -DQT_FEATURE_icu=ON \
 -DQT_FEATURE_enable_new_dtags=ON \
  \
 -DQT_FEATURE_journald=ON \
 -DQT_FEATURE_openssl_linked=ON \
 -DQT_FEATURE_openssl_hash=OFF \
 -DQT_FEATURE_libproxy=ON \
 -DQT_FEATURE_sctp=ON \
 -DQT_FEATURE_separate_debug_info=OFF \
 -DQT_FEATURE_reduce_relocations=OFF \
 -DQT_FEATURE_relocatable=OFF \
 -DQT_FEATURE_system_jpeg=ON \
 -DQT_FEATURE_system_png=ON \
 -DQT_FEATURE_system_zlib=ON \
 -DFEATURE_sql_ibase=OFF \
 -DFEATURE_sql_odbc=OFF \
 -DFEATURE_sql_mysql=OFF \
 -DFEATURE_sql_psql=OFF \
 -DQT_FEATURE_sql_sqlite=ON \
 -DQT_FEATURE_rpath=OFF \
 -DQT_FEATURE_zstd=ON \
 -DQT_FEATURE_elf_private_full_version=ON \
 -DQT_FEATURE_dbus_linked=ON \
 -DQT_FEATURE_system_pcre2=ON \
 -DQT_FEATURE_system_sqlite=ON \
 -DQT_FEATURE_cursor=OFF \
 -DBUILD_SHARED_LIBS=ON \
 -DQT_BUILD_EXAMPLES=OFF \
 -DQT_INSTALL_EXAMPLES_SOURCES=OFF \
 -DQT_BUILD_TESTS=OFF \
 -DQT_QMAKE_TARGET_MKSPEC=%{_qt6_platform} \
 -DQT_AVOID_CMAKE_ARCHIVING_API=ON \
 -DQT_FEATURE_forkfd_pidfd=OFF \
 -DQT_FEATURE_wayland=ON \
 -DQT_FEATURE_egl_x11=OFF \
 -DQT_FEATURE_eglfs_x11=OFF \
 -DQT_FEATURE_forkfd_pidfd=OFF \
%if %{with vulkan}
 -DQT_FEATURE_vulkan=ON \
%endif
 %{nil}

%cmake_build


%install
%cmake_install

mkdir -p %{buildroot}%{_qt6_datadir}
install -m644 -p -D %{SOURCE1} %{buildroot}%{_qt6_datadir}/qtlogging.ini

# rpm macros
install -p -m644 -D %{SOURCE10} \
  %{buildroot}%{rpm_macros_dir}/macros.qt6-qtbase
sed -i \
  -e "s|@@NAME@@|%{name}|g" \
  -e "s|@@EPOCH@@|%{?epoch}%{!?epoch:0}|g" \
  -e "s|@@VERSION@@|%{version}|g" \
  -e "s|@@EVR@@|%{?epoch:%{epoch:}}%{version}-%{release}|g" \
  %{buildroot}%{rpm_macros_dir}/macros.qt6-qtbase

# create/own dirs
mkdir -p %{buildroot}{%{_qt6_archdatadir}/mkspecs/modules,%{_qt6_importdir},%{_qt6_libexecdir},%{_qt6_plugindir}/{designer,iconengines,script,styles},%{_qt6_translationdir}}
mkdir -p %{buildroot}%{_sysconfdir}/xdg/QtProject

# hardlink files to {_bindir}, add -qt6 postfix to not conflict
mkdir %{buildroot}%{_bindir}
pushd %{buildroot}%{_qt6_bindir}
for i in * ; do
  case "${i}" in
    qdbuscpp2xml|qdbusxml2cpp|qtpaths)
      ln -v  ${i} %{buildroot}%{_bindir}/${i}-qt6
      ;;
    *)
      ln -v  ${i} %{buildroot}%{_bindir}/${i}
      ;;
  esac
done
popd

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt6_libdir}
for prl_file in libQt6*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

# install privat headers for qtxcb
mkdir -p %{buildroot}%{_qt6_headerdir}/QtXcb
install -m 644 src/plugins/platforms/xcb/*.h %{buildroot}%{_qt6_headerdir}/QtXcb/

# Copied from OpenSUSE packages

# These files are only useful for the Qt continuous integration
rm %{buildroot}%{_qt6_libexecdir}/ensure_pro_file.cmake
rm %{buildroot}%{_qt6_libexecdir}/qt-android-runner.py
rm %{buildroot}%{_qt6_libexecdir}/qt-testrunner.py
rm %{buildroot}%{_qt6_libexecdir}/sanitizer-testrunner.py

# Not useful for desktop installs
rm -r %{buildroot}%{_qt6_libdir}/cmake/Qt6ExamplesAssetDownloaderPrivate
rm -r %{buildroot}%{_qt6_headerdir}/QtExamplesAssetDownloader
rm %{buildroot}%{_qt6_descriptionsdir}/ExamplesAssetDownloaderPrivate.json
rm %{buildroot}%{_qt6_libdir}/libQt6ExamplesAssetDownloader.*
rm %{buildroot}%{_qt6_libdir}/qt6/metatypes/qt6examplesassetdownloaderprivate_*_metatypes.json

# This is only for Apple platforms and has a python2 dep
rm -r %{buildroot}%{_qt6_mkspecsdir}/features/uikit

#Remove unversioned files that clash with qt5/chooser
rm %{buildroot}/%{_bindir}/qmake

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post gui -p /sbin/ldconfig
%postun gui -p /sbin/ldconfig

%files
%license LICENSES/GPL*
%license LICENSES/LGPL*
%dir %{_sysconfdir}/xdg/QtProject/
#%%{_qt6_archdatadir}/sbom/qtbase-%%{qt_version}.spdx
%{_qt6_libdir}/libQt6Concurrent.so.6*
%{_qt6_libdir}/libQt6Core.so.6*
%{_qt6_libdir}/libQt6DBus.so.6*
%{_qt6_libdir}/libQt6Network.so.6*
%{_qt6_libdir}/libQt6Sql.so.6*
%{_qt6_libdir}/libQt6Test.so.6*
%{_qt6_libdir}/libQt6Xml.so.6*
%{_qt6_docdir}/global/
%{_qt6_docdir}/config/
%{_qt6_datadir}/qtlogging.ini
%dir %{_qt6_plugindir}/designer/
%dir %{_qt6_plugindir}/generic/
%dir %{_qt6_plugindir}/iconengines/
%dir %{_qt6_plugindir}/imageformats/
%dir %{_qt6_plugindir}/networkinformation/
%dir %{_qt6_plugindir}/platforminputcontexts/
%dir %{_qt6_plugindir}/platforms/
%dir %{_qt6_plugindir}/platformthemes/
%dir %{_qt6_plugindir}/printsupport/
%dir %{_qt6_plugindir}/script/
%dir %{_qt6_plugindir}/sqldrivers/
%dir %{_qt6_plugindir}/styles/
%dir %{_qt6_plugindir}/tls/
%{_qt6_plugindir}/networkinformation/libqglib.so
%{_qt6_plugindir}/networkinformation/libqnetworkmanager.so
%{_qt6_plugindir}/sqldrivers/libqsqlite.so
%{_qt6_plugindir}/tls/libqcertonlybackend.so
%{_qt6_plugindir}/tls/libqopensslbackend.so
%{_bindir}/qtpaths*
%{_qt6_bindir}/qtpaths*

%files common
# mostly empty for now, consider: filesystem/dir ownership, licenses
%{_rpmmacrodir}/macros.qt6-qtbase

%files devel
%dir %{_qt6_libdir}/cmake/Qt6
%dir %{_qt6_libdir}/cmake/Qt6/libexec
%dir %{_qt6_libdir}/cmake/Qt6/platforms
%dir %{_qt6_libdir}/cmake/Qt6/platforms/Platform
%dir %{_qt6_libdir}/cmake/Qt6/config.tests
%dir %{_qt6_libdir}/cmake/Qt6/3rdparty
%dir %{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules
%dir %{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/find-modules
%dir %{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/modules
%dir %{_qt6_libdir}/cmake/Qt6/3rdparty/kwin
%dir %{_qt6_libdir}/cmake/Qt6BuildInternals
%dir %{_qt6_libdir}/cmake/Qt6BuildInternals/StandaloneTests
%dir %{_qt6_libdir}/cmake/Qt6BuildInternals/QtStandaloneTestTemplateProject
%dir %{_qt6_libdir}/cmake/Qt6Concurrent
%dir %{_qt6_libdir}/cmake/Qt6Core
%dir %{_qt6_libdir}/cmake/Qt6CoreTools
%dir %{_qt6_libdir}/cmake/Qt6DBus
%dir %{_qt6_libdir}/cmake/Qt6DBusTools
%dir %{_qt6_libdir}/cmake/Qt6Gui
%dir %{_qt6_libdir}/cmake/Qt6GuiTools
%dir %{_qt6_libdir}/cmake/Qt6HostInfo
%dir %{_qt6_libdir}/cmake/Qt6Network
%dir %{_qt6_libdir}/cmake/Qt6OpenGL
%dir %{_qt6_libdir}/cmake/Qt6OpenGLWidgets
%dir %{_qt6_libdir}/cmake/Qt6PrintSupport
%dir %{_qt6_libdir}/cmake/Qt6Sql
%dir %{_qt6_libdir}/cmake/Qt6Test
%dir %{_qt6_libdir}/cmake/Qt6TestInternalsPrivate
%dir %{_qt6_libdir}/cmake/Qt6TestInternalsPrivate/3rdparty
%dir %{_qt6_libdir}/cmake/Qt6TestInternalsPrivate/3rdparty/cmake
%dir %{_qt6_libdir}/cmake/Qt6Widgets
%dir %{_qt6_libdir}/cmake/Qt6WidgetsTools
%dir %{_qt6_libdir}/cmake/Qt6Xml
%{_bindir}/androiddeployqt
%{_bindir}/androiddeployqt6
%{_bindir}/androidtestrunner
%{_bindir}/qdbuscpp2xml*
%{_bindir}/qdbusxml2cpp*
%{_bindir}/qmake6
%{_bindir}/qt-cmake
%{_bindir}/qt-cmake-create
%{_bindir}/qt-configure-module
%{_libdir}/qt6/bin/qmake6
%{_qt6_bindir}/androiddeployqt
%{_qt6_bindir}/androiddeployqt6
%{_qt6_bindir}/androidtestrunner
%{_qt6_bindir}/qdbuscpp2xml
%{_qt6_bindir}/qdbusxml2cpp
%{_qt6_bindir}/qmake
%{_qt6_bindir}/qt-cmake
%{_qt6_bindir}/qt-cmake-create
%{_qt6_bindir}/qt-configure-module
%{_qt6_libexecdir}/qt-cmake-private
%{_qt6_libexecdir}/qt-cmake-private-install.cmake
%{_qt6_libexecdir}/qt-cmake-standalone-test
%{_qt6_libexecdir}/cmake_automoc_parser
%{_qt6_libexecdir}/qt-internal-configure-examples
%{_qt6_libexecdir}/qt-internal-configure-tests
%{_qt6_libexecdir}/syncqt
%{_qt6_libexecdir}/moc
%{_qt6_libexecdir}/tracegen
%{_qt6_libexecdir}/tracepointgen
%{_qt6_libexecdir}/qlalr
%{_qt6_libexecdir}/qvkgen
%{_qt6_libexecdir}/rcc
%{_qt6_libexecdir}/uic
%{_qt6_headerdir}/QtConcurrent/
%{_qt6_headerdir}/QtCore/
%{_qt6_headerdir}/QtDBus/
%{_qt6_headerdir}/QtGui/
%{_qt6_headerdir}/QtNetwork/
%{_qt6_headerdir}/QtOpenGL/
%{_qt6_headerdir}/QtOpenGLWidgets
%{_qt6_headerdir}/QtPrintSupport/
%{_qt6_headerdir}/QtSql/
%{_qt6_headerdir}/QtTest/
%{_qt6_headerdir}/QtWidgets/
%{_qt6_headerdir}/QtXcb/
%{_qt6_headerdir}/QtXml/
%{_qt6_libdir}/libQt6Concurrent.prl
%{_qt6_libdir}/libQt6Concurrent.so
%{_qt6_libdir}/libQt6Core.prl
%{_qt6_libdir}/libQt6Core.so
%{_qt6_libdir}/libQt6DBus.prl
%{_qt6_libdir}/libQt6DBus.so
%{_qt6_libdir}/libQt6Gui.prl
%{_qt6_libdir}/libQt6Gui.so
%{_qt6_libdir}/libQt6Network.prl
%{_qt6_libdir}/libQt6Network.so
%{_qt6_libdir}/libQt6OpenGL.prl
%{_qt6_libdir}/libQt6OpenGL.so
%{_qt6_libdir}/libQt6OpenGLWidgets.prl
%{_qt6_libdir}/libQt6OpenGLWidgets.so
%{_qt6_libdir}/libQt6PrintSupport.prl
%{_qt6_libdir}/libQt6PrintSupport.so
%{_qt6_libdir}/libQt6Sql.prl
%{_qt6_libdir}/libQt6Sql.so
%{_qt6_libdir}/libQt6Test.prl
%{_qt6_libdir}/libQt6Test.so
%{_qt6_libdir}/libQt6Widgets.prl
%{_qt6_libdir}/libQt6Widgets.so
#%%{_qt6_libdir}/libQt6XcbQpa.prl
#%%{_qt6_libdir}/libQt6XcbQpa.so 
%{_qt6_libdir}/libQt6Xml.prl
%{_qt6_libdir}/libQt6Xml.so
%{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/REUSE.toml
%{_qt6_libdir}/cmake/Qt6/3rdparty/kwin/REUSE.toml
%{_qt6_libdir}/cmake/Qt6/*.h.in
%{_qt6_libdir}/cmake/Qt6/*.cmake
%{_qt6_libdir}/cmake/Qt6/*.cmake.in
%{_qt6_libdir}/cmake/Qt6/PkgConfigLibrary.pc.in
%{_qt6_libdir}/cmake/Qt6/config.tests/*
%{_qt6_libdir}/cmake/Qt6/libexec/*
%{_qt6_libdir}/cmake/Qt6/platforms/*.cmake
%{_qt6_libdir}/cmake/Qt6/platforms/Platform/*.cmake
%{_qt6_libdir}/cmake/Qt6/qbatchedtestrunner.in.cpp
%{_qt6_libdir}/cmake/Qt6/ModuleDescription.json.in
%{_qt6_libdir}/cmake/Qt6/QtFileConfigure.txt.in
%{_qt6_libdir}/cmake/Qt6/QtConfigureTimeExecutableCMakeLists.txt.in
%{_qt6_libdir}/cmake/Qt6/QtSeparateDebugInfo.Info.plist.in
%{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/COPYING-CMAKE-SCRIPTS
%{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/find-modules/*.cmake
%{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/modules/*.cmake
%{_qt6_libdir}/cmake/Qt6/3rdparty/extra-cmake-modules/qt_attribution.json
%{_qt6_libdir}/cmake/Qt6/3rdparty/kwin/COPYING-CMAKE-SCRIPTS
%{_qt6_libdir}/cmake/Qt6/3rdparty/kwin/*.cmake
%{_qt6_libdir}/cmake/Qt6/3rdparty/kwin/qt_attribution.json
%{_qt6_libdir}/cmake/Qt6BuildInternals/*.cmake
%{_qt6_libdir}/cmake/Qt6BuildInternals/QtStandaloneTestTemplateProject/CMakeLists.txt
%{_qt6_libdir}/cmake/Qt6BuildInternals/StandaloneTests/QtBaseTestsConfig.cmake
%{_qt6_libdir}/cmake/Qt6BuildInternals/QtStandaloneTestTemplateProject/Main.cmake
%{_qt6_libdir}/cmake/Qt6Concurrent/*.cmake
%{_qt6_libdir}/cmake/Qt6Core/*.cmake
%{_qt6_libdir}/cmake/Qt6Core/Qt6CoreResourceInit.in.cpp
%{_qt6_libdir}/cmake/Qt6Core/Qt6CoreConfigureFileTemplate.in
%{_qt6_libdir}/cmake/Qt6CoreTools/*.cmake
%{_qt6_libdir}/cmake/Qt6DBus/*.cmake
%{_qt6_libdir}/cmake/Qt6DBusTools/*.cmake
%{_qt6_libdir}/cmake/Qt6Gui/*.cmake
%{_qt6_libdir}/cmake/Qt6GuiTools/*.cmake
%{_qt6_libdir}/cmake/Qt6HostInfo/*.cmake
%{_qt6_libdir}/cmake/Qt6Network/*.cmake
%{_qt6_libdir}/cmake/Qt6OpenGL/*.cmake
%{_qt6_libdir}/cmake/Qt6OpenGLWidgets/*.cmake
%{_qt6_libdir}/cmake/Qt6PrintSupport/*.cmake
%{_qt6_libdir}/cmake/Qt6Sql/Qt6Sql*.cmake
%{_qt6_libdir}/cmake/Qt6Sql/Qt6QSQLiteDriverPlugin*.cmake
%{_qt6_libdir}/cmake/Qt6Test/*.cmake
%{_qt6_libdir}/cmake/Qt6TestInternalsPrivate/*.cmake
%{_qt6_libdir}/cmake/Qt6TestInternalsPrivate/3rdparty/cmake/*.cmake
%{_qt6_libdir}/cmake/Qt6Widgets/*.cmake
%{_qt6_libdir}/cmake/Qt6WidgetsTools/*.cmake
%{_qt6_libdir}/cmake/Qt6Xml/*.cmake
%{_qt6_descriptionsdir}/Concurrent.json
%{_qt6_descriptionsdir}/Core.json
%{_qt6_descriptionsdir}/DBus.json
%{_qt6_descriptionsdir}/Gui.json
%{_qt6_descriptionsdir}/Network.json
%{_qt6_descriptionsdir}/OpenGL.json
%{_qt6_descriptionsdir}/OpenGLWidgets.json
%{_qt6_descriptionsdir}/PrintSupport.json
%{_qt6_descriptionsdir}/Sql.json
%{_qt6_descriptionsdir}/Test.json
%{_qt6_descriptionsdir}/Widgets.json
%{_qt6_descriptionsdir}/Xml.json
%{_qt6_metatypesdir}/qt6concurrent_*_metatypes.json
%{_qt6_metatypesdir}/qt6core_*_metatypes.json
%{_qt6_metatypesdir}/qt6dbus_*_metatypes.json
%{_qt6_metatypesdir}/qt6gui_*_metatypes.json
%{_qt6_metatypesdir}/qt6network_*_metatypes.json
%{_qt6_metatypesdir}/qt6opengl_*_metatypes.json
%{_qt6_metatypesdir}/qt6openglwidgets_*_metatypes.json
%{_qt6_metatypesdir}/qt6printsupport_*_metatypes.json
%{_qt6_metatypesdir}/qt6sql_*_metatypes.json
%{_qt6_metatypesdir}/qt6test_*_metatypes.json
%{_qt6_metatypesdir}/qt6widgets_*_metatypes.json
%{_qt6_metatypesdir}/qt6xml_*_metatypes.json
%{_qt6_libdir}/pkgconfig/*.pc
%{_qt6_mkspecsdir}/*
%{_qt6_descriptionsdir}/TestInternalsPrivate.json

## private-devel globs
%exclude %{_qt6_headerdir}/*/%{qt_version}/

%files private-devel
%{_qt6_headerdir}/QtEglFSDeviceIntegration
%{_qt6_headerdir}/QtEglFsKmsGbmSupport
%{_qt6_headerdir}/QtEglFsKmsSupport
%dir %{_qt6_libdir}/cmake/Qt6EglFSDeviceIntegrationPrivate
%dir %{_qt6_libdir}/cmake/Qt6EglFsKmsGbmSupportPrivate
%dir %{_qt6_libdir}/cmake/Qt6EglFsKmsSupportPrivate
#%%dir %%{_qt6_libdir}/cmake/Qt6XcbQpaPrivate
%{_qt6_libdir}/cmake/Qt6EglFSDeviceIntegrationPrivate/*.cmake
%{_qt6_libdir}/cmake/Qt6EglFsKmsGbmSupportPrivate/*.cmake
%{_qt6_libdir}/cmake/Qt6EglFsKmsSupportPrivate/*.cmake
#%%{_qt6_libdir}/cmake/Qt6XcbQpaPrivate/*.cmake
%{_qt6_libdir}/libQt6EglFsKmsSupport.prl
%{_qt6_libdir}/libQt6EglFsKmsSupport.so
%{_qt6_libdir}/libQt6EglFSDeviceIntegration.prl
%{_qt6_libdir}/libQt6EglFSDeviceIntegration.so
%{_qt6_libdir}/libQt6EglFsKmsGbmSupport.prl
%{_qt6_libdir}/libQt6EglFsKmsGbmSupport.so
%{_qt6_descriptionsdir}/EglFSDeviceIntegrationPrivate.json
%{_qt6_descriptionsdir}/EglFsKmsGbmSupportPrivate.json
%{_qt6_descriptionsdir}/EglFsKmsSupportPrivate.json
#%%{_qt6_descriptionsdir}/XcbQpaPrivate.json
%{_qt6_metatypesdir}/qt6eglfsdeviceintegrationprivate_*_metatypes.json
%{_qt6_metatypesdir}/qt6eglfskmsgbmsupportprivate_*_metatypes.json
%{_qt6_metatypesdir}/qt6eglfskmssupportprivate_*_metatypes.json
#%%{_qt6_metatypesdir}/qt6xcbqpaprivate_*_metatypes.json
%{_qt6_headerdir}/*/%{qt_version}/

%files static
%dir %{_qt6_libdir}/cmake/Qt6ExampleIconsPrivate
%{_qt6_libdir}/cmake/Qt6ExampleIconsPrivate/*.cmake
%{_qt6_headerdir}/QtExampleIcons
%{_qt6_libdir}/libQt6ExampleIcons.a
%{_qt6_libdir}/libQt6ExampleIcons.prl
%{_qt6_descriptionsdir}/ExampleIconsPrivate.json
%dir %{_qt6_archdatadir}/objects-*
%{_qt6_archdatadir}/objects-*/ExampleIconsPrivate_resources_1/
%{_qt6_metatypesdir}/qt6exampleiconsprivate_*_metatypes.json
%dir %{_qt6_libdir}/cmake/Qt6DeviceDiscoverySupportPrivate
%{_qt6_libdir}/cmake/Qt6DeviceDiscoverySupportPrivate/*.cmake
%{_qt6_headerdir}/QtDeviceDiscoverySupport
%{_qt6_libdir}/libQt6DeviceDiscoverySupport.*a
%{_qt6_libdir}/libQt6DeviceDiscoverySupport.prl
%{_qt6_descriptionsdir}/DeviceDiscoverySupportPrivate.json
%{_qt6_metatypesdir}/qt6devicediscoverysupportprivate_*_metatypes.json
%dir %{_qt6_libdir}/cmake/Qt6FbSupportPrivate
%{_qt6_libdir}/cmake/Qt6FbSupportPrivate/*.cmake
%{_qt6_headerdir}/QtFbSupport
%{_qt6_libdir}/libQt6FbSupport.*a
%{_qt6_libdir}/libQt6FbSupport.prl
%{_qt6_descriptionsdir}/FbSupportPrivate.json
%{_qt6_metatypesdir}/qt6fbsupportprivate_*_metatypes.json
%dir %{_qt6_libdir}/cmake/Qt6InputSupportPrivate
%{_qt6_libdir}/cmake/Qt6InputSupportPrivate/*.cmake
%{_qt6_headerdir}/QtInputSupport
%{_qt6_libdir}/libQt6InputSupport.*a
%{_qt6_libdir}/libQt6InputSupport.prl
%{_qt6_descriptionsdir}/InputSupportPrivate.json
%{_qt6_metatypesdir}/qt6inputsupportprivate_*_metatypes.json
%dir %{_qt6_libdir}/cmake/Qt6KmsSupportPrivate
%{_qt6_libdir}/cmake/Qt6KmsSupportPrivate/*.cmake
%{_qt6_headerdir}/QtKmsSupport
%{_qt6_libdir}/libQt6KmsSupport.*a
%{_qt6_libdir}/libQt6KmsSupport.prl
%{_qt6_descriptionsdir}/KmsSupportPrivate.json
%{_qt6_metatypesdir}/qt6kmssupportprivate_*_metatypes.json

%files gui
%{_qt6_libdir}/libQt6Gui.so.6*
%{_qt6_libdir}/libQt6OpenGL.so.6*
%{_qt6_libdir}/libQt6OpenGLWidgets.so.6*
%{_qt6_libdir}/libQt6PrintSupport.so.6*
%{_qt6_libdir}/libQt6Widgets.so.6*
#%%{_qt6_libdir}/libQt6XcbQpa.so.6*
# Generic
%{_qt6_plugindir}/generic/libqevdevkeyboardplugin.so
%{_qt6_plugindir}/generic/libqevdevmouseplugin.so
%{_qt6_plugindir}/generic/libqevdevtabletplugin.so
%{_qt6_plugindir}/generic/libqevdevtouchplugin.so
%{_qt6_plugindir}/generic/libqtuiotouchplugin.so
# Imageformats
%{_qt6_plugindir}/imageformats/libqico.so
%{_qt6_plugindir}/imageformats/libqjpeg.so
%{_qt6_plugindir}/imageformats/libqgif.so
# Platforminputcontexts
%{_qt6_plugindir}/platforminputcontexts/libcomposeplatforminputcontextplugin.so
%{_qt6_plugindir}/platforminputcontexts/libibusplatforminputcontextplugin.so
# EGL
%{_qt6_libdir}/libQt6EglFSDeviceIntegration.so.6*
%{_qt6_libdir}/libQt6EglFsKmsSupport.so.6*
%{_qt6_libdir}/libQt6EglFsKmsGbmSupport.so.6*
%{_qt6_plugindir}/platforms/libqeglfs.so
%{_qt6_plugindir}/platforms/libqminimalegl.so
%dir %{_qt6_plugindir}/egldeviceintegrations/
%{_qt6_plugindir}/egldeviceintegrations/libqeglfs-kms-integration.so
#%%{_qt6_plugindir}/egldeviceintegrations/libqeglfs-x11-integration.so
%{_qt6_plugindir}/egldeviceintegrations/libqeglfs-kms-egldevice-integration.so
%{_qt6_plugindir}/egldeviceintegrations/libqeglfs-emu-integration.so
#%%dir %%{_qt6_plugindir}/xcbglintegrations/
#%%{_qt6_plugindir}/xcbglintegrations/libqxcb-egl-integration.so

# Platforms
%{_qt6_plugindir}/platforms/libqlinuxfb.so
%{_qt6_plugindir}/platforms/libqminimal.so
%{_qt6_plugindir}/platforms/libqoffscreen.so
#%%{_qt6_plugindir}/platforms/libqxcb.so
%{_qt6_plugindir}/platforms/libqvnc.so
%if %{with vulkan}
%{_qt6_plugindir}/platforms/libqvkkhrdisplay.so
%endif
# Platformthemes
%{_qt6_plugindir}/platformthemes/libqxdgdesktopportal.so
#%%{_qt6_plugindir}/platformthemes/libqgtk3.so

# Printsupport
%{_qt6_plugindir}/printsupport/libcupsprintersupport.so

