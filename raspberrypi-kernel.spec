%global Arch $(echo %{_host_cpu} | sed -e s/i.86/x86/ -e s/x86_64/x86/ -e s/aarch64.*/arm64/)

%global KernelVer %{version}-%{release}.raspi.%{_target_cpu}

%global hulkrelease 102.0.0

%global debug_package %{nil}

Name:	 raspberrypi-kernel
Version: 6.6.0
Release: %{hulkrelease}.1
Summary: Linux Kernel
License: GPLv2
URL:	 http://www.kernel.org/
Source0: kernel.tar.gz
Patch0000: 0000-raspberrypi-kernel.patch

BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl-devel
BuildRequires: hmaccalc
BuildRequires: ncurses-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: rpm >= 4.14.2
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison
BuildRequires: audit-libs-devel
BuildRequires: pciutils-devel gettext
BuildRequires: rpm-build, elfutils
BuildRequires: numactl-devel python3-devel glibc-static python3-docutils
BuildRequires: perl-generators perl(Carp) libunwind-devel gtk2-devel libbabeltrace-devel java-1.8.0-openjdk
AutoReq: no
AutoProv: yes

Provides: raspberrypi-kernel-aarch64 = %{version}-%{release}

ExclusiveArch: aarch64
ExclusiveOS: Linux

%description
The Linux Kernel image for RaspberryPi.

%package devel
Summary: Development package for building kernel modules to match the %{KernelVer} raspberrypi-kernel
AutoReqProv: no
Provides: raspberrypi-kernel-devel-uname-r = %{KernelVer}
Provides: raspberrypi-kernel-devel-%{_target_cpu} = %{version}-%{release}
Requires: perl findutils

%description devel
This package provides raspberrypi kernel headers and makefiles sufficient to build modules
against the %{KernelVer} raspberrypi-kernel package.

%prep
%setup -q -n kernel-%{version} -c
mv kernel linux-%{version}
cp -a linux-%{version} linux-%{KernelVer}

cd linux-%{KernelVer}
%patch0000 -p1

find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null
find . -name .gitignore -exec rm -f {} \; >/dev/null

%build
cd linux-%{KernelVer}

perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.raspi.%{_target_cpu}/" Makefile

make ARCH=%{Arch} %{?_smp_mflags} O=output/v8 bcm2711_defconfig

make ARCH=%{Arch} %{?_smp_mflags} O=output/v8 KERNELRELEASE=%{KernelVer}-v8

make ARCH=%{Arch} %{?_smp_mflags} O=output/2712 bcm2712_defconfig

make ARCH=%{Arch} %{?_smp_mflags} O=output/2712 KERNELRELEASE=%{KernelVer}-2712

%install
cd linux-%{KernelVer}

## install linux
mkdir -p $RPM_BUILD_ROOT/boot
rpi_version=("v8" "2712")
for rpi in "${rpi_version[@]}"; do
    pushd output/$rpi
    kernel_ver=%{KernelVer}-$rpi
    TargetImage=$(make -s image_name)
    make ARCH=%{Arch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$kernel_ver
    install -m 755 $TargetImage $RPM_BUILD_ROOT/boot/vmlinuz-$kernel_ver
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$kernel_ver
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$kernel_ver

    rm -rf $RPM_BUILD_ROOT/lib/modules/$kernel_ver/source $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build

    ############ to do collect devel file  #########
    # 1. Makefile And Kconfig, .config sysmbol
    # 2. scrpits dir
    # 3. .h file
    find -type f \( -name "Makefile*" -o -name "Kconfig*" \) -exec cp --parents {} $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build \;
    for f in Module.symvers System.map Module.markers .config;do
        test -f $f || continue
        cp $f $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build
    done

    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build
    if [ -d arch/%{Arch}/scripts ]; then
        cp -a arch/%{Arch}/scripts $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{Arch}/*lds ]; then
        cp -a arch/%{Arch}/*lds $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/arch/%{_arch}/ || :
    fi
    find $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/scripts/ -name "*.o" -exec rm -rf {} \;

    if [ -d arch/%{Arch}/include ]; then
        cp -a --parents arch/%{Arch}/include $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/include

    if [ -f arch/%{Arch}/kernel/module.lds ]; then
        cp -a --parents arch/%{Arch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/
    fi

    # module.lds is moved to scripts by commit 596b0474d3d9 in linux 5.10.
    if [ -f scripts/module.lds ]; then
        cp -a --parents scripts/module.lds $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/
    fi

    # copy objtool for raspberrypi-kernel-devel (needed for building external modules)
    if grep -q CONFIG_STACK_VALIDATION=y .config; then
        mkdir -p $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/tools/objtool
        cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/tools/objtool
    fi

    popd

    %ifarch aarch64
        cp -a --parents arch/arm/include/asm $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/
    %endif

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/Makefile $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/.config $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/include/generated/autoconf.h
    # for make prepare
    if [ ! -f $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/include/config/auto.conf ];then
        cp .config $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build/include/config/auto.conf
    fi

    mkdir -p %{buildroot}/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$kernel_ver/build $RPM_BUILD_ROOT/usr/src/kernels/$kernel_ver

    find $RPM_BUILD_ROOT/usr/src/kernels/$kernel_ver -name ".*.cmd" -exec rm -f {} \;

    pushd $RPM_BUILD_ROOT/lib/modules/$kernel_ver
    ln -sf /usr/src/kernels/$kernel_ver build
    ln -sf build source
    popd
done

pushd output/2712
mkdir -p $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/overlays
install -m 644 $(find arch/%{Arch}/boot/dts/broadcom/ -name "*.dtb") $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/
install -m 644 $(find arch/%{Arch}/boot/dts/overlays/ -name "*.dtbo") $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/overlays/
if ls arch/%{Arch}/boot/dts/overlays/*.dtb > /dev/null 2>&1; then
    install -m 644 $(find arch/%{Arch}/boot/dts/overlays/ -name "*.dtb") $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/overlays/
fi
install -m 644 ../../arch/%{Arch}/boot/dts/overlays/README $RPM_BUILD_ROOT/boot/dtb-%{KernelVer}/overlays/
popd

%postun
version_old=0
if [ "$1" == "0" ]; then
    echo "warning: something may go wrong when starting this device next time after uninstalling raspberrypi-kernel."
else
    version_tmp=0
    name_len=`echo -n %{name}-|wc -c`
    for item in `rpm -qa %{name} 2>/dev/null`
    do
        cur_version=${item:name_len}
        cpu_version=${cur_version##*.}
        if [ "$cpu_version" == "%{_target_cpu}" ]; then
            cur_version=${cur_version%.*}
            cur_version=$cur_version.raspi.$cpu_version
            if [[ "$cur_version" != "%{KernelVer}" && "$cur_version" > "$version_tmp" ]]; then
                version_tmp=$cur_version
            fi
        fi
    done
    if [[ "$version_tmp" < "%{KernelVer}" ]]; then
        version_old=$version_tmp
    fi
fi
if [ "$version_old" != "0" ]; then
    if [ -f /boot/vmlinuz-$version_old-v8 ] && [ -d /boot/dtb-$version_old ] && [ -d /lib/modules/$version_old-v8 ] && [ -f /boot/vmlinuz-$version_old-2712 ] && [ -d /lib/modules/$version_old-2712 ]; then
        ls /boot/dtb-$version_old/overlays/*.dtbo > /dev/null 2>&1
        if [ "$?" == "0" ]; then
            ls /boot/dtb-$version_old/*.dtb > /dev/null 2>&1
            if [ "$?" == "0" ]; then
                rm -rf /boot/*.dtb /boot/overlays /boot/kernel8.img /boot/kernel_2712.img
                mkdir /boot/overlays
                install -m 755 /boot/vmlinuz-$version_old-v8 /boot/kernel8.img
                install -m 755 /boot/vmlinuz-$version_old-2712 /boot/kernel_2712.img
                for file in `ls /boot/dtb-$version_old/*.dtb 2>/dev/null`
                do
                    if [ -f $file ]; then
                        install -m 644 $file /boot/`basename $file`
                    fi
                done
                install -m 644 $(find /boot/dtb-$version_old/overlays/ -name "*.dtbo") /boot/overlays/
                if ls /boot/dtb-$version_old/overlays/*.dtb > /dev/null 2>&1; then
                    install -m 644 $(find /boot/dtb-$version_old/overlays/ -name "*.dtb") /boot/overlays/
                fi
                install -m 644 /boot/dtb-$version_old/overlays/README /boot/overlays/
            else
                echo "warning: files in /boot/dtb-$version_old/*.dtb missing when resetting raspberrypi-kernel as $version_old, something may go wrong when starting this device next time."
            fi
        else
            echo "warning: files in /boot/dtb-$version_old/overlays missing when resetting raspberrypi-kernel as $version_old, something may go wrong when starting this device next time."
        fi
    else
        echo "warning: files missing when resetting raspberrypi-kernel as $version_old, something may go wrong when starting this device next time."
    fi
fi

%posttrans
rm -rf /boot/*.dtb /boot/overlays /boot/kernel8.img /boot/kernel_2712.img
mkdir -p /boot/overlays
install -m 755 /boot/vmlinuz-%{KernelVer}-v8 /boot/kernel8.img
install -m 755 /boot/vmlinuz-%{KernelVer}-2712 /boot/kernel_2712.img
for file in `ls /boot/dtb-%{KernelVer}/*.dtb 2>/dev/null`
do
    if [ -f $file ]; then
        install -m 644 $file /boot/`basename $file`
    fi
done
install -m 644 $(find /boot/dtb-%{KernelVer}/overlays/ -name "*.dtbo") /boot/overlays/
if ls /boot/dtb-%{KernelVer}/overlays/*.dtb > /dev/null 2>&1; then
    install -m 644 $(find /boot/dtb-%{KernelVer}/overlays/ -name "*.dtb") /boot/overlays/
fi
install -m 644 /boot/dtb-%{KernelVer}/overlays/README /boot/overlays/

%post devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]
then
    (pushd /usr/src/kernels/%{KernelVer}-v8 &&
     /usr/bin/find . -type f | while read f; do
       hardlink -c /usr/src/kernels/*.oe*.*/$f $f
     done &&
     popd &&
     pushd /usr/src/kernels/%{KernelVer}-2712 &&
     /usr/bin/find . -type f | while read f; do
       hardlink -c /usr/src/kernels/*.oe*.*/$f $f
     done &&
     popd)
fi

%files
%defattr (-, root, root)
%doc
/boot/config-*
/boot/System.map-*
/boot/vmlinuz-*
/boot/dtb-*
/lib/modules/%{KernelVer}-v8
/lib/modules/%{KernelVer}-2712

%files devel
%defattr (-, root, root)
%doc
/lib/modules/%{KernelVer}-v8/source
/lib/modules/%{KernelVer}-v8/build
/lib/modules/%{KernelVer}-2712/source
/lib/modules/%{KernelVer}-2712/build
/usr/src/kernels/%{KernelVer}-*

%changelog
* Wed Aug 13 2025 Yafen Fang <yafen@iscas.ac.cn> - 6.6.0-102.0.0.1
- update kernel version to openEuler 6.6.0-102.0.0
- update Raspberry Pi patch, last commit (bba53a117a4a5c29da892962332ff1605990e17a): dts: rp1: Don't use DMA with UARTs
