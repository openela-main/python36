# ==================
# Top-level metadata
# ==================

%global pybasever 3.6

Name:       python36
Version:    %{pybasever}.8
Release:    2%{?dist}
Summary:    Interpreter of the Python programming language

License:    Python
URL:        https://www.python.org/

# LICENSE file is fetched from the Python 3 github repository
# for the respective version.
Source0:    https://github.com/python/cpython/raw/v%{version}/LICENSE
Source1:    README
Source2:    macros.python36

%global debug_package %{nil}

# ==================================
# Conditionals controlling the build
# ==================================

# Extra build for debugging the interpreter or C-API extensions
# (the -debug subpackages)
%bcond_without debug_build


# ==============================================
# Metadata and macros from the python3 component
# ==============================================

# ABIFLAGS, LDVERSION and SOABI are in the upstream configure.ac
# See PEP 3149 for some background: http://www.python.org/dev/peps/pep-3149/
%global ABIFLAGS_optimized m
%global ABIFLAGS_debug     dm

%global LDVERSION_optimized %{pybasever}%{ABIFLAGS_optimized}
%global LDVERSION_debug     %{pybasever}%{ABIFLAGS_debug}


# =======================
# Package and subpackages
# =======================

# python36 package itself
Provides: python3 = %{version}-%{release}
Provides: python3%{?_isa} = %{version}-%{release}
Obsoletes: python3 < 3.6.6-13

# When the user tries to `yum install python`, yum will list this package among
# the possible alternatives
Provides: alternative-for(python)

Requires:   %{_libexecdir}/platform-python
# python36 carries alternatives slave links for these packages, so they have to be installed
Requires:   python3-pip
Requires:   python3-setuptools

# Runtime require alternatives
Requires:         %{_sbindir}/alternatives
Requires(post):   %{_sbindir}/alternatives
Requires(postun): %{_sbindir}/alternatives

%global _description \
Python is an accessible, high-level, dynamically typed, interpreted programming\
language, designed with an emphasis on code readibility.\
It includes an extensive standard library, and has a vast ecosystem of\
third-party libraries.\
\
The python36 package provides the "python3.6" executable: the reference\
interpreter for the Python language, version 3.\
The package also installs the "python3" executable which is user configurable\
using the "alternatives --config python3" command.\
For the unversioned "python" command, see manual page "unversioned-python".\
\
The python36-devel package contains files for dovelopment of Python application\
and the python36-debug is helpful for debugging.\
\
Packages containing additional libraries for Python 3.6 are generally named\
with the "python3-" prefix.

%description %_description


%package devel
Summary:    Libraries and header files needed for Python development
Provides:   python3-devel = %{version}-%{release}
Provides:   python3-devel%{?_isa} = %{version}-%{release}
Requires:   python36
Requires:   platform-python-devel
# python36 installs the alternatives master symlink to which we attach a slave
Requires(post): python36
Requires(postun): python36

%description devel
This package contains the header files and configuration needed to compile
Python extension modules (typically written in C or C++), to embed Python
into other programs, and to make binary distributions for Python libraries.

If you want to build an RPM against the python36 module, you also need to
install the python36-rpm-macros package.


%if %{with debug_build}
%package debug
Summary:    Debug version of the Python runtime
Provides:   python3-debug = %{version}-%{release}
Provides:   python3-debug%{?_isa} = %{version}-%{release}
Obsoletes:  python3-debug < 3.6.6-13
Requires:   python36
Requires:   python36-devel
Requires:   platform-python-debug
# python36 installs the alternatives master symlink to which we attach a slave
Requires(post): python36
Requires(postun): python36

%description debug
python36-debug provides a version of the Python runtime with numerous debugging
features enabled, aimed at advanced Python users such as developers of Python
extension modules.

This version uses more memory and will be slower than the regular Python build,
but is useful for tracking down reference-counting issues and other bugs.

The bytecode format is unchanged, so that .pyc files are compatible between
this and the standard version of Python, but the debugging features mean that
C/C++ extension modules are ABI-incompatible and must be built for each version
separately.

The debug build shares installation directories with the standard Python
runtime, so that .py and .pyc files can be shared.
Compiled extension modules use a special ABI flag ("d") in the filename,
so extensions for both verisons can co-exist in the same directory.
%endif # with debug_build


%package -n python36-rpm-macros
Summary:    RPM macros for building RPMs with Python 3.6
Provides:   python36-modular-devel = %{version}-%{release}
Provides:   python-modular-rpm-macros == 3.6
Conflicts:  python-modular-rpm-macros > 3.6
Requires:   python3-rpm-macros
BuildArch:  noarch

%description -n python36-rpm-macros
RPM macros for building RPMs with Python 3.6 from the python36 module.
If you want to build an RPM against the python36 module, you need to
BuildRequire: python36-rpm-macros.


%prep
cp %{SOURCE0} LICENSE
cp %{SOURCE1} README


%build


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man1/

# Symlink the executable to libexec
ln -s %{_libexecdir}/platform-python%{pybasever} %{buildroot}%{_bindir}/python%{pybasever}

# Symlink the config executables
ln -s python%{LDVERSION_optimized}-config %{buildroot}%{_bindir}/python%{pybasever}-config

# LDVERSION specific section
InstallPython() {
  LDVersion=$1

  # Symlink python*-config to libexec
  ln -s %{_libexecdir}/platform-python${LDVersion}-config %{buildroot}%{_bindir}/python${LDVersion}-config
  ln -s %{_libexecdir}/platform-python${LDVersion}-`uname -m`-config %{buildroot}%{_bindir}/python${LDVersion}-`uname -m`-config

  # Symlink optimized and debug executables
  ln -s %{_libexecdir}/platform-python${LDVersion} %{buildroot}%{_bindir}/python${LDVersion}
}

%if %{with debug_build}
InstallPython %{LDVERSION_debug}
# General debug symlinks
ln -s python%{LDVERSION_debug}-config %{buildroot}%{_bindir}/python%{pybasever}-debug-config
ln -s python%{LDVERSION_debug} %{buildroot}%{_bindir}/python%{pybasever}-debug
%endif # with debug_build

InstallPython %{LDVERSION_optimized}

# Python RPM macros
mkdir -p %{buildroot}/%{rpmmacrodir}/
install -m 644 %{SOURCE2} \
    %{buildroot}/%{rpmmacrodir}/

# All ghost files controlled by alternatives need to exist for the files
# section check to succeed
# - Don't list /usr/bin/python as a ghost file so `yum install /usr/bin/python`
#   doesn't install this package
touch %{buildroot}%{_bindir}/unversioned-python
touch %{buildroot}%{_mandir}/man1/python.1.gz
touch %{buildroot}%{_bindir}/python3
touch %{buildroot}%{_mandir}/man1/python3.1.gz
touch %{buildroot}%{_bindir}/pip3
touch %{buildroot}%{_bindir}/pip-3
touch %{buildroot}%{_bindir}/easy_install-3
touch %{buildroot}%{_bindir}/pydoc3
touch %{buildroot}%{_bindir}/pydoc-3
touch %{buildroot}%{_bindir}/pyvenv-3
touch %{buildroot}%{_bindir}/python3-config
touch %{buildroot}%{_bindir}/python3-debug
touch %{buildroot}%{_bindir}/python3-debug-config


%post
# Alternative for /usr/bin/python -> /usr/bin/python3 + man page
alternatives --install %{_bindir}/unversioned-python \
                       python \
                       %{_bindir}/python3 \
                       300 \
             --slave   %{_bindir}/python \
                       unversioned-python \
                       %{_bindir}/python3 \
             --slave   %{_mandir}/man1/python.1.gz \
                       unversioned-python-man \
                       %{_mandir}/man1/python3.1.gz

# Alternative for /usr/bin/python3 -> /usr/bin/python3.6
# Create only if it doesn't exist already
EXISTS=`alternatives --display python3 | \
        grep -c "^/usr/bin/python3.6 - priority [0-9]*"`

if [ $EXISTS -eq 0 ]; then
    alternatives --install %{_bindir}/python3 \
                           python3 \
                           %{_bindir}/python3.6 \
                           1000000 \
                 --slave   %{_mandir}/man1/python3.1.gz \
                           python3-man \
                           %{_mandir}/man1/python3.6.1.gz \
                 --slave   %{_bindir}/pip3 \
                           pip3 \
                           %{_bindir}/pip3.6 \
                 --slave   %{_bindir}/pip-3 \
                           pip-3 \
                           %{_bindir}/pip-3.6 \
                 --slave   %{_bindir}/easy_install-3 \
                           easy_install-3 \
                           %{_bindir}/easy_install-3.6 \
                 --slave   %{_bindir}/pydoc3 \
                           pydoc3 \
                           %{_bindir}/pydoc3.6 \
                 --slave   %{_bindir}/pydoc-3 \
                           pydoc-3 \
                           %{_bindir}/pydoc3.6 \
                 --slave   %{_bindir}/pyvenv-3 \
                           pyvenv-3 \
                           %{_bindir}/pyvenv-3.6
fi

%postun
# Do this only during uninstall process (not during update)
if [ $1 -eq 0 ]; then
    alternatives --remove python3 \
                        %{_bindir}/python3.6

    # Remove link python → python3 if no other python3.* exists
    if ! alternatives --display python3 > /dev/null; then
        alternatives --remove python \
                            %{_bindir}/python3
    fi
fi


%post -n python36-devel
alternatives --add-slave python3 %{_bindir}/python3.6 \
    %{_bindir}/python3-config \
    python3-config \
    %{_bindir}/python3.6-config

%postun -n python36-devel
# Do this only during uninstall process (not during update)
if [ $1 -eq 0 ]; then
    alternatives --remove-slave python3 %{_bindir}/python3.6 \
        python3-config
fi


%post -n python36-debug
alternatives --add-slave python3 %{_bindir}/python3.6 \
    %{_bindir}/python3-debug \
    python3-debug \
    %{_bindir}/python3.6-debug
alternatives --add-slave python3 %{_bindir}/python3.6 \
    %{_bindir}/python3-debug-config \
    python3-debug-config \
    %{_bindir}/python3.6-debug-config

%postun -n python36-debug
# Do this only during uninstall process (not during update)
if [ $1 -eq 0 ]; then
    alternatives --remove-slave python3 %{_bindir}/python3.6 \
        python3-debug
    alternatives --remove-slave python3 %{_bindir}/python3.6 \
        python3-debug-config
fi


%files
%license LICENSE
%doc README
%{_bindir}/python%{pybasever}
%{_bindir}/python%{LDVERSION_optimized}
%ghost %{_bindir}/unversioned-python
%ghost %{_mandir}/man1/python.1.gz
%ghost %{_bindir}/python3
%ghost %{_mandir}/man1/python3.1.gz
%ghost %{_bindir}/pip3
%ghost %{_bindir}/pip-3
%ghost %{_bindir}/easy_install-3
%ghost %{_bindir}/pydoc3
%ghost %{_bindir}/pydoc-3
%ghost %{_bindir}/pyvenv-3

%files devel
%license LICENSE
%doc README
%{_bindir}/python%{pybasever}-config
%{_bindir}/python%{LDVERSION_optimized}-config
%{_bindir}/python%{LDVERSION_optimized}-*-config
%ghost %{_bindir}/python3-config

%files debug
%license LICENSE
%doc README
%{_bindir}/python%{LDVERSION_debug}
%{_bindir}/python%{LDVERSION_debug}-config
%{_bindir}/python%{LDVERSION_debug}-*-config
%{_bindir}/python%{pybasever}-debug-config
%{_bindir}/python%{pybasever}-debug
%ghost %{_bindir}/python3-debug
%ghost %{_bindir}/python3-debug-config

%files -n python36-rpm-macros
%license LICENSE
%doc README
%{rpmmacrodir}/macros.python36


%changelog
* Thu Apr 25 2019 Tomas Orsava <torsava@redhat.com> - 3.6.8-2
- Bumping due to problems with modular RPM upgrade path
- Resolves: rhbz#1695587

* Mon Jan 21 2019 Charalampos Stratakis <cstratak@redhat.com> - 3.6.8-1
- Sync version-release with the python3 component
- Resolves: rhbz#1658271

* Tue Dec 04 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-18
- Remove the Python source tarball as it's not being used in this symlink
  component
- Create a new explanatory README
- Resolves: rhbz#1654867

* Tue Oct 16 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-17
- Slightly edit the description
- Related: rhbz#1633534

* Sun Oct 14 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-16
- Add Requires (/post/postun) on /usr/sbin/alternatives
- Resolves: rhbz#1633534

* Fri Oct 12 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-15
- Don't list /usr/bin/python as a ghost file so `yum install /usr/bin/python`
  doesn't install this package
- Resolves: rhbz#1633534

* Mon Oct 08 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-14
- Set a special Provides tag that advertises the `python36` package as an
  alternative to the non-existing `python` package
- Resolves: rhbz#1633561

* Tue Oct 02 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-13.1
- Fix update of alternatives in the devel and debug packages
- Resolves: rhbz#1633534

* Sat Sep 29 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-13
- Provide the name `python3`, `python3-devel` and `python3-debug` from their
  respective packages to provide a sane default for Python 3
- Provide the name `python36-modular-devel` from python36-rpm-macros so it's
  easier to remember and describe in documentation
- Sync version-release with the python3 component
- Resolves: rhbz#1632637

* Sat Sep 29 2018 Tomas Orsava <torsava@redhat.com> - 3.6-7
- Implement the alternatives system for Python in RHEL8
- Resolves: rhbz#1633534

* Tue Sep 25 2018 Tomas Orsava <torsava@redhat.com> - 3.6-6
- Require the Python interpreter directly instead of using the package name
- Related: rhbz#1619153

* Tue Aug 14 2018 Lumír Balhar <lbalhar@redhat.com> - 3.6-5
- Add general symlinks python3.6-debug[-config] for symlinks modules
- Resolves: rhbz#1615727

* Sat Aug 04 2018 Tomas Orsava <torsava@redhat.com> - 3.6-4
- Switched devel subpackage's dependency from python3-devel to
  python3-libs-devel: python3-devel is now buildroot only and the contents were
  moved to python3-libs-devel

* Tue Jul 31 2018 Tomas Orsava <torsava@redhat.com> - 3.6-3
- Make the python36-rpm-macros package noarch

* Wed Apr 04 2018 Tomas Orsava <torsava@redhat.com> - 3.6-2
- Include python36-rpm-macros for building RPMs against this module

* Wed Apr 04 2018 Tomas Orsava <torsava@redhat.com> - 3.6-1
- This new package python36 will belong to the python36 module that will house
  symlinks from /usr/bin/python* to /usr/libexec/platform-python* et al.

