# A simplified kernel spec initially based on Tencent Linux Kernels and Fedora/CentOS
#
# By changing a few rpm macros, it's very convenient to build for different archs or
# kernel config styles, and build different components.
### Kenrel version relation macros
# Following variables filled by automation scripts:
# %%{kernel_majver}: Kernel RPM package version, eg. 5.15.0, 5.15.3, 5.16.0
# %%{kernel_relver}: Kernel RPM package release, eg. 2207.1, 0.20211115git1135ec008ef3.rc0.2207, 0009.11
# %%{kernel_variant}: Kernel RPM package release, eg. 2207.1, 0.20211115git1135ec008ef3.rc0.2207, 0009.11
# %%{kernel_tarname} Kernel Source tar's basename and prefix after untar, eg. 5.16.0.20211115git1135ec008ef3.rc0.2207
# %%{kernel_unamer}: Define `uname -r` output, needed by scriptlets so prepare it early. (KVER.%{{?dist}}.%{{_target_cpu}}%{{kernel_variant}})
# %%{rpm_name}: Kernel RPM package name, eg. kernel, kernel-tlinux4, kernel-stream kernel-stream-debug
# %%{rpm_vendor}: RPM package vendor
# %%{rpm_url}: RPM url
# TODO: kernel_unamer don't have distro mark
%define kernel_majver 6.6.114
%define kernel_relver 6
%define kernel_variant %{nil}
%define kernel_tarname kernel
%define kernel_unamer 6.6.114-6%{?dist}.%{_target_cpu}%{kernel_variant}
%define rpm_name kernel
%define rpm_vendor TencentOS
%define rpm_url https://gitee.com/OpenCloudOS/OpenCloudOS-Kernel

# This section defines following value:
# %%{kernel_arch}
# Since kernel arch name differs from many other definations, this will insert a script snip
# to handle the convertion, and error out on unsupported arch.
ExclusiveArch: x86_64 aarch64 loongarch64
%ifarch x86_64
%define kernel_arch x86_64
%endif
%ifarch aarch64
%define kernel_arch arm64
%endif
%ifarch loongarch64
%define kernel_arch loongarch
%endif

# TODO: This is a workaround for kernel userspace tools (eg. perf), which doesn't
# support LTO, and causes FTBFS, need to remove this after LTO is available in
# upstream
%global _lto_cflags %{nil}

###### Kernel packaging options #################################################
# Since we need to generate kernel, kernel-subpackages, perf, bpftools, from
# this one single code tree, following build switches are very helpful.
#
# The following build options can be enabled or disabled with --with/--without
# in the rpmbuild command. But may by disabled by later checks#
#
# This section defines following options:
# with_core: kernel core pkg
# with_doc: kernel doc pkg
# with_headers: kernel headers pkg
# with_perf: perf tools pkg
# with_tools: kernel tools pkg
# with_bpftool: bpftool pkg
# with_debuginfo: debuginfo for all packages
# with_modsign: if mod should be signed
# with_kabichk: if kabi check is needed at the end of build
# with_keypkg: package the signing key for user, CAUTION: this package allows
#              users to be able to sign their modules using kernel trusted key.

# === Package options ===
# Eanbled by default:  core doc headers perf tools bpftool debuginfo modsign keypkg
# Disabled by default:  kabichk ofed

%define with_core	%{?_without_core:0}%{?!_without_core:1}
%define with_doc	%{?_without_doc:0}%{?!_without_doc:1}
%define with_headers	%{?_without_headers:0}%{?!_without_headers:1}
%define with_perf	%{?_without_perf:0}%{?!_without_perf:1}
%define with_tools	%{?_without_tools:0}%{?!_without_tools:1}
%define with_bpftool	%{?_without_bpftool:0}%{?!_without_bpftool:1}
%define with_debuginfo	%{?_without_debuginfo:0}%{?!_without_debuginfo:1}
%define with_modsign	%{?_without_modsign:0}%{?!_without_modsign:1}
%define with_kabichk	%{?_with_kabichk:1}%{?!_with_kabichk:0}
%define with_ofed	0
%define with_keypkg	%{?_without_keypkg:0}%{?!_without_keypkg:1}

# Only use with cross build, don't touch it unless you know what you are doing
%define with_crossbuild	%{?_with_crossbuild: 1}		%{?!_with_crossbuild: 0}

###### Kernel signing params #################################################
### TODO: Currently only module signing, no secureboot
# module-keygen
# Should be an executable accepting two params:
# module-keygen <kernel ver> <kernel objdir>
# <kernel ver>: Kernel's version-release, `uname -r` output of that kernel
# <kernel objdir>: Kernel build dir, where built kernel objs, certs, and vmlinux is stored
#
# This executable should provide required keys for signing, or at least disable builtin keygen
%define use_builtin_module_keygen %{?_module_keygen: 0} %{?!_module_keygen: 1}

# module-signer
# Should be an executable accepting three params:
# module-signer <buildroot> <kernel ver> <kernel objdir>
# <kernel ver>: Kernel's version-release, `uname -r` output of that kernel
# <kernel objdir>: Kernel build dir, where built kernel objs, certs, and vmlinux is stored
# <buildroot>: RPM's buildroot, where kernel modules are installed into
#
# This executable should sign all kernel modules in <builddir>/lib/modules/<kernel ver>
# based on the info gatherable from <kernel objdir>.
%define use_builtin_module_signer %{?_module_signer: 0} %{?!_module_signer: 1}

###### Required RPM macros #####################################################

### Debuginfo handling
# Following macros controls RPM's builtin debuginfo extracting behaviour,
# tune it into a kernel friendly style.
#
# Kernel package needs its own method to pack the debuginfo files.
# This disables RPM's built-in debuginfo files packaging, we package
# debuginfo files manually use find-debuginfo.sh.
%undefine _debuginfo_subpackages
# This disables RH vendor macro's debuginfo package template generation.
# It only generates debuginfo for the main package, but we only want debuginfo
# for subpackages so disable it and do things manually.
%undefine _enable_debug_packages
# This disable find-debuginfo.sh from appending minimal debuginfo
# to every binary.
%undefine _include_minidebuginfo
# This disables debugsource package which collect source files for debug info,
# we pack the kernel source code manually.
%undefine _debugsource_packages
# TODO: This prevents find-debuginfo.sh from adding unique suffix to .ko.debug files
# that will make .ko.debug file names unrecognizable by `crash`
# We may patch `crash` to fix that or find a better way, since this stops the unique
# debug file renaming for userspace packages too.
%undefine _unique_debug_names
# Pass --reloc-debug-sections to eu-strip, .ko files are ET_REL files. So they have relocation
# sections for debug sections. Those sections will not be relinked. This help create .debug files
# that has cross debug section relocations resolved.
%global _find_debuginfo_opts -r
%global debuginfo_dir /usr/lib/debug
%global debug_package %{nil}

###### Build time config #######################################################
# Disable kernel building for non-supported arch, allow building userspace package
%ifarch %nobuildarches noarch
%global with_core 0
%endif

# Require cross compiler if cross compiling
%if %{with_crossbuild}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%global with_perf 0
%global with_tools 0
%global with_bpftool 0
%global _cross_compile %{!?_cross_compile:%{_build_arch}-linux-gnu-}%{?_cross_compile:%{_cross_compile}}
%endif

# List the packages used during the kernel build
BuildRequires: kmod, patch, bash, coreutils, tar, git-core, which, gawk
BuildRequires: make, gcc, binutils, system-rpm-config, hmaccalc, bison, flex, gcc-c++
BuildRequires: bzip2, xz, findutils, gzip, perl-interpreter, perl-Carp, perl-devel
BuildRequires: net-tools, hostname, bc
BuildRequires: dwarves
BuildRequires: openssl-devel, elfutils-devel
# Required by multiple kernel tools
BuildRequires: python3-devel, python3-setuptools
BuildRequires: openssl
BuildRequires: gcc-plugin-devel
# glibc-static is required for a consistent build environment (specifically
# CONFIG_CC_CAN_LINK_STATIC=y).
BuildRequires: glibc-static
# Kernel could be compressed with lz4
BuildRequires: lz4
# Needing clone sub git repo
BuildRequires: git

%if %{with_perf}
BuildRequires: zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel
BuildRequires: java-devel
BuildRequires: libbabeltrace-devel
BuildRequires: libtraceevent-devel
%ifnarch aarch64
BuildRequires: numactl-devel
%endif
%endif

%if %{with_tools}
BuildRequires: gettext ncurses-devel
BuildRequires: pciutils-devel libcap-devel libnl3-devel libtool
%endif

%if %{with_doc}
BuildRequires: xmlto, asciidoc
%endif

%if %{with_bpftool}
BuildRequires: llvm
# We don't care about this utils's python version, since we only want rst2* commands during build time
BuildRequires: /usr/bin/rst2man
BuildRequires: zlib-devel binutils-devel
%endif

# If CONFIG=generic-release and CONFIG=generic-debug both generate kernel-source-*.noarch.rpm, the rpm
# will be same with each other, which is not necessary.
# What's worse, building two identical kernel-debug-*.rpm packages causes the kernel build pipeline to
# fail when attempting to download kernel-source-*.rpm.
%global with_source 0
# If CONFIG=generic-release, with_headers will be 1
# If CONFIG=generic-debug, with_headers will be 0
%if %{with_headers}
BuildRequires: rsync
# Because kernel-source-*.noarch.rpm is noarch, let's only generate kernel-source rpm when build x86_64
# kernel rpms.
# If generate kernel-source rpm in each arch's building, that will cause build pipeline fail when
# attempting to download kernel-source-*.rpm.
%ifarch x86_64
%global with_source 1
%endif
%endif

###### Kernel packages sources #################################################
### Kernel tarball
Source0: %{kernel_tarname}.tar.gz

### Build time scripts
# Script used to assist kernel building
Source10: filter-modules.sh

Source20: module-signer.sh
Source21: module-keygen.sh

Source30: check-kabi

# RUE module load at boot
Source40: rue.conf

### Arch speficied kernel configs and kABI
# Start from Source1000 to Source1199, for kernel config
# Start from Source1200 to Source1399, for kabi
Source1000: generic-release.x86_64.config
Source1001: generic-release.aarch64.config
Source1002: generic-release.loongarch64.config
Source1200: Module.kabi_x86_64
Source1201: Module.kabi_aarch64
Source1202: Module.kabi_loongarch64

### Userspace tools
# Start from Source2000 to Source2999, for userspace tools
Source2000: cpupower.service
Source2001: cpupower.config

### Used for download thirdparty drivers
# Start from Source3000 to Source3099, for thirdparty release drivers
Source3000: download-and-copy-drivers.sh
Source3001: MLNX_OFED_LINUX-23.10-3.2.2.0-rhel9.4-x86_64.tgz
Source3002: install.sh

###### Kernel package definations ##############################################
### Main meta package
Summary: %{rpm_vendor} Linux kernel meta package
Name: %{rpm_name}
Version: %{kernel_majver}
Release: %{kernel_relver}%{?dist}
License: GPLv2
URL: %{rpm_url}

# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

# Kernel requirements
# installonlypkg(kernel) is a hint for RPM that this package shouldn't be auto-cleaned.
Provides: installonlypkg(kernel)
Provides: kernel = %{version}-%{release}
Provides: %{rpm_name} = %{version}-%{release}
Requires: %{rpm_name}-core = %{version}-%{release}
Requires: %{rpm_name}-modules = %{version}-%{release}
Requires: linux-firmware

%description
This is the meta package of %{?rpm_vendor:%{rpm_vendor} }Linux kernel, the core of operating system.

%if %{with_core}
### Kernel core package
%package core
Summary: %{rpm_vendor} Linux Kernel
Provides: installonlypkg(kernel)
Provides: kernel = %{version}-%{release}
Provides: %{rpm_name}-core = %{version}-%{release}
Provides: %{rpm_name}-core-uname-r = %{kernel_unamer}
Provides: kernel-uname-r = %{kernel_unamer}
Requires(pre): coreutils
Requires(post): coreutils kmod dracut
Requires(preun): coreutils kmod
Requires(post): %{_bindir}/kernel-install
Requires(preun): %{_bindir}/kernel-install
# Kernel install hooks & initramfs
%if 0%{?rhel} == 7 || "%{?dist}" == ".tl2"
Requires(post): systemd
Requires(preun): systemd
%else
Requires(post): systemd-udev
Requires(preun): systemd-udev
%endif

%description core
The kernel package contains the %{?rpm_vendor:%{rpm_vendor} } Linux kernel (vmlinuz), the core of
operating system. The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.

### Kernel module package
%package modules
Summary: %{rpm_vendor} Kernel modules to match the %{rpm_name}-core kernel
Provides: installonlypkg(kernel-module)
Provides: %{rpm_name}-modules = %{version}-%{release}
Provides: %{rpm_name}-modules-uname-r = %{kernel_unamer}
Provides: kernel-modules = %{kernel_unamer}
Provides: kernel-modules-extra = %{version}-%{release}
Requires: %{rpm_name}-core = %{version}-%{release}
AutoReq: no
AutoProv: yes
Requires(pre): kmod
Requires(postun): kmod
%description modules
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.

### Kernel devel package
%package devel
Summary: Development package for building kernel modules to match the %{version}-%{release} kernel
Release: %{release}
Provides: installonlypkg(kernel)
Provides: %{rpm_name}-devel = %{version}-%{release}
Provides: %{rpm_name}-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-devel-uname-r = %{kernel_unamer}
AutoReqprov: no
%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the %{version}-%{release} kernel package.

### Kernel module package
%if %{with_keypkg}
%package signing-keys
Summary: %{rpm_vendor} Kernel signing key
Provides: installonlypkg(kernel)
Requires: %{rpm_name}-core = %{version}-%{release}
AutoReq: no
AutoProv: yes
%description signing-keys
This package provides kernel signing key for the %{?2:%{2}-}core kernel package.
%endif

%if %{with_debuginfo}
### Kernel debuginfo package
%package debuginfo
Summary: Debug information for package %{rpm_name}
# TK: Break the chain of dependency, to allow independent distribution of debuginfo/debuginfo-common
# debuginfo-common contains source code, and because of how `crash` utility works, it's included in
# this -common package instead of standalone debugsource (which is usually distributed in standlone
# repo, and causes trouble for uses)
# Removed "Requires: kernel--debuginfo-common = xxx"
# More info, pls run "git blame dist/templates/kernel.template.spec" (or "git log -p dist/templates/kernel.template.spec")
# to find and read the relevant commit.
Provides: installonlypkg(kernel)
Provides: %{rpm_name}-debuginfo = %{version}-%{release}
AutoReqProv: no
%description debuginfo
This package provides debug information including
vmlinux, System.map for package %{rpm_name}.
This is required to use SystemTap with %{rpm_name}.
# debuginfo search rule
# If BTF presents, keep it so kernel can use it.
%if 0%{?rhel} != 7
# Old version of find-debuginfo.sh doesn't support this, so only do it for newer version. Old version of eu-strip seems doesn't strip BTF either, so should be fine.
%global _find_debuginfo_opts %{_find_debuginfo_opts} --keep-section '.BTF'
%endif
# Debuginfo file list for main kernel package
# The (\+.*)? is used to match all variant kernel
%global _find_debuginfo_opts %{_find_debuginfo_opts} -p '.*\/usr\/src\/kernels/.*|XXX' -o ignored-debuginfo.list -p $(echo '.*/%{kernel_unamer}/.*|.*/%{kernel_unamer}(\.debug)?' | sed 's/+/[+]/g') -o debuginfo.list
# with_debuginfo
%endif
# with_core
%endif

%if %{with_debuginfo}
### Common debuginfo package
%package debuginfo-common
Summary: Kernel source files used by %{rpm_name}-debuginfo packages
Provides: installonlypkg(kernel)
Provides: %{rpm_name}-debuginfo-common = %{version}-%{release}
%description debuginfo-common
This package is required by %{rpm_name}-debuginfo subpackages.
It provides the kernel source files common to all builds.
# No need to define extra debuginfo search rule here, use debugfiles.list
# with_debuginfo
%endif

%if %{with_headers}
%package headers
Summary: Header files for the Linux kernel for use by glibc
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
Provides: kernel-headers = %{version}-%{release}
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs. The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.
# with_headers
%endif

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Requires: bzip2
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
# TK: Break the chain of dependency, removed "Requires: kernel--debuginfo-common = xxx"
# More info, pls run "git blame dist/templates/kernel.template.spec" to find and read the relevant commit.
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.
# debuginfo search rule
# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%global _find_debuginfo_opts %{_find_debuginfo_opts} -p '.*%{_bindir}/perf(.*\.debug)?|.*%{_libexecdir}/perf-core/.*|.*%{_libdir}/libperf-jvmti.so(.*\.debug)?|.*%{_libdir}/traceevent/(.*\.debug)?|XXX' -o perf-debuginfo.list

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
%description -n python3-perf
The python3-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%package -n python3-perf-debuginfo
Summary: Debug information for package perf python bindings
# TK: Break the chain of dependency, removed "Requires: kernel--debuginfo-common = xxx"
# More info, pls run "git blame dist/templates/kernel.template.spec" to find and read the relevant commit.
AutoReqProv: no
%description -n python3-perf-debuginfo
This package provides debug information for the perf python bindings.
# debuginfo search rule
# the python_sitearch macro should already be defined from above
%global _find_debuginfo_opts %{_find_debuginfo_opts} -p '.*%{python3_sitearch}/perf.*\.so(.*\.debug)?|XXX' -o python3-perf-debuginfo.list
# with_perf
%endif

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
License: GPLv2
%ifarch %{cpupowerarchs}
Provides: cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides: cpufreq-utils = 1:009-0.6.p1
Provides: cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%endif
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
%ifarch %{cpupowerarchs}
Provides: cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
%endif
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
# TK: Break the chain of dependency, removed "Requires: kernel--debuginfo-common = xxx"
# More info, pls run "git blame dist/templates/kernel.template.spec" to find and read the relevant commit.
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.
# debuginfo search rule
# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%global _find_debuginfo_opts %{_find_debuginfo_opts} -p '.*%{_bindir}/(cpupower|tmon|gpio-.*|iio_.*|ls.*|centrino-decode|powernow-k8-decode|turbostat|x86_energy_perf_policy|intel-speed-select|page_owner_sort|slabinfo)(.*\.debug)?|.*%{_libdir}/libcpupower.*|XXX' -o kernel-tools-debuginfo.list
# with_tools
%endif

%if %{with_bpftool}
%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
License: GPLv2
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package -n bpftool-debuginfo
Summary: Debug information for package bpftool
# TK: Break the chain of dependency, removed "Requires: kernel--debuginfo-common = xxx"
# More info, pls run "git blame dist/templates/kernel.template.spec" to find and read the relevant commit.
AutoReqProv: no
%description -n bpftool-debuginfo
This package provides debug information for the bpftool package.
# debuginfo search rule
%global _find_debuginfo_opts %{_find_debuginfo_opts} -p '.*%{_sbindir}/bpftool(.*\.debug)?|XXX' -o bpftool-debuginfo.list
# with_bpftool
%endif

# To avoid compile error, do not integrate mlnx commercial quality drivers if not tencentos release.
# Users could compile and install MLNX_OFED_LINUX-* manually.
#
# Some oc9 partners have nic driver, and the driver support RDMA and only compatble with kernel native infiniband.
# If integrate mlnx driver, oc9 partners RDMA nic driver cloud not run.
%if "%{?dist}" != ".tl4" && "%{?dist}" != ".tl3"
%define with_ofed 0
%endif

# If the arch is riscv64 or loongarch64, don't compile mlnx commercial-grade quality driver.
%ifnarch x86_64
%ifnarch aarch64
%define with_ofed 0
%endif
%endif

%if %{with_ofed}
%ifarch x86_64
%package -n mlnx-ofed-dist
Summary: Mellonax ofed rpms installation
License: GPLv2
%if "%{?dist}" != ".tl3"
## "${DISTRO}" is .tl4 or oc9
BuildRequires: kernel-srpm-macros
BuildRequires: perl-sigtrap
%endif
BuildRequires: kernel-rpm-macros
BuildRequires: lsof
BuildRequires: pciutils
%description -n mlnx-ofed-dist
This package contains all the signed ko files.
%endif
%endif

%if %{with_source}
%package source
Summary: source code included %{_vendor} patch
BuildRequires: tar, xz
BuildArch: noarch

%description source
This package provides source code included %{_vendor} patch for cross toolchains
%endif

###### common macros for build and install #####################################
### Signing scripts
# If externel module signer and keygen provided, ignore built-in keygen and
# signer, else use builtin keygen and signer.
%if %{use_builtin_module_signer}
	# SOURCE20 is just a wrapper for $BUILD_DIR/scripts/sign-file
	%define _module_signer %{SOURCE20}
%endif
%if %{use_builtin_module_keygen}
	# SOURCE21 is a dummy file, only perform some checks, we depend on Kbuild for builtin keygen
	%define _module_keygen %{SOURCE21}
%endif

### Prepare common build vars to share by %%prep, %%build and %%install section
# _KernSrc: Path to kernel source, located in _buildir
# _KernBuild: Path to the built kernel objects, could be same as $_KernSrc (just like source points to build under /lib/modules/<kver>)
# _KernVmlinuxH: path to vmlinux.h for BTF, located in _buildir
# KernUnameR: Get `uname -r` output of the built kernel
# KernModule: Kernel modules install path, located in %%{buildroot}
# KernDevel: Kernel headers and sources install path, located in %%{buildroot}
%global prepare_buildvar \
	cd %{kernel_tarname} \
	_KernSrc=%{_builddir}/%{rpm_name}-%{kernel_unamer}/%{kernel_tarname} \
	_KernBuild=%{_builddir}/%{rpm_name}-%{kernel_unamer}/%{kernel_unamer}-obj \
	_KernVmlinuxH=%{_builddir}/%{rpm_name}-%{kernel_unamer}/vmlinux.h \
	KernUnameR=%{kernel_unamer} \
	KernModule=%{buildroot}/lib/modules/%{kernel_unamer} \
	KernDevel=%{buildroot}/usr/src/kernels/%{kernel_unamer} \

###### Rpmbuild Prep Stage #####################################################
%prep
%setup -q -c -n %{rpm_name}-%{kernel_unamer}
%{prepare_buildvar}

# TODO: Apply test patch here
:

# Mangle /usr/bin/python shebangs to /usr/bin/python3
# Mangle all Python shebangs to be Python 3 explicitly
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
# This fixes errors such as
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.
# We patch all sources below for which we got a report/error.
find scripts/ tools/ Documentation/ \
	-type f -and \( \
		-name "*.py" -or \( -not -name "*.*" -exec grep -Iq '^#!.*python' {} \; \) \
	\) \
	-exec pathfix.py -i "%{__python3} %{py3_shbang_opts}" -p -n {} \+;

# Make a copy and add suffix for kernel licence to prevent conflict of multi kernel package installation
cp $_KernSrc/COPYING $_KernSrc/COPYING.%{kernel_unamer}

# Update kernel version and suffix info to make uname consistent with RPM version
# PATCHLEVEL inconsistent only happen on first merge window, but patch them all just in case
sed -i "/^VESION/cVERSION = $(echo %{kernel_majver} | cut -d '.' -f 1)" $_KernSrc/Makefile
sed -i "/^PATCHLEVEL/cPATCHLEVEL = $(echo %{kernel_majver} | cut -d '.' -f 2)" $_KernSrc/Makefile
sed -i "/^SUBLEVEL/cSUBLEVEL = $(echo %{kernel_majver} | cut -d '.' -f 3)" $_KernSrc/Makefile

# Patch the kernel to apply uname, the reason we use EXTRAVERSION to control uname
# instead of complete use LOCALVERSION is that, we don't want out scm/rpm version info
# get inherited by random kernels built reusing the config file under /boot, which
# will be confusing.
_KVERSION=$(sed -nE "/^VERSION\s*:?=\s*(.*)/{s/^\s*^VERSION\s*:?=\s*//;h};\${x;p}" $_KernSrc/Makefile)
_KPATCHLEVEL=$(sed -nE "/^PATCHLEVEL\s*:?=\s*(.*)/{s/^\s*^PATCHLEVEL\s*:?=\s*//;h};\${x;p}" $_KernSrc/Makefile)
_KSUBLEVEL=$(sed -nE "/^SUBLEVEL\s*:?=\s*(.*)/{s/^\s*^SUBLEVEL\s*:?=\s*//;h};\${x;p}" $_KernSrc/Makefile)
_KUNAMER_PREFIX=${_KVERSION}.${_KPATCHLEVEL}.${_KSUBLEVEL}
_KEXTRAVERSION=""
_KLOCALVERSION=""

case $KernUnameR in
	$_KUNAMER_PREFIX* )
		_KEXTRAVERSION=$(echo "$KernUnameR" | sed -e "s/^$_KUNAMER_PREFIX//")

		# Anything after "+" belongs to LOCALVERSION, eg, +debug/+minimal marker.
		_KLOCALVERSION=$(echo "$_KEXTRAVERSION" | sed -ne 's/.*\([+].*\)$/\1/p')
		_KEXTRAVERSION=$(echo "$_KEXTRAVERSION" | sed -e 's/[+].*$//')

		# Update Makefile to embed uname
		sed -i "/^EXTRAVERSION/cEXTRAVERSION = $_KEXTRAVERSION" $_KernSrc/Makefile
		# Save LOCALVERSION in .dist.localversion, it will be set to .config after
		# .config is ready in BuildConfig.
		echo "$_KLOCALVERSION" > $_KernSrc/.dist.localversion
		;;
	* )
		echo "FATAL: error: kernel version doesn't match with kernel spec." >&2 && exit 1
		;;
	esac

%if %{with_source}
# take tarball of source code
tar acvf %{name}-%{version}-%{release}.tar.xz *
%endif

###### Rpmbuild Build Stage ####################################################
%build

### Make flags
#
# Those defination have to be defined after %%build macro, %%build macro may change
# some build flags, and we have to inherit these changes.
#
# NOTE: kernel's tools build system doesn't playwell with command line variables, some
# `override` statement will stop working after recursive Makefile `include` call.
# So keep these variables as environment variables so they are available globally,
# `make` will transformed env vars into makefile variable in every iteration.

## Common flags
%global make %{__make} %{_smp_mflags}
%global kernel_make_opts INSTALL_HDR_PATH=%{buildroot}/usr INSTALL_MOD_PATH=%{buildroot} KERNELRELEASE=$KernUnameR
%global tools_make_opts DESTDIR="%{buildroot}" prefix=%{_prefix} lib=%{_lib} PYTHON=%{__python3} INSTALL_ROOT="%{buildroot}"

## Cross compile flags
%if %{with_crossbuild}
%global kernel_make_opts %{kernel_make_opts} CROSS_COMPILE=%{_cross_compile} ARCH=%{kernel_arch}
# make for host tool, reset arch and flags for native host bulid, also limit to 1 job for better stability
%global host_make CFLAGS= LDFLAGS= ARCH= %{make} -j1
%global __strip %{_build_arch}-linux-gnu-strip
%else
%global host_make CFLAGS= LDFLAGS= %{make} -j1
%endif

# Drop host cflags for crossbuild, arch options from build target will break host compiler
%if !%{with_crossbuild}
%global kernel_make_opts %{kernel_make_opts} HOSTCFLAGS="%{?build_cflags}" HOSTLDFLAGS="%{?build_ldflags}"
%endif

## make for kernel
%global kernel_make %{make} %{kernel_make_opts}
## make for tools
%global tools_make CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{make} %{tools_make_opts}
%global perf_make EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 LIBTRACEEVENT_DYNAMIC=1 %{make} %{tools_make_opts}
%global bpftool_make EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" %{make} %{tools_make_opts} $([ -e "$_KernVmlinuxH" ] && echo VMLINUX_H="$_KernVmlinuxH")

### Real make
%{prepare_buildvar}

# Prepare Kernel config
BuildConfig() {
	# Copy mlnx drivers to drivers/thirdparty/release-drivers/mlnx/ dir
	pushd ${_KernSrc}/drivers/thirdparty
	%if %{with_ofed}
		rm -f download-and-copy-drivers.sh; cp -a %{SOURCE3000} ./
		mlnx_tgz_sha256=$(release-drivers/mlnx/get_mlnx_info.sh mlnx_tgz_sha256)
		sha256_tmp=$(sha256sum %{SOURCE3001} | awk '{printf $1}')
		if [[ $sha256_tmp == $mlnx_tgz_sha256 ]]; then
			cp -a %{SOURCE3001} release-drivers/mlnx/
			./copy-drivers.sh without_mlnx
		else
			./copy-drivers.sh
		fi
	%else
		./copy-drivers.sh without_mlnx
	%endif
	popd

	mkdir -p $_KernBuild
	pushd $_KernBuild
	cp $1 .config
	%if "%{?dist}" == ".oc9"
		cat ${_KernSrc}/kernel/configs/oc.config >> .config
	%endif

	[ "$_KernBuild" != "$_KernSrc" ] && echo "include $_KernSrc/Makefile" > Makefile
	[ "$_KernBuild" != "$_KernSrc" ] && cp $_KernSrc/.dist.localversion ./

	# Respect scripts/setlocalversion, avoid it from potentially mucking with our version numbers.
	# Also update LOCALVERSION in .config
	cp .dist.localversion .scmversion
	"$_KernSrc"/scripts/config --file .config --set-str LOCALVERSION "$(cat .dist.localversion)"

	# Ensures build-ids are unique to allow parallel debuginfo
	sed -i -e "s/^CONFIG_BUILD_SALT.*/CONFIG_BUILD_SALT=\"$KernUnameR\"/" .config

	# Call olddefconfig before make all, set all unset config to default value.
	# The packager uses CROSS_COMPILE=scripts/dummy-tools for generating .config
	# so compiler related config are always unset, let's just use defconfig for them for now
	%{kernel_make} olddefconfig

	%if %{with_modsign}
	# Don't use Kbuild's signing, use %%{_module_signer} instead, be compatible with debuginfo and compression
	sed -i -e "s/^CONFIG_MODULE_SIG_ALL=.*/# CONFIG_MODULE_SIG_ALL is not set/" .config
	%else
	# Not signing, unset all signing related configs
	sed -i -e "s/^CONFIG_MODULE_SIG_ALL=.*/# CONFIG_MODULE_SIG_ALL is not set/" .config
	sed -i -e "s/^CONFIG_MODULE_SIG_FORCE=.*/# CONFIG_MODULE_SIG_FORCE is not set/" .config
	sed -i -e "s/^CONFIG_MODULE_SIG=.*/# CONFIG_MODULE_SIG is not set/" .config
	# Lockdown can't work without module sign
	sed -i -e "s/^CONFIG_SECURITY_LOCKDOWN_LSM=.*/# CONFIG_SECURITY_LOCKDOWN_LSM is not set/" .config
	sed -i -e "s/^CONFIG_SECURITY_LOCKDOWN_LSM_EARLY=.*/# CONFIG_SECURITY_LOCKDOWN_LSM_EARLY is not set/" .config
	%endif
	# Don't use kernel's builtin module compression, imcompatible with debuginfo packaging and signing
	sed -i -e "s/^\(CONFIG_DECOMPRESS_.*\)=y/# \1 is not set/" .config
	popd
}

## $1: .config file
BuildKernel() {
	echo "*** Start building kernel $KernUnameR"
	mkdir -p $_KernBuild
	pushd $_KernBuild

	%if %{with_modsign}
	# Call keygen here, if it generate the module keys, it should come before kbuild,
	# so kbuild may avoid regenerate cert keys.
	%{_module_keygen} "$KernUnameR" "$_KernBuild"
	%endif

	# Build vmlinux
	%{kernel_make} all
	# Build modules
	grep -q "CONFIG_MODULES=y" ".config" && %{kernel_make} modules
	# CONFIG_KERNEL_HEADER_TEST generates some extra files in the process of
	# testing so just delete
	find . -name *.h.s -delete

	popd
}

BuildPerf() {
	%{perf_make} -C tools/perf all
	%{perf_make} -C tools/perf man
}

BuildTools() {
	%{tools_make} -C tools/power/cpupower CPUFREQ_BENCH=false DEBUG=false

%ifarch x86_64
	%{tools_make} -C tools/power/cpupower/debug/x86_64 centrino-decode powernow-k8-decode
	%{tools_make} -C tools/power/x86/x86_energy_perf_policy
	%{tools_make} -C tools/power/x86/turbostat
	%{tools_make} -C tools/power/x86/intel-speed-select
%endif

	%{tools_make} -C tools/thermal/tmon/
	%{tools_make} -C tools/iio/
	%{tools_make} -C tools/gpio/
	%{tools_make} -C tools/mm/ slabinfo page_owner_sort
}

BuildBpfTool() {
	echo "*** Building bootstrap bpftool and extrace vmlinux.h"
	if ! [ -s $_KernVmlinuxH ]; then
		# Precompile a minimized bpftool without vmlinux.h, use it to extract vmlinux.h
		# for bootstraping the full feature bpftool
		%{host_make} -C tools/bpf/bpftool/ VMLINUX_BTF= VMLINUX_H=
		# Prefer to extract the vmlinux.h from the vmlinux that were just compiled
		# fallback to use host's vmlinux
		# Skip this if bpftools is too old and doesn't support BTF dump
		if tools/bpf/bpftool/bpftool btf help 2>&1 | grep -q "\bdump\b"; then
			if grep -q "CONFIG_DEBUG_INFO_BTF=y" "$_KernBuild/.config" && [ -s "$_KernBuild/vmlinux" ]; then
				tools/bpf/bpftool/bpftool btf dump file "$_KernBuild/vmlinux" format c > $_KernVmlinuxH
			else
				if [ -e /sys/kernel/btf/vmlinux ]; then
					tools/bpf/bpftool/bpftool btf dump file /sys/kernel/btf/vmlinux format c > $_KernVmlinuxH
				fi
			fi
		fi
		%{host_make} -C tools/bpf/bpftool/ clean
	fi

	echo "*** Building bpftool"
	%{bpftool_make} -C tools/bpf/bpftool
}

%if %{with_core}
%ifnarch x86_64 aarch64 loongarch64
{error:unsupported arch}
%endif
%ifarch x86_64
BuildConfig %{SOURCE1000}
%endif
%ifarch aarch64
BuildConfig %{SOURCE1001}
%endif
%ifarch loongarch64
BuildConfig %{SOURCE1002}
%endif
BuildKernel
%endif

%if %{with_perf}
BuildPerf
%endif

%if %{with_tools}
BuildTools
%endif

%if %{with_bpftool}
BuildBpfTool
%endif

###### Rpmbuild Install Stage ##################################################
%install
%{prepare_buildvar}

InstKernelBasic() {
	####### Basic environment ##################
	# prepare and pushd into the kernel module top dir
	mkdir -p $KernModule
	pushd $KernModule

	####### modules_install ##################
	pushd $_KernBuild
	# Override $(mod-fw) because we don't want it to install any firmware
	# we'll get it from the linux-firmware package and we don't want conflicts
	grep -q "CONFIG_MODULES=y" ".config" && %{kernel_make} mod-fw= modules_install
	# Check again, don't package firmware, use linux-firmware rpm instead
	rm -rf %{buildroot}/lib/firmware
	popd

	####### Prepare kernel modules files for packaging ################
	# Don't package depmod files, they should be auto generated by depmod at rpm -i
	rm -f modules.{alias,alias.bin,builtin.alias.bin,builtin.bin} \
		modules.{dep,dep.bin,devname,softdep,symbols,symbols.bin}

	# Process kernel modules
	find . -name "*.ko" -type f | \
	while read -r _kmodule; do
		# Mark it executable so strip and find-debuginfo can see it
		chmod u+x "$_kmodule"

		# Detect missing or incorrect license tags
		modinfo "$_kmodule" -l | grep -E -qv \
			'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' && \
			echo "Module $_kmodule has incorrect license." >&2 && exit 1

		# Collect module symbol reference info for later usage
		case "$kmodule" in */drivers/*) nm -upA "$_kmodule" ;;
		esac | sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' >> drivers.undef
	done || exit $?

	# Generate a list of modules for block and networking.
	collect_modules_list() {
		sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
			LC_ALL=C sort -u > $KernModule/modules.$1
		if [ ! -z "$3" ]; then
			sed -r -e "/^($3)\$/d" -i $KernModule/modules.$1
		fi
	}

	collect_modules_list networking \
		'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
	collect_modules_list block \
		'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' \
		'pktcdvd.ko|dm-mod.ko'
	collect_modules_list drm \
		'drm_open|drm_init'
	collect_modules_list modesetting \
		'drm_crtc_init'
	# Finish preparing the kernel module files

	###### Install kernel core components #############################
	mkdir -p %{buildroot}/boot
	install -m 644 $_KernBuild/.config config
	install -m 644 $_KernBuild/.config %{buildroot}/boot/config-$KernUnameR
	install -m 644 $_KernBuild/System.map System.map
	install -m 644 $_KernBuild/System.map %{buildroot}/boot/System.map-$KernUnameR

	# Install RUE module probe file
	mkdir -p %{buildroot}%{_modulesloaddir}
	install -m 644 %{SOURCE40} %{buildroot}%{_modulesloaddir}/rue.conf

	# NOTE: If we need to sign the vmlinuz, this is the place to do it.
	%ifarch aarch64
	INSTALL_DTB_ARCH_PATH=$_KernBuild/arch/arm64/boot/dts
	install -m 644 $_KernBuild/arch/arm64/boot/Image vmlinuz
	%endif

	%ifarch riscv64
	INSTALL_DTB_ARCH_PATH=$_KernBuild/arch/riscv/boot/dts
	install -m 644 $_KernBuild/arch/riscv/boot/Image vmlinuz
	%endif

	%ifarch x86_64
	INSTALL_DTB_ARCH_PATH=
	install -m 644 $_KernBuild/arch/x86/boot/bzImage vmlinuz
	%endif

	%ifarch loongarch64
	INSTALL_DTB_ARCH_PATH=
	strip -s $_KernBuild/vmlinux -o $_KernBuild/vmlinux.elf
	install -m 644 $_KernBuild/vmlinux.elf vmlinuz
	%endif

	# Install Arch DTB if exists
	if [ -n "$INSTALL_DTB_ARCH_PATH" ]; then
		pushd $INSTALL_DTB_ARCH_PATH || :
		find . -name "*.dtb" | while read -r dtb; do
			mkdir -p %{buildroot}/boot/dtb-$KernUnameR/$(dirname $dtb)
			cp $dtb %{buildroot}/boot/dtb-$KernUnameR/$(dirname $dtb)
		done
		popd
	fi

	%ifarch x86_64 aarch64
	# Sign the vmlinuz for supporting secure boot feature only when
	# external efi secure boot signer provided.
	%if 0%{?_sb_signer:1}
	%{_sb_signer vmlinuz vmlinuz.signed}
	mv vmlinuz.signed vmlinuz
	%endif
	%endif

	# Install Arch vmlinuz
	install -m 644 vmlinuz %{buildroot}/boot/vmlinuz-$KernUnameR

	sha512hmac %{buildroot}/boot/vmlinuz-$KernUnameR | sed -e "s,%{buildroot},," > .vmlinuz.hmac
	cp .vmlinuz.hmac %{buildroot}/boot/.vmlinuz-$KernUnameR.hmac

	###### Doc and certs #############################
	mkdir -p %{buildroot}/%{_datadir}/doc/kernel-keys/$KernUnameR
	if [ -e $_KernBuild/certs/signing_key.x509 ]; then
		install -m 0644 $_KernBuild/certs/signing_key.x509 %{buildroot}/%{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.cer
%if %{with_keypkg}
		if [ -e $_KernBuild/certs/signing_key.pem ]; then
			install -m 0644 $_KernBuild/certs/signing_key.pem %{buildroot}/%{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.pem
		fi
%else
		echo "# This is a dummy file as private key is not exported." > %{buildroot}/%{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.pem
%endif
	fi

	###### kABI checking and packaging #############################
	# Always create the kABI metadata for use in packaging
	echo "**** GENERATING kernel ABI metadata ****"
	gzip -c9 < $_KernBuild/Module.symvers > symvers.gz
	cp symvers.gz %{buildroot}/boot/symvers-$KernUnameR.gz

	###### End of installing kernel modules and core
	popd
}

CheckKernelABI() {
	echo "**** kABI checking is enabled. ****"
	if ! [ -s "$1" ]; then
		echo "**** But cannot find reference Module.kabi file. ****"
	else
		cp $1 %{buildroot}/Module.kabi
		%{SOURCE30} -k %{buildroot}/Module.kabi -s $_KernBuild/Module.symvers || exit 1
		rm %{buildroot}/Module.kabi
	fi
}

InstKernelDevel() {
	###### Install kernel-devel package ###############################
	### TODO: need tidy up
	### Save the headers/makefiles etc for building modules against.
	# This all looks scary, but the end result is supposed to be:
	# * all arch relevant include/ files
	# * all Makefile/Kconfig files
	# * all script/ files

	# `modules_install` will symlink build to $_KernBuild, and source to $_KernSrc, remove the symlinks first
	rm -rf $KernModule/{build,source}
	mkdir -p $KernModule/{extra,updates,weak-updates}

	# Symlink $KernDevel to kernel module build path
	ln -sf /usr/src/kernels/$KernUnameR $KernModule/build
	ln -sf /usr/src/kernels/$KernUnameR $KernModule/source

	# Start installing kernel devel files
	mkdir -p $KernDevel
	pushd $KernDevel

	# First copy everything
	(cd $_KernSrc; cp --parents $(find . -type f -name "Makefile*" -o -name "Kconfig*" -o -name "Kbuild*") $KernDevel/)
	# Copy built config and sym files
	cp $_KernBuild/Module.symvers .
	cp $_KernBuild/System.map .
	cp $_KernBuild/.config .
	if [ -s $_KernBuild/Module.markers ]; then
		cp $_KernBuild/Module.markers .
	fi

	# We may want to keep Documentation, I got complain from users of missing Makefile
	# of Documentation when building custom module with document.
	# rm -rf build/Documentation
	# Script files
	rm -rf scripts
	cp -a $_KernSrc/scripts .
	cp -a $_KernBuild/scripts .

	# Include files
	rm -rf include
	cp -a $_KernSrc/include .
	cp -a $_KernBuild/include/config include/
	cp -a $_KernBuild/include/generated include/

	# SELinux
	mkdir -p security/selinux/
	cp -a $_KernSrc/security/selinux/include security/selinux/

	# Set arch name
	Arch=$(head -4 $_KernBuild/.config | sed -ne "s/.*Linux\/\([^\ ]*\).*/\1/p" | sed -e "s/x86_64/x86/" )

	# Arch include
	mkdir -p arch/$Arch
	cp -a $_KernSrc/arch/$Arch/include arch/$Arch/
	cp -a $_KernBuild/arch/$Arch/include arch/$Arch/

	if [ -d $_KernBuild/arch/$Arch/scripts ]; then
		cp -a $_KernBuild/arch/$Arch/scripts arch/$Arch/ || :
	fi

	# Kernel module build dependency
	if [ -f $_KernBuild/tools/objtool/objtool ]; then
		cp -a $_KernBuild/tools/objtool/objtool tools/objtool/ || :
	fi

	if [ -f $_KernBuild/tools/objtool/fixdep ]; then
		cp -a $_KernBuild/tools/objtool/fixdep tools/objtool/ || :
	fi

	cp -a $_KernSrc/arch/$Arch/*lds arch/$Arch/ &>/dev/null || :
	cp -a $_KernBuild/arch/$Arch/*lds arch/$Arch/ &>/dev/null || :

	mkdir -p arch/$Arch/kernel
	if [ -f $_KernSrc/arch/$Arch/kernel/module.lds ]; then
		cp -a $_KernSrc/arch/$Arch/kernel/module.lds arch/$Arch/kernel/
	fi
	if [ -f $_KernBuild/arch/$Arch/kernel/module.lds ]; then
		cp -a $_KernBuild/arch/$Arch/kernel/module.lds arch/$Arch/kernel/
	fi

	# Symlink include/asm-$Arch for better compatibility with some old system
	ln -sfr arch/$Arch include/asm-$Arch

	# Make sure the Makefile and version.h have a matching timestamp so that
	# external modules can be built
	touch -r Makefile include/generated/uapi/linux/version.h
	touch -r .config include/linux/autoconf.h

	# If we have with_modsign, the key should be installed under _datadir, make a symlink here:
	if [ -e %{buildroot}/%{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.cer ]; then
		mkdir -p certs
		ln -sf %{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.cer signing_key.x509
		ln -sf %{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.cer certs/signing_key.x509
		ln -sf %{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.pem signing_key.pem
		ln -sf %{_datadir}/doc/kernel-keys/$KernUnameR/kernel-signing-ca.pem certs/signing_key.pem
	fi


	# Delete obj files
	find . -iname "*.o" -o -iname "*.cmd" -delete

	# Done
	popd
}

InstKernelHeaders () {
	%{kernel_make} headers_install
	find %{buildroot}/usr/include \
		\( -name .install -o -name .check -o \
		-name ..install.cmd -o -name ..check.cmd \) -delete
}

InstPerf () {
	%{perf_make} -C tools/perf install-bin install-python_ext install-man

	# remove the 'trace' symlink.
	rm -f %{buildroot}%{_bindir}/trace

	# Be just like CentOS:
	# remove any tracevent files, eg. its plugins still gets built and installed,
	# even if we build against system's libtracevent during perf build (by setting
	# LIBTRACEEVENT_DYNAMIC=1 above in perf_make macro). Those files should already
	# ship with libtraceevent package.
	rm -rf %{buildroot}%{_libdir}/traceevent
}

InstTools() {
	%{tools_make} -C tools/power/cpupower DESTDIR=%{buildroot} libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
	rm -f %{buildroot}%{_libdir}/*.{a,la}
	%find_lang cpupower
	mv cpupower.lang ../

%ifarch x86_64
	pushd tools/power/cpupower/debug/x86_64
	install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
	install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
	popd
%endif

	chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
	mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
	install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
	install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower

%ifarch x86_64
	mkdir -p %{buildroot}%{_mandir}/man8
	%{tools_make} -C tools/power/x86/x86_energy_perf_policy DESTDIR=%{buildroot} install
	%{tools_make} -C tools/power/x86/turbostat DESTDIR=%{buildroot} install
	%{tools_make} -C tools/power/x86/intel-speed-select DESTDIR=%{buildroot} install
%endif

	%{tools_make} -C tools/thermal/tmon install
	%{tools_make} -C tools/iio install
	%{tools_make} -C tools/gpio install

	pushd tools/mm/
	install -m755 slabinfo %{buildroot}%{_bindir}/slabinfo
	install -m755 page_owner_sort %{buildroot}%{_bindir}/page_owner_sort
	popd
	# with_tools
}

InstBpfTool () {
	%{bpftool_make} -C tools/bpf/bpftool bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
}

CollectKernelFile() {
	###### Collect file list #########################################
	pushd %{buildroot}

	# Collect all module files, dtb files, and dirs
	{
		# Install certs in core package if found
		# Echo a dir so it don't fail as a empty list if signing is disabled.
		echo "%%dir %{_datadir}/doc/kernel-keys"
		if [ -e "%{buildroot}/%{_datadir}/doc/kernel-keys/%{kernel_unamer}/kernel-signing-ca.cer" ]; then
			echo %{_datadir}/doc/kernel-keys/%{kernel_unamer}/kernel-signing-ca.cer
		fi

		find lib/modules/$KernUnameR/ boot/dtb-$KernUnameR/ -not -type d -printf '/%%p\n' 2>/dev/null
		find lib/modules/$KernUnameR/ boot/dtb-$KernUnameR/ -type d -printf '%%%%dir /%%p\n' 2>/dev/null
	} | sort -u > core.list

	# Install private key in cert package if found
	# Echo a dir so it don't fail as a empty list if signing is disabled.
	echo "%%dir %{_datadir}/doc/kernel-keys" >> signing-keys.list
	if [ -e "%{buildroot}/%{_datadir}/doc/kernel-keys/%{kernel_unamer}/kernel-signing-ca.pem" ]; then
%if %{with_keypkg}
		echo %{_datadir}/doc/kernel-keys/%{kernel_unamer}/kernel-signing-ca.pem >> signing-keys.list
%else
		# Dummy key goes to kernel-core pkg, kernel-keys dir created above
		echo %{_datadir}/doc/kernel-keys/%{kernel_unamer}/kernel-signing-ca.pem >> core.list
%endif
	fi

	# Do module splitting, filter-modules.sh will generate a list of
	# modules to be split into external module package
	# Rest of the modules stay in core package
	%SOURCE10 "%{buildroot}" "$KernUnameR" "%{_target_cpu}" "$_KernBuild/System.map" non-core-modules >> modules.list || exit $?

	comm -23 core.list modules.list > core.list.tmp
	mv core.list.tmp core.list

	popd

	# Make these file list usable in rpm build dir
	mv %{buildroot}/*.list ../
}

## Build MLNX OFED
BuildInstMLNXOFED() {
	inst_mod() {
		src_mod=$1
		src_mod_name=$(basename "$src_mod")
		dest=""

		# Replace old module
		for mod in $(find $KernModule -name "*$src_mod_name*"); do
			echo "MLNX_OFED: REPLACING: kernel module $mod"
			dest=$(dirname "$mod")
			rm -f "$mod"
		done

		# Install new module
		if [ ! -d "$dest" ]; then
			echo "MLNX_OFED: NEW: kernel module $dest/$mod"
			dest="$KernModule/kernel/drivers/ofed_addon"
			mkdir -p $dest
		fi

		cp -f "$src_mod" "$dest/"
	}

	handle_rpm() {
		rm -rf extracted
		mkdir -p extracted && pushd extracted

		rpm2cpio $1 | cpio -id
		find . -name "*.ko" -or -name "*.ko.xz" | while read -r mod; do
			inst_mod "$mod"
		done
		# find . -name "*.debug" | while read -r mod; do
		#       inst_debuginfo "$mod"
		# done

		popd
	}

	pushd drivers/thirdparty/release-drivers/mlnx
	MLNX_OFED_VERSION=$(./get_mlnx_info.sh mlnx_version) ; 	MLNX_OFED_TGZ_NAME=$(./get_mlnx_info.sh mlnx_tgz_name)
	tar -xzvf $MLNX_OFED_TGZ_NAME
	pushd MLNX_OFED_LINUX-${MLNX_OFED_VERSION}-rhel9.4-x86_64
	pushd src
	echo "tar -xzvf MLNX_OFED_SRC-${MLNX_OFED_VERSION}.tgz"
	tar -xzvf MLNX_OFED_SRC-${MLNX_OFED_VERSION}.tgz
	pushd MLNX_OFED_SRC-${MLNX_OFED_VERSION}

	# Fix TS4 compile errors by enabling LTO. So, disable LTO,  and enabling -fPIE.
	DISTRO=$(echo "%{?dist}" | sed "s/\.//g")
	if [[ "${DISTRO}" != "tl3" ]]; then
		## "${DISTRO}" == "tl4" or "${DISTRO}" == "oc9"
		sed -i "s/rpmbuild --rebuild/rpmbuild --define 'rhel 9' --define '_lto_cflags -fno-lto' --define '_hardened_cflags -fPIE' --rebuild/g" ./install.pl
	fi
	# Unset $HOME, when doing koji build, koji insert special macros into ~/.rpmmacros that will break MLNX installer:
	# Koji sets _rpmfilename  %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm,
	# But the installer assumes "_rpmfilename %{_build_name_fmt}" so it will fail to find the built rpm.
	HOME= ./install.pl --build-only --kernel-only --without-depcheck --distro $DISTRO \
	--kernel $KernUnameR --kernel-sources $KernDevel \
	--without-mlx5_fpga_tools --without-mlnx-rdma-rxe --without-mlnx-nfsrdma \
	--without-mlnx-nvme --without-isert --without-iser --without-srp --without-rshim --without-mdev \
	--disable-kmp

	# get all kernel module rpms that were built against target kernel
	find RPMS -name "*.rpm" -type f | while read -r pkg; do
		if rpm -qlp $pkg | grep "\.ko"; then
			handle_rpm "$(realpath $pkg)"
		fi
	done

	popd ## MLNX_OFED_SRC*
	rm -rf MLNX_OFED_SRC-${MLNX_OFED_VERSION}
	popd ## src

	echo "Begin to build $MLNX_OFED_TGZ_NAME"
	## Now, we in MLNX_OFED_LINUX-* dir!
	%if %{with_modsign}
	%ifarch x86_64
	# The purpose is to reorgnise the mlnx tgz files for our TencentOS
	# Build the full packages of mlnx ofed.
	# change to build/
	tmp=%{buildroot}/tmp
	mkdir $tmp
	tmppath=$(realpath $tmp)

	# We need to jump the root privilege because we'll assign a normal tmpdir
	sed -i 's/$UID -ne 0/! -z $JUMP_ROOT/g' mlnx_add_kernel_support.sh
	if [ "${DISTRO}" != "tl3" ]; then
		sed -i '/# Check for needed packages by install.pl/a sed -i "s/rpmbuild --rebuild/rpmbuild --define '\''rhel 9'\'' --define '\''_lto_cflags -fno-lto'\'' --define '\''_hardened_cflags -fPIE'\'' --rebuild/g" ${ofed}/install.pl' mlnx_add_kernel_support.sh
	fi
	sed -i 's/\(ex ${ofed}\/install\.pl\)/\1 --without-mlnx-nvme/g' mlnx_add_kernel_support.sh

	# unset home
	if [[ "${DISTRO}" != "tl3" ]]; then
		## "${DISTRO}" == "tl4" or "${DISTRO}" == "oc9"
		HOME= ./mlnx_add_kernel_support.sh -m ./ --distro rhel9.4 --make-tgz -y \
			--kernel $KernUnameR --kernel-sources $KernDevel --skip-repo --tmpdir $tmppath
	else
		## "${DISTRO}" == "tl3"
		HOME= ./mlnx_add_kernel_support.sh -m ./ --make-tgz -y \
			--kernel $KernUnameR --kernel-sources $KernDevel --skip-repo --tmpdir $tmppath
	fi

	# Prepare first
	pushd $tmppath
	tar -xzvf MLNX_OFED_LINUX-*
	touch ko.location
	# compatible with module signer script
	signed=ko_files/lib/modules/$KernUnameR
	mkdir -p workdir $signed

	# Extract all the rpms containing ko files to workdir
	rpm_rp=$(realpath MLNX_OFED_LINUX-*/RPMS)
	pushd workdir
	find $rpm_rp -name "*.rpm" -type f | while read -r pkg; do
		if rpm -qlp $pkg | grep "\.ko$" | grep "6.6" >> ../ko.location; then
			rpm_bn=$(basename $pkg)
			mkdir $rpm_bn && pushd $rpm_bn
			rpm2cpio $rpm_rp/$rpm_bn | cpio -id
			popd ## $rpm_bn
		fi
	done
	popd ## workdir

	# Start collecting all the ko files
	find workdir/ -name "*.ko" | while read -r mod; do
		mv $mod $signed/
	done

	# Now we're about to sign them.
	%{_module_signer} "$KernUnameR" "$_KernBuild" "ko_files" x509 || exit $?

	# Compress it into a new tgz file.
	if [[ "${DISTRO}" != "tl3" ]]; then
		## "${DISTRO}" == "tl4" or "${DISTRO}" == "oc9"
		mlnxfulname=$(basename %{SOURCE3001})
		mlnxrelease=${mlnxfulname%.*}
	else
		## "${DISTRO}" == "tl3"
		mlnxrelease=MLNX_OFED_LINUX-${MLNX_OFED_VERSION}-tencent-x86_64
	fi
	mv $mlnxrelease-ext  $mlnxrelease-ext.$KernUnameR/
	# Turn it back to the original file
	sed -i 's/! -z $JUMP_ROOT/$UID -ne 0/g' $mlnxrelease-ext.$KernUnameR/mlnx_add_kernel_support.sh
	cp -r $signed $mlnxrelease-ext.$KernUnameR/ko_files.signed
	sed -i "s/KERNELMODULE_REPLACE/$KernUnameR/g" %{SOURCE3002}
	cp -r ko.location %{SOURCE3002} $mlnxrelease-ext.$KernUnameR/
	tar -zcvf $mlnxrelease-ext.$KernUnameR.tgz $mlnxrelease-ext.$KernUnameR
	mkdir %{buildroot}/mlnx/
	install -m 755 $mlnxrelease-ext.$KernUnameR.tgz %{buildroot}/mlnx/

	popd ## $tmppath
	rm -rf $tmppath
	%endif
	%endif

	popd ## MLNX_OFED_LINUX-${MLNX_OFED_VERSION}-rhel9.4-x86_64
	rm -rf MLNX_OFED_LINUX-*
	popd ## drivers/thirdparty/release-drivers/mlnx
}

###### Start Kernel Install

%if %{with_core}
InstKernelBasic

%if %{with_kabichk}
%ifnarch x86_64 aarch64 loongarch64
{error:unsupported arch}
%endif
%ifarch x86_64
CheckKernelABI %{SOURCE1200}
%endif
%ifarch aarch64
CheckKernelABI %{SOURCE1201}
%endif
%ifarch loongarch64
CheckKernelABI %{SOURCE1202}
%endif
%endif

InstKernelDevel
%endif

%if %{with_headers}
InstKernelHeaders
%endif

%if %{with_ofed}
# MLNXOFED driver's Makefile doesn't support cross build.
%if !%{with_crossbuild}
BuildInstMLNXOFED
%endif
%endif

%if %{with_perf}
InstPerf
%endif

%if %{with_tools}
InstTools
%endif

%if %{with_bpftool}
InstBpfTool
%endif

%if %{with_core}
CollectKernelFile
%endif

###### Debuginfo ###############################################################
%if %{with_debuginfo}

###### Kernel core debuginfo #######
%if %{with_core}
mkdir -p %{buildroot}%{debuginfo_dir}/lib/modules/$KernUnameR
cp -rpf $_KernBuild/vmlinux %{buildroot}%{debuginfo_dir}/lib/modules/$KernUnameR/vmlinux
ln -sf %{debuginfo_dir}/lib/modules/$KernUnameR/vmlinux %{buildroot}/boot/vmlinux-$KernUnameR
%endif
#with_core

# All binary installation are done here, so run __debug_install_post, then undefine it.
# This triggers find-debuginfo.sh, undefine prevents it from being triggered again
# in post %%install. we do this here because we need to compress and sign modules
# after the debuginfo extraction.
%__debug_install_post

# Delete the debuginfo for kernel-devel files
rm -rf %{buildroot}%{debuginfo_dir}/usr/src

%undefine __debug_install_post
%global __debug_install_post %{nil}

###### Finally, module sign and compress ######
%if %{with_modsign} && %{with_core}
### Sign after debuginfo extration, extraction breaks signature
%{_module_signer} "$KernUnameR" "$_KernBuild" "%{buildroot}" || exit $?
%endif

### Compression after signing, compressed module can't be signed
# Spawn at most 16 workers, at least 2 workers, each worker compress 4 files
NPROC=$(nproc --all)
[ "$NPROC" ] || NPROC=2
[ "$NPROC" -gt 16 ] && NPROC=16
find "$KernModule" -type f -name '*.ko' -print0 | xargs -0r -P${NPROC} -n4 xz -T1;

### Change module path in file lists
for list in ../*.list; do
	sed -i -e 's/\.ko$/\.ko.xz/' $list
done

%endif
#with_debuginfo

%if %{with_source}
# copy source code tarball to installing directory
mkdir -p %{buildroot}%{_usrsrc}/%{name}
cp -f %{name}-%{version}-%{release}.tar.xz  %{buildroot}%{_usrsrc}/%{name}/
%endif

###### RPM scriptslets #########################################################
### Core package
# Pre
%if %{with_core}
%pre core
# Best effort try to avoid installing with wrong arch
if command -v uname > /dev/null; then
	system_arch=$(uname -m)
	if [ %{_target_cpu} != $system_arch ]; then
		echo "WARN: This kernel is built for %{_target_cpu}. but your system is $system_arch." > /dev/stderr
	fi
fi

%post core
touch %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.installing_core

%posttrans core
# Weak modules
if command -v weak-modules > /dev/null; then
	weak-modules --add-kernel %{kernel_unamer} || exit $?
fi
# Boot entry and depmod files
if command -v kernel-install > /dev/null; then
	kernel-install add %{kernel_unamer} /lib/modules/%{kernel_unamer}/vmlinuz
elif command -v new-kernel-pkg > /dev/null; then
	new-kernel-pkg --package kernel --install %{kernel_unamer} --kernel-args="crashkernel=512M-12G:128M,12G-64G:256M,64G-128G:512M,128G-:768M" --make-default || exit $?
	new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{kernel_unamer} || exit $?
else
	echo "NOTICE: No available kernel install handler found. Please make sure boot loader and initramfs are properly configured after the installation." > /dev/stderr
fi
# Just in case kernel-install didn't depmod
depmod -A %{kernel_unamer}
# Core install done
rm -f %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.installing_core

# XXX: Workaround for TLinux 2.x, TLinux 2.x has broken SELinux rule, enabling SELinux will cause boot failure.
%if "%{?dist}" == ".tl2"
if command -v grubby > /dev/null; then
	grubby --update-kernel /boot/vmlinuz-%{kernel_unamer} --args selinux=0
else
	echo "NOTICE: TL2 detected, but grubby is missing, please set selinux=0 for new installed kernel manually, or it may fail to boot due to broken SELinux rule." > /dev/stderr
fi
%endif

# Some system still expect us to setup vmlinuz manually, vmlinuz is listed
# as ghost file to detect such systems
if [ ! -e /boot/vmlinuz-%{kernel_unamer} ]; then
	cp /lib/modules/%{kernel_unamer}/vmlinuz /boot/vmlinuz-%{kernel_unamer}
	cp /lib/modules/%{kernel_unamer}/config /boot/config-%{kernel_unamer}
	cp /lib/modules/%{kernel_unamer}/System.map /boot/System.map-%{kernel_unamer}
	ln -srf /boot/vmlinuz-%{kernel_unamer} /boot/vmlinuz
	ln -srf /boot/config-%{kernel_unamer} /boot/config
	ln -srf /boot/System.map-%{kernel_unamer} /boot/System.map
fi

%preun core
# Boot entry and depmod files
if command -v kernel-install > /dev/null; then
	kernel-install remove %{kernel_unamer} /lib/modules/%{kernel_unamer}/vmlinuz || exit $?
elif command -v new-kernel-pkg > /dev/null; then
	/sbin/new-kernel-pkg --rminitrd --dracut --remove %{kernel_unamer}
else
	echo "NOTICE: No available kernel uninstall handler found. Please make sure boot loader and initramfs are properly cleared after the uninstallation." > /dev/stderr
fi

# Weak modules
if command -v weak-modules > /dev/null; then
	weak-modules --remove-kernel %{kernel_unamer} || exit $?
fi

### Module package
%pre modules
# In TS private release, kernel command line in /etc/default/grub will add "tk_private=1".
# When install TS private release, do not need install "usb-storage nouveau cfg80211" into initramfs.
tk_private_val=1
grep -q "tk_private=1" /etc/default/grub 2>/dev/null || tk_private_val=0
if (( $tk_private_val == 1 )); then echo "omit_dracutmodules+=\" usb-storage nouveau cfg80211 \"" >> /etc/dracut.conf ; fi

%post modules
depmod -a %{kernel_unamer}
if [ ! -f %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.installing_core ]; then
	touch %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.need_to_run_dracut
fi
# Because /lib link to /usr/lib, /lib/modules is the same to /usr/lib/modules.
# So, in TS private release, we only delete usb-storage and nouveau module in /usr/lib/modules dir.
rm_public_ko=1
grep -q "omit_dracutmodules+=\" usb-storage nouveau cfg80211 \"" /etc/dracut.conf 2>/dev/null || rm_public_ko=0
if (( $rm_public_ko == 1 )); then
	sed -i '/omit_dracutmodules+=\" usb-storage nouveau cfg80211 \"/d' /etc/dracut.conf
	rm -f /usr/lib/modules/%{kernel_unamer}/kernel/drivers/usb/storage/*
	rm -f /usr/lib/modules/%{kernel_unamer}/kernel/drivers/gpu/drm/nouveau/*
	rm -f /usr/lib/modules/%{kernel_unamer}/kernel/net/wireless/*
fi

%posttrans modules
if [ -f %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.need_to_run_dracut ]; then\
	dracut -f --kver "%{kernel_unamer}"
	rm -f %{_localstatedir}/lib/rpm-state/%{name}-%{version}-%{version}%{?dist}.need_to_run_dracut
fi

%postun modules
depmod -a %{kernel_unamer}

### Devel package
%post devel
if [ -f /etc/sysconfig/kernel ]; then
	. /etc/sysconfig/kernel || exit $?
fi
# This hardlink merges same devel files across different kernel packages
if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ]; then
	(cd /usr/src/kernels/%{kernel_unamer} && /usr/bin/find . -type f | while read -r f; do
		hardlink /usr/src/kernels/*/$f $f > /dev/null
	done)
fi
%endif

### kernel-tools package
%if %{with_tools}
%post -n kernel-tools-libs
/sbin/ldconfig

%postun -n kernel-tools-libs
/sbin/ldconfig
%endif

%if %{with_source}
%files source
%{_usrsrc}/%{name}/%{name}-%{version}-%{release}.tar.xz
%endif

###### Rpmbuild packaging file list ############################################
### empty meta-package
%if %{with_core}
%files
%{nil}

%files core -f core.list
%defattr(-,root,root)
# Mark files as ghost in case rewritten after install (eg. by kernel-install script)
%ghost /boot/vmlinuz-%{kernel_unamer}
%ghost /boot/.vmlinuz-%{kernel_unamer}.hmac
/boot/System.map-%{kernel_unamer}
/boot/config-%{kernel_unamer}
/boot/symvers-%{kernel_unamer}.gz
# RUE module probe file
%config(noreplace) %{_modulesloaddir}/rue.conf
# Initramfs will be generated after install
%ghost /boot/initramfs-%{kernel_unamer}.img
%ghost /boot/initramfs-%{kernel_unamer}kdump.img
# Make depmod files ghost files of the core package
%dir /lib/modules/%{kernel_unamer}
%ghost /lib/modules/%{kernel_unamer}/modules.alias
%ghost /lib/modules/%{kernel_unamer}/modules.alias.bin
%ghost /lib/modules/%{kernel_unamer}/modules.builtin.bin
%ghost /lib/modules/%{kernel_unamer}/modules.builtin.alias.bin
%ghost /lib/modules/%{kernel_unamer}/modules.dep
%ghost /lib/modules/%{kernel_unamer}/modules.dep.bin
%ghost /lib/modules/%{kernel_unamer}/modules.devname
%ghost /lib/modules/%{kernel_unamer}/modules.softdep
%ghost /lib/modules/%{kernel_unamer}/modules.symbols
%ghost /lib/modules/%{kernel_unamer}/modules.symbols.bin
%{!?_licensedir:%global license %%doc}
%license %{kernel_tarname}/COPYING.%{kernel_unamer}

%files modules -f modules.list
%defattr(-,root,root)

%if %{with_keypkg}
%files signing-keys -f signing-keys.list
%defattr(-,root,root)
%endif

%files devel
%defattr(-,root,root)
/usr/src/kernels/%{kernel_unamer}

%if %{with_debuginfo}
%files debuginfo -f debuginfo.list
%defattr(-,root,root)
/boot/vmlinux-%{kernel_unamer}
%endif
# with_core
%endif

%if %{with_debuginfo}
%files debuginfo-common -f debugfiles.list
%defattr(-,root,root)
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf*
%{_libdir}/libperf-jvmti.so
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%{_docdir}/perf-tip/tips.txt
# TODO: Missing doc?
# %%doc linux-%%{kernel_unamer}/tools/perf/Documentation/examples.txt

%files -n python3-perf
%defattr(-,root,root)
%{python3_sitearch}/*

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%files -f python3-perf-debuginfo.list -n python3-perf-debuginfo
%defattr(-,root,root)
%endif
# with_perf
%endif

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-,root,root)
%{_bindir}/cpupower
%{_datadir}/bash-completion/completions/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%{_bindir}/intel-speed-select
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-*
%{_bindir}/page_owner_sort
%{_bindir}/slabinfo

%files -n kernel-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_libdir}/libcpupower.so.*

%files -n kernel-tools-libs-devel
%defattr(-,root,root)
%{_includedir}/cpufreq.h

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif
# with_tools
%endif

%if %{with_bpftool}
%files -n bpftool
%defattr(-,root,root)
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool.8.*
%{_mandir}/man8/bpftool-*.8.*

%if %{with_debuginfo}
%files -f bpftool-debuginfo.list -n bpftool-debuginfo
%defattr(-,root,root)
%endif
# with_bpftool
%endif

%if %{with_ofed}
%ifarch x86_64
%files -n mlnx-ofed-dist
%if "%{?dist}" != ".tl3"
/mlnx/MLNX_OFED_LINUX-23.10-3.2.2.0-rhel9.4-x86_64-ext.%{kernel_unamer}.tgz
%else
/mlnx/MLNX_OFED_LINUX-23.10-3.2.2.0-tencent-x86_64-ext.%{kernel_unamer}.tgz
%endif
%endif
%endif

###### Changelog ###############################################################
%changelog
* Mon Mar 24 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.80-29
- aegis: disable aegis config, default n

* Tue Mar 18 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.80-28
- dist: restrict secure boot signing to x86_64 and aarch64
- dist: disable mlnx outtree driver

* Tue Mar 18 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.80-27
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !331 [linux-6.6/devel][bugfix]: LoongArch: config: enable pci host controller fdt driver
- LoongArch: config: enable pci host controller fdt driver
- dist: only generate kernel-source rpm when build x86_64
- Merge branch 'honglin/release' into 'release' (merge request !369)
- rue/net: fix the association between sock and cgroup
- Merge branch 'aurelianliu/release_0305' into 'release' (merge request !359)
- epoll: introduce min_wait_time
- dist: do not build kernel-source rpm in debug version
- Merge branch OCK linux-6.6/devel into TK5 release branch
- !327 added source subpackage for dist/rpm scripts
- added source subpackage for dist/rpm scripts
- !330 [linux-6.6/devel][bugfix]: LoongArch: Disable CONFIG_RT_GROUP_SCHED to prevent cgroup2 issues
- LoongArch: Disable CONFIG_RT_GROUP_SCHED to prevent cgroup2 issues
- !326 Backport PRM update and bugfixes up to v6.14
- ACPI: PRM: Add PRM handler direct call support
- ACPI: PRM: Annotate struct prm_module_info with __counted_by
- !325 [Intel-SIG] Backport SierreForest MAXPHYSADDR support
- KVM: selftests: x86: Prioritize getting max_gfn from GuestPhysBits
- KVM: x86: Advertise max mappable GPA in CPUID.0x80000008.GuestPhysBits
- !323 [Intel-SIG] 6.6: x86/cpu: KVM: Advertise CPUIDs for new instructions in Clearwater Forest (CWF)
- x86: KVM: Advertise CPUIDs for new instructions in Clearwater Forest
- dist: take turns to download mlnx packages from two URLs
- emm: add empty emm kernel module
- emm: Remove submodule emm
- Merge branch 'cunhuang/hinic_update' into 'release' (merge request !364)
- net/hinic: Fix several compilation warnings with aarch64-openEuler-linux toolchain
- net/hinic: Update Huawei Intelligent Network Card Driver: hinic
- Revert "net: hinic: Fix cleanup in create_rxqs/txqs()"
- Merge branch 'haisu/release-cgroupfs-remove-burst' into 'release' (merge request !362)
- rue/cgroupfs: support quota_aware to /proc/stat
- rue/cgroupfs: remove the CPU burst field

* Mon Mar  3 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.80-26
- Merge linux-6.6.80 into TK5 release branch
- Linux 6.6.80
- Merge branch 'haisu/release-fix-cgroupfs' into 'release' (merge request !350)
- rue/cgroupfs: use effective_cpus to replace cpus_allowed
- rue/cgroupfs: show 2 cores when quota=1 and cpuset>1
- rue/cgroupfs: align the CPU quota_aware and cpuset show
- rue/cgroupfs: simplify the cgroupfs_cpu_dir_filter function
- rue/cgroupfs: rename cpu_subdir_xxx to cfs_subdir_xxx
- rue/cgroupfs: remove the unnecessary cgroupfs_dentry_simple_ops
- rue/cgroupfs: cpu/online show the same result of cpuset instead of number
- fs: cgroup: fix compile errors on allyesconfig
- cgroupfs: get data from ancestor cgroup
- cgroupfs: add role in cgroup
- Merge branch 'linuszeng/local_counter' into 'release' (merge request !352)
- mm/memcontrol: add fields to memory.stat of cgroupv2
- Merge branch 'likexu/kvm/fixes' into 'release' (merge request !344)
- KVM: x86: Drop the now unused KVM_X86_DISABLE_VALID_EXITS
- KVM: x86: Reject disabling of MWAIT/HLT interception when not allowed
- KVM: x86: Disallow KVM_CAP_X86_DISABLE_EXITS after vCPU creation
- KVM: x86: Drop now-redundant MAXPHYADDR and GPA rsvd bits from vCPU creation
- KVM: x86/pmu: Drop now-redundant refresh() during init()
- KVM: x86: Move __kvm_is_valid_cr4() definition to x86.h
- KVM: x86: Account for KVM-reserved CR4 bits when passing through CR4 on VMX
- KVM: x86: Explicitly do runtime CPUID updates "after" initial setup
- KVM: x86: Do all post-set CPUID processing during vCPU creation
- KVM: x86: Limit use of F() and SF() to kvm_cpu_cap_{mask,init_kvm_defined}()
- KVM: x86: Use feature_bit() to clear CONSTANT_TSC when emulating CPUID
- KVM: nVMX: fix canonical check of vmcs12 HOST_RIP
- KVM: x86: model canonical checks more precisely
- KVM: x86: Add X86EMUL_F_MSR and X86EMUL_F_DT_LOAD to aid canonical checks
- KVM: x86: Route non-canonical checks in emulator through emulate_ops
- KVM: x86: drop x86.h include from cpuid.h
- Merge branch 'frankjpliu/release-mr-ock' into 'release' (merge request !353)
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !320 [linux-6.6/devel][[bugfix] LoongArch: Correct Cache Sharing, Update Flush Policy, HDA and Bluetooth Fixes
- blutetooth/btusb: delay 1ms while suspending
- LoongArch: Correct the cacheinfo sharing information
- hda/pci: Add AZX_DCAPS_NO_TCSEL flag for Loongson HDA devices
- LoongArch: Update the flush cache policy
- !319 [linux-6.6/devel] LoongArch: Update Loongson-3 default config file
- LoongArch: Update Loongson-3 default config file
- !315 Backport upstream auto-tune per-CPU pageset size patchset
- mm and cache_info: remove unnecessary CPU cache info update
- mm, pcp: reduce detecting time of consecutive high order page freeing
- mm, pcp: decrease PCP high if free pages < high watermark
- mm: tune PCP high automatically
- mm: add framework for PCP high auto-tuning
- mm, page_alloc: scale the number of pages that are batch allocated
- mm, pcp: reduce lock contention for draining high-order pages
- cacheinfo: calculate size of per-CPU data cache slice
- mm, pcp: avoid to drain PCP when process exit
- tkernel: support kill protect feature
- Merge branch 'costinchen/release' into 'release' (merge request !345)
- dim: fix memory allocation size in store_task_pids()
- integrity: Add a boot parameter to explicitly enable integrity subsystems
- dist,copy-drivers: exit 1 if download driver fail
- Merge linux 6.6.79 into TK5 release branch
- Linux 6.6.79
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !314 [linux-6.6/devel]  Some eevdf scheduling enhancements from upstream
- sched/eevdf: O(1) fastpath for task selection
- sched/eevdf: Sort the rbtree by virtual deadline
- !313 Add support for Hygon model 8h processor Merge pull request !313 from fuhao/linux-6.6-hygon-model8h
- EDAC/amd64: Add support for Hygon family 18h model 8h
- x86/amd_nb: Add support for Hygon family 18h model 8h
- !311 [linux-6.6/devel]montage: update Mont-TSSE driver update Montage Mont-TSSE driver from 1.0.0 to 1.1.2 in 6.6.
- montage: update Mont-TSSE driver
- dist: check mlnx driver sha256sum before copy it
- Merge branch linux-6.6.78 into TK5 release branch
- Linux 6.6.78
- Merge linux 6.6.77 into TK5 release branch
- Linux 6.6.77
- !310 Some fixes and optimization for Hygon model 7h10h processors
- perf/x86/amd/core: Fix performance monitor for Hygon family 18h processor
- EDAC/amd64: Get instance_id for Hygon family 18h model 10h
- EDAC/amd64: Get correct memory type for Hygon family 18h model 10h
- EDAC/amd64: Check if umc channel is enabled for Hygon family 18h model 10h
- EDAC/amd64: Adjust address translation for Hygon family 18h model 10h
- x86/amd_nb: Add helper function to identify Hygon family 18h model 10h
- iommu/hygon: Add support for Hygon family 18h model 10h IOAPIC
- EDAC/mce_amd: Add LS and IF mce types for Hygon family 18h model 7h
- !309 Some fixes and optimization for Hygon model 4h~6h processors
- EDAC/amd64: Get intlv_num_dies from F0x60 for Hygon family 18h model 6h
- EDAC/amd64: Fix the calculation of instance_id for Hygon family 18h model 6h
- EDAC/amd64: Use u16 for some umc variables for Hygon family 18h model 4h
- EDAC/amd64: Fix the calculation of cs_id for Hygon family 18h model 4h
- x86/amd_nb: Fix northbridge init warning in guest for Hygon family 18h model 4h
- KVM: x86/svm: Add set_guest_pat_wb parameter for non-passthrough application scenarios
- pinctrl: Add device HID for Hygon GPIO controller
- !307 [linux-6.6/devel] Intel: backport KVM Fix for Clearing SGX EDECCSSA to 6.6
- KVM: VMX: Also clear SGX EDECCSSA in KVM CPU caps when SGX is disabled
- Merge branch 'alexyonghe/reparent_memcg' into 'release' (merge request !338)
- selftests: cgroup: Add memory.reparent_file test case
- mm: Drop memory cgroup css reference when reparent page cache
- Merge branch 'haisu/rue-compile-loongarch-fix' into 'release' (merge request !335)
- rue/io: enable CONFIG_BLK_DEV_THROTTLING_CGROUP_V1 in loongarch
- Merge linux 6.6.76 into TK5 release branch
- Linux 6.6.76
- Merge linux 6.6.75 into TK5 release branch
- Linux 6.6.75
- Merge linux 6.6.74 into TK5 release branch
- Linux 6.6.74
- Merge linux 6.6.73 into TK5 release
- Linux 6.6.73
- Merge linux 6.6.72 into TK5 release
- Linux 6.6.72
- Merge linux 6.6.71 into TK5 release
- Linux 6.6.71

* Sun Jan 19 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.70-24
- emm: update emm to v0.1.7.7

* Fri Jan 17 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.70-23
- emm: update emm to v0.1.7.6
- Merge branch 'cunhuang/arm64-mlnx-BuildRequires' into 'release' (merge request !315)
- dist: fix BuildRequires for mlnx commercial-grade driver
- Merge branch 'cunhuang/pick-v6.6.71_kdump' into 'release' (merge request !314)
- x86/hyperv: Fix hv tsc page based sched_clock for hibernation
- Revert "x86, crash: wrap crash dumping code into crash related ifdefs"
- Revert "x86/hyperv: Fix hv tsc page based sched_clock for hibernation"
- dist: fix the method of arch judge
- dist: compile mlnx commercial-grade driver only on x86 and arm64
- Merge branch 'cunhuang/kabi-vermagic-match-release' into 'release' (merge request !300)
- kabi: modules: vermagic check match to release number
- Merge branch 'aurelianliu/release_1030' into 'release' (merge request !298)
- ACPI: PRM: Remove unnecessary strict handler address checks
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !306 Hygon: sync upstream bugfix patch for LRU and revert the workaround patch
- Revert "mm/gup: don't check if a page is in lru before draining it"
- mm: vmscan.c: fix OOM on swap stress test
- mm/gup: clear the LRU flag of a page before adding to LRU batch
- Revert "mm/page_alloc: don't use PCP list for THP-sized allocations when using PF_MEMALLOC_PIN"
- dist: delete inner url for some reason
- dist: change OC kernel URL discription

* Fri Jan 10 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.70-22
- Merge branch 'paulning/tk5-mglru-pclimit' into 'release' (merge request !297)
- rue/mm: fix a line of code to comply with coding standards
- Merge branch 'frankjpliu/release-mr-stable' into 'release' (merge request !295)
- drivers,linkdata: fix tkci compile error after merge OCK linux-6.6/devel
- Merge branch 'frankjpliu/release-mr-stable' into 'release' (merge request !294)
- Merge branch OCK linux-6.6/devel branch into TK5 release branch
- !301 linkdata: Add support for sxe/sxevf Controller driver in 6.6 kernel
- fix compile error when using allyesconfig config
- Add support for sxe/sxevf Controller driver in 6.6 kernel
- Merge branch 'frankjpliu/release-mr-stable' into 'release' (merge request !292)
- Merge linux 6.6.70 into TK5 release branch
- Linux 6.6.70

* Thu Jan  9 2025 Jianping Liu <frankjpliu@tencent.com> - 6.6.69-21
- Merge branch OCK linux-6.6/devel branch into TK5 release branch
- !305 [linux-6.6/devel][bugfix]: LoongArch: set CONFIG_CMA_SIZE_MBYTES to 0
- LoongArch: set CONFIG_CMA_SIZE_MBYTES to 0
- !303 perf/x86/uncore: Add DF PMU support for Hygon family 18h model 4-7h and 10h
- perf/x86/uncore: Add DF PMU support for Hygon family 18h model 4-7h and 10h
- Merge branch 'paulning/tk5-mglru-pclimit' into 'release' (merge request !277)
- rue/mm: support for sysctl pagecache_limit_ignore_slab when mglru enabled.
- rue/mm: support for pagecache_limit_ignore_dirty when mglru enabled.
- rue/mm: global pagecache limit support when mglru enabled.
- rue/mm: check page_max in mem_cgroup_shrink_pagecache
- rue/mm: pagecache limit feature for memcg when mglru enabled
- Merge branch 'likexu/kvm/fixes' into 'release' (merge request !283)
- tools headers: Sync x86 kvm and cpufeature headers with the kernel
- KVM: SVM: Allow guest writes to set MSR_AMD64_DE_CFG bits
- KVM: x86: Remove ordering check b/w MSR_PLATFORM_INFO and MISC_FEATURES_ENABLES
- KVM: x86: Reject userspace attempts to access ARCH_CAPABILITIES w/o support
- KVM: VMX: Remove restriction that PMU version > 0 for PERF_CAPABILITIES
- KVM: x86: Reject userspace attempts to access PERF_CAPABILITIES w/o PDCM
- KVM: x86: Quirk initialization of feature MSRs to KVM's max configuration
- KVM: x86: Disallow changing MSR_PLATFORM_INFO after vCPU has run
- KVM: x86: Co-locate initialization of feature MSRs in kvm_arch_vcpu_create()
- KVM: x86: Suppress userspace access failures on unsupported, "emulated" MSRs
- KVM: x86: Suppress failures on userspace access to advertised, unsupported MSRs
- KVM: x86: Hoist x86.c's global msr_* variables up above kvm_do_msr_access()
- KVM: x86: Funnel all fancy MSR return value handling into a common helper
- KVM: x86: Refactor kvm_get_feature_msr() to avoid struct kvm_msr_entry
- KVM: x86: Rename get_msr_feature() APIs to get_feature_msr()
- KVM: x86: Refactor kvm_x86_ops.get_msr_feature() to avoid kvm_msr_entry
- KVM: x86: Rename KVM_MSR_RET_INVALID to KVM_MSR_RET_UNSUPPORTED
- KVM: x86: Move MSR_TYPE_{R,W,RW} values from VMX to x86, as enums
- KVM: SVM: Disallow guest from changing userspace's MSR_AMD64_DE_CFG value
- Merge branch 'katrinzhou/release-fix-errno' into 'release' (merge request !285)
- KEYS: include header for EINVAL definition
- rue/io: check blkcg exist before doing account cgroup IO
- configs: update std-configs-list
- config,loongarch: delete the duplicate configuration of CONFIG_DRM_LOONGSON
- config: keep with wangxinban
- Merge linux 6.6.69 into TK5 release branch
- Linux 6.6.69
- !300 net: yt6801: Fix NULL pointer dereference in fxgmac_map_tx_skb
- net: yt6801: Fix NULL pointer dereference in fxgmac_map_tx_skb

* Tue Dec 31 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.68-20
- emm: update emm to v0.1.7.5
- Merge branch 'frankjpliu/release-mr-ock' into 'release' (merge request !282)
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !299 Enhanced Hygon processor's processing capabilities for large memory copying
- [6.6][feat]Hygon: Enhanced Hygon processor's processing capabilities for large memory copying.
- !298 Fix some known issues related to the LoongArch architecture
- net: stmmac: dwmac-loongson: Fix slow MAC DMA reset
- LoongArch: eiointc: Fix external interrupt routing errors
- i2c: ls2x: Fix incorrect frequency register configuration causing functional issues
- loongarch: Modularize Loongson DRM driver (CONFIG_DRM_LOONGSON=m)
- pci/quirks: ls7a2000: fix pm transition of devices under pcie port
- !297 Add CPU hardware monitoring platform driver and ACPI firmware support for Loongson SE driver
- LoongArch: Adjust calculation method for the number of CPU packages
- drivers/char: add ACPI firmware support for Loongson SE driver
- LoongArch: Add CPU HWMon platform driver
- Merge branch 'frankjpliu/release-mr-stable' into 'release' (merge request !281)
- Merge linux 6.6.68 into TK5 release branch
- Linux 6.6.68
- Merge linux 6.6.67 into TK5 release branch
- Linux 6.6.67
- Merge linux 6.6.66 into release branch
- Linux 6.6.66
- Merge linux 6.6.65 into release branch
- Linux 6.6.65
- Merge branch 'frankjpliu/release-mr-ock' into 'release' (merge request !280)
- !296 Fixed multiple vfio devices not working properly
- driver/iommu: Fixed multiple vfio devices not working properly
- !295 Hygon: kernel startup hash verification and secret injection for CSV3
- KVM: SVM: CSV: Support inject secret to Hygon CSV3 guest
- KVM: SVM: CSV: Support issue non-4K aligned CSV3_CMD_LAUNCH_ENCRYPT_DATA and more than once
- KVM: SVM: CSV: Provide KVM_CSV3_SET_GUEST_PRIVATE_MEMORY ioctl interface
- KVM: SVM: CSV: Provide KVM_CAP_HYGON_COCO_EXT interface
- crypto: ccp: Provide csv_get_extension_info() to present extensions of newer CSV firmware
- KVM: SVM: CSV: Ensure all the GPRs and some non-GPRs are synced before LAUNCH_ENCRYPT_VMCB
- crypto: ccp: Get api version again when update Hygon CSV firmware at runtime
- KVM: SVM: CSV: Fix the vm_size even if CSV3 feature is unsupported on Hygon CPUs
- !294 Hygon: Add remote authentication support for Hygon CSV3 virtual machines
- virt/csv-guest: Provide interface for request of CSV3 attestation report
- x86/csv: Add support for CSV3 ATTESTATION secure call
- x86/csv: Define ATTESTATION secure call command
- !293 Hygon: Fix regressions on CSV2 live migration, CSV3 boot, CSV3 live migration
- KVM: SVM: CSV: Explicitly enable LBR Virtualization after succeed to RECEIVE_ENCRYPT_CONTEXT
- KVM: SVM: CSV: Explicitly enable LBR Virtualization after succeed to LAUNCH_ENCRYPT_VMCB
- KVM: SVM: CSV: Explicitly enable LBR Virtualization after succeed to RECEIVE_UPDATE_VMSA
- !286 Intel RDT monitoring support on Sub-NUMA Cluster (SNC) enabled systems
- x86/resctrl: Fix arch_mbm_* array overrun on SNC
- x86/resctrl: Update documentation with Sub-NUMA cluster changes
- x86/resctrl: Detect Sub-NUMA Cluster (SNC) mode
- x86/resctrl: Enable shared RMID mode on Sub-NUMA Cluster (SNC) systems
- x86/resctrl: Make __mon_event_count() handle sum domains
- x86/resctrl: Fill out rmid_read structure for smp_call*() to read a counter
- x86/resctrl: Handle removing directories in Sub-NUMA Cluster (SNC) mode
- x86/resctrl: Create Sub-NUMA Cluster (SNC) monitor files
- x86/resctrl: Allocate a new field in union mon_data_bits
- x86/resctrl: Refactor mkdir_mondata_subdir() with a helper function
- x86/resctrl: Initialize on-stack struct rmid_read instances
- x86/resctrl: Add a new field to struct rmid_read for summation of domains
- x86/resctrl: Prepare for new Sub-NUMA Cluster (SNC) monitor files
- x86/resctrl: Block use of mba_MBps mount option on Sub-NUMA Cluster (SNC) systems
- x86/resctrl: Introduce snc_nodes_per_l3_cache
- x86/resctrl: Add node-scope to the options for feature scope
- x86/resctrl: Split the rdt_domain and rdt_hw_domain structures
- x86/resctrl: Prepare for different scope for control/monitor operations
- x86/resctrl: Prepare to split rdt_domain structure
- x86/resctrl: Prepare for new domain scope
- x86/resctrl: Replace open coded cacheinfo searches
- cacheinfo: Add function to get cacheinfo for a given CPU and cache level
- cpu: Drop "extern" from function declarations in cpuhplock.h
- cpu: Move CPU hotplug function declarations into their own header
- x86/resctrl: Don't try to free nonexistent RMIDs
- x86/resctrl: Add tracepoint for llc_occupancy tracking
- x86/resctrl: Rename pseudo_lock_event.h to trace.h
- x86/resctrl: Simplify call convention for MSR update functions
- x86/resctrl: Pass domain to target CPU
- x86/resctrl: Fix uninitialized memory read when last CPU of domain goes offline
- Documentation/x86: Document that resctrl bandwidth control units are MiB
- x86/resctrl: Remove lockdep annotation that triggers false positive
- x86/resctrl: Separate arch and fs resctrl locks
- x86/resctrl: Move domain helper migration into resctrl_offline_cpu()
- x86/resctrl: Add CPU offline callback for resctrl work
- x86/resctrl: Allow overflow/limbo handlers to be scheduled on any-but CPU
- x86/resctrl: Add CPU online callback for resctrl work
- x86/resctrl: Add helpers for system wide mon/alloc capable
- x86/resctrl: Make rdt_enable_key the arch's decision to switch
- x86/resctrl: Move alloc/mon static keys into helpers
- x86/resctrl: Make resctrl_mounted checks explicit
- x86/resctrl: Allow arch to allocate memory needed in resctrl_arch_rmid_read()
- x86/resctrl: Allow resctrl_arch_rmid_read() to sleep
- x86/resctrl: Queue mon_event_read() instead of sending an IPI
- x86/resctrl: Add cpumask_any_housekeeping() for limbo/overflow
- x86/resctrl: Move CLOSID/RMID matching and setting to use helpers
- x86/resctrl: Allocate the cleanest CLOSID by searching closid_num_dirty_rmid
- x86/resctrl: Use __set_bit()/__clear_bit() instead of open coding
- x86/resctrl: Track the number of dirty RMID a CLOSID has
- x86/resctrl: Allow RMID allocation to be scoped by CLOSID
- x86/resctrl: Access per-rmid structures by index
- x86/resctrl: Track the closid with the rmid
- x86/resctrl: Move RMID allocation out of mkdir_rdt_prepare()
- x86/resctrl: Create helper for RMID allocation and mondata dir creation
- x86/resctrl: Free rmid_ptrs from resctrl_exit()
- tick/nohz: Move tick_nohz_full_mask declaration outside the #ifdef
- x86/resctrl: Remove redundant variable in mbm_config_write_domain()
- x86/resctrl: Fix unused variable warning in cache_alloc_hsw_probe()
- x86/resctrl: Display RMID of resource group
- x86/resctrl: Add support for the files of MON groups only
- x86/resctrl: Display CLOSID for resource group
- x86/resctrl: Introduce "-o debug" mount option
- x86/resctrl: Move default group file creation to mount
- x86/resctrl: Unwind properly from rdt_enable_ctx()
- x86/resctrl: Rename rftype flags for consistency
- x86/resctrl: Simplify rftype flag definitions
- x86/resctrl: Add multiple tasks to the resctrl group at once
- x86/resctrl: Fix remaining kernel-doc warnings
- !290 drivers: ethernet: Add motorcomm yt6801 support
- drivers: ethernet: Add motorcomm yt6801 support
- !291 Fix extioi restart issue in vm
- arch/loongarch/kvm: Fix extioi restart issue
- Merge branch 'korantli/release-cve' into 'release' (merge request !279)
- drm/amd/display: Check denominator crb_pipes before used
- Merge branch 'frankjpliu/release-cves' into 'release' (merge request !274)
- net: napi: Prevent overflow of napi_defer_hard_irqs
- x86/mm/ident_map: Use gbpages only where full GB page should be mapped.

* Tue Dec 10 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.64-18
- Merge linux-6.6.64 into TK5 release branch
- Linux 6.6.64
- Merge OCK linux-6.6/devel branch into TK5 release branch
- !285 [linux-6.6] LoongArch: Revert "drm/loongson: disable loongson drm driver by default for LS7A2000"
- Revert "drm/loongson: disable loongson drm driver by default for LS7A2000"
- !284 [linux-6.6/devel] drm: loongson: Always build Loongson DRM drivers Merge pull request !284 from Ming Wang/linux-6.6/devel
- drm: loongson: Always build Loongson DRM drivers
- !282 [devel-6.6] linkdata: ps3stor compilation optimization Merge pull request !282 from liujie_answer/linux-6.6/devel
- scsi: linkdata ps3stor compilation optimization category: feature
- !280 [linux6.6-devel] LoongArch: backport ptw&set_pte patches from upstream Merge pull request !280 from Ming Wang/backport
- LoongArch: Set initial pte entry with PAGE_GLOBAL for kernel space
- LoongArch: Improve hardware page table walker
- LoongArch: Use accessors to page table entries instead of direct dereference
- LoongArch: Remove superfluous flush_dcache_page() definition
- !281 [linux-6.6/devel] LoongArch: drm/loongson: disable loongson drm driver by default for LS7A2000 Merge pull request !281 from Ming Wang/drm
- drm/loongson: disable loongson drm driver by default for LS7A2000
- !279 [linux-6.6/devel] Makefile: Use `filter` for dist Makefile inclusion condition Merge pull request !279 from Ming Wang/dist-style
- Makefile: Use `filter` for dist Makefile inclusion condition
- !278 [linux-6.6/devel] loongarch:  Enables the Advanced Extended Interrupt Controllers (AVEC) functionality in multi-node 3C6000 systems and fix irq issue.
- irq-loongarch-avec.c: Enables the Advanced Extended Interrupt Controllers (AVEC) functionality in multi-node 3C6000 systems.
- drivers/irqchip: Disable pci_irq_limit when using avec interrupt controller
- !277 Intel pstate backport from6.11 Merge pull request !277 from jiayingbao/intel_pstate_backport_from6.11
- !276 Tpmi based drivers backport from 6.11 Merge pull request !276 from jiayingbao/tpmi_based_drivers_backport_from6.11
- !274 [devel-6.6] linkdata: add ps3stor driver support Merge pull request !274 from liujie_answer/linux-6.6/devel
- scsi: add support for linkdata HBA/RAID Controller driver category: feature
- !273 [linux-6.6/devel] perf/x86/zhaoxin/uncore: fix pci_driver conflict issue Merge pull request
- perf/x86/zhaoxin/uncore: fix pci_driver conflict issue
- Merge branch 'leonylgao/check_kconfig' into 'release' (merge request !265)
- configs: check whether TencentOS Kennel configs is compliant
- Merge branch 'leonylgao/check_kapi' into 'release' (merge request !264)
- kapi: check whether TencentOS Kernel KAPI is compliant
- tkernel: support check the compliance of KAPI
- Merge branch 'alexyonghe/reparent_memcg' into 'release' (merge request !267)
- mm: Reparent page cache to parent memory cgroup
- Merge branch 'aurelianliu/origin/master_CVE-2024-49885' into 'release' (merge request !218)
- mm, slub: avoid zeroing kmalloc redzone
- Merge branch 'leonylgao/check_kabi' into 'release' (merge request !266)
- kabi: use pr_xxx to print colors
- Merge branch 'cunhuang/6.6-release/CONFIG_SCSI_HISI_SAS' into 'release' (merge request !259)
- config: arm64: SCSI_HISI_SAS=m
- Merge branch 'costinchen/dim' into 'release' (merge request !262)
- dim: optimized dim logging for dynamic measurements
- drivers,3snic: support incremental compilation
- Merge branch 'katrinzhou/smc_module' into 'release' (merge request !261)
- smc: Enable smc as module

* Tue Dec  3 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.63-17
- smc: Enable smc as module
- config: disable CONFIG_SYSFB_SIMPLEFB
- Merge branch 'linuszeng/CVE-2024-50278' into 'release' (merge request !254)
- dm cache: fix potential out-of-bounds access on the first resume
- dm cache: optimize dirty bit checking with find_next_bit when resizing
- dm cache: fix out-of-bounds access to the dirty bitset when resizing
- dm cache: fix flushing uninitialized delayed_work on cache_ctr error
- dm cache: correct the number of origin blocks to match the target length
- Merge branch 'linuszeng/CVE-2024-53083' into 'release' (merge request !253)
- usb: typec: qcom-pmic: init value of hdr_len/txbuf_len earlier
- Merge branch 'linuszeng/CVE-2024-50300' into 'release' (merge request !252)
- regulator: rtq2208: Fix uninitialized use of regulator_config
- Merge branch 'katrinzhou/cve/release' into 'release' (merge request !236)
- ext4: fix error message when rejecting the default hash
- ext4: filesystems without casefold feature cannot be mounted with siphash
- f2fs: fix to wait dio completion
- xfs: add bounds checking to xlog_recover_process_data
- xfs: don't walk off the end of a directory data block
- Merge linux-6.6.63 into TK5 release branch
- Linux 6.6.63
- Merge branch 'cunhuang/6.6-release/CVE-2024-46775' into 'release' (merge request !251)
- drm/amd/display: Validate function returns
- Merge branch 'cunhuang/cve/6.6-release-24nov20' into 'release' (merge request !248)
- drm/amd/display: Check phantom_stream before it is used
- drm/amd/display: Add NULL check for clk_mgr and clk_mgr->funcs in dcn30_init_hw
- Merge linux 6.6.62 into TK5 release branch
- Linux 6.6.62
- Merge linux 6.6.61 into TK5 release branch
- Linux 6.6.61
- Merge linux 6.6.60 into TK5 release branch
- Linux 6.6.60
- Merge linux 6.6.59 into TK5 release branch
- Linux 6.6.59
- cifs: Fix server re-repick on subrequest retry

* Thu Nov  7 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.58-15
- integrity: add dynamic integrity measurement (DIM) support
- Merge branch 'honglin/release' into 'release' (merge request !220)
- rue/mm: fix suspicious RCU usage in mem_cgroup_account_oom_skip
- rue/mm: fix some sparse warnings of incorrect type in argument
- rue/mm: fix compile error of dereferencing pointer to incomplete type
- rue/mm: fix some sparse warnings due to no previous prototype
- rue/net: fix some sparse warnings in netclassid_cgroup.c
- Merge linux 6.6.58
- kunit/overflow: Fix UB in overflow_allocation_test
- Merge branch 'frankjpliu/master-mr-ocknext' into 'release' (merge request !217)
- Loongarch: Dynamically enable Write Combining
- Loongarch: Driver for loongson SE SDF
- pci/quirks: Enable MSI for LS7A2000 PCIe devices
- !240 [next-6.6] LoongArch: Add AVEC irqchip support and add acpi mcfg quirk for 3C6000
- acpi: mcfg quirk: Increased multi-chip support for the 3C6000
- LoongArch: Add AVEC irqchip support
- !239 [next-6.6] LoongArch: Change SHMLBA from SZ_64K to PAGE_SIZE
- LoongArch: Change SHMLBA from SZ_64K to PAGE_SIZE
- rue/io: fix child blkcg of hier buffered write can not exceed 2MB
- crashkernel: auto adjust crashkernel min size to 800MB for KASAN
- sli: fix crash when open the sli.monitor file in rw mode
- Merge linux 6.6.57
- Merge branch 'cunhuang/jitterentropy-failed' into 'master' (merge request !209)
- crypto: jitter - set default OSR to 3
- crypto: jitter - use permanent health test storage
- crypto: jitter - reuse allocated entropy collector
- crypto: jitter - Allow configuration of oversampling rate
- crypto: jitter - Allow configuration of memory size
- crypto: jitter - add RCT/APT support for different OSRs
- watchdog: handle the ENODEV failure case of lockup_detector_delay_init() separately
- Merge branch 'haisu/master-fix-rue-lore-issues' into 'master' (merge request !207)
- rue/io: mem_cgroup_bind_blkio_write also require CONFIG_SWAP
- rue/io: fix sparse error of restricted blk_opf_t degrades to integer
- rue/io: fix compile errors of redefinition blkg_policy_data
- config: iommu: default arm64 iommu Lazy mode
- mpt3sas: add mpt3sas commercial-quality driver
- Merge branch 'likexu/kvm/fixes' into 'master' (merge request !205)
- KVM: x86: Add fastpath handling of HLT VM-Exits
- KVM: x86: Reorganize code in x86.c to co-locate vCPU blocking/running helpers
- KVM: x86: Exit to userspace if fastpath triggers one on instruction skip
- KVM: x86: Dedup fastpath MSR post-handling logic
- KVM: x86: Re-enter guest if WRMSR(X2APIC_ICR) fastpath is successful
- KVM: x86: Re-split x2APIC ICR into ICR+ICR2 for AMD (x2AVIC)
- KVM: nVMX: Assert that vcpu->mutex is held when accessing secondary VMCSes
- KVM: nVMX: Explicitly invalidate posted_intr_nv if PI is disabled at VM-Enter
- KVM: x86: Fold kvm_get_apic_interrupt() into kvm_cpu_get_interrupt()
- KVM: nVMX: Detect nested posted interrupt NV at nested VM-Exit injection
- KVM: nVMX: Suppress external interrupt VM-Exit injection if there's no IRQ
- KVM: nVMX: Get to-be-acknowledge IRQ for nested VM-Exit at injection site
- KVM: x86: Move "ack" phase of local APIC IRQ delivery to separate API
- KVM: Fix coalesced_mmio_has_room() to avoid premature userspace exit
- KVM: x86: Fully defer to vendor code to decide how to force immediate exit
- KVM: VMX: Handle KVM-induced preemption timer exits in fastpath for L2
- KVM: x86: Move handling of is_guest_mode() into fastpath exit handlers
- KVM: VMX: Handle forced exit due to preemption timer in fastpath
- KVM: VMX: Re-enter guest in fastpath for "spurious" preemption timer exits
- KVM: x86: Plumb "force_immediate_exit" into kvm_entry() tracepoint
- Merge branch 'haisu/master-cve-v9' into 'master' (merge request !204)
- btrfs: don't BUG_ON on ENOMEM from btrfs_lookup_extent_info() in walk_down_proc()
- btrfs: handle errors from btrfs_dec_ref() properly
- binfmt_elf_fdpic: fix AUXV size calculation when ELF_HWCAP2 is defined
- f2fs: fix null reference error when checking end of zone
- nfs: pass explicit offset/count to trace events
- Merge linux 6.6.56
- Merge linux 6.6.55
- Merge linux 6.6.54
- Merge linux 6.6.53
- Merge linux 6.6.52
- Merge linux 6.6.51
- Merge linux 6.6.50
- Merge linux 6.6.49
- Merge linux 6.6.48
- Merge branch 'haisu/master-tryrue-20240905-merge-honglin' into 'master' (merge request !197)
- rue/io: introduce wbt class for cgroup priority
- rue/io: skip throttle REQ_META/REQ_PRIO IO
- rue/io: buffered_write_bps hierarchy support
- rue/io: support readwrite unified configuration
- rue/io: Add iocost and iolatency entry for cgroup v1
- rue/io: add io_cgv1_buff_wb to enable buffer IO counting in cgroup v1
- rue/io: introduce per mem_cgroup sync interface
- rue/io: add bufio isolation based for cgroup v1
- rue/io: Add bps information to blkio.throttle.stat
- rue/io: Add blkio.throttle.stat
- rue/io: add buffer IO writeback throtl for cgroup v1
- rue/io: add io_qos switch and throtl hierarchy
- rue/io: Enable CONFIG_BLK_DEV_THROTTLING_CGROUP_V1 configuration
- rue/io: Correct the alloc type to disk_stats
- rue/io: add support for recursive diskstats
- rue/io: blkcg export blkcg symbols to be used in bpf accounting
- rue/mm: add sysctl_vm_use_priority_oom to enable priority oom for all cgroups
- rue/mm: compatible with mglru for pagecache limit
- rue/mm: fix file page_counter 'memcg->pagecache' error when THP enabled
- rue/mm: introduce new feature to async clean dying memcgs
- rue/mm: introduce memcg page cache hit & miss ratio tool
- rue/mm: introduce memory allocation latency for per-cgroup tool
- rue/mm: async free memory while process exiting
- rue/mm: pagecache limit per cgroup support
- rue/mm: add memory cgroup async page reclaim mechanism
- rue/mm: introduce memcg priority oom
- rue/mm: add priority reclaim support
- pagecachelimit: set an initial value for may_deactivate in shrink page cache
- rue/net: avoid wrong memory access to struct net_device
- rue/net: avoid wrong memory access to struct cgroup_cls_state
- rue/net: adapt to the new rue modular framework
- rue/net: add dynamic bandwidth allocation between online cgroups
- rue/net: add netdev-based rate limit for per cgroup
- rue/net: add total bandwidth limit for multiprio preemption
- rue/net: add support for cgroup whitelist ports
- rue/net: add rx && tx rate limit for per cgroup
- rue/net: init netcls traffic controller
- rue: Revert "kallsyms: unexport kallsyms_lookup_name() and kallsyms_on_each_symbol()"
- rue: Add support for rue modularization
- rue: init rue module
- rue: cgroup priority
- blkcg/diskstats: Fix the extra cpu parameter
- mm: set default watermark_boost_factor value to 0
- Revert "io/tqos: merge buffer io limit series patch from brookxu, and rework some function."
- Revert "io/tqos: add sysctl_buffer_io_limit switch for buffer io limit."
- Revert "cgroup: allow cgroup to split direct io and buffered io into different blkio cgroup"
- emm: update to v0.1.7.4
- dist,spec: provide kernel-debug-debuginfo in debug version
- dist,sepc: supprot kernel-debug in core and modules and devel rpm
- Merge branch 'frankjpliu/master-mr-ocknext' into 'master' (merge request !202)
- !234 [next-6.6] Intel: Backport to support Intel IFS(In Field Scan) SBAF on GNR for kernel 6.6
- platform/x86/intel/ifs: Fix SBAF title underline length
- trace: platform/x86/intel/ifs: Add SBAF trace support
- platform/x86/intel/ifs: Add SBAF test support
- platform/x86/intel/ifs: Add SBAF test image loading support
- platform/x86/intel/ifs: Refactor MSR usage in IFS test code
- selftests: ifs: verify IFS ARRAY BIST functionality
- selftests: ifs: verify IFS scan test functionality
- selftests: ifs: verify test image loading functionality
- selftests: ifs: verify test interfaces are created by the driver
- platform/x86/intel/ifs: Disable irq during one load stage
- platform/x86/intel/ifs: trace: display batch num in hex
- platform/x86/intel/ifs: Classify error scenarios correctly
- platform/x86/intel/ifs: Remove unnecessary initialization of 'ret'
- platform/x86/intel/ifs: Add an entry rendezvous for SAF
- platform/x86/intel/ifs: Replace the exit rendezvous with an entry rendezvous for ARRAY_BIST
- platform/x86/intel/ifs: Add current batch number to trace output
- platform/x86/intel/ifs: Trace on all HT threads when executing a test
- ALSA: hda: Add support for Hygon family 18h model 10h HD-Audio
- hwmon/k10temp: Add support for Hygon family 18h model 10h
- EDAC/amd64: Add support for Hygon family 18h model 10h
- x86/amd_nb: Add support for Hygon family 18h model 10h
- x86/cpu: Get LLC ID for Hygon family 18h model 10h
- perf/x86/uncore: Add L3 PMU support for Hygon family 18h model 7h
- EDAC/amd64: Add support for Hygon family 18h model 7h
- x86/amd_nb: Add support for Hygon family 18h model 7h
- crypto: ccp: add more checks for sev_dev_hooks_installed
- config: set CONFIG_KASAN_STACK=y in debug.config
- net/netlat: fix a deadlock when reset the /proc/net/twatcher/log
- xfs: allow symlinks with short remote targets
- Merge branch 'likexu/kvm/vpmu/fixes' into 'master' (merge request !200)
- KVM: x86/pmu: Explicitly check NMI from guest to reducee false positives
- KVM: x86: Get CPL directly when checking if loaded vCPU is in kernel mode
- KVM: VMX: Disable LBR virtualization if the CPU doesn't support LBR callstacks
- perf/x86/intel: Expose existence of callback support to KVM
- KVM: VMX: Snapshot LBR capabilities during module initialization
- KVM: x86/pmu: Explicitly check for RDPMC of unsupported Intel PMC types
- KVM: x86/pmu: Treat "fixed" PMU type in RDPMC as index as a value, not flag
- KVM: x86/pmu: Disallow "fast" RDPMC for architectural Intel PMUs
- KVM: x86/pmu: Apply "fast" RDPMC only to Intel PMUs
- KVM: x86/pmu: Prioritize VMX interception over #GP on RDPMC due to bad index
- KVM: x86/pmu: Don't ignore bits 31:30 for RDPMC index on AMD
- KVM: x86/pmu: Get eventsel for fixed counters from perf
- KVM: x86/pmu: Setup fixed counters' eventsel during PMU initialization
- KVM: x86/pmu: Remove KVM's enumeration of Intel's architectural encodings
- KVM: x86/pmu: Allow programming events that match unsupported arch events
- KVM: x86/pmu: Always treat Fixed counters as available when supported
- KVM: x86/pmu: Track emulated counter events instead of previous counter
- KVM: x86/pmu: Update sample period in pmc_write_counter()
- KVM: x86/pmu: Remove manual clearing of fields in kvm_pmu_init()
- KVM: x86/pmu: Stop calling kvm_pmu_reset() at RESET (it's redundant)
- selftests/bpf: DENYLIST.aarch64: Skip fexit_sleep again
- bpf, arm64: Fix trampoline for BPF_TRAMP_F_CALL_ORIG
- closures: Change BUG_ON() to WARN_ON()
- dist,Makefile: inherit the existing value of the DISABLED variable
- config: configure panic_timeout=-1, restart immediately when panic occurs
- config,debug: set CONFIG_LOCALVERSION="+debug" in debug*.config
- dist,Makefile: generic-debug config only build kernel rpm
- config: split debug.config to debug.config and debug-sched.config

* Mon Sep 23 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.47-12
- crypto: ccp: fix the sev_do_cmd panic on non-Hygon platforms
- emm: upadate to v0.1.7.3
- emm: fix cgroup initilization check
- tools headers UAPI: Sync kvm headers with the kernel sources
- KVM: x86: Prevent excluding the BSP on setting max_vcpu_ids
- KVM: x86: Limit check IDs for KVM_SET_BOOT_CPU_ID
- KVM: Reject overly excessive IDs in KVM_CREATE_VCPU
- KVM: x86: Make x2APIC ID 100% readonly
- KVM: Introduce KVM_SET_USER_MEMORY_REGION2
- config/x86: Add EROFS_FS and CACHEFILES for image-granularity acceleration
- config,x86: open edr
- riscv/purgatory: align riscv_kernel_entry
- config,x86: disable CONFIG_IOMMU_DEBUGFS
- hung_task,watchdog: set thresh time to 600 seconds
- zhaoxin_rng: Remove redundant pr_err log after matching cpu_ids
- config,x86: set CONFIG_HW_RANDOM_ZHAOXIN to m
- emm: fix panic in kdump
- config: trace: enable CONFIG_FUNCTION_GRAPH_RETVAL
- rue/scx: Fix cgroupv2 cpu controller regression
- watchdog: increase watchdog_thresh max value to 300 in debug kernel
- dist: delete useless code in kernel.template.spec
- i2c/zhaoxin: switch i2c registration to devm functions
- lkp: intel: selftests/bpf: Add netlink helper library

* Tue Aug 27 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.47-11
- config,oc: support WLAN and MTD and more SND drivers
- Merge linux 6.6.47
- Merge linux 6.6.46
- Merge linux 6.6.45
- Merge OCK next branch to TK5 master branch
- x86/hpet: Read HPET directly if panic in progress
- i2c/zhaoxin: I2C controller driver enhancement and optimization
- x86/mce: Add NMIs setup in machine_check func
- x86/mce/zhaoxin: Enable mcelog to decode PCIE, ZDI/ZPI, and DRAM errors
- x86/mce: Set bios_cmci_threshold for CMCI threshold
- perf/x86/zhaoxin/uncore: update KX-7000 support
- iommu/dma: Fix not fully traversing iova reservations issue
- x86/cpu: Remove pointless evaluation of x86_coreid_bits
- i2c: smbus: Add support for Zhaoxin SMBUS controller
- anolis: efi: cper: Add Zhaoxin/Centaur ZDI/ZPI error decode
- ata: ahci: Add support for AHCI SGPIO Enclosure Management
- Set ASYM_PACKING Flag on Zhaoxin KH-40000 platform
- cpufreq: ACPI: add ITMT support when CPPC enabled
- iommu/vt-d: Add support for detecting ACPI namespace device in RMRR
- Add kh40000_iommu_dma_ops for KH-40000 platform
- Add kh40000_direct_dma_ops for KH-40000 platform
- Add early quirk to identify kh-40000
- Merge OCK next branch to TK5 master branch
- !201 [next-6.6] Intel: Backport some core PMU bugfixes to kernel 6.6
- !200 [next-6.6] Intel: Backport SPR/EMR CXL and HBM perfmon support to kernel 6.6
- USB:Fix kernel NULL pointer when unbind UHCI form vfio-pci
- hwmon: Add support for Zhaoxin core temperature monitoring
- anolis: Add support for Zhaoxin Serial ATA IDE.
- rue/scx: Kill user tasks in SCHED_EXT when scheduler is gone
- rue/scx: Add readonly sysctl knob kernel.cpu_qos for SCHED_BT compatibility
- rue/scx: Add /proc/bt_stat to maintain SCHED_BT compatibility
- rue/scx: Add cpu.offline to maintain SCHED_BT compatibility
- rue/scx: Add cpu.scx to the cpu cgroup controller
- rue/scx: Add /proc/scx_stat to do scx cputime accounting
- rue/scx: Fix lockdep warn on printk with rq lock held
- rue/scx: Reorder scx_fork_rwsem, cpu_hotplug_lock and scx_cgroup_rwsem
- Revert "sched: adaptive default skew_tick value"
- KVM: x86: Don't sync user-written TSC against startup values
- KVM: s390: Don't re-setup dummy routing when KVM_CREATE_IRQCHIP
- KVM: x86: Don't re-setup empty IRQ routing when KVM_CAP_SPLIT_IRQCHIP
- KVM: Setup empty IRQ routing when creating a VM
- kabi: Introduce CONFIG_KABI_RESERVE
- null_blk: Fix return value of nullb_device_power_store()
- null_blk: fix null-ptr-dereference while configuring 'power' and 'submit_queues'
- [PATCH] security: add security hook point
- dist: provide mlnx-ofed-dist rpm
- drivers,dist: add mlnx commercial quality drivers
- submodule: update emm and thirdparty/release-drivers
- net: csig toa patch toa patch from csig luckyqiu@tencent.com
- Merge linux 6.6.44

* Thu Aug 1 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.43-10
- !199 [next-6.6] LoongArch: Add writecombine support for DMW-based ioremap and fix kexec boot faild issue.
- pci-driver: Do not disable PCIE ports and bridge on kexec reboot
- LoongArch: enable CONFIG_CRYPTO_XTS by default
- LoongArch: Add writecombine support for DMW-based ioremap()
- Merge linux 6.6.43
- Merge linux 6.6.42
- !197 [next-6.6] AMD: Backport Turin patches from upstream Merge pull request !197 from kile2009/next-turin-6.6
- perf/x86/amd/core: Define a proper ref-cycles event for Zen 4 and later
- x86/CPU/AMD: Add models 0x10-0x1f to the Zen5 range
- x86/CPU/AMD: Do the common init on future Zens too
- x86/CPU/AMD: Add more models to X86_FEATURE_ZEN5
- x86/CPU/AMD: Add X86_FEATURE_ZEN5
- x86/CPU/AMD: Drop now unused CPU erratum checking function
- x86/CPU/AMD: Get rid of amd_erratum_1485[]
- x86/CPU/AMD: Get rid of amd_erratum_400[]
- x86/CPU/AMD: Get rid of amd_erratum_383[]
- x86/CPU/AMD: Rename init_amd_zn() to init_amd_zen_common()
- x86/CPU/AMD: Call the spectral chicken in the Zen2 init function
- x86/CPU/AMD: Move the Zen3 BTC_NO detection to the Zen3 init function
- Revert "vfio/type1: Unpin zero pages"
- drivers/thirdparty: keep compile bnxt_re if not using thirdparty drivers
- iommu/arm-smmu: Use the correct type in nvidia_smmu_context_fault()
- thermal: intel: powerclamp: fix mismatch in get function for max_idle
- Merge linux 6.6.41
- drivers/thirdparty: add copy-drivers.sh to using thirdparty drivers
- Merge linux 6.6.40
- Merge linux 6.6.39
- Merge linux 6.6.38
- Merge linux 6.6.37
- config: enable CONFIG_WIREGUARD
- Merge linux 6.6.36
- kabi: fix check-kabi file path when checking kABI
- x86/tencentconfig: Enable CONFIG_UNWINDER_ORC in tencent.config
- Merge linux 6.6.35
- emm: don't set zram_memcg_nocharge as true until module load

* Wed Jun 19 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.34-9
- dist: do not run scripts fail in kernel.template.spec
- drm/amdgpu: Fix possible NULL dereference in amdgpu_ras_query_error_status_helper()

* Mon Jun 17 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.34-8
- Merge linux 6.6.34

* Thu Jun 13 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.33-7
- emm: update to v0.1.5
- arm64: add unprivileged instruction support
- arm64: fix the error for instruction :b9400000
- arm64: Add new code for unaligned pcie access
- arm64: remove the hardcode about PCI address checking
- arm64: Add alignment faults handler for Advanced SIMD load/store single
- arm64: Add a fixup handler for alignment faults in aarch64 code
- arm64: update Work around Ampere Altra erratum #82288 PCIE_65
- Merge Linux 6.6.33
- [next-6.6] Intel: Backport Granite Rapids RAPL PMU support to kernel 6.6 Merge pull request !186
- powercap: intel_rapl_tpmi: Enable PMU support
- powercap: intel_rapl: Introduce APIs for PMU support
- powercap: intel_rapl: Sort header files
- [next-6.6] LoongArch:  Fix some irqchip/loongson-eiointc issues and kdump function for loongarch. Merge pull request !182
- anolis: LoongArch: fix efi map page table error
- Revert "LoongArch: kdump: Add memory reservation for old kernel"
- Revert "LoongArch: Fix kdump failure on v40 interface specification"
- Revert "LoongArch: kdump: Add high memory reservation"
- irqchip/loongson-eiointc: fix gsi register error
- irqchip: LoongArch: Fix secondary bridge routing errors
- PCI/MSI: LoongArch: Limit min pci msi-x/msi vector number
- [next-6.6]Intel: Backport QuickAssist Technology(QAT) live migration for in-tree driver Merge pull request !184
- x86: configs: Enable QAT_VFIO_PCI as kernel module
- crypto: qat - Fix ADF_DEV_RESET_SYNC memory leak
- crypto: qat - specify firmware files for 402xx
- crypto: qat - validate slices count returned by FW
- crypto: qat - improve error logging to be consistent across features
- crypto: qat - improve error message in adf_get_arbiter_mapping()
- crypto: qat - implement dh fallback for primes > 4K
- crypto: qat - Fix spelling mistake "Invalide" -> "Invalid"
- crypto: qat - Avoid -Wflex-array-member-not-at-end warnings
- vfio/qat: Add vfio_pci driver for Intel QAT SR-IOV VF devices
- crypto: qat - implement interface for live migration
- crypto: qat - add interface for live migration
- crypto: qat - add bank save and restore flows
- crypto: qat - expand CSR operations for QAT GEN4 devices
- crypto: qat - rename get_sla_arr_of_type()
- crypto: qat - relocate CSR access code
- crypto: qat - move PFVF compat checker to a function
- crypto: qat - relocate and rename 4xxx PF2VM definitions
- crypto: qat - adf_get_etr_base() helper
- iommu/vt-d: Set variable intel_dirty_ops to static
- iommufd/selftest: Fix _test_mock_dirty_bitmaps()
- iommufd/selftest: Fix page-size check in iommufd_test_dirty()
- iommu/vt-d: Enhance capability check for nested parent domain allocation
- iommufd/selftest: Test IOMMU_HWPT_GET_DIRTY_BITMAP_NO_CLEAR flag
- iommufd/selftest: Test out_capabilities in IOMMU_GET_HW_INFO
- iommufd/selftest: Test IOMMU_HWPT_GET_DIRTY_BITMAP
- iommufd/selftest: Test IOMMU_HWPT_SET_DIRTY_TRACKING
- iommufd/selftest: Test IOMMU_HWPT_ALLOC_DIRTY_TRACKING
- iommufd/selftest: Expand mock_domain with dev_flags
- iommu/vt-d: Access/Dirty bit support for SS domains
- iommu/amd: Access/Dirty bit support in IOPTEs
- iommu/amd: Add domain_alloc_user based domain allocation
- iommufd: Add a flag to skip clearing of IOPTE dirty
- iommufd: Add capabilities to IOMMU_GET_HW_INFO
- iommufd: Add IOMMU_HWPT_GET_DIRTY_BITMAP
- iommufd: Add IOMMU_HWPT_SET_DIRTY_TRACKING
- iommufd: Add a flag to enforce dirty tracking on attach
- iommufd: Correct IOMMU_HWPT_ALLOC_NEST_PARENT description
- iommu: Add iommu_domain ops for dirty tracking
- iommufd/iova_bitmap: Move symbols to IOMMUFD namespace
- vfio: Move iova_bitmap into iommufd
- vfio/iova_bitmap: Export more API symbols
- iommufd/selftest: Rework TEST_LENGTH to test min_size explicitly
- iommu/vt-d: Add domain_alloc_user op
- iommufd/selftest: Add domain_alloc_user() support in iommu mock
- iommufd/selftest: Iterate idev_ids in mock_domain's alloc_hwpt test
- iommufd: Support allocating nested parent domain
- iommufd: Flow user flags for domain allocation to domain_alloc_user()
- iommufd: Use the domain_alloc_user() op for domain allocation
- iommu: Add new iommu op to create domains owned by userspace
- !183 [next-6.6] Intel IAA Compression Accelerator Crypto Driver (iaa_crypto) Merge pull request !183 from Xiaochen Shen/intel-iaa-crypto-driver-next-6.6
- x86/config: Add kernel config for Intel IAA crypto driver
- dmaengine: idxd: Avoid unnecessary destruction of file_ida
- dmaengine: idxd: Check for driver name match before sva user feature
- crypto: iaa - Use cpumask_weight() when rebalancing
- crypto: iaa - Fix some errors in IAA documentation
- crypto: iaa - Change iaa statistics to atomic64_t
- crypto: iaa - Add global_stats file and remove individual stat files
- crypto: iaa - Remove comp/decomp delay statistics
- crypto: iaa - fix decomp_bytes_in stats
- crypto: iaa - Fix nr_cpus < nr_iaa case
- crypto: iaa - fix the missing CRYPTO_ALG_ASYNC in cra_flags
- crypto: iaa - Fix comp/decomp delay statistics
- crypto: iaa - Fix async_disable descriptor leak
- crypto: iaa - Remove unnecessary debugfs_create_dir() error check in iaa_crypto_debugfs_init()
- crypto: iaa - Remove header table code
- dmaengine: idxd: constify the struct device_type usage
- dmaengine: idxd: make dsa_bus_type const
- dmaengine: idxd: Remove usage of the deprecated ida_simple_xx() API
- crypto: iaa - Account for cpu-less numa nodes
- crypto: iaa - remove unneeded semicolon
- crypto: iaa - Remove unneeded newline in update_max_adecomp_delay_ns()
- crypto: iaa - Change desc->priv to 0
- dmaengine: idxd: Add support for device/wq defaults
- crypto: iaa - Add IAA Compression Accelerator stats
- crypto: iaa - Add irq support for the crypto async interface
- crypto: iaa - Add support for deflate-iaa compression algorithm
- crypto: iaa - Add compression mode management along with fixed mode
- crypto: iaa - Add per-cpu workqueue table with rebalancing
- crypto: iaa - Add Intel IAA Compression Accelerator crypto driver core
- crypto: iaa - Add IAA Compression Accelerator Documentation
- dmaengine: idxd: add callback support for iaa crypto
- dmaengine: idxd: Add wq private data accessors
- dmaengine: idxd: Export wq resource management functions
- dmaengine: idxd: Export descriptor management functions
- dmaengine: idxd: Rename drv_enable/disable_wq to idxd_drv_enable/disable_wq, and export
- dmaengine: idxd: add external module driver support for dsa_bus_type
- dmaengine: idxd: Fix incorrect descriptions for GRPCFG register
- dmaengine: idxd: add wq driver name support for accel-config user tool
- dmaengine: idxd: rate limit printk in misc interrupt thread
- drm/phytium: Replace default efi fb0 with dc fb
- [next-6.6] phytium-Bugfix-Xorg-startup-for-ps23xx Merge pull request !188
- drm/ast: Fixed display error for ps23xx
- drm/phytium: Bugfix Xorg startup for ps23xx
- anolis: LoongArch: fix efi map page table error
- Revert "LoongArch: kdump: Add memory reservation for old kernel"
- Revert "LoongArch: Fix kdump failure on v40 interface specification"
- Revert "LoongArch: kdump: Add high memory reservation"
- LoongArch: fix HT RX INT TRANS register not initialized
- irqchip/loongson-eiointc: fix gsi register error
- irqchip: LoongArch: Fix secondary bridge routing errors
- PCI/MSI: LoongArch: Limit min pci msi-x/msi vector number
- cgroup: allow cgroup to split direct io and buffered io into different blkio cgroup
- io/tqos: add sysctl_buffer_io_limit switch for buffer io limit.
- io/tqos: merge buffer io limit series patch from brookxu, and rework some function.
- Merge branch 'caelli/cgroupfs' into 'master' (merge request !102)
- cgroupfs: optimize cpu usage
- sli: open CONFIG_CGROUP_SLI
- sli: backport sli function from tk3
- mbuf: backport mbuf functions for memcontrol/cpuacct from tk3
- btrfs: make sure that WRITTEN is set on all metadata blocks
- nvme:driver core probes in serial
- config: enable ce instruction set optimization for shangmi support
- config: enable some configs for shangmi support
- kconfig: add more module for arm64
- Merge ock repo's next branch into tk5 repo's master branch
- [next-6.6]Hisi:backport some bugfix from upstream about PCIe_PMU and hisi_hns3 perf Merge pull request !179
- drivers/perf: hisi: hns3: Actually use devm_add_action_or_reset()
- drivers/perf: hisi: hns3: Fix out-of-bound access when valid event group
- docs: perf: Update usage for target filter of hisi-pcie-pmu
- drivers/perf: hisi_pcie: Merge find_related_event() and get_event_idx()
- drivers/perf: hisi_pcie: Relax the check on related events
- drivers/perf: hisi_pcie: Check the target filter properly
- drivers/perf: hisi_pcie: Add more events for counting TLP bandwidth
- drivers/perf: hisi_pcie: Fix incorrect counting under metric mode
- drivers/perf: hisi_pcie: Introduce hisi_pcie_pmu_get_event_ctrl_val()
- drivers/perf: hisi_pcie: Rename hisi_pcie_pmu_{config,clear}_filter()
- !176 [next-6.6] net: stmmac: add 7A2000 chipset gnet support Merge pull request !176 from Ming Wang/master
- net: stmmac: dwmac-loongson: Add loongson module author
- net: stmmac: dwmac-loongson: Move disable_force flag to _gnet_date
- net: stmmac: dwmac-loongson: Add Loongson GNET support
- net: stmmac: dwmac-loongson: Fixed failure to set network speed to 1000.
- net: stmmac: dwmac-loongson: Add loongson_dwmac_config_legacy
- net: stmmac: dwmac-loongson: Add full PCI support
- net: stmmac: dwmac-loongson: Add phy_interface for Loongson GMAC
- net: stmmac: dwmac-loongson: Add phy mask for Loongson GMAC
- net: stmmac: dwmac-loongson: Add ref and ptp clocks for Loongson
- net: stmmac: dwmac-loongson: Split up the platform data initialization
- net: stmmac: dwmac-loongson: Use PCI_DEVICE_DATA() macro for device identification
- net: stmmac: dwmac-loongson: Drop useless platform data
- net: stmmac: Export dwmac1000_dma_ops
- net: stmmac: Add multi-channel support
- net: stmmac: Move the atds flag to the stmmac_dma_cfg structure
- net: stmmac: Move MAC caps init to phylink MAC caps getter
- net: stmmac: Rename phylink_get_caps() callback to update_caps()
- net: phylink: provide mac_get_caps() method
- Merge branch 'dev/mengensun/netlat_v2' into 'master' (merge request !100)
- netlat: fix warnning when del netns
- netlat: not use ack_seq to keeping timestamp
- netlat: add more queue latency check point
- net/netlat: add a tcp latency watcher
- netns/mbuf: add a per net namespace ring buffer
- tqos: open CONFIG_RQM
- tqos/mbuf: backport mbuf infrastructure from tk3
- dist: using "tk_private=1" to judge private release
- Merge branch 'frankjpliu/master' into 'master' (merge request !107)
- Merge linux 6.6.32
- Linux 6.6.32
- block: add a partscan sysfs attribute for disks
- block: add a disk_has_partscan helper
- Docs/admin-guide/mm/damon/usage: fix wrong example of DAMOS filter matching sysfs file
- docs: kernel_include.py: Cope with docutils 0.21
- admin-guide/hw-vuln/core-scheduling: fix return type of PR_SCHED_CORE_GET
- KEYS: trusted: Do not use WARN when encode fails
- remoteproc: mediatek: Make sure IPI buffer fits in L2TCM
- serial: kgdboc: Fix NMI-safety problems from keyboard reset code
- usb: typec: tipd: fix event checking for tps6598x
- usb: typec: ucsi: displayport: Fix potential deadlock
- net: usb: ax88179_178a: fix link status when link is set to down/up
- usb: dwc3: Wait unconditionally after issuing EndXfer command
- binder: fix max_thread type inconsistency
- drm/amdgpu: Fix possible NULL dereference in amdgpu_ras_query_error_status_helper()
- erofs: reliably distinguish block based and fscache mode
- erofs: get rid of erofs_fs_context
- bpf: Add missing BPF_LINK_TYPE invocations
- kselftest: Add a ksft_perror() helper
- mmc: core: Add HS400 tuning in HS400es initialization
- KEYS: trusted: Fix memory leak in tpm2_key_encode()
- Bluetooth: L2CAP: Fix div-by-zero in l2cap_le_flowctl_init()
- Bluetooth: L2CAP: Fix slab-use-after-free in l2cap_connect()
- ice: remove unnecessary duplicate checks for VF VSI ID
- ice: pass VSI pointer into ice_vc_isvalid_q_id
- net: ks8851: Fix another TX stall caused by wrong ISR flag handling
- drm/amd/display: Fix division by zero in setup_dsc_config
- smb: smb2pdu.h: Avoid -Wflex-array-member-not-at-end warnings
- ksmbd: add continuous availability share parameter
- cifs: Add tracing for the cifs_tcon struct refcounting
- smb: client: instantiate when creating SFU files
- smb: client: fix NULL ptr deref in cifs_mark_open_handles_for_deleted_file()
- smb3: add trace event for mknod
- smb311: additional compression flag defined in updated protocol spec
- smb311: correct incorrect offset field in compression header
- cifs: Move some extern decls from .c files to .h
- ksmbd: fix potencial out-of-bounds when buffer offset is invalid
- ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()
- ksmbd: Fix spelling mistake "connction" -> "connection"
- ksmbd: fix possible null-deref in smb_lazy_parent_lease_break_close
- cifs: remove redundant variable assignment
- cifs: fixes for get_inode_info
- cifs: defer close file handles having RH lease
- ksmbd: add support for durable handles v1/v2
- ksmbd: mark SMB2_SESSION_EXPIRED to session when destroying previous session
- smb: common: simplify compression headers
- smb: common: fix fields sizes in compression_pattern_payload_v1
- smb: client: negotiate compression algorithms
- smb3: add dynamic trace point for ioctls
- smb: client: return reparse type in /proc/mounts
- smb: client: set correct d_type for reparse DFS/DFSR and mount point
- smb: client: parse uid, gid, mode and dev from WSL reparse points
- smb: client: introduce SMB2_OP_QUERY_WSL_EA
- smb: client: Fix a NULL vs IS_ERR() check in wsl_set_xattrs()
- smb: client: add support for WSL reparse points
- smb: client: reduce number of parameters in smb2_compound_op()
- smb: client: fix potential broken compound request
- smb: client: move most of reparse point handling code to common file
- smb: client: introduce reparse mount option
- smb: client: retry compound request without reusing lease
- smb: client: do not defer close open handles to deleted files
- smb: client: reuse file lease key in compound operations
- smb: client: get rid of smb311_posix_query_path_info()
- smb: client: parse owner/group when creating reparse points
- smb3: update allocation size more accurately on write completion
- smb: client: handle path separator of created SMB symlinks
- cifs: update the same create_guid on replay
- ksmbd: Add kernel-doc for ksmbd_extract_sharename() function
- cifs: set replay flag for retries of write command
- cifs: commands that are retried should have replay flag set
- smb: client: delete "true", "false" defines
- smb: Fix some kernel-doc comments
- cifs: new mount option called retrans
- smb: client: don't clobber ->i_rdev from cached reparse points
- cifs: new nt status codes from MS-SMB2
- cifs: pick channel for tcon and tdis
- cifs: minor comment cleanup
- cifs: remove redundant variable tcon_exist
- ksmbd: vfs: fix all kernel-doc warnings
- ksmbd: auth: fix most kernel-doc warnings
- cifs: remove unneeded return statement
- cifs: get rid of dup length check in parse_reparse_point()
- cifs: Pass unbyteswapped eof value into SMB2_set_eof()
- smb3: Improve exception handling in allocate_mr_list()
- cifs: fix in logging in cifs_chan_update_iface
- smb: client: handle special files and symlinks in SMB3 POSIX
- smb: client: cleanup smb2_query_reparse_point()
- smb: client: allow creating symlinks via reparse points
- smb: client: optimise reparse point querying
- smb: client: allow creating special files via reparse points
- smb: client: extend smb2_compound_op() to accept more commands
- smb: client: Fix minor whitespace errors and warnings
- smb: client: introduce cifs_sfu_make_node()
- cifs: fix use after free for iface while disabling secondary channels
- Missing field not being returned in ioctl CIFS_IOC_GET_MNT_INFO
- smb3: minor cleanup of session handling code
- smb3: more minor cleanups for session handling routines
- smb3: minor RDMA cleanup
- cifs: print server capabilities in DebugData
- smb: use crypto_shash_digest() in symlink_hash()
- Add definition for new smb3.1.1 command type
- SMB3: clarify some of the unused CreateOption flags
- cifs: Add client version details to NTLM authenticate message
- dist: remove usb-storage.ko and nouveau.ko when install private release
- dist: revert "add a modules-private rpm subpackage"
- Kconfig: add more modules
- Merge branch 'kasong/tk5/dist-optimization' into 'master' (merge request !106)
- dist: don't parse kernel version unless needed
- dist: optimize version parsing
- dist: stop using --show-toplevel for speed up

* Tue May 21 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.31-6
- Hygon: CSV3 patch series part 4 (Enable the concurrent memory allocation of CMA for Hygon CSV3) Merge pull request !173
- x86/mm: CSV allows CMA allocation concurrently
- mm/cma: add API to enable concurrent allocation from the CMA
- LoongArch: fix KASLR can not be disabled by nokaslr when boot from old BPI Merge pull request !153
- LoongArch: fix KASLR can not be disabled by nokaslr when boot from old BPI
- irqchip/loongson-pch-pic: Update interrupt registration policy
- Hygon: CSV3 patch series part 3 (Support live migration for Hygon CSV3 guest, and manage shared page by rbtree) Merge pull request !171
- x86/mm: Merge contiguous pages into a large range when notifying pages enc status changes
- KVM: SVM: CSV: Manage CSV3 guest's shared pages by rbtree
- KVM: SVM: CSV: Add ioctl API to unpin shared pages of CSV3 guest
- KVM: SVM: CSV: Add KVM_CSV3_RECEIVE_ENCRYPT_CONTEXT command
- KVM: SVM: CSV: Add KVM_CSV3_RECEIVE_ENCRYPT_DATA command
- KVM: SVM: CSV: Add KVM_CSV3_SEND_ENCRYPT_CONTEXT command
- KVM: SVM: CSV: Add KVM_CSV3_SEND_ENCRYPT_DATA command
- crypto: ccp: Define CSV3 migration command id
- Hygon:Support TKM function Merge pull request !164 from xisme/tkm
- crypto: ccp: Eliminate dependence of the kvm module on the ccp module
- Allow VM without a configured vid to use TKM
- support tkm key isolation
- Support tkm virtualization
- Support psp virtualization
- newfeature: crypto: ccp: Add psp mutex enable ioctl support
- newfeature: crypto: ccp: concurrent psp access support between user and kernel space
- Hygon: CSV3 patch series part 2 (launch and running support on both KVM and guest sides) Merge pull request !162
- x86/mm: Print CSV3 info into kernel log
- x86: Add support for changing the memory attribute for CSV3 guest
- x86: Update memory shared/private attribute in early boot for CSV3 guest
- x86/kernel: Set bss decrypted memory as shared in CSV3 guest
- x86/kernel: Add CSV3 early update(enc/dec)/reset memory helpers
- x86/boot/compressed/64: Add CSV3 update page attr(private/shared)
- x86/boot/compressed/64: Init CSV3 secure call pages
- x86/boot/compressed/64: Add CSV3 guest detection
- KVM: SVM: CSV: Manage CSV3 guest's nested page table
- KVM: SVM: CSV: Add KVM_CSV3_LAUNCH_ENCRYPT_VMCB command
- KVM: SVM: CSV: Add KVM_CSV3_LAUNCH_ENCRYPT_DATA command
- KVM: SVM: CSV: Add KVM_CSV3_INIT command
- KVM: Define CSV3 key management command id
- Hygon:Support TPM/TCM/TDM/TPCM function Merge pull request !160
- newfeature: linux: tcm: add Hygon TCM2 driver
- newfeature: linux: tpm: add Hygon TPM2 driver
- newfeature:crypto: tdm: Support dynamic protection for SCT and IDT by HYGON TDM
- newfeature: crypto: tdm: Add Hygon TDM driver
- Merge linux 6.6.31

* Fri May 17 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.30-5
- emm: update emm to v0.1.4
- config: enable CONFIG_SQUASHFS_ZSTD
- KVM: x86: Use actual kvm_cpuid.base for clearing KVM_FEATURE_PV_UNHALT
- KVM: x86: Introduce __kvm_get_hypervisor_cpuid() helper
- ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()
- ksmbd: fix potencial out-of-bounds when buffer offset is invalid
- KVM: x86: Virtualize HWCR.TscFreqSel[bit 24]
- KVM: x86: Allow HWCR.McStatusWrEn to be cleared once set
- cpustat: make get_iowait_time external

* Mon May 13 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.30-4
- 3snic：change sssnic kernel driver name Merge pull request !159 from cleanerleon/next
- change kernel driver name to sssnic
- Hygon: CSV3 patch series part 1 (Secure memory management and initialization) Merge pull request !157 from hanliyang/next_CSV3-host-cma-smr-smcr
- crypto: ccp: Add SET_SMR/SET_SMCR commands for CSV3
- x86/mm: Manage CSV3 guest's private memory by CMA
- crypto: ccp: Define CSV3 key management command id
- KVM: SEV: Pin SEV guest memory out of CMA area
- Hygon：Fixed bugs related to THP allocation and memory page migration Merge pull request !154 from hanliyang/next_mm-fix
- mm/gup: don't check if a page is in lru before draining it
- mm/page_alloc: don't use PCP list for THP-sized allocations when using PF_MEMALLOC_PIN
- Hygon: Support reuse ASID feature for Hygon CSV Merge pull request !156 from hanliyang/next_CSV-reuse-ASID
- KVM: SVM: Add support for different CSV guests to reuse the same ASID
- Hygon: Support passthru DCU to virtual machine Merge pull request !151 from hanliyang/next_hydcu
- drm/hygon: Add support to passthrough Hygon DCU to virtual machine
- Hygon: Some enhancement and bugfixes for HYGON SME/CSV/CSV2 Merge pull request !150 from hanliyang/next_SME_CSV1_CSV2_robust
- KVM: SVM: Unmap ghcb pages if they're still mapped when destroy guest
- anolis: x86/setup: Preserve _ENC flag when initrd is being relocated
- anolis: mm/early_ioremap.c: Always build early_memremap_prot() in x86
- KVM: x86: Fix KVM_GET_MSRS stack info leak
- KVM: SEV: Do not intercept accesses to MSR_IA32_XSS for SEV-ES guests
- x86/head/64: Flush caches for .bss..decrypted section after CR3 switches to early_top_pgt
- KVM: x86: Calls is_64_bit_hypercall() instead of is_64_bit_mode() in complete_hypercall_exit()
- x86/csv2: Keep in atomic context when holding ghcb page if the #VC comes from userspace
- KVM: SVM: Fix the available ASID range for CSV2 guest
- mm/unevictable: avoid root memcg calling mem_cgroup_scan_tasks to  trigger BUG_ON
- config: add SIMPLEFB and SIMPLEDRM

* Sat May 11 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.30-3
- config: add some drm configs to support more drm

* Thu May  9 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.30-2
- irqchip/loongson-pch-pic: Update interrupt registration policy
- Merge linux 6.6.30
- Merge linux 6.6.29
- Merge branch 'ock/next'
- !146 [next-6.6]kunpeng：Backport hns3 features and bugfixes Merge pull request !146 from hongrongxuan/linux-6.6/next-ronson-dev
- net: hns3: add support for Hisilicon ptp sync device
- net: hns3: fix port vlan filter not disabled problem in dynamic vlan mode
- net: hns3: default select PAGE_POOL_STATS
- net: hns3: fix kernel crash when devlink reload during vf initialization
- net: hns3: support set/get VxLAN rule of rx flow director by ethtool
- net: ethtool: add VxLAN to the NFC API
- net: hns3: Add support for some CMIS transceiver modules
- net: sfp: Synchronize some CMIS transceiver modules from ethtool
- net: hns3: add command queue trace for hns3
- net: hns3: dump more reg info based on ras mod
- net: hns3: add support for page_pool_get_stats
- net: hns3: add support to query scc version by devlink info
- net: hns3: correct the logic of hclge_sync_vf_qb_mode()
- net: hns3: add support for FD counter
- net: hns3: allocate fd counter for queue bonding
- net: hns3: refactor the debugfs for dumping FD tcam
- net: hns3: add queue bonding mode support for VF
- net: hns3: add support for queue bonding mode of flow director
- net: hns3: add checking for vf id of mailbox
- net: hns3: fix reset timeout under full functions and queues
- net: hns3: fix delete tc fail issue
- net: hns3: Disable SerDes serial loopback for HiLink H60
- net: hns3: add new 200G link modes for hisilicon device
- net: hns3: add input parameters checking
- net: hns3: add extend interface support for read and write phy register
- net: hns3: add support set led
- net: hns3: add support set mac state
- net: hns3: add support detect port wire type
- net: hns3: add support PF provides customized interfaces to detect port faults.
- net: hns3: support set pfc pause trans time
- net: hns3: add support disable nic clock
- net: hns3: add support config and query serdes lane status
- net: hns3: add supports configure optical module enable
- net: hns3: add support query the presence of optical module
- net: hns3: add support modified tx timeout
- net: hns3: add support query port ext information
- net: hns3: add support configuring function-level interrupt affinity
- net: hns3: add support clear mac statistics
- net: hns3: add support to get/set 1d torus param
- net: hns3: add supports fast reporting of faulty nodes
- net: hns3: add supports pfc storm detection and suppression
- net: hns3: add support customized exception handling interfaces
- net: hns3: add some link modes for hisilicon device
- net: hns3: add vf fault detect support
- net: hns3: add hns3 vf fault detect cap bit support
- kunpeng：Backport some bugfixes for hisi_sas Merge pull request !143 from chenyi/linux-6.6/next-cy-dev
- scsi: hisi_sas: Modify the deadline for ata_wait_after_reset()
- scsi: hisi_sas: Remove hisi_hba->timer for v3 hw
- scsi: hisi_sas: Check whether debugfs is enabled before removing or releasing it
- scsi: libsas: Allocation SMP request is aligned to ARCH_DMA_MINALIGN
- scsi: hisi_sas: Fix the deadlock issue that occurs during automatic dump
- scsi: hisi_sas: Handle the NCQ error returned by D2H frame
- scsi: hisi_sas: Remove redundant checks for automatic debugfs dump
- scsi: hisi_sas: Allocate DFX memory during dump trigger
- scsi: hisi_sas: Directly call register snapshot instead of using workqueue
- scsi: hisi_sas: Check usage count only when the runtime PM status is RPM_SUSPENDING
- scsi: hisi_sas: Add slave_destroy interface for v3 hw
- Revert "scsi: hisi_sas: Disable SATA disk phy for severe I_T nexus reset failure"
- Hygon:Update ccp-crypto driver to support Hygon 4th CPU & add hct.ko module which needed by HCT engine Merge pull request !149 from partyCoder/next
- Commit Message: Support 1024 processes simutaneously in the hct-mdev mode.
- Commit Message: Change the maximum number of supported ccps from 16 to 48.
- Commit Message: Compiling hct.ko when the module mdev is disabled.
- ccp: supporting memory encryption features for host vfio-noiommu mode, and wb attribute for the bar memory of virtual machine.
- Add mediated ccp driver support for hygon crypto technology.
- ccp: ccp-crypto support sm2 on Hygon generation 4th CPU
- Hygon:Support CSV(2) guest attestation, CSV firmware update, CSV(2) guest migration, CSV(2) guest reboot, x86-psp communicate interfaces Merge pull request !148 from hanliyang/next
- KVM: SVM: Force flush caches before reboot CSV guest
- KVM: SVM: Add support for rebooting CSV2 guest
- KVM: x86: Introduce control_{pre,post}_system_reset ioctl interfaces
- KVM: SVM: Export MSR_AMD64_SEV_ES_GHCB to userspace for CSV2 guest
- KVM: x86: Restore control registers in __set_sregs() to support CSV2 guest live migration
- KVM: SVM: Add KVM_SEV_RECEIVE_UPDATE_VMSA command
- KVM: SVM: Add KVM_SEV_SEND_UPDATE_VMSA command
- crypto: ccp: Fix definition of struct sev_data_send_update_vmsa
- crypto: ccp: Add another mailbox interrupt support for PSP sending command to X86
- crypto: ccp: Add a new interface for X86 sending command to PSP
- KVM: SVM: Add RECEIVE_UPDATE_DATA command helper to support KVM_CSV_COMMAND_BATCH
- KVM: SVM: Add SEND_UPDATE_DATA command helper to support KVM_CSV_COMMAND_BATCH
- KVM: SVM: Prepare memory pool to allocate buffers for KVM_CSV_COMMAND_BATCH
- KVM: SVM: Add KVM_CSV_COMMAND_BATCH command for applying CSV RING_BUFFER mode
- crypto: ccp: Add support for issue commands in CSV RING_BUFFER mode
- crypto: ccp: Add support to switch to CSV RING_BUFFER mode
- crypto: ccp: Add support for dequeue status in CSV RING_BUFFER mode
- crypto: ccp: Add support for enqueue command pointers in CSV RING_BUFFER mode
- crypto: ccp: Introduce init and free helpers to manage CSV RING_BUFFER queues
- crypto: ccp: Implement CSV_DOWNLOAD_FIRMWARE ioctl command
- crypto: ccp: Implement CSV_PLATFORM_SHUTDOWN ioctl command
- crypto: ccp: Implement CSV_PLATFORM_INIT ioctl command
- crypto: ccp: Support DOWNLOAD_FIRMWARE when detect CSV
- driver/virt/coco: Add HYGON CSV Guest dirver.
- KVM: x86: Support VM_ATTESTATION hypercall
- Montage：add support for Montage Mont-TSSE Driver Merge pull request !147 from carrie.cai/next
- add support for Montage Mont-TSSE driver
- Support PSP identification for Hygon 4th CPU and print secure features when running on Hygon CPUs Merge pull request !144 from hanliyang/next_ident-hygon-cc-all-others
- x86/config: Set CONFIG_HYGON_CSV by default
- x86/cpu/hygon: Clear SME feature flag when not in use
- x86/cpufeatures: Add CSV3 CPU feature
- x86/cpufeatures: Add CPUID_8C86_0000_EDX CPUID leaf
- x86/cpu: Detect memory encryption features on Hygon CPUs
- KVM: SVM: Print Hygon CSV support info if support is detected
- crypto: ccp: Print Hygon CSV API version when CSV support is detected
- x86/mm: Print CSV info into the kernel log
- x86/mm: Provide a Kconfig entry to build the HYGON memory encryption support into the kernel
- Documentation/arch/x86: Add HYGON secure virtualization description
- crypto: ccp: Add support to detect CCP devices on Hygon 4th CPUs
- !141 add 3snic 3s9xx NIC driver Merge pull request !141 from cleanerleon/next
- add 3snic 3s9xx driver
- Hyper-V: support Hyper-V synthetic video device
- amdkfd: use calloc instead of kzalloc to avoid integer overflow
- emm: add submodule of emm
- block: fix deadlock between bd_link_disk_holder and partition scan
- md: fix kmemleak of rdev->serial
- Kconfig: delete intel atom and apple human interface device support
- driver: compile mdev.ko by default
- Kconfig: update many tencent.config of x86
- driver: make regmap-mmio.c compiled in by default
- net/proc: added sockets details statistics
- net: rps using pvipi
- smp: introduce a new interface smp_call_function_many_async
- virtio_net: disable napi_tx by default
- tcp: backport two patch from tk4 about gso
- Merge linux 6.6.28
- Merge linux 6.6.27
- dist: config: add LOCALVERSION="+debug" for debug config
- config: enable CONFIG_DEBUG_INFO_BTF in eks config
- exit: wait_task_zombie: kill the no longer necessary spin_lock_irq(siglock)
- fs/proc: do_task_stat: use sig->stats_lock to gather the threads/children stats
- fs/proc: do_task_stat: use __for_each_thread()
- net: ip_tunnel: prevent perpetual headroom growth
- dist: ensure release start with decimal number
- dist: sanitize usage of unamer
- dist: add missing place holder for loongarch64 kabi
- emm/oversell: fix memsw page counter

* Wed Apr 17 2024 Jianping Liu <frankjpliu@tencent.com> - 6.6.26-1
- SUNRPC: discard sv_refcnt, and svc_get/svc_put
- svc: don't hold reference for poolstats, only mutex.
- config: support phytium soc and ampereone pmu
- sched/eevdf: fix soft lockup while __pick_eevdf failed
- Merge linux 6.6.26
- Merge linux 6.6.25
- Merge linux 6.6.24
- Merge linux 6.6.23
- Merge linux 6.6.22
- Merge linux 6.6.21
- x86/perf: Add PMU uncore support for Zhaoxin CPU
- BeiZhongWangXin:Add Chengdu BeiZhongWangXin Technology N5/N6 Series Network Card Driver
- Hygon：Add HGSC_CERT_IMPORT ioctl interface for Hygon CPUs.
- Loogarch:add steal time hypcall software breakpoint pmu support for loongarch kvm
- Add Phytium Display Engine support to the linux-6.6
- Intel: Backport QuickAssist Technology(QAT) in-tree driver
- Loongarch: support loongarch and add kvm support for loongarch
- platform/x86/intel/ifs: Call release_firmware() when handling errors.
- crypto: ccp: Add support to detect Hygon PSP on Hygon 2nd/3rd CPUs
- crypto: ccp: Fixup the capability of Hygon PSP during initialization
- Support zhaoxin cpu
- zhaoxin: Fix CRC32C instruction low performance issue
- crypto: x86/crc32c-intel Exclude low performance CRC32C instruction CPUs
- x86/cpu: Set low performance CRC32C flag on some Zhaoxin CPUs
- x86/cpufeatures: Add low performance CRC32C instruction CPU feature
- ALSA: hda: Add support of Zhaoxin SB HDAC
- x86/cpu: Add detect extended topology for Zhaoxin CPUs
- x86/cpufeatures: Add Zhaoxin feature bits
- btrfs: fix double free of anonymous device after snapshot creation failure
- arm64: Work around Ampere Altra erratum #82288 PCIE_65
- rue/io: fix blkcg_dkstats_show_comm implicit declaration error
- emm: fix compile error of MEMCG_ZRAM_B undeclared
- tcp/dccp: add support for port usage in proportion to allocation
- cgroup: add cgroup.id to show each css id within a cgroup
- tcp: fix issues when enabling tcp_wan_timestamps feature.
- tcp: initialize sysctl_tcp_wan_timestamps to 1 by default.
- net: add net.ipv4.tcp_wan_timestamps sysctl to switch timestamps function
- mm/workingset: fix compile error when using allyesconfig in aarch64
- ck: mm: Pin code section of process in memory
- mm, oom_kill: introduce oom_kill_largest_task sysctl interface
- emm: configs: enabled EMM related configs
- emm: memcg/reclaim: adapt for enhanced memory reclaim interface
- emm: memcg/reclaim: add support for enhanced memory reclaim
- emm: memcg: add support for core memcg handling
- emm: mm: support forcing swappiness for global reclaim
- emm: mm: Kconfig: add EMM config
- emm: memcg, zram: add support for ZRAM memory accounting
- ocfs2: Avoid touching renamed directory if parent does not change
- rue/scx/sched_ext: Add a basic, userland vruntime scheduler
- rue/scx/sched_ext: Implement core-sched support
- rue/scx/sched_ext: Implement sched_ext_ops.cpu_online/offline()
- rue/scx/sched_ext: Implement sched_ext_ops.cpu_acquire/release()
- rue/scx/sched_ext: Implement runnable task stall watchdog
- rue/scx/sched_ext: Implement BPF extensible scheduler class
- script: update check-kabi script
- kabi: provide kabi check/update/create commands for local users
- config: add kernel/configs/tkci.config
- pci: bypass NVMe when booting PCIe storage with 5s delay
- pci: prohibit storage probe delay of virtio block device
- pci: delay 5s to proble multiple storage controllers
- perf vendor events arm64 AmpereOneX: Add core PMU events and metrics
- KVM: arm64: Always invalidate TLB for stage-2 permission faults
- KVM: arm64: Avoid soft lockups due to I-cache maintenance
- arm64: tlbflush: Rename MAX_TLBI_OPS
- docs/perf: Add ampere_cspmu to toctree to fix a build warning
- perf: arm_cspmu: ampere_cspmu: Add support for Ampere SoC PMU
- perf: arm_cspmu: Support implementation specific validation
- perf: arm_cspmu: Support implementation specific filters
- perf: arm_cspmu: Split 64-bit write to 32-bit writes
- perf: arm_cspmu: Separate Arm and vendor module
- x86 and arm64 config: add more module config
- config: enable slub debug as default in debug.config
- config: enable CONFIG_HARDLOCKUP_DETECTOR
- Add support for Hygon model 4h~6h processors Merge
- Intel: Backport GNR/SRF PMU uncore support to kernel v6.6
- Intel: Backport SRF/GRR perf cstate support to kernel v6.6
- Intel: Backport SRF LBR branch counter support to kernel v6.6
- Intel-SIG: microcode restructuring backport Merge pull request
- Intel-SIG: backport cluster scheduler wakeup optimization
- SAF & Array BIST support for GNR & SRF
- RDT non-contiguous CBM support

* Wed Dec 20 2023 Kairui Song <kasong@tencent.com> - 6.6.6-2401.0.1
- kabi: freeze kabi for x86_64 and arm64
- x86/mpparse, kexec: switch apic driver early when x2apic is pre-enabled
- tracing: workaround UAF caused by memory ordering issue
- mm/slub.c: sanitize freelist pointer assignment even more
- mm/slub.c: fix a potential UAF
- cgroup: use a standalone workqueue for killing css
- mm/vmscan.c: add cond_resched function call into __shrink_page_cache
- swap: expose required symbols for some 3rd part modules
- swapfile: add a helper get_cached_swap_page_of_type
- mm: memcg: introduce v2's interface to v1
- psi: only show SOME PSI for non-IRQ in cgroup v1
- psi: support cgroup v1 psi accounting
- psi: expose cgroup v1 interface for psi
- psi: link legacy root to psi_system
- sched/psi: simplify cgroup psi retrieving
- arm64: fake a reliable stacktrace for livepath
- arm64: enable livepatch without stable stacktrace
- arm64: basic infrastructure for livepatch
- pagecachelimit: limit the pagecache ratio of totalram
- blkcg: add buffer IO throttle for cgroup v1
- cgroupfs: support stat based on cpuacct
- cgroupfs: fix non inited i_ino when inode created
- cgroupfs: add files inside sys
- cgroupfs: support for proc and sys
- cgroupfs: quota aware support
- cgroupfs: refactor cgroup resource statistics for reuse
- memcg: make meminfo optionally recursive and rework
- memcg: add meminfo and vmstat show
- cpuset: add switch support for cpuset.stat in container
- cpuset: fix cpuset.stat process field value exception
- cpuset: add switch for cpuinfo in container
- cpuset: add loadavg calc for each container
- cpuset: add cpuinfo and stat show
- sysfs: add sysfs attribute to hide disk devices
- blkcg/diskstats/dm: add support for blkcg diskstats
- blkcg/diskstats/md: add support for blkcg diskstats
- blkcg/diskstats: add per blkcg diskstats support
- ext4: Add an error info during new_inode
- ext4: fix soft lockup caused by sbi->s_es_lru
- ceph: add mds request pid info into debugfs
- ceph: Add new mount option req_resend
- ceph: re-send osd requests if timeout
- nvme: add the hotplug info output about drive letter and BDF
- nbd: add the nbd_ignore_blksize_set support
- xfs: add kmem_alloc_by_vmalloc and kmem_alloc_large_dump_stack sysctl
- xfs: set xfs default error level to 5
- ceph: add sysctl to ignore error epoch barrier
- ext3: set nobarrier as default
- block: check whether queue is NULL or not in stats functions
- net: modify default value of host max_orphan
- net: namespaceify sysctl_tcp_max_orphans
- vm: isolate max_map_count by pid namespace
- cpuacct: get the uptime of container
- proc: add pid mapping between host and container
- taskstats: expose taskstats to all netspace
- tcp: make TCP_RTO_MIN/MAX be tunable
- tcp: support self define parameter to tune rto of syn/synack packets
- tcp: introduce sysctl tcp_inherit_buffsize
- net: ipv6 neigh tunnel bypass
- net: add sysctl to control page frag
- net: add sriov debug info
- net: increase tcp listen hash
- tcp: add TCP_FULLNAT_REAL setsockopt options for fullnat real ip
- net: reduce the confliction while multi threads connecting same host
- bonding: add broadcast_arp param to send arp broadcast
- netlink: don't modprobe proto audit & selinux
- tcp: add proc parameter to change init cwnd
- net: add tcp_no_delay_ack to enable absolute quick ack
- tcp: add tcp_loss_init_cwnd sysctl to tunnel packet numbers in loss
- network: default zero bond_devices to support
- tcp: double the default value of thash_entries
- tcp: backoff the commit allowing timestamps even if SYN packet has tsval=0
- net: dev ipv4/v6 stat
- net: add tcp drop stats
- ipmi: set kipmid_max_busy_us default to 1
- sched: adaptive default skew_tick value
- ipc/msg: increase defaults for shmmall, shmmax, msgmax and msgmnb
- mm: increase dirty-ratio from 20 to 40
- tkernel: netfilter: conntrack: add netagent extention slot
- tkernel: net: add toa support
- tkernel: mounts: add shield mountpoint in container support
- tkernel: netatop: add netatop module in kernel/tkernel/
- tkernel: ttools: add ttools module to support ptrace protect
- tkernel: initial support and nonpriv_bind
- sysrq: add ALT+LEFTCTRL to trigger crash dump
- kabi: add paddings and optimize (part 3)
- kabi: add paddings (part 2)
- kabi: add paddings (part 1)
- kabi: add kabi.h
- kabi: modules: better vermagic check on module load
- config: update config for ocks-2401
- dist: config: update config from ocks-2303
- dist: config: add default config files
- dist: fix script checker
- dist: tools/vm -> tools/mm
- dist: move libcpupower.so to kernel-libs
- dist: initial support
- Linux 6.6.6

