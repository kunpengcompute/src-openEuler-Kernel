%define with_signmodules  1
%define with_kabichk 0

# Default without toolchain_clang
%bcond_with toolchain_clang

%if %{with toolchain_clang}
%global toolchain clang
%endif

%bcond_with clang_lto

%if %{with clang_lto} && "%{toolchain}" != "clang"
{error:clang_lto requires --with toolchain_clang}
%endif

%define modsign_cmd %{SOURCE10}

%if 0%{?openEuler_sign_rsa}
# Use the open-source signature when the EBS permission is insufficient.
# Now only the admin user in EBS can send the signature request. But the
# user triggering the acces control build task and the personal build
# task is non-admin. Inorder to avoid build failures caused by failed
# signing, use the open-source signature.
# The flag_openEuler_has_sign_perm used in the rpm execution phase
# The openEuler_has_sign_perm used in the rpm execution phase

%define openEuler_check_EBS_perm openEuler_has_sign_perm=0 \
echo "" >> test_openEuler_sign.ko \
sh /usr/lib/rpm/brp-ebs-sign --module test_openEuler_sign.ko || \
[ $? -ne 2 ] && openEuler_has_sign_perm=1 \
%global flag_openEuler_has_sign_perm $openEuler_has_sign_perm \
rm -f test_openEuler_sign.ko test_openEuler_sign.ko.sig
%endif

%global Arch $(echo %{_host_cpu} | sed -e s/i.86/x86/ -e s/x86_64/x86/ -e s/aarch64.*/arm64/ -e s/riscv.*/riscv/ -e s/powerpc64le/powerpc/ -e s/loongarch64/loongarch/)

%global KernelVer %{version}-%{release}.%{_target_cpu}
%global debuginfodir /usr/lib/debug

%global upstream_version    6.6
%global upstream_sublevel   0
%global devel_release       72
%global maintenance_release .1.0
%global pkg_release         .5
%global rt_release          .rt30

%define with_debuginfo 1
# Do not recompute the build-id of vmlinux in find-debuginfo.sh
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%undefine _include_minidebuginfo
%undefine _include_gdb_index
%undefine _unique_build_ids

%define with_source 1

%define with_python2 0

# failed if there is new config options
%define listnewconfig_fail 0

%ifarch aarch64
%define with_64kb  %{?_with_64kb: 1} %{?!_with_64kb: 0}
%if %{with_64kb}
%global package64kb -64kb
%endif
%else
%define with_64kb  0
%endif

#default is enabled. You can disable it with --without option
%define with_perf    %{?_without_perf: 0} %{?!_without_perf: 1}

Name:	 kernel-rt%{?package64kb}
Version: %{upstream_version}.%{upstream_sublevel}
Release: %{devel_release}%{?maintenance_release}%{?rt_release}%{?pkg_release}
Summary: Linux Kernel
License: GPLv2
URL:	 http://www.kernel.org/
Source0: kernel.tar.gz
Source10: sign-modules
Source11: x509.genkey
Source12: extra_certificates

%if 0%{?openEuler_sign_rsa}
Source15: openeuler_kernel_cert.cer
Source16: sign-modules-openeuler
%endif

%if 0%{?with_kabichk}
Source18: check-kabi
Source20: Module.kabi_aarch64
Source21: Module.kabi_x86_64
%endif

Source200: mkgrub-menu-aarch64.sh

Source2000: cpupower.service
Source2001: cpupower.config

%if 0%{?with_patch}
Source9000: apply-patches
Source9001: guards
Source9002: series.conf
Source9998: patches.tar.bz2
%endif

Patch0002: 0002-cpupower-clang-compile-support.patch
Patch0003: 0003-x86_energy_perf_policy-clang-compile-support.patch
Patch0004: 0004-turbostat-clang-compile-support.patch
Patch0: patch-6.6.0-6.0.0-rt20.patch
Patch1: patch-6.6.0-6.0.0-rt20.patch-openeuler_defconfig.patch
#BuildRequires:
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: libcap-devel, libcap-ng-devel, rsync
BuildRequires: gcc >= 3.4.2, binutils >= 2.12
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl-devel openssl
BuildRequires: hmaccalc
BuildRequires: ncurses-devel
#BuildRequires: pesign >= 0.109-4
BuildRequires: elfutils-libelf-devel
BuildRequires: rpm >= 4.14.2
#BuildRequires: sparse >= 0.4.1
%if 0%{?with_python2}
BuildRequires: python-devel
%endif

BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison
BuildRequires: audit-libs-devel libpfm-devel libtraceevent-devel
BuildRequires: pciutils-devel gettext
BuildRequires: rpm-build, elfutils
BuildRequires: numactl-devel python3-devel glibc-static python3-docutils
BuildRequires: perl-generators perl(Carp) libunwind-devel gtk2-devel libbabeltrace-devel java-1.8.0-openjdk java-1.8.0-openjdk-devel perl-devel

AutoReq: no
AutoProv: yes

Conflicts: device-mapper-libs < 1.02.63-2 e2fsprogs < 1.37-4 initscripts < 7.23 iptables < 1.3.2-1
Conflicts: ipw2200-firmware < 2.4 isdn4k-utils < 3.2-32 iwl4965-firmware < 228.57.2 jfsutils < 1.1.7-2
Conflicts: mdadm < 3.2.1-5 nfs-utils < 1.0.7-12 oprofile < 0.9.1-2 ppp < 2.4.3-3 procps < 3.2.5-6.3
Conflicts: reiserfs-utils < 3.6.19-2 selinux-policy-targeted < 1.25.3-14 squashfs-tools < 4.0
Conflicts: udev < 063-6 util-linux < 2.12 wireless-tools < 29-3 xfsprogs < 2.6.13-4

Provides: kernel-rt-%{_target_cpu} = %{version}-%{release} kernel-rt-drm = 4.3.0 kernel-rt-drm-nouveau = 16 kernel-rt-modeset = 1
Provides: kernel-rt-uname-r = %{KernelVer} kernel-rt=%{KernelVer}

Requires: dracut >= 001-7 grubby >= 8.28-2 initscripts >= 8.11.1-1 linux-firmware >= 20100806-2 module-init-tools >= 3.16-2

ExclusiveArch: noarch aarch64 i686 x86_64 riscv64 ppc64le loongarch64
ExclusiveOS: Linux

%if %{with_perf}
BuildRequires: flex xz-devel libzstd-devel
BuildRequires: java-devel
%ifarch aarch64
BuildRequires: OpenCSD
%endif
%endif

BuildRequires: dwarves
BuildRequires: clang >= 10.0.0
BuildRequires: llvm
BuildRequires: llvm-devel
%if %{with clang_lto}
BuildRequires: lld
%endif

%description
The Linux Kernel, the operating system core itself.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.


%package devel
Summary: Development package for building kernel modules to match the %{KernelVer} kernel
AutoReqProv: no
Provides: kernel-rt-devel-uname-r = %{KernelVer}
Provides: kernel-rt-devel-%{_target_cpu} = %{version}-%{release}
Requires: perl findutils

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the %{KernelVer} kernel package.

%package tools
Summary: Assortment of tools for the Linux kernel
Provides: %{name}-tools-libs
Obsoletes: %{name}-tools-libs
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
%description tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package tools-devel
Summary: Assortment of tools for the Linux kernel
Requires: %{name}-tools = %{version}-%{release}
Requires: %{name}-tools-libs = %{version}-%{release}
Provides: %{name}-tools-libs-devel = %{version}-%{release}
Obsoletes: %{name}-tools-libs-devel
%description tools-devel
This package contains the development files for the tools/ directory from
the kernel source.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%if 0%{?with_python2}
%package -n python2-perf
Provides: python-perf = %{version}-%{release}
Obsoletes: python-perf
Summary: Python bindings for apps which will manipulate perf events

%description -n python2-perf
A Python module that permits applications written in the Python programming
language to use the interface to manipulate perf events.
%endif

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
%description -n python3-perf
A Python module that permits applications written in the Python programming
language to use the interface to manipulate perf events.
# with_perf
%endif

%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package source
Summary: the kernel source
%description source
This package contains vaious source files from the kernel.

%if 0%{?with_debuginfo}
%define _debuginfo_template %{nil}
%define _debuginfo_subpackages 0

%define debuginfo_template(n:) \
%package -n %{-n*}-debuginfo\
Summary: Debug information for package %{-n*}\
Group: Development/Debug\
AutoReq: 0\
AutoProv: 1\
%description -n %{-n*}-debuginfo\
This package provides debug information for package %{-n*}.\
Debug information is useful when developing applications that use this\
package or when debugging this package.\
%{nil}

%debuginfo_template -n kernel-rt
%files -n kernel-rt-debuginfo -f kernel-debugfiles.list -f debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} --keep-section '.BTF' -p '.*/%{KernelVer}/.*|.*/vmlinux|XXX' -o kernel-debugfiles.list}

%debuginfo_template -n bpftool
%files -n bpftool-debuginfo -f bpftool-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_sbindir}/bpftool.*(\.debug)?|XXX' -o bpftool-debugfiles.list}

%debuginfo_template -n kernel-rt-tools
%files -n kernel-rt-tools-debuginfo -f kernel-tools-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_bindir}/centrino-decode.*(\.debug)?|.*%{_bindir}/powernow-k8-decode.*(\.debug)?|.*%{_bindir}/cpupower.*(\.debug)?|.*%{_libdir}/libcpupower.*|.*%{_libdir}/libcpupower.*|.*%{_bindir}/turbostat.(\.debug)?|.*%{_bindir}/.*gpio.*(\.debug)?|.*%{_bindir}/.*iio.*(\.debug)?|.*%{_bindir}/tmon.*(.debug)?|XXX' -o kernel-tools-debugfiles.list}

%if %{with_perf}
%debuginfo_template -n perf
%files -n perf-debuginfo -f perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_bindir}/perf.*(\.debug)?|.*%{_libexecdir}/perf-core/.*|.*%{_libdir}/traceevent/.*|XXX' -o perf-debugfiles.list}

%if 0%{?with_python2}
%debuginfo_template -n python2-perf
%files -n python2-perf-debuginfo -f python2-perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{python2_sitearch}/perf.*(.debug)?|XXX' -o python2-perf-debugfiles.list}
%endif

%debuginfo_template -n python3-perf
%files -n python3-perf-debuginfo -f python3-perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{python3_sitearch}/perf.*(.debug)?|XXX' -o python3-perf-debugfiles.list}
#with_perf
%endif

%endif

%prep
%setup -q -n kernel-%{version} -c

%if 0%{?with_patch}
tar -xjf %{SOURCE9998}
%endif

mv kernel linux-%{KernelVer}
cd linux-%{KernelVer}

%if 0%{?with_patch}
cp %{SOURCE9000} .
cp %{SOURCE9001} .
cp %{SOURCE9002} .

if [ ! -d patches ];then
    mv ../patches .
fi

Applypatches()
{
    set -e
    set -o pipefail
    local SERIESCONF=$1
    local PATCH_DIR=$2
    sed -i '/^#/d'  $SERIESCONF
    sed -i '/^[\s]*$/d' $SERIESCONF
    (
        echo "trap 'echo \"*** patch \$_ failed ***\"' ERR"
        echo "set -ex"
        cat $SERIESCONF | \
        sed "s!^!patch -s -F0 -E -p1 --no-backup-if-mismatch -i $PATCH_DIR/!" \
    ) | sh
}

Applypatches series.conf %{_builddir}/kernel-%{version}/linux-%{KernelVer}
%endif

%if "%toolchain" == "clang"
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%endif
%patch0 -p1
%patch1 -p1

find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null
find . -name .gitignore -exec rm -f {} \; >/dev/null

%if 0%{?with_signmodules}
    cp %{SOURCE11} certs/.
%endif

%if 0%{?with_source}
# Copy directory backup for kernel-source
cp -a ../linux-%{KernelVer} ../linux-%{KernelVer}-source
find ../linux-%{KernelVer}-source -type f -name "\.*" -exec rm -rf {} \; >/dev/null
%endif

cp -a tools/perf tools/python3-perf

%build
cd linux-%{KernelVer}

perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}/" Makefile

## make linux
make mrproper %{_smp_mflags}

%if %{with_64kb}
sed -i arch/arm64/configs/openeuler_defconfig -e 's/^CONFIG_ARM64_4K_PAGES.*/CONFIG_ARM64_64K_PAGES=y/'
sed -i arch/arm64/configs/openeuler_defconfig -e 's/^CONFIG_ARM64_PA_BITS=.*/CONFIG_ARM64_PA_BITS=52/'
sed -i arch/arm64/configs/openeuler_defconfig -e 's/^CONFIG_ARM64_PA_BITS_.*/CONFIG_ARM64_PA_BITS_52=y/'
sed -i arch/arm64/configs/openeuler_defconfig -e 's/^CONFIG_ARM64_VA_BITS=.*/CONFIG_ARM64_VA_BITS=52/'
sed -i arch/arm64/configs/openeuler_defconfig -e 's/^CONFIG_ARM64_VA_BITS_.*/CONFIG_ARM64_VA_BITS_52=y/'
%endif

%if "%toolchain" == "clang"

%ifarch s390x ppc64le
%global llvm_ias 0
%else
%global llvm_ias 1
%endif

%global clang_make_opts HOSTCC=clang CC=clang LLVM_IAS=%{llvm_ias}

%if %{with clang_lto}
%global clang_make_opts %{clang_make_opts} HOSTLD=ld.lld LD=ld.lld AR=llvm-ar NM=llvm-nm HOSTAR=llvm-ar HOSTNM=llvm-nm
%endif

%endif

%global make %{__make} %{?clang_make_opts} HOSTCFLAGS="%{?build_cflags}" HOSTLDFLAGS="%{?build_ldflags}"

%ifarch loongarch64

%if 0%{with_signmodules}
echo "CONFIG_MODULE_SIG=y" >>arch/loongarch/configs/loongson3_defconfig
%endif

%if 0%{with_debuginfo}
echo "CONFIG_DEBUG_INFO=y" >>arch/loongarch/configs/loongson3_defconfig
%endif

make ARCH=%{Arch} loongson3_defconfig

%else
%{make} ARCH=%{Arch} openeuler_defconfig
%endif

%if %{with clang_lto}
scripts/config -e LTO_CLANG_FULL
sed -i 's/# CONFIG_LTO_CLANG_FULL is not set/CONFIG_LTO_CLANG_FULL=y/' .config
sed -i 's/CONFIG_LTO_NONE=y/# CONFIG_LTO_NONE is not set/' .config
%endif

%if 0%{?openEuler_sign_rsa}
    %{openEuler_check_EBS_perm}
    if [ $openEuler_has_sign_perm -eq 1 ]; then
        cp %{SOURCE15} ./certs/openeuler-cert.pem
    # close kernel native signature
        sed -i 's/CONFIG_MODULE_SIG_KEY=.*$/CONFIG_MODULE_SIG_KEY=""/g' .config
        sed -i 's/CONFIG_SYSTEM_TRUSTED_KEYS=.*$/CONFIG_SYSTEM_TRUSTED_KEYS="certs\/openeuler-cert.pem"/g' .config
        sed -i 's/CONFIG_MODULE_SIG_ALL=y$/CONFIG_MODULE_SIG_ALL=n/g' .config
    fi
%endif

TargetImage=$(basename $(make -s image_name))

%{make} ARCH=%{Arch} $TargetImage %{?_smp_mflags}
%{make} ARCH=%{Arch} modules %{?_smp_mflags}

%if 0%{?with_kabichk}
    chmod 0755 %{SOURCE18}
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu} ]; then
        %{SOURCE18} -k $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu} -s Module.symvers || exit 1
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

# aarch64 make dtbs
%ifarch aarch64 riscv64
    %{make} ARCH=%{Arch} dtbs
%endif

## make tools
%if %{with_perf}
# perf
%ifarch aarch64
# aarch64 make perf with CORESIGHT=1
%global perf_make \
    make %{?clang_make_opts} EXTRA_LDFLAGS="%[ "%{toolchain}" == "clang" ? "-z now" : "" ]" EXTRA_CFLAGS="%[ "%{toolchain}" == "clang" ? "" : "-Wl,-z,now" ] -g -Wall -fstack-protector-strong -fPIC" EXTRA_PERFLIBS="-fpie -pie" %{?_smp_mflags} -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 CORESIGHT=1 prefix=%{_prefix}
%else
%global perf_make \
    make %{?clang_make_opts} EXTRA_LDFLAGS="%[ "%{toolchain}" == "clang" ? "-z now" : "" ]" EXTRA_CFLAGS="%[ "%{toolchain}" == "clang" ? "" : "-Wl,-z,now" ] -g -Wall -fstack-protector-strong -fPIC" EXTRA_PERFLIBS="-fpie -pie" %{?_smp_mflags} -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 prefix=%{_prefix}
%endif
%if 0%{?with_python2}
%global perf_python2 -C tools/perf PYTHON=%{__python2}
%global perf_python3 -C tools/python3-perf PYTHON=%{__python3}
%else
%global perf_python3 -C tools/perf PYTHON=%{__python3}
%endif

chmod +x tools/perf/check-headers.sh
# perf
%if 0%{?with_python2}
%{perf_make} %{perf_python2} all
%endif

# make sure check-headers.sh is executable
chmod +x tools/python3-perf/check-headers.sh
%{perf_make} %{perf_python3} all

pushd tools/perf/Documentation/
%{make} %{?_smp_mflags} man
popd
%endif

# bpftool
pushd tools/bpf/bpftool
%{make}
popd

# cpupower
chmod +x tools/power/cpupower/utils/version-gen.sh
%{make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch %{ix86} x86_64
    pushd tools/power/x86/x86_energy_perf_policy/
    %{make}
    popd
    pushd tools/power/x86/turbostat
    %{make}
    popd
%endif
# thermal
pushd tools/thermal/tmon/
%{make}
popd
# iio
pushd tools/iio/
%{make}
popd
# gpio
pushd tools/gpio/
%{make}
popd
# kvm
pushd tools/kvm/kvm_stat/
%{make} %{?_smp_mflags} man
popd
# libbpf.a and bpf_helper_defs.h
pushd tools/lib/bpf
%{make}
popd
# netacc
pushd tools/netacc
%{make} BPFTOOL=../../tools/bpf/bpftool/bpftool
popd

%install
%if 0%{?with_source}
    %define _python_bytecompile_errors_terminate_build 0
    mkdir -p $RPM_BUILD_ROOT/usr/src/
    mv linux-%{KernelVer}-source $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}
    cp linux-%{KernelVer}/.config $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}/
%endif

cd linux-%{KernelVer}

## install linux

# deal with kernel-source, now we don't need kernel-source
#mkdir $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}
#tar cf - --exclude SCCS --exclude BitKeeper --exclude .svn --exclude CVS --exclude .pc --exclude .hg --exclude .git --exclude=.tmp_versions --exclude=*vmlinux* --exclude=*.o --exclude=*.ko --exclude=*.cmd --exclude=Documentation --exclude=.config.old --exclude=.missing-syscalls.d --exclude=patches . | tar xf - -C %{buildroot}/usr/src/linux-%{KernelVer}

mkdir -p $RPM_BUILD_ROOT/boot
dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KernelVer}.img bs=1M count=20

%ifarch loongarch64
strip -s vmlinux -o vmlinux.elf
install -m 755 vmlinux.elf $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
%else
install -m 755 $(make -s image_name) $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
%endif

%if 0%{?openEuler_sign_rsa}
    %{openEuler_check_EBS_perm}
    if [ $openEuler_has_sign_perm -eq 1 ]; then
        echo "start sign"
        %ifarch %arm aarch64
	    gunzip -c $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}>$RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    sh /usr/lib/rpm/brp-ebs-sign --efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi.sig $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip
	    gzip -c $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip>$RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
	    rm -f $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip
        %endif
        %ifarch x86_64
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer} $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    sh /usr/lib/rpm/brp-ebs-sign --efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi.sig $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
        %endif
    fi
%endif

pushd $RPM_BUILD_ROOT/boot
sha512hmac ./vmlinuz-%{KernelVer} >./.vmlinuz-%{KernelVer}.hmac
popd

install -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KernelVer}
install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KernelVer}

gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KernelVer}.gz

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -m 755 %{SOURCE200} $RPM_BUILD_ROOT%{_sbindir}/mkgrub-menu-%{version}-%{devel_release}%{?maintenance_release}%{?pkg_release}.sh


%if 0%{?with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KernelVer}
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KernelVer}
%endif

# deal with module, if not kdump
%{make} ARCH=%{Arch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=%{KernelVer} mod-fw=
######## to collect ko to module.filelist about netwoking. block. drm. modesetting ###############
pushd $RPM_BUILD_ROOT/lib/modules/%{KernelVer}
find -type f -name "*.ko" >modnames

# mark modules executable so that strip-to-file can strip them
xargs --no-run-if-empty chmod u+x < modnames

# Generate a list of modules for block and networking.

grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

collect_modules_list()
{
    sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
    LC_ALL=C sort -u > modules.$1
    if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i modules.$1
    fi
}

collect_modules_list networking \
			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
collect_modules_list block \
		 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size|ahci_platform_get_resources' 'pktcdvd.ko|dm-mod.ko'
collect_modules_list drm \
			 'drm_open|drm_init'
collect_modules_list modesetting \
			 'drm_crtc_init'

# detect missing or incorrect license tags
rm -f modinfo
while read i
do
    echo -n "$i " >> modinfo
    /sbin/modinfo -l $i >> modinfo
done < modnames

grep -E -v \
	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
  modinfo && exit 1

rm -f modinfo modnames drivers.undef

for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
do
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
done
popd
# modsign module ko;need after find-debuginfo,strip
%define __modsign_install_post \
    if [ "%{with_signmodules}" -eq "1" ];then \
        cp certs/signing_key.pem . \
        cp certs/signing_key.x509 . \
        chmod 0755 %{modsign_cmd} \
        %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
    fi \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -n1 -P`nproc --all` xz; \
%{nil}

%if 0%{?openEuler_sign_rsa}
%define __modsign_install_post \
    if [ "%{with_signmodules}" -eq "1" ];then \
        if [ %flag_openEuler_has_sign_perm -eq 1 ]; then \
            sh %{SOURCE16} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
        else \
            cp certs/signing_key.pem . \
            cp certs/signing_key.x509 . \
            chmod 0755 %{modsign_cmd} \
            %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
        fi \
    fi \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -n1 -P`nproc --all` xz; \
%{nil}
%endif

# deal with header
%{make} ARCH=%{Arch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr KBUILD_SRC= headers_install
find $RPM_BUILD_ROOT/usr/include -name "\.*"  -exec rm -rf {} \;

# dtbs install
%ifarch aarch64 riscv64
    mkdir -p $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}
    install -m 644 $(find arch/%{Arch}/boot -name "*.dtb") $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/
    rm -f $(find arch/$Arch/boot -name "*.dtb")
%endif

# deal with vdso
%ifnarch ppc64le
%{make} -s ARCH=%{Arch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=%{KernelVer}
%endif
if [ ! -s ldconfig-kernel.conf ]; then
    echo "# Placeholder file, no vDSO hwcap entries used in this kernel." >ldconfig-kernel.conf
fi
install -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-%{KernelVer}.conf

# deal with /lib/module/ path- sub path: build source kernel
rm -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
rm -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/source
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/extra
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/updates
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/weak-updates
############ to do collect devel file  #########
# 1. Makefile And Kconfig, .config sysmbol
# 2. scrpits dir
# 3. .h file
find -type f \( -name "Makefile*" -o -name "Kconfig*" \) -exec cp --parents {} $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build \;
for f in Module.symvers System.map Module.markers .config;do
    test -f $f || continue
    cp $f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
done

cp -a scripts $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
if [ -d arch/%{Arch}/scripts ]; then
    cp -a arch/%{Arch}/scripts $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/arch/%{_arch} || :
fi
if [ -f arch/%{Arch}/*lds ]; then
    cp -a arch/%{Arch}/*lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/arch/%{_arch}/ || :
fi
find $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/scripts/ -name "*.o" -exec rm -rf {} \;

if [ -d arch/%{Arch}/include ]; then
    cp -a --parents arch/%{Arch}/include $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi
cp -a include $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include

if [ -f arch/%{Arch}/kernel/module.lds ]; then
    cp -a --parents arch/%{Arch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi

# module.lds is moved to scripts by commit 596b0474d3d9 in linux 5.10.
if [ -f scripts/module.lds ]; then
    cp -a --parents scripts/module.lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi

%ifarch aarch64
    cp -a --parents arch/arm/include/asm $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
%endif

# copy objtool for kernel-devel (needed for building external modules)
if grep -q CONFIG_OBJTOOL=y .config; then
    mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/tools/objtool
    cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/tools/objtool
fi

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built
touch -r $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/generated/uapi/linux/version.h
touch -r $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/.config $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/generated/autoconf.h
# for make prepare
if [ ! -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/config/auto.conf ];then
    cp .config $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/config/auto.conf
fi

mkdir -p %{buildroot}/usr/src/kernels
mv $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build $RPM_BUILD_ROOT/usr/src/kernels/%{KernelVer}

find $RPM_BUILD_ROOT/usr/src/kernels/%{KernelVer} -name ".*.cmd" -exec rm -f {} \;

pushd $RPM_BUILD_ROOT/lib/modules/%{KernelVer}
ln -sf /usr/src/kernels/%{KernelVer} build
ln -sf build source
popd


# deal with doc , now we don't need


# deal with kernel abi whitelists. now we don't need


## install tools
%if %{with_perf}
# perf
# perf tool binary and supporting scripts/binaries
%if 0%{?with_python2}
%{perf_make} %{perf_python2} DESTDIR=%{buildroot} lib=%{_lib} install-bin
%else
%{perf_make} %{perf_python3} DESTDIR=%{buildroot} lib=%{_lib} install-bin
%endif
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# remove examples
rm -rf %{buildroot}/usr/lib/perf/examples
# remove the stray header file that somehow got packaged in examples
rm -rf %{buildroot}/usr/lib/perf/include/bpf/

# python-perf extension
%{perf_make} %{perf_python3} DESTDIR=%{buildroot} install-python_ext
%if 0%{?with_python2}
%{perf_make} %{perf_python2} DESTDIR=%{buildroot} install-python_ext
%endif

# perf man pages (note: implicit rpm magic compresses them later)
install -d %{buildroot}/%{_mandir}/man1
install -pm0644 tools/kvm/kvm_stat/kvm_stat.1 %{buildroot}/%{_mandir}/man1/
install -pm0644 tools/perf/Documentation/*.1 %{buildroot}/%{_mandir}/man1/
%endif

# bpftool
pushd tools/bpf/bpftool
%{make} DESTDIR=%{buildroot} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
popd

# resolve_btfids
mkdir -p %{buildroot}/usr/src/kernels/%{KernelVer}/tools/bpf/resolve_btfids
cp tools/bpf/resolve_btfids/resolve_btfids %{buildroot}/usr/src/kernels/%{KernelVer}/tools/bpf/resolve_btfids

# cpupower
%{make} -C tools/power/cpupower DESTDIR=%{buildroot} libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
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
%ifarch %{ix86} x86_64
    mkdir -p %{buildroot}%{_mandir}/man8
    pushd tools/power/x86/x86_energy_perf_policy
    %{make} DESTDIR=%{buildroot} install
    popd
    pushd tools/power/x86/turbostat
    %{make} DESTDIR=%{buildroot} install
    popd
%endif
# thermal
pushd tools/thermal/tmon
%{make} INSTALL_ROOT=%{buildroot} install
popd
# iio
pushd tools/iio
%{make} DESTDIR=%{buildroot} install
popd
# gpio
pushd tools/gpio
%{make} DESTDIR=%{buildroot} install
popd
# kvm
pushd tools/kvm/kvm_stat
%{make} INSTALL_ROOT=%{buildroot} install-tools
popd
# netacc
pushd tools/netacc
%{make} INSTALL_ROOT=%{buildroot} install
popd

%define __spec_install_post\
%{?__debug_package:%{__debug_install_post}}\
%{__arch_install_post}\
%{__os_install_post}\
%{__modsign_install_post}\
%{nil}

%post
%{_sbindir}/new-kernel-pkg --package kernel --install %{KernelVer} || exit $?

%preun
if [ `uname -i` == "aarch64" ] &&
        [ -f /boot/EFI/grub2/grub.cfg ]; then
    /usr/bin/sh  %{_sbindir}/mkgrub-menu-%{version}-%{devel_release}%{?maintenance_release}%{?pkg_release}.sh %{version}-%{release}.aarch64  /boot/EFI/grub2/grub.cfg  remove
fi

%postun
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KernelVer} || exit $?
if [ -x %{_sbindir}/weak-modules ]
then
    %{_sbindir}/weak-modules --remove-kernel %{KernelVer} || exit $?
fi

# remove empty directory
if [ -d /lib/modules/%{KernelVer} ] && [ "`ls -A  /lib/modules/%{KernelVer}`" = "" ]; then
    rm -rf /lib/modules/%{KernelVer}
fi
if [ `uname -i` == "loongarch64" ];then
	[ -f /etc/grub2.cfg ] && GRUB_CFG=`readlink -f /etc/grub2.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /etc/grub2-efi.cfg ] && GRUB_CFG=`readlink -f /etc/grub2-efi.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /boot/efi/EFI/openEuler/grub.cfg ] && GRUB_CFG=/boot/efi/EFI/openEuler/grub.cfg
	[ "x${GRUB_CFG}" != "x" ] && grub2-mkconfig -o ${GRUB_CFG}
fi

%posttrans
%{_sbindir}/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{KernelVer} || exit $?
%{_sbindir}/new-kernel-pkg --package kernel --rpmposttrans %{KernelVer} || exit $?
if [ `uname -i` == "aarch64" ] &&
        [ -f /boot/EFI/grub2/grub.cfg ]; then
	/usr/bin/sh %{_sbindir}/mkgrub-menu-%{version}-%{devel_release}%{?maintenance_release}%{?pkg_release}.sh %{version}-%{release}.aarch64  /boot/EFI/grub2/grub.cfg  update
fi
if [ `uname -i` == "loongarch64" ];then
	[ -f /etc/grub2.cfg ] && GRUB_CFG=`readlink -f /etc/grub2.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /etc/grub2-efi.cfg ] && GRUB_CFG=`readlink -f /etc/grub2-efi.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /boot/efi/EFI/openEuler/grub.cfg ] && GRUB_CFG=/boot/efi/EFI/openEuler/grub.cfg
	[ "x${GRUB_CFG}" != "x" ] && grub2-mkconfig -o ${GRUB_CFG}
	grubby --set-default=/boot/vmlinuz-%{KernelVer}
fi
if [ -x %{_sbindir}/weak-modules ]
then
    %{_sbindir}/weak-modules --add-kernel %{KernelVer} || exit $?
fi
%{_sbindir}/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{KernelVer} || exit $?
%{_sbindir}/new-kernel-pkg --package kernel --rpmposttrans %{KernelVer} || exit $?

%post devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]
then
    (cd /usr/src/kernels/%{KernelVer} &&
     /usr/bin/find . -type f | while read f; do
       hardlink -c /usr/src/kernels/*.oe*.*/$f $f
     done)
fi

%post -n %{name}-tools
/sbin/ldconfig
%systemd_post cpupower.service

%preun -n %{name}-tools
%systemd_preun cpupower.service

%postun -n %{name}-tools
/sbin/ldconfig
%systemd_postun cpupower.service

%files
%defattr (-, root, root)
%doc
/boot/config-*
%ifarch aarch64 riscv64
/boot/dtb-*
%endif
/boot/symvers-*
/boot/System.map-*
/boot/vmlinuz-*
%ghost /boot/initramfs-%{KernelVer}.img
/boot/.vmlinuz-*.hmac
/etc/ld.so.conf.d/*
/lib/modules/%{KernelVer}/
%exclude /lib/modules/%{KernelVer}/source
%exclude /lib/modules/%{KernelVer}/build
%{_sbindir}/mkgrub-menu*.sh

%files devel
%defattr (-, root, root)
%doc
/lib/modules/%{KernelVer}/source
/lib/modules/%{KernelVer}/build
/usr/src/kernels/%{KernelVer}

%files headers
%defattr (-, root, root)
/usr/include/*
%exclude %{_includedir}/cpufreq.h
%exclude %{_includedir}/cpuidle.h

%if %{with_perf}
%files -n perf
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%{_libexecdir}/perf-core
%{_datadir}/perf-core/
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KernelVer}/tools/perf/Documentation/examples.txt
%dir %{_datadir}/doc/perf-tip
%{_datadir}/doc/perf-tip/*
%license linux-%{KernelVer}/COPYING

%if 0%{?with_python2}
%files -n python2-perf
%license linux-%{KernelVer}/COPYING
%{python2_sitearch}/*
%endif

%files -n python3-perf
%license linux-%{KernelVer}/COPYING
%{python3_sitearch}/*
%endif

%files -n %{name}-tools -f cpupower.lang
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_datadir}/bash-completion/completions/cpupower
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat
%{_sbindir}/net-acc
%{_sbindir}/tuned_acc/netacc
%{_libdir}/libcpupower.so.1
%{_libdir}/libcpupower.so.0.0.1
%license linux-%{KernelVer}/COPYING

%files -n %{name}-tools-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h

%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool-cgroup.8.gz
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man8/bpftool-btf.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-gen.8.gz
%{_mandir}/man8/bpftool-iter.8.gz
%{_mandir}/man8/bpftool-link.8.gz
%{_mandir}/man8/bpftool-net.8.gz
%{_mandir}/man8/bpftool-struct_ops.8.gz
%license linux-%{KernelVer}/COPYING

%if 0%{?with_source}
%files source
%defattr(-,root,root)
/usr/src/linux-%{KernelVer}/*
/usr/src/linux-%{KernelVer}/.config
%endif

%changelog
* Tue Feb  20 2025 zhangyu <zhangyu4@kylinos.cn> - 6.6.0-72.1.0.5
- update kernel-rt version to 6.6.0-72.1.0.3

* Tue May  21 2024 zhangyu <zhangyu4@kylinos.cn> - 6.6.0-27.0.0.4
- update kernel-rt version to 6.6.0-27.0.0.3

* Fir May  17 2024 zhangyu <zhangyu4@kylinos.cn> - 6.6.0-26.0.0.3
- update kernel-rt version to 6.6.0-26.0.0.3

* Wed May  15 2024 zhangyu <zhangyu4@kylinos.cn> - 6.6.0-26.0.0.2
- update kernel-rt version to 6.6.0-26.0.0.2
* Mon May  10 2024 zhangyu <zhangyu4@kylinos.cn> - 6.6.0-25.0.0.1
- update kernel-rt version to 6.6.0-25.0.0.1

* Thu May 09 2024 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-25.0.0.28
- !6930  fix general protection fault in update_cpumask
- cgroup/cpuset: fix general protection fault in update_cpumask
- !6905 v2  arm64: mmap: disable align larger anonymous mappings on THP boundaries
- arm64: mmap: disable align larger anonymous mappings on THP boundaries
- !7015  Fixes and cleanups to fs-writeback
- fs/writeback: remove unnecessary return in writeback_inodes_sb
- fs/writeback: correct comment of __wakeup_flusher_threads_bdi
- fs/writeback: only calculate dirtied_before when b_io is empty
- fs/writeback: remove unused parameter wb of finish_writeback_work
- fs/writeback: bail out if there is no more inodes for IO and queued once
- fs/writeback: avoid to writeback non-expired inode in kupdate writeback
- !6581  LoongArch: fix KASLR can not be disabled by nokaslr when boot from old BPI
- LoongArch: fix KASLR can not be disabled by nokaslr when boot from old BPI
- !6483  LoongArch: fix boot error caused by ioremap_page_range error
- LoongArch: fix boot error caused by ioremap_page_range error
- !6759 net: hns3: backport some maillist patches
- net: hns3: move constants from hclge_debugfs.h to hclge_debugfs.c
- net: hns3: dump more reg info based on ras mod
- net: hns3: add command queue trace for hns3
- net: hns3: add support to query scc version by devlink info
- net: hns3: revert "net: hns3: dump more reg info based on ras mod"
- net: hns3: revert "net: hns3: add command queue trace for hns3"
- net: hns3: revert "net: hns3: add support to query scc version by devlink info"
- !7011 v3  bugfix patches from OLK-5.10
- x86/quirks: Add parameter to clear MSIs early on boot
- x86/PCI: Export find_cap() to be used in early PCI code
- !6844  block: fix deadlock between bd_link_disk_holder and partition scan
- block: fix deadlock between bd_link_disk_holder and partition scan
- !5879 [OLK-6.6] Fix 'duplicate symbol rnp10_netdev_ops' error  for RNPGBE driver with x86_64-allyesconfig
- RNPGBE: NET: Fix 'duplicate symbol rnp10_netdev_ops' errors
- !5836 [OLK-6.6] Fix "'snprintf' output between 10 and 37 bytes into a destination of size 24" warning for RNP driver with loongarch-allmodconfig
- RNP: NET: Fix "'snprintf' output between 10 and 37 bytes into a 	  destination of size 24" wanrings

* Wed May 08 2024 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-24.0.0.27
- !6824  Introduce CONFIG_ARCH_CUSTOM_NUMA_DISTANCE
- config: enable COBFIG_ARCH_CUSTOM_NUMA_DISTANCE for arm64
- arm64/numa: Support node_reclaim_distance adjust for arch
- !6877  maple_tree: avoid checking other gaps after getting the largest gap
- maple_tree: avoid checking other gaps after getting the largest gap
- !6859 [openEuler-24.03-LTS][linux-6.6.y sync] Backport 6.6.23-6.6.30 LTS Patches
- x86: update openeuler_defconfig for x86_64
- bounds: Use the right number of bits for power-of-two CONFIG_NR_CPUS
- net/mlx5e: Advertise mlx5 ethernet driver updates sk_buff md_dst for MACsec
- macsec: Detect if Rx skb is macsec-related for offloading devices that update md_dst
- macsec: Enable devices to advertise whether they update sk_buff md_dst during offloads
- Revert "riscv: kdump: fix crashkernel reserving problem on RISC-V"
- ovl: fix memory leak in ovl_parse_param()
- phy: qcom: qmp-combo: fix VCO div offset on v5_5nm and v6
- i2c: smbus: fix NULL function pointer dereference
- sched/eevdf: Prevent vlag from going out of bounds in reweight_eevdf()
- sched/eevdf: Fix miscalculation in reweight_entity() when se is not curr
- sched/eevdf: Always update V if se->on_rq when reweighting
- phy: ti: tusb1210: Resolve charger-det crash if charger psy is unregistered
- riscv: Fix loading 64-bit NOMMU kernels past the start of RAM
- riscv: Fix TASK_SIZE on 64-bit NOMMU
- riscv: fix VMALLOC_START definition
- dmaengine: idxd: Fix oops during rmmod on single-CPU platforms
- dma: xilinx_dpdma: Fix locking
- dmaengine: idxd: Convert spinlock to mutex to lock evl workqueue
- phy: qcom: m31: match requested regulator name with dt schema
- phy: rockchip: naneng-combphy: Fix mux on rk3588
- phy: rockchip-snps-pcie3: fix clearing PHP_GRF_PCIESEL_CON bits
- phy: rockchip-snps-pcie3: fix bifurcation on rk3588
- phy: freescale: imx8m-pcie: fix pcie link-up instability
- phy: marvell: a3700-comphy: Fix hardcoded array size
- phy: marvell: a3700-comphy: Fix out of bounds read
- soundwire: amd: fix for wake interrupt handling for clockstop mode
- idma64: Don't try to serve interrupts when device is powered off
- dmaengine: tegra186: Fix residual calculation
- dmaengine: owl: fix register access functions
- x86/tdx: Preserve shared bit on mprotect()
- phy: qcom: qmp-combo: Fix VCO div offset on v3
- phy: qcom: qmp-combo: Fix register base for QSERDES_DP_PHY_MODE
- mtd: diskonchip: work around ubsan link failure
- udp: preserve the connected status if only UDP cmsg
- fbdev: fix incorrect address computation in deferred IO
- stackdepot: respect __GFP_NOLOCKDEP allocation flag
- net: b44: set pause params only when interface is up
- ethernet: Add helper for assigning packet type when dest address does not match device address
- ACPI: CPPC: Fix access width used for PCC registers
- ACPI: CPPC: Fix bit_offset shift in MASK_VAL() macro
- ACPI: CPPC: Use access_width over bit_width for system memory accesses
- irqchip/gic-v3-its: Prevent double free on error
- drm/amdgpu: Fix leak when GPU memory allocation fails
- drm/amdgpu: Assign correct bits for SDMA HDP flush
- drm/amdgpu/sdma5.2: use legacy HDP flush for SDMA2/3
- arm64: dts: rockchip: enable internal pull-up for Q7_THRM# on RK3399 Puma
- arm64: dts: qcom: sm8450: Fix the msi-map entries
- arm64: dts: qcom: sc8280xp: add missing PCIe minimum OPP
- LoongArch: Fix access error when read fault on a write-only VMA
- LoongArch: Fix callchain parse error with kernel tracepoint events
- cpu: Re-enable CPU mitigations by default for !X86 architectures
- btrfs: fix information leak in btrfs_ioctl_logical_to_ino()
- btrfs: scrub: run relocation repair when/only needed
- btrfs: fix wrong block_start calculation for btrfs_drop_extent_map_range()
- btrfs: fallback if compressed IO fails for ENOSPC
- HID: i2c-hid: remove I2C_HID_READ_PENDING flag to prevent lock-up
- smb3: fix lock ordering potential deadlock in cifs_sync_mid_result
- smb3: missing lock when picking channel
- smb: client: Fix struct_group() usage in __packed structs
- mm: support page_mapcount() on page_has_type() pages
- mm: create FOLIO_FLAG_FALSE and FOLIO_TYPE_OPS macros
- mmc: sdhci-msm: pervent access to suspended controller
- mtd: rawnand: qcom: Fix broken OP_RESET_DEVICE command in qcom_misc_cmd_type_exec()
- Bluetooth: qca: fix NULL-deref on non-serdev setup
- Bluetooth: qca: fix NULL-deref on non-serdev suspend
- Bluetooth: btusb: Add Realtek RTL8852BE support ID 0x0bda:0x4853
- Bluetooth: Fix type of len in {l2cap,sco}_sock_getsockopt_old()
- rust: remove `params` from `module` macro example
- kbuild: rust: force `alloc` extern to allow "empty" Rust files
- kbuild: rust: remove unneeded `@rustc_cfg` to avoid ICE
- rust: make mutually exclusive with CFI_CLANG
- rust: init: remove impl Zeroable for Infallible
- rust: don't select CONSTRUCTORS
- x86/cpu: Fix check for RDPKRU in __show_regs()
- selftests/seccomp: Handle EINVAL on unshare(CLONE_NEWPID)
- selftests/seccomp: Change the syscall used in KILL_THREAD test
- selftests/seccomp: user_notification_addfd check nextfd is available
- Squashfs: check the inode number is not the invalid value of zero
- squashfs: convert to new timestamp accessors
- drm/amdgpu: fix visible VRAM handling during faults
- drm/amdgpu: add shared fdinfo stats
- drm: add drm_gem_object_is_shared_for_memory_stats() helper
- mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly
- mm/gup: explicitly define and check internal GUP flags, disallow FOLL_TOUCH
- KVM: x86/pmu: Set enable bits for GP counters in PERF_GLOBAL_CTRL at "RESET"
- KVM: x86/pmu: Zero out PMU metadata on AMD if PMU is disabled
- af_unix: Suppress false-positive lockdep splat for spin_lock() in __unix_gc().
- tls: fix lockless read of strp->msg_ready in ->poll
- net: ethernet: ti: am65-cpts: Fix PTPv1 message type on TX packets
- ice: fix LAG and VF lock dependency in ice_reset_vf()
- iavf: Fix TC config comparison with existing adapter TC config
- i40e: Report MFS in decimal base instead of hex
- i40e: Do not use WQ_MEM_RECLAIM flag for workqueue
- net: ti: icssg-prueth: Fix signedness bug in prueth_init_rx_chns()
- net: phy: dp83869: Fix MII mode failure
- netfilter: nf_tables: honor table dormant flag from netdev release event path
- ARM: dts: imx6ull-tarragon: fix USB over-current polarity
- eth: bnxt: fix counting packets discarded due to OOM and netpoll
- mlxsw: spectrum_acl_tcam: Fix memory leak when canceling rehash work
- mlxsw: spectrum_acl_tcam: Fix incorrect list API usage
- mlxsw: spectrum_acl_tcam: Fix warning during rehash
- mlxsw: spectrum_acl_tcam: Fix memory leak during rehash
- mlxsw: spectrum_acl_tcam: Rate limit error message
- mlxsw: spectrum_acl_tcam: Fix possible use-after-free during rehash
- mlxsw: spectrum_acl_tcam: Fix possible use-after-free during activity update
- mlxsw: spectrum_acl_tcam: Fix race during rehash delayed work
- mlxsw: spectrum_acl_tcam: Fix race in region ID allocation
- mlxsw: Use refcount_t for reference counting
- net: openvswitch: Fix Use-After-Free in ovs_ct_exit
- ipvs: Fix checksumming on GSO of SCTP packets
- Bluetooth: qca: set power_ctrl_enabled on NULL returned by gpiod_get_optional()
- Bluetooth: hci_sync: Using hci_cmd_sync_submit when removing Adv Monitor
- Bluetooth: btusb: mediatek: Fix double free of skb in coredump
- Bluetooth: MGMT: Fix failing to MGMT_OP_ADD_UUID/MGMT_OP_REMOVE_UUID
- Bluetooth: hci_event: Fix sending HCI_OP_READ_ENC_KEY_SIZE
- Bluetooth: btusb: Fix triggering coredump implementation for QCA
- gpio: tegra186: Fix tegra186_gpio_is_accessible() check
- net: phy: mediatek-ge-soc: follow netdev LED trigger semantics
- net: gtp: Fix Use-After-Free in gtp_dellink
- net: usb: ax88179_178a: stop lying about skb->truesize
- ipv4: check for NULL idev in ip_route_use_hint()
- net: fix sk_memory_allocated_{add|sub} vs softirqs
- net: make SK_MEMORY_PCPU_RESERV tunable
- tools: ynl: don't ignore errors in NLMSG_DONE messages
- ax25: Fix netdev refcount issue
- NFC: trf7970a: disable all regulators on removal
- net: dsa: mv88e6xx: fix supported_interfaces setup in mv88e6250_phylink_get_caps()
- cxl/core: Fix potential payload size confusion in cxl_mem_get_poison()
- bnxt_en: Fix the PCI-AER routines
- bnxt_en: refactor reset close code
- bridge/br_netlink.c: no need to return void function
- icmp: prevent possible NULL dereferences from icmp_build_probe()
- ARM: dts: microchip: at91-sama7g5ek: Replace regulator-suspend-voltage with the valid property
- mlxsw: core_env: Fix driver initialization with old firmware
- mlxsw: core: Unregister EMAD trap using FORWARD action
- net: bcmasp: fix memory leak when bringing down interface
- vxlan: drop packets from invalid src-address
- net: libwx: fix alloc msix vectors failed
- wifi: mac80211: fix unaligned le16 access
- wifi: mac80211: remove link before AP
- wifi: mac80211_hwsim: init peer measurement result
- drm/gma500: Remove lid code
- wifi: iwlwifi: mvm: return uid from iwl_mvm_build_scan_cmd
- wifi: iwlwifi: mvm: remove old PASN station when adding a new one
- wifi: mac80211: split mesh fast tx cache into local/proxied/forwarded
- wifi: mac80211: clean up assignments to pointer cache.
- ARC: [plat-hsdk]: Remove misplaced interrupt-cells property
- gpio: tangier: Use correct type for the IRQ chip data
- arm64: dts: qcom: sc8180x: Fix ss_phy_irq for secondary USB controller
- arm64: dts: rockchip: regulator for sd needs to be always on for BPI-R2Pro
- arm64: dts: mediatek: mt2712: fix validation errors
- arm64: dts: mediatek: mt7986: prefix BPI-R3 cooling maps with "map-"
- arm64: dts: mediatek: mt7986: drop invalid thermal block clock
- arm64: dts: mediatek: mt7986: reorder nodes
- arm64: dts: mediatek: mt7986: drop "#reset-cells" from Ethernet controller
- arm64: dts: mediatek: mt7986: drop invalid properties from ethsys
- arm64: dts: mediatek: mt7986: reorder properties
- arm64: dts: mediatek: mt7622: drop "reset-names" from thermal block
- arm64: dts: mediatek: mt7622: fix ethernet controller "compatible"
- arm64: dts: mediatek: mt7622: fix IR nodename
- arm64: dts: mediatek: mt7622: fix clock controllers
- arm64: dts: mediatek: mt8183-kukui: Use default min voltage for MT6358
- arm64: dts: mediatek: mt8195-cherry: Update min voltage constraint for MT6315
- arm64: dts: mediatek: mt8192-asurada: Update min voltage constraint for MT6315
- arm64: dts: mediatek: cherry: Describe CPU supplies
- arm64: dts: mediatek: cherry: Add platform thermal configuration
- arm64: dts: mediatek: mt8195: Add missing gce-client-reg to mutex1
- arm64: dts: mediatek: mt8195: Add missing gce-client-reg to mutex
- arm64: dts: mediatek: mt8195: Add missing gce-client-reg to vpp/vdosys
- arm64: dts: mediatek: mt8192: Add missing gce-client-reg to mutex
- arm64: dts: mediatek: mt8183: Add power-domains properity to mfgcfg
- arm64: dts: rockchip: Remove unsupported node from the Pinebook Pro dts
- arm64: dts: rockchip: enable internal pull-up on PCIE_WAKE# for RK3399 Puma
- arm64: dts: rockchip: fix alphabetical ordering RK3399 puma
- arm64: dts: rockchip: enable internal pull-up on Q7_USB_ID for RK3399 Puma
- arm64: dts: rockchip: set PHY address of MT7531 switch to 0x1f
- HID: logitech-dj: allow mice to use all types of reports
- HID: intel-ish-hid: ipc: Fix dev_err usage with uninitialized dev->devc
- cifs: reinstate original behavior again for forceuid/forcegid
- smb: client: fix rename(2) regression against samba
- cifs: Fix reacquisition of volume cookie on still-live connection
- selftests: kselftest: Fix build failure with NOLIBC
- thunderbolt: Reset only non-USB4 host routers in resume
- PCI/ASPM: Fix deadlock when enabling ASPM
- ksmbd: common: use struct_group_attr instead of struct_group for network_open_info
- ksmbd: clear RENAME_NOREPLACE before calling vfs_rename
- ksmbd: validate request buffer size in smb2_allocate_rsp_buf()
- ksmbd: fix slab-out-of-bounds in smb2_allocate_rsp_buf
- powerpc/ftrace: Ignore ftrace locations in exit text sections
- virtio_net: Do not send RSS key if it is not supported
- net: dsa: mt7530: fix enabling EEE on MT7531 switch on all boards
- net: dsa: mt7530: fix improper frames on all 25MHz and 40MHz XTAL MT7530
- nilfs2: fix OOB in nilfs_set_de_type
- bootconfig: use memblock_free_late to free xbc memory to buddy
- nouveau: fix instmem race condition around ptr stores
- drm/vmwgfx: Fix crtc's atomic check conditional
- drm/vmwgfx: Sort primary plane formats by order of preference
- drm/vmwgfx: Fix prime import/export
- drm/amdgpu: remove invalid resource->start check v2
- drm/amdkfd: Fix memory leak in create_process failure
- drm/amdgpu: validate the parameters of bo mapping operations more clearly
- fuse: fix leaked ENOSYS error on first statx call
- mm/shmem: inline shmem_is_huge() for disabled transparent hugepages
- mm/memory-failure: fix deadlock when hugetlb_optimize_vmemmap is enabled
- mm,swapops: update check in is_pfn_swap_entry for hwpoison entries
- mm/userfaultfd: allow hugetlb change protection upon poison entry
- init/main.c: Fix potential static_command_line memory overflow
- arm64: hibernate: Fix level3 translation fault in swsusp_save()
- arm64/head: Disable MMU at EL2 before clearing HCR_EL2.E2H
- KVM: x86/mmu: Write-protect L2 SPTEs in TDP MMU when clearing dirty status
- KVM: x86/pmu: Do not mask LVTPC when handling a PMI on AMD platforms
- KVM: x86/pmu: Disable support for adaptive PEBS
- KVM: x86: Snapshot if a vCPU's vendor model is AMD vs. Intel compatible
- sched: Add missing memory barrier in switch_mm_cid
- fs: sysfs: Fix reference leak in sysfs_break_active_protection()
- speakup: Avoid crash on very long word
- mei: me: disable RPL-S on SPS and IGN firmwares
- usb: gadget: f_ncm: Fix UAF ncm object at re-bind after usb ep transport error
- usb: Disable USB3 LPM at shutdown
- usb: dwc2: host: Fix dereference issue in DDMA completion flow.
- Revert "usb: cdc-wdm: close race between read and workqueue"
- USB: serial: option: add Telit FN920C04 rmnet compositions
- USB: serial: option: add Rolling RW101-GL and RW135-GL support
- USB: serial: option: support Quectel EM060K sub-models
- USB: serial: option: add Lonsung U8300/U9300 product
- USB: serial: option: add support for Fibocom FM650/FG650
- USB: serial: option: add Fibocom FM135-GL variants
- serial: core: Fix missing shutdown and startup for serial base port
- serial: core: Clearing the circular buffer before NULLifying it
- serial: stm32: Reset .throttled state in .startup()
- serial: stm32: Return IRQ_NONE in the ISR if no handling happend
- serial/pmac_zilog: Remove flawed mitigation for rx irq flood
- serial: mxs-auart: add spinlock around changing cts state
- comedi: vmk80xx: fix incomplete endpoint checking
- thunderbolt: Fix wake configurations after device unplug
- thunderbolt: Avoid notify PM core about runtime PM resume
- binder: check offset alignment in binder_get_object()
- ALSA: hda/realtek - Enable audio jacks of Haier Boyue G42 with ALC269VC
- ALSA: hda/realtek: Add quirks for Huawei Matebook D14 NBLB-WAX9N
- ALSA: hda/tas2781: Add new vendor_id and subsystem_id to support ThinkPad ICE-1
- ALSA: hda/tas2781: correct the register for pow calibrated data
- ALSA: seq: ump: Fix conversion from MIDI2 to MIDI1 UMP messages
- net/mlx5: E-switch, store eswitch pointer before registering devlink_param
- x86/cpufeatures: Fix dependencies for GFNI, VAES, and VPCLMULQDQ
- x86/bugs: Fix BHI retpoline check
- clk: mediatek: Do a runtime PM get on controllers during probe
- clk: Get runtime PM before walking tree for clk_summary
- clk: Show active consumers of clocks in debugfs
- clk: Get runtime PM before walking tree during disable_unused
- clk: Initialize struct clk_core kref earlier
- clk: Remove prepare_lock hold assertion in __clk_release()
- interconnect: Don't access req_list while it's being manipulated
- platform/x86/amd/pmc: Extend Framework 13 quirk to more BIOSes
- usb: new quirk to reduce the SET_ADDRESS request timeout
- usb: xhci: Add timeout argument in address_device USB HCD callback
- drm: panel-orientation-quirks: Add quirk for Lenovo Legion Go
- ALSA: scarlett2: Rename scarlett_gen2 to scarlett2
- PCI: Simplify pcie_capability_clear_and_set_word() to ..._clear_word()
- PCI/DPC: Use FIELD_GET()
- ALSA: scarlett2: Add Focusrite Clarett 2Pre and 4Pre USB support
- ALSA: scarlett2: Add Focusrite Clarett+ 2Pre and 4Pre support
- ALSA: scarlett2: Add correct product series name to messages
- ALSA: scarlett2: Default mixer driver to enabled
- thunderbolt: Reset topology created by the boot firmware
- thunderbolt: Make tb_switch_reset() support Thunderbolt 2, 3 and USB4 routers
- thunderbolt: Introduce tb_path_deactivate_hop()
- thunderbolt: Introduce tb_port_reset()
- ASoC: ti: Convert Pandora ASoC to GPIO descriptors
- ALSA: scarlett2: Add support for Clarett 8Pre USB
- ALSA: scarlett2: Move USB IDs out from device_info struct
- drm/radeon: make -fstrict-flex-arrays=3 happy
- drm/panel: visionox-rm69299: don't unregister DSI device
- drm: nv04: Fix out of bounds access
- s390/cio: fix race condition during online processing
- s390/qdio: handle deferred cc1
- perf lock contention: Add a missing NULL check
- RDMA/mlx5: Fix port number for counter query in multi-port configuration
- RDMA/cm: Print the old state when cm_destroy_id gets timeout
- RDMA/rxe: Fix the problem "mutex_destroy missing"
- drm/i915/mst: Limit MST+DSC to TGL+
- net: ethernet: ti: am65-cpsw-nuss: cleanup DMA Channels before using them
- net: ethernet: mtk_eth_soc: fix WED + wifi reset
- gpiolib: swnode: Remove wrong header inclusion
- s390/ism: Properly fix receive message buffer allocation
- net: dsa: mt7530: fix port mirroring for MT7988 SoC switch
- net: dsa: mt7530: fix mirroring frames received on local port
- tun: limit printing rate when illegal packet received by tun dev
- ice: Fix checking for unsupported keys on non-tunnel device
- ice: tc: allow zero flags in parsing tc flower
- ice: tc: check src_vsi in case of traffic from VF
- net: stmmac: Fix IP-cores specific MAC capabilities
- net: stmmac: Fix max-speed being ignored on queue re-init
- net: stmmac: Apply half-duplex-less constraint for DW QoS Eth only
- octeontx2-pf: fix FLOW_DIS_IS_FRAGMENT implementation
- net: change maximum number of UDP segments to 128
- net/mlx5e: Prevent deadlock while disabling aRFS
- net/mlx5: Lag, restore buckets number to default after hash LAG deactivation
- net: sparx5: flower: fix fragment flags handling
- af_unix: Don't peek OOB data without MSG_OOB.
- af_unix: Call manage_oob() for every skb in unix_stream_read_generic().
- netfilter: flowtable: incorrect pppoe tuple
- netfilter: flowtable: validate pppoe header
- netfilter: nft_set_pipapo: do not free live element
- netfilter: nf_tables: Fix potential data-race in __nft_obj_type_get()
- netfilter: nf_tables: Fix potential data-race in __nft_expr_type_get()
- scsi: ufs: qcom: Add missing interconnect bandwidth values for Gear 5
- arm64: tlb: Fix TLBI RANGE operand
- arm64/mm: Modify range-based tlbi to decrement scale
- net: usb: ax88179_178a: avoid writing the mac address before first reading
- scsi: core: Fix handling of SCMD_FAIL_IF_RECOVERING
- random: handle creditable entropy from atomic process context
- selftests/ftrace: Limit length in subsystem-enable tests
- SUNRPC: Fix rpcgss_context trace event acceptor field
- drm/i915/vma: Fix UAF on destroy against retire race
- io_uring: Fix io_cqring_wait() not restoring sigmask on get_timespec64() failure
- media: videobuf2: request more buffers for vb2_read
- drm/msm/dpu: populate SSPP scaler block version
- selftests: timers: Fix posix_timers ksft_print_msg() warning
- ceph: redirty page before returning AOP_WRITEPAGE_ACTIVATE
- ceph: rename _to_client() to _to_fs_client()
- ceph: pass the mdsc to several helpers
- drm/amd/display: Do not recursively call manual trigger programming
- selftests/timers/posix_timers: Reimplement check_timer_distribution()
- selftests: timers: Convert posix_timers test to generate KTAP output
- drm/i915: Disable live M/N updates when using bigjoiner
- drm/i915: Adjust seamless_m_n flag behaviour
- drm/i915: Enable VRR later during fastsets
- drm/i915: Extract intel_crtc_vblank_evade_scanlines()
- drm/i915: Change intel_pipe_update_{start,end}() calling convention
- drm/i915/cdclk: Fix voltage_level programming edge case
- drm/i915/mst: Reject FEC+MST on ICL
- drm/i915: Fix FEC pipe A vs. DDI A mixup
- smb: client: refresh referral without acquiring refpath_lock
- smb: client: guarantee refcounted children from parent session
- smb3: show beginning time for per share stats
- smb: client: fix UAF in smb2_reconnect_server()
- smb: client: remove extra @chan_count check in __cifs_put_smb_ses()
- drm/amd/display: fix disable otg wa logic in DCN316
- drm/amd/display: Set VSC SDP Colorimetry same way for MST and SST
- drm/amd/display: Program VSC SDP colorimetry for all DP sinks >= 1.4
- drm/amdgpu: fix incorrect number of active RBs for gfx11
- drm/amdgpu: always force full reset for SOC21
- drm/amdgpu: Reset dGPU if suspend got aborted
- drm/i915: Disable port sync when bigjoiner is used
- drm/i915/cdclk: Fix CDCLK programming order when pipes are active
- x86/bugs: Replace CONFIG_SPECTRE_BHI_{ON,OFF} with CONFIG_MITIGATION_SPECTRE_BHI
- x86/bugs: Remove CONFIG_BHI_MITIGATION_AUTO and spectre_bhi=auto
- x86/bugs: Clarify that syscall hardening isn't a BHI mitigation
- x86/bugs: Fix BHI handling of RRSBA
- x86/bugs: Rename various 'ia32_cap' variables to 'x86_arch_cap_msr'
- x86/bugs: Cache the value of MSR_IA32_ARCH_CAPABILITIES
- x86/bugs: Fix BHI documentation
- x86/bugs: Fix return type of spectre_bhi_state()
- irqflags: Explicitly ignore lockdep_hrtimer_exit() argument
- x86/apic: Force native_apic_mem_read() to use the MOV instruction
- selftests: timers: Fix abs() warning in posix_timers test
- x86/cpu: Actually turn off mitigations by default for SPECULATION_MITIGATIONS=n
- perf/x86: Fix out of range data
- vhost: Add smp_rmb() in vhost_enable_notify()
- vhost: Add smp_rmb() in vhost_vq_avail_empty()
- arm64: dts: imx8-ss-dma: fix spi lpcg indices
- arm64: dts: imx8-ss-lsio: fix pwm lpcg indices
- arm64: dts: imx8-ss-conn: fix usb lpcg indices
- arm64: dts: imx8-ss-dma: fix adc lpcg indices
- arm64: dts: imx8-ss-dma: fix can lpcg indices
- arm64: dts: imx8qm-ss-dma: fix can lpcg indices
- drm/client: Fully protect modes[] with dev->mode_config.mutex
- drm/panfrost: Fix the error path in panfrost_mmu_map_fault_addr()
- drm/ast: Fix soft lockup
- drm/amdkfd: Reset GPU on queue preemption failure
- drm/i915/vrr: Disable VRR when using bigjoiner
- drm/vmwgfx: Enable DMA mappings with SEV
- accel/ivpu: Fix deadlock in context_xa
- scsi: sg: Avoid race in error handling & drop bogus warn
- scsi: sg: Avoid sg device teardown race
- kprobes: Fix possible use-after-free issue on kprobe registration
- io_uring/net: restore msg_control on sendzc retry
- btrfs: qgroup: convert PREALLOC to PERTRANS after record_root_in_trans
- btrfs: record delayed inode root in transaction
- btrfs: qgroup: fix qgroup prealloc rsv leak in subvolume operations
- btrfs: qgroup: correctly model root qgroup rsv in convert
- selftests: mptcp: use += operator to append strings
- iommu/vt-d: Allocate local memory for page request queue
- iommu/vt-d: Fix wrong use of pasid config
- tracing: hide unused ftrace_event_id_fops
- net: ena: Set tx_info->xdpf value to NULL
- net: ena: Use tx_ring instead of xdp_ring for XDP channel TX
- net: ena: Pass ena_adapter instead of net_device to ena_xmit_common()
- net: ena: Move XDP code to its new files
- net: ena: Fix incorrect descriptor free behavior
- net: ena: Wrong missing IO completions check order
- net: ena: Fix potential sign extension issue
- af_unix: Fix garbage collector racing against connect()
- af_unix: Do not use atomic ops for unix_sk(sk)->inflight.
- net: dsa: mt7530: trap link-local frames regardless of ST Port State
- Revert "s390/ism: fix receive message buffer allocation"
- net: sparx5: fix wrong config being used when reconfiguring PCS
- net/mlx5e: Do not produce metadata freelist entries in Tx port ts WQE xmit
- net/mlx5e: HTB, Fix inconsistencies with QoS SQs number
- net/mlx5e: Fix mlx5e_priv_init() cleanup flow
- net/mlx5: Correctly compare pkt reformat ids
- net/mlx5: Properly link new fs rules into the tree
- net/mlx5: offset comp irq index in name by one
- net/mlx5: Register devlink first under devlink lock
- net/mlx5: SF, Stop waiting for FW as teardown was called
- netfilter: complete validation of user input
- Bluetooth: l2cap: Don't double set the HCI_CONN_MGMT_CONNECTED bit
- Bluetooth: SCO: Fix not validating setsockopt user input
- Bluetooth: hci_sync: Fix using the same interval and window for Coded PHY
- Bluetooth: hci_sync: Use QoS to determine which PHY to scan
- Bluetooth: ISO: Don't reject BT_ISO_QOS if parameters are unset
- Bluetooth: ISO: Align broadcast sync_timeout with connection timeout
- ipv6: fix race condition between ipv6_get_ifaddr and ipv6_del_addr
- ipv4/route: avoid unused-but-set-variable warning
- ipv6: fib: hide unused 'pn' variable
- octeontx2-af: Fix NIX SQ mode and BP config
- af_unix: Clear stale u->oob_skb.
- net: ks8851: Handle softirqs at the end of IRQ thread to fix hang
- net: ks8851: Inline ks8851_rx_skb()
- bnxt_en: Reset PTP tx_avail after possible firmware reset
- bnxt_en: Fix error recovery for RoCE ulp client
- bnxt_en: Fix possible memory leak in bnxt_rdma_aux_device_init()
- s390/ism: fix receive message buffer allocation
- geneve: fix header validation in geneve[6]_xmit_skb
- block: fix q->blkg_list corruption during disk rebind
- octeontx2-pf: Fix transmit scheduler resource leak
- xsk: validate user input for XDP_{UMEM|COMPLETION}_FILL_RING
- u64_stats: fix u64_stats_init() for lockdep when used repeatedly in one file
- net: openvswitch: fix unwanted error log on timeout policy probing
- scsi: qla2xxx: Fix off by one in qla_edif_app_getstats()
- nouveau: fix function cast warning
- Revert "drm/qxl: simplify qxl_fence_wait"
- cxl/core: Fix initialization of mbox_cmd.size_out in get event
- arm64: dts: imx8-ss-conn: fix usdhc wrong lpcg clock order
- drm/msm/dpu: don't allow overriding data from catalog
- cxl/core/regs: Fix usage of map->reg_type in cxl_decode_regblock() before assigned
- cxl/mem: Fix for the index of Clear Event Record Handle
- firmware: arm_scmi: Make raw debugfs entries non-seekable
- ARM: OMAP2+: fix USB regression on Nokia N8x0
- mmc: omap: restore original power up/down steps
- mmc: omap: fix deferred probe
- mmc: omap: fix broken slot switch lookup
- ARM: OMAP2+: fix N810 MMC gpiod table
- ARM: OMAP2+: fix bogus MMC GPIO labels on Nokia N8x0
- media: cec: core: remove length check of Timer Status
- PM: s2idle: Make sure CPUs will wakeup directly on resume
- ACPI: scan: Do not increase dep_unmet for already met dependencies
- platform/chrome: cros_ec_uart: properly fix race condition
- drm/amd/pm: fixes a random hang in S4 for SMU v13.0.4/11
- Bluetooth: Fix memory leak in hci_req_sync_complete()
- ring-buffer: Only update pages_touched when a new page is touched
- raid1: fix use-after-free for original bio in raid1_write_request()
- ARM: dts: imx7s-warp: Pass OV2680 link-frequencies
- batman-adv: Avoid infinite loop trying to resize local TT
- ata: libata-scsi: Fix ata_scsi_dev_rescan() error path
- ata: libata-core: Allow command duration limits detection for ACS-4 drives
- smb3: fix Open files on server counter going negative
- drm: Check polling initialized before enabling in drm_helper_probe_single_connector_modes
- Revert "drm/amd/amdgpu: Fix potential ioremap() memory leaks in amdgpu_device_init()"
- VMCI: Fix possible memcpy() run-time warning in vmci_datagram_invoke_guest_handler()
- net: mpls: error out if inner headers are not set
- Bluetooth: btintel: Fixe build regression
- platform/x86: intel-vbtn: Update tablet mode switch at end of probe
- randomize_kstack: Improve entropy diffusion
- media: mediatek: vcodec: adding lock to protect encoder context list
- media: mediatek: vcodec: adding lock to protect decoder context list
- media: mediatek: vcodec: Fix oops when HEVC init fails
- selftests: mptcp: display simult in extra_msg
- gcc-plugins/stackleak: Avoid .head.text section
- ALSA: hda/realtek: Add quirks for some Clevo laptops
- fbmon: prevent division by zero in fb_videomode_from_videomode()
- drivers/nvme: Add quirks for device 126f:2262
- modpost: fix null pointer dereference
- io_uring: clear opcode specific data for an early failure
- fbdev: viafb: fix typo in hw_bitblt_1 and hw_bitblt_2
- x86/xen: attempt to inflate the memory balloon on PVH
- ASoC: soc-core.c: Skip dummy codec when adding platforms
- thermal/of: Assume polling-delay(-passive) 0 when absent
- ASoC: amd: yc: Fix non-functional mic on ASUS M7600RE
- usb: sl811-hcd: only defined function checkdone if QUIRK2 is defined
- usb: typec: tcpci: add generic tcpci fallback compatible
- thunderbolt: Keep the domain powered when USB4 port is in redrive mode
- usb: typec: ucsi: Limit read size on v1.2
- usb: gadget: uvc: mark incomplete frames with UVC_STREAM_ERR
- bus: mhi: host: Add MHI_PM_SYS_ERR_FAIL state
- tools: iio: replace seekdir() in iio_generic_buffer
- ring-buffer: use READ_ONCE() to read cpu_buffer->commit_page in concurrent environment
- Input: xpad - add support for Snakebyte GAMEPADs
- ktest: force $buildonly = 1 for 'make_warnings_file' test type
- ALSA: hda/realtek: Add quirk for Lenovo Yoga 9 14IMH9
- platform/x86: touchscreen_dmi: Add an extra entry for a variant of the Chuwi Vi8 tablet
- Input: allocate keycode for Display refresh rate toggle
- Input: imagis - use FIELD_GET where applicable
- RDMA/cm: add timeout to cm_destroy_id wait
- block: prevent division by zero in blk_rq_stat_sum()
- input/touchscreen: imagis: Correct the maximum touch area value
- libperf evlist: Avoid out-of-bounds access
- Revert "ACPI: PM: Block ASUS B1400CEAE from suspend to idle by default"
- PCI: Disable D3cold on Asus B1400 PCI-NVMe bridge
- SUNRPC: increase size of rpc_wait_queue.qlen from unsigned short to unsigned int
- drm: Check output polling initialized before disabling
- drm/amd/amdgpu: Fix potential ioremap() memory leaks in amdgpu_device_init()
- HID: input: avoid polling stylus battery on Chromebook Pompom
- i2c: designware: Fix RX FIFO depth define on Wangxun 10Gb NIC
- accel/habanalabs: increase HL_MAX_STR to 64 bytes to avoid warnings
- drm/amd/display: Fix nanosec stat overflow
- ext4: forbid commit inconsistent quota data when errors=remount-ro
- ext4: add a hint for block bitmap corrupt state in mb_groups
- ASoC: Intel: avs: Populate board selection with new I2S entries
- ALSA: firewire-lib: handle quirk to calculate payload quadlets as data block counter
- media: sta2x11: fix irq handler cast
- Julia Lawall reported this null pointer dereference, this should fix it.
- rcu-tasks: Repair RCU Tasks Trace quiescence check
- rcu/nocb: Fix WARN_ON_ONCE() in the rcu_nocb_bypass_lock()
- ASoC: Intel: common: DMI remap for rebranded Intel NUC M15 (LAPRC710) laptops
- isofs: handle CDs with bad root inode but good Joliet root directory
- scsi: lpfc: Fix possible memory leak in lpfc_rcv_padisc()
- sysv: don't call sb_bread() with pointers_lock held
- pinctrl: renesas: checker: Limit cfg reg enum checks to provided IDs
- drm/ttm: return ENOSPC from ttm_bo_mem_space v3
- ASoC: SOF: amd: Optimize quirk for Valve Galileo
- drm: panel-orientation-quirks: Add quirk for GPD Win Mini
- Input: synaptics-rmi4 - fail probing if memory allocation for "phys" fails
- drm/vc4: don't check if plane->state->fb == state->fb
- Bluetooth: Add new quirk for broken read key length on ATS2851
- Bluetooth: btmtk: Add MODULE_FIRMWARE() for MT7922
- Bluetooth: btintel: Fix null ptr deref in btintel_read_version
- net/smc: reduce rtnl pressure in smc_pnet_create_pnetids_list()
- ice: use relative VSI index for VFs instead of PF VSI number
- btrfs: send: handle path ref underflow in header iterate_inode_ref()
- btrfs: export: handle invalid inode or root reference in btrfs_get_parent()
- btrfs: handle chunk tree lookup error in btrfs_relocate_sys_chunks()
- wifi: cfg80211: check A-MSDU format more carefully
- wifi: iwlwifi: Add missing MODULE_FIRMWARE() for *.pnvm
- overflow: Allow non-type arg to type_max() and type_min()
- cpufreq: Don't unregister cpufreq cooling on CPU hotplug
- wifi: ath11k: decrease MHI channel buffer length to 8KB
- dma-direct: Leak pages on dma_set_decrypted() failure
- net: pcs: xpcs: Return EINVAL in the internal methods
- tools/power x86_energy_perf_policy: Fix file leak in get_pkg_num()
- pstore/zone: Add a null pointer check to the psz_kmsg_read
- ACPI: x86: Move acpi_quirk_skip_serdev_enumeration() out of CONFIG_X86_ANDROID_TABLETS
- wifi: mt76: mt7996: add locking for accessing mapped registers
- wifi: mt76: mt7996: disable AMSDU for non-data frames
- wifi: mt76: mt7915: add locking for accessing mapped registers
- wifi: brcmfmac: Add DMI nvram filename quirk for ACEPC W5 Pro
- firmware: tegra: bpmp: Return directly after a failed kzalloc() in get_filename()
- net: skbuff: add overflow debug check to pull/push helpers
- ionic: set adminq irq affinity
- pmdomain: imx8mp-blk-ctrl: imx8mp_blk: Add fdcc clock to hdmimix domain
- pmdomain: ti: Add a null pointer check to the omap_prm_domain_init
- net: add netdev_lockdep_set_classes() to virtual drivers
- arm64: dts: rockchip: fix rk3399 hdmi ports node
- arm64: dts: rockchip: fix rk3328 hdmi ports node
- ARM: dts: rockchip: fix rk322x hdmi ports node
- ARM: dts: rockchip: fix rk3288 hdmi ports node
- cpuidle: Avoid potential overflow in integer multiplication
- panic: Flush kernel log buffer at the end
- printk: For @suppress_panic_printk check for other CPU in panic
- wifi: iwlwifi: pcie: Add the PCI device id for new hardware
- VMCI: Fix memcpy() run-time warning in dg_dispatch_as_host()
- wifi: rtw89: pci: enlarge RX DMA buffer to consider size of RX descriptor
- net: phy: phy_device: Prevent nullptr exceptions on ISR
- net: stmmac: dwmac-starfive: Add support for JH7100 SoC
- bnx2x: Fix firmware version string character counts
- wifi: rtw89: fix null pointer access when abort scan
- wifi: ath9k: fix LNA selection in ath_ant_try_scan()
- amdkfd: use calloc instead of kzalloc to avoid integer overflow
- x86: set SPECTRE_BHI_ON as default
- KVM: x86: Add BHI_NO
- x86/bhi: Mitigate KVM by default
- x86/bhi: Add BHI mitigation knob
- x86/bhi: Enumerate Branch History Injection (BHI) bug
- x86/bhi: Define SPEC_CTRL_BHI_DIS_S
- x86/bhi: Add support for clearing branch history at syscall entry
- x86/syscall: Don't force use of indirect calls for system calls
- x86/bugs: Change commas to semicolons in 'spectre_v2' sysfs file
- x86/boot: Move mem_encrypt= parsing to the decompressor
- x86/efistub: Remap kernel text read-only before dropping NX attribute
- x86/sev: Move early startup code into .head.text section
- x86/sme: Move early SME kernel encryption handling into .head.text
- efi/libstub: Add generic support for parsing mem_encrypt=
- x86/head/64: Move the __head definition to <asm/init.h>
- bpf: put uprobe link's path and task in release callback
- mptcp: don't account accept() of non-MPC client as fallback to TCP
- mptcp: don't overwrite sock_ops in mptcp_is_tcpsk()
- selftests: mptcp: connect: fix shellcheck warnings
- of: module: prevent NULL pointer dereference in vsnprintf()
- Revert "x86/mpparse: Register APIC address only once"
- drm/i915/gt: Enable only one CCS for compute workload
- drm/i915/gt: Do not generate the command streamer for all the CCS
- drm/i915/gt: Disable HW load balancing for CCS
- smb: client: fix potential UAF in cifs_signal_cifsd_for_reconnect()
- smb: client: fix potential UAF in smb2_is_network_name_deleted()
- smb: client: fix potential UAF in is_valid_oplock_break()
- smb: client: fix potential UAF in smb2_is_valid_lease_break()
- smb: client: fix potential UAF in smb2_is_valid_oplock_break()
- smb: client: fix potential UAF in cifs_dump_full_key()
- smb: client: fix potential UAF in cifs_stats_proc_show()
- smb: client: fix potential UAF in cifs_stats_proc_write()
- smb: client: fix potential UAF in cifs_debug_files_proc_show()
- smb3: retrying on failed server close
- smb: client: serialise cifs_construct_tcon() with cifs_mount_mutex
- smb: client: handle DFS tcons in cifs_construct_tcon()
- riscv: process: Fix kernel gp leakage
- riscv: Fix spurious errors from __get/put_kernel_nofault
- s390/entry: align system call table on 8 bytes
- selftests/mm: include strings.h for ffsl
- mm/secretmem: fix GUP-fast succeeding on secretmem folios
- arm64/ptrace: Use saved floating point state type to determine SVE layout
- perf/x86/intel/ds: Don't clear ->pebs_data_cfg for the last PEBS event
- x86/coco: Require seeding RNG with RDRAND on CoCo systems
- x86/mce: Make sure to grab mce_sysfs_mutex in set_bank()
- x86/mm/pat: fix VM_PAT handling in COW mappings
- of: dynamic: Synchronize of_changeset_destroy() with the devlink removals
- driver core: Introduce device_link_wait_removal()
- io_uring/kbuf: hold io_buffer_list reference over mmap
- io_uring: use private workqueue for exit work
- io_uring/kbuf: protect io_buffer_list teardown with a reference
- io_uring/kbuf: get rid of bl->is_ready
- io_uring/kbuf: get rid of lower BGID lists
- ALSA: hda/realtek: Update Panasonic CF-SZ6 quirk to support headset with microphone
- ALSA: hda/realtek - Fix inactive headset mic jack
- ksmbd: do not set SMB2_GLOBAL_CAP_ENCRYPTION for SMB 3.1.1
- ksmbd: validate payload size in ipc response
- ksmbd: don't send oplock break if rename fails
- gpio: cdev: fix missed label sanitizing in debounce_setup()
- gpio: cdev: check for NULL labels when sanitizing them for irqs
- x86/retpoline: Add NOENDBR annotation to the SRSO dummy return thunk
- ice: fix typo in assignment
- nfsd: hold a lighter-weight client reference over CB_RECALL_ANY
- riscv: Disable preemption when using patch_map()
- ASoC: SOF: amd: fix for false dsp interrupts
- ata: sata_mv: Fix PCI device ID table declaration compilation warning
- spi: mchp-pci1xxx: Fix a possible null pointer dereference in pci1xxx_spi_probe
- cifs: Fix caching to try to do open O_WRONLY as rdwr on server
- Revert "ALSA: emu10k1: fix synthesizer sample playback position and caching"
- scsi: mylex: Fix sysfs buffer lengths
- ata: sata_sx4: fix pdc20621_get_from_dimm() on 64-bit
- regmap: maple: Fix uninitialized symbol 'ret' warnings
- ASoC: amd: acp: fix for acp_init function error handling
- spi: s3c64xx: Use DMA mode from fifo size
- spi: s3c64xx: determine the fifo depth only once
- spi: s3c64xx: allow full FIFO masks
- spi: s3c64xx: define a magic value
- spi: s3c64xx: remove else after return
- spi: s3c64xx: explicitly include <linux/bits.h>
- spi: s3c64xx: sort headers alphabetically
- spi: s3c64xx: Extract FIFO depth calculation to a dedicated macro
- ASoC: ops: Fix wraparound for mask in snd_soc_get_volsw
- ASoC: rt722-sdca-sdw: fix locking sequence
- ASoC: rt712-sdca-sdw: fix locking sequence
- ASoC: rt711-sdw: fix locking sequence
- ASoC: rt711-sdca: fix locking sequence
- ASoC: rt5682-sdw: fix locking sequence
- drm/prime: Unbreak virtgpu dma-buf export
- nouveau/uvmm: fix addr/range calcs for remap operations
- drm/panfrost: fix power transition timeout warnings
- ALSA: hda: cs35l56: Add ACPI device match tables
- regmap: maple: Fix cache corruption in regcache_maple_drop()
- RISC-V: Update AT_VECTOR_SIZE_ARCH for new AT_MINSIGSTKSZ
- drivers/perf: riscv: Disable PERF_SAMPLE_BRANCH_* while not supported
- ASoC: wm_adsp: Fix missing mutex_lock in wm_adsp_write_ctl()
- 9p: Fix read/write debug statements to report server reply
- fs/pipe: Fix lockdep false-positive in watchqueue pipe_write()
- KVM: SVM: Add support for allowing zero SEV ASIDs
- KVM: SVM: Use unsigned integers when dealing with ASIDs
- net: ravb: Always update error counters
- net: ravb: Always process TX descriptor ring
- net: ravb: Let IP-specific receive function to interrogate descriptors
- e1000e: move force SMBUS from enable ulp function to avoid PHY loss issue
- e1000e: Minor flow correction in e1000_shutdown function
- e1000e: Workaround for sporadic MDI error on Meteor Lake systems
- intel: legacy: field get conversion
- intel: add bit macro includes where needed
- i40e: Remove circular header dependencies and fix headers
- i40e: Split i40e_osdep.h
- i40e: Move memory allocation structures to i40e_alloc.h
- i40e: Simplify memory allocation functions
- virtchnl: Add header dependencies
- i40e: Refactor I40E_MDIO_CLAUSE* macros
- i40e: Remove back pointer from i40e_hw structure
- i40e: Enforce software interrupt during busy-poll exit
- i40e: Remove _t suffix from enum type names
- drm/amd: Flush GFXOFF requests in prepare stage
- drm/amd: Add concept of running prepare_suspend() sequence for IP blocks
- drm/amd: Evict resources during PM ops prepare() callback
- drm/amd/display: Prevent crash when disable stream
- drm/amd/display: Fix DPSTREAM CLK on and off sequence
- usb: typec: ucsi: Fix race between typec_switch and role_switch
- i40e: fix vf may be used uninitialized in this function warning
- i40e: fix i40e_count_filters() to count only active/new filters
- octeontx2-af: Add array index check
- octeontx2-pf: check negative error code in otx2_open()
- octeontx2-af: Fix issue with loading coalesced KPU profiles
- udp: prevent local UDP tunnel packets from being GROed
- udp: do not transition UDP GRO fraglist partial checksums to unnecessary
- udp: do not accept non-tunnel GSO skbs landing in a tunnel
- r8169: skip DASH fw status checks when DASH is disabled
- mlxbf_gige: stop interface during shutdown
- ipv6: Fix infinite recursion in fib6_dump_done().
- ax25: fix use-after-free bugs caused by ax25_ds_del_timer
- tcp: Fix bind() regression for v6-only wildcard and v4(-mapped-v6) non-wildcard addresses.
- selftests: reuseaddr_conflict: add missing new line at the end of the output
- erspan: make sure erspan_base_hdr is present in skb->head
- i40e: Fix VF MAC filter removal
- ice: fix enabling RX VLAN filtering
- gro: fix ownership transfer
- selftests: net: gro fwd: update vxlan GRO test expectations
- net: dsa: mv88e6xxx: fix usable ports on 88e6020
- net: phy: micrel: Fix potential null pointer dereference
- net: fec: Set mac_managed_pm during probe
- net: txgbe: fix i2c dev name cannot match clkdev
- net: phy: micrel: lan8814: Fix when enabling/disabling 1-step timestamping
- net: stmmac: fix rx queue priority assignment
- net/sched: fix lockdep splat in qdisc_tree_reduce_backlog()
- net: dsa: sja1105: Fix parameters order in sja1110_pcs_mdio_write_c45()
- net/sched: act_skbmod: prevent kernel-infoleak
- KVM: arm64: Ensure target address is granule-aligned for range TLBI
- x86/retpoline: Do the necessary fixup to the Zen3/4 srso return thunk for !SRSO
- bpf, sockmap: Prevent lock inversion deadlock in map delete elem
- vboxsf: Avoid an spurious warning if load_nls_xxx() fails
- netfilter: validate user input for expected length
- netfilter: nf_tables: discard table flag update with pending basechain deletion
- netfilter: nf_tables: Fix potential data-race in __nft_flowtable_type_get()
- netfilter: nf_tables: flush pending destroy work before exit_net release
- netfilter: nf_tables: reject new basechain after table flag update
- x86/bugs: Fix the SRSO mitigation on Zen3/4
- x86/nospec: Refactor UNTRAIN_RET[_*]
- x86/srso: Disentangle rethunk-dependent options
- x86/srso: Improve i-cache locality for alias mitigation
- vsock/virtio: fix packet delivery to tap device
- net: mana: Fix Rx DMA datasize and skb_over_panic
- net: usb: ax88179_178a: avoid the interface always configured as random address
- net/rds: fix possible cp null dereference
- xen-netfront: Add missing skb_mark_for_recycle
- selftests: mptcp: join: fix dev in check_endpoint
- netfilter: nf_tables: release mutex after nft_gc_seq_end from abort path
- netfilter: nf_tables: release batch on table validation from abort path
- Bluetooth: Fix TOCTOU in HCI debugfs implementation
- Bluetooth: hci_event: set the conn encrypted before conn establishes
- Bluetooth: add quirk for broken address properties
- Bluetooth: qca: fix device-address endianness
- arm64: dts: qcom: sc7180-trogdor: mark bluetooth address as broken
- Revert "Bluetooth: hci_qca: Set BDA quirk bit if fwnode exists in DT"
- x86/bpf: Fix IP after emitting call depth accounting
- r8169: fix issue caused by buggy BIOS on certain boards with RTL8168d
- selinux: avoid dereference of garbage after mount failure
- KVM: arm64: Fix host-programmed guest events in nVHE
- RISC-V: KVM: Fix APLIC in_clrip[x] read emulation
- RISC-V: KVM: Fix APLIC setipnum_le/be write emulation
- gpio: cdev: sanitize the label before requesting the interrupt
- modpost: do not make find_tosym() return NULL
- btrfs: fix race when detecting delalloc ranges during fiemap
- btrfs: ensure fiemap doesn't race with writes when FIEMAP_FLAG_SYNC is given
- Revert "x86/mm/ident_map: Use gbpages only where full GB page should be mapped."
- mm/treewide: replace pud_large() with pud_leaf()
- dm integrity: fix out-of-range warning
- drm/i915/mtl: Update workaround 14018575942
- drm/i915/xelpg: Extend some workarounds/tuning to gfx version 12.74
- drm/i915/mtl: Update workaround 14016712196
- drm/i915: Replace several IS_METEORLAKE with proper IP version checks
- drm/i915: Eliminate IS_MTL_GRAPHICS_STEP
- drm/i915/xelpg: Call Xe_LPG workaround functions based on IP version
- drm/i915: Consolidate condition for Wa_22011802037
- drm/i915: Tidy workaround definitions
- drm/i915/dg2: Drop pre-production GT workarounds
- inet: inet_defrag: prevent sk release while still in use
- Octeontx2-af: fix pause frame configuration in GMP mode
- net: lan743x: Add set RFE read fifo threshold for PCI1x1x chips
- net: bcmasp: Bring up unimac after PHY link up
- netfilter: nf_tables: skip netdev hook unregistration if table is dormant
- netfilter: nf_tables: reject table flag and netdev basechain updates
- netfilter: nf_tables: reject destroy command to remove basechain hooks
- cifs: Fix duplicate fscache cookie warnings
- bpf: Protect against int overflow for stack access size
- mlxbf_gige: call request_irq() after NAPI initialized
- tls: get psock ref after taking rxlock to avoid leak
- tls: adjust recv return with async crypto and failed copy to userspace
- tls: recv: process_rx_list shouldn't use an offset with kvec
- net: hns3: mark unexcuted loopback test result as UNEXECUTED
- net: hns3: fix kernel crash when devlink reload during pf initialization
- net: hns3: fix index limit to support all queue stats
- ACPICA: debugger: check status of acpi_evaluate_object() in acpi_db_walk_for_fields()
- selftests: vxlan_mdb: Fix failures with old libnet
- net: wwan: t7xx: Split 64bit accesses to fix alignment issues
- tcp: properly terminate timers for kernel sockets
- net: hsr: hsr_slave: Fix the promiscuous mode in offload mode
- s390/qeth: handle deferred cc1
- igc: Remove stale comment about Tx timestamping
- ixgbe: avoid sleeping allocation in ixgbe_ipsec_vf_add_sa()
- ice: fix memory corruption bug with suspend and rebuild
- ice: realloc VSI stats arrays
- ice: Refactor FW data type and fix bitmap casting issue
- ALSA: hda: cs35l56: Set the init_done flag before component_add()
- wifi: iwlwifi: mvm: include link ID when releasing frames
- wifi: iwlwifi: disable multi rx queue for 9000
- wifi: iwlwifi: mvm: rfi: fix potential response leaks
- mlxbf_gige: stop PHY during open() error paths
- tools: ynl: fix setting presence bits in simple nests
- nfc: nci: Fix uninit-value in nci_dev_up and nci_ntf_packet
- arm64: bpf: fix 32bit unconditional bswap
- dma-buf: Fix NULL pointer dereference in sanitycheck()
- bpf, arm64: fix bug in BPF_LDX_MEMSX
- s390/bpf: Fix bpf_plt pointer arithmetic
- scripts/bpf_doc: Use silent mode when exec make cmd
- drm/i915: Pre-populate the cursor physical dma address
- drm/i915/display: Use i915_gem_object_get_dma_address to get dma address
- Revert "workqueue.c: Increase workqueue name length"
- Revert "workqueue: Move pwq->max_active to wq->max_active"
- Revert "workqueue: Factor out pwq_is_empty()"
- Revert "workqueue: Replace pwq_activate_inactive_work() with [__]pwq_activate_work()"
- Revert "workqueue: Move nr_active handling into helpers"
- Revert "workqueue: Make wq_adjust_max_active() round-robin pwqs while activating"
- Revert "workqueue: Introduce struct wq_node_nr_active"
- Revert "workqueue: Shorten events_freezable_power_efficient name"
- drm/amdgpu: fix use-after-free bug
- tools/resolve_btfids: fix build with musl libc
- x86/sev: Skip ROM range scans and validation for SEV-SNP guests
- scsi: lpfc: Correct size for wqe for memset()
- scsi: lpfc: Correct size for cmdwqe/rspwqe for memset()
- usb: dwc3: pci: Drop duplicate ID
- Revert "x86/bugs: Use fixed addressing for VERW operand"
- x86/bugs: Use fixed addressing for VERW operand
- scsi: qla2xxx: Delay I/O Abort on PCI error
- scsi: qla2xxx: Change debug message during driver unload
- scsi: qla2xxx: Fix double free of fcport
- scsi: qla2xxx: Fix double free of the ha->vp_map pointer
- scsi: qla2xxx: Fix command flush on cable pull
- scsi: qla2xxx: NVME|FCP prefer flag not being honored
- scsi: qla2xxx: Update manufacturer detail
- scsi: qla2xxx: Split FCE|EFT trace control
- scsi: qla2xxx: Fix N2N stuck connection
- scsi: qla2xxx: Prevent command send on chip reset
- usb: typec: ucsi: Clear UCSI_CCI_RESET_COMPLETE before reset
- usb: typec: ucsi_acpi: Refactor and fix DELL quirk
- usb: typec: ucsi: Ack unsupported commands
- usb: typec: ucsi: Clear EVENT_PENDING under PPM lock
- usb: typec: Return size of buffer if pd_set operation succeeds
- usb: udc: remove warning when queue disabled ep
- usb: dwc2: gadget: LPM flow fix
- usb: dwc2: gadget: Fix exiting from clock gating
- usb: dwc2: host: Fix ISOC flow in DDMA mode
- usb: dwc2: host: Fix hibernation flow
- usb: dwc2: host: Fix remote wakeup from hibernation
- USB: core: Fix deadlock in port "disable" sysfs attribute
- USB: core: Add hub_get() and hub_put() routines
- USB: core: Fix deadlock in usb_deauthorize_interface()
- usb: dwc3: Properly set system wakeup
- staging: vc04_services: fix information leak in create_component()
- staging: vc04_services: changen strncpy() to strscpy_pad()
- scsi: core: Fix unremoved procfs host directory regression
- scsi: sd: Fix TCG OPAL unlock on system resume
- vfio/pds: Make sure migration file isn't accessed after reset
- drm/amd/display: Clear OPTC mem select on disable
- drm/amd/display: Disconnect phantom pipe OPP from OPTC being disabled
- drm/amd/display: Fix hang/underflow when transitioning to ODM4:1
- USB: UAS: return ENODEV when submit urbs fail with device not attached
- usb: cdc-wdm: close race between read and workqueue
- Revert "usb: phy: generic: Get the vbus supply"
- mtd: spinand: Add support for 5-byte IDs
- Bluetooth: hci_sync: Fix not checking error on hci_cmd_sync_cancel_sync
- drm/i915/gt: Reset queue_priority_hint on parking
- drm/i915: Do not match JSL in ehl_combo_pll_div_frac_wa_needed()
- drm/i915/dsi: Go back to the previous INIT_OTP/DISPLAY_ON order, mostly
- drm/i915/bios: Tolerate devdata==NULL in intel_bios_encoder_supports_dp_dual_mode()
- drm/i915/hwmon: Fix locking inversion in sysfs getter
- drm/amdgpu: fix deadlock while reading mqd from debugfs
- drm/amdkfd: fix TLB flush after unmap for GFX9.4.2
- drm/vmwgfx: Create debugfs ttm_resource_manager entry only if needed
- net: ll_temac: platform_get_resource replaced by wrong function
- nouveau/dmem: handle kcalloc() allocation failure
- thermal: devfreq_cooling: Fix perf state when calculate dfc res_util
- block: Do not force full zone append completion in req_bio_endio()
- sdhci-of-dwcmshc: disable PM runtime in dwcmshc_remove()
- mmc: core: Avoid negative index with array access
- mmc: core: Initialize mmc_blk_ioc_data
- mmc: sdhci-omap: re-tuning is needed after a pm transition to support emmc HS200 mode
- selftests/mm: fix ARM related issue with fork after pthread_create
- selftests/mm: sigbus-wp test requires UFFD_FEATURE_WP_HUGETLBFS_SHMEM
- mm: cachestat: fix two shmem bugs
- hexagon: vmlinux.lds.S: handle attributes section
- exec: Fix NOMMU linux_binprm::exec in transfer_args_to_stack()
- Revert "drm/amd/display: Fix sending VSC (+ colorimetry) packets for DP/eDP displays without PSR"
- wifi: iwlwifi: fw: don't always use FW dump trig
- wifi: iwlwifi: mvm: disable MLO for the time being
- wifi: cfg80211: add a flag to disable wireless extensions
- wifi: mac80211: check/clear fast rx for non-4addr sta VLAN changes
- btrfs: zoned: use zone aware sb location for scrub
- btrfs: zoned: don't skip block groups with 100% zone unusable
- btrfs: fix race in read_extent_buffer_pages()
- tmpfs: fix race on handling dquot rbtree
- ARM: prctl: reject PR_SET_MDWE on pre-ARMv6
- prctl: generalize PR_SET_MDWE support check to be per-arch
- x86/efistub: Reinstate soft limit for initrd loading
- x86/efistub: Add missing boot_params for mixed mode compat entry
- init: open /initrd.image with O_LARGEFILE
- ALSA: hda/tas2781: add locks to kcontrols
- ALSA: hda/tas2781: remove digital gain kcontrol
- perf top: Use evsel's cpus to replace user_requested_cpus
- selftests/mm: Fix build with _FORTIFY_SOURCE
- selftests/mm: gup_test: conform test to TAP format output
- pwm: img: fix pwm clock lookup
- efi: fix panic in kdump kernel
- x86/fpu: Keep xfd_state in sync with MSR_IA32_XFD
- x86/mpparse: Register APIC address only once
- kprobes/x86: Use copy_from_kernel_nofault() to read from unsafe address
- irqchip/renesas-rzg2l: Prevent spurious interrupts when setting trigger type
- irqchip/renesas-rzg2l: Rename rzg2l_irq_eoi()
- irqchip/renesas-rzg2l: Rename rzg2l_tint_eoi()
- irqchip/renesas-rzg2l: Add macro to retrieve TITSR register offset based on register's index
- irqchip/renesas-rzg2l: Flush posted write in irq_eoi()
- irqchip/renesas-rzg2l: Implement restriction when writing ISCR register
- printk: Update @console_may_schedule in console_trylock_spinning()
- iommu/dma: Force swiotlb_max_mapping_size on an untrusted device
- swiotlb: Fix alignment checks when both allocation and DMA masks are present
- swiotlb: Honour dma_alloc_coherent() alignment in swiotlb_alloc()
- swiotlb: Fix double-allocation of slots due to broken alignment handling
- entry: Respect changes to system call number by trace_sys_enter()
- ARM: 9359/1: flush: check if the folio is reserved for no-mapping addresses
- ARM: 9352/1: iwmmxt: Remove support for PJ4/PJ4B cores
- clocksource/drivers/arm_global_timer: Fix maximum prescaler value
- x86/sev: Fix position dependent variable references in startup code
- x86/Kconfig: Remove CONFIG_AMD_MEM_ENCRYPT_ACTIVE_BY_DEFAULT
- vfio/fsl-mc: Block calling interrupt handler without trigger
- vfio/platform: Create persistent IRQ handlers
- vfio/pci: Create persistent INTx handler
- vfio: Introduce interface to flush virqfd inject workqueue
- btrfs: fix deadlock with fiemap and extent locking
- xfs: remove conditional building of rt geometry validator functions
- xfs: reset XFS_ATTR_INCOMPLETE filter on node removal
- xfs: update dir3 leaf block metadata after swap
- xfs: ensure logflagsp is initialized in xfs_bmap_del_extent_real
- xfs: short circuit xfs_growfs_data_private() if delta is zero
- xfs: initialise di_crc in xfs_log_dinode
- xfs: add missing nrext64 inode flag check to scrub
- xfs: force all buffers to be written during btree bulk load
- xfs: fix an off-by-one error in xreap_agextent_binval
- xfs: recompute growfsrtfree transaction reservation while growing rt volume
- xfs: remove unused fields from struct xbtree_ifakeroot
- xfs: make xchk_iget safer in the presence of corrupt inode btrees
- xfs: don't allow overly small or large realtime volumes
- xfs: fix 32-bit truncation in xfs_compute_rextslog
- xfs: make rextslog computation consistent with mkfs
- xfs: transfer recovered intent item ownership in ->iop_recover
- xfs: pass the xfs_defer_pending object to iop_recover
- xfs: use xfs_defer_pending objects to recover intent items
- xfs: don't leak recovered attri intent items
- xfs: consider minlen sized extents in xfs_rtallocate_extent_block
- xfs: convert rt bitmap extent lengths to xfs_rtbxlen_t
- xfs: move the xfs_rtbitmap.c declarations to xfs_rtbitmap.h
- wifi: rtw88: 8821cu: Fix connection failure
- wifi: iwlwifi: pcie: fix RB status reading
- ASoC: amd: yc: Revert "Fix non-functional mic on Lenovo 21J2"
- x86/efistub: Call mixed mode boot services on the firmware's stack
- drm/amd/display: handle range offsets in VRR ranges
- drm/i915: Don't explode when the dig port we don't have an AUX CH
- iio: imu: inv_mpu6050: fix FIFO parsing when empty
- iio: imu: inv_mpu6050: fix frequency setting when chip is off
- i2c: i801: Avoid potential double call to gpiod_remove_lookup_table
- iio: accel: adxl367: fix I2C FIFO data register
- iio: accel: adxl367: fix DEVID read after reset
- arm64: dts: qcom: sc8280xp-x13s: limit pcie4 link speed
- mm, vmscan: prevent infinite loop for costly GFP_NOIO | __GFP_RETRY_MAYFAIL allocations
- ARM: imx_v6_v7_defconfig: Restore CONFIG_BACKLIGHT_CLASS_DEVICE
- tee: optee: Fix kernel panic caused by incorrect error handling
- ALSA: hda/realtek: fix mute/micmute LEDs for HP EliteBook
- ALSA: hda/realtek - Add Headset Mic supported Acer NB platform
- fs/aio: Check IOCB_AIO_RW before the struct aio_kiocb conversion
- Revert "tty: serial: simplify qcom_geni_serial_send_chunk_fifo()"
- vt: fix unicode buffer corruption when deleting characters
- mei: me: add arrow lake point H DID
- mei: me: add arrow lake point S DID
- serial: port: Don't suspend if the port is still busy
- misc: fastrpc: Pass proper arguments to scm call
- misc: lis3lv02d_i2c: Fix regulators getting en-/dis-abled twice on suspend/resume
- tty: serial: fsl_lpuart: avoid idle preamble pending if CTS is enabled
- xhci: Fix failure to detect ring expansion need.
- usb: port: Don't try to peer unused USB ports based on location
- usb: gadget: ncm: Fix handling of zero block length packets
- usb: typec: altmodes/displayport: create sysfs nodes as driver's default device attribute group
- USB: usb-storage: Prevent divide-by-0 error in isd200_ata_command
- ALSA: hda/realtek - Fix headset Mic no show at resume back for Lenovo ALC897 platform
- drm/i915: Check before removing mm notifier
- tty: serial: imx: Fix broken RS485
- drm/amdgpu/pm: Fix the error of pwm1_enable setting
- tracing: Use .flush() call to wake up readers
- SEV: disable SEV-ES DebugSwap by default
- KVM: SVM: Flush pages under kvm->lock to fix UAF in svm_register_enc_region()
- KVM: x86: Mark target gfn of emulated atomic instruction as dirty
- firewire: ohci: prevent leak of left-over IRQ on unbind
- init/Kconfig: lower GCC version check for -Warray-bounds
- Input: xpad - add additional HyperX Controller Identifiers
- cgroup/cpuset: Fix retval in update_cpumask()
- usb: typec: tpcm: Fix PORT_RESET behavior for self powered devices
- selftests: mptcp: diag: return KSFT_FAIL not test_cnt
- mm, mmap: fix vma_merge() case 7 with vma_ops->close
- xfrm: Avoid clang fortify warning in copy_to_user_tmpl()
- crypto: sun8i-ce - Fix use after free in unprepare
- crypto: rk3288 - Fix use after free in unprepare
- drm/nouveau: fix stale locked mutex in nouveau_gem_ioctl_pushbuf
- nouveau: lock the client object tree.
- Drivers: hv: vmbus: Calculate ring buffer size for more efficient use of memory
- netfilter: nf_tables: reject constant set with timeout
- netfilter: nf_tables: disallow anonymous set with timeout flag
- netfilter: nf_tables: mark set as dead when unbinding anonymous set with timeout
- net: fix IPSTATS_MIB_OUTPKGS increment in OutForwDatagrams.
- drm/amd/display: Use freesync when `DRM_EDID_FEATURE_CONTINUOUS_FREQ` found
- workqueue: Shorten events_freezable_power_efficient name
- drm/bridge: lt8912b: do not return negative values from .get_modes()
- drm/bridge: lt8912b: clear the EDID property on failures
- drm/bridge: lt8912b: use drm_bridge_edid_read()
- drm/bridge: add ->edid_read hook and drm_bridge_edid_read()
- drm/ttm: Make sure the mapped tt pages are decrypted when needed
- wifi: brcmfmac: Demote vendor-specific attach/detach messages to info
- wifi: brcmfmac: cfg80211: Use WSEC to set SAE password
- wifi: brcmfmac: add per-vendor feature detection callback
- x86/pm: Work around false positive kmemleak report in msr_build_context()
- dm snapshot: fix lockup in dm_exception_table_exit
- drm/amd/display: Fix noise issue on HDMI AV mute
- drm/amd/display: Return the correct HDCP error code
- drm/amdgpu: amdgpu_ttm_gart_bind set gtt bound flag
- ahci: asm1064: asm1166: don't limit reported ports
- ahci: asm1064: correct count of reported ports
- wireguard: selftests: set RISCV_ISA_FALLBACK on riscv{32,64}
- wireguard: netlink: access device through ctx instead of peer
- wireguard: netlink: check for dangling peer via is_dead instead of empty list
- LoongArch/crypto: Clean up useless assignment operations
- LoongArch: Define the __io_aw() hook as mmiowb()
- LoongArch: Change __my_cpu_offset definition to avoid mis-optimization
- virtio: reenable config if freezing device failed
- cxl/trace: Properly initialize cxl_poison region name
- net: hns3: tracing: fix hclgevf trace event strings
- drm/i915: Add missing ; to __assign_str() macros in tracepoint code
- NFSD: Fix nfsd_clid_class use of __string_len() macro
- net: esp: fix bad handling of pages from page_pool
- x86/CPU/AMD: Update the Zenbleed microcode revisions
- cpufreq: dt: always allocate zeroed cpumask
- mtd: rawnand: Constrain even more when continuous reads are enabled
- mtd: rawnand: Fix and simplify again the continuous read derivations
- cifs: open_cached_dir(): add FILE_READ_EA to desired access
- cifs: reduce warning log level for server not advertising interfaces
- cifs: make cifs_chan_update_iface() a void function
- cifs: delete unnecessary NULL checks in cifs_chan_update_iface()
- cifs: do not let cifs_chan_update_iface deallocate channels
- cifs: make sure server interfaces are requested only for SMB3+
- cifs: add xid to query server interface call
- nilfs2: prevent kernel bug at submit_bh_wbc()
- nilfs2: fix failure to detect DAT corruption in btree and direct mappings
- f2fs: truncate page cache before clearing flags when aborting atomic write
- f2fs: mark inode dirty for FI_ATOMIC_COMMITTED flag
- Revert "block/mq-deadline: use correct way to throttling write requests"
- memtest: use {READ,WRITE}_ONCE in memory scanning
- drm/vc4: hdmi: do not return negative values from .get_modes()
- drm/imx/ipuv3: do not return negative values from .get_modes()
- drm/exynos: do not return negative values from .get_modes()
- drm/panel: do not return negative error codes from drm_panel_get_modes()
- drm/probe-helper: warn about negative .get_modes()
- s390/zcrypt: fix reference counting on zcrypt card objects
- soc: fsl: qbman: Use raw spinlock for cgr_lock
- soc: fsl: qbman: Always disable interrupts when taking cgr_lock
- dlm: fix user space lkb refcounting
- ring-buffer: Use wait_event_interruptible() in ring_buffer_wait()
- ring-buffer: Fix full_waiters_pending in poll
- ring-buffer: Fix resetting of shortest_full
- ring-buffer: Do not set shortest_full when full target is hit
- ring-buffer: Fix waking up ring buffer readers
- io_uring: clean rings on NO_MMAP alloc fail
- platform/x86/intel/tpmi: Change vsec offset to u64
- ksmbd: retrieve number of blocks using vfs_getattr in set_file_allocation_info
- ksmbd: replace generic_fillattr with vfs_getattr
- server: convert to new timestamp accessors
- vfio/platform: Disable virqfds on cleanup
- vfio/pci: Lock external INTx masking ops
- vfio/pci: Disable auto-enable of exclusive INTx IRQ
- thermal/drivers/mediatek: Fix control buffer enablement on MT7896
- cifs: allow changing password during remount
- cifs: prevent updating file size from server if we have a read/write lease
- smb: client: stop revalidating reparse points unnecessarily
- PCI: hv: Fix ring buffer size calculation
- PCI: dwc: endpoint: Fix advertised resizable BAR size
- PCI: qcom: Enable BDF to SID translation properly
- kbuild: Move -Wenum-{compare-conditional,enum-conversion} into W=1
- NFS: Read unlock folio on nfs_page_create_from_folio() error
- nfs: fix UAF in direct writes
- sparc32: Fix parport build with sparc32
- io_uring: fix mshot io-wq checks
- io_uring/net: correctly handle multishot recvmsg retry setup
- PCI/AER: Block runtime suspend when handling errors
- speakup: Fix 8bit characters from direct synth
- usb: gadget: tegra-xudc: Fix USB3 PHY retrieval logic
- phy: tegra: xusb: Add API to retrieve the port number of phy
- slimbus: core: Remove usage of the deprecated ida_simple_xx() API
- nvmem: meson-efuse: fix function pointer type mismatch
- ext4: fix corruption during on-line resize
- hwmon: (amc6821) add of_match table
- landlock: Warn once if a Landlock action is requested while disabled
- drm/etnaviv: Restore some id values
- leds: trigger: netdev: Fix kernel panic on interface rename trig notify
- Bluetooth: btnxpuart: Fix btnxpuart_close
- mmc: core: Fix switch on gp3 partition
- mm: swap: fix race between free_swap_and_cache() and swapoff()
- mac802154: fix llsec key resources release in mac802154_llsec_key_del
- block: Fix page refcounts for unaligned buffers in __bio_release_pages()
- powerpc: xor_vmx: Add '-mhard-float' to CFLAGS
- dm-raid: fix lockdep waring in "pers->hot_add_disk"
- PCI/DPC: Quirk PIO log size for Intel Raptor Lake Root Ports
- PCI/PM: Drain runtime-idle callbacks before driver removal
- wifi: rtw88: Add missing VID/PIDs for 8811CU and 8821CU
- btrfs: fix off-by-one chunk length calculation at contains_pending_extent()
- btrfs: qgroup: always free reserved space for extent records
- serial: Lock console when calling into driver before registration
- serial: core: only stop transmit when HW fifo is empty
- usb: dwc3-am62: Disable wakeup at remove
- usb: dwc3-am62: fix module unload/reload behavior
- usb: typec: ucsi: Clean up UCSI_CABLE_PROP macros
- fuse: don't unhash root
- fuse: fix root lookup with nonzero generation
- fuse: replace remaining make_bad_inode() with fuse_make_bad()
- mmc: tmio: avoid concurrent runs of mmc_request_done()
- PM: sleep: wakeirq: fix wake irq warning in system suspend
- USB: serial: cp210x: add pid/vid for TDK NC0110013M and MM0110113M
- KVM: x86/xen: inject vCPU upcall vector when local APIC is enabled
- USB: serial: option: add MeiG Smart SLM320 product
- USB: serial: cp210x: add ID for MGP Instruments PDS100
- USB: serial: add device ID for VeriFone adapter
- USB: serial: ftdi_sio: add support for GMC Z216C Adapter IR-USB
- powerpc/fsl: Fix mfpmr build errors with newer binutils
- usb: xhci: Add error handling in xhci_map_urb_for_dma
- clk: qcom: mmcc-msm8974: fix terminating of frequency table arrays
- clk: qcom: mmcc-apq8084: fix terminating of frequency table arrays
- clk: qcom: gcc-ipq9574: fix terminating of frequency table arrays
- clk: qcom: gcc-ipq8074: fix terminating of frequency table arrays
- clk: qcom: gcc-ipq6018: fix terminating of frequency table arrays
- clk: qcom: gcc-ipq5018: fix terminating of frequency table arrays
- vfio/pds: Always clear the save/restore FDs on reset
- PM: suspend: Set mem_sleep_current during kernel command line setup
- cpufreq: Limit resolving a frequency to policy min/max
- docs: Restore "smart quotes" for quotes
- iio: adc: rockchip_saradc: use mask for write_enable bitfield
- iio: adc: rockchip_saradc: fix bitmask for channels on SARADCv2
- md/raid5: fix atomicity violation in raid5_cache_count
- parisc: Strip upper 32 bit of sum in csum_ipv6_magic for 64-bit builds
- parisc: Fix csum_ipv6_magic on 64-bit systems
- parisc: Fix csum_ipv6_magic on 32-bit systems
- parisc: Fix ip_fast_csum
- parisc: Avoid clobbering the C/B bits in the PSW with tophys and tovirt macros
- parisc/unaligned: Rewrite 64-bit inline assembly of emulate_ldd()
- x86/nmi: Fix the inverse "in NMI handler" check
- md/md-bitmap: fix incorrect usage for sb_index
- mtd: rawnand: meson: fix scrambling mode value in command macro
- ubi: correct the calculation of fastmap size
- ubifs: Set page uptodate in the correct place
- fuse: fix VM_MAYSHARE and direct_io_allow_mmap
- fat: fix uninitialized field in nostale filehandles
- bounds: support non-power-of-two CONFIG_NR_CPUS
- kasan/test: avoid gcc warning for intentional overflow
- block: Clear zone limits for a non-zoned stacked queue
- ext4: correct best extent lstart adjustment logic
- selftests/mqueue: Set timeout to 180 seconds
- sparc: vDSO: fix return value of __setup handler
- sparc64: NMI watchdog: fix return value of __setup handler
- powerpc/smp: Increase nr_cpu_ids to include the boot CPU
- powerpc/smp: Adjust nr_cpu_ids to cover all threads of a core
- powercap: intel_rapl_tpmi: Fix System Domain probing
- powercap: intel_rapl_tpmi: Fix a register bug
- powercap: intel_rapl: Fix locking in TPMI RAPL
- sched: Simplify tg_set_cfs_bandwidth()
- powercap: intel_rapl: Fix a NULL pointer dereference
- thermal/intel: Fix intel_tcc_get_temp() to support negative CPU temperature
- cpufreq: amd-pstate: Fix min_perf assignment in amd_pstate_adjust_perf()
- arm64: dts: qcom: sm8550-mtp: correct WCD9385 TX port mapping
- arm64: dts: qcom: sm8550-qrd: correct WCD9385 TX port mapping
- KVM: Always flush async #PF workqueue when vCPU is being destroyed
- media: nxp: imx8-isi: Mark all crossbar sink pads as MUST_CONNECT
- media: mc: Expand MUST_CONNECT flag to always require an enabled link
- media: mc: Rename pad variable to clarify intent
- media: mc: Add num_links flag to media_pad
- media: nxp: imx8-isi: Check whether crossbar pad is non-NULL before access
- media: mc: Fix flags handling when creating pad links
- media: mc: Add local pad to pipeline regardless of the link state
- media: xc4000: Fix atomicity violation in xc4000_get_frequency
- pci_iounmap(): Fix MMIO mapping leak
- drm/vmwgfx: Fix the lifetime of the bo cursor memory
- serial: max310x: fix NULL pointer dereference in I2C instantiation
- drm/vmwgfx: Fix possible null pointer derefence with invalid contexts
- arm: dts: marvell: Fix maxium->maxim typo in brownstone dts
- smack: Handle SMACK64TRANSMUTE in smack_inode_setsecurity()
- smack: Set SMACK64TRANSMUTE only for dirs in smack_inode_setxattr()
- clk: qcom: gcc-sdm845: Add soft dependency on rpmhpd
- remoteproc: virtio: Fix wdg cannot recovery remote processor
- arm64: dts: qcom: sc7280: Add additional MSI interrupts
- media: staging: ipu3-imgu: Set fields before media_entity_pads_init()
- wifi: brcmfmac: avoid invalid list operation when vendor attach fails
- wifi: brcmfmac: Fix use-after-free bug in brcmf_cfg80211_detach
- drm/vmwgfx: Unmap the surface before resetting it on a plane state
- KVM: x86: Use a switch statement and macros in __feature_translate()
- KVM: x86: Advertise CPUID.(EAX=7,ECX=2):EDX[5:0] to userspace
- x86/efistub: Don't clear BSS twice in mixed mode
- x86/efistub: Clear decompressor BSS in native EFI entrypoint
- dm-integrity: align the outgoing bio in integrity_recheck
- dm io: Support IO priority
- selftests: forwarding: Fix ping failure due to short timeout
- spi: spi-mt65xx: Fix NULL pointer access in interrupt handler
- netfilter: nf_tables: Fix a memory leak in nf_tables_updchain
- net: dsa: mt7530: fix handling of all link-local frames
- net: dsa: mt7530: fix link-local frames that ingress vlan filtering ports
- bpf: report RCU QS in cpumap kthread
- net: report RCU QS on threaded NAPI repolling
- rcu: add a helper to report consolidated flavor QS
- netfilter: nf_tables: do not compare internal table flags on updates
- netfilter: nft_set_pipapo: release elements in clone only from destroy path
- octeontx2-af: Use separate handlers for interrupts
- octeontx2-pf: Send UP messages to VF only when VF is up.
- octeontx2-pf: Use default max_active works instead of one
- octeontx2-pf: Wait till detach_resources msg is complete
- octeontx2: Detect the mbox up or down message via register
- devlink: fix port new reply cmd type
- net/bnx2x: Prevent access to a freed page in page_pool
- dm-integrity: fix a memory leak when rechecking the data
- net: phy: fix phy_read_poll_timeout argument type in genphy_loopback
- ceph: stop copying to iter at EOF on sync reads
- ipv4: raw: Fix sending packets from raw sockets via IPsec tunnels
- hsr: Handle failures in module init
- rds: introduce acquire/release ordering in acquire/release_in_xmit()
- wireguard: receive: annotate data-race around receiving_counter.counter
- virtio: packed: fix unmap leak for indirect desc table
- vdpa/mlx5: Allow CVQ size changes
- vdpa_sim: reset must not run
- drm: Fix drm_fixp2int_round() making it add 0.5
- spi: spi-imx: fix off-by-one in mx51 CPU mode burst length
- net: dsa: mt7530: prevent possible incorrect XTAL frequency selection
- net: veth: do not manipulate GRO when using XDP
- xfrm: Allow UDP encapsulation only in offload modes
- packet: annotate data-races around ignore_outgoing
- xen/events: increment refcnt only if event channel is refcounted
- xen/evtchn: avoid WARN() when unbinding an event channel
- riscv: Fix compilation error with FAST_GUP and rv32
- io_uring: fix poll_remove stalled req completion
- net: ethernet: mtk_eth_soc: fix PPE hanging issue
- net: mediatek: mtk_eth_soc: clear MAC_MCR_FORCE_LINK only when MAC is up
- nvme: fix reconnection fail due to reserved tag allocation
- net: txgbe: fix clk_name exceed MAX_DEV_ID limits
- hsr: Fix uninit-value access in hsr_get_node()
- vmxnet3: Fix missing reserved tailroom
- tcp: Fix refcnt handling in __inet_hash_connect().
- io_uring: Fix release of pinned pages when __io_uaddr_map fails
- cpufreq: Fix per-policy boost behavior on SoCs using cpufreq_boost_set_sw()
- soc: fsl: dpio: fix kcalloc() argument order
- net/sched: taprio: proper TCA_TAPRIO_TC_ENTRY_INDEX check
- s390/vtime: fix average steal time calculation
- octeontx2-af: Use matching wake_up API variant in CGX command interface
- rds: tcp: Fix use-after-free of net in reqsk_timer_handler().
- tcp: Fix NEW_SYN_RECV handling in inet_twsk_purge()
- nouveau: reset the bo resource bus info after an eviction
- ASoC: rockchip: i2s-tdm: Fix inaccurate sampling rates
- spi: lpspi: Avoid potential use-after-free in probe()
- io_uring: don't save/restore iowait state
- thermal/drivers/qoriq: Fix getting tmu range
- thermal/drivers/mediatek/lvts_thermal: Fix a memory leak in an error handling path
- ASoC: tlv320adc3xxx: Don't strip remove function when driver is builtin
- x86/hyperv: Use per cpu initial stack for vtl context
- usb: gadget: net2272: Use irqflags in the call to net2272_probe_fin
- staging: greybus: fix get_channel_from_mode() failure path
- serial: 8250_exar: Don't remove GPIO device on suspend
- rtc: mt6397: select IRQ_DOMAIN instead of depending on it
- bus: mhi: ep: check the correct variable in mhi_ep_register_controller()
- iio: gts-helper: Fix division loop
- kconfig: fix infinite loop when expanding a macro at the end of file
- coresight: etm4x: Set skip_power_up in etm4_init_arch_data function
- coresight: Fix issue where a source device's helpers aren't disabled
- arm64: dts: broadcom: bcmbca: bcm4908: drop invalid switch cells
- tty: serial: samsung: fix tx_empty() to return TIOCSER_TEMT
- serial: max310x: fix syntax error in IRQ error message
- tty: vt: fix 20 vs 0x20 typo in EScsiignore
- usb: phy: generic: Get the vbus supply
- iio: pressure: mprls0025pa fix off-by-one enum
- remoteproc: stm32: Fix incorrect type assignment returned by stm32_rproc_get_loaded_rsc_tablef
- remoteproc: stm32: Fix incorrect type in assignment for va
- mei: gsc_proxy: match component when GSC is on different bus
- comedi: comedi_test: Prevent timers rescheduling during deletion
- io_uring/net: correct the type of variable
- afs: Revert "afs: Hide silly-rename files from userspace"
- f2fs: zone: fix to remove pow2 check condition for zoned block device
- f2fs: compress: fix reserve_cblocks counting error when out of space
- f2fs: compress: relocate some judgments in f2fs_reserve_compress_blocks
- NFSv4.1/pnfs: fix NFS with TLS in pnfs
- NFS: Fix an off by one in root_nfs_cat()
- NFS: Fix nfs_netfs_issue_read() xarray locking for writeback interrupt
- Input: iqs7222 - add support for IQS7222D v1.1 and v1.2
- RDMA/mana_ib: Fix bug in creation of dma regions
- f2fs: ro: compress: fix to avoid caching unaligned extent
- f2fs: fix to use correct segment type in f2fs_allocate_data_block()
- watchdog: stm32_iwdg: initialize default timeout
- watchdog: starfive: Check pm_runtime_enabled() before decrementing usage counter
- f2fs: check number of blocks in a current section
- f2fs: compress: fix to check compress flag w/ .i_sem lock
- NFSv4.2: fix listxattr maximum XDR buffer size
- NFSv4.2: fix nfs4_listxattr kernel BUG at mm/usercopy.c:102
- net: sunrpc: Fix an off by one in rpc_sockaddr2uaddr()
- f2fs: compress: fix to check zstd compress level correctly in mount option
- f2fs: fix to create selinux label during whiteout initialization
- scsi: bfa: Fix function pointer type mismatch for hcb_qe->cbfn
- RDMA/rtrs-clt: Check strnlen return len in sysfs mpath_policy_store()
- RDMA/device: Fix a race between mad_client and cm_client init
- i3c: dw: Disable IBI IRQ depends on hot-join and SIR enabling
- scsi: csiostor: Avoid function pointer casts
- f2fs: fix to avoid potential panic during recovery
- f2fs: compress: fix to cover f2fs_disable_compressed_file() w/ i_sem
- f2fs: zone: fix to wait completion of last bio in zone correctly
- f2fs: fix to remove unnecessary f2fs_bug_on() to avoid panic
- f2fs: compress: fix to avoid inconsistence bewteen i_blocks and dnode
- f2fs: update blkaddr in __set_data_blkaddr() for cleanup
- f2fs: introduce get_dnode_addr() to clean up codes
- f2fs: delete obsolete FI_DROP_CACHE
- f2fs: delete obsolete FI_FIRST_BLOCK_WRITTEN
- f2fs: compress: fix to check unreleased compressed cluster
- f2fs: compress: fix to cover normal cluster write with cp_rwsem
- f2fs: compress: fix to guarantee persisting compressed blocks by CP
- RDMA/srpt: Do not register event handler until srpt device is fully setup
- RDMA/irdma: Remove duplicate assignment
- ALSA: usb-audio: Stop parsing channels bits when all channels are found.
- ALSA: hda/tas2781: restore power state after system_resume
- ALSA: hda/tas2781: configure the amp after firmware load
- ALSA: hda/tas2781: do not call pm_runtime_force_* in system_resume/suspend
- ALSA: hda/tas2781: add ptrs to calibration functions
- ALSA: hda/tas2781: do not reset cur_* values in runtime_suspend
- ALSA: hda/tas2781: add lock to system_suspend
- ALSA: hda/tas2781: use dev_dbg in system_resume
- ALSA: hda/realtek: fix ALC285 issues on HP Envy x360 laptops
- cifs: Fix writeback data corruption
- cifs: Don't use certain unnecessary folio_*() functions
- smb: do not test the return value of folio_start_writeback()
- PCI: brcmstb: Fix broken brcm_pcie_mdio_write() polling
- clk: zynq: Prevent null pointer dereference caused by kmalloc failure
- clk: Fix clk_core_get NULL dereference
- sparc32: Fix section mismatch in leon_pci_grpci
- backlight: lp8788: Fully initialize backlight_properties during probe
- backlight: lm3639: Fully initialize backlight_properties during probe
- backlight: da9052: Fully initialize backlight_properties during probe
- backlight: lm3630a: Don't set bl->props.brightness in get_brightness
- backlight: lm3630a: Initialize backlight_properties on init
- backlight: ktz8866: Correct the check for of_property_read_u32
- leds: sgm3140: Add missing timer cleanup and flash gpio control
- leds: aw2013: Unlock mutex before destroying it
- powerpc/embedded6xx: Fix no previous prototype for avr_uart_send() etc.
- mfd: cs42l43: Fix wrong GPIO_FN_SEL and SPI_CLK_CONFIG1 defaults
- modules: wait do_free_init correctly
- drm/msm/dpu: add division of drm_display_mode's hskew parameter
- clk: qcom: gcc-ipq5018: fix register offset for GCC_UBI0_AXI_ARES reset
- clk: qcom: gcc-ipq5018: fix 'halt_reg' offset of 'gcc_pcie1_pipe_clk'
- clk: qcom: gcc-ipq5018: fix 'enable_reg' offset of 'gcc_gmac0_sys_clk'
- powerpc/hv-gpci: Fix the H_GET_PERF_COUNTER_INFO hcall return value checks
- powerpc/pseries: Fix potential memleak in papr_get_attr()
- mfd: cs42l43: Fix wrong register defaults
- drm/mediatek: Fix a null pointer crash in mtk_drm_crtc_finish_page_flip
- gpio: nomadik: fix offset bug in nmk_pmx_set()
- drm/amd/pm: Fix esm reg mask use to get pcie speed
- drm/tests: helpers: Include missing drm_drv header
- arm64: ftrace: Don't forbid CALL_OPS+CC_OPTIMIZE_FOR_SIZE with Clang
- media: mediatek: vcodec: avoid -Wcast-function-type-strict warning
- media: ttpci: fix two memleaks in budget_av_attach
- media: go7007: fix a memleak in go7007_load_encoder
- media: dvb-frontends: avoid stack overflow warnings with clang
- drm/amdgpu: Fix missing break in ATOM_ARG_IMM Case of atom_get_src_int()
- HID: amd_sfh: Avoid disabling the interrupt
- HID: amd_sfh: Update HPD sensor structure elements
- perf pmu: Fix a potential memory leak in perf_pmu__lookup()
- ASoC: meson: axg-tdm-interface: add frame rate constraint
- ASoC: meson: axg-tdm-interface: fix mclk setup without mclk-fs
- mtd: rawnand: lpc32xx_mlc: fix irq handler prototype
- mtd: maps: physmap-core: fix flash size larger than 32-bit
- clk: imx: imx8mp: Fix SAI_MCLK_SEL definition
- drm/tidss: Fix sync-lost issue with two displays
- drm/tidss: Fix initial plane zpos values
- crypto: jitter - fix CRYPTO_JITTERENTROPY help text
- crypto: ccp - Avoid discarding errors in psp_send_platform_access_msg()
- crypto: arm/sha - fix function cast warnings
- perf print-events: make is_event_supported() more robust
- mfd: altera-sysmgr: Call of_node_put() only when of_parse_phandle() takes a ref
- mfd: syscon: Call of_node_put() only when of_parse_phandle() takes a ref
- media: i2c: imx290: Fix IMX920 typo
- media: ivsc: csi: Swap SINK and SOURCE pads
- drm/tegra: put drm_gem_object ref on error in tegra_fb_create
- clk: mediatek: mt7981-topckgen: flag SGM_REG_SEL as critical
- clk: mediatek: mt8183: Correct parent of CLK_INFRA_SSPM_32K_SELF
- clk: mediatek: mt7622-apmixedsys: Fix an error handling path in clk_mt8135_apmixed_probe()
- clk: mediatek: mt8135: Fix an error handling path in clk_mt8135_apmixed_probe()
- clk: hisilicon: hi3559a: Fix an erroneous devm_kfree()
- clk: hisilicon: hi3519: Release the correct number of gates in hi3519_clk_unregister()
- pinctrl: renesas: Allow the compiler to optimize away sh_pfc_pm
- PCI: Mark 3ware-9650SE Root Port Extended Tags as broken
- drm/mediatek: dsi: Fix DSI RGB666 formats and definitions
- drm/panel: boe-tv101wum-nl6: make use of prepare_prev_first
- drm/amd/display: Add 'replay' NULL check in 'edp_set_replay_allow_active()'
- clk: qcom: dispcc-sdm845: Adjust internal GDSC wait times
- media: pvrusb2: fix pvr2_stream_callback casts
- media: pvrusb2: remove redundant NULL check
- media: go7007: add check of return value of go7007_read_addr()
- media: imx: csc/scaler: fix v4l2_ctrl_handler memory leak
- media: sun8i-di: Fix chroma difference threshold
- media: sun8i-di: Fix power on/off sequences
- media: sun8i-di: Fix coefficient writes
- media: cedrus: h265: Fix configuring bitstream size
- NTB: fix possible name leak in ntb_register_device()
- drm: ci: use clk_ignore_unused for apq8016
- ASoC: SOF: Add some bounds checking to firmware data
- powerpc: Force inlining of arch_vmap_p{u/m}d_supported()
- ASoC: meson: t9015: fix function pointer type mismatch
- ASoC: meson: aiu: fix function pointer type mismatch
- perf metric: Don't remove scale from counts
- perf stat: Avoid metric-only segv
- perf expr: Fix "has_event" function for metric style events
- ALSA: seq: fix function cast warnings
- clk: renesas: r8a779f0: Correct PFC/GPIO parent clock
- clk: renesas: r8a779g0: Correct PFC/GPIO parent clocks
- drm/amd/display: fix NULL checks for adev->dm.dc in amdgpu_dm_fini()
- drm/radeon/ni: Fix wrong firmware size logging in ni_init_microcode()
- drm/msm/dpu: Only enable DSC_MODE_MULTIPLEX if dsc_merge is enabled
- drm/msm/dpu: fix the programming of INTF_CFG2_DATA_HCTL_EN
- dt-bindings: msm: qcom, mdss: Include ommited fam-b compatible
- perf srcline: Add missed addr2line closes
- perf thread_map: Free strlist on normal path in thread_map__new_by_tid_str()
- drivers/ps3: select VIDEO to provide cmdline functions
- crypto: xilinx - call finalize with bh disabled
- PCI: switchtec: Fix an error handling path in switchtec_pci_probe()
- PCI/P2PDMA: Fix a sleeping issue in a RCU read section
- quota: Properly annotate i_dquot arrays with __rcu
- quota: Fix rcu annotations of inode dquot pointers
- clk: qcom: reset: Ensure write completion on reset de/assertion
- clk: qcom: reset: Commonize the de/assert functions
- drm/amdgpu: Fix potential out-of-bounds access in 'amdgpu_discovery_reg_base_init()'
- pinctrl: mediatek: Drop bogus slew rate register range for MT8192
- pinctrl: mediatek: Drop bogus slew rate register range for MT8186
- media: edia: dvbdev: fix a use-after-free
- mtd: spinand: esmt: Extend IDs to 5 bytes
- media: v4l2-mem2mem: fix a memleak in v4l2_m2m_register_entity
- media: v4l2-tpg: fix some memleaks in tpg_alloc
- media: em28xx: annotate unchecked call to media_device_register()
- clk: meson: Add missing clocks to axg_clk_regmaps
- perf bpf: Clean up the generated/copied vmlinux.h
- perf evsel: Fix duplicate initialization of data->id in evsel__parse_sample()
- media: v4l2: cci: print leading 0 on error
- clk: samsung: exynos850: Propagate SPI IPCLK rate change
- pinctrl: renesas: r8a779g0: Add missing SCIF_CLK2 pin group/function
- drm/vmwgfx: Fix vmw_du_get_cursor_mob fencing of newly-created MOBs
- ASoC: sh: rz-ssi: Fix error message print
- drm/amd/display: Fix potential NULL pointer dereferences in 'dcn10_set_output_transfer_func()'
- perf pmu: Treat the msr pmu as software
- drm/amd/display: Fix a potential buffer overflow in 'dp_dsc_clock_en_read()'
- HID: lenovo: Add middleclick_workaround sysfs knob for cptkbd
- perf record: Check conflict between '--timestamp-filename' option and pipe mode before recording
- perf top: Uniform the event name for the hybrid machine
- perf record: Fix possible incorrect free in record__switch_output()
- PCI/DPC: Print all TLP Prefixes, not just the first
- media: cadence: csi2rx: use match fwnode for media link
- media: tc358743: register v4l2 async device only after successful setup
- dmaengine: tegra210-adma: Update dependency to ARCH_TEGRA
- ASoC: SOF: amd: Fix memory leak in amd_sof_acp_probe()
- ASoC: amd: acp: Add missing error handling in sof-mach
- drm/lima: fix a memleak in lima_heap_alloc
- drm/panel-edp: use put_sync in unprepare
- drm/rockchip: lvds: do not print scary message when probing defer
- drm/rockchip: lvds: do not overwrite error code
- drm/vmwgfx: fix a memleak in vmw_gmrid_man_get_node
- drm/vkms: Avoid reading beyond LUT array
- drm: Don't treat 0 as -1 in drm_fixp2int_ceil
- drm/rockchip: inno_hdmi: Fix video timing
- drm/tegra: output: Fix missing i2c_put_adapter() in the error handling paths of tegra_output_probe()
- drm/tegra: rgb: Fix missing clk_put() in the error handling paths of tegra_dc_rgb_probe()
- drm/tegra: rgb: Fix some error handling paths in tegra_dc_rgb_probe()
- drm/tegra: hdmi: Fix some error handling paths in tegra_hdmi_probe()
- drm/tegra: dsi: Fix missing pm_runtime_disable() in the error handling path of tegra_dsi_probe()
- drm/tegra: dsi: Fix some error handling paths in tegra_dsi_probe()
- drm/tegra: dpaux: Fix PM disable depth imbalance in tegra_dpaux_probe
- drm/tegra: dsi: Add missing check for of_find_device_by_node
- dm: call the resume method on internal suspend
- dm raid: fix false positive for requeue needed during reshape
- bpf: hardcode BPF_PROG_PACK_SIZE to 2MB * num_possible_nodes()
- nfp: flower: handle acti_netdevs allocation failure
- net/x25: fix incorrect parameter validation in the x25_getsockopt() function
- net: kcm: fix incorrect parameter validation in the kcm_getsockopt) function
- udp: fix incorrect parameter validation in the udp_lib_getsockopt() function
- l2tp: fix incorrect parameter validation in the pppol2tp_getsockopt() function
- ipmr: fix incorrect parameter validation in the ip_mroute_getsockopt() function
- tcp: fix incorrect parameter validation in the do_tcp_getsockopt() function
- OPP: debugfs: Fix warning around icc_get_name()
- erofs: fix lockdep false positives on initializing erofs_pseudo_mnt
- net: phy: dp83822: Fix RGMII TX delay configuration
- Bluetooth: Fix eir name length
- net: phy: fix phy_get_internal_delay accessing an empty array
- net: ip_tunnel: make sure to pull inner header in ip_tunnel_rcv()
- ipv6: fib6_rules: flush route cache when rule is changed
- iommu: Fix compilation without CONFIG_IOMMU_INTEL
- bpf: Fix stackmap overflow check on 32-bit arches
- bpf: Fix hashtab overflow check on 32-bit arches
- bpf: Fix DEVMAP_HASH overflow check on 32-bit arches
- s390/cache: prevent rebuild of shared_cpu_list
- Bluetooth: fix use-after-free in accessing skb after sending it
- Bluetooth: af_bluetooth: Fix deadlock
- Bluetooth: btusb: Fix memory leak
- Bluetooth: msft: Fix memory leak
- Bluetooth: msft: __hci_cmd_sync() doesn't return NULL
- Bluetooth: hci_core: Fix possible buffer overflow
- Bluetooth: btrtl: fix out of bounds memory access
- Bluetooth: hci_h5: Add ability to allocate memory for private data
- Bluetooth: hci_sync: Fix overwriting request callback
- Bluetooth: hci_core: Cancel request on command timeout
- Bluetooth: hci_qca: don't use IS_ERR_OR_NULL() with gpiod_get_optional()
- Bluetooth: hci_event: Fix not indicating new connection for BIG Sync
- Bluetooth: Remove BT_HS
- Bluetooth: Remove superfluous call to hci_conn_check_pending()
- Bluetooth: mgmt: Remove leftover queuing of power_off work
- Bluetooth: Remove HCI_POWER_OFF_TIMEOUT
- ice: fix stats being updated by way too large values
- igb: Fix missing time sync events
- igc: Fix missing time sync events
- iommu/vt-d: Don't issue ATS Invalidation request when device is disconnected
- PCI: Make pci_dev_is_disconnected() helper public for other drivers
- wifi: brcm80211: handle pmk_op allocation failure
- wifi: rtw88: 8821c: Fix false alarm count
- wifi: rtw88: 8821c: Fix beacon loss and disconnect
- wifi: rtw88: 8821cu: Fix firmware upload fail
- ACPI: CPPC: enable AMD CPPC V2 support for family 17h processors
- mmc: wmt-sdmmc: remove an incorrect release_mem_region() call in the .remove function
- arm64: dts: qcom: sm8550: Fix SPMI channels size
- SUNRPC: fix some memleaks in gssx_dec_option_array
- SUNRPC: fix a memleak in gss_import_v2_context
- x86, relocs: Ignore relocations in .notes section
- objtool: Fix UNWIND_HINT_{SAVE,RESTORE} across basic blocks
- arm64: dts: rockchip: drop rockchip,trcm-sync-tx-only from rk3588 i2s
- arm64: dts: rockchip: fix reset-names for rk356x i2s2 controller
- arm64: dts: rockchip: add missing interrupt-names for rk356x vdpu
- ACPI: scan: Fix device check notification handling
- ACPI: resource: Add MAIBENBEN X577 to irq1_edge_low_force_override
- ACPI: resource: Do IRQ override on Lunnen Ground laptops
- ACPI: resource: Add Infinity laptops to irq1_edge_low_force_override
- arm64: dts: marvell: reorder crypto interrupts on Armada SoCs
- gpiolib: Pass consumer device through to core in devm_fwnode_gpiod_get_index()
- regulator: userspace-consumer: add module device table
- arm64: dts: imx8mp-evk: Fix hdmi@3d node
- arm64: dts: imx8mp: Set SPI NOR to max 40 MHz on Data Modul i.MX8M Plus eDM SBC
- ARM: dts: imx6dl-yapp4: Move the internal switch PHYs under the switch node
- ARM: dts: imx6dl-yapp4: Fix typo in the QCA switch register address
- arm64: dts: allwinner: h6: Add RX DMA channel for SPDIF
- pstore: inode: Only d_invalidate() is needed
- pstore: inode: Convert mutex usage to guard(mutex)
- net: mctp: copy skb ext data when fragmenting
- arm64: dts: renesas: r8a779g0: Correct avb[01] reg sizes
- arm64: dts: renesas: r8a779a0: Correct avb[01] reg sizes
- arm64: dts: renesas: rzg2l: Add missing interrupts to IRQC nodes
- wifi: mt76: mt792x: fix a potential loading failure of the 6Ghz channel config from ACPI
- wifi: mt76: mt7921e: fix use-after-free in free_irq()
- wifi: mt76: mt792x: fix ethtool warning
- wifi: mt76: mt7996: fix HIF_TXD_V2_1 value
- wifi: mt76: mt7996: fix efuse reading issue
- wifi: mt76: mt7996: fix HE beamformer phy cap for station vif
- wifi: mt76: mt7996: fix incorrect interpretation of EHT MCS caps
- wifi: mt76: mt7996: fix TWT issues
- memory: tegra: Correct DLA client names
- ARM: dts: arm: realview: Fix development chip ROM compatible value
- wifi: wilc1000: revert reset line logic flip
- arm64: dts: ti: k3-am62p: Fix memory ranges for DMSS
- firmware: arm_scmi: Fix double free in SMC transport cleanup path
- arm64: dts: ti: Add common1 register space for AM62x SoC
- arm64: dts: ti: Add common1 register space for AM65x SoC
- arm64: dts: mt8195-cherry-tomato: change watchdog reset boot flow
- arm64: dts: ti: k3-am64-main: Fix ITAP/OTAP values for MMC
- arm64: dts: ti: k3-am64: Enable SDHCI nodes at the board level
- arm64: dts: ti: k3-am642-sk: Add boot phase tags marking
- arm64: dts: ti: k3-am642-evm: Add boot phase tags marking
- arm64: dts: ti: k3-j784s4-evm: Remove Pinmux for CTS and RTS in wkup_uart0
- arm64: dts: ti: k3-j721s2-common-proc-board: Remove Pinmux for CTS and RTS in wkup_uart0
- arm64: dts: ti: k3-j7200-common-proc-board: Remove clock-frequency from mcu_uart0
- arm64: dts: ti: k3-j7200-common-proc-board: Modify Pinmux for wkup_uart0 and mcu_uart0
- net: ena: Remove ena_select_queue
- powercap: dtpm_cpu: Fix error check against freq_qos_add_request()
- arm64: dts: qcom: sm8150: correct PCIe wake-gpios
- arm64: dts: qcom: sm8150: use 'gpios' suffix for PCI GPIOs
- arm64: dts: qcom: sdm845-db845c: correct PCIe wake-gpios
- wifi: brcmsmac: avoid function pointer casts
- iommu/amd: Mark interrupt as managed
- bus: tegra-aconnect: Update dependency to ARCH_TEGRA
- arm64: dts: ti: k3-am62-main: disable usb lpm
- wifi: wilc1000: prevent use-after-free on vif when cleaning up all interfaces
- cpufreq: qcom-hw: add CONFIG_COMMON_CLK dependency
- arm64: dts: mediatek: mt8186: Add missing xhci clock to usb controllers
- arm64: dts: mediatek: mt8186: Add missing clocks to ssusb power domains
- ARM: dts: qcom: msm8974: correct qfprom node size
- soc: qcom: llcc: Check return value on Broadcast_OR reg read
- arm64: dts: qcom: sdm845: Use the Low Power Island CX/MX for SLPI
- bpf: Mark bpf_spin_{lock,unlock}() helpers with notrace correctly
- wifi: iwlwifi: mvm: Fix the listener MAC filter flags
- can: m_can: Start/Cancel polling timer together with interrupts
- arm64: dts: mediatek: mt7622: add missing "device_type" to memory nodes
- arm64: dts: mediatek: mt8186: fix VENC power domain clocks
- arm64: dts: mediatek: mt8192: fix vencoder clock name
- arm64: dts: mediatek: mt8192-asurada: Remove CrosEC base detection node
- arm64: dts: mediatek: mt7986: add "#reset-cells" to infracfg
- arm64: dts: mediatek: mt7986: drop "#clock-cells" from PWM
- arm64: dts: mediatek: mt7986: fix SPI nodename
- arm64: dts: mediatek: mt7986: fix SPI bus width properties
- arm64: dts: mediatek: mt7986: drop crypto's unneeded/invalid clock name
- arm64: dts: mediatek: mt7986: fix reference to PWM in fan node
- arm64: dts: mt8183: Move CrosEC base detection node to kukui-based DTs
- ipv6: mcast: remove one synchronize_net() barrier in ipv6_mc_down()
- selftests: forwarding: Add missing multicast routing config entries
- selftests: forwarding: Add missing config entries
- s390/vdso: drop '-fPIC' from LDFLAGS
- s390/pai: fix attr_event_free upper limit for pai device drivers
- wifi: iwlwifi: mvm: don't set replay counters to 0xff
- wifi: iwlwifi: mvm: don't set the MFP flag for the GTK
- wifi: iwlwifi: mvm: fix erroneous queue index mask
- wifi: iwlwifi: support EHT for WH
- tools/resolve_btfids: Fix cross-compilation to non-host endianness
- tools/resolve_btfids: Refactor set sorting with types from btf_ids.h
- pwm: sti: Fix capture for st,pwm-num-chan < st,capture-num-chan
- printk: Disable passing console lock owner completely during panic()
- wifi: ath12k: fix incorrect logic of calculating vdev_stats_id
- arm64: dts: qcom: sm6115: declare VLS CLAMP register for USB3 PHY
- arm64: dts: qcom: qcm2290: declare VLS CLAMP register for USB3 PHY
- wifi: wfx: fix memory leak when starting AP
- libbpf: Use OPTS_SET() macro in bpf_xdp_query()
- wifi: libertas: fix some memleaks in lbs_allocate_cmd_buffer()
- wifi: ath11k: initialize rx_mcs_80 and rx_mcs_160 before use
- arm64: dts: ti: k3-j784s4: Fix power domain for VTM node
- arm64: dts: ti: k3-j721s2: Fix power domain for VTM node
- net: blackhole_dev: fix build warning for ethh set but not used
- pwm: atmel-hlcdc: Fix clock imbalance related to suspend support
- arm64: dts: imx8mm-venice-gw71xx: fix USB OTG VBUS
- gpio: vf610: allow disabling the vf610 driver
- wifi: iwlwifi: read BIOS PNVM only for non-Intel SKU
- wifi: iwlwifi: mvm: fix the TLC command after ADD_STA
- wifi: iwlwifi: mvm: d3: fix IPN byte order
- wifi: iwlwifi: fix EWRD table validity check
- wifi: iwlwifi: mvm: initialize rates in FW earlier
- wifi: iwlwifi: acpi: fix WPFC reading
- wifi: iwlwifi: dbg-tlv: ensure NUL termination
- wifi: iwlwifi: mvm: report beacon protection failures
- wifi: ath12k: fix fetching MCBC flag for QCN9274
- wifi: ath12k: Update Qualcomm Innovation Center, Inc. copyrights
- wifi: ath11k: change to move WMI_VDEV_PARAM_SET_HEMU_MODE before WMI_PEER_ASSOC_CMDID
- wifi: ath9k: delay all of ath9k_wmi_event_tasklet() until init is complete
- libbpf: Add missing LIBBPF_API annotation to libbpf_set_memlock_rlim API
- arm64: dts: imx8mm-kontron: Fix interrupt for RTC on OSM-S i.MX8MM module
- arm64: dts: imx8mm-kontron: Disable pull resistors for SD card signals on BL board
- arm64: dts: imx8mm-kontron: Disable pull resistors for SD card signals on BL OSM-S board
- arm64: dts: imx8mm-kontron: Disable pullups for onboard UART signals on BL board
- arm64: dts: imx8mm-kontron: Disable pullups for onboard UART signals on BL OSM-S board
- arm64: dts: imx8mm-kontron: Disable pullups for I2C signals on SL/BL i.MX8MM
- arm64: dts: imx8mm-kontron: Disable pullups for I2C signals on OSM-S i.MX8MM
- selftests/bpf: Disable IPv6 for lwt_redirect test
- arm64: dts: renesas: r8a779g0: Add missing SCIF_CLK2
- arm64: dts: renesas: r8a779g0: Restore sort order
- arm64: dts: qcom: sa8540p: Drop gfx.lvl as power-domain for gpucc
- pmdomain: qcom: rpmhpd: Drop SA8540P gfx.lvl
- libbpf: Fix faccessat() usage on Android
- cpufreq: mediatek-hw: Don't error out if supply is not found
- arm64: dts: qcom: sdm845-oneplus-common: improve DAI node naming
- soc: qcom: socinfo: rename PM2250 to PM4125
- arm64: dts: qcom: sm8450: Add missing interconnects to serial
- af_unix: Annotate data-race of gc_in_progress in wait_for_unix_gc().
- selftests/bpf: Wait for the netstamp_needed_key static key to be turned on
- selftests/bpf: Fix the flaky tc_redirect_dtime test
- selftests/bpf: Add netkit to tc_redirect selftest
- selftests/bpf: De-veth-ize the tc_redirect test case
- wifi: ath12k: Fix issues in channel list update
- selftest/bpf: Add map_in_maps with BPF_MAP_TYPE_PERF_EVENT_ARRAY values
- libbpf: Apply map_set_def_max_entries() for inner_maps on creation
- selftests/bpf: Fix potential premature unload in bpf_testmod
- bpftool: Silence build warning about calloc()
- inet_diag: annotate data-races around inet_diag_table[]
- sock_diag: annotate data-races around sock_diag_handlers[family]
- cpufreq: mediatek-hw: Wait for CPU supplies before probing
- cpufreq: brcmstb-avs-cpufreq: add check for cpufreq_cpu_get's return value
- arm64: dts: qcom: sc8180x: Shrink aoss_qmp register space size
- arm64: dts: qcom: sc8180x: Require LOW_SVS vote for MMCX if DISPCC is on
- arm64: dts: qcom: sc8180x: Don't hold MDP core clock at FMAX
- arm64: dts: qcom: sc8180x: Fix eDP PHY power-domains
- arm64: dts: qcom: sc8180x: Add missing CPU off state
- arm64: dts: qcom: sc8180x: Fix up big CPU idle state entry latency
- arm64: dts: qcom: sc8180x: Hook up VDD_CX as GCC parent domain
- ARM: dts: renesas: r8a73a4: Fix external clocks and clock rate
- wifi: mwifiex: debugfs: Drop unnecessary error check for debugfs_create_dir()
- wifi: wilc1000: fix multi-vif management when deleting a vif
- wifi: wilc1000: do not realloc workqueue everytime an interface is added
- wifi: rtl8xxxu: add cancel_work_sync() for c2hcmd_work
- wifi: wilc1000: fix RCU usage in connect path
- wifi: wilc1000: fix declarations ordering
- wifi: b43: Disable QoS for bcm4331
- wifi: b43: Stop correct queue in DMA worker when QoS is disabled
- wifi: b43: Stop/wake correct queue in PIO Tx path when QoS is disabled
- wifi: b43: Stop/wake correct queue in DMA Tx path when QoS is disabled
- wifi: ath10k: fix NULL pointer dereference in ath10k_wmi_tlv_op_pull_mgmt_tx_compl_ev()
- timekeeping: Fix cross-timestamp interpolation for non-x86
- timekeeping: Fix cross-timestamp interpolation corner case decision
- timekeeping: Fix cross-timestamp interpolation on counter wrap
- x86/sme: Fix memory encryption setting if enabled by default and not overridden
- x86/mm: Ensure input to pfn_to_kaddr() is treated as a 64-bit type
- aoe: fix the potential use-after-free problem in aoecmd_cfg_pkts
- io_uring/net: fix overflow check in io_recvmsg_mshot_prep()
- io_uring/net: move receive multishot out of the generic msghdr path
- io_uring/net: unify how recvmsg and sendmsg copy in the msghdr
- rtc: test: Fix invalid format specifier.
- time: test: Fix incorrect format specifier
- lib: memcpy_kunit: Fix an invalid format specifier in an assertion msg
- lib/cmdline: Fix an invalid format specifier in an assertion msg
- kunit: test: Log the correct filter string in executor_test
- ovl: Always reject mounting over case-insensitive directories
- ovl: add support for appending lowerdirs one by one
- ovl: refactor layer parsing helpers
- ovl: store and show the user provided lowerdir mount option
- ovl: remove unused code in lowerdir param parsing
- md: Don't clear MD_CLOSING when the raid is about to stop
- fs/select: rework stack allocation hack for clang
- rcu/exp: Handle RCU expedited grace period kworker allocation failure
- rcu/exp: Fix RCU expedited parallel grace period kworker allocation failure recovery
- s390/dasd: fix double module refcount decrement
- s390/dasd: Use dev_*() for device log messages
- io_uring: remove unconditional looping in local task_work handling
- io_uring: remove looping around handling traditional task_work
- fs: Fix rw_hint validation
- workqueue: Introduce struct wq_node_nr_active
- workqueue: Make wq_adjust_max_active() round-robin pwqs while activating
- workqueue: Move nr_active handling into helpers
- workqueue: Replace pwq_activate_inactive_work() with [__]pwq_activate_work()
- workqueue: Factor out pwq_is_empty()
- workqueue: Move pwq->max_active to wq->max_active
- workqueue.c: Increase workqueue name length
- ASoC: wm8962: Fix up incorrect error message in wm8962_set_fll
- ASoC: wm8962: Enable both SPKOUTR_ENA and SPKOUTL_ENA in mono mode
- ASoC: wm8962: Enable oscillator if selecting WM8962_FLL_OSC
- Input: gpio_keys_polled - suppress deferred probe error for gpio
- xfrm: set skb control buffer based on packet offload as well
- xfrm: fix xfrm child route lookup for packet offload
- ASoC: amd: yc: Add HP Pavilion Aero Laptop 13-be2xxx(8BD6) into DMI quirk table
- x86/hyperv: Allow 15-bit APIC IDs for VTL platforms
- ASoC: Intel: bytcr_rt5640: Add an extra entry for the Chuwi Vi8 tablet
- arm64: tegra: Set the correct PHY mode for MGBE
- perf: RISCV: Fix panic on pmu overflow handler
- firewire: core: use long bus reset on gap count error
- Bluetooth: mgmt: Fix limited discoverable off timeout
- ASoC: amd: yc: Fix non-functional mic on Lenovo 21J2
- drm/amdgpu: Enable gpu reset for S3 abort cases on Raven series
- ALSA: hda/realtek - ALC285 reduce pop noise from Headphone port
- scsi: mpt3sas: Prevent sending diag_reset when the controller is ready
- ASoC: amd: yc: Add Lenovo ThinkBook 21J0 into DMI quirk table
- drm/ttm/tests: depend on UML || COMPILE_TEST
- wifi: mac80211: only call drv_sta_rc_update for uploaded stations
- net: smsc95xx: add support for SYS TEC USB-SPEmodule1
- regulator: max5970: Fix regulator child node name
- ARM: dts: renesas: rcar-gen2: Add missing #interrupt-cells to DA9063 nodes
- arm64: dts: qcom: Fix interrupt-map cell sizes
- arm: dts: Fix dtc interrupt_map warnings
- arm64: dts: Fix dtc interrupt_provider warnings
- arm: dts: Fix dtc interrupt_provider warnings
- dm-verity, dm-crypt: align "struct bvec_iter" correctly
- platform/x86: x86-android-tablets: Fix acer_b1_750_goodix_gpios name
- perf: CXL: fix CPMU filter value mask length
- cxl/region: Allow out of order assembly of autodiscovered regions
- cxl/region: Handle endpoint decoders in cxl_region_find_decoder()
- block: sed-opal: handle empty atoms when parsing response
- parisc/ftrace: add missing CONFIG_DYNAMIC_FTRACE check
- net/iucv: fix the allocation size of iucv_path_table array
- x86/mm: Disallow vsyscall page read for copy_from_kernel_nofault()
- x86/mm: Move is_vsyscall_vaddr() into asm/vsyscall.h
- riscv: dts: sifive: add missing #interrupt-cells to pmic
- ARM: dts: rockchip: Drop interrupts property from pwm-rockchip nodes
- RDMA/mlx5: Relax DEVX access upon modify commands
- RDMA/mlx5: Fix fortify source warning while accessing Eth segment
- arm64: dts: rockchip: mark system power controller on rk3588-evb1
- soc: microchip: Fix POLARFIRE_SOC_SYS_CTRL input prompt
- arm64/sve: Lower the maximum allocation for the SVE ptrace regset
- gen_compile_commands: fix invalid escape sequence warning
- ASoC: SOF: ipc4-pcm: Workaround for crashed firmware on system suspend
- HID: multitouch: Add required quirk for Synaptics 0xcddc device
- MIPS: Clear Cause.BD in instruction_pointer_set
- x86/xen: Add some null pointer checking to smp.c
- ASoC: amd: yc: Fix non-functional mic on Lenovo 82UU
- regmap: kunit: Ensure that changed bytes are actually different
- spi: intel-pci: Add support for Lunar Lake-M SPI serial flash
- ASoC: rt5645: Make LattePanda board DMI match more precise
- selftests: tls: use exact comparison in recv_partial
- selftests: openvswitch: Add validation for the recursion test
- perf/arm-cmn: Workaround AmpereOneX errata AC04_MESH_1 (incorrect child count)
- wifi: iwlwifi: mvm: use correct address 3 in A-MSDU
- ASoC: cs42l43: Handle error from devm_pm_runtime_enable
- media: rkisp1: Fix IRQ handling due to shared interrupts
- soc: qcom: pmic_glink_altmode: fix drm bridge use-after-free
- io_uring: drop any code related to SCM_RIGHTS
- io_uring/unix: drop usage of io_uring socket
- platform/x86: p2sb: On Goldmont only cache P2SB and SPI devfn BAR
- !6730  quota: Fix potential NULL pointer dereference
- quota: Fix potential NULL pointer dereference
- !6782 i2c: hisi: Add I2C controller reset and initialization  proccess in bus recovery action
- i2c: hisi: Correct the description comment for PIN_MUX METHOD
- i2c: hisi: Add I2C controller reset and initialization proccess in bus recovery action
- !6760 spi: hisi-kunpeng: Delete the dump interface of data registers in debugfs
- spi: hisi-kunpeng: Delete the dump interface of data registers in debugfs
- !3176 [OLK-6.6] Turning off Zhaoxin ahci controller runtime pm
- Turning off Zhaoxin ahci controller runtime pm
- !6403  iommu/arm-smmu-v3: fix using uninitialized or unchecked symbol
- iommu/arm-smmu-v3: fix using uninitialized or unchecked symbol
- !6479  do_sys_name_to_handle(): use kzalloc() to fix kernel-infoleak
- do_sys_name_to_handle(): use kzalloc() to fix kernel-infoleak
- !6005 [OLK-6.6]Add Yunsilicon eth driver and rdma driver
- drivers: support for xsc drivers from Yunsilicon Technology
- !6595  A Solution to Re-enable hugetlb vmemmap optimize on ARM64
- arm64: update openeuler_defconfig for HVO enable
- arm64: mm: Re-enable OPTIMIZE_HUGETLB_VMEMMAP
- arm64: mm: HVO: support BBM of vmemmap pgtable safely
- mm: HVO: introduce helper function to update and flush pgtable
- !6731 [OLK-6.6] watchdog: Fix call trace when failed to initialize sdei
- watchdog: Fix call trace when failed to initialize sdei
- !6651 [OLK - 6.6]net: hns3: add support for Hisilicon ptp sync device
- net: hns3: add support for Hisilicon ptp sync device
- !6385  ipvlan: Fix warning while IPVLAN_L2E disabled
- ipvlan: Fix warning while IPVLAN_L2E disabled
- !6409 [OLK-6.6] irqchip: gic-v3: Collection table support muti pages
- irqchip: gic-v3: Collection table support muti pages
- !6735 v2  SUNRPC: Fix a slow server-side memory leak with RPC-over-TCP
- SUNRPC: Fix a slow server-side memory leak with RPC-over-TCP
- !6590 v6  Introduce BPF_READAHEAD option for optimizing read performance
- arch: Add BPF_READAHEAD config options for supported architectures
- mm, fs: Add BPF_READAHEAD build option for bpf readhead
- !6681 v2  btrfs: fix data races when accessing the reserved amount of block reserves
- btrfs: fix data races when accessing the reserved amount of block reserves

* Sun Apr 28 2024 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-23.0.0.26
- !6306 【OLK-6.6】fix compiling problem in bzwx N5/N6 series NIC drivers
- drivers: fix compiling problem in bzwx N5/N6 series NIC drivers
- !6692  ipvlan: enable CONFIG_IPVLAN_L2E option in openeuler config
- ipvlan: enable CONFIG_IPVLAN_L2E option in openeuler config
- !6632  ext4: use iomap for regular file's buffered IO path and enable large foilo
- ext4: add mount option for buffered IO iomap path
- ext4: don't mark IOMAP_F_DIRTY for buffer write
- ext4: enable large folio for regular file with iomap buffered IO path
- filemap: support disable large folios on active inode
- ext4: partial enable iomap for regular file's buffered IO path
- ext4: fall back to buffer_head path for defrag
- ext4: writeback partial blocks before zeroing out range
- ext4: implement zero_range iomap path
- ext4: implement mmap iomap path
- ext4: implement writeback iomap path
- ext4: implement buffered write iomap path
- ext4: implement buffered read iomap path
- ext4: add a new iomap aops for regular file's buffered IO path
- ext4: introduce seq counter for the extent status entry
- ext4: factor out ext4_map_create_blocks() to allocate new blocks
- ext4: use reserved metadata blocks when splitting extent on endio
- ext4: make ext4_da_map_blocks() buffer_head unaware
- ext4: make ext4_insert_delayed_block() insert multi-blocks
- ext4: factor out check for whether a cluster is allocated
- ext4: make ext4_da_reserve_space() reserve multi-clusters
- ext4: make ext4_es_insert_delayed_block() insert multi-blocks
- ext4: drop iblock parameter
- ext4: trim delalloc extent
- ext4: check the extent status again before inserting delalloc block
- ext4: factor out a common helper to query extent map
- ext4: make ext4_set_iomap() recognize IOMAP_DELALLOC map type
- ext4: make ext4_map_blocks() distinguish delalloc only extent
- ext4: add a hole extent entry in cache after punch
- ext4: convert to exclusive lock while inserting delalloc extents
- ext4: refactor ext4_da_map_blocks()
- iomap: do some small logical cleanup in buffered write
- iomap: make iomap_write_end() return a boolean
- iomap: use a new variable to handle the written bytes in iomap_write_iter()
- iomap: don't increase i_size if it's not a write operation
- iomap: drop the write failure handles when unsharing and zeroing
- xfs: convert delayed extents to unwritten when zeroing post eof blocks
- xfs: make xfs_bmapi_convert_delalloc() to allocate the target offset
- xfs: make the seq argument to xfs_bmapi_convert_delalloc() optional
- xfs: match lock mode in xfs_buffered_write_iomap_begin()
- iomap: add pos and dirty_len into trace_iomap_writepage_map
- iomap: pass the length of the dirty region to ->map_blocks
- iomap: map multiple blocks at a time
- iomap: submit ioends immediately
- iomap: factor out a iomap_writepage_map_block helper
- iomap: only call mapping_set_error once for each failed bio
- iomap: don't chain bios
- iomap: move the iomap_sector sector calculation out of iomap_add_to_ioend
- iomap: clean up the iomap_alloc_ioend calling convention
- iomap: move all remaining per-folio logic into iomap_writepage_map
- iomap: factor out a iomap_writepage_handle_eof helper
- iomap: move the PF_MEMALLOC check to iomap_writepages
- iomap: move the io_folios field out of struct iomap_ioend
- iomap: treat inline data in iomap_writepage_map as an I/O error
- iomap: clear the per-folio dirty bits on all writeback failures
- !6625 v2  perf data convert: Fix segfault when converting to json when cpu_desc isn't set
- perf data convert: Fix segfault when converting to json when cpu_desc isn't set
- !6647  infiniband/hw/hiroce3: Add Huawei Intelligent Network Card RDMA Driver
- infiniband/hw/hiroce3: Add Huawei Intelligent Network Card RDMA Driver
- net/ethernet/huawei/hinic3: Add the CQM on which the RDMA depends
- !6624  hisi-acc-vfio-pci:add DFX for acc migration driver
- hisi_acc_vfio_pci: add exception error handling
- hisi-acc-vfio-pci:add DFX for acc migration driver
- !6658  sched: disable sched_autogroup by default
- sched: disable sched_autogroup by default
- !6626  Backport page fault and fork optimization
- mm: swapfile: check usable swap device in __folio_throttle_swaprate()
- mm/filemap: optimize filemap folio adding
- lib/xarray: introduce a new helper xas_get_order
- lib/xarray: introduce a new helper xas_get_order
- mm/filemap: clean up hugetlb exclusion code
- mm/filemap: return early if failed to allocate memory for split
- mm: memory: check userfaultfd_wp() in vmf_orig_pte_uffd_wp()
- !6179 crypto: hisilicon - fixed some code security review issues
- crypto: hisilicon/debugfs - Resolve the problem of applying for redundant space in sq dump
- crypto: hisilicon/sec - Fix memory leak for sec resource release
- crypto: hisilicon - Adjust debugfs creation and release order
- crypto: hisilicon/qm - Add the default processing branch
- crypto: hisilicon/debugfs - Fix the processing logic issue in the debugfs creation
- crypto: hisilicon/sgl - Delete redundant parameter verification
- crypto: hisilicon/debugfs - Fix debugfs uninit process issue
- crypto: hisilicon/sec - Add the condition for configuring the sriov function
- crypto: hisilicon/zip - fix the missing CRYPTO_ALG_ASYNC in cra_flags
- !6400  btrfs: fix data race at btrfs_use_block_rsv() when accessing block reserve
- btrfs: fix data race at btrfs_use_block_rsv() when accessing block reserve
- !6444  Fix CVE-2024-26869
- f2fs: fix to truncate meta inode pages forcely
- f2fs: introduce f2fs_invalidate_internal_cache() for cleanup
- !6585  ACPI: processor_idle: Fix memory leak in acpi_processor_power_exit()
- ACPI: processor_idle: Fix memory leak in acpi_processor_power_exit()
- !6251  ubi: Check for too small LEB size in VTBL code
- ubi: Check for too small LEB size in VTBL code
- !6418  media: pvrusb2: fix uaf in pvr2_context_set_notify
- media: pvrusb2: fix uaf in pvr2_context_set_notify

* Wed Apr 24 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-22.0.0.25
- !6467 RDMA/hns: Some bugfixes and cleanups
- RDMA/hns: Fix incorrect variable usage in scc_attr_is_visible()
- RDMA/hns: Fix null pointer when alloc_scc_param() fails
- RDMA/hns: Fix scc_param delay_work to execute after sysfs shutdown
- RDMA/hns: Add mutex_destroy() to destroy the mutex
- RDMA/hns: Fix a potential Sleep-in-Atomic-Context
- !6468 v2  scsi: fnic: Move fnic_fnic_flush_tx() to a work queue
- scsi: fnic: Move fnic_fnic_flush_tx() to a work queue
- !6439 v3  m: convert mm's rss stats to use atomic mode
- mm: convert mm's rss stats to use atomic mode
- percpu_counter: introduce atomic mode for percpu_counter
- !6424  mm/migrate: correct nr_failed in migrate_pages_sync()
- mm/migrate: add nr_split to trace_mm_migrate_pages stats.
- mm/migrate: correct nr_failed in migrate_pages_sync()
- !6390  nfs: fix panic when nfs4_ff_layout_prepare_ds() fails
- nfs: fix panic when nfs4_ff_layout_prepare_ds() fails
- !5482 [OLK-6.6] crypto: update zhaoxin-aes for __pcpu_unique_paes_last_cword
- crypto: update zhaoxin-aes for __pcpu_unique_paes_last_cword
- !3171 [OLK-6.6] ata: libata: disabling PhyRdy Change Interrupt based on actual LPM capability
- ata: libata: disabling PhyRdy Change Interrupt based on actual LPM capability
- !6443  f2fs: fix NULL pointer dereference in f2fs_submit_page_write()
- f2fs: fix NULL pointer dereference in f2fs_submit_page_write()
- !6261 RDMA/hns: Some bugfixes and cleanups
- RDMA/hns: Modify the print level of CQE error
- RDMA/hns: Add mutex_destroy()
- RDMA/hns: Fix GMV table pagesize
- RDMA/hns: Fix mismatch exception rollback
- RDMA/hns: Fix UAF for cq async event
- RDMA/hns: Fix deadlock on SRQ async events.
- RDMA/hns: Remove unused parameters and variables
- RDMA/hns: Use macro instead of magic number
- RDMA/hns: Fix return value in hns_roce_map_mr_sg
- !6265 tpm_tis: Avoid warning splat at shutdown
- tpm,tpm_tis: Avoid warning splat at shutdown
- !6402  bpf: Add missing BPF_LINK_TYPE invocations
- bpf: Add missing BPF_LINK_TYPE invocations
- !6256 [OLK-6.6] bugfix from upstream v6.9 for AMD EPYC perf
- perf/x86/amd/core: Define a proper ref-cycles event for Zen 4 and later
- perf/x86/amd/core: Update and fix stalled-cycles-* events for Zen 2 and later
- perf/x86/amd/lbr: Use freeze based on availability
- !6134 v3  rootfs: Fix support for rootfstype= when root= is given
- rootfs: Fix support for rootfstype= when root= is given

* Tue Apr 23 2024 Hongchen Zhang <zhanghongchen@loongson.cn> - 6.6.0-21.0.0.24
- add LoongArch support

* Tue Apr 23 2024 Hongchen Zhang <zhanghongchen@loongson.cn> - 6.6.0-21.0.0.23
- exclude cpufreq.h and cpuidle.h from kernel-headers package

* Sat Apr 20 2024 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-21.0.0.22
- !6201 v2  mm: some optimization about hugetlb and thp
- mm: filemap: try to enable THP for exec mapping
- mm/khugepaged: keep mm in mm_slot without MMF_DISABLE_THP check
- mm/khugepaged: bypassing unnecessary scans with MMF_DISABLE_THP check
- mm: mmap: no need to call khugepaged_enter_vma() for stack
- mm: remove VM_EXEC requirement for THP eligibility
- mm: thp_get_unmapped_area must honour topdown preference
- mm: huge_memory: don't force huge page alignment on 32 bit
- mm: mmap: map MAP_STACK to VM_NOHUGEPAGE
- mm: align larger anonymous mappings on THP boundaries
- fs/hugetlbfs/inode.c: mm/memory-failure.c: fix hugetlbfs hwpoison handling
- mm/hugetlb: have CONFIG_HUGETLB_PAGE select CONFIG_XARRAY_MULTI
- mm/filemap: remove hugetlb special casing in filemap.c
- mm/filemap: clarify filemap_fault() comments for not uptodate case
- mm: huge_memory: batch tlb flush when splitting a pte-mapped THP
- !6230  xarray: inline xas_descend to improve performance
- xarray: inline xas_descend to improve performance
- !5891  Fix several compilation warnings for hinic driver
- net/hinic: Fix several compilation warnings with aarch64-openEuler-linux toolchain
- !6244  arm64: enable CONFIG_ARM64_MPAM in openeuler_defconfig
- arm64: enable CONFIG_ARM64_MPAM in openeuler_defconfig
- !6105  fix some issues for arm64 machine check safe
- ACPI: APEI: handle synchronous exceptions in task work to send correct SIGBUS si_code
- mm: memory-failure: move return value documentation to function declaration
- ACPI: APEI: send SIGBUS to current task if synchronous memory error not recovered
- arm64: add machine check safe sysctl interface
- arm64: introduce copy_mc_to_kernel() implementation
- arm64: support copy_mc_[user]_highpage()
- arm64: Get rid of ARM64_HAS_NO_HW_PREFETCH
- mm/hwpoison: return -EFAULT when copy fail in copy_mc_[user]_highpage()
- arm64: add support for ARCH_HAS_COPY_MC
- Revert "arm64: add support for machine check error safe"
- Revert "arm64: add uaccess to machine check safe"
- Revert "mm/hwpoison: return -EFAULT when copy fail in copy_mc_[user]_highpage()"
- Revert "arm64: support copy_mc_[user]_highpage()"
- Revert "arm64: introduce copy_mc_to_kernel() implementation"
- Revert "arm64: add machine check safe sysctl interface"
- Revert "kasan: fix the compilation error for memcpy_mcs()"

* Tue Apr 16 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-20.0.0.21
- !6048 improve 3SNIC 910/920/930 NIC driver
- improve 3SNIC 910/920/930 NIC driver
- !5815 v2  Support NMI in the virtual machine
- KVM: arm64: vgic-v3: Handle traps of ICV_NMIAR1_EL1
- arm64: Decouple KVM from CONFIG_ARM64_NMI
- KVM: arm64: Handle traps of ALLINT
- KVM: arm64: Allow GICv3.3 NMI if the host supports it
- KVM: arm64: vgic-v3: Don't inject an NMI if the vcpu doesn't have FEAT_NMI
- KVM: arm64: Don't trap ALLINT accesses if the vcpu has FEAT_NMI
- KVM: arm64: Allow userspace to control ID_AA64PFR1_EL1.NMI
- KVM: arm64: vgic-debug: Add the NMI field to the debug output
- KVM: arm64: vgic-v3: Add userspace selection for GICv3.3 NMI
- KVM: arm64: vgic-v3: Add support for GIC{D,R}_INMIR registers
- KVM: arm64: vgic-v3: Use the NMI attribute as part of the AP-list sorting
- KVM: arm64: vgic-v4: Propagate the NMI state into the GICv4.1 VSGI configuration
- KVM: arm64: vgic-v3: Make NMI priority RES0
- KVM: arm64: vgic-v3: Allow the NMI state to make it into the LRs
- KVM: arm64: vgic-v3: Upgrade AP1Rn to 64bit.
- !5752 【OLK-6.6】Add Chengdu BeiZhongWangXin Technology N5/N6 Series Network Card Driver
- drivers: add Chengdu BeiZhongWangXin Technology N5/N6 Series Network Card Driver
- !5730 [OLK-6.6] Fix warnings for RNPGBEVF driver
- RNPGBEVF: NET: Fix wanrings
- !5726 [OLK-6.6] Fix warnings for RNPVF driver
- RNPVF: NET: Fix wanrings
- !5854 [OLK-6.6] Make Cluster Scheduling Configurable
- scheduler: Disable cluster scheduling by default
- scheduler: Add boot time enabling/disabling of cluster scheduling
- scheduler: Add runtime knob sysctl_sched_cluster
- scheduler: Create SDTL_SKIP flag to skip topology level
- !6068  mm: batch mm counter updating in filemap_map_pages()
- mm: filemap: batch mm counter updating in filemap_map_pages()
- mm: move mm counter updating out of set_pte_range()
- !5931  irqchip/gicv3-its: Add workaround for hip09 ITS erratum 162100801
- irqchip/gicv3-its: Add workaround for hip09 ITS erratum 162100801
- !5678 v2  KVM: arm64: Translate logic cluster id to physical cluster id when updating lsudvmbm
- KVM: arm64: Translate logic cluster id to physical cluster id when updating lsudvmbm
- !5972 Perf-related bugfix
- docs: perf: Fix build warning of hisi-pcie-pmu.rst
- drivers/perf: hisi_pcie: Merge find_related_event() and get_event_idx()
- drivers/perf: hisi_pcie: Relax the check on related events
- drivers/perf: hisi_pcie: Check the target filter properly
- drivers/perf: hisi_pcie: Add more events for counting TLP bandwidth
- drivers/perf: hisi_pcie: Fix incorrect counting under metric mode
- drivers/perf: hisi_pcie: Introduce hisi_pcie_pmu_get_event_ctrl_val()
- drivers/perf: hisi_pcie: Rename hisi_pcie_pmu_{config,clear}_filter()
- drivers/perf: hisi: Enable HiSilicon Erratum 162700402 quirk for HIP09
- docs: perf: Update usage for target filter of hisi-pcie-pmu
- !6063 RDMA/hns: Some bugfixes and cleanups
- RDMA/hns: Fix long waiting cmd event when reset
- RDMA/hns: Fix the overflow risk of hem_list_calc_ba_range()
- RDMA/hns: Fix simultaneous reset and resource deregistration
- RDMA/hns: Fix cpu stuck by printings during reset
- RDMA/hns: Fix missing capacities in query_device()
- RDMA/hns: Fix missing resetting notify
- RDMA/hns: Remove extra blank line in get_sge_num_from_max_inl_data()
- RDMA/hns: Use complete parentheses in macros
- RDMA/hns: fix iommu_map_sg() failed when MR bigger than 4G
- !6069 RDMA/hns: support roh
- RDMA/hns: Support RDMA_CM in ROH mode
- RDMA/hns: Support for ROH
- RDMA/hns: Add new device ID
- !6008  locking/osq_lock: Avoid false sharing in optimistic_spin_node
- locking/osq_lock: Avoid false sharing in optimistic_spin_node
- !5774  irqdomain: Fix driver re-inserting failures when IRQs not being freed
- irqdomain: Fix driver re-inserting failures when IRQs not being freed
- !5709 【OLK-6.6】configs: arm64: Enable CONFIG_DLM
- configs: arm64: Enable CONFIG_DLM
- !5971 RDMA/hns: Support hns roce DCA mode
- RDMA/hns: Fix DCA's dependence on ib_uverbs
- RDMA/hns: Fixes concurrent ressetting and post_recv in DCA mode
- RDMA/hns: Optimize user DCA perfermance by sharing DCA status
- RDMA/hns: Add debugfs support for DCA
- RDMA/hns: Add DCA support for kernel space
- RDMA/hns: Add method to query WQE buffer's address
- RDMA/hns: Add method to detach WQE buffer
- RDMA/hns: Setup the configuration of WQE addressing to QPC
- RDMA/hns: Add method for attaching WQE buffer
- RDMA/hns: Configure DCA mode for the userspace QP
- RDMA/hns: Add method for shrinking DCA memory pool
- RDMA/hns: Introduce DCA for RC QP

* Fri Apr 12 2024 Jin Lun <jinlun@huawei.com> - 6.6.0-19.0.0.20
- Remove PGP certificates.
- Optimize the signing process, if the project has no permission
  to send sign request, use the kernel native signing.

* Wed Apr 10 2024 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-19.0.0.19
- !5877  optimize eevdf scheduler
- sched/eevdf: Skip eligibility check for current entity during wakeup preemption
- sched/eevdf: O(1) fastpath for task selection
- sched/eevdf: Sort the rbtree by virtual deadline
- !5922  Some fixes and cleanups for SAS
- Revert "scsi: hisi_sas: Disable SATA disk phy for severe I_T nexus reset failure"
- scsi: hisi_sas: Add slave_destroy interface for v3 hw
- scsi: hisi_sas: Modify the deadline for ata_wait_after_reset()
- scsi: libsas: Allocation SMP request is aligned to ARCH_DMA_MINALIGN
- scsi: libsas: Add a helper sas_get_sas_addr_and_dev_type()
- scsi: libsas: Fix disk not being scanned in after being removed
- scsi: hisi_sas: Remove redundant checks for automatic debugfs dump
- scsi: hisi_sas: Check usage count only when the runtime PM status is RPM_SUSPENDING
- scsi: hisi_sas: Handle the NCQ error returned by D2H frame
- scsi: hisi_sas: Remove hisi_hba->timer for v3 hw
- scsi: hisi_sas: Check whether debugfs is enabled before removing or releasing it
- scsi: hisi_sas: Fix a deadlock issue related to automatic dump
- scsi: hisi_sas: Allocate DFX memory during dump trigger
- scsi: hisi_sas: Directly call register snapshot instead of using workqueue
- !5546 support 3snic NIC
- support 3SNIC 910/920/930 NIC
- !5869  KVM: arm64: vgic-its: use vgic_get_irq_kref() before vgic_put_irq()
- KVM: arm64: vgic-its: use vgic_get_irq_kref() before vgic_put_irq()
- !5878 ima:Dont check xattr when loading digest lists
- ima:Dont check xattr when loading digest lists
- !5800  firmware: arm_sdei: Move sdei_cpuhp_up/down() before lockup_detector_online_cpu()
- firmware: arm_sdei: Move sdei_cpuhp_up/down() before lockup_detector_online_cpu()
- !3175 [OLK-6.6] x86/tsc: Make cur->adjusted values in package#1 to be the same
- x86/tsc: Make cur->adjusted values in package#1 to be the same
- !5022 [devel-6.6] perf/x86/zhaoxin/uncore: Add KX-7000 support
- perf/x86/zhaoxin/uncore: Add KX-7000 support
- !5652 [OLK-6.6] i2c: zhaoxin: update support for Zhaoxin I2C controller
- i2c: zhaoxin: update support for Zhaoxin I2C controller
- !4475 [OLK-6.6] Update zhaoxin cputemp driver with using the same MSR uniformly
- Update zhaoxin cputemp driver with using the same MSR uniformly
- !5813 [intel]OLK-tdx-guest-configs-6.6
- Enable Intel TDX guest as kernel module
- !5723 vfio/migration: some bugfix
- hisi_acc_vfio_pci: obtain the mailbox configuration at one time
- vfio/migration: remove unused local variable
- vfio/migration: bugfix cache write-back issue
- vfio/migration: add eq and aeq interruption restore
- vfio/migration: bugfix some driver code
- vfio/migration: added map length page alignment
- !5707 [OLK-6.6] Fix warnings for RNPGBE driver
- RNPGBE: NET: Fix wanrings
- !5659 [OLK-6.6] Fix warnings for RNP driver
- RNP: Fix warnings

* Mon Apr 08 2024 Ren Zhijie <zhijie.ren@shingroup.cn> - 6.6.0-18.0.0.18
- add support for arch ppc64le

* Mon Apr 08 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-18.0.0.17
- !5768  resctrl: fix undefined reference to lockdep_is_cpus_held()
- fs/resctrl: Move rdtgroup_setup_default() out of init.text section
- resctrl: fix undefined reference to lockdep_is_cpus_held()
- !5769  Revert "KVM: arm64: Disable MPAM visibility by default, and handle traps"
- Revert "KVM: arm64: Disable MPAM visibility by default, and handle traps"
- !5744  Backport maple_tree: iterator state changes
- lib/maple_tree.c: fix build error due to hotfix alteration
- maple_tree: mtree_range_walk() clean up
- maple_tree: don't find node end in mtree_lookup_walk()
- maple_tree: use maple state end for write operations
- maple_tree: remove mas_searchable()
- maple_tree: separate ma_state node from status
- maple_tree: clean up inlines for some functions
- maple_tree: use cached node end in mas_destroy()
- maple_tree: use cached node end in mas_next()
- maple_tree: add end of node tracking to the maple state
- maple_tree: move debug check to __mas_set_range()
- maple_tree: make mas_erase() more robust
- maple_tree: remove unnecessary default labels from switch statements
- !5725  ALSA: sh: aica: reorder cleanup operations to avoid UAF bugs
- ALSA: sh: aica: reorder cleanup operations to avoid UAF bugs

* Sun Apr 07 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-17.0.0.16
- !5695 v2  Disable OLK-6.6 configs
- arm64: configs: Disable PROBE_EVENTS_BTF_ARGS
- x86: configs: Disable PROBE_EVENTS_BTF_ARGS
- x86: configs: Disable X86_KERNEL_IBT
- x86: configs: Disable CRASH_HOTPLUG
- !5733  fix port vlan filter not disabled problem in dynamic vlan mode
- net: hns3: fix port vlan filter not disabled problem in dynamic vlan mode
- !5734  arch/mm/fault: accelerate pagefault when badaccess
- x86: mm: accelerate pagefault when badaccess
- arm64: mm: accelerate pagefault when VM_FAULT_BADACCESS
- !5657  Backport slub performance optimization
- mm/slub: remove unused parameter in next_freelist_entry()
- mm/slub: remove full list manipulation for non-debug slab
- mm/slub: directly load freelist from cpu partial slab in the likely case
- slub: Update frozen slabs documentations in the source
- slub: Rename all *unfreeze_partials* functions to *put_partials*
- slub: Optimize deactivate_slab()
- slub: Delay freezing of partial slabs
- slub: Introduce freeze_slab()
- slub: Prepare __slab_free() for unfrozen partial slab out of node partial list
- slub: Keep track of whether slub is on the per-node partial list
- slub: Change get_partial() interfaces to return slab
- slub: Reflow ___slab_alloc()
- !5699  sr9800: Add check for usbnet_get_endpoints
- sr9800: Add check for usbnet_get_endpoints

* Tue Apr 02 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-16.0.0.15
- !5647 hisilicon - some bugfix and cleanup
- crypto: hisilicon/sec2: fix memory use-after-free issue
- crypto: hisilicon/qm - hardware error does not reset during binding/unbinding
- crypto: hisilicon/qm - check device status before sending mailbox
- crypto: hisilicon/qm - mask error bit before flr
- crypto: hisilicon/qm - fix the pf2vf timeout when global reset
- crypto: hisilicon/qm - obtain the mailbox configuration at one time
- crypto: hisilicon/hpre - mask cluster timeout error
- crypto: hisilicon/qm - disable same error report before resetting
- crypto: hisilicon/qm - modify interrupt processing resource application
- crypto: hisilicon/qm - reset device before enabling it
- openeuler_defconfig: enable HISI_ACC_VFIO_PCI=m
- Revert "openeuler_defconfig: enable HISI_ACC_VFIO_PCI=m"
- !5509  ext4: Validate inode pa before using preallocation blocks
- ext4: Validate inode pa before using preallocation blocks
- !5630 scsi: sd: try more retries of START_STOP when resuming scsi device
- scsi: sd: try more retries of START_STOP when resuming scsi device
- !5561 roh: backport roh driver feature support
- roh/hns3: Fix the processing flow of ROH CMDq during the reset process.
- roh/core: Synchronously update the mac address of the vlan device when configuring the vlan device ip
- roh/hns3: Fix ROH multi-BD cmdq issue
- roh/hns3: Add support for roh dfx(debugfs)
- roh/hns3: Add support for roh reset
- roh/core: Add support for inetaddr notifier in roh/core
- roh/hns3: Add support for roh abnormal interruption
- roh/core: Add roh device sysfs node
- roh/hns3: Add ROH cmdq interface support
- roh/hns3: Add ROH hns3 driver and register a ROH device
- roh/core: Add ROH device driver
- net: hns3: add support for ROH reset
- net: hns3: intercept invalid MAC address setting in ROH
- !5703  openeuler_defconfig: Disable CONFIG_PREEMPT_DYNAMIC for x86
- openeuler_defconfig: Disable CONFIG_PREEMPT_DYNAMIC for x86
- !5513 [OLK-6.6] SCSI: SSSRAID: Support 3SNIC 3S5XX serial RAID/HBA controllers
- SCSI: SSSRAID: Support 3SNIC 3S5XX serial RAID/HBA controllers
- !5582 [OLK-6.6]Open CONFIG_LZ4_COMPRESS option for x86_64 architecture
- Open CONFIG_LZ4_COMPRESS option for x86_64 architecture
- !5688 v3  Optimize compaction
- mm/compaction: optimize >0 order folio compaction with free page split.
- mm/compaction: add support for >0 order folio memory compaction.
- mm/compaction: enable compacting >0 order folios.
- mm/page_alloc: remove unused fpi_flags in free_pages_prepare()
- mm/compaction: introduce NR_PAGE_ORDERS and MAX_PAGE_ORDER
- mm: compaction: limit the suitable target page order to be less than cc->order
- mm: compaction: update the cc->nr_migratepages when allocating or freeing the freepages
- mm: compaction: avoid fast_isolate_freepages blindly choose improper pageblock
- mm: add page_rmappable_folio() wrapper
- mm: page_alloc: check the order of compound page even when the order is zero
- mm/compaction: factor out code to test if we should run compaction for target order
- mm/compaction: improve comment of is_via_compact_memory
- mm/compaction: remove repeat compact_blockskip_flush check in reset_isolation_suitable
- mm/compaction: correctly return failure with bogus compound_order in strict mode
- mm/compaction: call list_is_{first}/{last} more intuitively in move_freelist_{head}/{tail}
- mm/compaction: use correct list in move_freelist_{head}/{tail}
- !5655 add steal time software breakpoint pv ipi  support for loongarch kvm
- LoongArch: Add steal time support in guest side
- LoongArch: KVM: Add steal time support in kvm side
- irqchip/loongson-eiointc: Add virt extension support
- LoongArch: KVM: Add software breakpoint support
- Documentation: KVM: Add hypercall for LoongArch
- LoongArch: Add pv ipi support on guest kernel side
- LoongArch: KVM: Add pv ipi support on kvm side
- LoongArch: KVM: Add vcpu search support from physical cpuid
- LoongArch: KVM: Add cpucfg area for kvm hypervisor
- LoongArch: KVM: Add hypercall instruction emulation support
- LoongArch/smp: Refine some ipi functions on LoongArch platform
- !5653  arm64: Enable hardware NMI for perf events NMI
- arm64: Enable hardware NMI for perf events NMI
- !5667  configs: arm64: Enable CONFIG_ACPI_AGDI and CONFIG_ACPI_FFH
- configs: arm64: Enable CONFIG_ACPI_AGDI and CONFIG_ACPI_FFH
- !5669  disable CONFIG_CMDLINE_FROM_BOOTLOADER CONFIG_INITRAMFS_PRESERVE_MTIME in 6.6
- configs: disable CONFIG_CMDLINE_FROM_BOOTLOADER CONFIG_INITRAMFS_PRESERVE_MTIME in 6.6
- !5663  arm64: transparent contiguous PTEs for user mappings
- arm64: configs: enable ARM64_CONTPTE
- tools/mm: add thpmaps script to dump THP usage info
- mm: make folio_pte_batch available outside of mm/memory.c
- arm64/mm: automatically fold contpte mappings
- arm64/mm: __always_inline to improve fork() perf
- arm64/mm: implement pte_batch_hint()
- mm: add pte_batch_hint() to reduce scanning in folio_pte_batch()
- arm64/mm: implement new [get_and_]clear_full_ptes() batch APIs
- arm64/mm: implement new wrprotect_ptes() batch API
- arm64/mm: wire up PTE_CONT for user mappings
- arm64/mm: dplit __flush_tlb_range() to elide trailing DSB
- arm64/mm: new ptep layer to manage contig bit
- arm64/mm: convert ptep_clear() to ptep_get_and_clear()
- arm64/mm: convert set_pte_at() to set_ptes(..., 1)
- arm64/mm: convert READ_ONCE(*ptep) to ptep_get(ptep)
- mm: tidy up pte_next_pfn() definition
- x86/mm: convert pte_next_pfn() to pte_advance_pfn()
- arm64/mm: convert pte_next_pfn() to pte_advance_pfn()
- mm: introduce pte_advance_pfn() and use for pte_next_pfn()
- mm: thp: batch-collapse PMD with set_ptes()
- mm: clarify the spec for set_ptes()
- mm: memory: move mem_cgroup_charge() into alloc_anon_folio()
- mm: memory: use folio_prealloc() in wp_page_copy()
- mm: memory: use a folio in do_cow_fault()
- mm: memory: rename page_copy_prealloc() to folio_prealloc()
- !5662 v4  Introduce dynamic pool feature part 2
- mm/dynamic_pool: Wrap some core functions with dpool prefix
- mm/dynamic_pool: disable irq for dynamic_pool lock
- mm/dynamic_pool: don't set subpool for page from dynamic pool
- mm/dynamic_pool: skip unexpected migration
- mm/mem_reliable: Fallback to dpool if reliable memory is not enough
- mm/mem_reliable: Treat page from dhugetlb pool as unreliable page
- mm/dynamic_pool: Stop alloc reliable page from dynamic pool
- !5621  irqchip/gic-v3: Fix a system stall when using pseudo NMI with CONFIG_ARM64_NMI closed
- irqchip/gic-v3: Fix a system stall when using pseudo NMI with CONFIG_ARM64_NMI closed
- !5656 v3  mm: backport fork/unmap/zap optimize
- mm/memory: fix missing pte marker for !page on pte zaps
- mm/memory: optimize unmap/zap with PTE-mapped THP
- mm/mmu_gather: improve cond_resched() handling with large folios and expensive page freeing
- mm/mmu_gather: add __tlb_remove_folio_pages()
- mm/mmu_gather: add tlb_remove_tlb_entries()
- mm/mmu_gather: define ENCODED_PAGE_FLAG_DELAY_RMAP
- mm/mmu_gather: pass "delay_rmap" instead of encoded page to __tlb_remove_page_size()
- mm/memory: factor out zapping folio pte into zap_present_folio_pte()
- mm/memory: further separate anon and pagecache folio handling in zap_present_pte()
- mm/memory: handle !page case in zap_present_pte() separately
- mm/memory: factor out zapping of present pte into zap_present_pte()
- mm/memory: ignore writable bit in folio_pte_batch()
- mm/memory: ignore dirty/accessed/soft-dirty bits in folio_pte_batch()
- mm/memory: optimize fork() with PTE-mapped THP
- mm/memory: pass PTE to copy_present_pte()
- mm/memory: factor out copying the actual PTE in copy_present_pte()
- powerpc/mm: use pte_next_pfn() in set_ptes()
- arm/mm: use pte_next_pfn() in set_ptes()
- mm/pgtable: make pte_next_pfn() independent of set_ptes()
- sparc/pgtable: define PFN_PTE_SHIFT
- s390/pgtable: define PFN_PTE_SHIFT
- riscv/pgtable: define PFN_PTE_SHIFT
- powerpc/pgtable: define PFN_PTE_SHIFT
- nios2/pgtable: define PFN_PTE_SHIFT
- arm/pgtable: define PFN_PTE_SHIFT
- arm64/mm: make set_ptes() robust when OAs cross 48-bit boundary
- arm64: Mark the 'addr' argument to set_ptes() and __set_pte_at() as unused
- arm64/mm: Hoist synchronization out of set_ptes() loop
- mm: convert mm_counter_file() to take a folio
- mm: convert mm_counter() to take a folio
- mm: convert to should_zap_page() to should_zap_folio()
- mm: use pfn_swap_entry_folio() in copy_nonpresent_pte()
- mm: use pfn_swap_entry_to_folio() in zap_huge_pmd()
- mm: use pfn_swap_entry_folio() in __split_huge_pmd_locked()
- s390: use pfn_swap_entry_folio() in ptep_zap_swap_entry()
- mprotect: use pfn_swap_entry_folio
- mm: add pfn_swap_entry_folio()

* Tue Apr 2 2024 Jin Lun <jinlun@huawei.com> - 6.6.0-15.0.0.14
- Support generating moudle/kernel signature with openEuler signature platform

* Sat Mar 30 2024 Liu Jian <liujian56@huawei.com> - 6.6.0-15.0.0.13
- And net-acc tool to kernel-tools.

* Fri Mar 29 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-15.0.0.12
- !5470 [OLK-6.6] Add support for Mucse Virtual Function Network Adapter(N500/n210)
- drivers: initial support for rnpgbevf drivers from Mucse Technology
- !3164 [OLK-6.6] Fix CRC32C instruction low performance issue
- crypto: x86/crc32c-intel - Don't match some Zhaoxin CPUs
- !5547 Synchronizing upstream patch
- LoongArch: KVM: Set reserved bits as zero in CPUCFG
- LoongArch: KVM: Do not restart SW timer when it is expired
- LoongArch: KVM: Start SW timer only when vcpu is blocking
- irqchip/loongson-eiointc: Remove explicit interrupt affinity restore on resume
- irqchip/loongson-eiointc: Skip handling if there is no pending irq
- !3182 [OLK-6.6] Add support for Zhaoxin GMI SM2 Secure Hash algorithm
- configs: add CONFIG_CRYPTO_SM2_ZHAOXIN_GMI to m
- Add support for Zhaoxin GMI SM2 Secure Hash algorithm
- !5578  SCSI: hisi_raid: support SPxxx serial RAID/HBA controllers
- SCSI: hisi_raid: support SPxxx serial RAID/HBA controllers
- !5641  userfaultfd: early return in dup_userfaultfd()
- userfaultfd: early return in dup_userfaultfd()
- !5629 v3  Mitigate a vmap lock contention
- mm: vmalloc: refactor vmalloc_dump_obj() function
- mm: vmalloc: improve description of vmap node layer
- mm: vmalloc: add a shrinker to drain vmap pools
- mm: vmalloc: set nr_nodes based on CPUs in a system
- mm: vmalloc: support multiple nodes in vmallocinfo
- mm: vmalloc: support multiple nodes in vread_iter
- mm: vmalloc: add a scan area of VA only once
- mm: vmalloc: offload free_vmap_area_lock lock
- mm: vmalloc: remove global purge_vmap_area_root rb-tree
- mm/vmalloc: remove vmap_area_list
- mm: vmalloc: remove global vmap_area_root rb-tree
- mm: vmalloc: move vmap_init_free_space() down in vmalloc.c
- mm: vmalloc: rename adjust_va_to_fit_type() function
- mm: vmalloc: add va_alloc() helper
- mm: Introduce vmap_page_range() to map pages in PCI address space
- mm: Introduce VM_SPARSE kind and vm_area_[un]map_pages().
- mm: Enforce VM_IOREMAP flag and range in ioremap_page_range.
- mm/vmalloc: fix the unchecked dereference warning in vread_iter()
- !5609  Adding Huawei BMA driver
- configs: add config BMA to config files
- Huawei BMA: Adding Huawei BMA driver: cdev_veth_drv
- Huawei BMA: Adding Huawei BMA driver: host_kbox_drv
- Huawei BMA: Adding Huawei BMA driver: host_veth_drv
- Huawei BMA: Adding Huawei BMA driver: host_cdev_drv
- Huawei BMA: Adding Huawei BMA driver: host_edma_drv
- !5613  mm: backport rmap interface overhaul
- mm/memory: fix folio_set_dirty() vs. folio_mark_dirty() in zap_pte_range()
- mm/huge_memory: fix folio_set_dirty() vs. folio_mark_dirty()
- mm/rmap: silence VM_WARN_ON_FOLIO() in __folio_rmap_sanity_checks()
- mm: remove one last reference to page_add_*_rmap()
- mm/rmap: rename COMPOUND_MAPPED to ENTIRELY_MAPPED
- mm: convert page_try_share_anon_rmap() to folio_try_share_anon_rmap_[pte|pmd]()
- mm/rmap: remove page_try_dup_anon_rmap()
- mm/memory: page_try_dup_anon_rmap() -> folio_try_dup_anon_rmap_pte()
- mm/huge_memory: page_try_dup_anon_rmap() -> folio_try_dup_anon_rmap_pmd()
- mm/rmap: introduce folio_try_dup_anon_rmap_[pte|ptes|pmd]()
- mm/rmap: convert page_dup_file_rmap() to folio_dup_file_rmap_[pte|ptes|pmd]()
- mm/rmap: remove page_remove_rmap()
- Documentation: stop referring to page_remove_rmap()
- mm: userswap: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/rmap: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/migrate_device: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/memory: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/ksm: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/khugepaged: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/huge_memory: page_remove_rmap() -> folio_remove_rmap_pmd()
- kernel/events/uprobes: page_remove_rmap() -> folio_remove_rmap_pte()
- mm/rmap: introduce folio_remove_rmap_[pte|ptes|pmd]()
- mm/rmap: remove RMAP_COMPOUND
- mm/rmap: remove page_add_anon_rmap()
- mm/memory: page_add_anon_rmap() -> folio_add_anon_rmap_pte()
- mm/swapfile: page_add_anon_rmap() -> folio_add_anon_rmap_pte()
- mm/ksm: page_add_anon_rmap() -> folio_add_anon_rmap_pte()
- mm/migrate: page_add_anon_rmap() -> folio_add_anon_rmap_pte()
- mm/huge_memory: page_add_anon_rmap() -> folio_add_anon_rmap_pmd()
- mm/huge_memory: batch rmap operations in __split_huge_pmd_locked()
- mm/rmap: introduce folio_add_anon_rmap_[pte|ptes|pmd]()
- mm/rmap: factor out adding folio mappings into __folio_add_rmap()
- mm/rmap: remove page_add_file_rmap()
- mm/userfaultfd: page_add_file_rmap() -> folio_add_file_rmap_pte()
- mm/migrate: page_add_file_rmap() -> folio_add_file_rmap_pte()
- mm/huge_memory: page_add_file_rmap() -> folio_add_file_rmap_pmd()
- mm/memory: page_add_file_rmap() -> folio_add_file_rmap_[pte|pmd]()
- mm/rmap: convert folio_add_file_rmap_range() into folio_add_file_rmap_[pte|ptes|pmd]()
- mm/rmap: add hugetlb sanity checks for anon rmap handling
- mm/rmap: introduce and use hugetlb_try_share_anon_rmap()
- mm/rmap: introduce and use hugetlb_try_dup_anon_rmap()
- mm/rmap: introduce and use hugetlb_add_file_rmap()
- mm/rmap: introduce and use hugetlb_remove_rmap()
- mm/rmap: rename hugepage_add* to hugetlb_add*
- mm/khugepaged: convert collapse_pte_mapped_thp() to use folios
- mm/khugepaged: convert alloc_charge_hpage() to use folios
- mm/khugepaged: convert is_refcount_suitable() to use folios
- mm/khugepaged: convert hpage_collapse_scan_pmd() to use folios
- mm/khugepaged: convert __collapse_huge_page_isolate() to use folios
- !5543 v2  locking/qspinlock: Add CNA support for ARM64
- config/arm64: Enable numa aware qspinlock by default
- locking/qspinlock: Add CNA support for ARM64 without pvspinlock
- !5555 v2  ACPI/arm64: add support for virtual cpu hotplug
- arm64/psci: Add undefined error message printing for psci_x_cpu_on
- cpumask: Add enabled cpumask for present CPUs that can be brought online
- ACPI: Add _OSC bits to advertise OS support for toggling CPU present/enabled
- arm64: document virtual CPU hotplug's expectations
- ACPI: processor: Only call arch_unregister_cpu() if HOTPLUG_CPU is selected
- ACPI: add support to register CPUs based on the _STA enabled bit
- arm64: psci: Ignore DENIED CPUs
- irqchip/gic-v3: Add support for ACPI's disabled but 'online capable' CPUs
- irqchip/gic-v3: Don't return errors from gic_acpi_match_gicc()
- ACPICA: Add new MADT GICC flags fields
- arm64: acpi: Move get_cpu_for_acpi_id() to a header
- ACPI: Warn when the present bit changes but the feature is not enabled
- ACPI: Check _STA present bit before making CPUs not present
- ACPI: convert acpi_processor_post_eject() to use IS_ENABLED()
- ACPI: Add post_eject to struct acpi_scan_handler for cpu hotplug
- ACPI: Rename acpi_processor_hotadd_init and remove pre-processor guards
- ACPI: Move acpi_bus_trim_one() before acpi_scan_hot_remove()
- ACPI: Rename ACPI_HOTPLUG_CPU to include 'present'
- ACPI: processor: Register all CPUs from acpi_processor_get_info()
- ACPI: processor: Register CPUs that are online, but not described in the DSDT
- ACPI: processor: Add support for processors described as container packages
- ACPI: Only enumerate enabled (or functional) devices
- !5461 [OLK-6.6] Add support for Mucse Virtual Function Network Adapter(N10)
- drivers: initial support for rnpvf drivers from Mucse Technology
- !5526 Intel: Backport QuickAssist Technology(QAT) in-tree driver
- Enable Intel QAT_4XXX as kernel module
- crypto: qat - make ring to service map common for QAT GEN4
- crypto: qat - fix ring to service map for dcc in 420xx
- crypto: qat - fix ring to service map for dcc in 4xxx
- crypto: qat - fix comment structure
- crypto: qat - remove unnecessary description from comment
- crypto: qat - remove double initialization of value
- crypto: qat - avoid division by zero
- crypto: qat - removed unused macro in adf_cnv_dbgfs.c
- crypto: qat - remove unused macros in qat_comp_alg.c
- crypto: qat - uninitialized variable in adf_hb_error_inject_write()
- Documentation: qat: fix auto_reset section
- crypto: qat - resolve race condition during AER recovery
- crypto: qat - change SLAs cleanup flow at shutdown
- crypto: qat - improve aer error reset handling
- crypto: qat - limit heartbeat notifications
- crypto: qat - add auto reset on error
- crypto: qat - add fatal error notification
- crypto: qat - re-enable sriov after pf reset
- crypto: qat - update PFVF protocol for recovery
- crypto: qat - disable arbitration before reset
- crypto: qat - add fatal error notify method
- crypto: qat - add heartbeat error simulator
- crypto: qat - use kcalloc_node() instead of kzalloc_node()
- crypto: qat - avoid memcpy() overflow warning
- crypto: qat - fix arbiter mapping generation algorithm for QAT 402xx
- crypto: qat - generate dynamically arbiter mappings
- crypto: qat - add support for ring pair level telemetry
- crypto: qat - add support for device telemetry
- crypto: qat - add admin msgs for telemetry
- crypto: qat - include pci.h for GET_DEV()
- crypto: qat - add support for 420xx devices
- crypto: qat - move fw config related structures
- crypto: qat - relocate portions of qat_4xxx code
- crypto: qat - change signature of uof_get_num_objs()
- crypto: qat - relocate and rename get_service_enabled()
- crypto: qat - add NULL pointer check
- crypto: qat - fix mutex ordering in adf_rl
- crypto: qat - fix error path in add_update_sla()
- crypto: qat - add sysfs_added flag for rate limiting
- crypto: qat - add sysfs_added flag for ras
- crypto: qat - prevent underflow in rp2srv_store()
- units: add missing header
- seq_file: add helper macro to define attribute for rw file
- crypto: qat - move adf_cfg_services
- crypto: qat - add num_rps sysfs attribute
- crypto: qat - add rp2svc sysfs attribute
- crypto: qat - add rate limiting sysfs interface
- crypto: qat - add rate limiting feature to qat_4xxx
- crypto: qat - add retrieval of fw capabilities
- crypto: qat - add bits.h to icp_qat_hw.h
- units: Add BYTES_PER_*BIT
- crypto: qat - move admin api
- crypto: qat - count QAT GEN4 errors
- crypto: qat - add error counters
- crypto: qat - add handling of errors from ERRSOU3 for QAT GEN4
- crypto: qat - add adf_get_aram_base() helper function
- crypto: qat - add handling of compression related errors for QAT GEN4
- crypto: qat - add handling of errors from ERRSOU2 for QAT GEN4
- crypto: qat - add reporting of errors from ERRSOU1 for QAT GEN4
- crypto: qat - add reporting of correctable errors for QAT GEN4
- crypto: qat - add infrastructure for error reporting
- crypto: qat - add cnv_errors debugfs file
- crypto: qat - add pm_status debugfs file
- crypto: qat - refactor included headers
- crypto: qat - add namespace to driver
- crypto: qat - Remove zlib-deflate
- crypto: qat - Annotate struct adf_fw_counters with __counted_by
- crypto: qat - do not shadow error code
- crypto: qat - refactor deprecated strncpy
- crypto: qat - Use list_for_each_entry() helper
- Documentation: ABI: debugfs-driver-qat: fix fw_counters path

* Thu Mar 28 2024 Bing Xia <xiabing12@h-partners.com> - 6.6.0-14.0.0.11
- perf: add CoreSight trace component support on aarch64 platform

* Wed Mar 27 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-14.0.0.10
- !5524 [OLK-6.6] fix 0day bugs reported by CI robot for Mont-TSSE
- fix 0 day bugs for Mont-TSSE Driver
- !5284 [OLK-6.6] fs/address_space: move i_mmap_rwsem to mitigate a false sharing with i_mmap.
- fs/address_space: move i_mmap_rwsem to mitigate a false sharing with i_mmap.
- !5280  Add Huawei Intelligent Network Card Driver: hinic3
- net/hinic3: add huawei/hinic3 driver
- !5179  Update Huawei Intelligent Network Card Driver: hinic
- net/hinic: Update Huawei Intelligent Network Card Driver: hinic
- !5523 enable openeuler_defconfig HISI_ACC_VFIO_PCI=m
- openeuler_defconfig: enable HISI_ACC_VFIO_PCI=m
- !5529 arch/powerpc: open BTF relevant configs in openuler defconfig
- arch/powerpc: open BTF relevant configs in openuler defconfig
- !5541 RDMA/hns: Backport bugfixes
- RDMA/hns: Refactor hns_roce_alloc_ucontext()
- RDMA/hns: Fix missing reset notification by user space driver
- RDMA/hns: Kernel notify usr space to stop ring db
- RDMA/hns: Support flexible wqe buffer page size
- !5464 net: hns3: backport some driver feature enhancement
- net: hns3: default select PAGE_POOL_STATS
- net: hns3: support set/get VxLAN rule of rx flow director by ethtool
- net: ethtool: add VxLAN to the NFC API
- net: hns3: add support for ROH ras
- net: hns3: fix bug for init roh client instance
- net: hns3: HNAE3 framework add support for ROH client
- net: hns3: add support handling tx dhcp packets for ROH
- net: hns3: support arp proxy
- net: hns3: add arp proxy switch in ethtool
- net: hns3: support tc limit rate
- net: hns3: support tc command with max rate parameter
- net: hns3: add ROH MAC type definitions and support query MAC type
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
- !5426 BTC's bugfix  for openeuler OLK-6.6
- ipmi: Add erratum 162102203 config to enable workaround for SMS message processing timeout
- ipmi: Errata workaround to prevent SMS message processing timeout
- !5049 [OLK-6.6]Add pcie acs and no-bus-reset quirk for mucse Nics
- Add pcie acs and no-bus-reset quirk for mucse Nics
- !5354  iommu/arm-smmu-v3: Disable ECMDQ before reset
- iommu/arm-smmu-v3: Disable ECMDQ before reset
- !5061 [OLK-6.6] riscv: Update openeuler_defconfig to support sg2042 SoC
- riscv: Update openeuler_defconfig to support sg2042 SoC
- !5427 crypto/trng: Remove the automatic loading of the hisi_trng driver
- crypto/trng: Remove the automatic loading of the hisi_trng driver
- crypto: hisilicon/trng - use %u to print u32 variables
- !5492  Backport Introduce __mt_dup() to improve the performance of fork()
- fork: use __mt_dup() to duplicate maple tree in dup_mmap()
- maple_tree: preserve the tree attributes when destroying maple tree
- maple_tree: update check_forking() and bench_forking()
- maple_tree: skip other tests when BENCH is enabled
- maple_tree: update the documentation of maple tree
- maple_tree: add test for mtree_dup()
- radix tree test suite: align kmem_cache_alloc_bulk() with kernel behavior.
- maple_tree: introduce interfaces __mt_dup() and mtree_dup()
- maple_tree: introduce {mtree,mas}_lock_nested()
- maple_tree: add mt_free_one() and mt_attr() helpers
- radix tree test suite: fix allocation calculation in kmem_cache_alloc_bulk()
- !5334 v4  iommu/iova: avoid softlockup in fq_flush_timeout
- iommu/iova: avoid softlockup in fq_flush_timeout
- !5412 [OLK-6.6] perf/x86/amd: Miscellaneous fixes
- perf vendor events amd: Fix Zen 4 cache latency events
- perf/x86/amd/lbr: Discard erroneous branch entries
- perf/x86/amd/core: Avoid register reset when CPU is dead
- !5376  Bluetooth: rfcomm: Fix null-ptr-deref in rfcomm_check_security
- Bluetooth: rfcomm: Fix null-ptr-deref in rfcomm_check_security

* Fri Mar 22 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-13.0.0.9
- !5424  block: Fix iterating over an empty bio with bio_for_each_folio_all
- block: Fix iterating over an empty bio with bio_for_each_folio_all
- !5425  nbd: always initialize struct msghdr completely
- nbd: always initialize struct msghdr completely
- !5255  CVE-2024-26627
- scsi: core: Move scsi_host_busy() out of host lock if it is for per-command
- scsi: core: Move scsi_host_busy() out of host lock for waking up EH handler
- !5221  powerpc/mm: Fix null-pointer dereference in pgtable_cache_add
- powerpc/mm: Fix null-pointer dereference in pgtable_cache_add
- !5045 [OLK-6.6] Add support for Mont-TSSE firmware update and fix 0day bugs
- add firmware update function for Mont-TSSE
- fix 0day bugs for Mont-TSSE in CI test
- !5363 [OLK-6.6] ima: Support modsig verify using trusted keys
- ima: Enable modsig appraisal by default
- ima: Support modsig verify using trusted keys
- !5369 Backport 6.6.9-6.6.22 LTS
- KVM/x86: Export RFDS_NO and RFDS_CLEAR to guests
- x86/rfds: Mitigate Register File Data Sampling (RFDS)
- Documentation/hw-vuln: Add documentation for RFDS
- x86/mmio: Disable KVM mitigation when X86_FEATURE_CLEAR_CPU_BUF is set
- selftests: mptcp: decrease BW in simult flows
- readahead: avoid multiple marked readahead pages
- KVM: s390: vsie: fix race during shadow creation
- KVM: s390: add stat counter for shadow gmap events
- net: pds_core: Fix possible double free in error handling path
- netrom: Fix data-races around sysctl_net_busy_read
- netrom: Fix a data-race around sysctl_netrom_link_fails_count
- netrom: Fix a data-race around sysctl_netrom_routing_control
- netrom: Fix a data-race around sysctl_netrom_transport_no_activity_timeout
- netrom: Fix a data-race around sysctl_netrom_transport_requested_window_size
- netrom: Fix a data-race around sysctl_netrom_transport_busy_delay
- netrom: Fix a data-race around sysctl_netrom_transport_acknowledge_delay
- netrom: Fix a data-race around sysctl_netrom_transport_maximum_tries
- netrom: Fix a data-race around sysctl_netrom_transport_timeout
- netrom: Fix data-races around sysctl_netrom_network_ttl_initialiser
- netrom: Fix a data-race around sysctl_netrom_obsolescence_count_initialiser
- netrom: Fix a data-race around sysctl_netrom_default_path_quality
- erofs: apply proper VMA alignment for memory mapped files on THP
- netfilter: nf_conntrack_h323: Add protection for bmp length out of range
- netfilter: nft_ct: fix l3num expectations with inet pseudo family
- net/rds: fix WARNING in rds_conn_connect_if_down
- net: dsa: microchip: fix register write order in ksz8_ind_write8()
- cpumap: Zero-initialise xdp_rxq_info struct before running XDP program
- selftests/bpf: Fix up xdp bonding test wrt feature flags
- xdp, bonding: Fix feature flags when there are no slave devs anymore
- bpf: check bpf_func_state->callback_depth when pruning states
- net/ipv6: avoid possible UAF in ip6_route_mpath_notify()
- igc: avoid returning frame twice in XDP_REDIRECT
- net: ice: Fix potential NULL pointer dereference in ice_bridge_setlink()
- ice: virtchnl: stop pretending to support RSS over AQ or registers
- net: sparx5: Fix use after free inside sparx5_del_mact_entry
- geneve: make sure to pull inner header in geneve_rx()
- tracing/net_sched: Fix tracepoints that save qdisc_dev() as a string
- net/mlx5e: Switch to using _bh variant of of spinlock API in port timestamping NAPI poll context
- net/mlx5e: Use a memory barrier to enforce PTP WQ xmit submission tracking occurs after populating the metadata_map
- net/mlx5e: Fix MACsec state loss upon state update in offload path
- net/mlx5e: Change the warning when ignore_flow_level is not supported
- net/mlx5: Check capability for fw_reset
- net/mlx5: E-switch, Change flow rule destination checking
- Revert "net/mlx5e: Check the number of elements before walk TC rhashtable"
- Revert "net/mlx5: Block entering switchdev mode with ns inconsistency"
- ice: reorder disabling IRQ and NAPI in ice_qp_dis
- i40e: disable NAPI right after disabling irqs when handling xsk_pool
- ixgbe: {dis, en}able irqs in ixgbe_txrx_ring_{dis, en}able
- net: lan78xx: fix runtime PM count underflow on link stop
- xfrm: Pass UDP encapsulation in TX packet offload
- mm/vmscan: fix a bug calling wakeup_kswapd() with a wrong zone index
- ceph: switch to corrected encoding of max_xattr_size in mdsmap
- dmaengine: fsl-edma: correct max_segment_size setting
- dmaengine: fsl-edma: utilize common dt-binding header file
- dt-bindings: dma: fsl-edma: Add fsl-edma.h to prevent hardcoding in dts
- drm/nouveau: don't fini scheduler before entity flush
- selftests: mptcp: rm subflow with v4/v4mapped addr
- selftests: mptcp: add mptcp_lib_is_v6
- selftests: mptcp: update userspace pm test helpers
- selftests: mptcp: add chk_subflows_total helper
- selftests: mptcp: add evts_get_info helper
- KVM/VMX: Move VERW closer to VMentry for MDS mitigation
- KVM/VMX: Use BT+JNC, i.e. EFLAGS.CF to select VMRESUME vs. VMLAUNCH
- x86/bugs: Use ALTERNATIVE() instead of mds_user_clear static key
- x86/entry_32: Add VERW just before userspace transition
- x86/entry_64: Add VERW just before userspace transition
- block: define bvec_iter as __packed __aligned(4)
- gpio: fix resource unwinding order in error path
- gpiolib: Fix the error path order in gpiochip_add_data_with_key()
- gpio: 74x164: Enable output pins after registers are reset
- powerpc/rtas: use correct function name for resetting TCE tables
- powerpc/pseries/iommu: IOMMU table is not initialized for kdump over SR-IOV
- dmaengine: idxd: Ensure safe user copy of completion record
- dmaengine: idxd: Remove shadow Event Log head stored in idxd
- phy: freescale: phy-fsl-imx8-mipi-dphy: Fix alias name to use dashes
- dmaengine: dw-edma: eDMA: Add sync read before starting the DMA transfer in remote setup
- dmaengine: dw-edma: HDMA: Add sync read before starting the DMA transfer in remote setup
- dmaengine: dw-edma: Add HDMA remote interrupt configuration
- dmaengine: dw-edma: HDMA_V0_REMOTEL_STOP_INT_EN typo fix
- dmaengine: dw-edma: Fix wrong interrupt bit set for HDMA
- dmaengine: dw-edma: Fix the ch_count hdma callback
- ASoC: cs35l56: fix reversed if statement in cs35l56_dspwait_asp1tx_put()
- af_unix: Drop oob_skb ref before purging queue in GC.
- af_unix: Fix task hung while purging oob_skb in GC.
- NFS: Fix data corruption caused by congestion.
- mptcp: fix possible deadlock in subflow diag
- mptcp: fix double-free on socket dismantle
- mptcp: fix potential wake-up event loss
- mptcp: fix snd_wnd initialization for passive socket
- selftests: mptcp: join: add ss mptcp support check
- mptcp: push at DSS boundaries
- mptcp: avoid printing warning once on client side
- mptcp: map v4 address to v6 when destroying subflow
- x86/cpu/intel: Detect TME keyid bits before setting MTRR mask registers
- x86/e820: Don't reserve SETUP_RNG_SEED in e820
- mm/debug_vm_pgtable: fix BUG_ON with pud advanced test
- pmdomain: qcom: rpmhpd: Fix enabled_corner aggregation
- efivarfs: Request at most 512 bytes for variable names
- kbuild: Add -Wa,--fatal-warnings to as-instr invocation
- riscv: add CALLER_ADDRx support
- RISC-V: Drop invalid test from CONFIG_AS_HAS_OPTION_ARCH
- mmc: sdhci-xenon: fix PHY init clock stability
- mmc: sdhci-xenon: add timeout for PHY init complete
- mmc: core: Fix eMMC initialization with 1-bit bus connection
- mmc: mmci: stm32: fix DMA API overlapping mappings warning
- dmaengine: fsl-qdma: init irq after reg initialization
- dmaengine: fsl-edma: correct calculation of 'nbytes' in multi-fifo scenario
- dmaengine: ptdma: use consistent DMA masks
- crypto: arm64/neonbs - fix out-of-bounds access on short input
- dmaengine: fsl-qdma: fix SoC may hang on 16 byte unaligned read
- soc: qcom: pmic_glink: Fix boot when QRTR=m
- drm/amd/display: Add monitor patch for specific eDP
- drm/buddy: fix range bias
- Revert "drm/amd/pm: resolve reboot exception for si oland"
- btrfs: send: don't issue unnecessary zero writes for trailing hole
- btrfs: dev-replace: properly validate device names
- btrfs: fix double free of anonymous device after snapshot creation failure
- wifi: nl80211: reject iftype change with mesh ID change
- mtd: rawnand: marvell: fix layouts
- gtp: fix use-after-free and null-ptr-deref in gtp_newlink()
- landlock: Fix asymmetric private inodes referring
- Bluetooth: hci_bcm4377: do not mark valid bd_addr as invalid
- ALSA: hda/realtek: Add special fixup for Lenovo 14IRP8
- ALSA: hda/realtek: fix mute/micmute LED For HP mt440
- ALSA: hda/realtek: Enable Mute LED on HP 840 G8 (MB 8AB8)
- ALSA: hda/realtek: tas2781: enable subwoofer volume control
- ALSA: ump: Fix the discard error code from snd_ump_legacy_open()
- ALSA: firewire-lib: fix to check cycle continuity
- tomoyo: fix UAF write bug in tomoyo_write_control()
- of: property: fw_devlink: Fix stupid bug in remote-endpoint parsing
- btrfs: fix race between ordered extent completion and fiemap
- riscv: Sparse-Memory/vmemmap out-of-bounds fix
- riscv: Fix pte_leaf_size() for NAPOT
- Revert "riscv: mm: support Svnapot in huge vmap"
- drivers: perf: ctr_get_width function for legacy is not defined
- drivers: perf: added capabilities for legacy PMU
- afs: Fix endless loop in directory parsing
- fbcon: always restore the old font data in fbcon_do_set_font()
- drm/tegra: Remove existing framebuffer only if we support display
- RISC-V: Ignore V from the riscv,isa DT property on older T-Head CPUs
- ASoC: soc-card: Fix missing locking in snd_soc_card_get_kcontrol()
- ASoC: cs35l56: Fix deadlock in ASP1 mixer register initialization
- ASoC: cs35l56: Fix misuse of wm_adsp 'part' string for silicon revision
- ASoC: cs35l56: Fix for initializing ASP1 mixer registers
- ASoC: cs35l56: Don't add the same register patch multiple times
- ASoC: cs35l56: cs35l56_component_remove() must clean up wm_adsp
- ASoC: cs35l56: cs35l56_component_remove() must clear cs35l56->component
- riscv: Fix build error if !CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION
- ASoC: qcom: Fix uninitialized pointer dmactl
- ASoC: qcom: convert not to use asoc_xxx()
- ASoC: soc.h: convert asoc_xxx() to snd_soc_xxx()
- ALSA: Drop leftover snd-rtctimer stuff from Makefile
- ASoC: cs35l56: Must clear HALO_STATE before issuing SYSTEM_RESET
- power: supply: bq27xxx-i2c: Do not free non existing IRQ
- efi/capsule-loader: fix incorrect allocation size
- tls: fix use-after-free on failed backlog decryption
- tls: separate no-async decryption request handling from async
- tls: fix peeking with sync+async decryption
- tls: decrement decrypt_pending if no async completion will be called
- net: hsr: Use correct offset for HSR TLV values in supervisory HSR frames
- igb: extend PTP timestamp adjustments to i211
- rtnetlink: fix error logic of IFLA_BRIDGE_FLAGS writing back
- tools: ynl: fix handling of multiple mcast groups
- netfilter: nf_tables: allow NFPROTO_INET in nft_(match/target)_validate()
- Bluetooth: qca: Fix triggering coredump implementation
- Bluetooth: hci_qca: Set BDA quirk bit if fwnode exists in DT
- Bluetooth: qca: Fix wrong event type for patch config command
- Bluetooth: Enforce validation on max value of connection interval
- Bluetooth: hci_event: Fix handling of HCI_EV_IO_CAPA_REQUEST
- Bluetooth: hci_event: Fix wrongly recorded wakeup BD_ADDR
- Bluetooth: hci_sync: Fix accept_list when attempting to suspend
- Bluetooth: Avoid potential use-after-free in hci_error_reset
- Bluetooth: hci_sync: Check the correct flag before starting a scan
- stmmac: Clear variable when destroying workqueue
- uapi: in6: replace temporary label with rfc9486
- net: lan78xx: fix "softirq work is pending" error
- net: usb: dm9601: fix wrong return value in dm9601_mdio_read
- veth: try harder when allocating queue memory
- lan78xx: enable auto speed configuration for LAN7850 if no EEPROM is detected
- ipv6: fix potential "struct net" leak in inet6_rtm_getaddr()
- net: veth: clear GRO when clearing XDP even when down
- cpufreq: intel_pstate: fix pstate limits enforcement for adjust_perf call back
- tun: Fix xdp_rxq_info's queue_index when detaching
- net: dpaa: fman_memac: accept phy-interface-type = "10gbase-r" in the device tree
- net: mctp: take ownership of skb in mctp_local_output
- net: ip_tunnel: prevent perpetual headroom growth
- netlink: add nla be16/32 types to minlen array
- netlink: Fix kernel-infoleak-after-free in __skb_datagram_iter
- spi: cadence-qspi: fix pointer reference in runtime PM hooks
- mtd: spinand: gigadevice: Fix the get ecc status issue
- ublk: move ublk_cancel_dev() out of ub->mutex
- ksmbd: fix wrong allocation size update in smb2_open()
- ASoC: cs35l34: Fix GPIO name and drop legacy include
- fs/ntfs3: fix build without CONFIG_NTFS3_LZX_XPRESS
- ahci: Extend ASM1061 43-bit DMA address quirk to other ASM106x parts
- ata: ahci: add identifiers for ASM2116 series adapters
- mptcp: add needs_id for netlink appending addr
- mptcp: userspace pm send RM_ADDR for ID 0
- selftests: mptcp: add mptcp_lib_get_counter
- selftests: mptcp: join: stop transfer when check is done (part 2)
- mm: zswap: fix missing folio cleanup in writeback race path
- mm/zswap: invalidate duplicate entry when !zswap_enabled
- selftests: mptcp: join: stop transfer when check is done (part 1)
- i2c: imx: when being a target, mark the last read as processed
- drm/amd/display: Fix memory leak in dm_sw_fini()
- drm/syncobj: handle NULL fence in syncobj_eventfd_entry_func
- drm/syncobj: call drm_syncobj_fence_add_wait when WAIT_AVAILABLE flag is set
- net: phy: realtek: Fix rtl8211f_config_init() for RTL8211F(D)(I)-VD-CG PHY
- Fix write to cloned skb in ipv6_hop_ioam()
- phonet/pep: fix racy skb_queue_empty() use
- phonet: take correct lock to peek at the RX queue
- net: sparx5: Add spinlock for frame transmission from CPU
- net/sched: flower: Add lock protection when remove filter handle
- devlink: fix port dump cmd type
- tools: ynl: don't leak mcast_groups on init error
- tools: ynl: make sure we always pass yarg to mnl_cb_run
- net: mctp: put sock on tag allocation failure
- netfilter: nf_tables: use kzalloc for hook allocation
- netfilter: nf_tables: register hooks last when adding new chain/flowtable
- netfilter: nft_flow_offload: release dst in case direct xmit path is used
- netfilter: nft_flow_offload: reset dst in route object after setting up flow
- netfilter: nf_tables: set dormant flag on hook register failure
- tls: don't skip over different type records from the rx_list
- tls: stop recv() if initial process_rx_list gave us non-DATA
- tls: break out of main loop when PEEK gets a non-data record
- hwmon: (nct6775) Fix access to temperature configuration registers
- cache: ax45mp_cache: Align end size to cache boundary in ax45mp_dma_cache_wback()
- bpf, sockmap: Fix NULL pointer dereference in sk_psock_verdict_data_ready()
- s390: use the correct count for __iowrite64_copy()
- net: ipa: don't overrun IPA suspend interrupt registers
- octeontx2-af: Consider the action set by PF
- drm/i915/tv: Fix TV mode
- platform/x86: thinkpad_acpi: Only update profile if successfully converted
- arm64/sme: Restore SMCR_EL1.EZT0 on exit from suspend
- arm64/sme: Restore SME registers on exit from suspend
- arp: Prevent overflow in arp_req_get().
- devlink: fix possible use-after-free and memory leaks in devlink_init()
- ipv6: sr: fix possible use-after-free and null-ptr-deref
- afs: Increase buffer size in afs_update_volume_status()
- parisc: Fix stack unwinder
- bpf: Fix racing between bpf_timer_cancel_and_free and bpf_timer_cancel
- ata: ahci_ceva: fix error handling for Xilinx GT PHY support
- selftests: bonding: set active slave to primary eth1 specifically
- powerpc/pseries/iommu: DLPAR add doesn't completely initialize pci_controller
- net: bcmasp: Sanity check is off by one
- net: bcmasp: Indicate MAC is in charge of PHY PM
- ipv6: properly combine dev_base_seq and ipv6.dev_addr_genid
- ipv4: properly combine dev_base_seq and ipv4.dev_addr_genid
- net: stmmac: Fix incorrect dereference in interrupt handlers
- x86/numa: Fix the sort compare func used in numa_fill_memblks()
- x86/numa: Fix the address overlap check in numa_fill_memblks()
- nouveau: fix function cast warnings
- net/sched: act_mirred: don't override retval if we already lost the skb
- net/sched: act_mirred: use the backlog for mirred ingress
- net/sched: act_mirred: Create function tcf_mirred_to_dev and improve readability
- dccp/tcp: Unhash sk from ehash for tb2 alloc failure after check_estalblished().
- net: bridge: switchdev: Ensure deferred event delivery on unoffload
- net: bridge: switchdev: Skip MDB replays of deferred events on offload
- scsi: jazz_esp: Only build if SCSI core is builtin
- scsi: smartpqi: Fix disable_managed_interrupts
- bpf, scripts: Correct GPL license name
- RDMA/srpt: fix function pointer cast warnings
- xsk: Add truesize to skb_add_rx_frag().
- arm64: dts: rockchip: Correct Indiedroid Nova GPIO Names
- arm64: dts: rockchip: set num-cs property for spi on px30
- RDMA/qedr: Fix qedr_create_user_qp error flow
- bus: imx-weim: fix valid range check
- arm64: dts: tqma8mpql: fix audio codec iov-supply
- RDMA/srpt: Support specifying the srpt_service_guid parameter
- RDMA/irdma: Add AE for too many RNRS
- RDMA/irdma: Set the CQ read threshold for GEN 1
- RDMA/irdma: Validate max_send_wr and max_recv_wr
- RDMA/irdma: Fix KASAN issue with tasklet
- arm64: dts: imx8mp: Disable UART4 by default on Data Modul i.MX8M Plus eDM SBC
- IB/mlx5: Don't expose debugfs entries for RRoCE general parameters if not supported
- RDMA/bnxt_re: Add a missing check in bnxt_qplib_query_srq
- RDMA/bnxt_re: Return error for SRQ resize
- IB/hfi1: Fix a memleak in init_credit_return
- bpf: Derive source IP addr via bpf_*_fib_lookup()
- xen/events: fix error code in xen_bind_pirq_msi_to_irq()
- Revert "drm/amd/display: increased min_dcfclk_mhz and min_fclk_mhz"
- drm/amd/display: Fix buffer overflow in 'get_host_router_total_dp_tunnel_bw()'
- drm/amd/display: Avoid enum conversion warning
- smb3: add missing null server pointer check
- selftests: mptcp: diag: unique 'cestab' subtest names
- selftests: mptcp: diag: unique 'in use' subtest names
- selftests: mptcp: diag: fix bash warnings on older kernels
- selftests: mptcp: diag: check CURRESTAB counters
- selftests: mptcp: pm nl: avoid error msg on older kernels
- selftests: mptcp: pm nl: also list skipped tests
- selftests: mptcp: simult flows: fix some subtest names
- selftests: mptcp: userspace_pm: unique subtest names
- mptcp: fix duplicate subflow creation
- mptcp: fix data races on remote_id
- mptcp: fix data races on local_id
- mptcp: fix lockless access in subflow ULP diag
- mptcp: add needs_id for userspace appending addr
- usb: roles: don't get/set_role() when usb_role_switch is unregistered
- usb: roles: fix NULL pointer issue when put module's reference
- usb: gadget: omap_udc: fix USB gadget regression on Palm TE
- usb: gadget: ncm: Avoid dropping datagrams of properly parsed NTBs
- usb: cdns3: fix memory double free when handle zero packet
- usb: cdns3: fixed memory use after free at cdns3_gadget_ep_disable()
- usb: cdnsp: fixed issue with incorrect detecting CDNSP family controllers
- usb: cdnsp: blocked some cdns3 specific code
- usb: dwc3: gadget: Don't disconnect if not started
- serial: amba-pl011: Fix DMA transmission in RS485 mode
- serial: stm32: do not always set SER_RS485_RX_DURING_TX if RS485 is enabled
- Revert "usb: typec: tcpm: reset counter when enter into unattached state after try role"
- erofs: fix refcount on the metabuf used for inode lookup
- dm-integrity, dm-verity: reduce stack usage for recheck
- ARM: ep93xx: Add terminator to gpiod_lookup_table
- l2tp: pass correct message length to ip6_append_data
- PCI/MSI: Prevent MSI hardware interrupt number truncation
- irqchip/sifive-plic: Enable interrupt if needed before EOI
- irqchip/gic-v3-its: Do not assume vPE tables are preallocated
- irqchip/mbigen: Don't use bus_get_dev_root() to find the parent
- crypto: virtio/akcipher - Fix stack overflow on memcpy
- gtp: fix use-after-free and null-ptr-deref in gtp_genl_dump_pdp()
- accel/ivpu: Don't enable any tiles by default on VPU40xx
- KVM: arm64: vgic-its: Test for valid IRQ in its_sync_lpi_pending_table()
- KVM: arm64: vgic-its: Test for valid IRQ in MOVALL handler
- md: Fix missing release of 'active_io' for flush
- sparc: Fix undefined reference to fb_is_primary_device
- platform/x86: touchscreen_dmi: Allow partial (prefix) matches for ACPI names
- platform/x86: intel-vbtn: Stop calling "VBDL" from notify_handler
- mm/damon/reclaim: fix quota stauts loss due to online tunings
- mm: memcontrol: clarify swapaccount=0 deprecation warning
- mm/damon/lru_sort: fix quota status loss due to online tunings
- mm/swap: fix race when skipping swapcache
- selftests/mm: uffd-unit-test check if huge page size is 0
- scsi: core: Consult supported VPD page list prior to fetching page
- scsi: target: pscsi: Fix bio_put() for error case
- scsi: sd: usb_storage: uas: Access media prior to querying device properties
- cxl/acpi: Fix load failures due to single window creation failure
- dm-verity: recheck the hash after a failure
- dm-crypt: don't modify the data when using authenticated encryption
- dm-integrity: recheck the integrity tag after a failure
- Revert "parisc: Only list existing CPUs in cpu_possible_mask"
- dm-crypt: recheck the integrity tag after a failure
- lib/Kconfig.debug: TEST_IOV_ITER depends on MMU
- fs/aio: Restrict kiocb_set_cancel_fn() to I/O submitted via libaio
- ata: libata-core: Do not try to set sleeping devices to standby
- s390/cio: fix invalid -EBUSY on ccw_device_start
- drm/amd/display: adjust few initialization order in dm
- drm/meson: Don't remove bridges which are created by other drivers
- drm/ttm: Fix an invalid freeing on already freed page in error path
- btrfs: defrag: avoid unnecessary defrag caused by incorrect extent size
- LoongArch: Update cpu_sibling_map when disabling nonboot CPUs
- LoongArch: Disable IRQ before init_fn() for nonboot CPUs
- LoongArch: Call early_init_fdt_scan_reserved_mem() earlier
- docs: Instruct LaTeX to cope with deeper nesting
- x86/bugs: Add asm helpers for executing VERW
- IB/hfi1: Fix sdma.h tx->num_descs off-by-one error
- xen/events: close evtchn after mapping cleanup
- xen/events: modify internal [un]bind interfaces
- xen/events: drop xen_allocate_irqs_dynamic()
- xen/events: remove some simple helpers from events_base.c
- xen/events: reduce externally visible helper functions
- xen: evtchn: Allow shared registration of IRQ handers
- drm/amd/display: fixed integer types and null check locations
- drm/amd/display: Request usb4 bw for mst streams
- drm/amd/display: Add dpia display mode validation logic
- mptcp: corner case locking for rx path fields initialization
- mptcp: fix more tx path fields initialization
- mptcp: use mptcp_set_state
- mptcp: add CurrEstab MIB counter support
- smb3: clarify mount warning
- cifs: handle cases where multiple sessions share connection
- cifs: change tcon status when need_reconnect is set on it
- virtio-blk: Ensure no requests in virtqueues before deleting vqs.
- smb: client: set correct d_type for reparse points under DFS mounts
- drm/amdgpu: Fix HDP flush for VFs on nbio v7.9
- drm/amdgpu: Fix shared buff copy to user
- drm/amdgpu: reset gpu for s3 suspend abort case
- drm/amdgpu: skip to program GFXDEC registers for suspend abort
- libceph: fail sparse-read if the data length doesn't match
- firewire: core: send bus reset promptly on gap count error
- accel/ivpu/40xx: Stop passing SKU boot parameters to FW
- accel/ivpu: Disable d3hot_delay on all NPU generations
- accel/ivpu: Force snooping for MMU writes
- LoongArch: vDSO: Disable UBSAN instrumentation
- LoongArch: Change acpi_core_pic[NR_CPUS] to acpi_core_pic[MAX_CORE_PIC]
- LoongArch: Select HAVE_ARCH_SECCOMP to use the common SECCOMP menu
- LoongArch: Select ARCH_ENABLE_THP_MIGRATION instead of redefining it
- scsi: ufs: core: Remove the ufshcd_release() in ufshcd_err_handling_prepare()
- scsi: ufs: core: Fix shift issue in ufshcd_clear_cmd()
- scsi: lpfc: Use unsigned type for num_sge
- hwmon: (coretemp) Enlarge per package core count limit
- efi: Don't add memblocks for soft-reserved memory
- efi: runtime: Fix potential overflow of soft-reserved region size
- wifi: iwlwifi: do not announce EPCS support
- wifi: mac80211: accept broadcast probe responses on 6 GHz
- wifi: mac80211: adding missing drv_mgd_complete_tx() call
- wifi: mac80211: set station RX-NSS on reconfig
- fs/ntfs3: Fix oob in ntfs_listxattr
- fs/ntfs3: Update inode->i_size after success write into compressed file
- fs/ntfs3: Fixed overflow check in mi_enum_attr()
- fs/ntfs3: Correct function is_rst_area_valid
- fs/ntfs3: Use i_size_read and i_size_write
- fs/ntfs3: Prevent generic message "attempt to access beyond end of device"
- fs/ntfs3: use non-movable memory for ntfs3 MFT buffer cache
- fs/ntfs3: Use kvfree to free memory allocated by kvmalloc
- fs/ntfs3: Disable ATTR_LIST_ENTRY size check
- fs/ntfs3: Add NULL ptr dereference checking at the end of attr_allocate_frame()
- fs/ntfs3: ntfs3_forced_shutdown use int instead of bool
- fs/ntfs3: Implement super_operations::shutdown
- fs/ntfs3: Drop suid and sgid bits as a part of fpunch
- fs/ntfs3: Add file_modified
- fs/ntfs3: Fix detected field-spanning write (size 8) of single field "le->name"
- fs/ntfs3: Fix multithreaded stress test
- fs/ntfs3: Reduce stack usage
- fs/ntfs3: Print warning while fixing hard links count
- fs/ntfs3: Correct hard links updating when dealing with DOS names
- fs/ntfs3: Improve ntfs_dir_count
- fs/ntfs3: Modified fix directory element type detection
- fs/ntfs3: Improve alternative boot processing
- Input: i8042 - add Fujitsu Lifebook U728 to i8042 quirk table
- ext4: correct the hole length returned by ext4_map_blocks()
- smb: client: increase number of PDUs allowed in a compound request
- cifs: do not search for channel if server is terminating
- nvmet-fc: take ref count on tgtport before delete assoc
- nvmet-fc: avoid deadlock on delete association path
- nvmet-fc: abort command when there is no binding
- nvmet-fc: hold reference on hostport match
- nvmet-fc: defer cleanup using RCU properly
- nvmet-fc: release reference on target port
- nvmet-fcloop: swap the list_add_tail arguments
- nvme-fc: do not wait in vain when unloading module
- ALSA: usb-audio: Ignore clock selector errors for single connection
- ASoC: wm_adsp: Don't overwrite fwf_name with the default
- cifs: make sure that channel scaling is done only once
- drm/amd/display: increased min_dcfclk_mhz and min_fclk_mhz
- drm/amdkfd: Use correct drm device for cgroup permission check
- netfilter: conntrack: check SCTP_CID_SHUTDOWN_ACK for vtag setting in sctp_new
- misc: open-dice: Fix spurious lockdep warning
- Input: xpad - add Lenovo Legion Go controllers
- spi: sh-msiof: avoid integer overflow in constants
- regulator (max5970): Fix IRQ handler
- ASoC: sunxi: sun4i-spdif: Add support for Allwinner H616
- ALSA: usb-audio: Check presence of valid altsetting control
- usb: ucsi_acpi: Quirk to ack a connector change ack cmd
- nvmet-tcp: fix nvme tcp ida memory leak
- HID: nvidia-shield: Add missing null pointer checks to LED initialization
- ALSA: hda: Increase default bdl_pos_adj for Apollo Lake
- ALSA: hda: Replace numeric device IDs with constant values
- HID: logitech-hidpp: add support for Logitech G Pro X Superlight 2
- regulator: pwm-regulator: Add validity checks in continuous .get_voltage
- ASoC: amd: acp: Add check for cpu dai link initialization
- dmaengine: ti: edma: Add some null pointer checks to the edma_probe
- Input: goodix - accept ACPI resources with gpio_count == 3 && gpio_int_idx == 0
- ext4: avoid allocating blocks from corrupted group in ext4_mb_find_by_goal()
- ext4: avoid allocating blocks from corrupted group in ext4_mb_try_best_found()
- ext4: avoid dividing by 0 in mb_update_avg_fragment_size() when block bitmap corrupt
- platform/x86: touchscreen_dmi: Add info for the TECLAST X16 Plus tablet
- MIPS: reserve exception vector space ONLY ONCE
- ARM: dts: Fix TPM schema violations
- ahci: add 43-bit DMA address quirk for ASMedia ASM1061 controllers
- spi: cs42l43: Handle error from devm_pm_runtime_enable
- aoe: avoid potential deadlock at set_capacity
- ahci: asm1166: correct count of reported ports
- cifs: helper function to check replayable error codes
- cifs: translate network errors on send to -ECONNABORTED
- cifs: cifs_pick_channel should try selecting active channels
- smb: Work around Clang __bdos() type confusion
- block: Fix WARNING in _copy_from_iter
- spi: intel-pci: Add support for Arrow Lake SPI serial flash
- platform/mellanox: mlxbf-tmfifo: Drop Tx network packet when Tx TmFIFO is full
- fbdev: sis: Error out if pixclock equals zero
- fbdev: savage: Error out if pixclock equals zero
- wifi: mac80211: fix race condition on enabling fast-xmit
- wifi: cfg80211: fix missing interfaces when dumping
- dmaengine: dw-edma: increase size of 'name' in debugfs code
- dmaengine: fsl-qdma: increase size of 'irq_name'
- dmaengine: shdma: increase size of 'dev_id'
- cifs: open_cached_dir should not rely on primary channel
- scsi: target: core: Add TMF to tmr_list handling
- tools: selftests: riscv: Fix compile warnings in mm tests
- tools: selftests: riscv: Fix compile warnings in vector tests
- scsi: smartpqi: Fix logical volume rescan race condition
- scsi: smartpqi: Add new controller PCI IDs
- dmaengine: apple-admac: Keep upper bits of REG_BUS_WIDTH
- riscv/efistub: Ensure GP-relative addressing is not used
- PCI: dwc: Fix a 64bit bug in dw_pcie_ep_raise_msix_irq()
- sched/rt: Disallow writing invalid values to sched_rt_period_us
- tracing: Fix a NULL vs IS_ERR() bug in event_subsystem_dir()
- tracing: Make system_callback() function static
- Documentation/arch/ia64/features.rst: fix kernel-feat directive
- nilfs2: fix potential bug in end_buffer_async_write
- of: property: Add in-ports/out-ports support to of_graph_get_port_parent()
- sched/membarrier: reduce the ability to hammer on sys_membarrier
- x86/efistub: Use 1:1 file:memory mapping for PE/COFF .compat section
- x86/boot: Increase section and file alignment to 4k/512
- x86/boot: Split off PE/COFF .data section
- x86/boot: Drop PE/COFF .reloc section
- x86/boot: Construct PE/COFF .text section from assembler
- x86/boot: Derive file size from _edata symbol
- x86/boot: Define setup size in linker script
- x86/boot: Set EFI handover offset directly in header asm
- x86/boot: Grab kernel_info offset from zoffset header directly
- x86/boot: Drop references to startup_64
- x86/boot: Drop redundant code setting the root device
- x86/boot: Omit compression buffer from PE/COFF image memory footprint
- x86/boot: Remove the 'bugger off' message
- x86/efi: Drop alignment flags from PE section headers
- x86/efi: Disregard setup header of loaded image
- x86/efi: Drop EFI stub .bss from .data section
- nfsd: don't take fi_lock in nfsd_break_deleg_cb()
- eventfs: Keep all directory links at 1
- eventfs: Remove fsnotify*() functions from lookup()
- eventfs: Restructure eventfs_inode structure to be more condensed
- eventfs: Warn if an eventfs_inode is freed without is_freed being set
- eventfs: Get rid of dentry pointers without refcounts
- eventfs: Clean up dentry ops and add revalidate function
- eventfs: Remove unused d_parent pointer field
- tracefs: dentry lookup crapectomy
- tracefs: Avoid using the ei->dentry pointer unnecessarily
- eventfs: Initialize the tracefs inode properly
- tracefs: Zero out the tracefs_inode when allocating it
- tracefs: remove stale update_gid code
- eventfs: Save directory inodes in the eventfs_inode structure
- eventfs: Use kcalloc() instead of kzalloc()
- eventfs: Do not create dentries nor inodes in iterate_shared
- eventfs: Have the inodes all for files and directories all be the same
- eventfs: Shortcut eventfs_iterate() by skipping entries already read
- eventfs: Read ei->entries before ei->children in eventfs_iterate()
- eventfs: Do ctx->pos update for all iterations in eventfs_iterate()
- eventfs: Have eventfs_iterate() stop immediately if ei->is_freed is set
- tracefs/eventfs: Use root and instance inodes as default ownership
- eventfs: Stop using dcache_readdir() for getdents()
- eventfs: Remove "lookup" parameter from create_dir/file_dentry()
- eventfs: Fix bitwise fields for "is_events"
- tracefs: Check for dentry->d_inode exists in set_gid()
- eventfs: Fix file and directory uid and gid ownership
- eventfs: Have event files and directories default to parent uid and gid
- eventfs: Fix events beyond NAME_MAX blocking tasks
- eventfs: Make sure that parent->d_inode is locked in creating files/dirs
- eventfs: Do not allow NULL parent to eventfs_start_creating()
- eventfs: Move taking of inode_lock into dcache_dir_open_wrapper()
- eventfs: Use GFP_NOFS for allocation when eventfs_mutex is held
- eventfs: Do not invalidate dentry in create_file/dir_dentry()
- eventfs: Remove expectation that ei->is_freed means ei->dentry == NULL
- eventfs: Use simple_recursive_removal() to clean up dentries
- eventfs: Remove special processing of dput() of events directory
- eventfs: Delete eventfs_inode when the last dentry is freed
- eventfs: Hold eventfs_mutex when calling callback functions
- eventfs: Save ownership and mode
- eventfs: Test for ei->is_freed when accessing ei->dentry
- eventfs: Have a free_ei() that just frees the eventfs_inode
- eventfs: Remove "is_freed" union with rcu head
- eventfs: Fix kerneldoc of eventfs_remove_rec()
- eventfs: Remove extra dget() in eventfs_create_events_dir()
- eventfs: Fix typo in eventfs_inode union comment
- eventfs: Fix WARN_ON() in create_file_dentry()
- tracefs/eventfs: Modify mismatched function name
- eventfs: Fix failure path in eventfs_create_events_dir()
- eventfs: Use ERR_CAST() in eventfs_create_events_dir()
- eventfs: Use eventfs_remove_events_dir()
- eventfs: Remove eventfs_file and just use eventfs_inode
- Revert "eventfs: Remove "is_freed" union with rcu head"
- Revert "eventfs: Save ownership and mode"
- Revert "eventfs: Delete eventfs_inode when the last dentry is freed"
- Revert "eventfs: Use simple_recursive_removal() to clean up dentries"
- Revert "eventfs: Check for NULL ef in eventfs_set_attr()"
- Revert "eventfs: Do not allow NULL parent to eventfs_start_creating()"
- parisc: Fix random data corruption from exception handler
- netfilter: ipset: Missing gc cancellations fixed
- netfilter: ipset: fix performance regression in swap operation
- block: fix partial zone append completion handling in req_bio_endio()
- tracing: Inform kmemleak of saved_cmdlines allocation
- tracing: Fix HAVE_DYNAMIC_FTRACE_WITH_REGS ifdef
- fs/proc: do_task_stat: move thread_group_cputime_adjusted() outside of lock_task_sighand()
- pmdomain: core: Move the unused cleanup to a _sync initcall
- can: j1939: Fix UAF in j1939_sk_match_filter during setsockopt(SO_J1939_FILTER)
- can: j1939: prevent deadlock by changing j1939_socks_lock to rwlock
- can: netlink: Fix TDCO calculation using the old data bittiming
- of: property: fix typo in io-channels
- docs: kernel_feat.py: fix build error for missing files
- blk-wbt: Fix detection of dirty-throttled tasks
- LoongArch: Fix earlycon parameter if KASAN enabled
- mm: hugetlb pages should not be reserved by shmat() if SHM_NORESERVE
- ceph: prevent use-after-free in encode_cap_msg()
- hv_netvsc: Register VF in netvsc_probe if NET_DEVICE_REGISTER missed
- net: stmmac: protect updates of 64-bit statistics counters
- pmdomain: renesas: r8a77980-sysc: CR7 must be always on
- net: ethernet: ti: cpsw_new: enable mac_managed_pm to fix mdio
- s390/qeth: Fix potential loss of L3-IP@ in case of network issues
- net: ethernet: ti: cpsw: enable mac_managed_pm to fix mdio
- fs: relax mount_setattr() permission checks
- tools/rtla: Fix Makefile compiler options for clang
- tools/rtla: Fix uninitialized bucket/data->bucket_size warning
- tools/rtla: Exit with EXIT_SUCCESS when help is invoked
- tools/rtla: Fix clang warning about mount_point var size
- tools/rtla: Replace setting prio with nice for SCHED_OTHER
- tools/rtla: Remove unused sched_getattr() function
- tools/rv: Fix Makefile compiler options for clang
- tools/rv: Fix curr_reactor uninitialized variable
- ASoC: amd: yc: Add DMI quirk for Lenovo Ideapad Pro 5 16ARP8
- ASoC: tas2781: add module parameter to tascodec_init()
- ASoC: SOF: IPC3: fix message bounds on ipc ops
- arm64: Subscribe Microsoft Azure Cobalt 100 to ARM Neoverse N2 errata
- arm64/signal: Don't assume that TIF_SVE means we saved SVE state
- mmc: sdhci-pci-o2micro: Fix a warm reboot issue that disk can't be detected by BIOS
- zonefs: Improve error handling
- KVM: arm64: Fix circular locking dependency
- smb: Fix regression in writes when non-standard maximum write size negotiated
- smb: client: set correct id, uid and cruid for multiuser automounts
- thunderbolt: Fix setting the CNS bit in ROUTER_CS_5
- irqchip/gic-v3-its: Fix GICv4.1 VPE affinity update
- irqchip/gic-v3-its: Restore quirk probing for ACPI-based systems
- irqchip/irq-brcmstb-l2: Add write memory barrier before exit
- wifi: iwlwifi: mvm: fix a crash when we run out of stations
- wifi: mac80211: reload info pointer in ieee80211_tx_dequeue()
- wifi: cfg80211: fix wiphy delayed work queueing
- wifi: iwlwifi: fix double-free bug
- nfp: flower: prevent re-adding mac index for bonded port
- nfp: enable NETDEV_XDP_ACT_REDIRECT feature flag
- nfp: use correct macro for LengthSelect in BAR config
- crypto: algif_hash - Remove bogus SGL free on zero-length error path
- crypto: ccp - Fix null pointer dereference in __sev_platform_shutdown_locked
- nilfs2: fix hang in nilfs_lookup_dirty_data_buffers()
- nilfs2: fix data corruption in dsync block recovery for small block sizes
- ALSA: hda/realtek: add IDs for Dell dual spk platform
- ALSA: hda/conexant: Add quirk for SWS JS201D
- ALSA: hda/realtek: fix mute/micmute LED For HP mt645
- mmc: slot-gpio: Allow non-sleeping GPIO ro
- io_uring/net: fix multishot accept overflow handling
- x86/mm/ident_map: Use gbpages only where full GB page should be mapped.
- KVM: x86/pmu: Fix type length error when reading pmu->fixed_ctr_ctrl
- KVM: x86: make KVM_REQ_NMI request iff NMI pending for vcpu
- x86/Kconfig: Transmeta Crusoe is CPU family 5, not 6
- serial: mxs-auart: fix tx
- serial: core: introduce uart_port_tx_flags()
- powerpc/pseries: fix accuracy of stolen time
- powerpc/cputable: Add missing PPC_FEATURE_BOOKE on PPC64 Book-E
- powerpc/64: Set task pt_regs->link to the LR value on scv entry
- ftrace: Fix DIRECT_CALLS to use SAVE_REGS by default
- serial: max310x: prevent infinite while() loop in port startup
- serial: max310x: fail probe if clock crystal is unstable
- serial: max310x: improve crystal stable clock detection
- serial: max310x: set default value when reading clock ready bit
- nfp: flower: fix hardware offload for the transfer layer port
- nfp: flower: add hardware offload check for post ct entry
- net: dsa: mv88e6xxx: Fix failed probe due to unsupported C45 reads
- ring-buffer: Clean ring_buffer_poll_wait() error return
- hv_netvsc: Fix race condition between netvsc_probe and netvsc_remove
- drm/amd/display: Preserve original aspect ratio in create stream
- drm/amd/display: Increase frame-larger-than for all display_mode_vba files
- drm/amd/display: Fix MST Null Ptr for RV
- drm/amdgpu/soc21: update VCN 4 max HEVC encoding resolution
- drm/prime: Support page array >= 4GB
- drm/amd/display: Add align done check
- drm/msm: Wire up tlb ops
- ksmbd: free aux buffer if ksmbd_iov_pin_rsp_read fails
- media: rc: bpf attach/detach requires write permission
- pmdomain: mediatek: fix race conditions with genpd
- iio: pressure: bmp280: Add missing bmp085 to SPI id table
- iio: imu: bno055: serdev requires REGMAP
- iio: imu: adis: ensure proper DMA alignment
- iio: adc: ad_sigma_delta: ensure proper DMA alignment
- iio: accel: bma400: Fix a compilation problem
- iio: commom: st_sensors: ensure proper DMA alignment
- iio: core: fix memleak in iio_device_register_sysfs
- iio: magnetometer: rm3100: add boundary check for the value read from RM3100_REG_TMRC
- staging: iio: ad5933: fix type mismatch regression
- tracing/probes: Fix to search structure fields correctly
- tracing/probes: Fix to set arg size and fmt after setting type from BTF
- tracing/probes: Fix to show a parse error for bad type for $comm
- tracing/synthetic: Fix trace_string() return value
- tracing: Fix wasted memory in saved_cmdlines logic
- tracing/timerlat: Move hrtimer_init to timerlat_fd open()
- ext4: avoid bb_free and bb_fragments inconsistency in mb_free_blocks()
- ext4: fix double-free of blocks due to wrong extents moved_len
- misc: fastrpc: Mark all sessions as invalid in cb_remove
- binder: signal epoll threads of self-work
- ALSA: hda/realtek: fix mute/micmute LEDs for HP ZBook Power
- ALSA: hda/cs8409: Suppress vmaster control for Dolphin models
- ASoC: codecs: wcd938x: handle deferred probe
- ALSA: hda/realtek - Add speaker pin verbtable for Dell dual speaker platform
- ALSA: hda/realtek: Enable headset mic on Vaio VJFE-ADL
- usb: typec: tpcm: Fix issues with power being removed during reset
- modpost: Add '.ltext' and '.ltext.*' to TEXT_SECTIONS
- linux/init: remove __memexit* annotations
- um: Fix adding '-no-pie' for clang
- xen-netback: properly sync TX responses
- parisc: BTLB: Fix crash when setting up BTLB at CPU bringup
- net: stmmac: do not clear TBS enable bit on link up/down
- net: hsr: remove WARN_ONCE() in send_hsr_supervision_frame()
- nfc: nci: free rx_data_reassembly skb on NCI device cleanup
- kbuild: Fix changing ELF file type for output of gen_btf for big endian
- ALSA: hda/realtek: Apply headset jack quirk for non-bass alc287 thinkpads
- firewire: core: correct documentation of fw_csr_string() kernel API
- lsm: fix the logic in security_inode_getsecctx()
- lsm: fix default return value of the socket_getpeersec_*() hooks
- drm/amd: Don't init MEC2 firmware when it fails to load
- drm/amdgpu: Reset IH OVERFLOW_CLEAR bit
- drm/virtio: Set segment size for virtio_gpu device
- connector/cn_proc: revert "connector: Fix proc_event_num_listeners count not cleared"
- Revert "drm/msm/gpu: Push gpu lock down past runpm"
- Revert "drm/amd: flush any delayed gfxoff on suspend entry"
- scsi: Revert "scsi: fcoe: Fix potential deadlock on &fip->ctlr_lock"
- media: Revert "media: rkisp1: Drop IRQF_SHARED"
- Revert "powerpc/pseries/iommu: Fix iommu initialisation during DLPAR add"
- mptcp: really cope with fastopen race
- mptcp: check addrs list in userspace_pm_get_local_id
- mptcp: fix rcv space initialization
- mptcp: drop the push_pending field
- selftests: mptcp: add mptcp_lib_kill_wait
- selftests: mptcp: allow changing subtests prefix
- selftests: mptcp: increase timeout to 30 min
- selftests: mptcp: add missing kconfig for NF Mangle
- selftests: mptcp: add missing kconfig for NF Filter in v6
- selftests: mptcp: add missing kconfig for NF Filter
- mptcp: fix data re-injection from stale subflow
- kallsyms: ignore ARMv4 thunks along with others
- modpost: trim leading spaces when processing source files list
- i2c: i801: Fix block process call transactions
- i2c: pasemi: split driver into two separate modules
- powerpc/kasan: Limit KASAN thread size increase to 32KB
- irqchip/gic-v3-its: Handle non-coherent GICv4 redistributors
- i2c: qcom-geni: Correct I2C TRE sequence
- cifs: fix underflow in parse_server_interfaces()
- iio: adc: ad4130: only set GPIO_CTRL if pin is unused
- iio: adc: ad4130: zero-initialize clock init data
- PCI: Fix active state requirement in PME polling
- Revert "kobject: Remove redundant checks for whether ktype is NULL"
- powerpc/kasan: Fix addr error caused by page alignment
- powerpc/6xx: set High BAT Enable flag on G2_LE cores
- powerpc/pseries/iommu: Fix iommu initialisation during DLPAR add
- driver core: fw_devlink: Improve detection of overlapping cycles
- media: ir_toy: fix a memleak in irtoy_tx
- interconnect: qcom: sm8550: Enable sync_state
- interconnect: qcom: sc8180x: Mark CO0 BCM keepalive
- usb: dwc3: gadget: Fix NULL pointer dereference in dwc3_gadget_suspend
- usb: core: Prevent null pointer dereference in update_port_device_state
- usb: chipidea: core: handle power lost in workqueue
- usb: f_mass_storage: forbid async queue when shutdown happen
- USB: hub: check for alternate port before enabling A_ALT_HNP_SUPPORT
- usb: ucsi_acpi: Fix command completion handling
- usb: ulpi: Fix debugfs directory leak
- usb: ucsi: Add missing ppm_lock
- iio: hid-sensor-als: Return 0 for HID_USAGE_SENSOR_TIME_TIMESTAMP
- HID: wacom: Do not register input devices until after hid_hw_start
- HID: wacom: generic: Avoid reporting a serial of '0' to userspace
- HID: i2c-hid-of: fix NULL-deref on failed power up
- HID: bpf: actually free hdev memory after attaching a HID-BPF program
- HID: bpf: remove double fdget()
- ALSA: hda/realtek: Enable Mute LED on HP Laptop 14-fq0xxx
- ALSA: hda/realtek: Fix the external mic not being recognised for Acer Swift 1 SF114-32
- parisc: Prevent hung tasks when printing inventory on serial console
- ASoC: amd: yc: Add DMI quirk for MSI Bravo 15 C7VF
- dm-crypt, dm-verity: disable tasklets
- nouveau: offload fence uevents work to workqueue
- scsi: storvsc: Fix ring buffer size calculation
- selftests: mm: fix map_hugetlb failure on 64K page size systems
- selftests/mm: Update va_high_addr_switch.sh to check CPU for la57 flag
- mm/writeback: fix possible divide-by-zero in wb_dirty_limits(), again
- selftests/mm: switch to bash from sh
- tracing/trigger: Fix to return error if failed to alloc snapshot
- scs: add CONFIG_MMU dependency for vfree_atomic()
- selftests/mm: ksm_tests should only MADV_HUGEPAGE valid memory
- userfaultfd: fix mmap_changing checking in mfill_atomic_hugetlb
- i40e: Fix waiting for queues of all VSIs to be disabled
- i40e: Do not allow untrusted VF to remove administratively set MAC
- mm/memory: Use exception ip to search exception tables
- ptrace: Introduce exception_ip arch hook
- MIPS: Add 'memory' clobber to csum_ipv6_magic() inline assembler
- nouveau/svm: fix kvcalloc() argument order
- net: sysfs: Fix /sys/class/net/<iface> path for statistics
- ASoC: rt5645: Fix deadlock in rt5645_jack_detect_work()
- spi: ppc4xx: Drop write-only variable
- net: tls: fix returned read length with async decrypt
- net: tls: fix use-after-free with partial reads and async decrypt
- net: tls: handle backlogging of crypto requests
- tls: fix race between tx work scheduling and socket close
- tls: fix race between async notify and socket close
- net: tls: factor out tls_*crypt_async_wait()
- tls: extract context alloc/initialization out of tls_set_sw_offload
- lan966x: Fix crash when adding interface under a lag
- net: openvswitch: limit the number of recursions from action sets
- selftests: forwarding: Fix bridge locked port test flakiness
- selftests: forwarding: Suppress grep warnings
- selftests: bridge_mdb: Use MDB get instead of dump
- selftests: forwarding: Fix bridge MDB test flakiness
- selftests: forwarding: Fix layer 2 miss test flakiness
- selftests: net: Fix bridge backup port test flakiness
- selftests/net: convert test_bridge_backup_port.sh to run it in unique namespace
- perf: CXL: fix mismatched cpmu event opcode
- ALSA: hda/cs35l56: select intended config FW_CS_DSP
- of: property: Improve finding the supplier of a remote-endpoint property
- of: property: Improve finding the consumer of a remote-endpoint property
- devlink: Fix command annotation documentation
- bonding: do not report NETDEV_XDP_ACT_XSK_ZEROCOPY
- net/handshake: Fix handshake_req_destroy_test1
- ASoC: SOF: ipc3-topology: Fix pipeline tear down logic
- wifi: iwlwifi: uninitialized variable in iwl_acpi_get_ppag_table()
- wifi: iwlwifi: Fix some error codes
- KVM: selftests: Fix a semaphore imbalance in the dirty ring logging test
- spi: imx: fix the burst length at DMA mode and CPU mode
- drm/msm/gem: Fix double resv lock aquire
- of: unittest: Fix compile in the non-dynamic case
- KVM: selftests: Avoid infinite loop in hyperv_features when invtsc is missing
- KVM: selftests: Delete superfluous, unused "stage" variable in AMX test
- selftests/landlock: Fix fs_test build with old libc
- driver core: Fix device_link_flag_is_sync_state_only()
- btrfs: don't drop extent_map for free space inode on write error
- btrfs: reject encoded write if inode has nodatasum flag set
- btrfs: don't reserve space for checksums when writing to nocow files
- btrfs: send: return EOPNOTSUPP on unknown flags
- btrfs: forbid deleting live subvol qgroup
- btrfs: do not ASSERT() if the newly created subvolume already got read
- btrfs: forbid creating subvol qgroups
- btrfs: do not delete unused block group if it may be used soon
- btrfs: add and use helper to check if block group is used
- update workarounds for gcc "asm goto" issue
- work around gcc bugs with 'asm goto' with outputs
- netfilter: nft_set_rbtree: skip end interval element from gc
- net: stmmac: xgmac: fix a typo of register name in DPP safety handling
- ALSA: usb-audio: Sort quirk table entries
- net: stmmac: xgmac: use #define for string constants
- io_uring/net: limit inline multishot retries
- io_uring/poll: add requeue return code from poll multishot handling
- io_uring/net: un-indent mshot retry path in io_recv_finish()
- io_uring/poll: move poll execution helpers higher up
- io_uring/net: fix sr->len for IORING_OP_RECV with MSG_WAITALL and buffers
- media: solo6x10: replace max(a, min(b, c)) by clamp(b, a, c)
- Revert "ASoC: amd: Add new dmi entries for acp5x platform"
- Input: atkbd - skip ATKBD_CMD_SETLEDS when skipping ATKBD_CMD_GETID
- Input: i8042 - fix strange behavior of touchpad on Clevo NS70PU
- hrtimer: Report offline hrtimer enqueue
- usb: dwc3: pci: add support for the Intel Arrow Lake-H
- xhci: handle isoc Babble and Buffer Overrun events properly
- xhci: process isoc TD properly when there was a transaction error mid TD.
- usb: host: xhci-plat: Add support for XHCI_SG_TRB_CACHE_SIZE_QUIRK
- usb: dwc3: host: Set XHCI_SG_TRB_CACHE_SIZE_QUIRK
- x86/lib: Revert to _ASM_EXTABLE_UA() for {get,put}_user() fixups
- Revert "usb: typec: tcpm: fix cc role at port reset"
- USB: serial: cp210x: add ID for IMST iM871A-USB
- USB: serial: option: add Fibocom FM101-GL variant
- USB: serial: qcserial: add new usb-id for Dell Wireless DW5826e
- ALSA: usb-audio: add quirk for RODE NT-USB+
- ALSA: usb-audio: Add a quirk for Yamaha YIT-W12TX transmitter
- ALSA: usb-audio: Add delay quirk for MOTU M Series 2nd revision
- blk-iocost: Fix an UBSAN shift-out-of-bounds warning
- riscv: declare overflow_stack as exported from traps.c
- riscv: Fix arch_hugetlb_migration_supported() for NAPOT
- libceph: just wait for more data to be available on the socket
- libceph: rename read_sparse_msg_*() to read_partial_sparse_msg_*()
- riscv: Flush the tlb when a page directory is freed
- scsi: core: Move scsi_host_busy() out of host lock if it is for per-command
- riscv: Fix hugetlb_mask_last_page() when NAPOT is enabled
- riscv: Fix set_huge_pte_at() for NAPOT mapping
- riscv: mm: execute local TLB flush after populating vmemmap
- mm: Introduce flush_cache_vmap_early()
- riscv: Improve flush_tlb_kernel_range()
- riscv: Make __flush_tlb_range() loop over pte instead of flushing the whole tlb
- riscv: Improve tlb_flush()
- fs/ntfs3: Fix an NULL dereference bug
- netfilter: nft_set_pipapo: remove scratch_aligned pointer
- netfilter: nft_set_pipapo: add helper to release pcpu scratch area
- netfilter: nft_set_pipapo: store index in scratch maps
- netfilter: nft_ct: reject direction for ct id
- drm/amd/display: Implement bounds check for stream encoder creation in DCN301
- drm/amd/display: Add NULL test for 'timing generator' in 'dcn21_set_pipe()'
- drm/amd/display: Fix 'panel_cntl' could be null in 'dcn21_set_backlight_level()'
- netfilter: nft_compat: restrict match/target protocol to u16
- netfilter: nft_compat: reject unused compat flag
- netfilter: nft_compat: narrow down revision to unsigned 8-bits
- selftests: cmsg_ipv6: repeat the exact packet
- ppp_async: limit MRU to 64K
- af_unix: Call kfree_skb() for dead unix_(sk)->oob_skb in GC.
- tipc: Check the bearer type before calling tipc_udp_nl_bearer_add()
- selftests: net: let big_tcp test cope with slow env
- rxrpc: Fix counting of new acks and nacks
- rxrpc: Fix response to PING RESPONSE ACKs to a dead call
- rxrpc: Fix delayed ACKs to not set the reference serial number
- rxrpc: Fix generation of serial numbers to skip zero
- drm/i915/gvt: Fix uninitialized variable in handle_mmio()
- inet: read sk->sk_family once in inet_recv_error()
- hwmon: (coretemp) Fix bogus core_id to attr name mapping
- hwmon: (coretemp) Fix out-of-bounds memory access
- hwmon: (aspeed-pwm-tacho) mutex for tach reading
- octeontx2-pf: Fix a memleak otx2_sq_init
- atm: idt77252: fix a memleak in open_card_ubr0
- tunnels: fix out of bounds access when building IPv6 PMTU error
- tsnep: Fix mapping for zero copy XDP_TX action
- selftests: net: avoid just another constant wait
- selftests: net: fix tcp listener handling in pmtu.sh
- selftests/net: change shebang to bash to support "source"
- selftests/net: convert pmtu.sh to run it in unique namespace
- selftests/net: convert unicast_extensions.sh to run it in unique namespace
- selftests: net: cut more slack for gro fwd tests.
- net: atlantic: Fix DMA mapping for PTP hwts ring
- netdevsim: avoid potential loop in nsim_dev_trap_report_work()
- wifi: brcmfmac: Adjust n_channels usage for __counted_by
- wifi: iwlwifi: exit eSR only after the FW does
- wifi: mac80211: fix waiting for beacons logic
- wifi: mac80211: fix RCU use in TDLS fast-xmit
- net: stmmac: xgmac: fix handling of DPP safety error for DMA channels
- x86/efistub: Avoid placing the kernel below LOAD_PHYSICAL_ADDR
- x86/efistub: Give up if memory attribute protocol returns an error
- drm/msm/dpu: check for valid hw_pp in dpu_encoder_helper_phys_cleanup
- drm/msm/dp: return correct Colorimetry for DP_TEST_DYNAMIC_RANGE_CEA case
- drm/msms/dp: fixed link clock divider bits be over written in BPC unknown case
- xfs: respect the stable writes flag on the RT device
- xfs: clean up FS_XFLAG_REALTIME handling in xfs_ioctl_setattr_xflags
- xfs: dquot recovery does not validate the recovered dquot
- xfs: clean up dqblk extraction
- xfs: inode recovery does not validate the recovered inode
- xfs: fix again select in kconfig XFS_ONLINE_SCRUB_STATS
- xfs: fix internal error from AGFL exhaustion
- xfs: up(ic_sema) if flushing data device fails
- xfs: only remap the written blocks in xfs_reflink_end_cow_extent
- xfs: allow read IO and FICLONE to run concurrently
- xfs: handle nimaps=0 from xfs_bmapi_write in xfs_alloc_file_space
- xfs: introduce protection for drop nlink
- xfs: make sure maxlen is still congruent with prod when rounding down
- xfs: fix units conversion error in xfs_bmap_del_extent_delay
- xfs: rt stubs should return negative errnos when rt disabled
- xfs: prevent rt growfs when quota is enabled
- xfs: hoist freeing of rt data fork extent mappings
- xfs: bump max fsgeom struct version
- MAINTAINERS: add Catherine as xfs maintainer for 6.6.y
- rust: upgrade to Rust 1.73.0
- rust: print: use explicit link in documentation
- rust: task: remove redundant explicit link
- rust: upgrade to Rust 1.72.1
- rust: arc: add explicit `drop()` around `Box::from_raw()`
- cifs: failure to add channel on iface should bump up weight
- cifs: avoid redundant calls to disable multichannel
- phy: ti: phy-omap-usb2: Fix NULL pointer dereference for SRP
- dmaengine: fix is_slave_direction() return false when DMA_DEV_TO_DEV
- perf evlist: Fix evlist__new_default() for > 1 core PMU
- phy: renesas: rcar-gen3-usb2: Fix returning wrong error code
- dmaengine: fsl-qdma: Fix a memory leak related to the queue command DMA
- dmaengine: fsl-qdma: Fix a memory leak related to the status queue DMA
- dmaengine: ti: k3-udma: Report short packet errors
- dmaengine: fsl-dpaa2-qdma: Fix the size of dma pools
- pds_core: Prevent health thread from running during reset/remove
- drm/amdgpu: Fix missing error code in 'gmc_v6/7/8/9_0_hw_init()'
- ASoC: codecs: wsa883x: fix PA volume control
- ASoC: codecs: lpass-wsa-macro: fix compander volume hack
- ASoC: codecs: wcd938x: fix headphones volume controls
- ASoC: qcom: sc8280xp: limit speaker volumes
- bonding: remove print in bond_verify_device_path
- selftests/bpf: Remove flaky test_btf_id test
- LoongArch/smp: Call rcutree_report_cpu_starting() at tlb_init()
- drm/msm/dsi: Enable runtime PM
- Revert "drm/amd/display: Disable PSR-SU on Parade 0803 TCON again"
- mm, kmsan: fix infinite recursion due to RCU critical section
- arm64: irq: set the correct node for shadow call stack
- selftests: net: enable some more knobs
- selftests: net: add missing config for NF_TARGET_TTL
- selftests: bonding: Check initial state
- selftests: team: Add missing config options
- net: sysfs: Fix /sys/class/net/<iface> path
- octeontx2-pf: Remove xdp queues on program detach
- selftests: net: don't access /dev/stdout in pmtu.sh
- selftests: net: fix available tunnels detection
- selftests: net: add missing config for pmtu.sh tests
- selftests: net: add missing config for nftables-backed iptables
- pds_core: Rework teardown/setup flow to be more common
- pds_core: Clear BARs on reset
- pds_core: Prevent race issues involving the adminq
- pds_core: implement pci reset handlers
- pds_core: Use struct pdsc for the pdsc_adminq_isr private data
- pds_core: Cancel AQ work on teardown
- af_unix: fix lockdep positive in sk_diag_dump_icons()
- net: ipv4: fix a memleak in ip_setup_cork
- netfilter: nft_ct: sanitize layer 3 and 4 protocol number in custom expectations
- netfilter: nf_log: replace BUG_ON by WARN_ON_ONCE when putting logger
- netfilter: nf_tables: restrict tunnel object to NFPROTO_NETDEV
- netfilter: conntrack: correct window scaling with retransmitted SYN
- selftests: net: add missing config for GENEVE
- devlink: Fix referring to hw_addr attribute during state validation
- bridge: mcast: fix disabled snooping after long uptime
- selftests: net: Add missing matchall classifier
- llc: call sock_orphan() at release time
- ipv6: Ensure natural alignment of const ipv6 loopback and router addresses
- net: dsa: qca8k: fix illegal usage of GPIO
- ixgbe: Fix an error handling path in ixgbe_read_iosf_sb_reg_x550()
- ixgbe: Refactor overtemp event handling
- ixgbe: Refactor returning internal error codes
- e1000e: correct maximum frequency adjustment values
- tcp: add sanity checks to rx zerocopy
- net: lan966x: Fix port configuration when using SGMII interface
- ipmr: fix kernel panic when forwarding mcast packets
- net: dsa: mt7530: fix 10M/100M speed on MT7988 switch
- ip6_tunnel: make sure to pull inner header in __ip6_tnl_rcv()
- selftests: net: give more time for GRO aggregation
- selftests: net: add missing required classifier
- selftests: net: add missing config for big tcp tests
- net: phy: mediatek-ge-soc: sync driver with MediaTek SDK
- net: ethernet: mtk_eth_soc: set DMA coherent mask to get PPE working
- gve: Fix skb truesize underestimation
- selftests: net: explicitly wait for listener ready
- selftests: net: remove dependency on ebpf tests
- HID: hidraw: fix a problem of memory leak in hidraw_release()
- scsi: core: Move scsi_host_busy() out of host lock for waking up EH handler
- regulator: ti-abb: don't use devm_platform_ioremap_resource_byname for shared interrupt register
- kunit: run test suites only after module initialization completes
- scsi: isci: Fix an error code problem in isci_io_request_build()
- riscv: Fix build error on rv32 + XIP
- drm/amdkfd: only flush mes process context if mes support is there
- drm: using mul_u32_u32() requires linux/math64.h
- wifi: cfg80211: fix RCU dereference in __cfg80211_bss_update
- perf: Fix the nr_addr_filters fix
- i2c: rk3x: Adjust mask/value offset for i2c2 on rv1126
- drm/amdkfd: Fix 'node' NULL check in 'svm_range_get_range_boundaries()'
- drm/amdgpu: Release 'adev->pm.fw' before return in 'amdgpu_device_need_post()'
- drm/amdgpu: Fix with right return code '-EIO' in 'amdgpu_gmc_vram_checking()'
- drm/amd/powerplay: Fix kzalloc parameter 'ATOM_Tonga_PPM_Table' in 'get_platform_power_management_table()'
- drm/amdgpu: fix avg vs input power reporting on smu7
- ceph: fix invalid pointer access if get_quota_realm return ERR_PTR
- ceph: reinitialize mds feature bit even when session in open
- virtio_net: Fix "‘%d’ directive writing between 1 and 11 bytes into a region of size 10" warnings
- drm/amdkfd: Fix lock dependency warning with srcu
- drm/amdkfd: Fix lock dependency warning
- libsubcmd: Fix memory leak in uniq()
- misc: lis3lv02d_i2c: Add missing setting of the reg_ctrl callback
- usb: xhci-plat: fix usb disconnect issue after s4
- 9p: Fix initialisation of netfs_inode for 9p
- PCI/AER: Decode Requester ID when no error info found
- PCI: Fix 64GT/s effective data rate calculation
- spmi: mediatek: Fix UAF on device remove
- fs/kernfs/dir: obey S_ISGID
- tty: allow TIOCSLCKTRMIOS with CAP_CHECKPOINT_RESTORE
- selftests/sgx: Fix linker script asserts
- usb: hub: Add quirk to decrease IN-ep poll interval for Microchip USB491x hub
- usb: hub: Replace hardcoded quirk value with BIT() macro
- extcon: fix possible name leak in extcon_dev_register()
- perf cs-etm: Bump minimum OpenCSD version to ensure a bugfix is present
- PCI: switchtec: Fix stdev_release() crash after surprise hot remove
- PCI: Only override AMD USB controller if required
- mailbox: arm_mhuv2: Fix a bug for mhuv2_sender_interrupt
- mfd: ti_am335x_tscadc: Fix TI SoC dependencies
- xen/gntdev: Fix the abuse of underlying struct page in DMA-buf import
- riscv: Make XIP bootable again
- i3c: master: cdns: Update maximum prescaler value for i2c clock
- um: time-travel: fix time corruption
- um: net: Fix return type of uml_net_start_xmit()
- um: Don't use vfprintf() for os_info()
- um: Fix naming clash between UML and scheduler
- leds: trigger: panic: Don't register panic notifier if creating the trigger failed
- pinctrl: baytrail: Fix types of config value in byt_pin_config_set()
- ALSA: hda/conexant: Fix headset auto detect fail in cx8070 and SN6140
- drm/amdgpu: apply the RV2 system aperture fix to RN/CZN as well
- drm/amdkfd: Fix iterator used outside loop in 'kfd_add_peer_prop()'
- drm/amdgpu: Drop 'fence' check in 'to_amdgpu_amdkfd_fence()'
- drm/amdgpu: Fix '*fw' from request_firmware() not released in 'amdgpu_ucode_request()'
- Re-revert "drm/amd/display: Enable Replay for static screen use cases"
- drm/amdgpu: Let KFD sync with VM fences
- drm/amd/display: Fix minor issues in BW Allocation Phase2
- drm/amdgpu: Fix ecc irq enable/disable unpaired
- clk: imx: clk-imx8qxp: fix LVDS bypass, pixel and phy clocks
- drm/amd/display: Only clear symclk otg flag for HDMI
- drm/amd/display: make flip_timestamp_in_us a 64-bit variable
- accel/habanalabs: add support for Gaudi2C device
- watchdog: it87_wdt: Keep WDTCTRL bit 3 unmodified for IT8784/IT8786
- watchdog: starfive: add lock annotations to fix context imbalances
- clk: mmp: pxa168: Fix memory leak in pxa168_clk_init()
- clk: hi3620: Fix memory leak in hi3620_mmc_clk_init()
- drm/amdgpu: fix ftrace event amdgpu_bo_move always move on same heap
- drm/msm/dpu: fix writeback programming for YUV cases
- drm/msm/dpu: Ratelimit framedone timeout msgs
- drm/msm/dpu: enable writeback on SM8450
- drm/msm/dpu: enable writeback on SM8350
- drm/amdkfd: fix mes set shader debugger process management
- drm/amd/display: Force p-state disallow if leaving no plane config
- drm/amd/display: For prefetch mode > 0, extend prefetch if possible
- media: i2c: imx335: Fix hblank min/max values
- media: ddbridge: fix an error code problem in ddb_probe
- media: amphion: remove mutext lock in condition of wait_event
- IB/ipoib: Fix mcast list locking
- drm/exynos: Call drm_atomic_helper_shutdown() at shutdown/unbind time
- hwmon: (hp-wmi-sensors) Fix failure to load on EliteDesk 800 G6
- hwmon: (nct6775) Fix fan speed set failure in automatic mode
- media: rkisp1: resizer: Stop manual allocation of v4l2_subdev_state
- media: rkisp1: Fix IRQ disable race issue
- media: rkisp1: Store IRQ lines
- media: rkisp1: Fix IRQ handler return values
- media: rkisp1: Drop IRQF_SHARED
- media: uvcvideo: Fix power line control for SunplusIT camera
- media: uvcvideo: Fix power line control for a Chicony camera
- drm/msm/dp: Add DisplayPort controller for SM8650
- ALSA: hda: intel-dspcfg: add filters for ARL-S and ARL
- ALSA: hda: Intel: add HDA_ARL PCI ID support
- PCI: add INTEL_HDA_ARL to pci_ids.h
- media: rockchip: rga: fix swizzling for RGB formats
- media: stk1160: Fixed high volume of stk1160_dbg messages
- drm/mipi-dsi: Fix detach call without attach
- drm/framebuffer: Fix use of uninitialized variable
- drm/drm_file: fix use of uninitialized variable
- drm/amd/display: Fix MST PBN/X.Y value calculations
- ASoC: amd: Add new dmi entries for acp5x platform
- f2fs: fix write pointers on zoned device after roll forward
- drm/amd/display: Fix tiled display misalignment
- drm/bridge: anx7625: Fix Set HPD irq detect window to 2ms
- drm/panel-edp: Add override_edid_mode quirk for generic edp
- RDMA/IPoIB: Fix error code return in ipoib_mcast_join
- reiserfs: Avoid touching renamed directory if parent does not change
- fast_dput(): handle underflows gracefully
- ASoC: doc: Fix undefined SND_SOC_DAPM_NOPM argument
- ALSA: hda: Refer to correct stream index at loops
- f2fs: fix to check return value of f2fs_reserve_new_block()
- net: dsa: qca8k: put MDIO bus OF node on qca8k_mdio_register() failure
- net: kcm: fix direct access to bv_len
- octeontx2-af: Fix max NPC MCAM entry check while validating ref_entry
- i40e: Fix VF disable behavior to block all traffic
- arm64: dts: sprd: Change UMS512 idle-state nodename to match bindings
- arm64: dts: sprd: Add clock reference for pll2 on UMS512
- bridge: cfm: fix enum typo in br_cc_ccm_tx_parse
- net/smc: disable SEID on non-s390 archs where virtual ISM may be used
- Bluetooth: L2CAP: Fix possible multiple reject send
- Bluetooth: hci_sync: fix BR/EDR wakeup bug
- Bluetooth: ISO: Avoid creating child socket if PA sync is terminating
- Bluetooth: qca: Set both WIDEBAND_SPEECH and LE_STATES quirks for QCA2066
- wifi: cfg80211: free beacon_ies when overridden from hidden BSS
- wifi: rtlwifi: rtl8723{be,ae}: using calculate_bit_shift()
- libbpf: Fix NULL pointer dereference in bpf_object__collect_prog_relos
- wifi: rtw89: coex: Fix wrong Wi-Fi role info and FDDT parameter members
- wifi: rtl8xxxu: Add additional USB IDs for RTL8192EU devices
- arm64: dts: amlogic: fix format for s4 uart node
- ice: fix pre-shifted bit usage
- arm64: dts: qcom: Fix coresight warnings in in-ports and out-ports
- arm64: dts: qcom: msm8998: Fix 'out-ports' is a required property
- arm64: dts: qcom: msm8996: Fix 'in-ports' is a required property
- block: prevent an integer overflow in bvec_try_merge_hw_page
- net: dsa: mv88e6xxx: Fix mv88e6352_serdes_get_stats error path
- net: atlantic: eliminate double free in error handling logic
- ice: fix ICE_AQ_VSI_Q_OPT_RSS_* register values
- scsi: hisi_sas: Set .phy_attached before notifing phyup event HISI_PHYE_PHY_UP_PM
- scsi: lpfc: Move determination of vmid_flag after VMID reinitialization completes
- scsi: lpfc: Reinitialize an NPIV's VMID data structures after FDISC
- ARM: dts: imx23/28: Fix the DMA controller node name
- ARM: dts: imx23-sansa: Use preferred i2c-gpios properties
- ARM: dts: imx27-apf27dev: Fix LED name
- ARM: dts: imx25/27: Pass timing0
- ARM: dts: imx25: Fix the iim compatible string
- selftests/bpf: fix compiler warnings in RELEASE=1 mode
- arm64: zynqmp: Fix clock node name in kv260 cards
- arm64: zynqmp: Move fixed clock to / for kv260
- block/rnbd-srv: Check for unlikely string overflow
- ionic: bypass firmware cmds when stuck in reset
- ionic: pass opcode to devcmd_wait
- net: phy: at803x: fix passing the wrong reference for config_intr
- ARM: dts: imx1: Fix sram node
- ARM: dts: imx27: Fix sram node
- ARM: dts: imx: Use flash@0,0 pattern
- ARM: dts: imx25/27-eukrea: Fix RTC node name
- ARM: dts: rockchip: fix rk3036 hdmi ports node
- wifi: ath12k: fix the issue that the multicast/broadcast indicator is not read correctly for WCN7850
- bpf: Set uattr->batch.count as zero before batched update or deletion
- wifi: mt76: mt7996: add PCI IDs for mt7992
- wifi: mt76: connac: fix EHT phy mode check
- arm64: dts: qcom: sm8350: Fix remoteproc interrupt type
- arm64: dts: qcom: sm8450: fix soundwire controllers node name
- arm64: dts: qcom: sm8550: fix soundwire controllers node name
- net: mvmdio: Avoid excessive sleeps in polled mode
- minmax: relax check to allow comparison between unsigned arguments and signed constants
- minmax: allow comparisons of 'int' against 'unsigned char/short'
- minmax: fix indentation of __cmp_once() and __clamp_once()
- minmax: allow min()/max()/clamp() if the arguments have the same signedness.
- minmax: add umin(a, b) and umax(a, b)
- minmax: fix header inclusions
- minmax: deduplicate __unconst_integer_typeof()
- scsi: libfc: Fix up timeout error in fc_fcp_rec_error()
- scsi: libfc: Don't schedule abort twice
- wifi: ath12k: fix and enable AP mode for WCN7850
- bpf: Set need_defer as false when clearing fd array during map free
- bpf: Check rcu_read_lock_trace_held() before calling bpf map helpers
- wifi: rtw89: fix misbehavior of TX beacon in concurrent mode
- wifi: ath11k: fix race due to setting ATH11K_FLAG_EXT_IRQ_ENABLED too early
- wifi: ath9k: Fix potential array-index-out-of-bounds read in ath9k_htc_txstatus()
- bpf: Fix a few selftest failures due to llvm18 change
- ARM: dts: imx7s: Fix nand-controller #size-cells
- ARM: dts: imx7s: Fix lcdif compatible
- ARM: dts: imx7d: Fix coresight funnel ports
- scsi: arcmsr: Support new PCI device IDs 1883 and 1886
- scsi: mpi3mr: Add PCI checks where SAS5116 diverges from SAS4116
- scsi: mpi3mr: Add support for SAS5116 PCI IDs
- net: usb: ax88179_178a: avoid two consecutive device resets
- bonding: return -ENOMEM instead of BUG in alb_upper_dev_walk
- PCI: Add no PM reset quirk for NVIDIA Spectrum devices
- net: phy: micrel: fix ts_info value in case of no phc
- ARM: dts: samsung: s5pv210: fix camera unit addresses/ranges
- ARM: dts: samsung: exynos4: fix camera unit addresses/ranges
- scsi: lpfc: Fix possible file string name overflow when updating firmware
- soc: xilinx: fix unhandled SGI warning message
- soc: xilinx: Fix for call trace due to the usage of smp_processor_id()
- ARM: dts: qcom: msm8660: fix PMIC node labels
- ARM: dts: qcom: mdm9615: fix PMIC node labels
- ARM: dts: qcom: strip prefix from PMIC files
- selftests/bpf: Fix issues in setup_classid_environment()
- wifi: rt2x00: correct wrong BBP register in RxDCOC calibration
- selftests/bpf: Fix pyperf180 compilation failure with clang18
- libbpf: Fix potential uninitialized tail padding with LIBBPF_OPTS_RESET
- selftests/bpf: satisfy compiler by having explicit return in btf test
- selftests/bpf: fix RELEASE=1 build for tc_opts
- wifi: rt2x00: restart beacon queue when hardware reset
- wifi: rtw89: fix timeout calculation in rtw89_roc_end()
- ext4: avoid online resizing failures due to oversized flex bg
- ext4: remove unnecessary check from alloc_flex_gd()
- ext4: unify the type of flexbg_size to unsigned int
- ext4: fix inconsistent between segment fstrim and full fstrim
- ecryptfs: Reject casefold directory inodes
- smb: client: fix hardlinking of reparse points
- smb: client: fix renaming of reparse points
- ext4: treat end of range as exclusive in ext4_zero_range()
- SUNRPC: Fix a suspicious RCU usage warning
- sysctl: Fix out of bounds access for empty sysctl registers
- KVM: s390: fix setting of fpc register
- s390/ptrace: handle setting of fpc register correctly
- s390/vfio-ap: fix sysfs status attribute for AP queue devices
- arch: consolidate arch_irq_work_raise prototypes
- s390/boot: always align vmalloc area on segment boundary
- jfs: fix array-index-out-of-bounds in diNewExt
- rxrpc_find_service_conn_rcu: fix the usage of read_seqbegin_or_lock()
- afs: fix the usage of read_seqbegin_or_lock() in afs_find_server*()
- afs: fix the usage of read_seqbegin_or_lock() in afs_lookup_volume_rcu()
- crypto: stm32/crc32 - fix parsing list of devices
- erofs: fix ztailpacking for subpage compressed blocks
- crypto: octeontx2 - Fix cptvf driver cleanup
- crypto: starfive - Fix dev_err_probe return error
- erofs: fix up compacted indexes for block size < 4096
- pstore/ram: Fix crash when setting number of cpus to an odd number
- crypto: p10-aes-gcm - Avoid -Wstringop-overflow warnings
- hwrng: starfive - Fix dev_err_probe return error
- jfs: fix uaf in jfs_evict_inode
- jfs: fix array-index-out-of-bounds in dbAdjTree
- jfs: fix slab-out-of-bounds Read in dtSearch
- UBSAN: array-index-out-of-bounds in dtSplitRoot
- FS:JFS:UBSAN:array-index-out-of-bounds in dbAdjTree
- thermal: core: Fix thermal zone suspend-resume synchronization
- ACPI: APEI: set memory failure flags as MF_ACTION_REQUIRED on synchronous events
- PM / devfreq: Synchronize devfreq_monitor_[start/stop]
- kunit: tool: fix parsing of test attributes
- ACPI: NUMA: Fix the logic of getting the fake_pxm value
- selftests/nolibc: fix testcase status alignment
- ACPI: extlog: fix NULL pointer dereference check
- PNP: ACPI: fix fortify warning
- ACPI: video: Add quirk for the Colorful X15 AT 23 Laptop
- audit: Send netlink ACK before setting connection in auditd_set
- regulator: core: Only increment use_count when enable_count changes
- debugobjects: Stop accessing objects after releasing hash bucket lock
- perf/core: Fix narrow startup race when creating the perf nr_addr_filters sysfs file
- x86/mce: Mark fatal MCE's page as poison to avoid panic in the kdump kernel
- powerpc: pmd_move_must_withdraw() is only needed for CONFIG_TRANSPARENT_HUGEPAGE
- x86/boot: Ignore NMIs during very early boot
- powerpc/64s: Fix CONFIG_NUMA=n build due to create_section_mapping()
- powerpc/mm: Fix build failures due to arch_reserved_kernel_pages()
- powerpc: Fix build error due to is_valid_bugaddr()
- drivers/perf: pmuv3: don't expose SW_INCR event in sysfs
- arm64: irq: set the correct node for VMAP stack
- powerpc/mm: Fix null-pointer dereference in pgtable_cache_add
- asm-generic: make sparse happy with odd-sized put_unaligned_*()
- Documentation/sphinx: fix Python string escapes
- thermal: trip: Drop lockdep assertion from thermal_zone_trip_id()
- serial: core: fix kernel-doc for uart_port_unlock_irqrestore()
- x86/entry/ia32: Ensure s32 is sign extended to s64
- tick/sched: Preserve number of idle sleeps across CPU hotplug events
- clocksource: Skip watchdog check for large watchdog intervals
- genirq: Initialize resend_node hlist for all interrupt descriptors
- mips: Call lose_fpu(0) before initializing fcr31 in mips_set_personality_nan
- cxl/region：Fix overflow issue in alloc_hpa()
- drm: bridge: samsung-dsim: Don't use FORCE_STOP_STATE
- MIPS: lantiq: register smp_ops on non-smp platforms
- spi: fix finalize message on error return
- cifs: fix stray unlock in cifs_chan_skip_or_disable
- spi: spi-cadence: Reverse the order of interleaved write and read operations
- spi: bcm-qspi: fix SFDP BFPT read by usig mspi read
- cpufreq/amd-pstate: Fix setting scaling max/min freq values
- drm/bridge: anx7625: Ensure bridge is suspended in disable()
- block: Move checking GENHD_FL_NO_PART to bdev_add_partition()
- spi: intel-pci: Remove Meteor Lake-S SoC PCI ID from the list
- ARM: dts: exynos4212-tab3: add samsung,invert-vclk flag to fimd
- gpio: eic-sprd: Clear interrupt after set the interrupt type
- firmware: arm_scmi: Use xa_insert() when saving raw queues
- firmware: arm_scmi: Use xa_insert() to store opps
- drm/exynos: gsc: minor fix for loop iteration in gsc_runtime_resume
- drm/exynos: fix accidental on-stack copy of exynos_drm_plane
- memblock: fix crash when reserved memory is not added to memory
- drm/bridge: parade-ps8640: Make sure we drop the AUX mutex in the error case
- drm/bridge: parade-ps8640: Ensure bridge is suspended in .post_disable()
- drm/bridge: sii902x: Fix audio codec unregistration
- drm/bridge: sii902x: Fix probing race issue
- drm/panel: samsung-s6d7aa0: drop DRM_BUS_FLAG_DE_HIGH for lsl080al02
- drm: panel-simple: add missing bus flags for Tianma tm070jvhg[30/33]
- drm/bridge: parade-ps8640: Wait for HPD when doing an AUX transfer
- drm/amdgpu/gfx11: set UNORD_DISPATCH in compute MQDs
- drm/amdgpu/gfx10: set UNORD_DISPATCH in compute MQDs
- drm/panel-edp: drm/panel-edp: Fix AUO B116XTN02 name
- drm/panel-edp: drm/panel-edp: Fix AUO B116XAK01 name and timing
- drm/panel-edp: Add AUO B116XTN02, BOE NT116WHM-N21,836X2, NV116WHM-N49 V8.0
- drm/i915/psr: Only allow PSR in LPSP mode on HSW non-ULT
- drm/i915/lnl: Remove watchdog timers for PSR
- btrfs: zoned: optimize hint byte for zoned allocator
- btrfs: zoned: factor out prepare_allocation_zoned()
- serial: sc16is7xx: fix unconditional activation of THRI interrupt
- serial: sc16is7xx: Use port lock wrappers
- serial: core: Provide port lock wrappers
- mm: migrate: fix getting incorrect page mapping during page migration
- mm: migrate: record the mlocked page status to remove unnecessary lru drain
- thermal: gov_power_allocator: avoid inability to reset a cdev
- thermal: core: Store trip pointer in struct thermal_instance
- thermal: trip: Drop redundant trips check from for_each_thermal_trip()
- media: i2c: imx290: Properly encode registers as little-endian
- media: v4l2-cci: Add support for little-endian encoded registers
- media: v4l: cci: Add macros to obtain register width and address
- media: v4l: cci: Include linux/bits.h
- pipe: wakeup wr_wait after setting max_usage
- fs/pipe: move check to pipe_has_watch_queue()
- thermal: intel: hfi: Add syscore callbacks for system-wide PM
- thermal: intel: hfi: Disable an HFI instance when all its CPUs go offline
- thermal: intel: hfi: Refactor enabling code into helper functions
- net/bpf: Avoid unused "sin_addr_len" warning when CONFIG_CGROUP_BPF is not set
- drm/amd/display: Fix uninitialized variable usage in core_link_ 'read_dpcd() & write_dpcd()' functions
- drm/amdgpu/pm: Fix the power source flag error
- drm/amd/display: Fix late derefrence 'dsc' check in 'link_set_dsc_pps_packet()'
- drm/amd/display: Align the returned error code with legacy DP
- drm/amd/display: Port DENTIST hang and TDR fixes to OTG disable W/A
- drm/amd/display: Fix variable deferencing before NULL check in edp_setup_replay()
- drm/amdgpu: correct the cu count for gfx v11
- drm/bridge: nxp-ptn3460: simplify some error checking
- Revert "drm/amd/display: fix bandwidth validation failure on DCN 2.1"
- drm/amd/display: Disable PSR-SU on Parade 0803 TCON again
- drm/amd/display: fix bandwidth validation failure on DCN 2.1
- drm: Allow drivers to indicate the damage helpers to ignore damage clips
- drm/virtio: Disable damage clipping if FB changed since last page-flip
- drm: Disable the cursor plane on atomic contexts with virtualized drivers
- drm/tidss: Fix atomic_flush check
- drm: Fix TODO list mentioning non-KMS drivers
- drm/bridge: nxp-ptn3460: fix i2c_master_send() error checking
- drm: Don't unref the same fb many times by mistake due to deadlock handling
- Revert "drm/i915/dsi: Do display on sequence later on icl+"
- cpufreq: intel_pstate: Refine computation of P-state for given frequency
- gpiolib: acpi: Ignore touchpad wakeup on GPD G1619-04
- xfs: read only mounts with fsopen mount API are busted
- drm/amdgpu: Fix the null pointer when load rlc firmware
- Revert "drivers/firmware: Move sysfb_init() from device_initcall to subsys_initcall_sync"
- firmware: arm_scmi: Check mailbox/SMT channel for consistency
- ksmbd: fix global oob in ksmbd_nl_policy
- platform/x86: p2sb: Allow p2sb_bar() calls during PCI device probe
- platform/x86: intel-uncore-freq: Fix types in sysfs callbacks
- netfilter: nf_tables: reject QUEUE/DROP verdict parameters
- netfilter: nft_chain_filter: handle NETDEV_UNREGISTER for inet/ingress basechain
- hv_netvsc: Calculate correct ring size when PAGE_SIZE is not 4 Kbytes
- nfsd: fix RELEASE_LOCKOWNER
- wifi: iwlwifi: fix a memory corruption
- exec: Fix error handling in begin_new_exec()
- rbd: don't move requests to the running list on errors
- btrfs: don't abort filesystem when attempting to snapshot deleted subvolume
- btrfs: defrag: reject unknown flags of btrfs_ioctl_defrag_range_args
- btrfs: don't warn if discard range is not aligned to sector
- btrfs: tree-checker: fix inline ref size in error messages
- btrfs: ref-verify: free ref cache before clearing mount opt
- btrfs: avoid copying BTRFS_ROOT_SUBVOL_DEAD flag to snapshot of subvolume being deleted
- btrfs: zoned: fix lock ordering in btrfs_zone_activate()
- tsnep: Fix XDP_RING_NEED_WAKEUP for empty fill ring
- tsnep: Remove FCS for XDP data path
- net: fec: fix the unhandled context fault from smmu
- selftests: bonding: do not test arp/ns target with mode balance-alb/tlb
- fjes: fix memleaks in fjes_hw_setup
- i40e: update xdp_rxq_info::frag_size for ZC enabled Rx queue
- i40e: set xdp_rxq_info::frag_size
- xdp: reflect tail increase for MEM_TYPE_XSK_BUFF_POOL
- ice: update xdp_rxq_info::frag_size for ZC enabled Rx queue
- intel: xsk: initialize skb_frag_t::bv_offset in ZC drivers
- ice: remove redundant xdp_rxq_info registration
- i40e: handle multi-buffer packets that are shrunk by xdp prog
- ice: work on pre-XDP prog frag count
- xsk: fix usage of multi-buffer BPF helpers for ZC XDP
- bpf: Add bpf_sock_addr_set_sun_path() to allow writing unix sockaddr from bpf
- bpf: Propagate modified uaddrlen from cgroup sockaddr programs
- xsk: make xsk_buff_pool responsible for clearing xdp_buff::flags
- xsk: recycle buffer in case Rx queue was full
- selftests: netdevsim: fix the udp_tunnel_nic test
- selftests: net: fix rps_default_mask with >32 CPUs
- net: mvpp2: clear BM pool before initialization
- net: stmmac: Wait a bit for the reset to take effect
- netfilter: nf_tables: validate NFPROTO_* family
- netfilter: nf_tables: restrict anonymous set and map names to 16 bytes
- netfilter: nft_limit: reject configurations that cause integer overflow
- rcu: Defer RCU kthreads wakeup when CPU is dying
- net/mlx5e: fix a potential double-free in fs_any_create_groups
- net/mlx5e: fix a double-free in arfs_create_groups
- net/mlx5e: Ignore IPsec replay window values on sender side
- net/mlx5e: Allow software parsing when IPsec crypto is enabled
- net/mlx5: Use mlx5 device constant for selecting CQ period mode for ASO
- net/mlx5: DR, Can't go to uplink vport on RX rule
- net/mlx5: DR, Use the right GVMI number for drop action
- net/mlx5: Bridge, fix multicast packets sent to uplink
- net/mlx5: Bridge, Enable mcast in smfs steering mode
- net/mlx5: Fix a WARN upon a callback command failure
- net/mlx5e: Fix peer flow lists handling
- net/mlx5e: Fix operation precedence bug in port timestamping napi_poll context
- net/sched: flower: Fix chain template offload
- selftests: fill in some missing configs for net
- ipv6: init the accept_queue's spinlocks in inet6_create
- netlink: fix potential sleeping issue in mqueue_flush_file
- selftest: Don't reuse port for SO_INCOMING_CPU test.
- tcp: Add memory barrier to tcp_push()
- afs: Hide silly-rename files from userspace
- tracing: Ensure visibility when inserting an element into tracing_map
- netfs, fscache: Prevent Oops in fscache_put_cache()
- net/rds: Fix UBSAN: array-index-out-of-bounds in rds_cmsg_recv
- net: micrel: Fix PTP frame parsing for lan8814
- tun: add missing rx stats accounting in tun_xdp_act
- tun: fix missing dropped counter in tun_xdp_act
- net: fix removing a namespace with conflicting altnames
- udp: fix busy polling
- llc: Drop support for ETH_P_TR_802_2.
- llc: make llc_ui_sendmsg() more robust against bonding changes
- vlan: skip nested type that is not IFLA_VLAN_QOS_MAPPING
- bnxt_en: Prevent kernel warning when running offline self test
- bnxt_en: Wait for FLR to complete during probe
- tcp: make sure init the accept_queue's spinlocks once
- selftests: bonding: Increase timeout to 1200s
- net/smc: fix illegal rmb_desc access in SMC-D connection dump
- wifi: mac80211: fix potential sta-link leak
- SUNRPC: use request size to initialize bio_vec in svc_udp_sendto()
- cifs: after disabling multichannel, mark tcon for reconnect
- cifs: fix a pending undercount of srv_count
- cifs: fix lock ordering while disabling multichannel
- Revert "drm/amd: Enable PCIe PME from D3"
- selftests/bpf: check if max number of bpf_loop iterations is tracked
- bpf: keep track of max number of bpf_loop callback iterations
- selftests/bpf: test widening for iterating callbacks
- bpf: widening for callback iterators
- selftests/bpf: tests for iterating callbacks
- bpf: verify callbacks as if they are called unknown number of times
- bpf: extract setup_func_entry() utility function
- bpf: extract __check_reg_arg() utility function
- selftests/bpf: track string payload offset as scalar in strobemeta
- selftests/bpf: track tcp payload offset as scalar in xdp_synproxy
- bpf: print full verifier states on infinite loop detection
- selftests/bpf: test if state loops are detected in a tricky case
- bpf: correct loop detection for iterators convergence
- selftests/bpf: tests with delayed read/precision makrs in loop body
- bpf: exact states comparison for iterator convergence checks
- bpf: extract same_callsites() as utility function
- bpf: move explored_state() closer to the beginning of verifier.c
- dt-bindings: net: snps,dwmac: Tx coe unsupported
- ksmbd: Add missing set_freezable() for freezable kthread
- ksmbd: send lease break notification on FILE_RENAME_INFORMATION
- ksmbd: don't increment epoch if current state and request state are same
- ksmbd: fix potential circular locking issue in smb2_set_ea()
- ksmbd: set v2 lease version on lease upgrade
- serial: Do not hold the port lock when setting rx-during-tx GPIO
- mm: page_alloc: unreserve highatomic page blocks before oom
- LoongArch/smp: Call rcutree_report_cpu_starting() earlier
- serial: sc16is7xx: improve do/while loop in sc16is7xx_irq()
- serial: sc16is7xx: remove obsolete loop in sc16is7xx_port_irq()
- serial: sc16is7xx: fix invalid sc16is7xx_lines bitfield in case of probe error
- serial: sc16is7xx: convert from _raw_ to _noinc_ regmap functions for FIFO
- serial: sc16is7xx: change EFR lock to operate on each channels
- serial: sc16is7xx: remove unused line structure member
- serial: sc16is7xx: remove global regmap from struct sc16is7xx_port
- serial: sc16is7xx: remove wasteful static buffer in sc16is7xx_regmap_name()
- serial: sc16is7xx: improve regmap debugfs by using one regmap per port
- rename(): fix the locking of subdirectories
- mm/sparsemem: fix race in accessing memory_section->usage
- mm/rmap: fix misplaced parenthesis of a likely()
- selftests: mm: hugepage-vmemmap fails on 64K page size systems
- kexec: do syscore_shutdown() in kernel_kexec
- ubifs: ubifs_symlink: Fix memleak of inode->i_link in error path
- nouveau/vmm: don't set addr on the fail path to avoid warning
- rtc: Extend timeout for waiting for UIP to clear to 1s
- rtc: Add support for configuring the UIP timeout for RTC reads
- rtc: mc146818-lib: Adjust failure return code for mc146818_get_time()
- rtc: Adjust failure return code for cmos_set_alarm()
- rtc: cmos: Use ACPI alarm for non-Intel x86 systems too
- arm64: entry: fix ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD
- arm64/sme: Always exit sme_alloc() early with existing storage
- arm64: errata: Add Cortex-A510 speculative unprivileged load workaround
- arm64: Rename ARM64_WORKAROUND_2966298
- riscv: mm: Fixup compat mode boot failure
- riscv: mm: Fixup compat arch_get_mmap_end
- media: mtk-jpeg: Fix use after free bug due to error path handling in mtk_jpeg_dec_device_run
- media: mtk-jpeg: Fix timeout schedule error in mtk_jpegdec_worker.
- media: i2c: st-mipid02: correct format propagation
- mmc: mmc_spi: remove custom DMA mapped buffers
- mmc: core: Use mrq.sbc in close-ended ffu
- media: videobuf2-dma-sg: fix vmap callback
- scripts/get_abi: fix source path leak
- docs: kernel_abi.py: fix command injection
- dlm: use kernel_connect() and kernel_bind()
- lsm: new security_file_ioctl_compat() hook
- ARM: dts: qcom: sdx55: fix USB SS wakeup
- arm64: dts: qcom: sdm670: fix USB SS wakeup
- arm64: dts: qcom: sdm670: fix USB DP/DM HS PHY interrupts
- arm64: dts: qcom: sc8180x: fix USB SS wakeup
- arm64: dts: qcom: sc8180x: fix USB DP/DM HS PHY interrupts
- arm64: dts: qcom: sm8150: fix USB SS wakeup
- arm64: dts: qcom: sm8150: fix USB DP/DM HS PHY interrupts
- arm64: dts: qcom: sdm845: fix USB SS wakeup
- arm64: dts: qcom: sdm845: fix USB DP/DM HS PHY interrupts
- ARM: dts: qcom: sdx55: fix USB DP/DM HS PHY interrupts
- arm64: dts: qcom: Add missing vio-supply for AW2013
- arm64: dts: qcom: sc7280: fix usb_1 wakeup interrupt types
- arm64: dts: qcom: sc8180x: fix USB wakeup interrupt types
- arm64: dts: qcom: sm8150: fix USB wakeup interrupt types
- arm64: dts: qcom: sdm670: fix USB wakeup interrupt types
- arm64: dts: qcom: sdm845: fix USB wakeup interrupt types
- arm64: dts: qcom: sc7180: fix USB wakeup interrupt types
- arm64: dts: qcom: msm8939: Make blsp_dma controlled-remotely
- arm64: dts: qcom: msm8916: Make blsp_dma controlled-remotely
- arm64: dts: rockchip: Fix rk3588 USB power-domain clocks
- arm64: dts: rockchip: configure eth pad driver strength for orangepi r1 plus lts
- arm64: dts: sprd: fix the cpu node for UMS512
- ARM: dts: qcom: sdx55: fix pdc '#interrupt-cells'
- ARM: dts: samsung: exynos4210-i9100: Unconditionally enable LDO12
- ARM: dts: qcom: sdx55: fix USB wakeup interrupt types
- arm64: dts: qcom: sc8280xp-crd: fix eDP phy compatible
- ARM: dts: imx6q-apalis: add can power-up delay on ixora board
- parisc/power: Fix power soft-off button emulation on qemu
- parisc/firmware: Fix F-extend for PDC addresses
- bus: mhi: host: Add spinlock to protect WP access when queueing TREs
- bus: mhi: host: Drop chan lock before queuing buffers
- bus: mhi: host: Add alignment check for event ring read pointer
- mips: Fix max_mapnr being uninitialized on early stages
- nbd: always initialize struct msghdr completely
- s390/vfio-ap: do not reset queue removed from host config
- s390/vfio-ap: reset queues associated with adapter for queue unbound from driver
- s390/vfio-ap: reset queues filtered from the guest's AP config
- s390/vfio-ap: let on_scan_complete() callback filter matrix and update guest's APCB
- s390/vfio-ap: loop over the shadow APCB when filtering guest's AP configuration
- soc: fsl: cpm1: qmc: Fix rx channel reset
- soc: fsl: cpm1: qmc: Fix __iomem addresses declaration
- soc: fsl: cpm1: tsa: Fix __iomem addresses declaration
- media: ov01a10: Enable runtime PM before registering async sub-device
- media: ov13b10: Enable runtime PM before registering async sub-device
- media: ov9734: Enable runtime PM before registering async sub-device
- rpmsg: virtio: Free driver_override when rpmsg_remove()
- media: imx355: Enable runtime PM before registering async sub-device
- soc: qcom: pmic_glink_altmode: fix port sanity check
- mtd: rawnand: Clarify conditions to enable continuous reads
- mtd: rawnand: Prevent sequential reads with on-die ECC engines
- mtd: rawnand: Fix core interference with sequential reads
- mtd: rawnand: Prevent crossing LUN boundaries during sequential reads
- mtd: maps: vmu-flash: Fix the (mtd core) switch to ref counters
- PM / devfreq: Fix buffer overflow in trans_stat_show
- s390/vfio-ap: unpin pages on gisc registration failure
- crypto: s390/aes - Fix buffer overread in CTR mode
- hwrng: core - Fix page fault dead lock on mmap-ed hwrng
- PM: hibernate: Enforce ordering during image compression/decompression
- crypto: api - Disallow identical driver names
- crypto: lib/mpi - Fix unexpected pointer access in mpi_ec_init
- btrfs: sysfs: validate scrub_speed_max value
- OPP: Pass rounded rate to _set_opp()
- arm64: properly install vmlinuz.efi
- PM: sleep: Fix possible deadlocks in core system-wide PM code
- async: Introduce async_schedule_dev_nocall()
- async: Split async_schedule_node_domain()
- ext4: allow for the last group to be marked as trimmed
- powerpc/ps3_defconfig: Disable PPC64_BIG_ENDIAN_ELF_ABI_V2
- cifs: update iface_last_update on each query-and-update
- cifs: handle servers that still advertise multichannel after disabling
- cifs: reconnect worker should take reference on server struct unconditionally
- Revert "cifs: reconnect work should have reference on server struct"
- cifs: handle when server stops supporting multichannel
- cifs: handle when server starts supporting multichannel
- cifs: reconnect work should have reference on server struct
- cifs: handle cases where a channel is closed
- smb: client: fix parsing of SMB3.1.1 POSIX create context
- sh: ecovec24: Rename missed backlight field from fbdev to dev
- scsi: core: Kick the requeue list after inserting when flushing
- riscv: Fix an off-by-one in get_early_cmdline()
- scsi: ufs: core: Remove the ufshcd_hba_exit() call from ufshcd_async_scan()
- dmaengine: idxd: Move dma_free_coherent() out of spinlocked context
- dmaengine: fix NULL pointer in channel unregistration function
- dmaengine: fsl-edma: fix eDMAv4 channel allocation issue
- iio: adc: ad7091r: Enable internal vref if external vref is not supplied
- iio: adc: ad7091r: Allow users to configure device events
- iio: adc: ad7091r: Set alert bit in config register
- net: stmmac: Prevent DSA tags from breaking COE
- net: stmmac: Tx coe sw fallback
- soundwire: fix initializing sysfs for same devices on different buses
- soundwire: bus: introduce controller_id
- serial: core: set missing supported flag for RX during TX GPIO
- serial: core: Simplify uart_get_rs485_mode()
- docs: kernel_feat.py: fix potential command injection
- docs: sparse: add sparse.rst to toctree
- docs: sparse: move TW sparse.txt to TW dev-tools
- Revert "Revert "md/raid5: Wait for MD_SB_CHANGE_PENDING in raid5d""
- arm64: dts: armada-3720-turris-mox: set irq type for RTC
- Revert "KEYS: encrypted: Add check for strsep"
- riscv: Fix wrong usage of lm_alias() when splitting a huge linear mapping
- i2c: s3c24xx: fix transferring more than one message in polling mode
- i2c: s3c24xx: fix read transfers in polling mode
- ipv6: mcast: fix data-race in ipv6_mc_down / mld_ifc_work
- selftests: mlxsw: qos_pfc: Adjust the test to support 8 lanes
- mlxsw: spectrum_router: Register netdevice notifier before nexthop
- mlxsw: spectrum_acl_tcam: Fix stack corruption
- mlxsw: spectrum_acl_tcam: Fix NULL pointer dereference in error path
- mlxsw: spectrum_acl_erp: Fix error flow of pool allocation failure
- loop: fix the the direct I/O support check when used on top of block devices
- ethtool: netlink: Add missing ethnl_ops_begin/complete
- arm64/ptrace: Don't flush ZA/ZT storage when writing ZA via ptrace
- kdb: Fix a potential buffer overflow in kdb_local()
- io_uring: adjust defer tw counting
- ipvs: avoid stat macros calls from preemptible context
- netfilter: nf_tables: reject NFT_SET_CONCAT with not field length description
- netfilter: nf_tables: skip dead set elements in netlink dump
- netfilter: nf_tables: do not allow mismatch field size and set key length
- netfilter: bridge: replace physindev with physinif in nf_bridge_info
- netfilter: propagate net to nf_bridge_get_physindev
- netfilter: nf_queue: remove excess nf_bridge variable
- netfilter: nfnetlink_log: use proper helper for fetching physinif
- netfilter: nft_limit: do not ignore unsupported flags
- netfilter: nf_tables: reject invalid set policy
- net: netdevsim: don't try to destroy PHC on VFs
- mptcp: relax check on MPC passive fallback
- LoongArch: BPF: Prevent out-of-bounds memory access
- net: dsa: vsc73xx: Add null pointer check to vsc73xx_gpio_probe
- bpf: Reject variable offset alu on PTR_TO_FLOW_KEYS
- net: stmmac: ethtool: Fixed calltrace caused by unbalanced disable_irq_wake calls
- selftests: bonding: Change script interpreter
- drm/amdgpu: fall back to INPUT power for AVG power via INFO IOCTL
- drm/amdkfd: fixes for HMM mem allocation
- ASoC: SOF: ipc4-loader: remove the CPC check warnings
- gpio: mlxbf3: add an error code check in mlxbf3_gpio_probe
- dt-bindings: gpio: xilinx: Fix node address in gpio
- net: ravb: Fix dma_addr_t truncation in error case
- net: tls, fix WARNIING in __sk_msg_free
- bpf: Avoid iter->offset making backward progress in bpf_iter_udp
- bpf: iter_udp: Retry with a larger batch size without going back to the previous bucket
- net: netdev_queue: netdev_txq_completed_mb(): fix wake condition
- net: add more sanity check in virtio_net_hdr_to_skb()
- udp: annotate data-races around up->pending
- net: stmmac: Fix ethool link settings ops for integrated PCS
- block: ensure we hold a queue reference when using queue limits
- mptcp: refine opt_mp_capable determination
- mptcp: use OPTION_MPTCP_MPJ_SYN in subflow_check_req()
- mptcp: use OPTION_MPTCP_MPJ_SYNACK in subflow_finish_connect()
- mptcp: strict validation before using mp_opt->hmac
- mptcp: mptcp_parse_option() fix for MPTCPOPT_MP_JOIN
- ALSA: hda: Properly setup HDMI stream
- net: phy: micrel: populate .soft_reset for KSZ9131
- net: micrel: Fix PTP frame parsing for lan8841
- amt: do not use overwrapped cb area
- net: ethernet: ti: am65-cpsw: Fix max mtu to fit ethernet frames
- octeontx2-af: CN10KB: Fix FIFO length calculation for RPM2
- rxrpc: Fix use of Don't Fragment flag
- net: qualcomm: rmnet: fix global oob in rmnet_policy
- s390/pci: fix max size calculation in zpci_memcpy_toio()
- ASoC: mediatek: sof-common: Add NULL check for normal_link string
- PCI: mediatek-gen3: Fix translation window size calculation
- PCI: keystone: Fix race condition when initializing PHYs
- nvmet-tcp: Fix the H2C expected PDU len calculation
- nvme: trace: avoid memcpy overflow warning
- nvmet: re-fix tracing strncpy() warning
- hisi_acc_vfio_pci: Update migration data pointer correctly on saving/resume
- spi: coldfire-qspi: Remove an erroneous clk_disable_unprepare() from the remove function
- cxl/port: Fix missing target list lock
- perf db-export: Fix missing reference count get in call_path_from_sample()
- serial: apbuart: fix console prompt on qemu
- serial: imx: Correct clock error message in function probe()
- usb: xhci-mtk: fix a short packet issue of gen1 isoc-in transfer
- apparmor: avoid crash when parsed profile name is empty
- apparmor: fix possible memory leak in unpack_trans_table
- cxl/region: fix x9 interleave typo
- perf stat: Fix hard coded LL miss units
- perf env: Avoid recursively taking env->bpf_progs.lock
- nvmet-tcp: fix a crash in nvmet_req_complete()
- nvmet-tcp: Fix a kernel panic when host sends an invalid H2C PDU length
- apparmor: Fix ref count leak in task_kill
- vdpa: Fix an error handling path in eni_vdpa_probe()
- power: supply: Fix null pointer dereference in smb2_probe
- usb: gadget: webcam: Make g_webcam loadable again
- spmi: mtk-pmif: Serialize PMIF status check and command submission
- usb: cdc-acm: return correct error code on unsupported break
- tty: use 'if' in send_break() instead of 'goto'
- tty: don't check for signal_pending() in send_break()
- tty: early return from send_break() on TTY_DRIVER_HARDWARE_BREAK
- PCI: epf-mhi: Fix the DMA data direction of dma_unmap_single()
- bus: mhi: ep: Pass mhi_ep_buf_info struct to read/write APIs
- bus: mhi: ep: Use slab allocator where applicable
- bus: mhi: ep: Do not allocate event ring element on stack
- perf unwind-libunwind: Fix base address for .eh_frame
- perf unwind-libdw: Handle JIT-generated DSOs properly
- perf genelf: Set ELF program header addresses properly
- perf header: Fix one memory leakage in perf_event__fprintf_event_update()
- iio: adc: ad9467: fix scale setting
- iio: adc: ad9467: add mutex to struct ad9467_state
- iio: adc: ad9467: don't ignore error codes
- iio: adc: ad9467: fix reset gpio handling
- selftests/sgx: Skip non X86_64 platform
- selftests/sgx: Include memory clobber for inline asm in test enclave
- selftests/sgx: Fix uninitialized pointer dereferences in encl_get_entry
- selftests/sgx: Fix uninitialized pointer dereference in error path
- serial: imx: fix tx statemachine deadlock
- software node: Let args be NULL in software_node_get_reference_args
- acpi: property: Let args be NULL in __acpi_node_get_property_reference
- base/node.c: initialize the accessor list before registering
- perf stat: Exit perf stat if parse groups fails
- perf mem: Fix error on hybrid related to availability of mem event in a PMU
- perf vendor events arm64 AmpereOne: Rename BPU_FLUSH_MEM_FAULT to GPC_FLUSH_MEM_FAULT
- vfio/pds: Fix calculations in pds_vfio_dirty_sync
- perf test record user-regs: Fix mask for vg register
- libapi: Add missing linux/types.h header to get the __u64 type on io.h
- perf header: Fix segfault on build_mem_topology() error path
- perf test: Remove atomics from test_loop to avoid test failures
- power: supply: bq256xx: fix some problem in bq256xx_hw_init
- power: supply: cw2015: correct time_to_empty units in sysfs
- MIPS: Alchemy: Fix an out-of-bound access in db1550_dev_setup()
- MIPS: Alchemy: Fix an out-of-bound access in db1200_dev_setup()
- riscv: Fixed wrong register in XIP_FIXUP_FLASH_OFFSET macro
- riscv: Fix set_direct_map_default_noflush() to reset _PAGE_EXEC
- riscv: Fix set_memory_XX() and set_direct_map_XX() by splitting huge linear mappings
- riscv: Fix module_alloc() that did not reset the linear mapping permissions
- riscv: Check if the code to patch lies in the exit section
- um: virt-pci: fix platform map offset
- mips: Fix incorrect max_low_pfn adjustment
- mips: dmi: Fix early remap on MIPS32
- srcu: Use try-lock lockdep annotation for NMI-safe access.
- mfd: intel-lpss: Fix the fractional clock divider flags
- mfd: tps6594: Add null pointer check to tps6594_device_init()
- leds: aw200xx: Fix write to DIM parameter
- leds: aw2013: Select missing dependency REGMAP_I2C
- mfd: syscon: Fix null pointer dereference in of_syscon_register()
- mfd: cs42l43: Correct SoundWire port list
- mfd: rk8xx: fixup devices registration with PLATFORM_DEVID_AUTO
- ARM: 9330/1: davinci: also select PINCTRL
- serial: sc16is7xx: set safe default SPI clock frequency
- serial: sc16is7xx: add check for unsupported SPI modes during probe
- HID: wacom: Correct behavior when processing some confidence == false touches
- HID: sensor-hub: Enable hid core report processing for all devices
- iio: adc: ad7091r: Pass iio_dev to event handler
- KVM: x86/pmu: Reset the PMU, i.e. stop counters, before refreshing
- KVM: x86/pmu: Move PMU reset logic to common x86 code
- KVM: arm64: vgic-its: Avoid potential UAF in LPI translation cache
- x86/kvm: Do not try to disable kvmclock if it was not enabled
- PCI: mediatek: Clear interrupt status before dispatching handler
- PCI: dwc: endpoint: Fix dw_pcie_ep_raise_msix_irq() alignment support
- x86/pci: Reserve ECAM if BIOS didn't include it in PNP0C02 _CRS
- PCI/P2PDMA: Remove reference to pci_p2pdma_map_sg()
- cxl/port: Fix decoder initialization when nr_targets > interleave_ways
- Revert "nSVM: Check for reserved encodings of TLB_CONTROL in nested VMCB"
- Revert "net: rtnetlink: Enslave device before bringing it up"
- net: stmmac: fix ethtool per-queue statistics
- wifi: mwifiex: fix uninitialized firmware_stat
- wifi: mwifiex: configure BSSID consistently when starting AP
- wifi: mwifiex: add extra delay for firmware ready
- wifi: rtlwifi: Convert LNKCTL change to PCIe cap RMW accessors
- wifi: rtlwifi: Remove bogus and dangerous ASPM disable/enable code
- wifi: mt76: fix broken precal loading from MTD for mt7915
- iommu/arm-smmu-qcom: Add missing GMU entry to match table
- bpf: Fix re-attachment branch in bpf_tracing_prog_attach
- Bluetooth: Fix atomicity violation in {min,max}_key_size_set
- md/raid1: Use blk_opf_t for read and write operations
- pwm: Fix out-of-bounds access in of_pwm_single_xlate()
- pwm: jz4740: Don't use dev_err_probe() in .request()
- netfilter: nf_tables: check if catch-all set element is active in next generation
- block: Fix iterating over an empty bio with bio_for_each_folio_all
- block: Remove special-casing of compound pages
- drm/amd: Enable PCIe PME from D3
- scsi: mpi3mr: Block PEL Enable Command on Controller Reset and Unrecoverable State
- scsi: mpi3mr: Clean up block devices post controller reset
- scsi: mpi3mr: Refresh sdev queue depth after controller reset
- scsi: target: core: add missing file_{start,end}_write()
- scsi: ufs: core: Simplify power management during async scan
- fbdev: flush deferred IO before closing
- fbdev: flush deferred work in fb_deferred_io_fsync()
- fbdev/acornfb: Fix name of fb_ops initializer macro
- io_uring: ensure local task_work is run on wait timeout
- io_uring/rw: ensure io->bytes_done is always initialized
- io_uring: don't check iopoll if request completes
- LoongArch: Fix and simplify fcsr initialization on execve()
- ceph: select FS_ENCRYPTION_ALGS if FS_ENCRYPTION
- ksmbd: only v2 leases handle the directory
- ksmbd: fix UAF issue in ksmbd_tcp_new_connection()
- ksmbd: validate mech token in session setup
- ALSA: hda/realtek: Enable headset mic on Lenovo M70 Gen5
- ALSA: hda/realtek: Enable mute/micmute LEDs and limit mic boost on HP ZBook
- ALSA: hda/relatek: Enable Mute LED on HP Laptop 15s-fq2xxx
- ALSA: oxygen: Fix right channel of capture volume mixer
- serial: omap: do not override settings for RS485 support
- serial: 8250_exar: Set missing rs485_supported flag
- serial: imx: Ensure that imx_uart_rs485_config() is called with enabled clock
- serial: core, imx: do not set RS485 enabled if it is not supported
- serial: 8250_bcm2835aux: Restore clock error handling
- serial: core: make sure RS485 cannot be enabled when it is not supported
- serial: core: fix sanitizing check for RTS settings
- dt-bindings: phy: qcom,sc8280xp-qmp-usb43dp-phy: fix path to header
- usb: mon: Fix atomicity violation in mon_bin_vma_fault
- usb: typec: class: fix typec_altmode_put_partner to put plugs
- Revert "usb: typec: class: fix typec_altmode_put_partner to put plugs"
- usb: cdns3: Fix uvc fail when DMA cross 4k boundery since sg enabled
- usb: cdns3: fix iso transfer error when mult is not zero
- usb: cdns3: fix uvc failure work since sg support enabled
- usb: chipidea: wait controller resume finished for wakeup irq
- Revert "usb: dwc3: don't reset device side if dwc3 was configured as host-only"
- Revert "usb: dwc3: Soft reset phy on probe for host"
- usb: dwc3: gadget: Queue PM runtime idle on disconnect event
- usb: dwc3: gadget: Handle EP0 request dequeuing properly
- usb: dwc: ep0: Update request status in dwc3_ep0_stall_restart
- usb: phy: mxs: remove CONFIG_USB_OTG condition for mxs_phy_is_otg_host()
- Revert "usb: gadget: f_uvc: change endpoint allocation in uvc_function_bind()"
- tick-sched: Fix idle and iowait sleeptime accounting vs CPU hotplug
- powerpc/64s: Increase default stack size to 32KB
- clocksource/drivers/timer-ti-dm: Fix make W=n kerneldoc warnings
- binder: fix race between mmput() and do_exit()
- xen-netback: don't produce zero-size SKB frags
- Revert "drm/amdkfd: Relocate TBA/TMA to opposite side of VM hole"
- rust: Ignore preserve-most functions
- Input: atkbd - use ab83 as id when skipping the getid command
- mips/smp: Call rcutree_report_cpu_starting() earlier
- binder: fix unused alloc->free_async_space
- binder: fix async space check for 0-sized buffers
- keys, dns: Fix size check of V1 server-list header
- selftests/bpf: Add assert for user stacks in test_task_stack
- Revert "kernfs: convert kernfs_idr_lock to an irq safe raw spinlock"
- kernfs: convert kernfs_idr_lock to an irq safe raw spinlock
- class: fix use-after-free in class_register()
- of: unittest: Fix of_count_phandle_with_args() expected value message
- fbdev: imxfb: fix left margin setting
- of: Fix double free in of_parse_phandle_with_args_map
- ksmbd: validate the zero field of packet header
- kselftest/alsa - conf: Stringify the printed errno in sysfs_get()
- kselftest/alsa - mixer-test: Fix the print format specifier warning
- kselftest/alsa - mixer-test: fix the number of parameters to ksft_exit_fail_msg()
- drm/amd/display: avoid stringop-overflow warnings for dp_decide_lane_settings()
- drm/amd/pm/smu7: fix a memleak in smu7_hwmgr_backend_init
- drm/amdkfd: Confirm list is non-empty before utilizing list_first_entry in kfd_topology.c
- IB/iser: Prevent invalidating wrong MR
- gpio: sysfs: drop the mention of gpiochip_find() from sysfs code
- gpiolib: provide gpio_device_find()
- gpiolib: make gpio_device_get() and gpio_device_put() public
- drm/amdkfd: Fix type of 'dbg_flags' in 'struct kfd_process'
- mmc: sdhci_omap: Fix TI SoC dependencies
- mmc: sdhci_am654: Fix TI SoC dependencies
- ALSA: scarlett2: Add clamp() in scarlett2_mixer_ctl_put()
- ALSA: scarlett2: Add missing error checks to *_ctl_get()
- ALSA: scarlett2: Allow passing any output to line_out_remap()
- ALSA: scarlett2: Add missing error check to scarlett2_usb_set_config()
- ALSA: scarlett2: Add missing error check to scarlett2_config_save()
- ASoC: rt5645: Drop double EF20 entry from dmi_platform_data[]
- pwm: stm32: Fix enable count for clk in .probe()
- pwm: stm32: Use hweight32 in stm32_pwm_detect_channels
- clk: fixed-rate: fix clk_hw_register_fixed_rate_with_accuracy_parent_hw
- clk: qcom: dispcc-sm8550: Update disp PLL settings
- clk: qcom: gcc-sm8550: Mark RCGs shared where applicable
- clk: qcom: gcc-sm8550: use collapse-voting for PCIe GDSCs
- clk: qcom: gcc-sm8550: Mark the PCIe GDSCs votable
- clk: qcom: gcc-sm8550: Add the missing RETAIN_FF_ENABLE GDSC flag
- accel/habanalabs: fix information leak in sec_attest_info()
- drm/mediatek: dp: Add phy_mtk_dp module as pre-dependency
- ASoC: tas2781: add support for FW version 0x0503
- ASoC: amd: vangogh: Drop conflicting ACPI-based probing
- clk: si5341: fix an error code problem in si5341_output_clk_set_rate
- clk: rs9: Fix DIF OEn bit placement on 9FGV0241
- watchdog: rti_wdt: Drop runtime pm reference count when watchdog is unused
- watchdog: bcm2835_wdt: Fix WDIOC_SETTIMEOUT handling
- watchdog/hpwdt: Only claim UNKNOWN NMI if from iLO
- watchdog: set cdev owner before adding
- drivers: clk: zynqmp: update divider round rate logic
- drivers: clk: zynqmp: calculate closest mux rate
- clk: sp7021: fix return value check in sp7021_clk_probe()
- clk: qcom: videocc-sm8150: Add missing PLL config property
- clk: qcom: videocc-sm8150: Update the videocc resets
- dt-bindings: clock: Update the videocc resets for sm8150
- f2fs: fix to check return value of f2fs_recover_xattr_data
- drm/amd/pm: fix a double-free in amdgpu_parse_extended_power_table
- gpu/drm/radeon: fix two memleaks in radeon_vm_init
- drivers/amd/pm: fix a use-after-free in kv_parse_power_table
- drm/amd/pm: fix a double-free in si_dpm_init
- drm/amdgpu/debugfs: fix error code when smc register accessors are NULL
- drm/mediatek: Fix underrun in VDO1 when switches off the layer
- drm/mediatek: Remove the redundant driver data for DPI
- drm/mediatek: Return error if MDP RDMA failed to enable the clock
- drm/msm/dpu: Drop enable and frame_count parameters from dpu_hw_setup_misr()
- drm/msm/dpu: Set input_sel bit for INTF
- clk: renesas: rzg2l: Check reset monitor registers
- clk: renesas: rzg2l-cpg: Reuse code in rzg2l_cpg_reset()
- media: dvb-frontends: m88ds3103: Fix a memory leak in an error handling path of m88ds3103_probe()
- media: dvbdev: drop refcount on error path in dvb_device_open()
- f2fs: fix to update iostat correctly in f2fs_filemap_fault()
- f2fs: fix to check compress file in f2fs_move_file_range()
- f2fs: fix to wait on block writeback for post_read case
- drm/panel: st7701: Fix AVCL calculation
- drm/msm/adreno: Fix A680 chip id
- media: rkisp1: Fix media device memory leak
- media: dt-bindings: media: rkisp1: Fix the port description for the parallel interface
- media: imx-mipi-csis: Drop extra clock enable at probe()
- media: imx-mipi-csis: Fix clock handling in remove()
- media: bttv: add back vbi hack
- media: bttv: start_streaming should return a proper error code
- clk: qcom: gpucc-sm8150: Update the gpu_cc_pll1 config
- media: cx231xx: fix a memleak in cx231xx_init_isoc
- drm/bridge: tc358767: Fix return value on error case
- drm/bridge: cdns-mhdp8546: Fix use of uninitialized variable
- drm/radeon/trinity_dpm: fix a memleak in trinity_parse_power_table
- drm/radeon/dpm: fix a memleak in sumo_parse_power_table
- drm/msm/dpu: correct clk bit for WB2 block
- drm/panfrost: Ignore core_mask for poweroff and disable PWRTRANS irq
- ASoC: SOF: topology: Use partial match for disconnecting DAI link and DAI widget
- ASoC: Intel: sof_sdw_rt_sdca_jack_common: ctx->headset_codec_dev = NULL
- ASoC: Intel: glk_rt5682_max98357a: fix board id mismatch
- media: v4l: async: Fix duplicated list deletion
- drm/drv: propagate errors from drm_modeset_register_all()
- drm/msm/dsi: Use pm_runtime_resume_and_get to prevent refcnt leaks
- drm/msm/dpu: Add missing safe_lut_tbl in sc8180x catalog
- drm/msm/mdp4: flush vblank event on disable
- ASoC: cs35l33: Fix GPIO name and drop legacy include
- drm/imx/lcdc: Fix double-free of driver data
- drm/tidss: Fix dss reset
- drm/tidss: Check for K2G in in dispc_softreset()
- drm/tidss: Return error value from from softreset
- drm/tidss: Move reset to the end of dispc_init()
- drm/radeon: check return value of radeon_ring_lock()
- drm/radeon/r100: Fix integer overflow issues in r100_cs_track_check()
- drm/radeon/r600_cs: Fix possible int overflows in r600_cs_check_reg()
- drm/bridge: Fix typo in post_disable() description
- media: amphion: Fix VPU core alias name
- media: rkvdec: Hook the (TRY_)DECODER_CMD stateless ioctls
- media: verisilicon: Hook the (TRY_)DECODER_CMD stateless ioctls
- media: visl: Hook the (TRY_)DECODER_CMD stateless ioctls
- media: mtk-jpeg: Remove cancel worker in mtk_jpeg_remove to avoid the crash of multi-core JPEG devices
- media: pvrusb2: fix use after free on context disconnection
- drm/tilcdc: Fix irq free on unload
- drm/bridge: tpd12s015: Drop buggy __exit annotation for remove function
- drm/nouveau/fence:: fix warning directly dereferencing a rcu pointer
- drm/panel-elida-kd35t133: hold panel in reset for unprepare
- drm/panel: nv3051d: Hold panel in reset for unprepare
- RDMA/usnic: Silence uninitialized symbol smatch warnings
- drm/panfrost: Really power off GPU cores in panfrost_gpu_power_off()
- drm/dp_mst: Fix fractional DSC bpp handling
- Revert "drm/omapdrm: Annotate dma-fence critical section in commit path"
- Revert "drm/tidss: Annotate dma-fence critical section in commit path"
- ARM: davinci: always select CONFIG_CPU_ARM926T
- ip6_tunnel: fix NEXTHDR_FRAGMENT handling in ip6_tnl_parse_tlv_enc_lim()
- rxrpc: Fix skbuff cleanup of call's recvmsg_queue and rx_oos_queue
- mlxbf_gige: Enable the GigE port in mlxbf_gige_open
- mlxbf_gige: Fix intermittent no ip issue
- net/sched: act_ct: fix skb leak and crash on ooo frags
- blk-cgroup: fix rcu lockdep warning in blkg_lookup()
- sctp: fix busy polling
- sctp: support MSG_ERRQUEUE flag in recvmsg()
- bpf: sockmap, fix proto update hook to avoid dup calls
- wifi: cfg80211: parse all ML elements in an ML probe response
- wifi: cfg80211: correct comment about MLD ID
- arm64: dts: rockchip: Fix led pinctrl of lubancat 1
- null_blk: don't cap max_hw_sectors to BLK_DEF_MAX_SECTORS
- Bluetooth: btmtkuart: fix recv_buf() return value
- Bluetooth: btnxpuart: fix recv_buf() return value
- Bluetooth: Fix bogus check for re-auth no supported with non-ssp
- netfilter: nf_tables: validate chain type update if available
- netfilter: nf_tables: mark newset as dead on transaction abort
- wifi: iwlwifi: assign phy_ctxt before eSR activation
- wifi: iwlwifi: fix out of bound copy_from_user
- wifi: iwlwifi: mvm: send TX path flush in rfkill
- wifi: iwlwifi: mvm: set siso/mimo chains to 1 in FW SMPS request
- wifi: rtlwifi: rtl8192se: using calculate_bit_shift()
- wifi: rtlwifi: rtl8192ee: using calculate_bit_shift()
- wifi: rtlwifi: rtl8192de: using calculate_bit_shift()
- wifi: rtlwifi: rtl8192ce: using calculate_bit_shift()
- wifi: rtlwifi: rtl8192cu: using calculate_bit_shift()
- wifi: rtlwifi: rtl8192c: using calculate_bit_shift()
- wifi: rtlwifi: rtl8188ee: phy: using calculate_bit_shift()
- wifi: rtlwifi: add calculate_bit_shift()
- bpf: Use c->unit_size to select target cache during free
- bpf: Use pcpu_alloc_size() in bpf_mem_free{_rcu}()
- bpf: Re-enable unit_size checking for global per-cpu allocator
- arm64: dts: qcom: sc8180x: Fix up PCIe nodes
- arm64: dts: qcom: sc8180x: switch PCIe QMP PHY to new style of bindings
- arm64: dts: qcom: sc8180x: Mark PCIe hosts cache-coherent
- arm64: dts: qcom: sm8550: Update idle state time requirements
- arm64: dts: qcom: sm8550: Separate out X3 idle state
- arm64: dts: qcom: ipq6018: fix clock rates for GCC_USB0_MOCK_UTMI_CLK
- arm64: dts: qcom: sc7280: Mark SDHCI hosts as cache-coherent
- soc: qcom: llcc: Fix LLCC_TRP_ATTR2_CFGn offset
- arm64: dts: qcom: sm8150-hdk: fix SS USB regulators
- arm64: dts: qcom: sm8150: make dispcc cast minimal vote on MMCX
- arm64: dts: qcom: sm6375: Hook up MPM
- arm64: dts: qcom: sm6375: fix USB wakeup interrupt types
- soc: qcom: llcc: Fix dis_cap_alloc and retain_on_pc configuration
- arm64: dts: qcom: acer-aspire1: Correct audio codec definition
- bpf: Limit the number of kprobes when attaching program to multiple kprobes
- bpf: Limit the number of uprobes when attaching program to multiple uprobes
- dma-mapping: clear dev->dma_mem to NULL after freeing it
- virtio/vsock: send credit update during setting SO_RCVLOWAT
- virtio/vsock: fix logic which reduces credit update messages
- ipmr: support IP_PKTINFO on cache report IGMP msg
- selftests/net: fix grep checking for fib_nexthop_multiprefix
- bpf: Fix a race condition between btf_put() and map_free()
- ARM: dts: stm32: don't mix SCMI and non-SCMI board compatibles
- scsi: hisi_sas: Correct the number of global debugfs registers
- scsi: hisi_sas: Rollback some operations if FLR failed
- scsi: hisi_sas: Check before using pointer variables
- scsi: hisi_sas: Replace with standard error code return value
- scsi: ufs: qcom: Fix the return value when platform_get_resource_byname() fails
- scsi: ufs: qcom: Fix the return value of ufs_qcom_ice_program_key()
- arm64: dts: imx8mm: Reduce GPU to nominal speed
- arm64: dts: renesas: white-hawk-cpu: Fix missing serial console pin control
- arm64: dts: xilinx: Apply overlays to base dtbs
- selftests/bpf: Relax time_tai test for equal timestamps in tai_forward
- wifi: iwlwifi: don't support triggered EHT CQI feedback
- wifi: mt76: mt7921: fix country count limitation for CLC
- arm64: dts: mediatek: mt8186: fix address warning for ADSP mailboxes
- arm64: dts: mediatek: mt8186: Fix alias prefix for ovl_2l0
- arm64: dts: mediatek: mt8195: revise VDOSYS RDMA node name
- arm64: dts: mediatek: mt8183: correct MDP3 DMA-related nodes
- dt-bindings: media: mediatek: mdp3: correct RDMA and WROT node with generic names
- bpf: Fix accesses to uninit stack slots
- bpf: Guard stack limits against 32bit overflow
- arm64: dts: hisilicon: hikey970-pmic: fix regulator cells properties
- bpf: Fix verification of indirect var-off stack access
- wifi: mt76: mt7921s: fix workqueue problem causes STA association fail
- wifi: mt76: mt7915: also MT7981 is 3T3R but nss2 on 5 GHz band
- wifi: mt76: mt7915: fix EEPROM offset of TSSI flag on MT7981
- wifi: mt76: mt7996: fix rate usage of inband discovery frames
- wifi: mt76: mt7996: fix the size of struct bss_rate_tlv
- wifi: mt76: mt7915: fallback to non-wed mode if platform_get_resource fails in mt7915_mmio_wed_init()
- wifi: mt76: fix typo in mt76_get_of_eeprom_from_nvmem function
- arm64: dts: qcom: sm8550: fix USB wakeup interrupt types
- arm64: dts: qcom: sc7280: fix usb_2 wakeup interrupt types
- arm64: dts: qcom: sa8775p: fix USB wakeup interrupt types
- arm64: dts: qcom: sc7280: Mark Adreno SMMU as DMA coherent
- arm64: dts: qcom: sc7280: Fix up GPU SIDs
- arm64: dts: qcom: sm8350: Fix DMA0 address
- arm64: dts: qcom: sm6125: add interrupts to DWC3 USB controller
- arm64: dts: qcom: sdm845-db845c: correct LED panic indicator
- arm64: dts: qcom: qrb5165-rb5: correct LED panic indicator
- arm64: dts: qcom: qrb2210-rb1: use USB host mode
- arm64: dts: qcom: qrb2210-rb1: Hook up USB3
- scsi: fnic: Return error if vmalloc() failed
- bpf: fix check for attempt to corrupt spilled pointer
- selftests/net: specify the interface when do arping
- bpf: Defer the free of inner map when necessary
- bpf: Add map and need_defer parameters to .map_fd_put_ptr()
- arm64: dts: qcom: sm6350: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sc8280xp: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sa8775p: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sm8250: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sm8150: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sdm845: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sc7280: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sc7280: Mark some nodes as 'reserved'
- arm64: dts: qcom: sc7180: Make watchdog bark interrupt edge triggered
- arm64: dts: qcom: sm8550: correct TX Soundwire clock
- arm64: dts: qcom: sm8450: correct TX Soundwire clock
- arm64: dts: qcom: sc8180x-primus: Fix HALL_INT polarity
- dt-bindings: arm: qcom: Fix html link
- ARM: dts: qcom: sdx65: correct SPMI node name
- ARM: dts: qcom: sdx65: correct PCIe EP phy-names
- bpf: enforce precision of R0 on callback return
- selftests/bpf: Fix erroneous bitmask operation
- wifi: rtw88: sdio: Honor the host max_req_size in the RX path
- arm64: dts: ti: iot2050: Re-add aliases
- arm64: dts: ti: k3-am65-main: Fix DSS irq trigger type
- arm64: dts: ti: k3-am62a-main: Fix GPIO pin count in DT nodes
- wifi: rtlwifi: rtl8821ae: phy: fix an undefined bitwise shift behavior
- scsi: bfa: Use the proper data type for BLIST flags
- firmware: ti_sci: Fix an off-by-one in ti_sci_debugfs_create()
- net/ncsi: Fix netlink major/minor version numbers
- ARM: dts: qcom: apq8064: correct XOADC register address
- wifi: libertas: stop selecting wext
- wifi: ath11k: Defer on rproc_get failure
- bpf: Add crosstask check to __bpf_get_stack
- bpf, lpm: Fix check prefixlen before walking trie
- wifi: rtw88: fix RX filter in FIF_ALLMULTI flag
- wifi: plfxlc: check for allocation failure in plfxlc_usb_wreq_async()
- ARM: dts: qcom: msm8226: provide dsi phy clocks to mmcc
- arm64: dts: qcom: sc8280xp-x13s: add missing camera LED pin config
- arm64: dts: qcom: sc8280xp-x13s: Use the correct DP PHY compatible
- arm64: dts: qcom: qrb4210-rb2: don't force usb peripheral mode
- asm-generic: Fix 32 bit __generic_cmpxchg_local
- pNFS: Fix the pnfs block driver's calculation of layoutget size
- SUNRPC: fix _xprt_switch_find_current_entry logic
- NFSv4.1/pnfs: Ensure we handle the error NFS4ERR_RETURNCONFLICT
- NFS: Use parent's objective cred in nfs_access_login_time()
- blocklayoutdriver: Fix reference leak of pnfs_device_node
- csky: fix arch_jump_label_transform_static override
- crypto: scomp - fix req->dst buffer overflow
- crypto: sahara - do not resize req->src when doing hash operations
- crypto: sahara - fix processing hash requests with req->nbytes < sg->length
- crypto: sahara - improve error handling in sahara_sha_process()
- crypto: sahara - fix wait_for_completion_timeout() error handling
- crypto: sahara - fix ahash reqsize
- crypto: sahara - handle zero-length aes requests
- crypto: sahara - avoid skcipher fallback code duplication
- crypto: virtio - Wait for tasklet to complete on device remove
- dlm: fix format seq ops type 4
- gfs2: fix kernel BUG in gfs2_quota_cleanup
- fs: indicate request originates from old mount API
- erofs: fix memory leak on short-lived bounced pages
- pstore: ram_core: fix possible overflow in persistent_ram_init_ecc()
- crypto: sahara - fix error handling in sahara_hw_descriptor_create()
- crypto: sahara - fix processing requests with cryptlen < sg->length
- crypto: sahara - fix ahash selftest failure
- crypto: sahara - fix cbc selftest failure
- crypto: sahara - remove FLAGS_NEW_KEY logic
- crypto: safexcel - Add error handling for dma_map_sg() calls
- crypto: af_alg - Disallow multiple in-flight AIO requests
- crypto: ccp - fix memleak in ccp_init_dm_workarea
- crypto: sa2ul - Return crypto_aead_setkey to transfer the error
- crypto: virtio - Handle dataq logic with tasklet
- crypto: jh7110 - Correct deferred probe return
- crypto: rsa - add a check for allocation failure
- selinux: Fix error priority for bind with AF_UNSPEC on PF_INET6 socket
- drivers/thermal/loongson2_thermal: Fix incorrect PTR_ERR() judgment
- cpuidle: haltpoll: Do not enable interrupts when entering idle
- kunit: debugfs: Fix unchecked dereference in debugfs_print_results()
- thermal: core: Fix NULL pointer dereference in zone registration error path
- ACPI: extlog: Clear Extended Error Log status when RAS_CEC handled the error
- ACPI: LPSS: Fix the fractional clock divider flags
- spi: sh-msiof: Enforce fixed DTDL for R-Car H3
- efivarfs: Free s_fs_info on unmount
- calipso: fix memory leak in netlbl_calipso_add_pass()
- cpufreq: scmi: process the result of devm_of_clk_add_hw_provider()
- platform/x86/intel/vsec: Fix xa_alloc memory leak
- spi: cadence-quadspi: add missing clk_disable_unprepare() in cqspi_probe()
- KEYS: encrypted: Add check for strsep
- ACPI: LPIT: Avoid u32 multiplication overflow
- ACPI: video: check for error while searching for backlight device parent
- mtd: rawnand: Increment IFC_TIMEOUT_MSECS for nand controller response
- spi: spi-zynqmp-gqspi: fix driver kconfig dependencies
- perf/x86/intel/uncore: Fix NULL pointer dereference issue in upi_fill_topology()
- sched/fair: Update min_vruntime for reweight_entity() correctly
- powerpc/imc-pmu: Add a null pointer check in update_events_in_group()
- powerpc/powernv: Add a null pointer check in opal_powercap_init()
- powerpc/powernv: Add a null pointer check in opal_event_init()
- powerpc/powernv: Add a null pointer check to scom_debug_init_one()
- powerpc/rtas: Avoid warning on invalid token argument to sys_rtas()
- powerpc/hv-gpci: Add return value check in affinity_domain_via_partition_show function
- selftests/powerpc: Fix error handling in FPU/VMX preemption tests
- KVM: PPC: Book3S HV: Handle pending exceptions on guest entry with MSR_EE
- KVM: PPC: Book3S HV: Introduce low level MSR accessor
- KVM: PPC: Book3S HV: Use accessors for VCPU registers
- drivers/perf: hisi: Fix some event id for HiSilicon UC pmu
- perf/arm-cmn: Fix HN-F class_occup_id events
- powerpc/pseries/memhp: Fix access beyond end of drmem array
- powerpc/44x: select I2C for CURRITUCK
- x86: Fix CPUIDLE_FLAG_IRQ_ENABLE leaking timer reprogram
- powerpc: add crtsavres.o to always-y instead of extra-y
- EDAC/thunderx: Fix possible out-of-bounds string access
- x86/mce/inject: Clear test status value
- x86/lib: Fix overflow when counting digits
- mm/memory_hotplug: fix memmap_on_memory sysfs value retrieval
- scripts/decode_stacktrace.sh: optionally use LLVM utilities
- coresight: etm4x: Fix width of CCITMIN field
- PCI: Add ACS quirk for more Zhaoxin Root Ports
- leds: ledtrig-tty: Free allocated ttyname buffer on deactivate
- parport: parport_serial: Add Brainboxes device IDs and geometry
- parport: parport_serial: Add Brainboxes BAR details
- uio: Fix use-after-free in uio_open
- binder: fix comment on binder_alloc_new_buf() return value
- binder: fix trivial typo of binder_free_buf_locked()
- binder: fix use-after-free in shinker's callback
- binder: use EPOLLERR from eventpoll.h
- ksmbd: free ppace array on error in parse_dacl
- ksmbd: don't allow O_TRUNC open on read-only share
- drm/amd/display: Pass pwrseq inst for backlight and ABM
- ASoC: SOF: Intel: hda-codec: Delay the codec device registration
- bus: moxtet: Add spi device table
- bus: moxtet: Mark the irq as shared
- ACPI: resource: Add another DMI match for the TongFang GMxXGxx
- ALSA: hda/realtek: Fix mute and mic-mute LEDs for HP Envy X360 13-ay0xxx
- drm/crtc: fix uninitialized variable use
- x86/csum: clean up `csum_partial' further
- x86/csum: Remove unnecessary odd handling
- ARM: sun9i: smp: fix return code check of of_property_match_string
- connector: Fix proc_event_num_listeners count not cleared
- net: qrtr: ns: Return 0 if server port is not present
- nfc: Do not send datagram if socket state isn't LLCP_BOUND
- virtio_blk: fix snprintf truncation compiler warning
- ida: Fix crash in ida_free when the bitmap is empty
- posix-timers: Get rid of [COMPAT_]SYS_NI() uses
- pinctrl: cy8c95x0: Fix get_pincfg
- pinctrl: cy8c95x0: Fix regression
- pinctrl: cy8c95x0: Fix typo
- drm/amd/display: get dprefclk ss info from integration info table
- drm/amd/display: Add case for dcn35 to support usb4 dmub hpd event
- drm/amdkfd: svm range always mapped flag not working on APU
- i2c: rk3x: fix potential spinlock recursion on poll
- smb: client: fix potential OOB in smb2_dump_detail()
- HID: nintendo: Prevent divide-by-zero on code
- dm audit: fix Kconfig so DM_AUDIT depends on BLK_DEV_DM
- ALSA: hda/realtek: Add quirks for ASUS Zenbook 2022 Models
- ASoC: Intel: bytcr_rt5640: Add new swapped-speakers quirk
- ASoC: Intel: bytcr_rt5640: Add quirk for the Medion Lifetab S10346
- platform/x86/amd/pmc: Disable keyboard wakeup on AMD Framework 13
- platform/x86/amd/pmc: Move keyboard wakeup disablement detection to pmc-quirks
- platform/x86/amd/pmc: Only run IRQ1 firmware version check on Cezanne
- platform/x86/amd/pmc: Move platform defines to header
- platform/x86: thinkpad_acpi: fix for incorrect fan reporting on some ThinkPad systems
- HID: nintendo: fix initializer element is not constant error
- kselftest: alsa: fixed a print formatting warning
- driver core: Add a guard() definition for the device_lock()
- Input: xpad - add Razer Wolverine V2 support
- wifi: iwlwifi: pcie: avoid a NULL pointer dereference
- ARC: fix smatch warning
- ARC: fix spare error
- s390/scm: fix virtual vs physical address confusion
- ASoC: cs35l45: Prevents spinning during runtime suspend
- ASoC: cs35l45: Prevent IRQ handling when suspending/resuming
- ASoC: cs35l45: Use modern pm_ops
- pinctrl: amd: Mask non-wake source pins with interrupt enabled at suspend
- Input: i8042 - add nomux quirk for Acer P459-G2-M
- Input: atkbd - skip ATKBD_CMD_GETID in translated mode
- reset: hisilicon: hi6220: fix Wvoid-pointer-to-enum-cast warning
- Input: psmouse - enable Synaptics InterTouch for ThinkPad L14 G1
- ring-buffer: Do not record in NMI if the arch does not support cmpxchg in NMI
- tracing: Fix uaf issue when open the hist or hist_debug file
- MIPS: dts: loongson: drop incorrect dwmac fallback compatible
- stmmac: dwmac-loongson: drop useless check for compatible fallback
- tracing: Add size check when printing trace_marker output
- tracing: Have large events show up as '[LINE TOO BIG]' instead of nothing
- jbd2: fix soft lockup in journal_finish_inode_data_buffers()
- efi/loongarch: Use load address to calculate kernel entry address
- platform/x86: intel-vbtn: Fix missing tablet-mode-switch events
- neighbour: Don't let neigh_forced_gc() disable preemption for long
- drm/crtc: Fix uninit-value bug in drm_mode_setcrtc
- jbd2: increase the journal IO's priority
- jbd2: correct the printing of write_flags in jbd2_write_superblock()
- soundwire: intel_ace2x: fix AC timing setting for ACE2.x
- clk: rockchip: rk3128: Fix HCLK_OTG gate register
- clk: rockchip: rk3568: Add PLL rate for 292.5MHz
- LoongArch: Preserve syscall nr across execve()
- LoongArch: Set unwind stack type to unknown rather than set error flag
- LoongArch: Apply dynamic relocations for LLD
- hwmon: (corsair-psu) Fix probe when built-in
- ALSA: pcmtest: stop timer before buffer is released
- drm/exynos: fix a wrong error checking
- drm/exynos: fix a potential error pointer dereference
- drm/amdgpu: Add NULL checks for function pointers
- drm/amd/display: Add monitor patch for specific eDP
- arm64: dts: rockchip: Fix PCI node addresses on rk3399-gru
- nvme: fix deadlock between reset and scan
- nvme: prevent potential spectre v1 gadget
- nvme-ioctl: move capable() admin check to the end
- nvme: ensure reset state check ordering
- nvme: introduce helper function to get ctrl state
- ASoC: da7219: Support low DC impedance headset
- net/tg3: fix race condition in tg3_reset_task()
- pds_vdpa: set features order
- pds_vdpa: clear config callback when status goes to 0
- pds_vdpa: fix up format-truncation complaint
- ASoC: SOF: ipc4-topology: Correct data structures for the GAIN module
- ASoC: SOF: ipc4-topology: Correct data structures for the SRC module
- ASoC: hdac_hda: Conditionally register dais for HDMI and Analog
- ASoC: amd: yc: Add DMI entry to support System76 Pangolin 13
- nouveau/tu102: flush all pdbs on vmm flush
- ASoC: SOF: sof-audio: Modify logic for enabling/disabling topology cores
- ASoC: SOF: ipc4-topology: Add core_mask in struct snd_sof_pipeline
- ASoC: Intel: skl_hda_dsp_generic: Drop HDMI routes when HDMI is not available
- ASoC: fsl_xcvr: refine the requested phy clock frequency
- ASoC: rt5650: add mutex to avoid the jack detection failure
- ASoC: fsl_xcvr: Enable 2 * TX bit clock for spdif only case
- ASoC: cs43130: Fix incorrect frame delay configuration
- ASoC: cs43130: Fix the position of const qualifier
- ASoC: Intel: Skylake: mem leak in skl register function
- ASoC: SOF: topology: Fix mem leak in sof_dai_load()
- ASoC: nau8822: Fix incorrect type in assignment and cast to restricted __be16
- ASoC: Intel: Skylake: Fix mem leak in few functions
- arm64: dts: rockchip: fix rk356x pcie msg interrupt name
- ASoC: wm8974: Correct boost mixer inputs
- ASoC: amd: yc: Add HP 255 G10 into quirk table
- nvme-core: check for too small lba shift
- blk-mq: don't count completed flush data request as inflight in case of quiesce
- smb: client, common: fix fortify warnings
- drm/amdgpu: Use another offset for GC 9.4.3 remap
- drm/amdkfd: Free gang_ctx_bo and wptr_bo in pqm_uninit
- drm/amdgpu: Fix cat debugfs amdgpu_regs_didt causes kernel null pointer
- drm/amd/display: update dcn315 lpddr pstate latency
- drm/amdkfd: Use common function for IP version check
- drm/amdgpu: Do not issue gpu reset from nbio v7_9 bif interrupt
- block: warn once for each partition in bio_check_ro()
- io_uring: use fget/fput consistently
- nvme-core: fix a memory leak in nvme_ns_info_from_identify()
- ALSA: hda: intel-nhlt: Ignore vbps when looking for DMIC 32 bps format
- debugfs: fix automount d_fsdata usage
- wifi: mac80211: handle 320 MHz in ieee80211_ht_cap_ie_to_sta_ht_cap
- wifi: avoid offset calculation on NULL pointer
- wifi: cfg80211: lock wiphy mutex for rfkill poll
- mptcp: fix uninit-value in mptcp_incoming_options
- ALSA: hda - Fix speaker and headset mic pin config for CHUWI CoreBook XPro
- pinctrl: lochnagar: Don't build on MIPS
- pinctrl: s32cc: Avoid possible string truncation
- nfsd: drop the nfsd_put helper
- media: qcom: camss: Comment CSID dt_id field
- cxl/memdev: Hold region_rwsem during inject and clear poison ops
- cxl/hdm: Fix a benign lockdep splat
- cxl: Add cxl_num_decoders_committed() usage to cxl_test
- mmc: sdhci-sprd: Fix eMMC init failure after hw reset
- mmc: core: Cancel delayed work before releasing host
- mmc: rpmb: fixes pause retune on all RPMB partitions.
- mmc: meson-mx-sdhc: Fix initialization frozen issue
- drm/amd/display: Fix sending VSC (+ colorimetry) packets for DP/eDP displays without PSR
- drm/amd/display: add nv12 bounding box
- drm/amdgpu: skip gpu_info fw loading on navi12
- mm: fix unmap_mapping_range high bits shift bug
- i2c: core: Fix atomic xfer check for non-preempt config
- x86/kprobes: fix incorrect return address calculation in kprobe_emulate_call_indirect
- firewire: ohci: suppress unexpected system reboot in AMD Ryzen machines and ASM108x/VT630x PCIe cards
- mm/mglru: skip special VMAs in lru_gen_look_around()
- net: constify sk_dst_get() and __sk_dst_get() argument
- cxl/pmu: Ensure put_device on pmu devices
- net: prevent mss overflow in skb_segment()
- powerpc/pseries/vas: Migration suspend waits for no in-progress open windows
- RISCV: KVM: update external interrupt atomically for IMSIC swfile
- dmaengine: fsl-edma: fix wrong pointer check in fsl_edma3_attach_pd()
- dmaengine: idxd: Protect int_handle field in hw descriptor
- drm/amd/display: Increase frame warning limit with KASAN or KCSAN in dml
- kernel/resource: Increment by align value in get_free_mem_region()
- cxl/core: Always hold region_rwsem while reading poison lists
- cxl: Add cxl_decoders_committed() helper
- drm/amd/display: Increase num voltage states to 40
- drm/i915: Call intel_pre_plane_updates() also for pipes getting enabled
- clk: rockchip: rk3128: Fix SCLK_SDMMC's clock name
- clk: rockchip: rk3128: Fix aclk_peri_src's parent
- phy: sunplus: return negative error code in sp_usb_phy_probe
- phy: mediatek: mipi: mt8183: fix minimal supported frequency
- iio: imu: adis16475: use bit numbers in assign_bit()
- dmaengine: fsl-edma: Add judgment on enabling round robin arbitration
- dmaengine: fsl-edma: Do not suspend and resume the masked dma channel when the system is sleeping
- dmaengine: ti: k3-psil-am62a: Fix SPI PDMA data
- dmaengine: ti: k3-psil-am62: Fix SPI PDMA data
- phy: ti: gmii-sel: Fix register offset when parent is not a syscon node
- KVM: s390: vsie: fix wrong VIR 37 when MSO is used
- riscv: don't probe unaligned access speed if already done
- rcu/tasks-trace: Handle new PF_IDLE semantics
- rcu/tasks: Handle new PF_IDLE semantics
- rcu: Introduce rcu_cpu_online()
- rcu: Break rcu_node_0 --> &rq->__lock order
- ACPI: thermal: Fix acpi_thermal_unregister_thermal_zone() cleanup
- RDMA/mlx5: Fix mkey cache WQ flush
- clk: si521xx: Increase stack based print buffer size in probe
- vfio/mtty: Overhaul mtty interrupt handling
- crypto: qat - fix double free during reset
- crypto: xts - use 'spawn' for underlying single-block cipher
- bpftool: Align output skeleton ELF code
- bpftool: Fix -Wcast-qual warning
- tcp: derive delack_max from rto_min
- media: qcom: camss: Fix genpd cleanup
- media: qcom: camss: Fix V4L2 async notifier error path
- xsk: add multi-buffer support for sockets sharing umem
- mm/memory-failure: pass the folio and the page to collect_procs()
- mm: convert DAX lock/unlock page to lock/unlock folio
- net: Implement missing SO_TIMESTAMPING_NEW cmsg support
- bnxt_en: Remove mis-applied code from bnxt_cfg_ntp_filters()
- net: ravb: Wait for operating mode to be applied
- asix: Add check for usbnet_get_endpoints
- octeontx2-af: Re-enable MAC TX in otx2_stop processing
- octeontx2-af: Always configure NIX TX link credits based on max frame size
- net/smc: fix invalid link access in dumping SMC-R connections
- net/qla3xxx: fix potential memleak in ql_alloc_buffer_queues
- virtio_net: fix missing dma unmap for resize
- virtio_net: avoid data-races on dev->stats fields
- apparmor: Fix move_mount mediation by detecting if source is detached
- igc: Fix hicredit calculation
- i40e: Restore VF MSI-X state during PCI reset
- ASoC: meson: g12a-tohdmitx: Fix event generation for S/PDIF mux
- ASoC: meson: g12a-toacodec: Fix event generation
- ASoC: meson: g12a-tohdmitx: Validate written enum values
- ASoC: meson: g12a-toacodec: Validate written enum values
- i40e: fix use-after-free in i40e_aqc_add_filters()
- net: Save and restore msg_namelen in sock_sendmsg
- netfilter: nft_immediate: drop chain reference counter on error
- netfilter: nf_nat: fix action not being set for all ct states
- net: bcmgenet: Fix FCS generation for fragmented skbuffs
- sfc: fix a double-free bug in efx_probe_filters
- ARM: sun9i: smp: Fix array-index-out-of-bounds read in sunxi_mc_smp_init
- selftests: bonding: do not set port down when adding to bond
- net: Implement missing getsockopt(SO_TIMESTAMPING_NEW)
- r8169: Fix PCI error on system resume
- net: sched: em_text: fix possible memory leak in em_text_destroy()
- mlxbf_gige: fix receive packet race condition
- ASoC: mediatek: mt8186: fix AUD_PAD_TOP register and offset
- ASoC: fsl_rpmsg: Fix error handler with pm_runtime_enable
- igc: Check VLAN EtherType mask
- igc: Check VLAN TCI mask
- igc: Report VLAN EtherType matching back to user
- i40e: Fix filter input checks to prevent config with invalid values
- ice: Shut down VSI with "link-down-on-close" enabled
- ice: Fix link_down_on_close message
- drm/i915/perf: Update handling of MMIO triggered reports
- drm/i915/dp: Fix passing the correct DPCD_REV for drm_dp_set_phy_test_pattern
- octeontx2-af: Fix marking couple of structure as __packed
- nfc: llcp_core: Hold a ref to llcp_local->dev when holding a ref to llcp_local
- netfilter: nf_tables: set transport offset from mac header for netdev/egress
- drm/bridge: ps8640: Fix size mismatch warning w/ len
- drm/bridge: ti-sn65dsi86: Never store more than msg->size bytes in AUX xfer
- drm/bridge: parade-ps8640: Never store more than msg->size bytes in AUX xfer
- wifi: iwlwifi: pcie: don't synchronize IRQs from IRQ
- accel/qaic: Implement quirk for SOC_HW_VERSION
- accel/qaic: Fix GEM import path code
- KVM: x86/pmu: fix masking logic for MSR_CORE_PERF_GLOBAL_CTRL
- cifs: do not depend on release_iface for maintaining iface_list
- cifs: cifs_chan_is_iface_active should be called with chan_lock held
- drm/mgag200: Fix gamma lut not initialized for G200ER, G200EV, G200SE
- Revert "PCI/ASPM: Remove pcie_aspm_pm_state_change()"
- mptcp: prevent tcp diag from closing listener subflows
- drm/amd/display: pbn_div need be updated for hotplug event
- ALSA: hda/realtek: Fix mute and mic-mute LEDs for HP ProBook 440 G6
- ALSA: hda/realtek: fix mute/micmute LEDs for a HP ZBook
- ALSA: hda/realtek: enable SND_PCI_QUIRK for hp pavilion 14-ec1xxx series
- ALSA: hda/tas2781: remove sound controls in unbind
- ALSA: hda/tas2781: move set_drv_data outside tasdevice_init
- ALSA: hda/tas2781: do not use regcache
- keys, dns: Fix missing size check of V1 server-list header
- Revert "platform/x86: p2sb: Allow p2sb_bar() calls during PCI device probe"
- netfilter: nf_tables: skip set commit for deleted/destroyed sets
- wifi: nl80211: fix deadlock in nl80211_set_cqm_rssi (6.6.x)
- wifi: cfg80211: fix CQM for non-range use
- tracing: Fix blocked reader of snapshot buffer
- ftrace: Fix modification of direct_function hash while in use
- ring-buffer: Fix wake ups when buffer_percent is set to 100
- Revert "nvme-fc: fix race between error recovery and creating association"
- mm/memory-failure: check the mapcount of the precise page
- mm/memory-failure: cast index to loff_t before shifting it
- mm: migrate high-order folios in swap cache correctly
- mm/filemap: avoid buffered read/write race to read inconsistent data
- selftests: secretmem: floor the memory size to the multiple of page_size
- maple_tree: do not preallocate nodes for slot stores
- platform/x86: p2sb: Allow p2sb_bar() calls during PCI device probe
- platform/x86/intel/pmc: Move GBE LTR ignore to suspend callback
- platform/x86/intel/pmc: Allow reenabling LTRs
- platform/x86/intel/pmc: Add suspend callback
- block: renumber QUEUE_FLAG_HW_WC
- mptcp: fix inconsistent state on fastopen race
- mptcp: fix possible NULL pointer dereference on close
- mptcp: refactor sndbuf auto-tuning
- linux/export: Ensure natural alignment of kcrctab array
- linux/export: Fix alignment for 64-bit ksymtab entries
- kexec: select CRYPTO from KEXEC_FILE instead of depending on it
- kexec: fix KEXEC_FILE dependencies
- virtio_ring: fix syncs DMA memory with different direction
- fs: cifs: Fix atime update check
- client: convert to new timestamp accessors
- fs: new accessor methods for atime and mtime
- ksmbd: avoid duplicate opinfo_put() call on error of smb21_lease_break_ack()
- ksmbd: lazy v2 lease break on smb2_write()
- ksmbd: send v2 lease break notification for directory
- ksmbd: downgrade RWH lease caching state to RH for directory
- ksmbd: set v2 lease capability
- ksmbd: set epoch in create context v2 lease
- ksmbd: don't update ->op_state as OPLOCK_STATE_NONE on error
- ksmbd: move setting SMB2_FLAGS_ASYNC_COMMAND and AsyncId
- ksmbd: release interim response after sending status pending response
- ksmbd: move oplock handling after unlock parent dir
- ksmbd: separately allocate ci per dentry
- ksmbd: prevent memory leak on error return
- ksmbd: fix kernel-doc comment of ksmbd_vfs_kern_path_locked()
- ksmbd: no need to wait for binded connection termination at logoff
- ksmbd: add support for surrogate pair conversion
- ksmbd: fix missing RDMA-capable flag for IPoIB device in ksmbd_rdma_capable_netdev()
- ksmbd: fix kernel-doc comment of ksmbd_vfs_setxattr()
- ksmbd: reorganize ksmbd_iov_pin_rsp()
- ksmbd: Remove unused field in ksmbd_user struct
- spi: cadence: revert "Add SPI transfer delays"
- x86/smpboot/64: Handle X2APIC BIOS inconsistency gracefully
- x86/alternatives: Disable interrupts and sync when optimizing NOPs in place
- x86/alternatives: Sync core before enabling interrupts
- KVM: arm64: vgic: Force vcpu vgic teardown on vcpu destroy
- KVM: arm64: vgic: Add a non-locking primitive for kvm_vgic_vcpu_destroy()
- KVM: arm64: vgic: Simplify kvm_vgic_destroy()
- thunderbolt: Fix memory leak in margining_port_remove()
- lib/vsprintf: Fix %pfwf when current node refcount == 0
- gpio: dwapb: mask/unmask IRQ when disable/enale it
- bus: ti-sysc: Flush posted write only after srst_udelay
- pinctrl: starfive: jh7100: ignore disabled device tree nodes
- pinctrl: starfive: jh7110: ignore disabled device tree nodes
- selftests: mptcp: join: fix subflow_send_ack lookup
- dm-integrity: don't modify bio's immutable bio_vec in integrity_metadata()
- tracing / synthetic: Disable events after testing in synth_event_gen_test_init()
- scsi: core: Always send batch on reset or error handling command
- Revert "scsi: aacraid: Reply queue mapping to CPUs based on IRQ affinity"
- nvmem: brcm_nvram: store a copy of NVRAM content
- spi: atmel: Fix clock issue when using devices with different polarities
- spi: atmel: Prevent spi transfers from being killed
- spi: atmel: Do not cancel a transfer upon any signal
- ring-buffer: Fix slowpath of interrupted event
- ring-buffer: Remove useless update to write_stamp in rb_try_to_discard()
- ring-buffer: Fix 32-bit rb_time_read() race with rb_time_cmpxchg()
- 9p: prevent read overrun in protocol dump tracepoint
- drm/i915/dmc: Don't enable any pipe DMC events
- drm/i915: Reject async flips with bigjoiner
- smb: client: fix OOB in smbCalcSize()
- smb: client: fix OOB in SMB2_query_info_init()
- smb: client: fix potential OOB in cifs_dump_detail()
- smb: client: fix OOB in cifsd when receiving compounded resps
- nfsd: call nfsd_last_thread() before final nfsd_put()
- dt-bindings: nvmem: mxs-ocotp: Document fsl,ocotp
- net: stmmac: fix incorrect flag check in timestamp interrupt
- net: avoid build bug in skb extension length calculation
- net: ks8851: Fix TX stall caused by TX buffer overrun
- net: rfkill: gpio: set GPIO direction
- net: 9p: avoid freeing uninit memory in p9pdu_vreadf
- Input: soc_button_array - add mapping for airplane mode button
- net: usb: ax88179_178a: avoid failed operations when device is disconnected
- usb: fotg210-hcd: delete an incorrect bounds test
- usb: typec: ucsi: fix gpio-based orientation detection
- Bluetooth: Add more enc key size check
- Bluetooth: MGMT/SMP: Fix address type when using SMP over BREDR/LE
- Bluetooth: L2CAP: Send reject on command corrupted request
- Bluetooth: af_bluetooth: Fix Use-After-Free in bt_sock_recvmsg
- Bluetooth: hci_event: Fix not checking if HCI_OP_INQUIRY has been sent
- ASoC: tas2781: check the validity of prm_no/cfg_no
- ALSA: hda/realtek: Add quirk for ASUS ROG GV302XA
- ALSA: hda/tas2781: select program 0, conf 0 by default
- USB: serial: option: add Quectel RM500Q R13 firmware support
- USB: serial: option: add Foxconn T99W265 with new baseline
- USB: serial: option: add Quectel EG912Y module support
- USB: serial: ftdi_sio: update Actisense PIDs constant names
- wifi: cfg80211: fix certs build to not depend on file order
- wifi: cfg80211: Add my certificate
- wifi: mt76: fix crash with WED rx support enabled
- usb-storage: Add quirk for incorrect WP on Kingston DT Ultimate 3.0 G3
- ARM: dts: Fix occasional boot hang for am3 usb
- ALSA: usb-audio: Increase delay in MOTU M quirk
- iio: triggered-buffer: prevent possible freeing of wrong buffer
- iio: tmag5273: fix temperature offset
- iio: adc: ti_am335x_adc: Fix return value check of tiadc_request_dma()
- iio: imu: adis16475: add spi_device_id table
- iio: common: ms_sensors: ms_sensors_i2c: fix humidity conversion time table
- iio: adc: imx93: add four channels for imx93 adc
- iio: kx022a: Fix acceleration value scaling
- scsi: ufs: core: Let the sq_lock protect sq_tail_slot access
- scsi: ufs: qcom: Return ufs_qcom_clk_scale_*() errors in ufs_qcom_clk_scale_notify()
- scsi: bnx2fc: Fix skb double free in bnx2fc_rcv()
- iio: adc: meson: add separate config for axg SoC family
- Input: ipaq-micro-keys - add error handling for devm_kmemdup
- interconnect: qcom: sm8250: Enable sync_state
- iio: imu: inv_mpu6050: fix an error code problem in inv_mpu6050_read_raw
- interconnect: Treat xlate() returning NULL node as an error
- nvme-pci: fix sleeping function called from interrupt context
- gpiolib: cdev: add gpio_device locking wrapper around gpio_ioctl()
- pinctrl: at91-pio4: use dedicated lock class for IRQ
- x86/xen: add CPU dependencies for 32-bit build
- i2c: aspeed: Handle the coalesced stop conditions with the start conditions.
- drm/amdgpu: re-create idle bo's PTE during VM state machine reset
- i2c: qcom-geni: fix missing clk_disable_unprepare() and geni_se_resources_off()
- ASoC: fsl_sai: Fix channel swap issue on i.MX8MP
- ASoC: hdmi-codec: fix missing report for jack initial status
- drm/i915/mtl: Fix HDMI/DP PLL clock selection
- drm/i915/hwmon: Fix static analysis tool reported issues
- afs: Fix use-after-free due to get/remove race in volume tree
- afs: Fix overwriting of result of DNS query
- keys, dns: Allow key types (eg. DNS) to be reclaimed immediately on expiry
- net: check dev->gso_max_size in gso_features_check()
- net/ipv6: Revert remove expired routes with a separated list of routes
- net: ethernet: mtk_wed: fix possible NULL pointer dereference in mtk_wed_wo_queue_tx_clean()
- afs: Fix dynamic root lookup DNS check
- afs: Fix the dynamic root's d_delete to always delete unused dentries
- net: check vlan filter feature in vlan_vids_add_by_dev() and vlan_vids_del_by_dev()
- net: mana: select PAGE_POOL
- ice: Fix PF with enabled XDP going no-carrier after reset
- ice: alter feature support check for SRIOV and LAG
- ice: stop trashing VF VSI aggregator node ID information
- net: phy: skip LED triggers on PHYs on SFP modules
- bnxt_en: do not map packet buffers twice
- Bluetooth: hci_core: Fix hci_conn_hash_lookup_cis
- Bluetooth: hci_event: shut up a false-positive warning
- Bluetooth: Fix deadlock in vhci_send_frame
- Bluetooth: Fix not notifying when connection encryption changes
- net/rose: fix races in rose_kill_by_device()
- ethernet: atheros: fix a memleak in atl1e_setup_ring_resources
- net: sched: ife: fix potential use-after-free
- net: Return error from sk_stream_wait_connect() if sk_wait_event() fails
- octeontx2-pf: Fix graceful exit during PFC configuration failure
- net: mscc: ocelot: fix pMAC TX RMON stats for bucket 256-511 and above
- net: mscc: ocelot: fix eMAC TX RMON stats for bucket 256-511 and above
- net/mlx5e: Correct snprintf truncation handling for fw_version buffer used by representors
- net/mlx5e: Correct snprintf truncation handling for fw_version buffer
- net/mlx5e: Fix error codes in alloc_branch_attr()
- net/mlx5e: Fix error code in mlx5e_tc_action_miss_mapping_get()
- net/mlx5: Refactor mlx5_flow_destination->rep pointer to vport num
- net/mlx5: Fix fw tracer first block check
- net/mlx5e: XDP, Drop fragmented packets larger than MTU size
- net/mlx5e: Decrease num_block_tc when unblock tc offload
- net/mlx5e: Fix overrun reported by coverity
- net/mlx5e: fix a potential double-free in fs_udp_create_groups
- net/mlx5e: Fix a race in command alloc flow
- net/mlx5e: Fix slab-out-of-bounds in mlx5_query_nic_vport_mac_list()
- Revert "net/mlx5e: fix double free of encap_header"
- Revert "net/mlx5e: fix double free of encap_header in update funcs"
- bpf: syzkaller found null ptr deref in unix_bpf proto add
- ice: fix theoretical out-of-bounds access in ethtool link modes
- wifi: mac80211: mesh_plink: fix matches_local logic
- wifi: mac80211: mesh: check element parsing succeeded
- wifi: mac80211: check defragmentation succeeded
- wifi: mac80211: don't re-add debugfs during reconfig
- wifi: mac80211: check if the existing link config remains unchanged
- wifi: iwlwifi: pcie: add another missing bh-disable for rxq->lock
- wifi: ieee80211: don't require protected vendor action frames
- SUNRPC: Revert 5f7fc5d69f6e92ec0b38774c387f5cf7812c5806
- platform/x86/intel/pmc: Fix hang in pmc_core_send_ltr_ignore()
- s390/vx: fix save/restore of fpu kernel context
- reset: Fix crash when freeing non-existent optional resets
- ARM: OMAP2+: Fix null pointer dereference and memory leak in omap_soc_device_init
- ARM: dts: dra7: Fix DRA7 L3 NoC node register size
- arm64: dts: allwinner: h616: update emac for Orange Pi Zero 3
- spi: spi-imx: correctly configure burst length when using dma
- drm: Fix FD ownership check in drm_master_check_perm()
- drm: Update file owner during use
- drm/i915/edp: don't write to DP_LINK_BW_SET when using rate select
- drm/i915: Introduce crtc_state->enhanced_framing
- drm/i915: Fix FEC state dump
- drm/amd/display: fix hw rotated modes when PSR-SU is enabled
- btrfs: free qgroup pertrans reserve on transaction abort
- btrfs: qgroup: use qgroup_iterator in qgroup_convert_meta()
- btrfs: qgroup: iterate qgroups without memory allocation for qgroup_reserve()
- mm/damon/core: make damon_start() waits until kdamond_fn() starts
- mm/damon/core: use number of passed access sampling as a timer
- bpf: Fix prog_array_map_poke_run map poke update
- !5451  arm64: Delete macro in the scsnp feature
- arm64: Delete macro in the scsnp feature
- !5037 [OLK-6.6] Add support for Mucse Network Adapter(N500/N210)
- drivers: initial support for rnpgbe drivers from Mucse Technology
- !4782 [OLK-6.6] Add drivers support for Mucse Network Adapter rnpm (N10/N400)
- drivers: initial support for rnpm drivers from Mucse Technology
- !5340  CVE-2023-52593
- wifi: wfx: fix possible NULL pointer dereference in wfx_set_mfp_ap()
- !5341  powerpc/lib: Validate size for vector operations
- powerpc/lib: Validate size for vector operations
- !5346 v2  s390/vfio-ap: always filter entire AP matrix
- s390/vfio-ap: always filter entire AP matrix
- !5248  mm: cachestat: fix folio read-after-free in cache walk
- mm: cachestat: fix folio read-after-free in cache walk
- !5212 [OLK-6.6] Support PSPCCP/NTBCCP identification for Hygon 2th and 3th CPU
- crypto: ccp: Add Hygon CSV support
- crypto: ccp: Fixup the capability of Hygon PSP during initialization
- !5318  Backport 6.6.8 LTS Patches
- RDMA/mlx5: Change the key being sent for MPV device affiliation
- x86/speculation, objtool: Use absolute relocations for annotations
- ring-buffer: Have rb_time_cmpxchg() set the msb counter too
- ring-buffer: Do not try to put back write_stamp
- ring-buffer: Fix a race in rb_time_cmpxchg() for 32 bit archs
- ring-buffer: Fix writing to the buffer with max_data_size
- ring-buffer: Have saved event hold the entire event
- ring-buffer: Do not update before stamp when switching sub-buffers
- tracing: Update snapshot buffer on resize if it is allocated
- ring-buffer: Fix memory leak of free page
- smb: client: fix OOB in smb2_query_reparse_point()
- smb: client: fix NULL deref in asn1_ber_decoder()
- smb: client: fix potential OOBs in smb2_parse_contexts()
- drm/i915: Fix remapped stride with CCS on ADL+
- drm/i915: Fix intel_atomic_setup_scalers() plane_state handling
- drm/i915: Fix ADL+ tiled plane stride when the POT stride is smaller than the original
- drm/amd/display: Disable PSR-SU on Parade 0803 TCON again
- drm/amd/display: Restore guard against default backlight value < 1 nit
- drm/edid: also call add modes in EDID connector update fallback
- drm/amdgpu: fix tear down order in amdgpu_vm_pt_free
- btrfs: don't clear qgroup reserved bit in release_folio
- btrfs: fix qgroup_free_reserved_data int overflow
- btrfs: free qgroup reserve when ORDERED_IOERR is set
- kexec: drop dependency on ARCH_SUPPORTS_KEXEC from CRASH_DUMP
- mm/shmem: fix race in shmem_undo_range w/THP
- mm/mglru: reclaim offlined memcgs harder
- mm/mglru: respect min_ttl_ms with memcgs
- mm/mglru: try to stop at high watermarks
- mm/mglru: fix underprotected page cache
- dmaengine: fsl-edma: fix DMA channel leak in eDMAv4
- dmaengine: stm32-dma: avoid bitfield overflow assertion
- drm/mediatek: Fix access violation in mtk_drm_crtc_dma_dev_get
- drm/amdgpu/sdma5.2: add begin/end_use ring callbacks
- team: Fix use-after-free when an option instance allocation fails
- arm64: mm: Always make sw-dirty PTEs hw-dirty in pte_modify
- Revert "selftests: error out if kernel header files are not yet built"
- ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS
- soundwire: stream: fix NULL pointer dereference for multi_link
- cxl/hdm: Fix dpa translation locking
- btrfs: do not allow non subvolume root targets for snapshot
- perf: Fix perf_event_validate_size() lockdep splat
- HID: hid-asus: add const to read-only outgoing usb buffer
- arm64: add dependency between vmlinuz.efi and Image
- smb: client: set correct file type from NFS reparse points
- smb: client: introduce ->parse_reparse_point()
- smb: client: implement ->query_reparse_point() for SMB1
- net: usb: qmi_wwan: claim interface 4 for ZTE MF290
- eventfs: Do not allow NULL parent to eventfs_start_creating()
- asm-generic: qspinlock: fix queued_spin_value_unlocked() implementation
- scripts/checkstack.pl: match all stack sizes for s390
- nfc: virtual_ncidev: Add variable to check if ndev is running
- HID: multitouch: Add quirk for HONOR GLO-GXXX touchpad
- HID: hid-asus: reset the backlight brightness level on resume
- HID: add ALWAYS_POLL quirk for Apple kb
- HID: glorious: fix Glorious Model I HID report
- HID: apple: add Jamesdonkey and A3R to non-apple keyboards list
- HID: mcp2221: Allow IO to start during probe
- HID: mcp2221: Set driver data before I2C adapter add
- platform/x86: intel_telemetry: Fix kernel doc descriptions
- LoongArch: Mark {dmw,tlb}_virt_to_page() exports as non-GPL
- LoongArch: Silence the boot warning about 'nokaslr'
- LoongArch: Record pc instead of offset in la_abs relocation
- LoongArch: Add dependency between vmlinuz.efi and vmlinux.efi
- selftests/bpf: fix bpf_loop_bench for new callback verification scheme
- nvme: catch errors from nvme_configure_metadata()
- nvme-auth: set explanation code for failure2 msgs
- bcache: avoid NULL checking to c->root in run_cache_set()
- bcache: add code comments for bch_btree_node_get() and __bch_btree_node_alloc()
- bcache: remove redundant assignment to variable cur_idx
- bcache: avoid oversize memory allocation by small stripe_size
- blk-throttle: fix lockdep warning of "cgroup_mutex or RCU read lock required!"
- rxrpc: Fix some minor issues with bundle tracing
- stmmac: dwmac-loongson: Add architecture dependency
- usb: aqc111: check packet for fixup for true limit
- x86/hyperv: Fix the detection of E820_TYPE_PRAM in a Gen2 VM
- selftests/mm: cow: print ksft header before printing anything else
- drm/i915: Use internal class when counting engine resets
- drm/i915/selftests: Fix engine reset count storage for multi-tile
- accel/ivpu/37xx: Fix interrupt_clear_with_0 WA initialization
- accel/ivpu: Print information about used workarounds
- drm/mediatek: Add spinlock for setting vblank event in atomic_begin
- drm/mediatek: fix kernel oops if no crtc is found
- PCI: vmd: Fix potential deadlock when enabling ASPM
- ksmbd: fix wrong name of SMB2_CREATE_ALLOCATION_SIZE
- PCI/ASPM: Add pci_enable_link_state_locked()
- PCI: loongson: Limit MRRS to 256
- Revert "PCI: acpiphp: Reassign resources on bridge if necessary"
- ALSA: hda/tas2781: reset the amp before component_add
- ALSA: hda/tas2781: call cleanup functions only once
- ALSA: hda/tas2781: handle missing EFI calibration data
- ALSA: hda/tas2781: leave hda_component in usable state
- ALSA: hda/realtek: Apply mute LED quirk for HP15-db
- ALSA: hda/hdmi: add force-connect quirks for ASUSTeK Z170 variants
- ALSA: hda/hdmi: add force-connect quirk for NUC5CPYB
- io_uring/cmd: fix breakage in SOCKET_URING_OP_SIOC* implementation
- fuse: dax: set fc->dax to NULL in fuse_dax_conn_free()
- fuse: disable FOPEN_PARALLEL_DIRECT_WRITES with FUSE_DIRECT_IO_ALLOW_MMAP
- fuse: share lookup state between submount and its parent
- fuse: Rename DIRECT_IO_RELAX to DIRECT_IO_ALLOW_MMAP
- HID: Add quirk for Labtec/ODDOR/aikeec handbrake
- HID: i2c-hid: Add IDEA5002 to i2c_hid_acpi_blacklist[]
- net: atlantic: fix double free in ring reinit logic
- appletalk: Fix Use-After-Free in atalk_ioctl
- net: stmmac: Handle disabled MDIO busses from devicetree
- net: stmmac: dwmac-qcom-ethqos: Fix drops in 10M SGMII RX
- dpaa2-switch: do not ask for MDB, VLAN and FDB replay
- dpaa2-switch: fix size of the dma_unmap
- vsock/virtio: Fix unsigned integer wrap around in virtio_transport_has_space()
- sign-file: Fix incorrect return values check
- stmmac: dwmac-loongson: Make sure MDIO is initialized before use
- net: ena: Fix XDP redirection error
- net: ena: Fix DMA syncing in XDP path when SWIOTLB is on
- net: ena: Fix xdp drops handling due to multibuf packets
- net: ena: Destroy correct number of xdp queues upon failure
- net: Remove acked SYN flag from packet in the transmit queue correctly
- qed: Fix a potential use-after-free in qed_cxt_tables_alloc
- iavf: Fix iavf_shutdown to call iavf_remove instead iavf_close
- iavf: Handle ntuple on/off based on new state machines for flow director
- iavf: Introduce new state machines for flow director
- net/rose: Fix Use-After-Free in rose_ioctl
- atm: Fix Use-After-Free in do_vcc_ioctl
- octeontx2-af: Fix pause frame configuration
- octeontx2-af: Update RSS algorithm index
- octeontx2-pf: Fix promisc mcam entry action
- octeon_ep: explicitly test for firmware ready value
- net/sched: act_ct: Take per-cb reference to tcf_ct_flow_table
- octeontx2-af: fix a use-after-free in rvu_nix_register_reporters
- net: fec: correct queue selection
- atm: solos-pci: Fix potential deadlock on &tx_queue_lock
- atm: solos-pci: Fix potential deadlock on &cli_queue_lock
- bnxt_en: Fix HWTSTAMP_FILTER_ALL packet timestamp logic
- bnxt_en: Fix wrong return value check in bnxt_close_nic()
- bnxt_en: Fix skb recycling logic in bnxt_deliver_skb()
- bnxt_en: Clear resource reservation during resume
- qca_spi: Fix reset behavior
- qca_debug: Fix ethtool -G iface tx behavior
- qca_debug: Prevent crash on TX ring changes
- net: ipv6: support reporting otherwise unknown prefix flags in RTM_NEWPREFIX
- net/mlx5: Fix a NULL vs IS_ERR() check
- net/mlx5e: Check netdev pointer before checking its net ns
- net/mlx5: Nack sync reset request when HotPlug is enabled
- net/mlx5e: TC, Don't offload post action rule if not supported
- net/mlx5e: Fix possible deadlock on mlx5e_tx_timeout_work
- net/mlx5e: Disable IPsec offload support if not FW steering
- RDMA/mlx5: Send events from IB driver about device affiliation state
- net/mlx5e: Check the number of elements before walk TC rhashtable
- net/mlx5e: Reduce eswitch mode_lock protection context
- net/mlx5e: Tidy up IPsec NAT-T SA discovery
- net/mlx5e: Unify esw and normal IPsec status table creation/destruction
- net/mlx5e: Ensure that IPsec sequence packet number starts from 1
- net/mlx5e: Honor user choice of IPsec replay window size
- HID: lenovo: Restrict detection of patched firmware only to USB cptkbd
- afs: Fix refcount underflow from error handling race
- efi/x86: Avoid physical KASLR on older Dell systems
- ksmbd: fix memory leak in smb2_lock()
- ext4: fix warning in ext4_dio_write_end_io()
- r8152: add vendor/device ID pair for ASUS USB-C2500
- !5239 crypto: hisilicon support no-sva feature
- crypto: hisilicon/qm - register to UACCE subsystem in UACCE_MODE_NOIOMMU mode
- crypto: hisilicon/qm - get the type of iommu
- uacce: support UACCE_MODE_NOIOMMU mode
- !5256 net: hns3: some bugfix for the HNS3 ethernet driver
- net: hns3: add checking for vf id of mailbox
- net: hns3: fix port duplex configure error in IMP reset
- net: hns3: fix reset timeout under full functions and queues
- net: hns3: fix delete tc fail issue
- net: hns3: fix kernel crash when 1588 is received on HIP08 devices
- net: hns3: Disable SerDes serial loopback for HiLink H60
- net: hns3: add new 200G link modes for hisilicon device
- net: hns3: fix wrong judgment condition issue
- !5250  f2fs: fix to tag gcing flag on page during block migration
- f2fs: fix to tag gcing flag on page during block migration
- !5249  btrfs: scrub: avoid use-after-free when chunk length is not 64K aligned
- btrfs: scrub: avoid use-after-free when chunk length is not 64K aligned
- !5244  ceph: fix deadlock or deadcode of misusing dget()
- ceph: fix deadlock or deadcode of misusing dget()
- !5180 RDMA/hns: Support hns RoCE Bonding
- RDMA/hns: Fix the concurrency error between bond and reset.
- RDMA/hns: Fix the device loss after unbinding RoCE bond resource slave
- RDMA/hns: Fix wild pointer error of RoCE bonding when rmmod hns3
- RDMA/hns: Support reset recovery for RoCE bonding
- RDMA/hns: Add functions to obtain netdev and bus_num from an hr_dev
- RDMA/hns: Support dispatching IB event for RoCE bonding
- RDMA/hns: Set IB port state depending on upper device for RoCE bonding
- RDMA/hns: Support RoCE bonding

* Thu Mar 14 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-12.0.0.8
- !5174 [OLK-6.6][sync from OLK-5.10] Introduce multiple LPI translation caches
- KVM:arm64:vgic update openEuler's config's to enable MULTI_LPI_TRANSLATE_CACHE
- KVM: arm64: vgic-its: Do not execute invalidate MSI-LPI translation cache on movi command
- KVM: arm64: vgic-its: Introduce multiple LPI translation caches
- !5208 Revert “Fix the header file location error and adjust the function and structure version.”
- Revert “Fix the header file location error and adjust the function and structure version.”
- !5199 v2  mTHP anon support
- uprobes: use pagesize-aligned virtual address when replacing pages
- selftests/mm/cow: add tests for anonymous multi-size THP
- selftests/mm/cow: generalize do_run_with_thp() helper
- selftests/mm/khugepaged: enlighten for multi-size THP
- selftests/mm: support multi-size THP interface in thp_settings
- selftests/mm: factor out thp settings management
- selftests/mm/kugepaged: restore thp settings at exit
- mm: thp: support allocation of anonymous multi-size THP
- mm: thp: introduce multi-size THP sysfs interface
- mm: non-pmd-mappable, large folios for folio_add_new_anon_rmap()
- mm: allow deferred splitting of arbitrary anon large folios
- mm/readahead: do not allow order-1 folio
- mm: more ptep_get() conversion
- mm/thp: fix "mm: thp: kill __transhuge_page_enabled()"
- memory: move exclusivity detection in do_wp_page() into wp_can_reuse_anon_folio()
- mm/rmap: convert page_move_anon_rmap() to folio_move_anon_rmap()
- mm/rmap: move SetPageAnonExclusive() out of page_move_anon_rmap()
- mm/rmap: pass folio to hugepage_add_anon_rmap()
- mm/rmap: simplify PageAnonExclusive sanity checks when adding anon rmap
- mm/rmap: warn on new PTE-mapped folios in page_add_anon_rmap()
- mm/rmap: move folio_test_anon() check out of __folio_set_anon()
- mm/rmap: move SetPageAnonExclusive out of __page_set_anon_rmap()
- mm/rmap: drop stale comment in page_add_anon_rmap and hugepage_add_anon_rmap()
- !4908 cgroup/cpuset: add exclusive and exclusive.effective for v2
- cgroup/cpuset: Fix retval in update_cpumask()
- cgroup/cpuset: Fix a memory leak in update_exclusive_cpumask()
- cgroup/cpuset: Cleanup signedness issue in cpu_exclusive_check()
- cgroup/cpuset: Enable invalid to valid local partition transition
- cgroup/cpuset: Check partition conflict with housekeeping setup
- cgroup/cpuset: Introduce remote partition
- cgroup/cpuset: Add cpuset.cpus.exclusive for v2
- cgroup/cpuset: Add cpuset.cpus.exclusive.effective for v2
- !5159 【OLK-6.6】iommu: reserve KABI for struct iommu_ops
- [OLK-6.6] iommu:kabi reserver space for struct iommu_ops
- !5149 net: hns3: add support some customized exception handling interfaces
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
- !4761 [OLK-6.6] backport 6.7 kernel signal patch
- riscv: signal: handle syscall restart before get_signal
- !5151 intel-sig: configs: enable TPMI related configs for OLK6.6
- config: update Intel TPMI based driver configs to  openeuler_defconfig for x86
- !5150 intel-sig: configs: enable PMT related configs for OLK6.6
- config: x86: Intel: enabled PMT SDSI TPMI configs
- !4427 【OLK-6.6】watchdog: Support watchdog_sdei coexist with existing  watchdogs
- watchdog: Support watchdog_sdei coexist with existing watchdogs
- !4776 [OLK-6.6] kabi:reserve space for msi expansion
- [OLK-6.6] kabi:reserve space for msi expansion
- !5041 [OLK-6.6] support the AMD Zen5 Turin
- x86/CPU/AMD: Add more models to X86_FEATURE_ZEN5
- x86/CPU/AMD: Add X86_FEATURE_ZEN5
- x86/CPU/AMD: Add X86_FEATURE_ZEN1
- x86/CPU/AMD: Drop now unused CPU erratum checking function
- x86/CPU/AMD: Get rid of amd_erratum_1485[]
- x86/CPU/AMD: Get rid of amd_erratum_400[]
- x86/CPU/AMD: Get rid of amd_erratum_383[]
- x86/CPU/AMD: Get rid of amd_erratum_1054[]
- x86/CPU/AMD: Move the DIV0 bug detection to the Zen1 init function
- x86/CPU/AMD: Move Zenbleed check to the Zen2 init function
- x86/CPU/AMD: Rename init_amd_zn() to init_amd_zen_common()
- x86/CPU/AMD: Call the spectral chicken in the Zen2 init function
- x86/CPU/AMD: Move erratum 1076 fix into the Zen1 init function
- x86/CPU/AMD: Move the Zen3 BTC_NO detection to the Zen3 init function
- x86/CPU/AMD: Carve out the erratum 1386 fix
- x86/CPU/AMD: Add ZenX generations flags
- !5036 [OLK-6.6] Do not serialize MSR accesses on AMD
- x86/barrier: Do not serialize MSR accesses on AMD
- !5134  modpost: Optimize symbol search from linear to binary search
- modpost: Optimize symbol search from linear to binary search
- !4826 add sw64 architecture support
- drivers: vfio: add sw64 support
- drivers: usb: add sw64 support
- drivers: tty: add sw64 support
- drivers: spi: add sw64 support
- drivers: scsi: add sw64 support
- drivers: rtc: add sw64 rtc support
- drivers: qemu_fw_cfg: add sw64 support
- drivers: platform: add sw64 support
- drivers: pci: add sw64 support
- drivers: misc: add sw64 support
- drivers: mfd: add sw64 support
- drivers: irqchip: add sw64 support
- drivers: iommu: add sw64 support
- drivers: i2c: add sw64 support
- drivers: hwmon: add sw64 support
- drivers: gpio: add sw64 support
- drivers: efi: add sw64 support
- !4927 ima: digest list new support modsig
- ima: digest list new support modsig
- !4971 net: hns3: backport some patch from kernel 6.7
- net: hns3: add some link modes for hisilicon device
- net: hns3: add vf fault detect support
- net: hns3: add hns3 vf fault detect cap bit support
- !5040 [OLK-6.6] Add support for Vendor Defined Error Types in Einj Module
- ACPI: APEI: EINJ: Add support for vendor defined error types
- platform/chrome: cros_ec_debugfs: Fix permissions for panicinfo
- fs: debugfs: Add write functionality to debugfs blobs
- ACPI: APEI: EINJ: Refactor available_error_type_show()
- !5039 [OLK-6.6] Fix disabling memory if DVSEC CXL Range does not match a CFMWS window
- cxl/pci: Fix disabling memory if DVSEC CXL Range does not match a CFMWS window
- !5047  Backport etmem swapcache recalim feature to OLK 6.6
- etmem: add swapcache reclaim to etmem
- etmem: Expose symbol reclaim_folio_list
- !4514 [OLK-6.6] kabi: IOMMU subsystem reservation
- kabi: IOMMU reservations
- kabi: bus_type, device_driver, dev_pm_ops reservation
- !5056  erofs: fix handling kern_mount() failure
- erofs: fix handling kern_mount() failure
- !5059  dm: limit the number of targets and parameter size area
- dm: limit the number of targets and parameter size area
- !5021  LoongArch: fix some known issue and update defconfig
- LoongArch: enable CONFIG_DEBUG_INFO_BTF by default
- net: stmmac: fix potential double free of dma descriptor resources
- drm/radeon: Workaround radeon driver bug for Loongson
- irqchip/loongson-liointc: Set different isr for differnt core
- LoongArch: kdump: Add high memory reservation
- LoongArch: Fix kdump failure on v40 interface specification
- LoongArch: kexec: Add compatibility with old interfaces
- LoongArch: kdump: Add memory reservation for old kernel
- LoongArch: defconfig: Enable a large number of configurations
- irqchip/loongson-pch-pic: 7a1000 int_clear reg must use 64bit write.
- LoongArch: Remove generic irq migration
- LoongArch: Adapted SECTION_SIZE_BITS with page size
- !4689  Remove WQ_FLAG_BOOKMARK flag
- sched: remove wait bookmarks
- filemap: remove use of wait bookmarks
- !5024 v2  vmemmap optimize bugfix
- mm: hugetlb_vmemmap: allow alloc vmemmap pages fallback to other nodes
- mm: hugetlb_vmemmap: fix hugetlb page number decrease failed on movable nodes
- !4653 [OLK-6.6] Add support for Mucse Network Adapter(N10/N400)
- drivers: initial support for rnp drivers from Mucse Technology
- !4935 RDMA/hns: Support userspace configuring congestion control algorithm with QP granularity
- RDMA/hns: Support userspace configuring congestion control algorithm with QP granularity
- RDMA/hns: Fix mis-modifying default congestion control algorithm
- !4993 v3  kworker: Fix the problem of ipsan performance degradation
- Add kernel compilation configuration options
- iscsi: use dynamic single thread workqueue to improve performance
- workqueue: add member for NUMA aware order workqueue and implement NUMA affinity for single thread workqueue
- !4930  erofs: fix lz4 inplace decompression
- erofs: fix lz4 inplace decompression
- !4082 【OLK-6.6】KVM: arm64: vtimer irq bypass support
- mbigen: probe mbigen driver with arch_initcall
- mbigen: vtimer: disable vtimer mbigen probe when vtimer_irqbypass disabled
- mbigen: Sets the regs related to vtimer irqbypass
- KVM: arm64: vgic-v3: Clearing pending status of vtimer on guest reset
- mbigen: vtimer: add support for MBIX1_CPPI_NEGEDGE_CLR_EN_SETR(CLRR)
- KVM: arm64: arch_timer: Make vtimer_irqbypass a Distributor attr
- KVM: arm64: vtimer: Expose HW-based vtimer interrupt in debugfs
- KVM: arm64: GICv4.1: Allow non-trapping WFI when using direct vtimer interrupt
- KVM: arm64: GICv4.1: Add support for MBIGEN save/restore
- KVM: arm64: arch_timer: Rework vcpu init/reset logic
- KVM: arm64: arch_timer: Probe vtimer irqbypass capability
- KVM: arm64: GICv4.1: Enable vtimer vPPI irqbypass config
- KVM: arm64: GICv4.1: Add direct injection capability to PPI registers
- KVM: arm64: vgic: Add helper for vtimer vppi info register
- KVM: arm64: GICv4.1: Inform the HiSilicon vtimer irqbypass capability
- irqchip/gic-v4.1: Probe vtimer irqbypass capability at RD level
- irqchip/gic-v4.1: Rework its_alloc_vcpu_sgis() to support vPPI allocation
- irqchip/gic-v4.1: Rework get/set_irqchip_state callbacks of GICv4.1-sgi chip
- irqchip/gic-v4.1: Extend VSGI command to support the new vPPI
- irqchip/gic-v4.1: Detect ITS vtimer interrupt bypass capability
- mbigen: vtimer mbigen driver support
- mbigen: vtimer: isolate mbigen vtimer funcs with macro
- !4875 [OLK-6.6] backport latest v6.8 iommu fixes
- iommufd/selftest: Don't check map/unmap pairing with HUGE_PAGES
- iommufd: Fix protection fault in iommufd_test_syz_conv_iova
- iommufd/selftest: Fix mock_dev_num bug
- iommufd: Fix iopt_access_list_id overwrite bug
- iommu/sva: Fix SVA handle sharing in multi device case
- !4867  ext4: regenerate buddy after block freeing failed if under fc replay
- ext4: regenerate buddy after block freeing failed if under fc replay
- !4851  cachefiles: fix memory leak in cachefiles_add_cache()
- cachefiles: fix memory leak in cachefiles_add_cache()
- !4913 RDMA/hns: Support SCC parameter configuration and reporting of the down/up event of the HNS RoCE network port
- RDMA/hns: Add support for sending port down event fastly
- RDMA/hns: Deliver net device event to ofed
- RDMA/hns: Support congestion control algorithm parameter configuration
- !4670 crypto HiSilicon round main line code
- crypto: hisilicon/qm - change function type to void
- crypto: hisilicon/qm - obtain stop queue status
- crypto: hisilicon/qm - add stop function by hardware
- crypto: hisilicon/sec - remove unused parameter
- crypto: hisilicon/sec2 - fix some cleanup issues
- crypto: hisilicon/sec2 - modify nested macro call
- crypto: hisilicon/sec2 - updates the sec DFX function register
- crypto: hisilicon - Fix smp_processor_id() warnings
- crypto: hisilicon/qm - dump important registers values before resetting
- crypto: hisilicon/qm - support get device state
- crypto: hisilicon/sec2 - optimize the error return process
- crypto: hisilicon/qm - delete a dbg function
- crypto: hisilicon/sec2 - Remove cfb and ofb
- crypto: hisilicon/zip - save capability registers in probe process
- crypto: hisilicon/sec2 - save capability registers in probe process
- crypto: hisilicon/hpre - save capability registers in probe process
- crypto: hisilicon/qm - save capability registers in qm init process
- crypto: hisilicon/qm - add a function to set qm algs
- crypto: hisilicon/qm - add comments and remove redundant array element
- crypto: hisilicon/qm - simplify the status of qm
- crypto: hisilicon/sgl - small cleanups for sgl.c
- crypto: hisilicon/zip - add zip comp high perf mode configuration
- crypto: hisilicon/qm - remove incorrect type cast
- crypto: hisilicon/qm - print device abnormal information
- crypto: hisilicon/trng - Convert to platform remove callback returning void
- crypto: hisilicon/sec - Convert to platform remove callback returning void
- crypto: hisilicon/qm - fix EQ/AEQ interrupt issue
- crypto: hisilicon/qm - alloc buffer to set and get xqc
- crypto: hisilicon/qm - check function qp num before alg register
- crypto: hisilicon/qm - fix the type value of aeq
- crypto: hisilicon/sec - fix for sgl unmmap problem
- crypto: hisilicon/zip - remove zlib and gzip
- crypto: hisilicon/zip - support deflate algorithm
- uacce: make uacce_class constant
- !4725 [OLK-6.6] merge upstream net-v6.7 all wangxun patches
- net: fill in MODULE_DESCRIPTION()s for wx_lib
- wangxun: select CONFIG_PHYLINK where needed
- net: wangxun: add ethtool_ops for msglevel
- net: wangxun: add coalesce options support
- net: wangxun: add ethtool_ops for ring parameters
- net: wangxun: add flow control support
- net: ngbe: convert phylib to phylink
- net: txgbe: use phylink bits added in libwx
- net: libwx: add phylink to libwx
- net: wangxun: remove redundant kernel log
- net: ngbe: add ethtool stats support
- net: txgbe: add ethtool stats support
- net: wangxun: move MDIO bus implementation to the library
- net: libwx: fix memory leak on free page
- net: libwx: support hardware statistics
- net: wangxun: fix changing mac failed when running
- !4841 Intel-sig: intel_idle: add Sierra Forest SoC support on 6.6
- intel_idle: add Sierra Forest SoC support
- !4834 ras: fix return type of log_arm_hw_error when not add CONFIG_RAS_ARM_EVENT_INFO config
- ras: fix return type of log_arm_hw_error when not add CONFIG_RAS_ARM_EVENT_INFO config
- !4845  PCI: Avoid potential out-of-bounds read in pci_dev_for_each_resource()
- PCI: Avoid potential out-of-bounds read in pci_dev_for_each_resource()
- !4773 Add loongarch kernel kvm support
- loongarch/kernel: Fix loongarch compilation error
- LoongArch: KVM: Add returns to SIMD stubs
- LoongArch: KVM: Streamline kvm_check_cpucfg() and improve comments
- LoongArch: KVM: Rename _kvm_get_cpucfg() to _kvm_get_cpucfg_mask()
- LoongArch: KVM: Fix input validation of _kvm_get_cpucfg() & kvm_check_cpucfg()
- irqchip/loongson-eiointc: Use correct struct type in eiointc_domain_alloc()
- LoongArch: KVM: Add LASX (256bit SIMD) support
- LoongArch: KVM: Add LSX (128bit SIMD) support
- LoongArch: KVM: Fix timer emulation with oneshot mode
- LoongArch: KVM: Remove kvm_acquire_timer() before entering guest
- LoongArch: KVM: Allow to access HW timer CSR registers always
- LoongArch: KVM: Remove SW timer switch when vcpu is halt polling
- LoongArch: KVM: Optimization for memslot hugepage checking
- LoongArch: Implement constant timer shutdown interface
- LoongArch: KVM: Add maintainers for LoongArch KVM
- LoongArch: KVM: Supplement kvm document about LoongArch-specific part
- LoongArch: KVM: Enable kvm config and add the makefile
- LoongArch: KVM: Implement vcpu world switch
- LoongArch: KVM: Implement kvm exception vectors
- LoongArch: KVM: Implement handle fpu exception
- LoongArch: KVM: Implement handle mmio exception
- LoongArch: KVM: Implement handle gspr exception
- LoongArch: KVM: Implement handle idle exception
- LoongArch: KVM: Implement handle iocsr exception
- LoongArch: KVM: Implement handle csr exception
- LoongArch: KVM: Implement kvm mmu operations
- LoongArch: KVM: Implement virtual machine tlb operations
- LoongArch: KVM: Implement vcpu timer operations
- LoongArch: KVM: Implement misc vcpu related interfaces
- LoongArch: KVM: Implement vcpu load and vcpu put operations
- LoongArch: KVM: Implement vcpu interrupt operations
- LoongArch: KVM: Implement fpu operations for vcpu
- LoongArch: KVM: Implement basic vcpu ioctl interfaces
- LoongArch: KVM: Implement basic vcpu interfaces
- LoongArch: KVM: Add vcpu related header files
- LoongArch: KVM: Implement VM related functions
- LoongArch: KVM: Implement kvm hardware enable, disable interface
- LoongArch: KVM: Implement kvm module related interface
- LoongArch: KVM: Add kvm related header files
- !3951 【OLK-6.6】KVM/arm64: support virt_dev irqbypass
- KVM: arm64: update arm64 openeuler_defconfig for CONFIG_VIRT_PLAT_DEV
- KVM: arm64: sdev: Support virq bypass by INT/VSYNC command
- KVM: arm64: kire: irq routing entry cached the relevant cache data
- KVM: arm64: Introduce shadow device
- virt_plat_dev: Register the virt platform device driver
- irqchip/gic-v3-its: Add virt platform devices MSI support
- irqchip/gic-v3-its: Alloc/Free device id from pools for virtual devices
- irqchip/gic-v3-its: Introduce the reserved device ID pools
- !4425 【OLK-6.6】arm64/nmi: Support for FEAT_NMI
- irqchip/gic-v3: Fix hard LOCKUP caused by NMI being masked
- config: enable CONFIG_ARM64_NMI and CONFIG_HARDLOCKUP_DETECTOR_PERF for arm64
- irqchip/gic-v3: Implement FEAT_GICv3_NMI support
- arm64/nmi: Add Kconfig for NMI
- arm64/nmi: Add handling of superpriority interrupts as NMIs
- arm64/irq: Document handling of FEAT_NMI in irqflags.h
- arm64/entry: Don't call preempt_schedule_irq() with NMIs masked
- arm64/nmi: Manage masking for superpriority interrupts along with DAIF
- KVM: arm64: Hide FEAT_NMI from guests
- arm64/cpufeature: Detect PE support for FEAT_NMI
- arm64/idreg: Add an override for FEAT_NMI
- arm64/hyp-stub: Enable access to ALLINT
- arm64/asm: Introduce assembly macros for managing ALLINT
- arm64/sysreg: Add definitions for immediate versions of MSR ALLINT
- arm64/booting: Document boot requirements for FEAT_NMI
- !4679  f2fs: fix to avoid dirent corruption
- f2fs: fix to avoid dirent corruption
- !4730  coresight: trbe: Enable ACPI based devices
- coresight: trbe: Enable ACPI based TRBE devices
- coresight: trbe: Add a representative coresight_platform_data for TRBE
- !4807 [OLK-6.6] Intel: backport KVM LAM from v6.8 to OLK-6.6
- KVM: x86: Use KVM-governed feature framework to track "LAM enabled"
- KVM: x86: Advertise and enable LAM (user and supervisor)
- KVM: x86: Virtualize LAM for user pointer
- KVM: x86: Virtualize LAM for supervisor pointer
- KVM: x86: Untag addresses for LAM emulation where applicable
- KVM: x86: Introduce get_untagged_addr() in kvm_x86_ops and call it in emulator
- KVM: x86: Remove kvm_vcpu_is_illegal_gpa()
- KVM: x86: Add & use kvm_vcpu_is_legal_cr3() to check CR3's legality
- KVM: x86/mmu: Drop non-PA bits when getting GFN for guest's PGD
- KVM: x86: Add X86EMUL_F_INVLPG and pass it in em_invlpg()
- KVM: x86: Add an emulation flag for implicit system access
- KVM: x86: Consolidate flags for __linearize()
- !4700  efivarfs: force RO when remounting if SetVariable is not supported
- efivarfs: force RO when remounting if SetVariable is not supported
- !4785  Support PV-sched feature
- KVM: arm64: Support the vCPU preemption check
- KVM: arm64: Add interface to support vCPU preempted check
- KVM: arm64: Support pvsched preempted via shared structure
- KVM: arm64: Implement PV_SCHED_FEATURES call
- KVM: arm64: Document PV-sched interface
- !4629 add sw64 architecture support
- drivers: cpufreq: add sw64 support
- drivers: clocksource: add sw64 support
- drivers: acpi: add sw64 support
- selftests: fix sw64 support
- perf: fix sw64 support
- perf: add sw64 support
- tools: fix basic sw64 support
- tools: add basic sw64 support
- sw64: fix ftrace support
- sw64: fix audit support
- sw64: fix kexec support
- sw64: fix PCI support
- sw64: fix KVM support
- sw64: fix module support
- sw64: fix ACPI support
- sw64: fix rrk support
- sw64: fix ELF support
- !4727 RAS: Report ARM processor information to userspace
- RAS: Report ARM processor information to userspace
- !4769 [sync] PR-4729:  serial: 8250: omap: Don't skip resource freeing if pm_runtime_resume_and_get() failed
- serial: 8250: omap: Don't skip resource freeing if pm_runtime_resume_and_get() failed
- !4781  x86/fpu: Stop relying on userspace for info to fault in xsave buffer
- x86/fpu: Stop relying on userspace for info to fault in xsave buffer
- !4787 v2  gfs2: Fix kernel NULL pointer dereference in gfs2_rgrp_dump
- gfs2: Fix kernel NULL pointer dereference in gfs2_rgrp_dump
- !4789 v2  fix CVE-2024-26590
- erofs: fix inconsistent per-file compression format
- erofs: simplify compression configuration parser
- !4736 PCIe and miniIO OLK-5.10 branch partial code round OLK-6.6 branch
- xhci:fix USB xhci controller issue
- spi: hisi-sfc-v3xx: return IRQ_NONE if no interrupts were detected
- Add the verification operation after the bus recovery operation obtains resources through the ACPI
- i2c: hisi: Add gpio bus recovery support
- gpio: hisi: Fix format specifier
- perf hisi-ptt: Fix one memory leakage in hisi_ptt_process_auxtrace_event()
- Fix the header file location error and adjust the function and structure version.
- hwtracing: hisi_ptt: Don't try to attach a task
- hwtracing: hisi_ptt: Optimize the trace data committing
- hwtracing: hisi_ptt: Handle the interrupt in hardirq context
- hwtracing: hisi_ptt: Disable interrupt after trace end
- !4802  Export vcpu stat via debugfs
- kvm: debugfs: add EXIT_REASON_PREEMPTION_TIMER to vcpu_stat
- kvm: debugfs: add fastpath msr_wr exits to debugfs statistics
- kvm: debugfs: Export x86 kvm exits to vcpu_stat
- kvm: debugfs: aarch64 export cpu time related items to debugfs
- kvm: debugfs: export remaining aarch64 kvm exit reasons to debugfs
- kvm: debugfs: Export vcpu stat via debugfs
- !4676 [OLK-6.6] kabi/iommu: Backport patches from upstream and maintainer tree
- iommu/sva: Restore SVA handle sharing
- iommu/arm-smmu-v3: Do not use GFP_KERNEL under as spinlock
- Revert "iommu/arm-smmu: Convert to domain_alloc_paging()"
- iommu/vt-d: Fix constant-out-of-range warning
- iommu/vt-d: Set SSADE when attaching to a parent with dirty tracking
- iommu/vt-d: Add missing dirty tracking set for parent domain
- iommu/vt-d: Wrap the dirty tracking loop to be a helper
- iommu/vt-d: Remove domain parameter for intel_pasid_setup_dirty_tracking()
- iommu/vt-d: Add missing device iotlb flush for parent domain
- iommu/vt-d: Update iotlb in nested domain attach
- iommu/vt-d: Add missing iotlb flush for parent domain
- iommu/vt-d: Add __iommu_flush_iotlb_psi()
- iommu/vt-d: Track nested domains in parent
- iommu: Make iommu_report_device_fault() return void
- iommu: Make iopf_group_response() return void
- iommu: Track iopf group instead of last fault
- iommu: Improve iopf_queue_remove_device()
- iommu: Use refcount for fault data access
- iommu: Refine locking for per-device fault data management
- iommu: Separate SVA and IOPF
- iommu: Make iommu_queue_iopf() more generic
- iommu: Prepare for separating SVA and IOPF
- iommu: Merge iommu_fault_event and iopf_fault
- iommu: Remove iommu_[un]register_device_fault_handler()
- iommu: Merge iopf_device_param into iommu_fault_param
- iommu: Cleanup iopf data structure definitions
- iommu: Remove unrecoverable fault data
- iommu/arm-smmu-v3: Remove unrecoverable faults reporting
- iommu: Move iommu fault data to linux/iommu.h
- iommu/iova: use named kmem_cache for iova magazines
- iommu/iova: Reorganise some code
- iommu/iova: Tidy up iova_cache_get() failure
- selftests/iommu: fix the config fragment
- iommufd: Reject non-zero data_type if no data_len is provided
- iommufd/iova_bitmap: Consider page offset for the pages to be pinned
- iommufd/selftest: Add mock IO hugepages tests
- iommufd/selftest: Hugepage mock domain support
- iommufd/selftest: Refactor mock_domain_read_and_clear_dirty()
- iommufd/selftest: Refactor dirty bitmap tests
- iommufd/iova_bitmap: Handle recording beyond the mapped pages
- iommufd/selftest: Test u64 unaligned bitmaps
- iommufd/iova_bitmap: Switch iova_bitmap::bitmap to an u8 array
- iommufd/iova_bitmap: Bounds check mapped::pages access
- powerpc/iommu: Fix the missing iommu_group_put() during platform domain attach
- powerpc: iommu: Bring back table group release_ownership() call
- iommu: Allow ops->default_domain to work when !CONFIG_IOMMU_DMA
- iommufd/selftest: Check the bus type during probe
- iommu/vt-d: Add iotlb flush for nested domain
- iommufd: Add data structure for Intel VT-d stage-1 cache invalidation
- iommufd/selftest: Add coverage for IOMMU_HWPT_INVALIDATE ioctl
- iommufd/selftest: Add IOMMU_TEST_OP_MD_CHECK_IOTLB test op
- iommufd/selftest: Add mock_domain_cache_invalidate_user support
- iommu: Add iommu_copy_struct_from_user_array helper
- iommufd: Add IOMMU_HWPT_INVALIDATE
- iommu: Add cache_invalidate_user op
- iommu: Don't reserve 0-length IOVA region
- iommu/sva: Fix memory leak in iommu_sva_bind_device()
- iommu/dma: Trace bounce buffer usage when mapping buffers
- iommu/tegra: Use tegra_dev_iommu_get_stream_id() in the remaining places
- acpi: Do not return struct iommu_ops from acpi_iommu_configure_id()
- iommu: Mark dev_iommu_priv_set() with a lockdep
- iommu: Mark dev_iommu_get() with lockdep
- iommu/of: Use -ENODEV consistently in of_iommu_configure()
- iommmu/of: Do not return struct iommu_ops from of_iommu_configure()
- iommu: Remove struct iommu_ops *iommu from arch_setup_dma_ops()
- iommu: Set owner token to SVA domain
- mm: Deprecate pasid field
- iommu: Support mm PASID 1:n with sva domains
- mm: Add structure to keep sva information
- iommu: Add mm_get_enqcmd_pasid() helper function
- iommu/vt-d: Remove mm->pasid in intel_sva_bind_mm()
- iommu: Change kconfig around IOMMU_SVA
- iommu: Extend LPAE page table format to support custom allocators
- iommu: Allow passing custom allocators to pgtable drivers
- iommu: Clean up open-coded ownership checks
- iommu: Retire bus ops
- iommu/arm-smmu: Don't register fwnode for legacy binding
- iommu: Decouple iommu_domain_alloc() from bus ops
- iommu: Validate that devices match domains
- iommu: Decouple iommu_present() from bus ops
- iommu: Factor out some helpers
- iommu: Map reserved memory as cacheable if device is coherent
- iommu/vt-d: Move inline helpers to header files
- iommu/vt-d: Remove unused vcmd interfaces
- iommu/vt-d: Remove unused parameter of intel_pasid_setup_pass_through()
- iommu/vt-d: Refactor device_to_iommu() to retrieve iommu directly
- iommu/virtio: Add ops->flush_iotlb_all and enable deferred flush
- iommu/virtio: Make use of ops->iotlb_sync_map
- iommu/arm-smmu: Convert to domain_alloc_paging()
- iommu/arm-smmu: Pass arm_smmu_domain to internal functions
- iommu/arm-smmu: Implement IOMMU_DOMAIN_BLOCKED
- iommu/arm-smmu: Convert to a global static identity domain
- iommu/arm-smmu: Reorganize arm_smmu_domain_add_master()
- iommu/arm-smmu-v3: Remove ARM_SMMU_DOMAIN_NESTED
- iommu/arm-smmu-v3: Master cannot be NULL in arm_smmu_write_strtab_ent()
- iommu/arm-smmu-v3: Add a type for the STE
- iommu/apple-dart: Fix spelling mistake "grups" -> "groups"
- iommu/apple-dart: Use readl instead of readl_relaxed for consistency
- iommu/apple-dart: Add support for t8103 USB4 DART
- iommu/apple-dart: Write to all DART_T8020_STREAM_SELECT
- dt-bindings: iommu: dart: Add t8103-usb4-dart compatible
- iommufd: Do not UAF during iommufd_put_object()
- iommufd: Add iommufd_ctx to iommufd_put_object()
- iommu/vt-d: Support enforce_cache_coherency only for empty domains
- iommu: Flow ERR_PTR out from __iommu_domain_alloc()
- iommu/dma: Use a large flush queue and timeout for shadow_on_flush
- iommu/dma: Allow a single FQ in addition to per-CPU FQs
- iommu/s390: Disable deferred flush for ISM devices
- s390/pci: Use dma-iommu layer
- s390/pci: prepare is_passed_through() for dma-iommu
- iommu: Allow .iotlb_sync_map to fail and handle s390's -ENOMEM return
- iommu/dart: Remove the force_bypass variable
- iommu/dart: Call apple_dart_finalize_domain() as part of alloc_paging()
- iommu/dart: Convert to domain_alloc_paging()
- iommu/dart: Move the blocked domain support to a global static
- iommu/dart: Use static global identity domains
- iommufd: Convert to alloc_domain_paging()
- iommu/vt-d: Use ops->blocked_domain
- iommu/vt-d: Update the definition of the blocking domain
- iommu: Move IOMMU_DOMAIN_BLOCKED global statics to ops->blocked_domain
- iommu: change iommu_map_sgtable to return signed values
- powerpc/iommu: Do not do platform domain attach atctions after probe
- iommu: Fix return code in iommu_group_alloc_default_domain()
- iommu: Do not use IOMMU_DOMAIN_DMA if CONFIG_IOMMU_DMA is not enabled
- iommu: Remove duplicate include
- iommu: Improve map/unmap sanity checks
- iommu: Retire map/unmap ops
- iommu/tegra-smmu: Update to {map,unmap}_pages
- iommu/sun50i: Update to {map,unmap}_pages
- iommu/rockchip: Update to {map,unmap}_pages
- iommu/omap: Update to {map,unmap}_pages
- iommu/exynos: Update to {map,unmap}_pages
- iommu/omap: Convert to generic_single_device_group()
- iommu/ipmmu-vmsa: Convert to generic_single_device_group()
- iommu/rockchip: Convert to generic_single_device_group()
- iommu/sprd: Convert to generic_single_device_group()
- iommu/sun50i: Convert to generic_single_device_group()
- iommu: Add generic_single_device_group()
- iommu: Remove useless group refcounting
- iommu: Convert remaining simple drivers to domain_alloc_paging()
- iommu: Convert simple drivers with DOMAIN_DMA to domain_alloc_paging()
- iommu: Add ops->domain_alloc_paging()
- iommu: Add __iommu_group_domain_alloc()
- iommu: Require a default_domain for all iommu drivers
- iommu/sun50i: Add an IOMMU_IDENTITIY_DOMAIN
- iommu/mtk_iommu: Add an IOMMU_IDENTITIY_DOMAIN
- iommu/ipmmu: Add an IOMMU_IDENTITIY_DOMAIN
- iommu/qcom_iommu: Add an IOMMU_IDENTITIY_DOMAIN
- iommu: Remove ops->set_platform_dma_ops()
- iommu/msm: Implement an IDENTITY domain
- iommu/omap: Implement an IDENTITY domain
- iommu/tegra-smmu: Support DMA domains in tegra
- iommu/tegra-smmu: Implement an IDENTITY domain
- iommu/exynos: Implement an IDENTITY domain
- iommu: Allow an IDENTITY domain as the default_domain in ARM32
- iommu: Reorganize iommu_get_default_domain_type() to respect def_domain_type()
- iommu/mtk_iommu_v1: Implement an IDENTITY domain
- iommu/tegra-gart: Remove tegra-gart
- iommu/fsl_pamu: Implement a PLATFORM domain
- iommu: Add IOMMU_DOMAIN_PLATFORM for S390
- powerpc/iommu: Setup a default domain and remove set_platform_dma_ops
- iommu: Add IOMMU_DOMAIN_PLATFORM
- iommu: Add iommu_ops->identity_domain
- iommu/vt-d: debugfs: Support dumping a specified page table
- iommu/vt-d: debugfs: Create/remove debugfs file per {device, pasid}
- iommu/vt-d: debugfs: Dump entry pointing to huge page
- iommu/virtio: Add __counted_by for struct viommu_request and use struct_size()
- iommu/arm-smmu-v3-sva: Remove bond refcount
- iommu/arm-smmu-v3-sva: Remove unused iommu_sva handle
- iommu/arm-smmu-v3: Rename cdcfg to cd_table
- iommu/arm-smmu-v3: Update comment about STE liveness
- iommu/arm-smmu-v3: Cleanup arm_smmu_domain_finalise
- iommu/arm-smmu-v3: Move CD table to arm_smmu_master
- iommu/arm-smmu-v3: Refactor write_ctx_desc
- iommu/arm-smmu-v3: move stall_enabled to the cd table
- iommu/arm-smmu-v3: Encapsulate ctx_desc_cfg init in alloc_cd_tables
- iommu/arm-smmu-v3: Replace s1_cfg with cdtab_cfg
- iommu/arm-smmu-v3: Move ctx_desc out of s1_cfg
- iommu/tegra-smmu: Drop unnecessary error check for for debugfs_create_dir()
- powerpc: Remove extern from function implementations
- iommufd: Organize the mock domain alloc functions closer to Joerg's tree
- iommu/vt-d: Disallow read-only mappings to nest parent domain
- iommu/vt-d: Add nested domain allocation
- iommu/vt-d: Set the nested domain to a device
- iommu/vt-d: Make domain attach helpers to be extern
- iommu/vt-d: Add helper to setup pasid nested translation
- iommu/vt-d: Add helper for nested domain allocation
- iommu/vt-d: Extend dmar_domain to support nested domain
- iommufd: Add data structure for Intel VT-d stage-1 domain allocation
- iommufd/selftest: Add coverage for IOMMU_HWPT_ALLOC with nested HWPTs
- iommufd/selftest: Add nested domain allocation for mock domain
- iommu: Add iommu_copy_struct_from_user helper
- iommufd: Add a nested HW pagetable object
- iommu: Pass in parent domain with user_data to domain_alloc_user op
- iommufd: Share iommufd_hwpt_alloc with IOMMUFD_OBJ_HWPT_NESTED
- iommufd: Derive iommufd_hwpt_paging from iommufd_hw_pagetable
- iommufd/device: Wrap IOMMUFD_OBJ_HWPT_PAGING-only configurations
- iommufd: Rename IOMMUFD_OBJ_HW_PAGETABLE to IOMMUFD_OBJ_HWPT_PAGING
- iommu: Add IOMMU_DOMAIN_NESTED
- iommufd: Only enforce cache coherency in iommufd_hw_pagetable_alloc
- iommufd: Fix spelling errors in comments
- !4767  reserve space for arch related structures
- kabi: reserve space for struct mfd_cell
- kabi: reserve space for struct irq_work
- !4709  mtd: Fix gluebi NULL pointer dereference caused by ftl notifier
- mtd: Fix gluebi NULL pointer dereference caused by ftl notifier
- !4738  blk-mq: fix IO hang from sbitmap wakeup race
- blk-mq: fix IO hang from sbitmap wakeup race
- !4561  sched: migtate user interface from smart grid to sched bpf
- sched: migtate user interface from smart grid to sched bpf
- !4026 [OLK-6.6]Add support for Mont-TSSE
- add support for Mont-TSSE Driver
- !4564 v2  reserve space for arm64 related structures
- kabi: reserve space for processor.h
- kabi: reserve space for fb.h
- kabi: reserve space for efi.h
- !4675 v5  Backport vDPA migration support patches
- vdpa: add CONFIG_VHOST_VDPA_MIGRATION
- vdpa: add vmstate header file
- vhost-vdpa: add reset state params to indicate reset level
- vhost-vdpa: allow set feature VHOST_F_LOG_ALL when been negotiated.
- vhost-vdpa: fix msi irq request err
- vhost-vdpa: Allow transparent MSI IOV
- vhost: add VHOST feature VHOST_BACKEND_F_BYTEMAPLOG
- vhost-vdpa: add uAPI for device migration status
- vdpa: add vdpa device migration status ops
- vhost-vdpa: add uAPI for device buffer
- vdpa: add device state operations
- vhost-vdpa: add uAPI for logging
- vdpa: add log operations
- !4660 Intel: Backport to fix In Field Scan(IFS) SAF for GNR & SRF
- platform/x86/intel/ifs: Call release_firmware() when handling errors.
- !4652 RDMA/hns: Support SCC context query and DSCP configuration.
- RDMA/hns: Support DSCP of userspace
- RDMA/hns: Append SCC context to the raw dump of QP Resource
- !4628  fs:/dcache.c: fix negative dentry flag warning in dentry_free
- fs:/dcache.c: fix negative dentry flag warning in dentry_free
- !4654 hisi_ptt: Move type check to the beginning of hisi_ptt_pmu_event_init()
- hwtracing: hisi_ptt: Move type check to the beginning of hisi_ptt_pmu_event_init()
- !3880 ima: Add IMA digest lists extension
- ima: add default INITRAMFS_FILE_METADATA and EVM_DEFAULT_HASH CONFIG
- ima: don't allow control characters in policy path
- ima: Add max size for IMA digest database
- config: add digest list options for arm64 and x86
- evm: Propagate choice of HMAC algorithm in evm_crypto.c
- ima: Execute parser to upload digest lists not recognizable by the kernel
- evm: Extend evm= with x509. allow_metadata_writes and complete values
- ima: Add parser keyword to the policy
- ima: Allow direct upload of digest lists to securityfs
- ima: Search key in the built-in keyrings
- certs: Introduce search_trusted_key()
- KEYS: Provide a function to load keys from a PGP keyring blob
- KEYS: Introduce load_pgp_public_keyring()
- KEYS: Provide PGP key description autogeneration
- KEYS: PGP data parser
- PGPLIB: Basic packet parser
- PGPLIB: PGP definitions (RFC 4880)
- rsa: add parser of raw format
- mpi: introduce mpi_key_length()
- ima: Add Documentation/security/IMA-digest-lists.txt
- ima: Introduce appraise_exec_immutable policy
- ima: Introduce appraise_exec_tcb policy
- ima: Introduce exec_tcb policy
- ima: Add meta_immutable appraisal type
- evm: Add support for digest lists of metadata
- ima: Add support for appraisal with digest lists
- ima: Add support for measurement with digest lists
- ima: Load all digest lists from a directory at boot time
- ima: Introduce new hook DIGEST_LIST_CHECK
- ima: Introduce new securityfs files
- ima: Prevent usage of digest lists not measured or appraised
- ima: Add parser of compact digest list
- ima: Use ima_show_htable_value to show violations and hash table data
- ima: Generalize policy file operations
- ima: Generalize ima_write_policy() and raise uploaded data size limit
- ima: Generalize ima_read_policy()
- ima: Allow choice of file hash algorithm for measurement and audit
- ima: Add enforce-evm and log-evm modes to strictly check EVM status
- init: Add kernel option to force usage of tmpfs for rootfs
- gen_init_cpio: add support for file metadata
- initramfs: read metadata from special file METADATA!!!
- initramfs: add file metadata
- !4542  Support feature TLBI DVMBM
- KVM: arm64: Implement the capability of DVMBM
- KVM: arm64: Add kvm_arch::sched_cpus and sched_lock
- KVM: arm64: Add kvm_vcpu_arch::sched_cpus and pre_sched_cpus
- KVM: arm64: Probe and configure DVMBM capability on HiSi CPUs
- KVM: arm64: Support a new HiSi CPU type
- KVM: arm64: Only probe Hisi ncsnp feature on Hisi CPUs
- KVM: arm64: Add support for probing Hisi ncsnp capability
- KVM: arm64: Probe Hisi CPU TYPE from ACPI/DTB
- !4661 [OLK-6.6] Fix gic support for Phytium S2500
- Enable CONFIG_ARCH_PHYTIUM
- Fix gic support for Phytium S2500
- !4644  f2fs: explicitly null-terminate the xattr list
- f2fs: explicitly null-terminate the xattr list
- !4637  Using smmu IIDR registers
- iommu/arm-smmu-v3: Enable iotlb_sync_map according to SMMU_IIDR
- Revert "iommu/arm-smmu-v3: Add a SYNC command to avoid broken page table prefetch"
- !4506  ubi: fastmap: Optimize ubi wl algorithm to improve flash service life
- ubi: fastmap: Add control in 'UBI_IOCATT' ioctl to reserve PEBs for filling pools
- ubi: fastmap: Add module parameter to control reserving filling pool PEBs
- ubi: fastmap: Fix lapsed wear leveling for first 64 PEBs
- ubi: fastmap: Get wl PEB even ec beyonds the 'max' if free PEBs are run out
- ubi: fastmap: may_reserve_for_fm: Don't reserve PEB if fm_anchor exists
- ubi: fastmap: Remove unneeded break condition while filling pools
- ubi: fastmap: Wait until there are enough free PEBs before filling pools
- ubi: fastmap: Use free pebs reserved for bad block handling
- ubi: Replace erase_block() with sync_erase()
- ubi: fastmap: Allocate memory with GFP_NOFS in ubi_update_fastmap
- ubi: fastmap: erase_block: Get erase counter from wl_entry rather than flash
- ubi: fastmap: Fix missed ec updating after erasing old fastmap data block
- !4624 6.6: i2c: Optimized the value setting of maxwrite limit to fifo depth - 1
- i2c: hisi: Add clearing tx aempty interrupt operation
- i2c: hisi: Optimized the value setting of maxwrite limit to fifo depth - 1
- !4631  Add kabi reserve
- drm/ttm: Add kabi reserve in ttm_tt.h
- drm/ttm: Add kabi reserve in ttm_resource.h
- drm/ttm: Add kabi reserve in ttm_bo.h
- drm: Add kabi reserve in drm_gpu_scheduler.h
- drm: Add kabi reserve in drm_syncobj.h
- drm: Add kabi reserve in drm_plane.h
- drm: Add kabi reserve in drm_modeset_lock.h
- drm: Add kabi reserve in drm_mode_config.h
- sbitmap: Add kabi reserve
- xarray: Reserve kabi for xa_state
- delayacct: Reserve kabi for task_delay_info

* Mon Feb 26 2024 huangzq6 <huangzhenqiang2@huawei.com> - 6.6.0-10.0.0.7
- add signature for vmlinux

* Wed Feb 21 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-10.0.0.6
- !4598 [OLK-6.6] Add iommu support for Phytium S2500
- Add iommu support for Phytium S2500
- !4596 add sw64 architecture support
- sw64: fix build support
- sw64: add dynamic turning on/off cores support
- sw64: add dynamic frequency scaling support
- sw64: add kgdb support
- sw64: add jump_label support
- sw64: add uprobe support
- sw64: add kprobe support
- sw64: add kernel relocation support
- sw64: add ftrace support
- sw64: add hibernation support
- sw64: add suspend support
- sw64: add eBPF JIT support
- sw64: add kdump support
- sw64: add kexec support
- sw64: add perf events support
- sw64: add qspinlock support
- sw64: add stacktrace support
- !4567  Support feature TWED
- KVM: arm64: Make use of TWED feature
- arm64: cpufeature: TWED support detection
- !4383 [OLK-6.6] kabi: add more x86/cpu reservations in cpu feature bits and bug bits
- kabi: reserve x86 cpu bug fields
- kabi: reserve x86 cpu capability fields
- !3695 x86: Add x86 related kabi reservations
- x86: Add x86 related kabi reservations
- !4589  fs,hugetlb: fix NULL pointer dereference in hugetlbs_fill_super
- fs,hugetlb: fix NULL pointer dereference in hugetlbs_fill_super
- !4451 v5  kabi reserve patches
- kabi: reserve space for arm64 cpufeature related structure
- kabi: reserve space for power management related structure
- energy_model: Add kabi_reserve
- pm: pm.h: Add kabi_reserve
- pm: pm_domain.h: Add kabi_reserve
- drm: drm_gem.h: Add kabi_reserve
- drm: drm_fourcc.h: Add kabi_reserve
- drm: drm_file.h: Add kabi_reserve
- drm: drm_fb_helper.h: Add kabi_reserve
- drm: drm_drv.h: Add kabi_reserve
- drm: drm_device.h: Add kabi_reserve
- drm: drm_crtc.h: Add kabi_reserve
- drm: drm_connector.h: Add kabi_reserve
- drm: drm_client.h: Add kabi_reserve
- drm: drm_atomic.h: Add kabi_reserve
- irqdomain: Add kabi_reserve in irqdomain
- irq_desc: Add kabi_reserve in irq_desc
- irq: Add kabi_reserve in irq
- interrupt: Add kabi_reserve in interrupt.h
- msi: Add kabi_reserve in msi.h
- kabi: reserve space for struct cpu_stop_work
- KABI: reserve space for struct input_dev
- !4557  Add ZONE_EXTMEM to avoid kabi broken
- openeuler_defconfig: enable CONFIG_ZONE_EXTMEM for arm64
- mm: add ZONE_EXTMEM for future extension to avoid kabi broken
- !4569 add sw64 architecture support
- sw64: add KVM support
- sw64: add EFI support
- sw64: add DMA support
- sw64: add ACPI support
- sw64: add device trees
- sw64: add MSI support
- sw64: add PCI support
- sw64: add default configs
- sw64: add NUMA support
- sw64: add SMP support
- sw64: add VDSO support
- sw64: add some library functions
- sw64: add some other routines
- sw64: add some common routines
- sw64: add module support
- sw64: add basic IO support
- sw64: add FPU support
- !3498  fuse: reserve space for future expansion
- kabi:fuse: reserve space for future expansion
- !4435 v2  kabi: reserve space for struct ptp_clock
- kabi: reserve space for struct ptp_clock
- !4584 v5  kabi reserve
- kabi: reserve space for struct clocksource
- kabi: reserve space for struct timer_list
- kabi: reserve space for struct ptp_clock_info
- kabi: reserve space for posix clock related structure
- kabi: reserve space for hrtimer related structures
- kabi: reserve space for kobject related structures
- !4049  openeuler_defconfig: Disable new HW_RANDOM support for arm64
- openeuler_defconfig: Disable new HW_RANDOM support for arm64
- !4582 cgroup/hugetlb: hugetlb accounting
- mm: memcg: fix split queue list crash when large folio migration
- hugetlb: memcg: account hugetlb-backed memory in memory controller
- memcontrol: only transfer the memcg data for migration
- memcontrol: add helpers for hugetlb memcg accounting
- !4347 【OLK-6.6】AMD: CXL RCH Protocol Error Handling supporting
- openeuler_defconfig: Enable CONFIG_PCIEAER_CXL=y
- cxl/hdm: Fix && vs || bug
- cxl/pci: Change CXL AER support check to use native AER
- cxl/core/regs: Rework cxl_map_pmu_regs() to use map->dev for devm
- cxl/core/regs: Rename phys_addr in cxl_map_component_regs()
- PCI/AER: Unmask RCEC internal errors to enable RCH downstream port error handling
- PCI/AER: Forward RCH downstream port-detected errors to the CXL.mem dev handler
- cxl/pci: Disable root port interrupts in RCH mode
- cxl/pci: Add RCH downstream port error logging
- cxl/pci: Map RCH downstream AER registers for logging protocol errors
- cxl/pci: Update CXL error logging to use RAS register address
- PCI/AER: Refactor cper_print_aer() for use by CXL driver module
- cxl/pci: Add RCH downstream port AER register discovery
- cxl/port: Remove Component Register base address from struct cxl_port
- cxl/pci: Remove Component Register base address from struct cxl_dev_state
- cxl/hdm: Use stored Component Register mappings to map HDM decoder capability
- cxl/pci: Store the endpoint's Component Register mappings in struct cxl_dev_state
- cxl/port: Pre-initialize component register mappings
- cxl/port: Rename @comp_map to @reg_map in struct cxl_register_map
- !4390 [OLK-6.6] Add kdump support for Phytium S2500
- Add kdump support for Phytium S2500
- !4459 v2  Introduce page eject for arm64
- config: update defconfig for PAGE_EJECT
- mm: page_eject: Introuduce page ejection
- mm/memory-failure: introduce soft_online_page
- mm/hwpoison: Export symbol soft_offline_page
- !3699 [OLK-6.6] Enable CONFIG_IOMMUFD and CONFIG_VFIO_DEVICE_CDEV in x86/arm64 defconfig
- defconfig: enable CONFIG_IOMMUFD and CONFIG_VFIO_DEVICE_CDEV
- !4571  scsi: iscsi: kabi: KABI reservation for iscsi_transport
- scsi: iscsi: kabi: KABI reservation for iscsi_transport
- !4546 RDMA/hns: Support MR management
- RDMA/hns: Simplify 'struct hns_roce_hem' allocation
- RDMA/hns: Support adaptive PBL hopnum
- RDMA/hns: Support flexible umem page size
- RDMA/hns: Alloc MTR memory before alloc_mtt()
- RDMA/hns: Refactor mtr_init_buf_cfg()
- RDMA/hns: Refactor mtr find
- !4576 v6  Add support for ecmdq
- iommu/arm-smmu-v3: Allow disabling ECMDQs at boot time
- iommu/arm-smmu-v3: Add support for less than one ECMDQ per core
- iommu/arm-smmu-v3: Add arm_smmu_ecmdq_issue_cmdlist() for non-shared ECMDQ
- iommu/arm-smmu-v3: Ensure that a set of associated commands are inserted in the same ECMDQ
- iommu/arm-smmu-v3: Add support for ECMDQ register mode
- !3697 enable ARM64/X86 CONFIG_BPF_LSM config
- lsm: enable CONFIG_BPF_LSM for use bpf in lsm program
- !4537  mainline cgroup bufix
- cgroup: use legacy_name for cgroup v1 disable info
- blk-cgroup: bypass blkcg_deactivate_policy after destroying
- cgroup: Check for ret during cgroup1_base_files cft addition
- !4438  kabi: reserve space for workqueue subsystem related structure
- kabi: reserve space for workqueue subsystem related structure
- !4570 v2  scsi: reserve space for structures in scsi
- scsi: reserve space for structures in scsi
- !4566 v2  reserve kabi space for some structures
- libnvdimm: reserve space for structures in libnvdimm
- ata: libata: reserve space for structures in libata
- elevator: reserve space for structures in elevator

* Wed Feb 7 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-9.0.0.5
- !4545 add sw64 architecture support
- sw64: add signal handling support
- sw64: add system call support
- sw64: add hugetlb support
- sw64: add memory management
- sw64: add hardware match support
- sw64: add process management
- sw64: add exception handling support
- sw64: add irq handling support
- sw64: add timer support
- sw64: add topology setup routine
- sw64: add boot and setup routines
- sw64: add some other headers
- sw64: add ELF support
- sw64: add common headers
- sw64: add atomic/locking headers
- sw64: add CPU definition headers
- sw64: add build infrastructure
- !4423  kabi: reserve space for pci subsystem and thread_info
- kabi: reserve space for pci subsystem related structure
- kabi: reserve space for thread_info structure
- !3997 [OLK-6.6] openEuler-24.03 Phytium S2500 IPMI adaption
- ipmi_si: Phytium S2500 workaround for MMIO-based IPMI
- !3841 Add support for Hygon family 18h model 5h HD-Audio
- ALSA: hda: Fix single byte writing issue for Hygon family 18h model 5h
- ALSA: hda: Add support for Hygon family 18h model 5h HD-Audio
- !3835 Add support for Hygon model 6h L3 PMU
- perf/x86/uncore: Add L3 PMU support for Hygon family 18h model 6h
- !3698 enable ARM64/X86_64 CONFIG_MPTCP/CONFIG_MPTCP_IPV6 config
- mptcp: enable config CONFIG_MPTCP and CONFIG_MPTCP_IPV6
- !3696 enable ARM64/X86 CONFIG_XDP_SOCKET、CONFIG_XDP_SOCKETS_DIAG config
- xdp: enable config CONFIG_XDP_SOCKETS and CONFIG_XDP_SOCKETS_DIAG
- !3183 [OLK-6.6] Add support Zhaoxin GPIO pinctrl
- configs: add CONFIG_PINCTRL_ZHAOXIN and KX7000 to m
- Add support Zhaoxin GPIO pinctrl
- !4539  nvme: kabi: KABI reservation for nvme_ctrl
- nvme: kabi: KABI reservation for nvme_ctrl
- !4527 v3  block: kabi: KABI reservation for blk-cgroup
- block: kabi: KABI reservation for blk-cgroup
- !4554 v3  kabi: Reserve KABI slots for fs module
- sysfs: kabi: Reserve KABI slots for bin_attribute struct
- profs: kabi: Reserve KABI slots for proc_ops struct
- dax: kabi: Reserve KABI slots for dax_* struct
- fs: kabi: Reserve KABI slots for nameidata struct
- xattr: kabi: Reserve KABI slots for xattr_handler struct
- kernfs: kabi: Reserve KABI slots for kernfs_* struct
- fanotify: kabi: Reserve KABI slots for fsnotify_* struct
- fscrypt: kabi: Reserve KABI slots for fscrypt_operations struct
- !3932  [OLK-6.6] 同步OLK-5.10 SMMU HTTU补丁
- iommu/arm-smmu-v3: Add Arm SMMU HTTU config
- vfio/iommu_type1: Add support for manual dirty log clear
- vfio/iommu_type1: Optimize dirty bitmap population based on iommu HWDBM
- vfio/iommu_type1: Add HWDBM status maintenance
- iommu/arm-smmu-v3: Realize support_dirty_log iommu ops
- iommu/arm-smmu-v3: Realize clear_dirty_log iommu ops
- iommu/arm-smmu-v3: Realize sync_dirty_log iommu ops
- iommu/arm-smmu-v3: Realize switch_dirty_log iommu ops
- iommu/arm-smmu-v3: Add feature detection for BBML
- iommu/arm-smmu-v3: Enable HTTU for stage1 with io-pgtable mapping
- iommu/io-pgtable-arm: Add and realize clear_dirty_log ops
- iommu/io-pgtable-arm: Add and realize sync_dirty_log ops
- iommu/io-pgtable-arm: Add and realize merge_page ops
- iommu/io-pgtable-arm: Add and realize split_block ops
- iommu/io-pgtable-arm: Add __arm_lpae_set_pte
- iommu/io-pgtable-arm: Add quirk ARM_HD and ARM_BBMLx
- iommu: Introduce dirty log tracking framework
- iommu/arm-smmu-v3: Add support for Hardware Translation Table Update
- !4560 v5  block: reserve kabi space for general block layer structures
- block: reserve kabi space for general block layer structures
- !4168  Reserve syscall entries for kabi compatibility
- kabi: Reserve syscall entries for kabi compatibility
- arch: Reserve map_shadow_stack() syscall number for all architectures
- !4532 v2  fscache: reserve kabi for fscache structures
- fscache: reserve kabi for fscache structures
- !4543 v2  fs/dcache: kabi: KABI reservation for dentry
- fs/dcache: kabi: KABI reservation for dentry
- !4533  quota: kabi: KABI reservation for quota
- quota: kabi: KABI reservation for quota
- !4528 v3  jbd2: kabi: KABI reservation for jbd2
- jbd2: kabi: KABI reservation for jbd2
- !4483  block: kabi: KABI reservation for iocontext
- block: kabi: KABI reservation for iocontext
- !4455  scsi: iscsi: kabi: KABI reservation for scsi_transport_iscsi.h
- scsi: iscsi: kabi: KABI reservation for scsi_transport_iscsi.h
- !4456  scsi: scsi_transport_fc: kabi: KABI reservation for scsi_transport_fc
- scsi: scsi_transport_fc: kabi: KABI reservation for scsi_transport_fc
- !4472  nvmet-fc: kabi: KABI reservation for nvme_fc_port_template
- nvmet-fc: kabi: KABI reservation for nvme_fc_port_template
- !4474  scsi: libsas: kabi: KABI reservation for libsas
- scsi: libsas: kabi: KABI reservation for libsas
- !4463 RDMA/hns: Backport bugfix
- RDMA/hns: Fix memory leak in free_mr_init()
- RDMA/hns: Remove unnecessary checks for NULL in mtr_alloc_bufs()
- RDMA/hns: Add a max length of gid table
- RDMA/hns: Response dmac to userspace
- RDMA/hns: Rename the interrupts
- RDMA/hns: Support SW stats with debugfs
- RDMA/hns: Add debugfs to hns RoCE
- RDMA/hns: Fix inappropriate err code for unsupported operations
- !3838 Add support for Hygon model 4h EDAC
- EDAC/amd64: Adjust UMC channel for Hygon family 18h model 6h
- EDAC/amd64: Add support for Hygon family 18h model 6h
- EDAC/amd64: Add support for Hygon family 18h model 5h
- EDAC/mce_amd: Use struct cpuinfo_x86.logical_die_id for Hygon NodeId
- EDAC/amd64: Adjust address translation for Hygon family 18h model 4h
- EDAC/amd64: Add support for Hygon family 18h model 4h
- EDAC/amd64: Get UMC channel from the 6th nibble for Hygon
- !4408 v2  kabi: reserve space for struct acpi_device and acpi_scan_handler
- kabi: reserve space for struct acpi_device and acpi_scan_handler
- !4495  KABI reservation for driver
- audit: kabi: Remove extra semicolons
- ipmi: kabi: KABI reservation for ipmi
- mmc: kabi: KABI reservation for mmc
- mtd: kabi: KABI reservation for mtd
- tty: kabi: KABI reservation for tty
- !3831 Add support for loading Hygon microcode
- x86/microcode/hygon: Add microcode loading support for Hygon processors
- !4356 【OLK-6.6】AMD: support the UMC Performance Counters for Zen4
- perf vendor events amd: Add Zen 4 memory controller events
- perf/x86/amd/uncore: Pass through error code for initialization failures, instead of -ENODEV
- perf/x86/amd/uncore: Fix uninitialized return value in amd_uncore_init()
- perf/x86/amd/uncore: Add memory controller support
- perf/x86/amd/uncore: Add group exclusivity
- perf/x86/amd/uncore: Use rdmsr if rdpmc is unavailable
- perf/x86/amd/uncore: Move discovery and registration
- perf/x86/amd/uncore: Refactor uncore management
- !4494 v2  writeback: kabi: KABI reservation for writeback
- writeback: kabi: KABI reservation for writeback
- !4491  sched/rt: Fix possible warn when push_rt_task
- sched/rt: Fix possible warn when push_rt_task
- !4396 [OLK-6.6] perf/x86/zhaoxin/uncore: add NULL pointer check after kzalloc
- perf/x86/zhaoxin/uncore: add NULL pointer check after kzalloc
- !4405  mm: improve performance of accounted kernel memory allocations
- mm: kmem: properly initialize local objcg variable in current_obj_cgroup()
- mm: kmem: reimplement get_obj_cgroup_from_current()
- percpu: scoped objcg protection
- mm: kmem: scoped objcg protection
- mm: kmem: make memcg keep a reference to the original objcg
- mm: kmem: add direct objcg pointer to task_struct
- mm: kmem: optimize get_obj_cgroup_from_current()
- !4500  fs: kabi: KABI reservation for vfs
- fs: kabi: KABI reservation for vfs
- !4505  iov_iter: kabi: KABI reservation for iov_iter
- iov_iter: kabi: KABI reservation for iov_iter
- !4486 v2  openeuler_defconfig: enable CONFIG_PAGE_CACHE_LIMIT
- openeuler_defconfig: enable CONFIG_PAGE_CACHE_LIMIT
- !4489 【OLK-6.6】AMD: fix brstack event for AMD Zen CPU
- perf/x86/amd: Reject branch stack for IBS events
- !4376 [OLK-6.6] Add Phytium Display Engine support to the OLK-6.6.
- DRM: Phytium display DRM doc
- DRM: Phytium display DRM driver
- !4385 v2  sched: remove __GENKSYMS__ used
- sched: remove __GENKSYMS__ used
- !4449  memory tiering: calculate abstract distance based on ACPI HMAT
- dax, kmem: calculate abstract distance with general interface
- acpi, hmat: calculate abstract distance with HMAT
- acpi, hmat: refactor hmat_register_target_initiators()
- memory tiering: add abstract distance calculation algorithms management
- !4362  ubifs: Queue up space reservation tasks if retrying many times
- ubifs: Queue up space reservation tasks if retrying many times
- !4450  change zswap's default allocator to zsmalloc
- openeuler_defconfig: set ZSWAP_ZPOOL_DEFAULT to ZSMALLOC
- zswap: change zswap's default allocator to zsmalloc
- !4298 misc for controlling fd
- cgroup/misc: support cgroup misc to control fd
- filescgroup: add adapter for legacy and misc cgroup
- filescgroup: rename filescontrol.c to legacy-filescontrol.c
- filescgroup: Add CONFIG_CGROUP_FILES at files_cgroup in files_struct
- filescgroup: remove files of dfl_cftypes.
- !4173  block: remove precise_iostat
- block: remove precise_iostat
- !4481  cred: kabi: KABI reservation for cred
- cred: kabi: KABI reservation for cred
- !4418  KABI: Add reserve space for sched structures
- KABI: Reserve space for fwnode.h
- KABI: Reserve space for struct module
- fork: Allocate a new task_struct_resvd object for fork task
- KABI: Add reserve space for sched structures
- !4355 v4  kabi reserve for memcg and cgroup_bpf
- cgroup_bpf/kabi: reserve space for cgroup_bpf related structures
- memcg/kabi: reserve space for memcg related structures
- !4476  net/kabi: Reserve space for net structures
- net/kabi: Reserve space for net structures
- !4440 v2  kabi:dma:add kabi reserve for dma_map_ops structure
- kabi:dma:add kabi reserve for dma_map_ops structure
- !4479  mm/memcontrol: fix out-of-bound access in mem_cgroup_sysctls_init
- mm/memcontrol: fix out-of-bound access in mem_cgroup_sysctls_init
- !4429  Remove unnecessary KABI reservation
- crypto: kabi: Removed unnecessary KABI reservation
- !4211  blk-mq: avoid housekeeping CPUs scheduling a worker on a non-housekeeping CPU
- blk-mq: avoid housekeeping CPUs scheduling a worker on a non-housekeeping CPU
- !4407  sched/topology: Fix cpus hotplug deadlock in check_node_limit()
- sched/topology: Fix cpus hotplug deadlock in check_node_limit()
- !4351  kabi: net: reserve space for net subsystem related structure
- kabi: net: reserve space for net subsystem related structure
- !4453  arm64/ascend: Make enable_oom_killer feature depends on ASCEND_FEATURE
- arm64/ascend: Make enable_oom_killer feature depends on ASCEND_FEATURE
- !4386  fix static scanning issues
- bond: fix static scanning issue with bond_broadcast_arp_or_nd_table_header
- tcp: fix static scanning issue with sysctl_local_port_allocation
- !4403 v2  kabi: net: reserve space for net related structure
- kabi: net: reserve space for net related structure
- !4406 v2  net/kabi: reserve space for net related structures
- net/kabi: reserve space for net related structures
- !4398 v2  vfs: reserve kabi space for vfs related structures
- vfs: reserve kabi space for vfs related structures
- !4372  kabi: reserve space for struct rate_sample
- kabi: reserve space for struct rate_sample
- !4322  cgroup_writeback: fix deadlock
- cgroup_writeback: fix deadlock in cgroup1_writeback
- !4414 Support srq record doorbell and support query srq context
- RDMA/hns: Support SRQ record doorbell
- RDMA/hns: Support SRQ restrack ops for hns driver
- RDMA/core: Add support to dump SRQ resource in RAW format
- RDMA/core: Add dedicated SRQ resource tracker function
- !4165  tlb: reserve fields for struct mmu_gather
- tlb: reserve fields for struct mmu_gather
- !4178  OLK-6.6 cred backport for kabi reserve
- cred: get rid of CONFIG_DEBUG_CREDENTIALS
- groups: Convert group_info.usage to refcount_t
- cred: switch to using atomic_long_t
- cred: add get_cred_many and put_cred_many
- !4343 v3  reserve KABI slots for file system or storage related structures
- mtd: kabi: Reserve KABI slots for mtd_device_xxx_register() related structures
- pipe: kabi: Reserve KABI slots for pipe_inode_info structure
- exportfs: kabi: Reserve KABI slots for export_operations structure
- !4200  Expose swapcache stat for memcg v1
- memcg: remove unused do_memsw_account in memcg1_stat_format
- memcg: expose swapcache stat for memcg v1
- !4140 backport some patches for kunpeng hccs
- soc: hisilicon: kunpeng_hccs: Support the platform with PCC type3 and interrupt ack
- doc: kunpeng_hccs: Fix incorrect email domain name
- soc: hisilicon: kunpeng_hccs: Remove an unused blank line
- soc: hisilicon: kunpeng_hccs: Add failure log for no _CRS method
- soc: hisilicon: kunpeng_hccs: Fix some incorrect format strings
- soc/hisilicon: kunpeng_hccs: Convert to platform remove callback returning void
- soc: kunpeng_hccs: Migrate to use generic PCC shmem related macros
- hwmon: (xgene) Migrate to use generic PCC shmem related macros
- i2c: xgene-slimpro: Migrate to use generic PCC shmem related macros
- ACPI: PCC: Add PCC shared memory region command and status bitfields
- !3641  Make the cpuinfo_cur_freq interface read correctly
- cpufreq: CPPC: Keep the target core awake when reading its cpufreq rate
- arm64: cpufeature: Export cpu_has_amu_feat()
- !4410  config: Update openeuler_defconfig base on current
- config: x86: Update openeuler_defconfig base on current source code
- config: arm64: Update openeuler_defconfig base on current source code
- !4400 v2  soc: hisilicon: hisi_hbmdev: Fix compile error
- soc: hisilicon: hisi_hbmdev: Fix compile error
- !4397 v2  cryptd: kabi: Fixed boot panic
- cryptd: kabi: Fixed boot panic
- !4393 [OLK-6.6] crypto: sm4: fix the build warning issue of sm4 driver
- crypto: sm4: fix the build warning issue of sm4 driver
- !4368 cgroup/misc: fix compiling waring
- cgroup/misc: fix compiling waring
- !4364 [OLK-6.6] crypto: sm3/sm4: fix zhaoxin sm3/sm4 driver file name mismatch issue
- crypto: sm3/sm4: fix zhaoxin sm3/sm4 driver file name mismatch issue
- !4204  arm64: Turn on CONFIG_IPI_AS_NMI in openeuler_defconfig
- arm64: Turn on CONFIG_IPI_AS_NMI in openeuler_defconfig
- !4314  tracing: Reserve kabi fields
- tracing: Reserve kabi fields
- !4301 v3  kabi: reserve space for cpu cgroup and cpuset cgroup related structures
- kabi: reserve space for cpu cgroup and cpuset cgroup related structures
- !4177  kabi: reserve space for bpf related structures
- kabi: reserve space for bpf related structures
- !4354 v7  KABI reservation for IMA and crypto
- ima: kabi: KABI reservation for IMA
- crypto: kabi: KABI reservation for crypto
- !4346 v2  pciehp: fix a race between pciehp and removing operations by sysfs
- pciehp: fix a race between pciehp and removing operations by sysfs
- !4146  tcp: fix compilation issue when CONFIG_SYSCTL is disabled
- tcp: fix compilation issue when CONFIG_SYSCTL is disabled
- !4066  smb: client: fix OOB in receive_encrypted_standard()
- smb: client: fix OOB in receive_encrypted_standard()
- !3995  net: config: enable network config
- net: config: enable network config
- !3745 【OLK-6.6】Support SMT control on arm64
- config: enable CONFIG_HOTPLUG_SMT for arm64
- arm64: Kconfig: Enable HOTPLUG_SMT
- arm64: topology: Support SMT control on ACPI based system
- arch_topology: Support SMT control for OF based system
- arch_topology: Support basic SMT control for the driver
- !4000  audit: kabi: KABI reservation for audit
- audit: kabi: KABI reservation for audit
- !4249  ubifs: fix possible dereference after free
- ubifs: fix possible dereference after free
- !3178 [OLK-6.6] Driver for Zhaoxin SM3 and SM4 algorithm
- configs: Add Zhaoxin SM3 and SM4 algorithm configs
- Add support for Zhaoxin GMI SM4 Block Cipher algorithm
- Add support for Zhaoxin GMI SM3 Secure Hash algorithm
- !4219  Initial cleanups for vCPU hotplug
- riscv: convert to use arch_cpu_is_hotpluggable()
- riscv: Switch over to GENERIC_CPU_DEVICES
- LoongArch: convert to use arch_cpu_is_hotpluggable()
- LoongArch: Use the __weak version of arch_unregister_cpu()
- LoongArch: Switch over to GENERIC_CPU_DEVICES
- x86/topology: convert to use arch_cpu_is_hotpluggable()
- x86/topology: use weak version of arch_unregister_cpu()
- x86/topology: Switch over to GENERIC_CPU_DEVICES
- arm64: convert to arch_cpu_is_hotpluggable()
- arm64: setup: Switch over to GENERIC_CPU_DEVICES using arch_register_cpu()
- drivers: base: Print a warning instead of panic() when register_cpu() fails
- drivers: base: Move cpu_dev_init() after node_dev_init()
- drivers: base: add arch_cpu_is_hotpluggable()
- drivers: base: Implement weak arch_unregister_cpu()
- drivers: base: Allow parts of GENERIC_CPU_DEVICES to be overridden
- drivers: base: Use present CPUs in GENERIC_CPU_DEVICES
- ACPI: Move ACPI_HOTPLUG_CPU to be disabled on arm64 and riscv
- Loongarch: remove arch_*register_cpu() exports
- x86/topology: remove arch_*register_cpu() exports
- x86: intel_epb: Don't rely on link order
- arch_topology: Make register_cpu_capacity_sysctl() tolerant to late CPUs
- arm64, irqchip/gic-v3, ACPI: Move MADT GICC enabled check into a helper
- ACPI: scan: Rename acpi_scan_device_not_present() to be about enumeration
- ACPI: scan: Use the acpi_device_is_present() helper in more places
- !4215  pci: Enable acs for QLogic HBA cards
- pci: Enable acs for QLogic HBA cards
- !4267  ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()
- ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()
- !4317 [OLK-6.6] cputemp: zhaoxin: fix HWMON_THERMAL namespace not import issue
- cputemp: zhaoxin: fix HWMON_THERMAL namespace not import issue.
- !3682 cgroup and ns kabi reserve
- cgroup/misc: reserve kabi for future misc development
- cgroup/psi: reserve kabi for future psi development
- namespace: kabi: reserve for future namespace development
- cgroup: kabi: reserve space for cgroup frame
- !4291 fs:/dcache.c: fix negative dentry limit not complete problem
- fs:/dcache.c: fix negative dentry limit not complete problem
- !4292 powerpc: Add PVN support for HeXin C2000 processor
- powerpc: Add PVN support for HeXin C2000 processor
- !3129 [OLK-6.6] Driver for Zhaoxin AES and SHA algorithm
- Add Zhaoxin aes/sha items in openeuler_config
- Add support for Zhaoxin SHA algorithm
- Add support for Zhaoxin AES algorithm
- !3959  kabi: mm: add kabi reserve for mm structure
- kabi: mm: add kabi reserve for mm structure
- !4046 [OLK-6.6] Add gic support for Phytium S2500
- Add gic support for Phytium S2500
- !3126 [OLK-6.6] Driver for Zhaoxin HW Random Number Generator
- Add CONFIG_HW_RANDOM_ZHAOXIN in openeuler_defconfig
- Add support for Zhaoxin HW Random Number Generator
- !3169 [OLK-6.6] x86/perf: Add uncore performance events support for Zhaoxin CPU
- x86/perf: Add uncore performance events support for Zhaoxin CPU
- !3187 [OLK-6.6] Add support for Zhaoxin I2C controller
- configs: add CONFIG_I2C_ZHAOXIN to m
- Add support for Zhaoxin I2C controller
- !4164  arch/mm/fault: fix major fault accounting when retrying under per-VMA lock
- arch/mm/fault: fix major fault accounting when retrying under per-VMA lock
- !3903  kabi: Reserve space for perf subsystem related structures
- kabi: Reserve space for perf subsystem related structures
- !4128  drm/qxl: Fix missing free_irq
- drm/qxl: Fix missing free_irq
- !4050  kabi: net: reserve space for net
- kabi: net: reserve space for net sunrpc subsystem related structure
- kabi: net: reserve space for net rdma subsystem related structure
- kabi: net: reserve space for net netfilter subsystem related structure
- kabi: net: reserve space for net can subsystem related structure
- kabi: net: reserve space for net bpf subsystem related structure
- kabi: net: reserve space for net base subsystem related structure
- !3774 [OLK-6.6] sched/fair: Scan cluster before scanning LLC in wake-up path
- sched/fair: Use candidate prev/recent_used CPU if scanning failed for cluster wakeup
- sched/fair: Scan cluster before scanning LLC in wake-up path
- sched: Add cpus_share_resources API
- !3125 [OLK-6.6] Driver for Zhaoxin Serial ATA IDE
- configs: enable CONFIG_SATA_ZHAOXIN to y
- Add support for Zhaoxin Serial ATA IDE.
- !4044  Set CONFIG_NODES_SHIFT to 8
- openeuler_defconfig: set CONFIG_NODES_SHIFT to 8 for both x86_64/ARM64
- x86/Kconfig: allow NODES_SHIFT to be set on MAXSMP
- !3840 Remove Hygon SMBus IMC detecting
- i2c-piix4: Remove the IMC detecting for Hygon SMBus
- !3839 Add support for Hygon model 4h k10temp
- hwmon/k10temp: Add support for Hygon family 18h model 5h
- hwmon/k10temp: Add support for Hygon family 18h model 4h
- !3837 Add support for Hygon model 4h northbridge
- x86/amd_nb: Add support for Hygon family 18h model 6h
- x86/amd_nb: Add support for Hygon family 18h model 5h
- x86/amd_nb: Add northbridge support for Hygon family 18h model 4h
- x86/amd_nb: Add Hygon family 18h model 4h PCI IDs
- !4199  Support large folio for mlock
- mm: mlock: avoid folio_within_range() on KSM pages
- mm: mlock: update mlock_pte_range to handle large folio
- mm: handle large folio when large folio in VM_LOCKED VMA range
- mm: add functions folio_in_range() and folio_within_vma()
- !4147  arm64: Add CONFIG_IPI_AS_NMI to IPI as NMI feature
- arm64: Add CONFIG_IPI_AS_NMI to IPI as NMI feature
- !4159 Backport iommufd dirty tracking from v6.7
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
- !4109  PCI: add a member in 'struct pci_bus' to record the original 'pci_ops'
- PCI: add a member in 'struct pci_bus' to record the original 'pci_ops'
- !4108  PCI/AER: increments pci bus reference count in aer-inject process
- PCI/AER: increments pci bus reference count in aer-inject process
- !4114  pci: do not save 'PCI_BRIDGE_CTL_BUS_RESET'
- pci: do not save 'PCI_BRIDGE_CTL_BUS_RESET'
- !4113  PCI: check BIR before mapping MSI-X Table
- PCI: check BIR before mapping MSI-X Table
- !4112  PCI: Fail MSI-X mapping if MSI-X Table offset is out of range of BAR space
- PCI: Fail MSI-X mapping if MSI-X Table offset is out of range of BAR space
- !4110  PCI: Add MCFG quirks for some Hisilicon Chip host controllers
- PCI: Add MCFG quirks for some Hisilicon Chip host controllers
- !4111  sysrq: avoid concurrently info printing by 'sysrq-trigger'
- sysrq: avoid concurrently info printing by 'sysrq-trigger'
- !4107  ntp: Avoid undefined behaviour in second_overflow()
- ntp: Avoid undefined behaviour in second_overflow()
- !4105  PCI/sysfs: Take reference on device to be removed
- PCI/sysfs: Take reference on device to be removed
- !3836 Add support for Hygon model 4h QoS
- x86/resctrl: Add Hygon QoS support
- !4154  Add per-node vmstat info and memcg info
- mm/vmstat: move pgdemote_* out of CONFIG_NUMA_BALANCING
- mm/vmstat: move pgdemote_* to per-node stats
- mm: memcg: add THP swap out info for anonymous reclaim
- !4170  mm/ksm: generalize ksm_process_profit
- mm/ksm: generalize ksm_process_profit
- !4120  arm_mpam: support mpam feature in OLK-6.6
- arm_mpam: control memory bandwidth with hard limit flag
- fs/resctrl: Remove the limit on the number of CLOSID
- arm_mpam: resctrl: Update the rmid reallocation limit
- arm_mpam: resctrl: Call resctrl_exit() in the event of errors
- arm_mpam: resctrl: Tell resctrl about cpu/domain online/offline
- perf/arm-cmn: Stop claiming all the resources
- arm64: mpam: Select ARCH_HAS_CPU_RESCTRL
- arm_mpam: resctrl: Add dummy definition for free running counters
- arm_mpam: resctrl: Add empty definitions for fine-grained enables
- arm_mpam: resctrl: Add empty definitions for pseudo lock
- untested: arm_mpam: resctrl: Allow monitors to be configured
- arm_mpam: resctrl: Add resctrl_arch_rmid_read() and resctrl_arch_reset_rmid()
- arm_mpam: resctrl: Allow resctrl to allocate monitors
- untested: arm_mpam: resctrl: Add support for mbm counters
- untested: arm_mpam: resctrl: Add support for MB resource
- arm_mpam: resctrl: Add rmid index helpers
- arm64: mpam: Add helpers to change a tasks and cpu mpam partid/pmg values
- arm_mpam: resctrl: Add CDP emulation
- arm_mpam: resctrl: Implement helpers to update configuration
- arm_mpam: resctrl: Add resctrl_arch_get_config()
- arm_mpam: resctrl: Implement resctrl_arch_reset_resources()
- arm_mpam: resctrl: Pick a value for num_rmid
- arm_mpam: resctrl: Pick the caches we will use as resctrl resources
- arm_mpam: resctrl: Add boilerplate cpuhp and domain allocation
- arm_mpam: Add helper to reset saved mbwu state
- arm_mpam: Use long MBWU counters if supported
- arm_mpam: Probe for long/lwd mbwu counters
- arm_mpam: Track bandwidth counter state for overflow and power management
- arm_mpam: Add mpam_msmon_read() to read monitor value
- arm_mpam: Add helpers to allocate monitors
- arm_mpam: Probe and reset the rest of the features
- arm_mpam: Allow configuration to be applied and restored during cpu online
- arm_mpam: Use the arch static key to indicate when mpam is enabled
- arm_mpam: Register and enable IRQs
- arm_mpam: Extend reset logic to allow devices to be reset any time
- arm_mpam: Add a helper to touch an MSC from any CPU
- arm_mpam: Reset MSC controls from cpu hp callbacks
- arm_mpam: Merge supported features during mpam_enable() into mpam_class
- arm_mpam: Probe the hardware features resctrl supports
- arm_mpam: Probe MSCs to find the supported partid/pmg values
- arm_mpam: Add cpuhp callbacks to probe MSC hardware
- arm_mpam: Add MPAM MSC register layout definitions
- arm_mpam: Add the class and component structures for ris firmware described
- arm_mpam: Add probe/remove for mpam msc driver and kbuild boiler plate
- dt-bindings: arm: Add MPAM MSC binding
- ACPI / MPAM: Parse the MPAM table
- drivers: base: cacheinfo: Add helper to find the cache size from cpu+level
- cacheinfo: Expose the code to generate a cache-id from a device_node
- cacheinfo: Set cache 'id' based on DT data
- cacheinfo: Allow for >32-bit cache 'id'
- ACPI / PPTT: Add a helper to fill a cpumask from a cache_id
- ACPI / PPTT: Add a helper to fill a cpumask from a processor container
- ACPI / PPTT: Find PPTT cache level by ID
- ACPI / PPTT: Provide a helper to walk processor containers
- untested: KVM: arm64: Force guest EL1 to use user-space's partid configuration
- arm64: mpam: Context switch the MPAM registers
- KVM: arm64: Disable MPAM visibility by default, and handle traps
- KVM: arm64: Fix missing traps of guest accesses to the MPAM registers
- arm64: cpufeature: discover CPU support for MPAM
- arm64: head.S: Initialise MPAM EL2 registers and disable traps
- x86/resctrl: Move the filesystem portions of resctrl to live in '/fs/'
- x86/resctrl: Move the filesystem bits to headers visible to fs/resctrl
- fs/resctrl: Add boiler plate for external resctrl code
- x86/resctrl: Drop __init/__exit on assorted symbols
- x86/resctrl: Describe resctrl's bitmap size assumptions
- x86/resctrl: Claim get_domain_from_cpu() for resctrl
- x86/resctrl: Move get_config_index() to a header
- x86/resctrl: Move thread_throttle_mode_init() to be managed by resctrl
- x86/resctrl: Make resctrl_arch_pseudo_lock_fn() take a plr
- x86/resctrl: Make prefetch_disable_bits belong to the arch code
- x86/resctrl: Allow an architecture to disable pseudo lock
- x86/resctrl: Allow resctrl_arch_mon_event_config_write() to return an error
- x86/resctrl: Change mon_event_config_{read,write}() to be arch helpers
- x86/resctrl: Add resctrl_arch_is_evt_configurable() to abstract BMEC
- x86/resctrl: Export the is_mbm_*_enabled() helpers to asm/resctrl.h
- x86/resctrl: Stop using the for_each_*_rdt_resource() walkers
- x86/resctrl: Move max_{name,data}_width into resctrl code
- x86/resctrl: Move monitor exit work to a restrl exit call
- x86/resctrl: Move monitor init work to a resctrl init call
- x86/resctrl: Add a resctrl helper to reset all the resources
- x86/resctrl: Move resctrl types to a separate header
- x86/resctrl: Wrap resctrl_arch_find_domain() around rdt_find_domain()
- x86/resctrl: Export resctrl fs's init function
- x86/resctrl: Remove rdtgroup from update_cpu_closid_rmid()
- x86/resctrl: Add helper for setting CPU default properties
- x86/resctrl: Move ctrlval string parsing links away from the arch code
- x86/resctrl: Add a helper to avoid reaching into the arch code resource list
- x86/resctrl: Separate arch and fs resctrl locks
- x86/resctrl: Move domain helper migration into resctrl_offline_cpu()
- x86/resctrl: Add CPU offline callback for resctrl work
- x86/resctrl: Allow overflow/limbo handlers to be scheduled on any-but cpu
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
- x86/resctrl: Move rmid allocation out of mkdir_rdt_prepare()
- x86/resctrl: Create helper for RMID allocation and mondata dir creation
- x86/resctrl: kfree() rmid_ptrs from resctrl_exit()
- tick/nohz: Move tick_nohz_full_mask declaration outside the #ifdef
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
- !3834 Add support for Hygon model 4h IOAPIC
- iommu/hygon: Add support for Hygon family 18h model 4h IOAPIC
- !3830 Add support for Hygon model 5h CPU cache
- x86/cpu: Get LLC ID for Hygon family 18h model 5h
- !3311 Add support for Hygon model 4h CPU topology
- x86/cpu/hygon: Fix __max_die_per_package for Hygon family 18h model 4h
- !3124 [OLK-6.6] Add support for Zhaoxin HDAC and codec
- ALSA: hda: Add support of Zhaoxin NB HDAC codec
- ALSA: hda: Add support of Zhaoxin NB HDAC
- ALSA: hda: Add support of Zhaoxin SB HDAC
- !3098 [OLK-6.6] Add support for Zhaoxin Processors
- x86/cpu: Add detect extended topology for Zhaoxin CPUs
- x86/cpufeatures: Add Zhaoxin feature bits
- !3742 arch/powerpc: add ppc little endian openuler defconfig
- arch/powerpc: add ppc little endian openuler defconfig
- !4099 Intel: Backport SRF LBR branch counter support to kernel v6.6
- perf/x86/intel: Support branch counters logging
- perf/x86/intel: Reorganize attrs and is_visible
- perf: Add branch_sample_call_stack
- perf/x86: Add PERF_X86_EVENT_NEEDS_BRANCH_STACK flag
- perf: Add branch stack counters
- !3177 [OLK-6.6] Add MWAIT Cx support for Zhaoxin CPUs
- Add MWAIT Cx support for Zhaoxin CPUs
- !3170 [OLK-6.6] rtc: Fix set RTC time delay 500ms on some Zhaoxin SOCs
- rtc: Fix set RTC time delay 500ms on some Zhaoxin SOCs
- !3131 [OLK-6.6] Driver for Zhaoxin CPU core temperature monitoring
- Add CONFIG_SENSORS_ZHAOXIN_CPUTEMP in openeuler_defconfig
- Add support for Zhaoxin core temperature monitoring
- !3102 [OLK-6.6] x86/mce: Add Centaur MCA support
- x86/mce: Add Centaur MCA support
- !4116 Intel: Backport GNR/SRF PMU uncore support to kernel v6.6
- perf/x86/intel/uncore: Support Sierra Forest and Grand Ridge
- perf/x86/intel/uncore: Support IIO free-running counters on GNR
- perf/x86/intel/uncore: Support Granite Rapids
- perf/x86/uncore: Use u64 to replace unsigned for the uncore offsets array
- perf/x86/intel/uncore: Generic uncore_get_uncores and MMIO format of SPR
- !4115 Intel: Backport In Field Scan(IFS) SAF & Array BIST support for GNR & SRF
- platform/x86/intel/ifs: ARRAY BIST for Sierra Forest
- platform/x86/intel/ifs: Add new error code
- platform/x86/intel/ifs: Add new CPU support
- platform/x86/intel/ifs: Metadata validation for start_chunk
- platform/x86/intel/ifs: Validate image size
- platform/x86/intel/ifs: Gen2 Scan test support
- platform/x86/intel/ifs: Gen2 scan image loading
- platform/x86/intel/ifs: Refactor image loading code
- platform/x86/intel/ifs: Store IFS generation number
- !4103 [OLK-6.6] Intel: microcode restructuring backport
- x86/setup: Make relocated_ramdisk a local variable of relocate_initrd()
- x86/microcode/intel: Add a minimum required revision for late loading
- x86/microcode: Prepare for minimal revision check
- x86/microcode: Handle "offline" CPUs correctly
- x86/apic: Provide apic_force_nmi_on_cpu()
- x86/microcode: Protect against instrumentation
- x86/microcode: Rendezvous and load in NMI
- x86/microcode: Replace the all-in-one rendevous handler
- x86/microcode: Provide new control functions
- x86/microcode: Add per CPU control field
- x86/microcode: Add per CPU result state
- x86/microcode: Sanitize __wait_for_cpus()
- x86/microcode: Clarify the late load logic
- x86/microcode: Handle "nosmt" correctly
- x86/microcode: Clean up mc_cpu_down_prep()
- x86/microcode: Get rid of the schedule work indirection
- x86/microcode: Mop up early loading leftovers
- x86/microcode/amd: Use cached microcode for AP load
- x86/microcode/amd: Cache builtin/initrd microcode early
- x86/microcode/amd: Cache builtin microcode too
- x86/microcode/amd: Use correct per CPU ucode_cpu_info
- x86/microcode: Remove pointless apply() invocation
- x86/microcode/intel: Rework intel_find_matching_signature()
- x86/microcode/intel: Reuse intel_cpu_collect_info()
- x86/microcode/intel: Rework intel_cpu_collect_info()
- x86/microcode/intel: Unify microcode apply() functions
- x86/microcode/intel: Switch to kvmalloc()
- x86/microcode/intel: Save the microcode only after a successful late-load
- x86/microcode/intel: Simplify early loading
- x86/microcode/intel: Cleanup code further
- x86/microcode/intel: Simplify and rename generic_load_microcode()
- x86/microcode/intel: Simplify scan_microcode()
- x86/microcode/intel: Rip out mixed stepping support for Intel CPUs
- x86/microcode/32: Move early loading after paging enable
- x86/boot/32: Temporarily map initrd for microcode loading
- x86/microcode: Provide CONFIG_MICROCODE_INITRD32
- x86/boot/32: Restructure mk_early_pgtbl_32()
- x86/boot/32: De-uglify the 2/3 level paging difference in mk_early_pgtbl_32()
- x86/boot: Use __pa_nodebug() in mk_early_pgtbl_32()
- x86/boot/32: Disable stackprotector and tracing for mk_early_pgtbl_32()
- x86/microcode/amd: Fix snprintf() format string warning in W=1 build
- !4102 Intel: Backport Sierra Forest(SRF) perf cstate support to kernel OLK-6.6
- perf/x86/intel/cstate: Add Grand Ridge support
- perf/x86/intel/cstate: Add Sierra Forest support
- x86/smp: Export symbol cpu_clustergroup_mask()
- perf/x86/intel/cstate: Cleanup duplicate attr_groups
- !4104  arm64: Add the arm64.nolse command line option
- arm64: Add the arm64.nolse command line option
- !4093 introduce smart_grid zone
- smart_grid: introduce smart_grid cmdline
- smart_grid: cpufreq: introduce smart_grid cpufreq control
- smart_grid: introduce smart_grid_strategy_ctrl sysctl
- smart_grid: introduce /proc/pid/smart_grid_level
- sched: introduce smart grid qos zone
- config: enable CONFIG_QOS_SCHED_SMART_GRID by default
- sched: smart grid: init sched_grid_qos structure on QOS purpose
- sched: Introduce smart grid scheduling strategy for cfs

* Wed Jan 31 2024 Jialin Zhang <zhangjialin11@huawei.com> - 6.6.0-6.0.0.4
- Module.kabi_aarch64 and Module.kabi_x86_64 v1

* Tue Jan 23 2024 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-6.0.0.3
- !4087  backport two page_owner patchsets:
- mm/page_owner: record and dump free_pid and free_tgid
- tools/mm: update the usage output to be more organized
- tools/mm: fix the default case for page_owner_sort
- tools/mm: filter out timestamps for correct collation
- tools/mm: remove references to free_ts from page_owner_sort
- mm/page_owner: remove free_ts from page_owner output
- !4070  Backport etmem feature to OLK 6.6
- etmem: enable etmem configurations
- etmem: add original kernel swap enabled options
- etmem: add etmem swap feature
- mm: Export symbol reclaim_pages
- etmem: add etmem scan feature
- mm: Export symbol walk_page_range
- mm: Export symbol __pud_trans_huge_lock
- etmem: add ETMEM scan feature CONFIG to mm/Kconfig
- etmem: add ETMEM feature CONFIG to mm/Kconfig
- !3444  LoongArch: fix some pci problems
- LoongArch: pci root bridige set acpi companion only when not acpi_disabled.
- PCI: irq: Add early_param pci_irq_limit to limit pci irq numbers
- PCI: fix X server auto probe fail when both ast and etnaviv drm present
- PCI: LS7A2000: fix GPU card error
- PCI: LS7A2000: fix pm transition of devices under pcie port
- LoongArch: fix some PCIE card not scanning properly
- PCI: fix kabi error caused by pm_suspend_target_state
- PCI: PM: fix pcie mrrs restoring
- PCI: Check if the pci controller can use both CFG0 and CFG1 mode to access configuration space
- PCI: Check if entry->offset already exist for mem resource
- LS7A2000: Add quirk for OHCI device rev 0x02
- !4027 [OLK-6.6] Intel RDT non-contiguous CBM support
- Documentation/x86: Document resctrl's new sparse_masks
- x86/resctrl: Add sparse_masks file in info
- x86/resctrl: Enable non-contiguous CBMs in Intel CAT
- x86/resctrl: Rename arch_has_sparse_bitmaps
- !4098  sched: programmable: Fix is_cpu_allowed build error
- sched: programmable: Fix is_cpu_allowed build error
- !4072 cgroup/misc: openeuler_defconfig open misc config by default
- cgroup/misc: openeuler_defconfig open misc config by default
- !4053  sched: basic infrastructure for scheduler bpf
- openeuler_defconfig: enable CONFIG_BPF_SCHED
- sched: programmable: Add hook in can_migrate_task()
- sched: programmable: Add hook in select_task_rq_fair()
- sched: introduce bpf_sched_enable()
- sched: basic infrastructure for scheduler bpf
- sched: programmable: Add user interface of task tag
- sched: programmable: Add user interface of task group tag
- sched: programmable: Add a tag for the task group
- sched: programmable: Add a tag for the task
- sched: programmable: Introduce bpf sched
- !4068  mm/oom_kill: fix NULL pointer dereference in memcg_print_bad_task()
- mm/oom_kill: fix NULL pointer dereference in memcg_print_bad_task()
- !4036  ubi: fix slab-out-of-bounds in ubi_eba_get_ldesc+0xfb/0x130
- ubi: fix slab-out-of-bounds in ubi_eba_get_ldesc+0xfb/0x130
- !3971  optimize inlining
- make OPTIMIZE_INLINING config editable
- Revert "compiler: remove CONFIG_OPTIMIZE_INLINING entirely"
- !3631  drm: fix free illegal pointer when create drm_property_blob failed
- drm: fix free illegal pointer when create drm_property_blob failed
- !3958  Revert "drm/prime: Unexport helpers for fd/handle conversion"
- Revert "drm/prime: Unexport helpers for fd/handle conversion"
- !3670 Add initial openeuler_defconfig for riscv64
- config: add initial openeuler_defconfig for riscv64
- !3895  Spark SQL scenario bpf readahead optimization synchronization to OLK-6.6
- selftests/bpf: Update the demo file_read_pattern to run on libbpf 1.0+
- VFS: Rolling Back the fmode macro definition and structure members
- selftests/bpf: add demo for file read pattern detection
- ext4: add trace for the read and release of regular file
- xfs: add trace for read and release of regular file
- fs: add helper fs_file_read_do_trace()
- vfs: add bare tracepoints for vfs read and release
- readahead: introduce FMODE_CTL_WILLNEED to read first 2MB of file
- !3964  drivers: hooks: add bonding driver vendor hooks
- drivers: hooks: add bonding driver vendor hooks
- !3996  hfs: fix null-ptr-deref in hfs_find_init()
- hfs: fix null-ptr-deref in hfs_find_init()
- !3976  Introduce dynamic pool feature
- mm/dynamic_pool: enable CONFIG_DYNAMIC_POOL on x86_64 and arm64 by default
- mm/dynamic_pool: add Document for dynamic hugetlb feature
- mm/dynamic_pool: compatible with memory hwpoison
- mm/dynamic_pool: compatible with HugeTLB Vmemmap
- mm/dynamic_pool: compatible with HugeTLB dissolve
- mm/dynamic_pool: disable THP for task attached with dpool
- mm/dynamic_pool: fill dpool with pagelist
- mm/dynamic_pool: add tracepoints for dpool
- mm/dynamic_pool: support HugeTLB page allocation from dpool
- mm/dynamic_pool: check resv for HugeTLB allocation from dpool
- mm/dynamic_pool: speed up allocation by percpu pages pool
- mm/dynamic_pool: support page allocation from dpool
- mm/dynamic_pool: prevent task attach to another dpool
- mm/dynamic_pool: call mem_cgroup_force_empty before restore pool
- mm/dynamic_pool: migrate used pages before promote to huge page
- mm/dynamic_pool: support to flow pages between 2M and 4K pages pool
- mm/dynamic_pool: support to flow pages between 1G and 2M pages pool
- mm/dynamic_pool: add restore_pool ops to reclaim memory and restore hugepages
- mm/dynamic_pool: add interface to configure the count of hugepages
- mm/dynamic_pool: fill dpool with HugeTLB 1G pages
- mm/dynamic_pool: create dpool by dhugetlb.nr_pages interface
- mm/dynamic_pool: introduce PG_pool to mark pages allocated from dpool
- mm/dynamic_pool: introduce PG_dpool to mark free pages in dpool
- mm/dynamic_pool: introduce per-memcg memory pool
- mm/memcg: introduce memcg_has_children to check memcg
- mm/memcg: introduce mem_cgroup_scan_cgroups to scan all memcgs
- !3833  xfs: fix block space problems
- xfs: longest free extent no need consider postalloc
- xfs: fix xfs shutdown since we reserve more blocks in agfl fixup
- xfs: set minleft correctly for randomly sparse inode allocations
- xfs: account extra freespace btree splits for multiple allocations
- !3902  xfs: update the last_sync_lsn with ctx start lsn
- xfs: update the last_sync_lsn with ctx start lsn
- !3977  Terrace Service Acceleration
- bpf, sockmap: Add sk_rmem_alloc check for sockmap
- bpf: Add new bpf helper to get SO_ORIGINAL_DST/REPLY_SRC
- bpf: Add bpf_get_sockops_uid_gid helper function
- net: core: Add a GID field to struct sock.
- !3974  Add support for mbigen to generate SPIs
- dt-bindings/irqchip/mbigen: add example of MBIGEN generate SPIs
- irqchip/mbigen: add support for a MBIGEN generating SPIs
- irqchip/mbigen: rename register marcros
- !3963  block: Add config to show info about opening a mounted device for write
- add config about writing mounted devices in openeuler_defconfig
- block: Show info about opening a lower device for write while upper-layers mounted
- block: Add config option to show info about opening a mounted device for write
- block: Add config option to detect writing to part0 while partitions mounted
- block: Expand the meaning of bdev_allow_write_mounted
- block: Record writing and mounting regardless of whether bdev_allow_write_mounted is set
- !3921  mm: mem_reliable: Introduce memory reliable
- config: enable MEMORY_RELIABLE by default
- mm: mem_reliable: Show debug info about memory reliable if oom occurs
- mm: mem_reliable: Introduce proc interface to disable memory reliable features
- proc: mem_reliable: Count reliable memory usage of reliable tasks
- mm: mem_reliable: Introduce fallback mechanism for memory reliable
- mm: mem_reliable: Add limiting the usage of reliable memory
- mm: mem_reliable: Show reliable meminfo
- mm: mem_reliable: Count reliable shmem usage
- mm: mem_reliable: Count reliable page cache usage
- mm: mem_reliable: Add cmdline reliable_debug to enable separate feature
- mm/hugetlb: Allocate non-mirrored memory by default
- mm/memblock: Introduce ability to alloc memory from specify memory region
- mm: mem_reliable: Add memory reliable support during hugepaged collapse
- mm: mem_reliable: Alloc pagecache from reliable region
- shmem: mem_reliable: Alloc shmem from reliable region
- mm: mem_reliable: Alloc task memory from reliable region
- mm: mem_reliable: Introduce memory reliable
- efi: Disable mirror feature during crashkernel
- proc: introduce proc_hide_ents to hide proc files
- !3935  pid_ns: Make pid_max per namespace
- pid_ns: Make pid_max per namespace
- !3913  arm64: Add non nmi ipi backtrace support
- arm64: Add non nmi ipi backtrace support
- !3785 【OLK-6.6】PSI cgroupv1 and PSI fine grained
- sched/psi: enable PSI_CGROUP_V1 and PSI_FINE_GRAINED in openeuler_defconfig
- sched/psi: add cpu fine grained stall tracking in pressure.stat
- sched/psi: add more memory fine grained stall tracking in pressure.stat
- sched/psi: Introduce pressure.stat in psi
- sched/psi: Introduce avgs and total calculation for cgroup reclaim
- sched/psi: Introduce fine grained stall time collect for cgroup reclaim
- sched/psi: introduce tracepoints for psi_memstall_{enter, leave}
- sched/psi: update psi irqtime when the irq delta is nozero
- sched/psi: Export cgroup psi from cgroupv2 to cgroupv1
- sched/psi: Bail out early from irq time accounting
- !3907  cgroup: Support iocost for cgroup v1
- openeuler_defconfig: enable iocost in openeuler_defconfig for x86 and arm64
- cgroup: Support iocost for cgroup v1
- !3897  Some simple extensions of the kfence feature
- arm64: kfence: scale sample_interval to support early init for kfence.
- kfence: Add a module parameter to adjust kfence objects
- !3888  fs/dcache.c: avoid panic while lockref of dentry overflow
- fs/dcache.c: avoid panic while lockref of dentry overflow
- !3894  Add swap control for memcg
- config: enable memcg swap qos for x86_64 and arm64 by default
- memcg/swap: add ability to disable memcg swap
- mm: swap_slots: add per-type slot cache
- mm/swapfile: introduce per-memcg swapfile control
- memcg: add restrict to swap to cgroup1
- memcg: introduce per-memcg swapin interface
- memcg: introduce memcg swap qos feature
- memcg: make sysctl registration more extensible
- memcg: add page type to memory.reclaim interface
- !3827  backport mainline md patch
- dm-raid: delay flushing event_work() after reconfig_mutex is released
- md/raid1: support read error check
- md: factor out a helper exceed_read_errors() to check read_errors
- md: Whenassemble the array, consult the superblock of the freshest device
- md/raid1: remove unnecessary null checking
- md: split MD_RECOVERY_NEEDED out of mddev_resume
- md: fix stopping sync thread
- md: fix missing flush of sync_work
- md: synchronize flush io with array reconfiguration
- md/md-multipath: remove rcu protection to access rdev from conf
- md/raid5: remove rcu protection to access rdev from conf
- md/raid1: remove rcu protection to access rdev from conf
- md/raid10: remove rcu protection to access rdev from conf
- md: remove flag RemoveSynchronized
- Revert "md/raid5: Wait for MD_SB_CHANGE_PENDING in raid5d"
- md: bypass block throttle for superblock update
- md: cleanup pers->prepare_suspend()
- md-cluster: check for timeout while a new disk adding
- md: rename __mddev_suspend/resume() back to mddev_suspend/resume()
- md: remove old apis to suspend the array
- md: suspend array in md_start_sync() if array need reconfiguration
- md/raid5: replace suspend with quiesce() callback
- md/md-linear: cleanup linear_add()
- md: cleanup mddev_create/destroy_serial_pool()
- md: use new apis to suspend array before mddev_create/destroy_serial_pool
- md: use new apis to suspend array for ioctls involed array reconfiguration
- md: use new apis to suspend array for adding/removing rdev from state_store()
- md: use new apis to suspend array for sysfs apis
- md/raid5: use new apis to suspend array
- md/raid5-cache: use new apis to suspend array
- md/md-bitmap: use new apis to suspend array for location_store()
- md/dm-raid: use new apis to suspend array
- md: add new helpers to suspend/resume and lock/unlock array
- md: add new helpers to suspend/resume array
- md: replace is_md_suspended() with 'mddev->suspended' in md_check_recovery()
- md/raid5-cache: use READ_ONCE/WRITE_ONCE for 'conf->log'
- md: use READ_ONCE/WRITE_ONCE for 'suspend_lo' and 'suspend_hi'
- md/raid1: don't split discard io for write behind
- md: do not require mddev_lock() for all options in array_state_store()
- md: simplify md_seq_ops
- md: factor out a helper from mddev_put()
- md: replace deprecated strncpy with memcpy
- md: don't check 'mddev->pers' and 'pers->quiesce' from suspend_lo_store()
- md: don't check 'mddev->pers' from suspend_hi_store()
- md-bitmap: suspend array earlier in location_store()
- md-bitmap: remove the checking of 'pers->quiesce' from location_store()
- md: initialize 'writes_pending' while allocating mddev
- md: initialize 'active_io' while allocating mddev
- md: delay remove_and_add_spares() for read only array to md_start_sync()
- md: factor out a helper rdev_addable() from remove_and_add_spares()
- md: factor out a helper rdev_is_spare() from remove_and_add_spares()
- md: factor out a helper rdev_removeable() from remove_and_add_spares()
- md: delay choosing sync action to md_start_sync()
- md: factor out a helper to choose sync action from md_check_recovery()
- md: use separate work_struct for md_start_sync()
- !3857  scsi: fix use-after-free problem in scsi_remove_target
- scsi: fix use-after-free problem in scsi_remove_target
- !3906  sched/core: Change depends of SCHED_CORE
- sched/core: Change depends of SCHED_CORE
- !3747  Introduce multiple qos level
- config: Enable CONFIG_QOS_SCHED_MULTILEVEL
- sched/fair: Introduce multiple qos level
- !3899  fs/dirty_pages: dump the number of dirty pages for each inode
- fs/dirty_pages: dump the number of dirty pages for each inode
- !3815  JFFS2: Fix the race issues caused by the GC of jffs2
- jffs2: reset pino_nlink to 0 when inode creation failed
- jffs2: make the overwritten xattr invisible after remount
- jffs2: handle INO_STATE_CLEARING in jffs2_do_read_inode()
- jffs2: protect no-raw-node-ref check of inocache by erase_completion_lock
- !3891  block: support to account io_ticks precisely
- block: support to account io_ticks precisely
- !3881  iommu: set CONFIG_SMMU_BYPASS_DEV=y
- iommu: set CONFIG_SMMU_BYPASS_DEV=y
- !3819  support ext3/ext4 netlink error report.
- Add new config 'CONFIG_EXT4_ERROR_REPORT' to control ext3/4 error reporting
- ext4: report error to userspace by netlink
- !3720  blk-mq: make fair tag sharing configurable
- scsi_lib: disable fair tag sharing by default if total tags is less than 128
- scsi: core: make fair tag sharing configurable via sysfs
- blk-mq: add apis to disable fair tag sharing
- !3090  fs/dcache.c: avoid softlock since too many negative dentry
- fs/dcache.c: avoid softlock since too many negative dentry
- !3656  iommu: Enable smmu-v3 when 3408iMR/3416iMRraid card exist
- iommu: Enable smmu-v3 when 3408iMR/3416iMRraid card exist
- !3843 [OLK-6.6] export cgroup.stat from cgroupv2 to cgroupv1
- cgroup: Export cgroup.stat from cgroupv2 to cgroupv1
- !3828  openeuler_defconfig: enable erofs ondemand for x86 and arm64
- openeuler_defconfig: enable erofs ondemand for x86 and arm64
- !3851  ext4: fix slab-out-of-bounds in ext4_find_extent()
- ext4: check magic even the extent block bh is verified
- ext4: avoid recheck extent for EXT4_EX_FORCE_CACHE
- !3850  aio: add timeout validity check for io_[p
- aio: add timeout validity check for io_[p]getevents
- !3849  pipe: Fix endless sleep problem due to the out-of-order
- pipe: Fix endless sleep problem due to the out-of-order
- !3787  scsi: sd: unregister device if device_add_disk() failed in sd_probe()
- scsi: sd: unregister device if device_add_disk() failed in sd_probe()
- !3450  Backport nbd bugfix patch
- nbd: pass nbd_sock to nbd_read_reply() instead of index
- nbd: fix null-ptr-dereference while accessing 'nbd->config'
- nbd: factor out a helper to get nbd_config without holding 'config_lock'
- nbd: fold nbd config initialization into nbd_alloc_config()
- !3675  block mainline bugfix backport
- block: Set memalloc_noio to false on device_add_disk() error path
- block: add check of 'minors' and 'first_minor' in device_add_disk()
- block: add check that partition length needs to be aligned with block size
- !3786  ubi: block: fix memleak in ubiblock_create()
- ubi: block: fix memleak in ubiblock_create()
- !3448  ubi: block: Fix use-after-free in ubiblock_cleanup
- ubi: block: Fix use-after-free in ubiblock_cleanup
- !3760  Add huge page allocation limit
- openeuler_defconfig: enable HUGETLB_ALLOC_LIMIT
- hugetlb: Add huge page allocation limit
- !3818 [sync] PR-1989:  support Android vendor hooks
- openeuler_defconfig: enable CONFIG_VENDOR_HOOKS for x86 and arm64
- vendor_hooks: make android vendor hooks feature generic.
- ANDROID: fixup restricted hooks after tracepont refactoring
- ANDROID: simplify vendor hooks for non-GKI builds
- ANDROID: vendor_hooks: fix __section macro
- ANDROID: use static_call() for restricted hooks
- ANDROID: fix redefinition error for restricted vendor hooks
- ANDROID: add support for vendor hooks
- !3502  ARM: LPAE: Use phys_addr_t instead of unsigned long in outercache hooks
- ARM: LPAE: Use phys_addr_t instead of unsigned long in outercache hooks
- !3755  livepatch/core: Fix miss disable ro for MOD_RO_AFTER_INIT memory
- livepatch/core: Fix miss disable ro for MOD_RO_AFTER_INIT memory
- !3813  kernel: add OPENEULER_VERSION_CODE to version.h
- kernel: add OPENEULER_VERSION_CODE to version.h
- !3744  Add NUMA-awareness to qspinlock
- config: Enable CONFIG_NUMA_AWARE_SPINLOCKS on x86
- locking/qspinlock: Disable CNA by default
- locking/qspinlock: Introduce the shuffle reduction optimization into CNA
- locking/qspinlock: Avoid moving certain threads between waiting queues in CNA
- locking/qspinlock: Introduce starvation avoidance into CNA
- locking/qspinlock: Introduce CNA into the slow path of qspinlock
- locking/qspinlock: Refactor the qspinlock slow path
- locking/qspinlock: Rename mcs lock/unlock macros and make them more generic
- !3517  support CLOCKSOURCE_VALIDATE_LAST_CYCLE on
- config: make CLOCKSOURCE_VALIDATE_LAST_CYCLE not set by default
- timekeeping: Make CLOCKSOURCE_VALIDATE_LAST_CYCLE configurable
- !3710  Backport 6.6.7 LTS Patches
- drm/amdgpu: Restrict extended wait to PSP v13.0.6
- drm/amdgpu: update retry times for psp BL wait
- drm/amdgpu: Fix refclk reporting for SMU v13.0.6
- riscv: Kconfig: Add select ARM_AMBA to SOC_STARFIVE
- gcc-plugins: randstruct: Update code comment in relayout_struct()
- ASoC: qcom: sc8280xp: Limit speaker digital volumes
- netfilter: nft_set_pipapo: skip inactive elements during set walk
- MIPS: Loongson64: Enable DMA noncoherent support
- MIPS: Loongson64: Handle more memory types passed from firmware
- MIPS: Loongson64: Reserve vgabios memory on boot
- perf metrics: Avoid segv if default metricgroup isn't set
- perf list: Fix JSON segfault by setting the used skip_duplicate_pmus callback
- KVM: SVM: Update EFER software model on CR0 trap for SEV-ES
- KVM: s390/mm: Properly reset no-dat
- MIPS: kernel: Clear FPU states when setting up kernel threads
- cifs: Fix flushing, invalidation and file size with FICLONE
- cifs: Fix flushing, invalidation and file size with copy_file_range()
- USB: gadget: core: adjust uevent timing on gadget unbind
- powerpc/ftrace: Fix stack teardown in ftrace_no_trace
- x86/CPU/AMD: Check vendor in the AMD microcode callback
- devcoredump: Send uevent once devcd is ready
- serial: 8250_omap: Add earlycon support for the AM654 UART controller
- serial: 8250: 8250_omap: Do not start RX DMA on THRI interrupt
- serial: 8250: 8250_omap: Clear UART_HAS_RHR_IT_DIS bit
- serial: sc16is7xx: address RX timeout interrupt errata
- ARM: PL011: Fix DMA support
- usb: typec: class: fix typec_altmode_put_partner to put plugs
- smb: client: fix potential NULL deref in parse_dfs_referrals()
- Revert "xhci: Loosen RPM as default policy to cover for AMD xHC 1.1"
- cifs: Fix non-availability of dedup breaking generic/304
- parport: Add support for Brainboxes IX/UC/PX parallel cards
- serial: ma35d1: Validate console index before assignment
- serial: 8250_dw: Add ACPI ID for Granite Rapids-D UART
- nvmem: Do not expect fixed layouts to grab a layout driver
- usb: gadget: f_hid: fix report descriptor allocation
- kprobes: consistent rcu api usage for kretprobe holder
- ASoC: ops: add correct range check for limiting volume
- gpiolib: sysfs: Fix error handling on failed export
- x86/sev: Fix kernel crash due to late update to read-only ghcb_version
- perf: Fix perf_event_validate_size()
- drm/amdgpu: disable MCBP by default
- arm64: dts: mt8183: kukui: Fix underscores in node names
- arm64: dts: mediatek: add missing space before {
- parisc: Fix asm operand number out of range build error in bug table
- parisc: Reduce size of the bug_table on 64-bit kernel by half
- LoongArch: BPF: Don't sign extend function return value
- LoongArch: BPF: Don't sign extend memory load operand
- perf vendor events arm64: AmpereOne: Add missing DefaultMetricgroupName fields
- misc: mei: client.c: fix problem of return '-EOVERFLOW' in mei_cl_write
- misc: mei: client.c: return negative error code in mei_cl_write
- coresight: ultrasoc-smb: Fix uninitialized before use buf_hw_base
- coresight: ultrasoc-smb: Config SMB buffer before register sink
- coresight: ultrasoc-smb: Fix sleep while close preempt in enable_smb
- hwtracing: hisi_ptt: Add dummy callback pmu::read()
- coresight: Fix crash when Perf and sysfs modes are used concurrently
- coresight: etm4x: Remove bogous __exit annotation for some functions
- arm64: dts: mediatek: mt8186: Change gpu speedbin nvmem cell name
- arm64: dts: mediatek: mt8186: fix clock names for power domains
- arm64: dts: mediatek: mt8183-evb: Fix unit_address_vs_reg warning on ntc
- arm64: dts: mediatek: mt8183: Move thermal-zones to the root node
- arm64: dts: mediatek: mt8183: Fix unit address for scp reserved memory
- arm64: dts: mediatek: mt8195: Fix PM suspend/resume with venc clocks
- arm64: dts: mediatek: mt8173-evb: Fix regulator-fixed node names
- arm64: dts: mediatek: cherry: Fix interrupt cells for MT6360 on I2C7
- arm64: dts: mediatek: mt8183-kukui-jacuzzi: fix dsi unnecessary cells properties
- arm64: dts: mediatek: mt7622: fix memory node warning check
- arm64: dts: mt7986: fix emmc hs400 mode without uboot initialization
- arm64: dts: mt7986: define 3W max power to both SFP on BPI-R3
- arm64: dts: mt7986: change cooling trips
- drm/i915: Skip some timing checks on BXT/GLK DSI transcoders
- drm/i915/mst: Reject modes that require the bigjoiner
- drm/i915/mst: Fix .mode_valid_ctx() return values
- drm/atomic-helpers: Invoke end_fb_access while owning plane state
- md/raid6: use valid sector values to determine if an I/O should wait on the reshape
- powercap: DTPM: Fix missing cpufreq_cpu_put() calls
- mm/memory_hotplug: fix error handling in add_memory_resource()
- mm: fix oops when filemap_map_pmd() without prealloc_pte
- mm/memory_hotplug: add missing mem_hotplug_lock
- drivers/base/cpu: crash data showing should depends on KEXEC_CORE
- hugetlb: fix null-ptr-deref in hugetlb_vma_lock_write
- workqueue: Make sure that wq_unbound_cpumask is never empty
- platform/surface: aggregator: fix recv_buf() return value
- regmap: fix bogus error on regcache_sync success
- r8169: fix rtl8125b PAUSE frames blasting when suspended
- packet: Move reference count in packet_sock to atomic_long_t
- nfp: flower: fix for take a mutex lock in soft irq context and rcu lock
- leds: trigger: netdev: fix RTNL handling to prevent potential deadlock
- tracing: Fix a possible race when disabling buffered events
- tracing: Fix incomplete locking when disabling buffered events
- tracing: Disable snapshot buffer when stopping instance tracers
- tracing: Stop current tracer when resizing buffer
- tracing: Always update snapshot buffer size
- checkstack: fix printed address
- cgroup_freezer: cgroup_freezing: Check if not frozen
- lib/group_cpus.c: avoid acquiring cpu hotplug lock in group_cpus_evenly
- nilfs2: prevent WARNING in nilfs_sufile_set_segment_usage()
- nilfs2: fix missing error check for sb_set_blocksize call
- highmem: fix a memory copy problem in memcpy_from_folio
- ring-buffer: Force absolute timestamp on discard of event
- ring-buffer: Test last update in 32bit version of __rb_time_read()
- ALSA: hda/realtek: Add quirk for Lenovo Yoga Pro 7
- ALSA: hda/realtek: Add Framework laptop 16 to quirks
- ALSA: hda/realtek: add new Framework laptop to quirks
- ALSA: hda/realtek: Enable headset on Lenovo M90 Gen5
- ALSA: hda/realtek: fix speakers on XPS 9530 (2023)
- ALSA: hda/realtek: Apply quirk for ASUS UM3504DA
- ALSA: pcm: fix out-of-bounds in snd_pcm_state_names
- ALSA: usb-audio: Add Pioneer DJM-450 mixer controls
- io_uring: fix mutex_unlock with unreferenced ctx
- nvme-pci: Add sleep quirk for Kingston drives
- io_uring/af_unix: disable sending io_uring over sockets
- ASoC: amd: yc: Fix non-functional mic on ASUS E1504FA
- rethook: Use __rcu pointer for rethook::handler
- scripts/gdb: fix lx-device-list-bus and lx-device-list-class
- kernel/Kconfig.kexec: drop select of KEXEC for CRASH_DUMP
- md: don't leave 'MD_RECOVERY_FROZEN' in error path of md_set_readonly()
- riscv: errata: andes: Probe for IOCP only once in boot stage
- riscv: fix misaligned access handling of C.SWSP and C.SDSP
- arm64: dts: rockchip: Fix eMMC Data Strobe PD on rk3588
- ARM: dts: imx28-xea: Pass the 'model' property
- ARM: dts: imx7: Declare timers compatible with fsl,imx6dl-gpt
- arm64: dts: imx8-apalis: set wifi regulator to always-on
- ARM: imx: Check return value of devm_kasprintf in imx_mmdc_perf_init
- arm64: dts: imx93: correct mediamix power
- arm64: dts: freescale: imx8-ss-lsio: Fix #pwm-cells
- arm64: dts: imx8-ss-lsio: Add PWM interrupts
- scsi: be2iscsi: Fix a memleak in beiscsi_init_wrb_handle()
- tracing: Fix a warning when allocating buffered events fails
- io_uring/kbuf: check for buffer list readiness after NULL check
- io_uring/kbuf: Fix an NULL vs IS_ERR() bug in io_alloc_pbuf_ring()
- ARM: dts: imx6ul-pico: Describe the Ethernet PHY clock
- arm64: dts: imx8mp: imx8mq: Add parkmode-disable-ss-quirk on DWC3
- drm/bridge: tc358768: select CONFIG_VIDEOMODE_HELPERS
- RDMA/irdma: Avoid free the non-cqp_request scratch
- RDMA/irdma: Fix support for 64k pages
- RDMA/irdma: Ensure iWarp QP queue memory is OS paged aligned
- RDMA/core: Fix umem iterator when PAGE_SIZE is greater then HCA pgsz
- ASoC: wm_adsp: fix memleak in wm_adsp_buffer_populate
- firmware: arm_scmi: Fix possible frequency truncation when using level indexing mode
- firmware: arm_scmi: Simplify error path in scmi_dvfs_device_opps_add()
- firmware: arm_scmi: Fix frequency truncation by promoting multiplier type
- firmware: arm_scmi: Extend perf protocol ops to get information of a domain
- firmware: arm_scmi: Extend perf protocol ops to get number of domains
- hwmon: (nzxt-kraken2) Fix error handling path in kraken2_probe()
- ASoC: codecs: lpass-tx-macro: set active_decimator correct default value
- hwmon: (acpi_power_meter) Fix 4.29 MW bug
- ARM: dts: bcm2711-rpi-400: Fix delete-node of led_act
- ARM: dts: rockchip: Fix sdmmc_pwren's pinmux setting for RK3128
- ARM: dts: imx6q: skov: fix ethernet clock regression
- arm64: dt: imx93: tqma9352-mba93xxla: Fix LPUART2 pad config
- RDMA/irdma: Fix UAF in irdma_sc_ccq_get_cqe_info()
- RDMA/bnxt_re: Correct module description string
- RDMA/rtrs-clt: Remove the warnings for req in_use check
- RDMA/rtrs-clt: Fix the max_send_wr setting
- RDMA/rtrs-srv: Destroy path files after making sure no IOs in-flight
- RDMA/rtrs-srv: Free srv_mr iu only when always_invalidate is true
- RDMA/rtrs-srv: Check return values while processing info request
- RDMA/rtrs-clt: Start hb after path_up
- RDMA/rtrs-srv: Do not unconditionally enable irq
- ASoC: fsl_sai: Fix no frame sync clock issue on i.MX8MP
- arm64: dts: rockchip: Expand reg size of vdec node for RK3399
- arm64: dts: rockchip: Expand reg size of vdec node for RK3328
- RDMA/irdma: Add wait for suspend on SQD
- RDMA/irdma: Do not modify to SQD on error
- RDMA/hns: Fix unnecessary err return when using invalid congest control algorithm
- RDMA/core: Fix uninit-value access in ib_get_eth_speed()
- tee: optee: Fix supplicant based device enumeration
- mm/damon/sysfs: eliminate potential uninitialized variable warning
- drm/amdkfd: get doorbell's absolute offset based on the db_size
- drm/amd/amdgpu/amdgpu_doorbell_mgr: Correct misdocumented param 'doorbell_index'
- net/smc: fix missing byte order conversion in CLC handshake
- net: dsa: microchip: provide a list of valid protocols for xmit handler
- drop_monitor: Require 'CAP_SYS_ADMIN' when joining "events" group
- psample: Require 'CAP_NET_ADMIN' when joining "packets" group
- bpf: sockmap, updating the sg structure should also update curr
- net: tls, update curr on splice as well
- net: dsa: mv88e6xxx: Restore USXGMII support for 6393X
- tcp: do not accept ACK of bytes we never sent
- netfilter: xt_owner: Fix for unsafe access of sk->sk_socket
- netfilter: nf_tables: validate family when identifying table via handle
- netfilter: nf_tables: bail out on mismatching dynset and set expressions
- netfilter: nf_tables: fix 'exist' matching on bigendian arches
- netfilter: bpf: fix bad registration on nf_defrag
- dt-bindings: interrupt-controller: Allow #power-domain-cells
- octeontx2-af: Update Tx link register range
- octeontx2-af: Add missing mcs flr handler call
- octeontx2-af: Fix mcs stats register address
- octeontx2-af: Fix mcs sa cam entries size
- octeontx2-af: Adjust Tx credits when MCS external bypass is disabled
- net: hns: fix fake link up on xge port
- net: hns: fix wrong head when modify the tx feature when sending packets
- net: atlantic: Fix NULL dereference of skb pointer in
- ipv4: ip_gre: Avoid skb_pull() failure in ipgre_xmit()
- ionic: Fix dim work handling in split interrupt mode
- ionic: fix snprintf format length warning
- tcp: fix mid stream window clamp.
- net: bnxt: fix a potential use-after-free in bnxt_init_tc
- iavf: validate tx_coalesce_usecs even if rx_coalesce_usecs is zero
- i40e: Fix unexpected MFS warning message
- ice: Restore fix disabling RX VLAN filtering
- octeontx2-af: fix a use-after-free in rvu_npa_register_reporters
- xsk: Skip polling event check for unbound socket
- net: stmmac: fix FPE events losing
- octeontx2-pf: consider both Rx and Tx packet stats for adaptive interrupt coalescing
- arcnet: restoring support for multiple Sohard Arcnet cards
- platform/mellanox: Check devm_hwmon_device_register_with_groups() return value
- platform/mellanox: Add null pointer checks for devm_kasprintf()
- mlxbf-bootctl: correctly identify secure boot with development keys
- r8152: Add RTL8152_INACCESSIBLE to r8153_aldps_en()
- r8152: Add RTL8152_INACCESSIBLE to r8153_pre_firmware_1()
- r8152: Add RTL8152_INACCESSIBLE to r8156b_wait_loading_flash()
- r8152: Add RTL8152_INACCESSIBLE checks to more loops
- r8152: Hold the rtnl_lock for all of reset
- hv_netvsc: rndis_filter needs to select NLS
- bpf: Fix a verifier bug due to incorrect branch offset comparison with cpu=v4
- octeontx2-af: Check return value of nix_get_nixlf before using nixlf
- octeontx2-pf: Add missing mutex lock in otx2_get_pauseparam
- ipv6: fix potential NULL deref in fib6_add()
- platform/x86: wmi: Skip blocks with zero instances
- of: dynamic: Fix of_reconfig_get_state_change() return value documentation
- platform/x86: asus-wmi: Move i8042 filter install to shared asus-wmi code
- dt: dt-extract-compatibles: Don't follow symlinks when walking tree
- dt: dt-extract-compatibles: Handle cfile arguments in generator function
- x86/tdx: Allow 32-bit emulation by default
- x86/entry: Do not allow external 0x80 interrupts
- x86/entry: Convert INT 0x80 emulation to IDTENTRY
- x86/coco: Disable 32-bit emulation by default on TDX and SEV
- x86: Introduce ia32_enabled()
- dm-crypt: start allocating with MAX_ORDER
- drm/amdgpu: correct chunk_ptr to a pointer to chunk.
- drm/amdgpu: finalizing mem_partitions at the end of GMC v9 sw_fini
- drm/amdgpu: Do not program VF copy regs in mmhub v1.8 under SRIOV (v2)
- kconfig: fix memory leak from range properties
- modpost: fix section mismatch message for RELA
- tg3: Increment tx_dropped in tg3_tso_bug()
- tg3: Move the [rt]x_dropped counters to tg3_napi
- zstd: Fix array-index-out-of-bounds UBSAN warning
- nouveau: use an rwlock for the event lock.
- netfilter: ipset: fix race condition between swap/destroy and kernel side add/del/test
- i2c: ocores: Move system PM hooks to the NOIRQ phase
- i2c: designware: Fix corrupted memory seen in the ISR
- hrtimers: Push pending hrtimers away from outgoing CPU earlier
- scsi: sd: Fix sshdr use in sd_suspend_common()
- vdpa/mlx5: preserve CVQ vringh index
- !3749 support nokaslr and memmap parameter for kaslr collision detection
- kaslr: enable CONFIG_SKIP_KASLR_MEM_RANGE in openeuler defconfig
- x86/boot: add x86 nokaslr memory regions
- efi/libstub: add arm64 nokaslr memory regions
- efi/libstub: arm64: Fix KASLR and memmap= collision
- efi/libstub: arm64: support strchr function for EFI stub
- efi/libstub: add arm64 kaslr memory region avoid support
- !3737  arm64: Fix compilation error with ILP32
- config: Disable CONFIG_COMPAT_BINFMT_ELF as default
- arm64: Fix compilation error with ILP32 support
- Revert "Kconfig: regularize selection of CONFIG_BINFMT_ELF"
- !3743  Fix ppc32 build error
- powerpc: Fix ppc32 build
- !3713  Introduce CPU inspect feature
- openeuler_defconfig: enable CPU inspect for arm64 by default
- cpuinspect: add ATF inspector
- cpuinspect: add CPU-inspect infrastructure
- !3730  ARM: spectre-v2: turn off the mitigation via boot cmdline param
- ARM: spectre-v2: turn off the mitigation via boot cmdline param
- !3732  tcp_comp: implement tcp compression
- tcp_comp: implement tcp compression
- !3748  jffs2: move jffs2_init_inode_info() just after allocating inode
- jffs2: move jffs2_init_inode_info() just after allocating inode
- !3542  Support kernel livepatching
- livepatch/powerpc: Add arch_klp_module_check_calltrace
- livepatch/powerpc: Support breakpoint exception optimization
- livepatch/ppc64: Sample testcase fix ppc64
- livepatch/ppc64: Implement livepatch without ftrace for ppc64be
- livepatch: Bypass dead thread when check calltrace
- livepatch/arm: Add arch_klp_module_check_calltrace
- livepatch/arm64: Add arch_klp_module_check_calltrace
- livepatch/x86: Add arch_klp_module_check_calltrace
- livepatch: Add klp_module_delete_safety_check
- livepatch/arm: Support breakpoint exception optimization
- livepatch/arm64: Support breakpoint exception optimization
- livepatch: Add arch_klp_init
- livepatch/x86: Support breakpoint exception optimization
- livepatch: Use breakpoint exception to optimize enabling livepatch
- livepatch/ppc32: Support livepatch without ftrace
- livepatch/arm: Support livepatch without ftrace
- livepatch/core: Add support for arm for klp relocation
- arm/module: Use plt section indices for relocations
- livepatch: Enable livepatch configs in openeuler_defconfig
- livepatch/core: Revert module_enable_ro and module_disable_ro
- livepatch/arm64: Support livepatch without ftrace
- livepatch/core: Avoid conflict with static {call,key}
- livepatch: Fix patching functions which have static_call
- livepatch: Fix crash when access the global variable in hook
- livepatch/core: Support jump_label
- livepatch: samples: Adapt livepatch-sample for solution without ftrace
- livepatch/core: Support load and unload hooks
- livepatch/core: Restrict livepatch patched/unpatched when plant kprobe
- livepatch/core: Disable support for replacing
- livepatch/x86: Support livepatch without ftrace
- Revert "x86/insn: Make insn_complete() static"
- livepatch/core: Reuse common codes in the solution without ftrace
- livepatch/core: Allow implementation without ftrace
- !3678  timer_list: avoid other cpu soft lockup when printing timer list
- timer_list: avoid other cpu soft lockup when printing timer list
- !3733  drm/radeon: check the alloc_workqueue return value in radeon_crtc_init()
- drm/radeon: check the alloc_workqueue return value in radeon_crtc_init()
- !3734  Introduce qos smt expeller for co-location
- sched/fair: Add cmdline nosmtexpell
- sched/fair: Introduce QOS_SMT_EXPELL priority reversion mechanism
- sched/fair: Start tracking qos_offline tasks count in cfs_rq
- config: Enable CONFIG_QOS_SCHED_SMT_EXPELLER
- sched: Add tracepoint for qos smt expeller
- sched: Add statistics for qos smt expeller
- sched: Implement the function of qos smt expeller
- sched: Introduce qos smt expeller for co-location
- !3629  x86/kdump: make crash kernel boot faster
- x86/kdump: make crash kernel boot faster
- !3722  add memmap interface to reserved memory
- arm64: Request resources for reserved memory via memmap
- arm64: Add support for memmap kernel parameters
- !3724  lib/clear_user: ensure loop in __arch_clear_user cache-aligned v2
- config: enable CONFIG_CLEAR_USER_WORKAROUND by default
- lib/clear_user: ensure loop in __arch_clear_user cache-aligned v2
- !3688  Support priority load balance for qos scheduler
- sched: Introduce priority load balance for qos scheduler
- !3712  sched: steal tasks to improve CPU utilization
- config: enable CONFIG_SCHED_STEAL by default
- sched/fair: introduce SCHED_STEAL
- disable stealing by default
- sched/fair: Provide idle search schedstats
- sched/fair: disable stealing if too many NUMA nodes
- sched/fair: Steal work from an overloaded CPU when CPU goes idle
- sched/fair: Provide can_migrate_task_llc
- sched/fair: Generalize the detach_task interface
- sched/fair: Hoist idle_stamp up from idle_balance
- sched/fair: Dynamically update cfs_overload_cpus
- sched/topology: Provide cfs_overload_cpus bitmap
- sched/topology: Provide hooks to allocate data shared per LLC
- sched: Provide sparsemask, a reduced contention bitmap
- !3701  mm: Add sysctl to clear free list pages
- mm: Add sysctl to clear free list pages
- !3598  arm64: add config switch and kernel parameter for cpu0 hotplug
- config: disable config ARM64_BOOTPARAM_HOTPLUG_CPU0 by default
- arm64: Add config switch and kernel parameter for CPU0 hotplug
- !3649  x86/kdump: add log before booting crash kernel
- x86/kdump: add log before booting crash kernel
- !3700  Backport 6.6.6 LTS Patches
- Revert "wifi: cfg80211: fix CQM for non-range use"
- !3565  blk-throttle: enable hierarchical throttle in cgroup v1
- blk-throttle: enable hierarchical throttle in cgroup v1
- !3608  xfs: fix two corruption problems
- xfs: shutdown xfs once inode double free
- xfs: shutdown to ensure submits buffers on LSN boundaries
- !3674  mm/hugetlb: Introduce alloc_hugetlb_folio_size()
- mm/hugetlb: Introduce alloc_hugetlb_folio_size()
- !3651  nbd: get config_lock before sock_shutdown
- nbd: get config_lock before sock_shutdown
- !3573  Support dynamic affinity scheduler
- sched/fair: Modify idle cpu judgment in dynamic affinity
- sched/fair: Remove invalid cpu selection logic in dynamic affinity
- config: enable CONFIG_QOS_SCHED_DYNAMIC_AFFINITY by default
- sched: Add cmdline for dynamic affinity
- sched: Add statistics for scheduler dynamic affinity
- sched: Adjust cpu allowed in load balance dynamicly
- sched: Adjust wakeup cpu range according CPU util dynamicly
- cpuset: Introduce new interface for scheduler dynamic affinity
- sched: Introduce dynamic affinity for cfs scheduler
- !3599  arm64: Add framework to turn IPI as NMI
- arm64: kgdb: Roundup cpus using IPI as NMI
- kgdb: Expose default CPUs roundup fallback mechanism
- arm64: ipi_nmi: Add support for NMI backtrace
- nmi: backtrace: Allow runtime arch specific override
- arm64: smp: Assign and setup an IPI as NMI
- irqchip/gic-v3: Enable support for SGIs to act as NMIs
- arm64: Add framework to turn IPI as NMI
- !3638  memcg: support OOM priority for memcg
- memcg: enable CONFIG_MEMCG_OOM_PRIORITY by default
- memcg: Add sysctl memcg_qos_enable
- memcg: support priority for oom
- !3602  xfs: fix attr inactive problems
- xfs: atomic drop extent entries when inactiving attr
- xfs: factor out __xfs_da3_node_read()
- xfs: force shutdown xfs when xfs_attr_inactive fails
- !3601  xfs: fix perag leak when growfs fails
- xfs: fix perag leak when growfs fails
- xfs: add lock protection when remove perag from radix tree
- !3575  ubi: Enhance fault injection capability for the UBI driver
- mtd: Add several functions to the fail_function list
- ubi: Reserve sufficient buffer length for the input mask
- ubi: Add six fault injection type for testing
- ubi: Split io_failures into write_failure and erase_failure
- ubi: Use the fault injection framework to enhance the fault injection capability
- !3588 files cgroups
- enable CONFIG_CGROUP_FILES in openeuler_defconfig for x86 and arm64
- cgroup/files: support boot parameter to control if disable files cgroup
- fs/filescontrol: add a switch to enable / disable accounting of open fds
- cgroups: Resource controller for open files
- !3605  openeuler_defconfig: enable CONFIG_UNICODE for x86 and arm64
- openeuler_defconfig: enable CONFIG_UNICODE for x86 and arm64
- !3600  iommu/arm-smmu-v3: Add a SYNC command to avoid broken page table prefetch
- iommu/arm-smmu-v3: Add a SYNC command to avoid broken page table prefetch
- !3397  xfs: fix some growfs problems
- xfs: fix dir3 block read verify fail during log recover
- xfs: keep growfs sb log item active until ail flush success
- xfs: fix mounting failed caused by sequencing problem in the log records
- xfs: fix the problem of mount failure caused by not refreshing mp->m_sb
- !3582  Add support for memory limit
- mm: support pagecache limit
- mm: support periodical memory reclaim
- !3323  LoongArch: add cpufreq and ls2k500 bmc support
- LoongArch: fix ls2k500 bmc not work when installing iso
- LoongArch: defconfig: enable CONFIG_FB_LS2K500=m.
- ipmi: add ls2k500 bmc ipmi support.
- fbdev: add ls2k500sfb driver for ls2k500 bmc.
- cpufreq: Add cpufreq driver for LoongArch
- !3363  xfs: fix some misc issue
- xfs: xfs_trans_cancel() path must check for log shutdown
- xfs: don't verify agf length when log recovery
- xfs: fix a UAF in xfs_iflush_abort_clean
- xfs: fix a UAF when inode item push
- !3495  xfs: fix hung and warning
- xfs: fix warning in xfs_vm_writepages()
- xfs: fix hung when transaction commit fail in xfs_inactive_ifree
- xfs: fix dead loop when do mount with IO fault injection
- !3525 ARM: support kaslr feature in arm32 platform
- arm32: kaslr: Fix clock_gettime and gettimeofday performance degradation when configure CONFIG_RANDOMIZE_BASE
- arm32: kaslr: Fix the bug of symbols relocation
- arm32: kaslr: print kaslr offset when kernel panic
- arm32: kaslr: pop visibility when compile decompress boot code as we need relocate BSS by GOT.
- arm32: kaslr: When boot with vxboot, we must adjust dtb address before kaslr_early_init, and store dtb address after init.
- No idea why this broke ...
- ARM: decompressor: add KASLR support
- ARM: decompressor: explicitly map decompressor binary cacheable
- ARM: kernel: implement randomization of the kernel load address
- arm: vectors: use local symbol names for vector entry points
- ARM: kernel: refer to swapper_pg_dir via its symbol
- ARM: mm: export default vmalloc base address
- ARM: kernel: use PC relative symbol references in suspend/resume code
- ARM: kernel: use PC-relative symbol references in MMU switch code
- ARM: kernel: make vmlinux buildable as a PIE executable
- ARM: kernel: switch to relative exception tables
- arm-soc: various: replace open coded VA->PA calculation of pen_release
- arm-soc: mvebu: replace open coded VA->PA conversion
- arm-soc: exynos: replace open coded VA->PA conversions
- asm-generic: add .data.rel.ro sections to __ro_after_init
- !3563  memcg: support ksm merge any mode per cgroup
- memcg: support ksm merge any mode per cgroup
- !3528  Print rootfs and tmpfs files charged by memcg
- config: enable CONFIG_MEMCG_MEMFS_INFO by default
- mm/memcg_memfs_info: show files that having pages charged in mem_cgroup
- fs: move {lock, unlock}_mount_hash to fs/mount.h
- !3489  ascend: export interfaces required by ascend drivers
- ascend: export interfaces required by ascend drivers
- !3381 cgroupv1 cgroup writeback enable
- openeuler_defconfig: enable CONFIG_CGROUP_V1_WRITEBACK in openeuler_defconfig for x86 and arm64
- cgroup: support cgroup writeback on cgroupv1
- cgroup: factor out __cgroup_get_from_id() for cgroup v1
- !3537 backport cgroup bugs from olk5.10
- cgroup: disable kernel memory accounting for all memory cgroups by default
- cgroup: Return ERSCH when add Z process into task
- cgroup: wait for cgroup destruction to complete when umount
- cgroup: check if cgroup root is alive in cgroupstats_show()
- !3439  security: restrict init parameters by configuration
- security: restrict init parameters by configuration
- !3475  kaslr: ppc64: Introduce KASLR for PPC64
- powerpc/fsl_booke/kaslr: Fix preserved memory size for int-vectors issue
- powerpc/fsl_booke/kaslr: Provide correct r5 value for relocated kernel
- powerpc/fsl_booke/kaslr: rename kaslr-booke32.rst to kaslr-booke.rst and add 64bit part
- powerpc/fsl_booke/64: clear the original kernel if randomized
- powerpc/fsl_booke/64: do not clear the BSS for the second pass
- powerpc/fsl_booke/64: implement KASLR for fsl_booke64
- powerpc/fsl_booke/64: introduce reloc_kernel_entry() helper
- powerpc/fsl_booke/kaslr: refactor kaslr_legal_offset() and kaslr_early_init()
- !3486  sync smmu patches for olk-6.6
- iommu/arm-smmu-v3: disable stall for quiet_cd
- iommu/iova: Manage the depot list size
- iommu/iova: Make the rcache depot scale better
- !3434  arm64/ascend: Add new enable_oom_killer interface for oom contrl
- arm64/ascend: Add new enable_oom_killer interface for oom contrl
- !3479  cache: Workaround HiSilicon Linxicore DC CVAU
- cache: Workaround HiSilicon Linxicore DC CVAU
- !3367  ipv4: igmp: fix refcnt uaf issue when receiving igmp query packet
- ipv4: igmp: fix refcnt uaf issue when receiving igmp query packet
- !3471  add redis sockmap sample code
- tools: add sample sockmap code for redis
- net: add local_skb parameter to identify local tcp connection
- net: let sockops can use bpf_get_current_comm()
- !3432  ACPI / APEI: Notify all ras err to driver
- ACPI / APEI: Notify all ras err to driver

* Tue Dec 26 2023 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-2.0.0.2
- !3435  iommu/arm-smmu-v3: Add suspend and resume support
- !3315  Backport 6.6.5 LTS Patches
- !3314  Backport 6.6.4 LTS Patches
- !3286 block: Add config option to not allow writing to mounted devices
- !3430  Add support for hisi HBM devices
- !3431  memcg reclaim and cgroup kill
- iommu/arm-smmu-v3: Add suspend and resume support
- config: enable CONFIG_MEMCG_V1_RECLAIM and CONFIG_CGROUP_V1_KILL
- memcg: introduce per-memcg reclaim interface
- memcg: export high_async_ratio to userland
- memcg: enable memcg async reclaim
- memcg: Export memory.events{local} from cgroupv2 to cgroupv1
- memcg: Export memcg.{min/low/high} from cgroupv2 to cgroupv1
- cgroup: Export cgroup.kill from cgroupv2 to cgroupv1
- soc: hisilicon: hisi_hbmdev: Add hbm acls repair and query methods
- soc: hbmcache: Add support for online and offline the hbm cache
- soc: hisilicon: hisi_hbmdev: Provide extra memory topology information
- ACPI: memhotplug: export the state of each hotplug device
- soc: hisilicon: hisi_hbmdev: Add power domain control methods
- ACPI: OSL: Export the symbol of acpi_hotplug_schedule
- !3391  nbd_genl_status: null check for nla_nest_start
- !3352  support userswap feature
- !3383  Support Qos Scheduler
- nbd_genl_status: null check for nla_nest_start
- sched: Enable qos scheduler config
- sched: Introduce handle priority reversion mechanism
- sched: Support kill boost for offline task
- sched: Throttle qos cfs_rq when current cpu is running online task
- sched: Introduce qos scheduler for co-location
- !3306  improve gettimeofday() performance in user space
- !3331  kabi: add kabi helper macros and tools
- mm/userswap: openeuler_defconfig: enable userswap
- mm/userswap: provide cpu info in userfault msg
- mm/userswap: introduce UFFDIO_COPY_MODE_DIRECT_MAP
- mm/userswap: support userswap via userfaultfd
- mm/userswap: introduce MREMAP_USWAP_SET_PTE
- mm/userswap: add enable_userswap boot option
- mm/userswap: add VM_USWAP and SWP_USERSWAP_ENTRY
- !3326  config: Open CONFIG_AARCH32_EL0 and keep CONFIG_ARM64_ILP32 closed
- kabi: add kABI reference checking tool
- kabi: add a tool to generate the kabi reference relationship
- kabi: add script tools to check kabi symbol
- kabi: deduplication friendly structs
- kabi: Generalize naming of kabi helper macros
- openeuler_defconfig: Enable CONFIG_KABI_RESERVE for x86 and arm64
- KABI: Add CONFIG_KABI_RESERVE to control KABI padding reserve
- kabi: enables more stringent kabi checks
- kabi: add KABI_SIZE_ALIGN_CHECKS for more stringent kabi checks
- kabi: add kabi helper macros
- !3298  ARM: Add unwinding annotations to __loop.*delay functions
- config: Open CONFIG_AARCH32_EL0 and keep CONFIG_ARM64_ILP32 closed
- !3300  Add sharepool support v3
- vfio: Drop vfio_file_iommu_group() stub to fudge around a KVM wart
- x86/xen: fix percpu vcpu_info allocation
- vfio/pds: Fix possible sleep while in atomic context
- vfio/pds: Fix mutex lock->magic != lock warning
- drm/amd/display: Fix MPCC 1DLUT programming
- drm/amd/display: Simplify brightness initialization
- drm/amd/display: Reduce default backlight min from 5 nits to 1 nits
- drm/amd/display: refactor ILR to make it work
- iommu: Fix printk arg in of_iommu_get_resv_regions()
- drm/amd/pm: fix a memleak in aldebaran_tables_init
- cpufreq/amd-pstate: Only print supported EPP values for performance governor
- cpufreq/amd-pstate: Fix scaling_min_freq and scaling_max_freq update
- drm/panel: nt36523: fix return value check in nt36523_probe()
- drm/panel: starry-2081101qfh032011-53g: Fine tune the panel power sequence
- drm/i915/gsc: Mark internal GSC engine with reserved uabi class
- iommu/vt-d: Make context clearing consistent with context mapping
- iommu/vt-d: Disable PCI ATS in legacy passthrough mode
- iommu/vt-d: Omit devTLB invalidation requests when TES=0
- cpufreq: imx6q: Don't disable 792 Mhz OPP unnecessarily
- drm/amd/display: Remove power sequencing check
- drm/amd/display: Refactor edp power control
- s390/cmma: fix handling of swapper_pg_dir and invalid_pg_dir
- powerpc/pseries/iommu: enable_ddw incorrectly returns direct mapping for SR-IOV device
- net: ravb: Keep reverse order of operations in ravb_remove()
- net: ravb: Stop DMA in case of failures on ravb_open()
- net: ravb: Start TX queues after HW initialization succeeded
- net: ravb: Make write access to CXR35 first before accessing other EMAC registers
- net: ravb: Use pm_runtime_resume_and_get()
- net: ravb: Check return value of reset_control_deassert()
- ice: Fix VF Reset paths when interface in a failed over aggregate
- bpf, sockmap: af_unix stream sockets need to hold ref for pair sock
- ethtool: don't propagate EOPNOTSUPP from dumps
- ravb: Fix races between ravb_tx_timeout_work() and net related ops
- r8169: prevent potential deadlock in rtl8169_close
- efi/unaccepted: Fix off-by-one when checking for overlapping ranges
- neighbour: Fix __randomize_layout crash in struct neighbour
- octeontx2-pf: Restore TC ingress police rules when interface is up
- octeontx2-pf: Fix adding mbox work queue entry when num_vfs > 64
- net: stmmac: xgmac: Disable FPE MMC interrupts
- octeontx2-af: Fix possible buffer overflow
- selftests/net: mptcp: fix uninitialized variable warnings
- selftests/net: unix: fix unused variable compiler warning
- selftests/net: fix a char signedness issue
- selftests/net: ipsec: fix constant out of range
- uapi: propagate __struct_group() attributes to the container union
- bpf: Add missed allocation hint for bpf_mem_cache_alloc_flags()
- dpaa2-eth: recycle the RX buffer only after all processing done
- dpaa2-eth: increase the needed headroom to account for alignment
- net: dsa: mv88e6xxx: fix marvell 6350 probe crash
- net: dsa: mv88e6xxx: fix marvell 6350 switch probing
- wifi: mac80211: do not pass AP_VLAN vif pointer to drivers during flush
- wifi: iwlwifi: mvm: fix an error code in iwl_mvm_mld_add_sta()
- ipv4: igmp: fix refcnt uaf issue when receiving igmp query packet
- net: rswitch: Fix missing dev_kfree_skb_any() in error path
- net: rswitch: Fix return value in rswitch_start_xmit()
- net: rswitch: Fix type of ret in rswitch_start_xmit()
- netdevsim: Don't accept device bound programs
- media: v4l2-subdev: Fix a 64bit bug
- pinctrl: stm32: fix array read out of bound
- pinctrl: stm32: Add check for devm_kcalloc
- wifi: cfg80211: fix CQM for non-range use
- io_uring/kbuf: recycle freed mapped buffer ring entries
- io_uring/kbuf: defer release of mapped buffer rings
- io_uring: enable io_mem_alloc/free to be used in other parts
- btrfs: fix 64bit compat send ioctl arguments not initializing version member
- btrfs: free the allocated memory if btrfs_alloc_page_array() fails
- btrfs: make error messages more clear when getting a chunk map
- btrfs: send: ensure send_fd is writable
- btrfs: fix off-by-one when checking chunk map includes logical address
- btrfs: ref-verify: fix memory leaks in btrfs_ref_tree_mod()
- btrfs: add dmesg output for first mount and last unmount of a filesystem
- parisc: Mark altinstructions read-only and 32-bit aligned
- parisc: Ensure 32-bit alignment on parisc unwind section
- parisc: Mark jump_table naturally aligned
- parisc: Drop the HP-UX ENOSYM and EREMOTERELEASE error codes
- parisc: Mark lock_aligned variables 16-byte aligned on SMP
- parisc: Use natural CPU alignment for bug_table
- parisc: Mark ex_table entries 32-bit aligned in uaccess.h
- parisc: Mark ex_table entries 32-bit aligned in assembly.h
- powerpc: Don't clobber f0/vs0 during fp|altivec register save
- KVM: PPC: Book3S HV: Fix KVM_RUN clobbering FP/VEC user registers
- iommu/vt-d: Add MTL to quirk list to skip TE disabling
- ext2: Fix ki_pos update for DIO buffered-io fallback case
- bcache: revert replacing IS_ERR_OR_NULL with IS_ERR
- iommu: Avoid more races around device probe
- io_uring: don't guard IORING_OFF_PBUF_RING with SETUP_NO_MMAP
- dma-buf: fix check in dma_resv_add_fence
- cpufreq/amd-pstate: Fix the return value of amd_pstate_fast_switch()
- powercap: DTPM: Fix unneeded conversions to micro-Watts
- nouveau: find the smallest page allocation to cover a buffer alloc.
- io_uring: free io_buffer_list entries via RCU
- iommu/vt-d: Fix incorrect cache invalidation for mm notification
- io_uring: don't allow discontig pages for IORING_SETUP_NO_MMAP
- ACPI: video: Use acpi_video_device for cooling-dev driver data
- r8169: fix deadlock on RTL8125 in jumbo mtu mode
- nvme: check for valid nvme_identify_ns() before using it
- dm verity: don't perform FEC for failed readahead IO
- dm verity: initialize fec io before freeing it
- drm/amd/display: force toggle rate wa for first link training for a retimer
- drm/amd/display: fix ABM disablement
- drm/amd/display: Update min Z8 residency time to 2100 for DCN314
- drm/amd/display: Use DRAM speed from validation for dummy p-state
- drm/amd/display: Remove min_dst_y_next_start check for Z8
- drm/amd/display: Include udelay when waiting for INBOX0 ACK
- drm/amdgpu: Update EEPROM I2C address for smu v13_0_0
- drm/amdgpu: fix memory overflow in the IB test
- drm/amdgpu: Force order between a read and write to the same address
- drm/amdgpu: correct the amdgpu runtime dereference usage count
- drm/amd: Enable PCIe PME from D3
- scsi: ufs: core: Clear cmd if abort succeeds in MCQ mode
- scsi: sd: Fix system start for ATA devices
- scsi: Change SCSI device boolean fields to single bit flags
- dm-verity: align struct dm_verity_fec_io properly
- net: libwx: fix memory leak on msix entry
- ALSA: hda/realtek: Add supported ALC257 for ChromeOS
- ALSA: hda/realtek: Headset Mic VREF to 100%
- ALSA: hda: Disable power-save on KONTRON SinglePC
- drm/i915: Also check for VGA converter in eDP probe
- mmc: block: Be sure to wait while busy in CQE error recovery
- mmc: block: Do not lose cache flush during CQE error recovery
- mmc: block: Retry commands in CQE error recovery
- mmc: cqhci: Fix task clearing in CQE error recovery
- mmc: cqhci: Warn of halt or task clear failure
- mmc: cqhci: Increase recovery halt timeout
- mmc: sdhci-sprd: Fix vqmmc not shutting down after the card was pulled
- mmc: sdhci-pci-gli: Disable LPM during initialization
- firewire: core: fix possible memory leak in create_units()
- pinctrl: avoid reload of p state in list iteration
- ksmbd: fix possible deadlock in smb2_open
- smb: client: report correct st_size for SMB and NFS symlinks
- smb: client: fix missing mode bits for SMB symlinks
- cifs: Fix FALLOC_FL_INSERT_RANGE by setting i_size after EOF moved
- cifs: Fix FALLOC_FL_ZERO_RANGE by setting i_size if EOF moved
- leds: class: Don't expose color sysfs entry
- USB: dwc3: qcom: fix wakeup after probe deferral
- USB: dwc3: qcom: fix software node leak on probe errors
- usb: dwc3: set the dma max_seg_size
- usb: dwc3: Fix default mode initialization
- USB: dwc2: write HCINT with INTMASK applied
- usb: typec: tcpm: Skip hard reset when in error recovery
- usb: typec: tcpm: Fix sink caps op current check
- USB: serial: option: don't claim interface 4 for ZTE MF290
- USB: serial: option: fix FM101R-GL defines
- USB: serial: option: add Fibocom L7xx modules
- usb: cdnsp: Fix deadlock issue during using NCM gadget
- usb: config: fix iteration issue in 'usb_get_bos_descriptor()'
- USB: xhci-plat: fix legacy PHY double init
- bcache: fixup lock c->root error
- bcache: fixup init dirty data errors
- bcache: prevent potential division by zero error
- bcache: check return value from btree_node_alloc_replacement()
- veth: Use tstats per-CPU traffic counters
- dm-delay: fix a race between delay_presuspend and delay_bio
- ALSA: hda/realtek: Add quirks for ASUS 2024 Zenbooks
- ALSA: hda: ASUS UM5302LA: Added quirks for cs35L41/10431A83 on i2c bus
- cifs: fix leak of iface for primary channel
- cifs: account for primary channel in the interface list
- cifs: distribute channels across interfaces based on speed
- Revert "phy: realtek: usb: Add driver for the Realtek SoC USB 2.0 PHY"
- Revert "phy: realtek: usb: Add driver for the Realtek SoC USB 3.0 PHY"
- Revert "usb: phy: add usb phy notify port status API"
- hv_netvsc: Mark VF as slave before exposing it to user-mode
- hv_netvsc: Fix race of register_netdevice_notifier and VF register
- hv_netvsc: fix race of netvsc and VF register_netdevice
- platform/x86: ideapad-laptop: Set max_brightness before using it
- platform/x86/amd/pmc: adjust getting DRAM size behavior
- USB: serial: option: add Luat Air72*U series products
- usb: misc: onboard-hub: add support for Microchip USB5744
- dt-bindings: usb: microchip,usb5744: Add second supply
- platform/x86: hp-bioscfg: Fix error handling in hp_add_other_attributes()
- platform/x86: hp-bioscfg: move mutex_lock() down in hp_add_other_attributes()
- platform/x86: hp-bioscfg: Simplify return check in hp_add_other_attributes()
- s390/dasd: protect device queue against concurrent access
- io_uring/fs: consider link->flags when getting path for LINKAT
- bcache: fixup multi-threaded bch_sectors_dirty_init() wake-up race
- md: fix bi_status reporting in md_end_clone_io
- bcache: replace a mistaken IS_ERR() by IS_ERR_OR_NULL() in btree_gc_coalesce()
- io_uring: fix off-by one bvec index
- tls: fix NULL deref on tls_sw_splice_eof() with empty record
- swiotlb-xen: provide the "max_mapping_size" method
- ACPI: PM: Add acpi_device_fix_up_power_children() function
- ACPI: resource: Skip IRQ override on ASUS ExpertBook B1402CVA
- ACPI: processor_idle: use raw_safe_halt() in acpi_idle_play_dead()
- ACPI: video: Use acpi_device_fix_up_power_children()
- thunderbolt: Set lane bonding bit only for downstream port
- drm/ast: Disconnect BMC if physical connector is connected
- drm/msm/dpu: Add missing safe_lut_tbl in sc8280xp catalog
- kselftest/arm64: Fix output formatting for za-fork
- prctl: Disable prctl(PR_SET_MDWE) on parisc
- mm: add a NO_INHERIT flag to the PR_SET_MDWE prctl
- lockdep: Fix block chain corruption
- USB: dwc3: qcom: fix ACPI platform device leak
- USB: dwc3: qcom: fix resource leaks on probe deferral
- nvmet: nul-terminate the NQNs passed in the connect command
- nvme: blank out authentication fabrics options if not configured
- afs: Fix file locking on R/O volumes to operate in local mode
- afs: Return ENOENT if no cell DNS record can be found
- net: ipa: fix one GSI register field width
- net: axienet: Fix check for partial TX checksum
- vsock/test: fix SEQPACKET message bounds test
- i40e: Fix adding unsupported cloud filters
- amd-xgbe: propagate the correct speed and duplex status
- amd-xgbe: handle the corner-case during tx completion
- amd-xgbe: handle corner-case during sfp hotplug
- net: veth: fix ethtool stats reporting
- octeontx2-pf: Fix ntuple rule creation to direct packet to VF with higher Rx queue than its PF
- arm/xen: fix xen_vcpu_info allocation alignment
- arm64: mm: Fix "rodata=on" when CONFIG_RODATA_FULL_DEFAULT_ENABLED=y
- s390/ipl: add missing IPL_TYPE_ECKD_DUMP case to ipl_init()
- net/smc: avoid data corruption caused by decline
- net: usb: ax88179_178a: fix failed operations during ax88179_reset
- drm/panel: boe-tv101wum-nl6: Fine tune Himax83102-j02 panel HFP and HBP
- ipv4: Correct/silence an endian warning in __ip_do_redirect
- HID: fix HID device resource race between HID core and debugging support
- accel/ivpu/37xx: Fix hangs related to MMIO reset
- accel/ivpu: Do not initialize parameters on power up
- bpf: Fix dev's rx stats for bpf_redirect_peer traffic
- net: Move {l,t,d}stats allocation to core and convert veth & vrf
- net, vrf: Move dstats structure to core
- PM: tools: Fix sleepgraph syntax error
- drm/rockchip: vop: Fix color for RGB888/BGR888 format on VOP full
- libfs: getdents() should return 0 after reaching EOD
- block: update the stable_writes flag in bdev_add
- filemap: add a per-mapping stable writes flag
- drm/i915: do not clean GT table on error path
- ata: pata_isapnp: Add missing error check for devm_ioport_map()
- octeontx2-pf: Fix memory leak during interface down
- wireguard: use DEV_STATS_INC()
- net: wangxun: fix kernel panic due to null pointer
- drm/panel: simple: Fix Innolux G101ICE-L01 timings
- drm/panel: simple: Fix Innolux G101ICE-L01 bus flags
- fs: Pass AT_GETATTR_NOSEC flag to getattr interface function
- drm/panel: auo,b101uan08.3: Fine tune the panel power sequence
- blk-cgroup: avoid to warn !rcu_read_lock_held() in blkg_lookup()
- afs: Make error on cell lookup failure consistent with OpenAFS
- afs: Fix afs_server_list to be cleaned up with RCU
- rxrpc: Defer the response to a PING ACK until we've parsed it
- rxrpc: Fix RTT determination to use any ACK as a source
- s390/ism: ism driver implies smc protocol
- drm/msm/dsi: use the correct VREG_CTRL_1 value for 4nm cphy
- sched/fair: Fix the decision for load balance
- sched/eevdf: Fix vruntime adjustment on reweight
- hv/hv_kvp_daemon: Some small fixes for handling NM keyfiles
- irqchip/gic-v3-its: Flush ITS tables correctly in non-coherent GIC designs
- NFSD: Fix checksum mismatches in the duplicate reply cache
- NFSD: Fix "start of NFS reply" pointer passed to nfsd_cache_update()
- !3310  kasan: fix the compilation error for memcpy_mcs()
- kasan: fix the compilation error for memcpy_mcs()
- arm64: arch_timer: disable CONFIG_ARM_ARCH_TIMER_WORKAROUND_IN_USERSPACE
- vdso: do cntvct workaround in the VDSO
- arm64: arch_timer: Disable CNTVCT_EL0 trap if workaround is enabled
- mm/sharepool: Protect the va reserved for sharepool
- mm/sharepool: support fork() and exit() to handle the mm
- mm/sharepool: Add proc interfaces to show sp info
- mm/sharepool: Implement mg_sp_config_dvpp_range()
- mm/sharepool: Implement mg_sp_id_of_current()
- mm/sharepool: Implement mg_sp_group_id_by_pid()
- mm/sharepool: Implement mg_sp_group_add_task()
- mm/sharepool: Implement mg_sp_make_share_k2u()
- mm/sharepool: Implement mg_sp_alloc()
- mm/sharepool: Implement mg_sp_free()
- mm/sharepool: Implement mg_sp_walk_page_range()
- mm/sharepool: Implement mg_sp_unshare_kva
- mm/sharepool: Implement mg_sp_make_share_u2k()
- mm/sharepool: Reserve the va space for share_pool
- mm/sharepool: Add sp_area management code
- mm/sharepool: Add base framework for share_pool
- mm: Extend mmap assocated functions to accept mm_struct
- mm/vmalloc: Extend vmalloc usage about hugepage
- mm/hugetlb: Introduce hugetlb_insert_hugepage_pte[_by_pa]
- ARM: Add unwinding annotations to __loop.*delay functions
- !3285  arm64: errata: add option to disable cache readunique prefetch on HIP08
- !3280  arm64: add machine check safe support
- !3036  Added SM3 as module signing algorithm
- ext4: Block writes to journal device
- xfs: Block writes to log device
- fs: Block writes to mounted block devices
- btrfs: Do not restrict writes to btrfs devices
- block: Add config option to not allow writing to mounted devices
- arm64: errata: enable HISILICON_ERRATUM_HIP08_RU_PREFETCH
- arm64: errata: add option to disable cache readunique prefetch on HIP08
- arm64: add machine check safe sysctl interface
- arm64: introduce copy_mc_to_kernel() implementation
- arm64: support copy_mc_[user]_highpage()
- mm/hwpoison: return -EFAULT when copy fail in copy_mc_[user]_highpage()
- arm64: add uaccess to machine check safe
- arm64: add support for machine check error safe
- uaccess: add generic fallback version of copy_mc_to_user()
- !3275  arm64: kernel: disable CNP on LINXICORE9100
- !3099  block: Make blkdev_get_by_*() return
- arm64: kernel: disable CNP on LINXICORE9100
- !3111  openeuler_defconfig: enable some mm new
- !3211  Add SDEI Watchdog Support
- !3041  Random boot-time optimization
- !3026  Backport ARM64-ILP32 patches
- !3156  xfs: fix intent item leak during reovery
- !3137  LoongArch: add old BPI compatibility
- !3218  ipvlan: Introduce l2e mode
- !3209  exec: Remove redundant check in do_open_execat/uselib
- ipvlan: Introduce local xmit queue for l2e mode
- ipvlan: Introduce l2e mode
- arm64: kexec: only clear EOI for SDEI in NMI context
- stop_machine: mask sdei before running the callback
- openeuler_defconfig: Enable SDEI Watchdog
- kprobes/arm64: Blacklist sdei watchdog callback functions
- init: only move down lockup_detector_init() when sdei_watchdog is enabled
- sdei_watchdog: avoid possible false hardlockup
- sdei_watchdog: set secure timer period base on 'watchdog_thresh'
- sdei_watchdog: clear EOI of the secure timer before kdump
- watchdog: add nmi_watchdog support for arm64 based on SDEI
- lockup_detector: init lockup detector after all the init_calls
- firmware: arm_sdei: make 'sdei_api_event_disable/enable' public
- firmware: arm_sdei: add interrupt binding api
- exec: Remove redundant check in do_open_execat/uselib
- xfs: abort intent items when recovery intents fail
- xfs: factor out xfs_defer_pending_abort
- !3141 Backport 6.6.3 LTS Patches
- drm/amd/display: Change the DMCUB mailbox memory location from FB to inbox
- drm/amd/display: Clear dpcd_sink_ext_caps if not set
- drm/amd/display: Enable fast plane updates on DCN3.2 and above
- drm/amd/display: fix a NULL pointer dereference in amdgpu_dm_i2c_xfer()
- drm/amd/display: Fix DSC not Enabled on Direct MST Sink
- drm/amd/display: Guard against invalid RPTR/WPTR being set
- drm/amdgpu: Fix possible null pointer dereference
- drm/amdgpu: lower CS errors to debug severity
- drm/amdgpu: fix error handling in amdgpu_bo_list_get()
- drm/amdgpu: fix error handling in amdgpu_vm_init
- drm/amdgpu: don't use ATRM for external devices
- drm/amdgpu: add a retry for IP discovery init
- drm/amdgpu: fix GRBM read timeout when do mes_self_test
- drm/amdgpu: don't use pci_is_thunderbolt_attached()
- drm/amdgpu/smu13: drop compute workload workaround
- drm/amd/pm: Fix error of MACO flag setting code
- drm/i915: Flush WC GGTT only on required platforms
- drm/i915: Fix potential spectre vulnerability
- drm/i915: Bump GLK CDCLK frequency when driving multiple pipes
- drm/i915/mtl: Support HBR3 rate with C10 phy and eDP in MTL
- drm/amd/display: Add Null check for DPP resource
- x86/srso: Move retbleed IBPB check into existing 'has_microcode' code block
- drm: bridge: it66121: ->get_edid callback must not return err pointers
- drm/amd/pm: Handle non-terminated overdrive commands.
- ext4: fix racy may inline data check in dio write
- ext4: properly sync file size update after O_SYNC direct IO
- ext4: add missed brelse in update_backups
- ext4: remove gdb backup copy for meta bg in setup_new_flex_group_blocks
- ext4: correct the start block of counting reserved clusters
- ext4: correct return value of ext4_convert_meta_bg
- ext4: mark buffer new if it is unwritten to avoid stale data exposure
- ext4: correct offset of gdb backup in non meta_bg group to update_backups
- ext4: apply umask if ACL support is disabled
- ext4: make sure allocate pending entry not fail
- ext4: no need to generate from free list in mballoc
- ext4: fix race between writepages and remount
- Revert "net: r8169: Disable multicast filter for RTL8168H and RTL8107E"
- Revert "HID: logitech-dj: Add support for a new lightspeed receiver iteration"
- media: qcom: camss: Fix csid-gen2 for test pattern generator
- media: qcom: camss: Fix invalid clock enable bit disjunction
- media: qcom: camss: Fix set CSI2_RX_CFG1_VC_MODE when VC is greater than 3
- media: qcom: camss: Fix missing vfe_lite clocks check
- media: qcom: camss: Fix VFE-480 vfe_disable_output()
- media: qcom: camss: Fix VFE-17x vfe_disable_output()
- media: qcom: camss: Fix vfe_get() error jump
- media: qcom: camss: Fix pm_domain_on sequence in probe
- mmc: sdhci-pci-gli: GL9750: Mask the replay timer timeout of AER
- r8169: add handling DASH when DASH is disabled
- r8169: fix network lost after resume on DASH systems
- selftests: mptcp: fix fastclose with csum failure
- mptcp: fix setsockopt(IP_TOS) subflow locking
- mptcp: add validity check for sending RM_ADDR
- mptcp: deal with large GSO size
- mm: kmem: drop __GFP_NOFAIL when allocating objcg vectors
- mm: fix for negative counter: nr_file_hugepages
- mmc: sdhci-pci-gli: A workaround to allow GL9750 to enter ASPM L1.2
- riscv: kprobes: allow writing to x0
- riscv: correct pt_level name via pgtable_l5/4_enabled
- riscv: mm: Update the comment of CONFIG_PAGE_OFFSET
- riscv: put interrupt entries into .irqentry.text
- riscv: Using TOOLCHAIN_HAS_ZIHINTPAUSE marco replace zihintpause
- swiotlb: fix out-of-bounds TLB allocations with CONFIG_SWIOTLB_DYNAMIC
- swiotlb: do not free decrypted pages if dynamic
- tracing: fprobe-event: Fix to check tracepoint event and return
- LoongArch: Mark __percpu functions as always inline
- NFSD: Update nfsd_cache_append() to use xdr_stream
- nfsd: fix file memleak on client_opens_release
- dm-verity: don't use blocking calls from tasklets
- dm-bufio: fix no-sleep mode
- drm/mediatek/dp: fix memory leak on ->get_edid callback error path
- drm/mediatek/dp: fix memory leak on ->get_edid callback audio detection
- media: ccs: Correctly initialise try compose rectangle
- media: venus: hfi: add checks to handle capabilities from firmware
- media: venus: hfi: fix the check to handle session buffer requirement
- media: venus: hfi_parser: Add check to keep the number of codecs within range
- media: sharp: fix sharp encoding
- media: lirc: drop trailing space from scancode transmit
- f2fs: split initial and dynamic conditions for extent_cache
- f2fs: avoid format-overflow warning
- f2fs: set the default compress_level on ioctl
- f2fs: do not return EFSCORRUPTED, but try to run online repair
- i2c: i801: fix potential race in i801_block_transaction_byte_by_byte
- gfs2: don't withdraw if init_threads() got interrupted
- net: phylink: initialize carrier state at creation
- net: dsa: lan9303: consequently nested-lock physical MDIO
- net: ethtool: Fix documentation of ethtool_sprintf()
- s390/ap: fix AP bus crash on early config change callback invocation
- i2c: designware: Disable TX_EMPTY irq while waiting for block length byte
- sbsa_gwdt: Calculate timeout with 64-bit math
- lsm: fix default return value for inode_getsecctx
- lsm: fix default return value for vm_enough_memory
- Revert "i2c: pxa: move to generic GPIO recovery"
- Revert ncsi: Propagate carrier gain/loss events to the NCSI controller
- ALSA: hda/realtek: Add quirks for HP Laptops
- ALSA: hda/realtek: Enable Mute LED on HP 255 G10
- ALSA: hda/realtek - Enable internal speaker of ASUS K6500ZC
- ALSA: hda/realtek - Add Dell ALC295 to pin fall back table
- ALSA: hda/realtek: Enable Mute LED on HP 255 G8
- ALSA: info: Fix potential deadlock at disconnection
- btrfs: zoned: wait for data BG to be finished on direct IO allocation
- xfs: recovery should not clear di_flushiter unconditionally
- cifs: Fix encryption of cleared, but unset rq_iter data buffers
- cifs: do not pass cifs_sb when trying to add channels
- cifs: do not reset chan_max if multichannel is not supported at mount
- cifs: force interface update before a fresh session setup
- cifs: reconnect helper should set reconnect for the right channel
- smb: client: fix mount when dns_resolver key is not available
- smb: client: fix potential deadlock when releasing mids
- smb: client: fix use-after-free in smb2_query_info_compound()
- smb: client: fix use-after-free bug in cifs_debug_data_proc_show()
- smb3: fix caching of ctime on setxattr
- smb3: allow dumping session and tcon id to improve stats analysis and debugging
- smb3: fix touch -h of symlink
- smb3: fix creating FIFOs when mounting with "sfu" mount option
- xhci: Enable RPM on controllers that support low-power states
- parisc: fix mmap_base calculation when stack grows upwards
- parisc/power: Fix power soft-off when running on qemu
- parisc/pgtable: Do not drop upper 5 address bits of physical address
- parisc: Prevent booting 64-bit kernels on PA1.x machines
- selftests/resctrl: Extend signal handler coverage to unmount on receiving signal
- selftests/resctrl: Make benchmark command const and build it with pointers
- selftests/resctrl: Simplify span lifetime
- selftests/resctrl: Remove bw_report and bm_type from main()
- rcutorture: Fix stuttering races and other issues
- torture: Make torture_hrtimeout_ns() take an hrtimer mode parameter
- drm/amd/display: enable dsc_clk even if dsc_pg disabled
- Bluetooth: btusb: Add 0bda:b85b for Fn-Link RTL8852BE
- Bluetooth: btusb: Add RTW8852BE device 13d3:3570 to device tables
- apparmor: Fix regression in mount mediation
- apparmor: pass cred through to audit info.
- apparmor: rename audit_data->label to audit_data->subj_label
- apparmor: combine common_audit_data and apparmor_audit_data
- apparmor: Fix kernel-doc warnings in apparmor/policy.c
- apparmor: Fix kernel-doc warnings in apparmor/resource.c
- apparmor: Fix kernel-doc warnings in apparmor/lib.c
- apparmor: Fix kernel-doc warnings in apparmor/audit.c
- cxl/port: Fix delete_endpoint() vs parent unregistration race
- cxl/region: Fix x1 root-decoder granularity calculations
- i3c: master: svc: fix random hot join failure since timeout error
- i3c: master: svc: fix SDA keep low when polling IBIWON timeout happen
- i3c: master: svc: fix check wrong status register in irq handler
- i3c: master: svc: fix ibi may not return mandatory data byte
- i3c: master: svc: fix wrong data return when IBI happen during start frame
- i3c: master: svc: fix race condition in ibi work thread
- i3c: master: cdns: Fix reading status register
- cxl/region: Do not try to cleanup after cxl_region_setup_targets() fails
- mtd: cfi_cmdset_0001: Byte swap OTP info
- mm: make PR_MDWE_REFUSE_EXEC_GAIN an unsigned long
- mm/memory_hotplug: use pfn math in place of direct struct page manipulation
- mm/hugetlb: use nth_page() in place of direct struct page manipulation
- mm/cma: use nth_page() in place of direct struct page manipulation
- s390/cmma: fix detection of DAT pages
- s390/mm: add missing arch_set_page_dat() call to gmap allocations
- s390/mm: add missing arch_set_page_dat() call to vmem_crst_alloc()
- dmaengine: stm32-mdma: correct desc prep when channel running
- mcb: fix error handling for different scenarios when parsing
- driver core: Release all resources during unbind before updating device links
- tracing: Have the user copy of synthetic event address use correct context
- selftests/clone3: Fix broken test under !CONFIG_TIME_NS
- i2c: core: Run atomic i2c xfer when !preemptible
- mips: use nth_page() in place of direct struct page manipulation
- fs: use nth_page() in place of direct struct page manipulation
- scripts/gdb/vmalloc: disable on no-MMU
- kernel/reboot: emergency_restart: Set correct system_state
- quota: explicitly forbid quota files from being encrypted
- jbd2: fix potential data lost in recovering journal raced with synchronizing fs bdev
- ASoC: codecs: wsa-macro: fix uninitialized stack variables with name prefix
- hid: lenovo: Resend all settings on reset_resume for compact keyboards
- selftests/resctrl: Reduce failures due to outliers in MBA/MBM tests
- selftests/resctrl: Fix feature checks
- selftests/resctrl: Refactor feature check to use resource and feature name
- selftests/resctrl: Move _GNU_SOURCE define into Makefile
- selftests/resctrl: Remove duplicate feature check from CMT test
- selftests/resctrl: Fix uninitialized .sa_flags
- ASoC: codecs: wsa883x: make use of new mute_unmute_on_trigger flag
- ASoC: soc-dai: add flag to mute and unmute stream during trigger
- netfilter: nf_tables: split async and sync catchall in two functions
- netfilter: nf_tables: remove catchall element in GC sync path
- ima: detect changes to the backing overlay file
- ima: annotate iint mutex to avoid lockdep false positive warnings
- mfd: qcom-spmi-pmic: Fix revid implementation
- mfd: qcom-spmi-pmic: Fix reference leaks in revid helper
- leds: trigger: netdev: Move size check in set_device_name
- arm64: dts: qcom: ipq6018: Fix tcsr_mutex register size
- arm64: dts: qcom: ipq9574: Fix hwlock index for SMEM
- ACPI: FPDT: properly handle invalid FPDT subtables
- firmware: qcom_scm: use 64-bit calling convention only when client is 64-bit
- arm64: dts: qcom: ipq8074: Fix hwlock index for SMEM
- arm64: dts: qcom: ipq5332: Fix hwlock index for SMEM
- thermal: intel: powerclamp: fix mismatch in get function for max_idle
- btrfs: don't arbitrarily slow down delalloc if we're committing
- rcu: kmemleak: Ignore kmemleak false positives when RCU-freeing objects
- PM: hibernate: Clean up sync_read handling in snapshot_write_next()
- PM: hibernate: Use __get_safe_page() rather than touching the list
- dt-bindings: timer: renesas,rz-mtu3: Fix overflow/underflow interrupt names
- arm64: dts: qcom: ipq6018: Fix hwlock index for SMEM
- rcu/tree: Defer setting of jiffies during stall reset
- svcrdma: Drop connection after an RDMA Read error
- wifi: wilc1000: use vmm_table as array in wilc struct
- PCI: Lengthen reset delay for VideoPropulsion Torrent QN16e card
- PCI: exynos: Don't discard .remove() callback
- PCI: kirin: Don't discard .remove() callback
- PCI/ASPM: Fix L1 substate handling in aspm_attr_store_common()
- PCI: qcom-ep: Add dedicated callback for writing to DBI2 registers
- mmc: Add quirk MMC_QUIRK_BROKEN_CACHE_FLUSH for Micron eMMC Q2J54A
- mmc: sdhci_am654: fix start loop index for TAP value parsing
- mmc: vub300: fix an error code
- ksmbd: fix slab out of bounds write in smb_inherit_dacl()
- ksmbd: handle malformed smb1 message
- ksmbd: fix recursive locking in vfs helpers
- clk: qcom: ipq6018: drop the CLK_SET_RATE_PARENT flag from PLL clocks
- clk: qcom: ipq8074: drop the CLK_SET_RATE_PARENT flag from PLL clocks
- integrity: powerpc: Do not select CA_MACHINE_KEYRING
- clk: visconti: Fix undefined behavior bug in struct visconti_pll_provider
- clk: socfpga: Fix undefined behavior bug in struct stratix10_clock_data
- powercap: intel_rapl: Downgrade BIOS locked limits pr_warn() to pr_debug()
- cpufreq: stats: Fix buffer overflow detection in trans_stats()
- parisc/power: Add power soft-off when running on qemu
- parisc/pdc: Add width field to struct pdc_model
- parisc/agp: Use 64-bit LE values in SBA IOMMU PDIR table
- pmdomain: imx: Make imx pgc power domain also set the fwnode
- arm64: module: Fix PLT counting when CONFIG_RANDOMIZE_BASE=n
- arm64: Restrict CPU_BIG_ENDIAN to GNU as or LLVM IAS 15.x or newer
- pmdomain: amlogic: Fix mask for the second NNA mem PD domain
- PCI: keystone: Don't discard .probe() callback
- PCI: keystone: Don't discard .remove() callback
- KEYS: trusted: Rollback init_trusted() consistently
- KEYS: trusted: tee: Refactor register SHM usage
- pmdomain: bcm: bcm2835-power: check if the ASB register is equal to enable
- sched/core: Fix RQCF_ACT_SKIP leak
- genirq/generic_chip: Make irq_remove_generic_chip() irqdomain aware
- mmc: meson-gx: Remove setting of CMD_CFG_ERROR
- wifi: ath12k: fix dfs-radar and temperature event locking
- wifi: ath12k: fix htt mlo-offset event locking
- wifi: ath11k: fix gtk offload status event locking
- wifi: ath11k: fix htt pktlog locking
- wifi: ath11k: fix dfs radar event locking
- wifi: ath11k: fix temperature event locking
- regmap: Ensure range selector registers are updated after cache sync
- ACPI: resource: Do IRQ override on TongFang GMxXGxx
- parisc: Add nop instructions after TLB inserts
- mm/damon/sysfs: check error from damon_sysfs_update_target()
- mm/damon/core.c: avoid unintentional filtering out of schemes
- mm/damon/sysfs-schemes: handle tried regions sysfs directory allocation failure
- mm/damon/sysfs-schemes: handle tried region directory allocation failure
- mm/damon/core: avoid divide-by-zero during monitoring results update
- mm/damon: implement a function for max nr_accesses safe calculation
- mm/damon/ops-common: avoid divide-by-zero during region hotness calculation
- mm/damon/lru_sort: avoid divide-by-zero in hot threshold calculation
- dm crypt: account large pages in cc->n_allocated_pages
- fbdev: stifb: Make the STI next font pointer a 32-bit signed offset
- iommufd: Fix missing update of domains_itree after splitting iopt_area
- watchdog: move softlockup_panic back to early_param
- mm/damon/sysfs: update monitoring target regions for online input commit
- mm/damon/sysfs: remove requested targets when online-commit inputs
- PCI/sysfs: Protect driver's D3cold preference from user space
- hvc/xen: fix event channel handling for secondary consoles
- hvc/xen: fix error path in xen_hvc_init() to always register frontend driver
- hvc/xen: fix console unplug
- acpi/processor: sanitize _OSC/_PDC capabilities for Xen dom0
- tty: serial: meson: fix hard LOCKUP on crtscts mode
- tty/sysrq: replace smp_processor_id() with get_cpu()
- proc: sysctl: prevent aliased sysctls from getting passed to init
- audit: don't WARN_ON_ONCE(!current->mm) in audit_exe_compare()
- audit: don't take task_lock() in audit_exe_compare() code path
- sched: psi: fix unprivileged polling against cgroups
- mmc: sdhci-pci-gli: GL9755: Mask the replay timer timeout of AER
- KVM: x86: Fix lapic timer interrupt lost after loading a snapshot.
- KVM: x86: Clear bit12 of ICR after APIC-write VM-exit
- KVM: x86: Ignore MSR_AMD64_TW_CFG access
- KVM: x86: hyper-v: Don't auto-enable stimer on write from user-space
- x86/cpu/hygon: Fix the CPU topology evaluation for real
- x86/apic/msi: Fix misconfigured non-maskable MSI quirk
- x86/PCI: Avoid PME from D3hot/D3cold for AMD Rembrandt and Phoenix USB4
- crypto: x86/sha - load modules based on CPU features
- x86/shstk: Delay signal entry SSP write until after user accesses
- scsi: ufs: core: Fix racing issue between ufshcd_mcq_abort() and ISR
- scsi: qla2xxx: Fix system crash due to bad pointer access
- scsi: ufs: qcom: Update PHY settings only when scaling to higher gears
- scsi: megaraid_sas: Increase register read retry rount from 3 to 30 for selected registers
- scsi: mpt3sas: Fix loop logic
- bpf: Fix precision tracking for BPF_ALU | BPF_TO_BE | BPF_END
- bpf: Fix check_stack_write_fixed_off() to correctly spill imm
- spi: Fix null dereference on suspend
- randstruct: Fix gcc-plugin performance mode to stay in group
- powerpc/perf: Fix disabling BHRB and instruction sampling
- perf intel-pt: Fix async branch flags
- media: venus: hfi: add checks to perform sanity on queue pointers
- drivers: perf: Check find_first_bit() return value
- perf: arm_cspmu: Reject events meant for other PMUs
- i915/perf: Fix NULL deref bugs with drm_dbg() calls
- perf/core: Fix cpuctx refcounting
- cifs: fix check of rc in function generate_smb3signingkey
- cifs: spnego: add ';' in HOST_KEY_LEN
- scsi: ufs: core: Expand MCQ queue slot to DeviceQueueDepth + 1
- tools/power/turbostat: Enable the C-state Pre-wake printing
- tools/power/turbostat: Fix a knl bug
- macvlan: Don't propagate promisc change to lower dev in passthru
- net: sched: do not offload flows with a helper in act_ct
- net/mlx5e: Check return value of snprintf writing to fw_version buffer for representors
- net/mlx5e: Check return value of snprintf writing to fw_version buffer
- net/mlx5e: Reduce the size of icosq_str
- net/mlx5: Increase size of irq name buffer
- net/mlx5e: Update doorbell for port timestamping CQ before the software counter
- net/mlx5e: Track xmit submission to PTP WQ after populating metadata map
- net/mlx5e: Avoid referencing skb after free-ing in drop path of mlx5e_sq_xmit_wqe
- net/mlx5e: Don't modify the peer sent-to-vport rules for IPSec offload
- net/mlx5e: Fix pedit endianness
- net/mlx5e: fix double free of encap_header in update funcs
- net/mlx5e: fix double free of encap_header
- net/mlx5: Decouple PHC .adjtime and .adjphase implementations
- net/mlx5: Free used cpus mask when an IRQ is released
- Revert "net/mlx5: DR, Supporting inline WQE when possible"
- io_uring/fdinfo: remove need for sqpoll lock for thread/pid retrieval
- gve: Fixes for napi_poll when budget is 0
- pds_core: fix up some format-truncation complaints
- pds_core: use correct index to mask irq
- net: stmmac: avoid rx queue overrun
- net: stmmac: fix rx budget limit check
- netfilter: nf_tables: bogus ENOENT when destroying element which does not exist
- netfilter: nf_tables: fix pointer math issue in nft_byteorder_eval()
- netfilter: nf_conntrack_bridge: initialize err to 0
- af_unix: fix use-after-free in unix_stream_read_actor()
- net: ethernet: cortina: Fix MTU max setting
- net: ethernet: cortina: Handle large frames
- net: ethernet: cortina: Fix max RX frame define
- bonding: stop the device in bond_setup_by_slave()
- ptp: annotate data-race around q->head and q->tail
- blk-mq: make sure active queue usage is held for bio_integrity_prep()
- xen/events: fix delayed eoi list handling
- ppp: limit MRU to 64K
- net: mvneta: fix calls to page_pool_get_stats
- tipc: Fix kernel-infoleak due to uninitialized TLV value
- net: hns3: fix VF wrong speed and duplex issue
- net: hns3: fix VF reset fail issue
- net: hns3: fix variable may not initialized problem in hns3_init_mac_addr()
- net: hns3: fix out-of-bounds access may occur when coalesce info is read via debugfs
- net: hns3: fix incorrect capability bit display for copper port
- net: hns3: add barrier in vf mailbox reply process
- net: hns3: fix add VLAN fail issue
- xen/events: avoid using info_for_irq() in xen_send_IPI_one()
- net: ti: icssg-prueth: Fix error cleanup on failing pruss_request_mem_region
- net: ti: icssg-prueth: Add missing icss_iep_put to error path
- tty: Fix uninit-value access in ppp_sync_receive()
- ipvlan: add ipvlan_route_v6_outbound() helper
- net: set SOCK_RCU_FREE before inserting socket into hashtable
- bpf: fix control-flow graph checking in privileged mode
- bpf: fix precision backtracking instruction iteration
- bpf: handle ldimm64 properly in check_cfg()
- gcc-plugins: randstruct: Only warn about true flexible arrays
- vhost-vdpa: fix use after free in vhost_vdpa_probe()
- vdpa_sim_blk: allocate the buffer zeroed
- riscv: split cache ops out of dma-noncoherent.c
- drm/i915/tc: Fix -Wformat-truncation in intel_tc_port_init
- gfs2: Silence "suspicious RCU usage in gfs2_permission" warning
- riscv: provide riscv-specific is_trap_insn()
- RISC-V: hwprobe: Fix vDSO SIGSEGV
- SUNRPC: Fix RPC client cleaned up the freed pipefs dentries
- NFSv4.1: fix SP4_MACH_CRED protection for pnfs IO
- SUNRPC: Add an IS_ERR() check back to where it was
- NFSv4.1: fix handling NFS4ERR_DELAY when testing for session trunking
- drm/i915/mtl: avoid stringop-overflow warning
- mtd: rawnand: meson: check return value of devm_kasprintf()
- mtd: rawnand: intel: check return value of devm_kasprintf()
- SUNRPC: ECONNRESET might require a rebind
- dt-bindings: serial: fix regex pattern for matching serial node children
- samples/bpf: syscall_tp_user: Fix array out-of-bound access
- samples/bpf: syscall_tp_user: Rename num_progs into nr_tests
- sched/core: Optimize in_task() and in_interrupt() a bit
- wifi: iwlwifi: Use FW rate for non-data frames
- mtd: rawnand: tegra: add missing check for platform_get_irq()
- pwm: Fix double shift bug
- drm/amdgpu: fix software pci_unplug on some chips
- ALSA: hda/realtek: Add quirk for ASUS UX7602ZM
- drm/qxl: prevent memory leak
- ASoC: ti: omap-mcbsp: Fix runtime PM underflow warnings
- i2c: dev: copy userspace array safely
- riscv: VMAP_STACK overflow detection thread-safe
- kgdb: Flush console before entering kgdb on panic
- gfs2: Fix slab-use-after-free in gfs2_qd_dealloc
- drm/amd/display: Avoid NULL dereference of timing generator
- media: imon: fix access to invalid resource for the second interface
- media: ccs: Fix driver quirk struct documentation
- media: cobalt: Use FIELD_GET() to extract Link Width
- gfs2: fix an oops in gfs2_permission
- gfs2: ignore negated quota changes
- media: ipu-bridge: increase sensor_name size
- media: vivid: avoid integer overflow
- media: gspca: cpia1: shift-out-of-bounds in set_flicker
- i3c: master: mipi-i3c-hci: Fix a kernel panic for accessing DAT_data.
- virtio-blk: fix implicit overflow on virtio_max_dma_size
- i2c: sun6i-p2wi: Prevent potential division by zero
- i2c: fix memleak in i2c_new_client_device()
- i2c: i801: Add support for Intel Birch Stream SoC
- i3c: mipi-i3c-hci: Fix out of bounds access in hci_dma_irq_handler
- 9p: v9fs_listxattr: fix %s null argument warning
- 9p/trans_fd: Annotate data-racy writes to file::f_flags
- usb: gadget: f_ncm: Always set current gadget in ncm_bind()
- usb: host: xhci: Avoid XHCI resume delay if SSUSB device is not present
- f2fs: fix error handling of __get_node_page
- f2fs: fix error path of __f2fs_build_free_nids
- soundwire: dmi-quirks: update HP Omen match
- usb: ucsi: glink: use the connector orientation GPIO to provide switch events
- usb: dwc3: core: configure TX/RX threshold for DWC3_IP
- phy: qualcomm: phy-qcom-eusb2-repeater: Zero out untouched tuning regs
- phy: qualcomm: phy-qcom-eusb2-repeater: Use regmap_fields
- dt-bindings: phy: qcom,snps-eusb2-repeater: Add magic tuning overrides
- tty: vcc: Add check for kstrdup() in vcc_probe()
- thunderbolt: Apply USB 3.x bandwidth quirk only in software connection manager
- iio: adc: stm32-adc: harden against NULL pointer deref in stm32_adc_probe()
- mfd: intel-lpss: Add Intel Lunar Lake-M PCI IDs
- exfat: support handle zero-size directory
- HID: Add quirk for Dell Pro Wireless Keyboard and Mouse KM5221W
- crypto: hisilicon/qm - prevent soft lockup in receive loop
- ASoC: Intel: soc-acpi-cht: Add Lenovo Yoga Tab 3 Pro YT3-X90 quirk
- PCI: Use FIELD_GET() in Sapphire RX 5600 XT Pulse quirk
- misc: pci_endpoint_test: Add Device ID for R-Car S4-8 PCIe controller
- PCI: dwc: Add missing PCI_EXP_LNKCAP_MLW handling
- PCI: dwc: Add dw_pcie_link_set_max_link_width()
- PCI: Disable ATS for specific Intel IPU E2000 devices
- PCI: Extract ATS disabling to a helper function
- PCI: Use FIELD_GET() to extract Link Width
- scsi: libfc: Fix potential NULL pointer dereference in fc_lport_ptp_setup()
- PCI: Do error check on own line to split long "if" conditions
- atm: iphase: Do PCI error checks on own line
- PCI: mvebu: Use FIELD_PREP() with Link Width
- PCI: tegra194: Use FIELD_GET()/FIELD_PREP() with Link Width fields
- gpiolib: of: Add quirk for mt2701-cs42448 ASoC sound
- ALSA: hda: Fix possible null-ptr-deref when assigning a stream
- ARM: 9320/1: fix stack depot IRQ stack filter
- HID: lenovo: Detect quirk-free fw on cptkbd and stop applying workaround
- jfs: fix array-index-out-of-bounds in diAlloc
- jfs: fix array-index-out-of-bounds in dbFindLeaf
- fs/jfs: Add validity check for db_maxag and db_agpref
- fs/jfs: Add check for negative db_l2nbperpage
- scsi: ibmvfc: Remove BUG_ON in the case of an empty event pool
- scsi: hisi_sas: Set debugfs_dir pointer to NULL after removing debugfs
- RDMA/hfi1: Use FIELD_GET() to extract Link Width
- ASoC: SOF: ipc4: handle EXCEPTION_CAUGHT notification from firmware
- crypto: pcrypt - Fix hungtask for PADATA_RESET
- ASoC: cs35l56: Use PCI SSID as the firmware UID
- ASoC: Intel: sof_sdw: Copy PCI SSID to struct snd_soc_card
- ASoC: SOF: Pass PCI SSID to machine driver
- ASoC: soc-card: Add storage for PCI SSID
- ASoC: mediatek: mt8188-mt6359: support dynamic pinctrl
- selftests/efivarfs: create-read: fix a resource leak
- arm64: dts: ls208xa: use a pseudo-bus to constrain usb dma size
- arm64: dts: rockchip: Add NanoPC T6 PCIe e-key support
- soc: qcom: pmic: Fix resource leaks in a device_for_each_child_node() loop
- drm/amd: check num of link levels when update pcie param
- drm/amd/display: fix num_ways overflow error
- drm/amd: Disable PP_PCIE_DPM_MASK when dynamic speed switching not supported
- drm/amdgpu: Fix a null pointer access when the smc_rreg pointer is NULL
- drm/amdkfd: Fix shift out-of-bounds issue
- drm/panel: st7703: Pick different reset sequence
- drm/amdgpu/vkms: fix a possible null pointer dereference
- drm/radeon: fix a possible null pointer dereference
- drm/panel/panel-tpo-tpg110: fix a possible null pointer dereference
- drm/panel: fix a possible null pointer dereference
- drm/amdgpu: Fix potential null pointer derefernce
- drm/amd: Fix UBSAN array-index-out-of-bounds for Polaris and Tonga
- drm/amd: Fix UBSAN array-index-out-of-bounds for SMU7
- drm/msm/dp: skip validity check for DP CTS EDID checksum
- drm: vmwgfx_surface.c: copy user-array safely
- drm_lease.c: copy user-array safely
- kernel: watch_queue: copy user-array safely
- kernel: kexec: copy user-array safely
- string.h: add array-wrappers for (v)memdup_user()
- drm/amd/display: use full update for clip size increase of large plane source
- drm/amd: Update `update_pcie_parameters` functions to use uint8_t arguments
- drm/amdgpu: update retry times for psp vmbx wait
- drm/amdkfd: Fix a race condition of vram buffer unref in svm code
- drm/amdgpu: not to save bo in the case of RAS err_event_athub
- md: don't rely on 'mddev->pers' to be set in mddev_suspend()
- drm/edid: Fixup h/vsync_end instead of h/vtotal
- drm/amd/display: add seamless pipe topology transition check
- drm/amd/display: Don't lock phantom pipe on disabling
- drm/amd/display: Blank phantom OTG before enabling
- drm/komeda: drop all currently held locks if deadlock happens
- drm/amdkfd: ratelimited SQ interrupt messages
- drm/gma500: Fix call trace when psb_gem_mm_init() fails
- platform/x86: thinkpad_acpi: Add battery quirk for Thinkpad X120e
- of: address: Fix address translation when address-size is greater than 2
- platform/chrome: kunit: initialize lock for fake ec_dev
- gpiolib: acpi: Add a ignore interrupt quirk for Peaq C1010
- tsnep: Fix tsnep_request_irq() format-overflow warning
- ACPI: EC: Add quirk for HP 250 G7 Notebook PC
- Bluetooth: Fix double free in hci_conn_cleanup
- Bluetooth: btusb: Add date->evt_skb is NULL check
- wifi: iwlwifi: mvm: fix size check for fw_link_id
- bpf: Ensure proper register state printing for cond jumps
- vsock: read from socket's error queue
- net: sfp: add quirk for FS's 2.5G copper SFP
- wifi: ath10k: Don't touch the CE interrupt registers after power up
- wifi: ath12k: mhi: fix potential memory leak in ath12k_mhi_register()
- net: annotate data-races around sk->sk_dst_pending_confirm
- net: annotate data-races around sk->sk_tx_queue_mapping
- wifi: mt76: fix clang-specific fortify warnings
- wifi: mt76: mt7921e: Support MT7992 IP in Xiaomi Redmibook 15 Pro (2023)
- net: sfp: add quirk for Fiberstone GPON-ONU-34-20BI
- ACPI: APEI: Fix AER info corruption when error status data has multiple sections
- wifi: ath12k: fix possible out-of-bound write in ath12k_wmi_ext_hal_reg_caps()
- wifi: ath10k: fix clang-specific fortify warning
- wifi: ath12k: fix possible out-of-bound read in ath12k_htt_pull_ppdu_stats()
- wifi: ath9k: fix clang-specific fortify warnings
- bpf: Detect IP == ksym.end as part of BPF program
- atl1c: Work around the DMA RX overflow issue
- wifi: mac80211: don't return unset power in ieee80211_get_tx_power()
- wifi: mac80211_hwsim: fix clang-specific fortify warning
- wifi: ath12k: Ignore fragments from uninitialized peer in dp
- wifi: plfxlc: fix clang-specific fortify warning
- x86/mm: Drop the 4 MB restriction on minimal NUMA node memory size
- workqueue: Provide one lock class key per work_on_cpu() callsite
- cpu/hotplug: Don't offline the last non-isolated CPU
- smp,csd: Throw an error if a CSD lock is stuck for too long
- srcu: Only accelerate on enqueue time
- clocksource/drivers/timer-atmel-tcb: Fix initialization on SAM9 hardware
- clocksource/drivers/timer-imx-gpt: Fix potential memory leak
- selftests/lkdtm: Disable CONFIG_UBSAN_TRAP in test config
- srcu: Fix srcu_struct node grpmask overflow on 64-bit systems
- perf/core: Bail out early if the request AUX area is out of bound
- x86/retpoline: Make sure there are no unconverted return thunks due to KCSAN
- lib/generic-radix-tree.c: Don't overflow in peek()
- btrfs: abort transaction on generation mismatch when marking eb as dirty
- locking/ww_mutex/test: Fix potential workqueue corruption
- LoongArch: use arch specific phys_to_dma
- LoongArch: Fixed EIOINTC structure members
- LoongArch: Fix virtual machine startup error
- LoongArch: Old BPI compatibility
- LoongArch: add kernel setvirtmap for runtime
- arm64: openeuler_defconfig: update for new feature
- x86: openeuler_defconfig: update from new feature
- erofs: fix NULL dereference of dif->bdev_handle in fscache mode
- block: Remove blkdev_get_by_*() functions
- bcache: Fixup error handling in register_cache()
- xfs: Convert to bdev_open_by_path()
- reiserfs: Convert to bdev_open_by_dev/path()
- ocfs2: Convert to use bdev_open_by_dev()
- nfs/blocklayout: Convert to use bdev_open_by_dev/path()
- jfs: Convert to bdev_open_by_dev()
- f2fs: Convert to bdev_open_by_dev/path()
- ext4: Convert to bdev_open_by_dev()
- erofs: Convert to use bdev_open_by_path()
- btrfs: Convert to bdev_open_by_path()
- fs: Convert to bdev_open_by_dev()
- mm/swap: Convert to use bdev_open_by_dev()
- PM: hibernate: Drop unused snapshot_test argument
- PM: hibernate: Convert to bdev_open_by_dev()
- scsi: target: Convert to bdev_open_by_path()
- s390/dasd: Convert to bdev_open_by_path()
- nvmet: Convert to bdev_open_by_path()
- mtd: block2mtd: Convert to bdev_open_by_dev/path()
- md: Convert to bdev_open_by_dev()
- dm: Convert to bdev_open_by_dev()
- bcache: Convert to bdev_open_by_path()
- zram: Convert to use bdev_open_by_dev()
- xen/blkback: Convert to bdev_open_by_dev()
- rnbd-srv: Convert to use bdev_open_by_path()
- pktcdvd: Convert to bdev_open_by_dev()
- drdb: Convert to use bdev_open_by_path()
- block: Use bdev_open_by_dev() in disk_scan_partitions() and blkdev_bszset()
- block: Use bdev_open_by_dev() in blkdev_open()
- block: Provide bdev_open_* functions
- alinux: random: speed up the initialization of module
- keys: Allow automatic module signature with SM3
- arm64: fix image size inflation with CONFIG_COMPAT_TASK_SIZE
- arm64: set 32-bit compatible TASK_SIZE_MAX to fix U32 libc_write_01 error
- arm64: replace is_compat_task() with is_ilp32_compat_task() in TASK_SIZE_MAX
- arm64: fix address limit problem with TASK_SIZE_MAX
- ilp32: fix compile problem when ARM64_ILP32 and UBSAN are both enabled
- arm64: fix abi change caused by ILP32
- arm64: fix AUDIT_ARCH_AARCH64ILP32 bug on audit subsystem
- ilp32: skip ARM erratum 1418040 for ilp32 application
- ilp32: avoid clearing upper 32 bits of syscall return value for ilp32
- arm64: secomp: fix the secure computing mode 1 syscall check for ilp32
- arm64:ilp32: add ARM64_ILP32 to Kconfig
- arm64:ilp32: add vdso-ilp32 and use for signal return
- arm64: ptrace: handle ptrace_request differently for aarch32 and ilp32
- arm64: ilp32: introduce ilp32-specific sigframe and ucontext
- arm64: signal32: move ilp32 and aarch32 common code to separated file
- arm64: signal: share lp64 signal structures and routines to ilp32
- arm64: ilp32: introduce syscall table for ILP32
- arm64: ilp32: share aarch32 syscall handlers
- arm64: ilp32: introduce binfmt_ilp32.c
- arm64: change compat_elf_hwcap and compat_elf_hwcap2 prefix to a32
- arm64: introduce binfmt_elf32.c
- arm64: introduce AUDIT_ARCH_AARCH64ILP32 for ilp32
- arm64: ilp32: add is_ilp32_compat_{task,thread} and TIF_32BIT_AARCH64
- arm64: introduce is_a32_compat_{task,thread} for AArch32 compat
- arm64: uapi: set __BITS_PER_LONG correctly for ILP32 and LP64
- arm64: rename functions that reference compat term
- arm64: rename COMPAT to AARCH32_EL0
- arm64: ilp32: add documentation on the ILP32 ABI for ARM64
- thread: move thread bits accessors to separated file
- ptrace: Add compat PTRACE_{G,S}ETSIGMASK handlers
- arm64: signal: Make parse_user_sigframe() independent of rt_sigframe layout

* Tue Dec 5 2023 Zheng Zengkai <zhengzengkai@huawei.com> - 6.6.0-1.0.0.1
- !3058  tcp/dccp: Add another way to allocate local ports in connect()
- !3064  mm: PCP high auto-tuning
- !2985  hugetlbfs: avoid overflow in hugetlbfs_fallocate
- !3059  Handle more faults under the VMA lock
- mm, pcp: reduce detecting time of consecutive high order page freeing
- mm, pcp: decrease PCP high if free pages < high watermark
- mm: tune PCP high automatically
- mm: add framework for PCP high auto-tuning
- mm, page_alloc: scale the number of pages that are batch allocated
- mm: restrict the pcp batch scale factor to avoid too long latency
- mm, pcp: reduce lock contention for draining high-order pages
- cacheinfo: calculate size of per-CPU data cache slice
- mm, pcp: avoid to drain PCP when process exit
- mm: handle write faults to RO pages under the VMA lock
- mm: handle read faults under the VMA lock
- mm: handle COW faults under the VMA lock
- mm: handle shared faults under the VMA lock
- mm: call wp_page_copy() under the VMA lock
- mm: make lock_folio_maybe_drop_mmap() VMA lock aware
- tcp/dccp: Add another way to allocate local ports in connect()
- !3044  mm: hugetlb: Skip initialization of gigantic tail struct pages if freed by HVO
- !2980  io_uring: fix soft lockup in io_submit_sqes()
- !3014  anolis: bond: broadcast ARP or ND messages to all slaves
- !3018  folio conversions for numa balance
- mm: hugetlb: skip initialization of gigantic tail struct pages if freed by HVO
- memblock: introduce MEMBLOCK_RSRV_NOINIT flag
- memblock: pass memblock_type to memblock_setclr_flag
- mm: hugetlb_vmemmap: use nid of the head page to reallocate it
- mm: remove page_cpupid_xchg_last()
- mm: use folio_xchg_last_cpupid() in wp_page_reuse()
- mm: convert wp_page_reuse() and finish_mkwrite_fault() to take a folio
- mm: make finish_mkwrite_fault() static
- mm: huge_memory: use folio_xchg_last_cpupid() in __split_huge_page_tail()
- mm: migrate: use folio_xchg_last_cpupid() in folio_migrate_flags()
- sched/fair: use folio_xchg_last_cpupid() in should_numa_migrate_memory()
- mm: add folio_xchg_last_cpupid()
- mm: remove xchg_page_access_time()
- mm: huge_memory: use a folio in change_huge_pmd()
- mm: mprotect: use a folio in change_pte_range()
- sched/fair: use folio_xchg_access_time() in numa_hint_fault_latency()
- mm: add folio_xchg_access_time()
- mm: remove page_cpupid_last()
- mm: huge_memory: use folio_last_cpupid() in __split_huge_page_tail()
- mm: huge_memory: use folio_last_cpupid() in do_huge_pmd_numa_page()
- mm: memory: use folio_last_cpupid() in do_numa_page()
- mm: add folio_last_cpupid()
- mm_types: add virtual and _last_cpupid into struct folio
- sched/numa, mm: make numa migrate functions to take a folio
- mm: mempolicy: make mpol_misplaced() to take a folio
- mm: memory: make numa_migrate_prep() to take a folio
- mm: memory: use a folio in do_numa_page()
- mm: huge_memory: use a folio in do_huge_pmd_numa_page()
- mm: memory: add vm_normal_folio_pmd()
- mm: migrate: remove isolated variable in add_page_for_migration()
- mm: migrate: remove PageHead() check for HugeTLB in add_page_for_migration()
- mm: migrate: use a folio in add_page_for_migration()
- mm: migrate: use __folio_test_movable()
- mm: migrate: convert migrate_misplaced_page() to migrate_misplaced_folio()
- mm: migrate: convert numamigrate_isolate_page() to numamigrate_isolate_folio()
- mm: migrate: remove THP mapcount check in numamigrate_isolate_page()
- mm: migrate: remove PageTransHuge check in numamigrate_isolate_page()
- anolis: bond: broadcast ARP or ND messages to all slaves
- hugetlbfs: avoid overflow in hugetlbfs_fallocate
- io_uring: fix soft lockup in io_submit_sqes()
- !2971  net: sched: sch_qfq: Use non-work-conserving warning handler
- !2968  checkpatch: Update link tags to fix ci warning
- net: sched: sch_qfq: Use non-work-conserving warning handler
- checkpatch: Update check of link tags
- !2945 Backport linux 6.6.2 LTS patches
- btrfs: make found_logical_ret parameter mandatory for function queue_scrub_stripe()
- btrfs: use u64 for buffer sizes in the tree search ioctls
- Revert "mmc: core: Capture correct oemid-bits for eMMC cards"
- Revert "PCI/ASPM: Disable only ASPM_STATE_L1 when driver, disables L1"
- x86/amd_nb: Use Family 19h Models 60h-7Fh Function 4 IDs
- io_uring/net: ensure socket is marked connected on connect retry
- selftests: mptcp: fix wait_rm_addr/sf parameters
- selftests: mptcp: run userspace pm tests slower
- eventfs: Check for NULL ef in eventfs_set_attr()
- tracing/kprobes: Fix the order of argument descriptions
- fbdev: fsl-diu-fb: mark wr_reg_wa() static
- ALSA: hda/realtek: Add support dual speaker for Dell
- fbdev: imsttfb: fix a resource leak in probe
- fbdev: imsttfb: fix double free in probe()
- arm64/arm: arm_pmuv3: perf: Don't truncate 64-bit registers
- spi: spi-zynq-qspi: add spi-mem to driver kconfig dependencies
- ASoC: dapm: fix clock get name
- ASoC: hdmi-codec: register hpd callback on component probe
- ASoC: mediatek: mt8186_mt6366_rt1019_rt5682s: trivial: fix error messages
- ASoC: rt712-sdca: fix speaker route missing issue
- drm/syncobj: fix DRM_SYNCOBJ_WAIT_FLAGS_WAIT_AVAILABLE
- drm/vc4: tests: Fix UAF in the mock helpers
- fs: dlm: Simplify buffer size computation in dlm_create_debug_file()
- module/decompress: use kvmalloc() consistently
- drivers: perf: Do not broadcast to other cpus when starting a counter
- net: ti: icss-iep: fix setting counter value
- RISC-V: Don't fail in riscv_of_parent_hartid() for disabled HARTs
- net/sched: act_ct: Always fill offloading tuple iifidx
- netfilter: nat: fix ipv6 nat redirect with mapped and scoped addresses
- netfilter: xt_recent: fix (increase) ipv6 literal buffer length
- i2c: iproc: handle invalid slave state
- net: enetc: shorten enetc_setup_xdp_prog() error message to fit NETLINK_MAX_FMTMSG_LEN
- virtio/vsock: Fix uninit-value in virtio_transport_recv_pkt()
- r8169: respect userspace disabling IFF_MULTICAST
- vsock/virtio: remove socket from connected/bound list on shutdown
- blk-core: use pr_warn_ratelimited() in bio_check_ro()
- nbd: fix uaf in nbd_open
- tg3: power down device only on SYSTEM_POWER_OFF
- ice: Fix VF-VF direction matching in drop rule in switchdev
- ice: Fix VF-VF filter rules in switchdev mode
- ice: lag: in RCU, use atomic allocation
- ice: Fix SRIOV LAG disable on non-compliant aggregate
- riscv: boot: Fix creation of loader.bin
- nvme: fix error-handling for io_uring nvme-passthrough
- net/smc: put sk reference if close work was canceled
- net/smc: allow cdc msg send rather than drop it with NULL sndbuf_desc
- net/smc: fix dangling sock under state SMC_APPFINCLOSEWAIT
- octeontx2-pf: Free pending and dropped SQEs
- selftests: pmtu.sh: fix result checking
- net: stmmac: xgmac: Enable support for multiple Flexible PPS outputs
- Fix termination state for idr_for_each_entry_ul()
- net: r8169: Disable multicast filter for RTL8168H and RTL8107E
- dccp/tcp: Call security_inet_conn_request() after setting IPv6 addresses.
- dccp: Call security_inet_conn_request() after setting IPv4 addresses.
- net: page_pool: add missing free_percpu when page_pool_init fail
- octeontx2-pf: Fix holes in error code
- octeontx2-pf: Fix error codes
- inet: shrink struct flowi_common
- bpf: Check map->usercnt after timer->timer is assigned
- rxrpc: Fix two connection reaping bugs
- tipc: Change nla_policy for bearer-related names to NLA_NUL_STRING
- hsr: Prevent use after free in prp_create_tagged_frame()
- llc: verify mac len before reading mac header
- watchdog: ixp4xx: Make sure restart always works
- watchdog: marvell_gti_wdt: Fix error code in probe()
- Input: synaptics-rmi4 - fix use after free in rmi_unregister_function()
- pwm: brcmstb: Utilize appropriate clock APIs in suspend/resume
- pwm: sti: Reduce number of allocations and drop usage of chip_data
- drm/amdgpu: don't put MQDs in VRAM on ARM | ARM64
- drm/amdgpu/gfx10,11: use memcpy_to/fromio for MQDs
- regmap: prevent noinc writes from clobbering cache
- cpupower: fix reference to nonexistent document
- media: cec: meson: always include meson sub-directory in Makefile
- media: platform: mtk-mdp3: fix uninitialized variable in mdp_path_config()
- media: mediatek: vcodec: using encoder device to alloc/free encoder memory
- media: imx-jpeg: notify source chagne event when the first picture parsed
- media: mediatek: vcodec: Handle invalid encoder vsi
- media: verisilicon: Fixes clock list for rk3588 av1 decoder
- media: dvb-usb-v2: af9035: fix missing unlock
- media: cadence: csi2rx: Unregister v4l2 async notifier
- media: i2c: imx219: Drop IMX219_REG_CSI_LANE_MODE from common regs array
- media: i2c: imx219: Replace register addresses with macros
- media: i2c: imx219: Convert to CCI register access helpers
- media: cedrus: Fix clock/reset sequence
- media: vidtv: mux: Add check and kfree for kstrdup
- media: vidtv: psi: Add check for kstrdup
- media: s3c-camif: Avoid inappropriate kfree()
- media: mtk-jpegenc: Fix bug in JPEG encode quality selection
- media: amphion: handle firmware debug message
- media: bttv: fix use after free error due to btv->timeout timer
- media: ov5640: Fix a memory leak when ov5640_probe fails
- media: i2c: max9286: Fix some redundant of_node_put() calls
- media: ov5640: fix vblank unchange issue when work at dvp mode
- media: ov13b10: Fix some error checking in probe
- media: verisilicon: Do not enable G2 postproc downscale if source is narrower than destination
- media: hantro: Check whether reset op is defined before use
- media: imx-jpeg: initiate a drain of the capture queue in dynamic resolution change
- pcmcia: ds: fix possible name leak in error path in pcmcia_device_add()
- pcmcia: ds: fix refcount leak in pcmcia_device_add()
- pcmcia: cs: fix possible hung task and memory leak pccardd()
- cxl/hdm: Remove broken error path
- cxl/port: Fix @host confusion in cxl_dport_setup_regs()
- cxl/core/regs: Rename @dev to @host in struct cxl_register_map
- cxl/region: Fix cxl_region_rwsem lock held when returning to user space
- cxl/region: Use cxl_calc_interleave_pos() for auto-discovery
- cxl/region: Calculate a target position in a region interleave
- cxl/region: Prepare the decoder match range helper for reuse
- rtc: pcf85363: fix wrong mask/val parameters in regmap_update_bits call
- virt: sevguest: Fix passing a stack buffer as a scatterlist target
- cxl/mem: Fix shutdown order
- cxl/memdev: Fix sanitize vs decoder setup locking
- cxl/pci: Fix sanitize notifier setup
- cxl/pci: Clarify devm host for memdev relative setup
- cxl/pci: Remove inconsistent usage of dev_err_probe()
- cxl/pci: Cleanup 'sanitize' to always poll
- cxl/pci: Remove unnecessary device reference management in sanitize work
- rtc: brcmstb-waketimer: support level alarm_irq
- i3c: Fix potential refcount leak in i3c_master_register_new_i3c_devs
- rtla: Fix uninitialized variable found
- 9p/net: fix possible memory leak in p9_check_errors()
- perf vendor events intel: Add broadwellde two metrics
- perf vendor events intel: Fix broadwellde tma_info_system_dram_bw_use metric
- perf hist: Add missing puts to hist__account_cycles
- libperf rc_check: Make implicit enabling work for GCC
- perf machine: Avoid out of bounds LBR memory read
- powerpc/vmcore: Add MMU information to vmcoreinfo
- usb: host: xhci-plat: fix possible kernel oops while resuming
- xhci: Loosen RPM as default policy to cover for AMD xHC 1.1
- perf vendor events: Update PMC used in PM_RUN_INST_CMPL event for power10 platform
- powerpc/pseries: fix potential memory leak in init_cpu_associativity()
- powerpc/imc-pmu: Use the correct spinlock initializer.
- powerpc/vas: Limit open window failure messages in log bufffer
- perf trace: Use the right bpf_probe_read(_str) variant for reading user data
- powerpc: Hide empty pt_regs at base of the stack
- powerpc/xive: Fix endian conversion size
- powerpc/40x: Remove stale PTE_ATOMIC_UPDATES macro
- perf tools: Do not ignore the default vmlinux.h
- modpost: fix ishtp MODULE_DEVICE_TABLE built on big-endian host
- modpost: fix tee MODULE_DEVICE_TABLE built on big-endian host
- s390/ap: re-init AP queues on config on
- perf mem-events: Avoid uninitialized read
- perf parse-events: Fix for term values that are raw events
- perf build: Add missing comment about NO_LIBTRACEEVENT=1
- interconnect: fix error handling in qnoc_probe()
- powerpc: Only define __parse_fpscr() when required
- interconnect: qcom: osm-l3: Replace custom implementation of COUNT_ARGS()
- interconnect: qcom: sm8350: Set ACV enable_mask
- interconnect: qcom: sm8250: Set ACV enable_mask
- interconnect: qcom: sm8150: Set ACV enable_mask
- interconnect: qcom: sm6350: Set ACV enable_mask
- interconnect: qcom: sdm845: Set ACV enable_mask
- interconnect: qcom: sdm670: Set ACV enable_mask
- interconnect: qcom: sc8280xp: Set ACV enable_mask
- interconnect: qcom: sc8180x: Set ACV enable_mask
- interconnect: qcom: sc7280: Set ACV enable_mask
- interconnect: qcom: sc7180: Set ACV enable_mask
- interconnect: qcom: qdu1000: Set ACV enable_mask
- f2fs: fix to initialize map.m_pblk in f2fs_precache_extents()
- dmaengine: pxa_dma: Remove an erroneous BUG_ON() in pxad_free_desc()
- USB: usbip: fix stub_dev hub disconnect
- tools: iio: iio_generic_buffer ensure alignment
- debugfs: Fix __rcu type comparison warning
- misc: st_core: Do not call kfree_skb() under spin_lock_irqsave()
- tools/perf: Update call stack check in builtin-lock.c
- dmaengine: ti: edma: handle irq_of_parse_and_map() errors
- usb: chipidea: Simplify Tegra DMA alignment code
- usb: chipidea: Fix DMA overwrite for Tegra
- usb: dwc2: fix possible NULL pointer dereference caused by driver concurrency
- dmaengine: idxd: Register dsa_bus_type before registering idxd sub-drivers
- perf record: Fix BTF type checks in the off-cpu profiling
- perf vendor events arm64: Fix for AmpereOne metrics
- pinctrl: renesas: rzg2l: Make reverse order of enable() for disable()
- livepatch: Fix missing newline character in klp_resolve_symbols()
- perf parse-events: Fix tracepoint name memory leak
- tty: tty_jobctrl: fix pid memleak in disassociate_ctty()
- f2fs: fix to drop meta_inode's page cache in f2fs_put_super()
- f2fs: compress: fix to avoid redundant compress extension
- f2fs: compress: fix to avoid use-after-free on dic
- f2fs: compress: fix deadloop in f2fs_write_cache_pages()
- perf kwork: Set ordered_events to true in 'struct perf_tool'
- perf kwork: Add the supported subcommands to the document
- perf kwork: Fix incorrect and missing free atom in work_push_atom()
- pinctrl: baytrail: fix debounce disable case
- iio: frequency: adf4350: Use device managed functions and fix power down issue.
- perf stat: Fix aggr mode initialization
- apparmor: fix invalid reference on profile->disconnected
- scripts/gdb: fix usage of MOD_TEXT not defined when CONFIG_MODULES=n
- leds: trigger: ledtrig-cpu:: Fix 'output may be truncated' issue for 'cpu'
- leds: pwm: Don't disable the PWM when the LED should be off
- leds: turris-omnia: Do not use SMBUS calls
- mfd: arizona-spi: Set pdata.hpdet_channel for ACPI enumerated devs
- dt-bindings: mfd: mt6397: Split out compatible for MediaTek MT6366 PMIC
- mfd: dln2: Fix double put in dln2_probe
- mfd: core: Ensure disabled devices are skipped without aborting
- mfd: core: Un-constify mfd_cell.of_reg
- IB/mlx5: Fix init stage error handling to avoid double free of same QP and UAF
- erofs: fix erofs_insert_workgroup() lockref usage
- ASoC: ams-delta.c: use component after check
- crypto: qat - fix deadlock in backlog processing
- crypto: qat - fix ring to service map for QAT GEN4
- crypto: qat - use masks for AE groups
- crypto: qat - refactor fw config related functions
- crypto: qat - enable dc chaining service
- crypto: qat - consolidate services structure
- certs: Break circular dependency when selftest is modular
- padata: Fix refcnt handling in padata_free_shell()
- PCI: endpoint: Fix double free in __pci_epc_create()
- ASoC: Intel: Skylake: Fix mem leak when parsing UUIDs fails
- HID: logitech-hidpp: Move get_wireless_feature_index() check to hidpp_connect_event()
- HID: logitech-hidpp: Revert "Don't restart communication if not necessary"
- HID: logitech-hidpp: Don't restart IO, instead defer hid_connect() only
- sh: bios: Revive earlyprintk support
- HID: uclogic: Fix a work->entry not empty bug in __queue_work()
- HID: uclogic: Fix user-memory-access bug in uclogic_params_ugee_v2_init_event_hooks()
- hid: cp2112: Fix IRQ shutdown stopping polling for all IRQs on chip
- RDMA/hfi1: Workaround truncation compilation error
- scsi: ufs: core: Leave space for '\0' in utf8 desc string
- ASoC: fsl: Fix PM disable depth imbalance in fsl_easrc_probe
- ASoC: intel: sof_sdw: Stop processing CODECs when enough are found
- ASoC: SOF: core: Ensure sof_ops_free() is still called when probe never ran.
- RDMA/hns: Fix init failure of RoCE VF and HIP08
- RDMA/hns: Fix unnecessary port_num transition in HW stats allocation
- RDMA/hns: The UD mode can only be configured with DCQCN
- RDMA/hns: Add check for SL
- RDMA/hns: Fix signed-unsigned mixed comparisons
- RDMA/hns: Fix uninitialized ucmd in hns_roce_create_qp_common()
- RDMA/hns: Fix printing level of asynchronous events
- IB/mlx5: Fix rdma counter binding for RAW QP
- dlm: fix no ack after final message
- dlm: be sure we reset all nodes at forced shutdown
- dlm: fix remove member after close call
- dlm: fix creating multiple node structures
- fs: dlm: Fix the size of a buffer in dlm_create_debug_file()
- ASoC: fsl-asoc-card: Add comment for mclk in the codec_priv
- ASoC: Intel: sof_sdw_rt_sdca_jack_common: add rt713 support
- backlight: pwm_bl: Disable PWM on shutdown, suspend and remove
- ASoC: fsl: mpc5200_dma.c: Fix warning of Function parameter or member not described
- kselftest: vm: fix mdwe's mmap_FIXED test case
- ext4: move 'ix' sanity check to corrent position
- ext4: add missing initialization of call_notify_error in update_super_work()
- ARM: 9323/1: mm: Fix ARCH_LOW_ADDRESS_LIMIT when CONFIG_ZONE_DMA
- ARM: 9321/1: memset: cast the constant byte to unsigned char
- crypto: hisilicon/qm - fix PF queue parameter issue
- hid: cp2112: Fix duplicate workqueue initialization
- PCI: vmd: Correct PCI Header Type Register's multi-function check
- ASoC: SOF: ipc4-topology: Use size_add() in call to struct_size()
- crypto: qat - increase size of buffers
- crypto: caam/jr - fix Chacha20 + Poly1305 self test failure
- crypto: caam/qi2 - fix Chacha20 + Poly1305 self test failure
- nd_btt: Make BTT lanes preemptible
- libnvdimm/of_pmem: Use devm_kstrdup instead of kstrdup and check its return value
- ASoC: soc-pcm.c: Make sure DAI parameters cleared if the DAI becomes inactive
- scsi: ibmvfc: Fix erroneous use of rtas_busy_delay with hcall return code
- crypto: qat - fix unregistration of compression algorithms
- crypto: qat - fix unregistration of crypto algorithms
- crypto: qat - ignore subsequent state up commands
- crypto: qat - fix state machines cleanup paths
- RDMA/core: Use size_{add,sub,mul}() in calls to struct_size()
- hwrng: geode - fix accessing registers
- hwrng: bcm2835 - Fix hwrng throughput regression
- crypto: hisilicon/hpre - Fix a erroneous check after snprintf()
- crypto: ccp - Fix some unfused tests
- crypto: ccp - Fix sample application signature passing
- crypto: ccp - Fix DBC sample application error handling
- crypto: ccp - Fix ioctl unit tests
- crypto: ccp - Get a free page to use while fetching initial nonce
- KEYS: Include linux/errno.h in linux/verification.h
- ALSA: hda: cs35l41: Undo runtime PM changes at driver exit time
- ALSA: hda: cs35l41: Fix unbalanced pm_runtime_get()
- ASoC: cs35l41: Undo runtime PM changes at driver exit time
- ASoC: cs35l41: Verify PM runtime resume errors in IRQ handler
- ASoC: cs35l41: Fix broken shared boost activation
- ASoC: cs35l41: Initialize completion object before requesting IRQ
- ASoC: cs35l41: Handle mdsync_up reg write errors
- ASoC: cs35l41: Handle mdsync_down reg write errors
- module/decompress: use vmalloc() for gzip decompression workspace
- iommufd: Add iopt_area_alloc()
- ARM: dts: BCM5301X: Explicitly disable unused switch CPU ports
- soc: qcom: pmic_glink: fix connector type to be DisplayPort
- selftests/resctrl: Ensure the benchmark commands fits to its array
- selftests/pidfd: Fix ksft print formats
- arm64: tegra: Use correct interrupts for Tegra234 TKE
- memory: tegra: Set BPMP msg flags to reset IPC channels
- firmware: tegra: Add suspend hook and reset BPMP IPC early on resume
- arm64: tegra: Fix P3767 QSPI speed
- arm64: tegra: Fix P3767 card detect polarity
- arm64: dts: imx8mn: Add sound-dai-cells to micfil node
- arm64: dts: imx8mm: Add sound-dai-cells to micfil node
- arm64: dts: imx8mp-debix-model-a: Remove USB hub reset-gpios
- arm64: dts: imx8qm-ss-img: Fix jpegenc compatible entry
- clk: scmi: Free scmi_clk allocated when the clocks with invalid info are skipped
- ARM: dts: am3517-evm: Fix LED3/4 pinmux
- firmware: arm_ffa: Allow the FF-A drivers to use 32bit mode of messaging
- firmware: arm_ffa: Assign the missing IDR allocation ID to the FFA device
- arm64: dts: ti: Fix HDMI Audio overlay in Makefile
- arm64: dts: ti: k3-am62a7-sk: Drop i2c-1 to 100Khz
- arm64: dts: ti: k3-am625-beagleplay: Fix typo in ramoops reg
- arm64: dts: ti: verdin-am62: disable MIPI DSI bridge
- arm64: dts: ti: k3-j721s2-evm-gesi: Specify base dtb for overlay file
- firmware: ti_sci: Mark driver as non removable
- ARM: dts: stm32: stm32f7-pinctrl: don't use multiple blank lines
- kunit: test: Fix the possible memory leak in executor_test
- kunit: Fix possible memory leak in kunit_filter_suites()
- kunit: Fix the wrong kfree of copy for kunit_filter_suites()
- kunit: Fix missed memory release in kunit_free_suite_set()
- soc: qcom: llcc: Handle a second device without data corruption
- ARM: dts: qcom: mdm9615: populate vsdcc fixed regulator
- ARM: dts: qcom: apq8026-samsung-matisse-wifi: Fix inverted hall sensor
- arm64: dts: qcom: apq8016-sbc: Add missing ADV7533 regulators
- riscv: dts: allwinner: remove address-cells from intc node
- arm64: dts: qcom: msm8939: Fix iommu local address range
- arm64: dts: qcom: msm8976: Fix ipc bit shifts
- ARM64: dts: marvell: cn9310: Use appropriate label for spi1 pins
- arm64: dts: qcom: sdx75-idp: align RPMh regulator nodes with bindings
- arm64: dts: qcom: sdm845-mtp: fix WiFi configuration
- arm64: dts: qcom: sm8350: fix pinctrl for UART18
- arm64: dts: qcom: sm8150: add ref clock to PCIe PHYs
- arm64: dts: qcom: sc7280: drop incorrect EUD port on SoC side
- arm64: dts: qcom: sdm670: Fix pdc mapping
- arm64: dts: qcom: qrb2210-rb1: Fix regulators
- arm64: dts: qcom: qrb2210-rb1: Swap UART index
- arm64: dts: qcom: sc7280: Add missing LMH interrupts
- arm64: dts: qcom: sm6125: Pad APPS IOMMU address to 8 characters
- arm64: dts: qcom: msm8992-libra: drop duplicated reserved memory
- arm64: dts: qcom: msm8916: Fix iommu local address range
- arm64: dts: qcom: sc7280: link usb3_phy_wrapper_gcc_usb30_pipe_clk
- arm64: dts: qcom: sdm845: cheza doesn't support LMh node
- arm64: dts: qcom: sdm845: Fix PSCI power domain names
- ARM: dts: renesas: blanche: Fix typo in GP_11_2 pin name
- perf: hisi: Fix use-after-free when register pmu fails
- drivers/perf: hisi_pcie: Check the type first in pmu::event_init()
- perf/arm-cmn: Fix DTC domain detection
- drm/amd/pm: Fix a memory leak on an error path
- drivers/perf: hisi: use cpuhp_state_remove_instance_nocalls() for hisi_hns3_pmu uninit process
- drm: mediatek: mtk_dsi: Fix NO_EOT_PACKET settings/handling
- clocksource/drivers/arm_arch_timer: limit XGene-1 workaround
- drm/msm/dsi: free TX buffer in unbind
- drm/msm/dsi: use msm_gem_kernel_put to free TX buffer
- xen-pciback: Consider INTx disabled when MSI/MSI-X is enabled
- xen: irqfd: Use _IOW instead of the internal _IOC() macro
- xen: Make struct privcmd_irqfd's layout architecture independent
- xenbus: fix error exit in xenbus_init()
- drm/rockchip: Fix type promotion bug in rockchip_gem_iommu_map()
- arm64/arm: xen: enlighten: Fix KPTI checks
- drm/bridge: lt9611uxc: fix the race in the error path
- gpu: host1x: Correct allocated size for contexts
- drm/rockchip: cdn-dp: Fix some error handling paths in cdn_dp_probe()
- drm/msm/a6xx: Fix unknown speedbin case
- drm/msm/adreno: Fix SM6375 GPU ID
- accel/habanalabs/gaudi2: Fix incorrect string length computation in gaudi2_psoc_razwi_get_engines()
- drm/mediatek: Fix iommu fault during crtc enabling
- drm/mediatek: Fix iommu fault by swapping FBs after updating plane state
- drm/mediatek: Add mmsys_dev_num to mt8188 vdosys0 driver data
- io_uring/kbuf: Allow the full buffer id space for provided buffers
- io_uring/kbuf: Fix check of BID wrapping in provided buffers
- drm/amd/display: Bail from dm_check_crtc_cursor if no relevant change
- drm/amd/display: Refactor dm_get_plane_scale helper
- drm/amd/display: Check all enabled planes in dm_check_crtc_cursor
- drm/amd/display: Fix null pointer dereference in error message
- drm/amdkfd: Handle errors from svm validate and map
- drm/amdkfd: Remove svm range validated_once flag
- drm/amdkfd: fix some race conditions in vram buffer alloc/free of svm code
- drm/amdgpu: Increase IH soft ring size for GFX v9.4.3 dGPU
- drm: Call drm_atomic_helper_shutdown() at shutdown/remove time for misc drivers
- drm/bridge: tc358768: Fix tc358768_ns_to_cnt()
- drm/bridge: tc358768: Clean up clock period code
- drm/bridge: tc358768: Rename dsibclk to hsbyteclk
- drm/bridge: tc358768: Use dev for dbg prints, not priv->dev
- drm/bridge: tc358768: Print logical values, not raw register values
- drm/bridge: tc358768: Use struct videomode
- drm/bridge: tc358768: Fix bit updates
- drm/bridge: tc358768: Fix use of uninitialized variable
- x86/tdx: Zero out the missing RSI in TDX_HYPERCALL macro
- drm/mediatek: Fix coverity issue with unintentional integer overflow
- drm/ssd130x: Fix screen clearing
- drm/bridge: lt8912b: Add missing drm_bridge_attach call
- drm/bridge: lt8912b: Manually disable HPD only if it was enabled
- drm/bridge: lt8912b: Fix crash on bridge detach
- drm/bridge: lt8912b: Fix bridge_detach
- drm: bridge: it66121: Fix invalid connector dereference
- drm/radeon: Remove the references of radeon_gem_ pread & pwrite ioctls
- drm/radeon: possible buffer overflow
- drm/rockchip: vop2: Add missing call to crtc reset helper
- drm/rockchip: vop2: Don't crash for invalid duplicate_state
- drm/rockchip: vop: Fix call to crtc reset helper
- drm/rockchip: vop: Fix reset of state in duplicate state crtc funcs
- drm/loongson: Fix error handling in lsdc_pixel_pll_setup()
- drm: bridge: samsung-dsim: Fix waiting for empty cmd transfer FIFO on older Exynos
- drm: bridge: for GENERIC_PHY_MIPI_DPHY also select GENERIC_PHY
- drm: bridge: samsung-dsim: Initialize ULPS EXIT for i.MX8M DSIM
- spi: omap2-mcspi: Fix hardcoded reference clock
- spi: omap2-mcspi: switch to use modern name
- platform/chrome: cros_ec_lpc: Separate host command and irq disable
- hte: tegra: Fix missing error code in tegra_hte_test_probe()
- hwmon: (sch5627) Disallow write access if virtual registers are locked
- hwmon: (sch5627) Use bit macros when accessing the control register
- hwmon: (pmbus/mp2975) Move PGOOD fix
- Revert "hwmon: (sch56xx-common) Add automatic module loading on supported devices"
- Revert "hwmon: (sch56xx-common) Add DMI override table"
- hwmon: (coretemp) Fix potentially truncated sysfs attribute name
- hwmon: (axi-fan-control) Fix possible NULL pointer dereference
- regulator: qcom-rpmh: Fix smps4 regulator for pm8550ve
- platform/x86: wmi: Fix opening of char device
- platform/x86: wmi: Fix probe failure when failing to register WMI devices
- clk: mediatek: fix double free in mtk_clk_register_pllfh()
- clk: qcom: ipq5332: drop the CLK_SET_RATE_PARENT flag from GPLL clocks
- clk: qcom: ipq9574: drop the CLK_SET_RATE_PARENT flag from GPLL clocks
- clk: qcom: ipq5018: drop the CLK_SET_RATE_PARENT flag from GPLL clocks
- clk: qcom: apss-ipq-pll: Fix 'l' value for ipq5332_pll_config
- clk: qcom: apss-ipq-pll: Use stromer plus ops for stromer plus pll
- clk: qcom: clk-alpha-pll: introduce stromer plus ops
- clk: qcom: config IPQ_APSS_6018 should depend on QCOM_SMEM
- clk: mediatek: clk-mt2701: Add check for mtk_alloc_clk_data
- clk: mediatek: clk-mt7629: Add check for mtk_alloc_clk_data
- clk: mediatek: clk-mt7629-eth: Add check for mtk_alloc_clk_data
- clk: mediatek: clk-mt6797: Add check for mtk_alloc_clk_data
- clk: mediatek: clk-mt6779: Add check for mtk_alloc_clk_data
- clk: mediatek: clk-mt6765: Add check for mtk_alloc_clk_data
- clk: npcm7xx: Fix incorrect kfree
- clk: ti: fix double free in of_ti_divider_clk_setup()
- clk: keystone: pll: fix a couple NULL vs IS_ERR() checks
- clk: ralink: mtmips: quiet unused variable warning
- spi: nxp-fspi: use the correct ioremap function
- clk: linux/clk-provider.h: fix kernel-doc warnings and typos
- clk: renesas: rzg2l: Fix computation formula
- clk: renesas: rzg2l: Use FIELD_GET() for PLL register fields
- clk: renesas: rzg2l: Trust value returned by hardware
- clk: renesas: rzg2l: Lock around writes to mux register
- clk: renesas: rzg2l: Wait for status bit of SD mux before continuing
- clk: renesas: rcar-gen3: Extend SDnH divider table
- clk: imx: imx8qxp: Fix elcdif_pll clock
- clk: imx: imx8mq: correct error handling path
- clk: imx: imx8: Fix an error handling path in imx8_acm_clk_probe()
- clk: imx: imx8: Fix an error handling path if devm_clk_hw_register_mux_parent_data_table() fails
- clk: imx: imx8: Fix an error handling path in clk_imx_acm_attach_pm_domains()
- clk: imx: Select MXC_CLK for CLK_IMX8QXP
- regulator: mt6358: Fail probe on unknown chip ID
- gpio: sim: initialize a managed pointer when declaring it
- clk: qcom: gcc-sm8150: Fix gcc_sdcc2_apps_clk_src
- clk: qcom: mmcc-msm8998: Fix the SMMU GDSC
- clk: qcom: mmcc-msm8998: Don't check halt bit on some branch clks
- clk: qcom: clk-rcg2: Fix clock rate overflow for high parent frequencies
- clk: qcom: gcc-msm8996: Remove RPM bus clocks
- clk: qcom: ipq5332: Drop set rate parent from gpll0 dependent clocks
- spi: tegra: Fix missing IRQ check in tegra_slink_probe()
- regmap: debugfs: Fix a erroneous check after snprintf()
- ipvlan: properly track tx_errors
- net: add DEV_STATS_READ() helper
- virtio_net: use u64_stats_t infra to avoid data-races
- ipv6: avoid atomic fragment on GSO packets
- mptcp: properly account fastopen data
- ACPI: sysfs: Fix create_pnp_modalias() and create_of_modalias()
- bpf: Fix unnecessary -EBUSY from htab_lock_bucket
- Bluetooth: hci_sync: Fix Opcode prints in bt_dev_dbg/err
- Bluetooth: Make handle of hci_conn be unique
- Bluetooth: ISO: Pass BIG encryption info through QoS
- wifi: iwlwifi: empty overflow queue during flush
- wifi: iwlwifi: mvm: update IGTK in mvmvif upon D3 resume
- wifi: iwlwifi: pcie: synchronize IRQs before NAPI
- wifi: iwlwifi: mvm: fix netif csum flags
- wifi: iwlwifi: increase number of RX buffers for EHT devices
- wifi: iwlwifi: mvm: remove TDLS stations from FW
- wifi: iwlwifi: mvm: fix iwl_mvm_mac_flush_sta()
- wifi: iwlwifi: mvm: change iwl_mvm_flush_sta() API
- wifi: iwlwifi: mvm: Don't always bind/link the P2P Device interface
- wifi: iwlwifi: mvm: Fix key flags for IGTK on AP interface
- wifi: iwlwifi: mvm: Correctly set link configuration
- wifi: iwlwifi: yoyo: swap cdb and jacket bits values
- wifi: mac80211: Fix setting vif links
- wifi: mac80211: don't recreate driver link debugfs in reconfig
- wifi: iwlwifi: mvm: use correct sta ID for IGTK/BIGTK
- wifi: iwlwifi: mvm: fix removing pasn station for responder
- wifi: iwlwifi: mvm: update station's MFP flag after association
- tcp: fix cookie_init_timestamp() overflows
- chtls: fix tp->rcv_tstamp initialization
- thermal: core: Don't update trip points inside the hysteresis range
- selftests/bpf: Make linked_list failure test more robust
- net: skb_find_text: Ignore patterns extending past 'to'
- bpf: Fix missed rcu read lock in bpf_task_under_cgroup()
- thermal/drivers/mediatek: Fix probe for THERMAL_V2
- r8169: fix rare issue with broken rx after link-down on RTL8125
- thermal: core: prevent potential string overflow
- wifi: rtw88: Remove duplicate NULL check before calling usb_kill/free_urb()
- virtio-net: fix the vq coalescing setting for vq resize
- virtio-net: fix per queue coalescing parameter setting
- virtio-net: consistently save parameters for per-queue
- virtio-net: fix mismatch of getting tx-frames
- netfilter: nf_tables: Drop pointless memset when dumping rules
- wifi: wfx: fix case where rates are out of order
- PM / devfreq: rockchip-dfi: Make pmu regmap mandatory
- can: dev: can_put_echo_skb(): don't crash kernel if can_priv::echo_skb is accessed out of bounds
- can: dev: can_restart(): fix race condition between controller restart and netif_carrier_on()
- can: dev: can_restart(): don't crash kernel if carrier is OK
- wifi: ath11k: fix Tx power value during active CAC
- r8152: break the loop when the budget is exhausted
- selftests/bpf: Define SYS_NANOSLEEP_KPROBE_NAME for riscv
- selftests/bpf: Define SYS_PREFIX for riscv
- libbpf: Fix syscall access arguments on riscv
- can: etas_es58x: add missing a blank line after declaration
- can: etas_es58x: rework the version check logic to silence -Wformat-truncation
- ACPI: video: Add acpi_backlight=vendor quirk for Toshiba Portégé R100
- ACPI: property: Allow _DSD buffer data only for byte accessors
- wifi: rtlwifi: fix EDCA limit set by BT coexistence
- tcp_metrics: do not create an entry from tcp_init_metrics()
- tcp_metrics: properly set tp->snd_ssthresh in tcp_init_metrics()
- tcp_metrics: add missing barriers on delete
- wifi: ath: dfs_pattern_detector: Fix a memory initialization issue
- wifi: mt76: mt7921: fix the wrong rate selected in fw for the chanctx driver
- wifi: mt76: mt7921: fix the wrong rate pickup for the chanctx driver
- wifi: mt76: move struct ieee80211_chanctx_conf up to struct mt76_vif
- wifi: mt76: mt7915: fix beamforming availability check
- wifi: mt76: fix per-band IEEE80211_CONF_MONITOR flag comparison
- wifi: mt76: get rid of false alamrs of tx emission issues
- wifi: mt76: fix potential memory leak of beacon commands
- wifi: mt76: update beacon size limitation
- wifi: mt76: mt7996: fix TWT command format
- wifi: mt76: mt7996: fix rx rate report for CBW320-2
- wifi: mt76: mt7996: fix wmm queue mapping
- wifi: mt76: mt7996: fix beamformee ss subfield in EHT PHY cap
- wifi: mt76: mt7996: fix beamform mcu cmd configuration
- wifi: mt76: mt7996: set correct wcid in txp
- wifi: mt76: remove unused error path in mt76_connac_tx_complete_skb
- wifi: mt76: mt7603: improve stuck beacon handling
- wifi: mt76: mt7603: improve watchdog reset reliablity
- wifi: mt76: mt7603: rework/fix rx pse hang check
- cpufreq: tegra194: fix warning due to missing opp_put
- PM: sleep: Fix symbol export for _SIMPLE_ variants of _PM_OPS()
- wifi: mac80211: fix check for unusable RX result
- wifi: ath11k: fix boot failure with one MSI vector
- wifi: ath12k: fix DMA unmap warning on NULL DMA address
- wifi: rtw88: debug: Fix the NULL vs IS_ERR() bug for debugfs_create_file()
- net: ethernet: mtk_wed: fix EXT_INT_STATUS_RX_FBUF definitions for MT7986 SoC
- ice: fix pin assignment for E810-T without SMA control
- net: spider_net: Use size_add() in call to struct_size()
- tipc: Use size_add() in calls to struct_size()
- tls: Use size_add() in call to struct_size()
- mlxsw: Use size_mul() in call to struct_size()
- gve: Use size_add() in call to struct_size()
- bpf: Fix kfunc callback register type handling
- tcp: call tcp_try_undo_recovery when an RTOd TFO SYNACK is ACKed
- selftests/bpf: Skip module_fentry_shadow test when bpf_testmod is not available
- udplite: fix various data-races
- udplite: remove UDPLITE_BIT
- udp: annotate data-races around udp->encap_type
- udp: lockless UDP_ENCAP_L2TPINUDP / UDP_GRO
- udp: move udp->accept_udp_{l4|fraglist} to udp->udp_flags
- udp: add missing WRITE_ONCE() around up->encap_rcv
- udp: move udp->gro_enabled to udp->udp_flags
- udp: move udp->no_check6_rx to udp->udp_flags
- udp: move udp->no_check6_tx to udp->udp_flags
- udp: introduce udp->udp_flags
- wifi: cfg80211: fix kernel-doc for wiphy_delayed_work_flush()
- bpf, x64: Fix tailcall infinite loop
- selftests/bpf: Correct map_fd to data_fd in tailcalls
- iavf: Fix promiscuous mode configuration flow messages
- i40e: fix potential memory leaks in i40e_remove()
- wifi: iwlwifi: don't use an uninitialized variable
- wifi: iwlwifi: honor the enable_ini value
- wifi: mac80211: fix # of MSDU in A-MSDU calculation
- wifi: cfg80211: fix off-by-one in element defrag
- wifi: mac80211: fix RCU usage warning in mesh fast-xmit
- wifi: mac80211: move sched-scan stop work to wiphy work
- wifi: mac80211: move offchannel works to wiphy work
- wifi: mac80211: move scan work to wiphy work
- wifi: mac80211: move radar detect work to wiphy work
- wifi: cfg80211: add flush functions for wiphy work
- wifi: ath12k: fix undefined behavior with __fls in dp
- irqchip/sifive-plic: Fix syscore registration for multi-socket systems
- genirq/matrix: Exclude managed interrupts in irq_matrix_allocated()
- string: Adjust strtomem() logic to allow for smaller sources
- PCI/MSI: Provide stubs for IMS functions
- selftests/x86/lam: Zero out buffer for readlink()
- perf: Optimize perf_cgroup_switch()
- pstore/platform: Add check for kstrdup
- x86/nmi: Fix out-of-order NMI nesting checks & false positive warning
- drivers/clocksource/timer-ti-dm: Don't call clk_get_rate() in stop function
- srcu: Fix callbacks acceleration mishandling
- x86/apic: Fake primary thread mask for XEN/PV
- cpu/SMT: Make SMT control more robust against enumeration failures
- x86/boot: Fix incorrect startup_gdt_descr.size
- x86/sev-es: Allow copy_from_kernel_nofault() in earlier boot
- cgroup/cpuset: Fix load balance state in update_partition_sd_lb()
- ACPI/NUMA: Apply SRAT proximity domain to entire CFMWS window
- x86/numa: Introduce numa_fill_memblks()
- futex: Don't include process MM in futex key on no-MMU
- x86/srso: Fix unret validation dependencies
- x86/srso: Fix vulnerability reporting for missing microcode
- x86/srso: Print mitigation for retbleed IBPB case
- x86/srso: Fix SBPB enablement for (possible) future fixed HW
- writeback, cgroup: switch inodes with dirty timestamps to release dying cgwbs
- vfs: fix readahead(2) on block devices
- nfsd: Handle EOPENSTALE correctly in the filecache
- sched: Fix stop_one_cpu_nowait() vs hotplug
- objtool: Propagate early errors
- sched/uclamp: Ignore (util == 0) optimization in feec() when p_util_max = 0
- sched/uclamp: Set max_spare_cap_cpu even if max_spare_cap is 0
- iov_iter, x86: Be consistent about the __user tag on copy_mc_to_user()
- sched/fair: Fix cfs_rq_is_decayed() on !SMP
- sched/topology: Fix sched_numa_find_nth_cpu() in non-NUMA case
- sched/topology: Fix sched_numa_find_nth_cpu() in CPU-less case
- numa: Generalize numa_map_to_online_node()
- hwmon: (nct6775) Fix incorrect variable reuse in fan_div calculation
- !2933 Backport linux 6.6.1 LTS patches
- ASoC: SOF: sof-pci-dev: Fix community key quirk detection
- ALSA: hda: intel-dsp-config: Fix JSL Chromebook quirk detection
- serial: core: Fix runtime PM handling for pending tx
- misc: pci_endpoint_test: Add deviceID for J721S2 PCIe EP device support
- dt-bindings: serial: rs485: Add rs485-rts-active-high
- tty: 8250: Add Brainboxes Oxford Semiconductor-based quirks
- tty: 8250: Add support for Intashield IX cards
- tty: 8250: Add support for additional Brainboxes PX cards
- tty: 8250: Fix up PX-803/PX-857
- tty: 8250: Fix port count of PX-257
- tty: 8250: Add support for Intashield IS-100
- tty: 8250: Add support for Brainboxes UP cards
- tty: 8250: Add support for additional Brainboxes UC cards
- tty: 8250: Remove UC-257 and UC-431
- tty: n_gsm: fix race condition in status line change on dead connections
- Bluetooth: hci_bcm4377: Mark bcm4378/bcm4387 as BROKEN_LE_CODED
- usb: raw-gadget: properly handle interrupted requests
- usb: typec: tcpm: Fix NULL pointer dereference in tcpm_pd_svdm()
- usb: typec: tcpm: Add additional checks for contaminant
- usb: storage: set 1.50 as the lower bcdDevice for older "Super Top" compatibility
- PCI: Prevent xHCI driver from claiming AMD VanGogh USB3 DRD device
- ALSA: usb-audio: add quirk flag to enable native DSD for McIntosh devices
- eventfs: Use simple_recursive_removal() to clean up dentries
- eventfs: Delete eventfs_inode when the last dentry is freed
- eventfs: Save ownership and mode
- eventfs: Remove "is_freed" union with rcu head
- tracing: Have trace_event_file have ref counters
- perf evlist: Avoid frequency mode for the dummy event
- power: supply: core: Use blocking_notifier_call_chain to avoid RCU complaint
- drm/amd/display: Don't use fsleep for PSR exit waits
- !2927 dm ioctl: add DMINFO() to track dm device create/remove
- dm ioctl: add DMINFO() to track dm device create/remove
- !2900 Add initial openeuler_defconfig for arm64 and x86
- config: add initial openeuler_defconfig for x86
- config: add initial openeuler_defconfig for arm64
- kconfig: Add script to check & update openeuler_defconfig
- init from linux v6.6
