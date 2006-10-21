#
# TODO: kernel header is additional BR  (whatever it means???)
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		snap_year	2006
%define		snap_month	10
%define		snap_day	20
%define		snap	%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		_rel	0.%{snap}.5
%define		trunk	r1757
Summary:	Atheros WiFi card driver
Summary(pl):	Sterownik karty radiowej Atheros
Name:		madwifi-ng
Version:	0
Release:	%{_rel}
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Provides:	madwifi
Obsoletes:	madwifi
# http://snapshots.madwifi.org/madwifi-ng/madwifi-ng-r1757-20061020.tar.gz
Source0:	http://snapshots.madwifi.org/madwifi-ng/%{name}-%{trunk}-%{snap}.tar.gz
# Source0-md5:	862f8e61cf9d3f4b429ac9ffca21f8e1
# http://patches.aircrack-ng.org/madwifi-ng-r1730.patch
Patch0:		%{name}-r1730.patch
Patch1:		%{name}-gcc4.patch
# http://madwifi.org/ticket/617
Patch2:		%{name}-ticket-617.patch
# http://madwifi.org/ticket/967
Patch3:		%{name}-011-suppress_plaintext.patch
# http://madwifi.org/ticket/963
Patch4:		%{name}-009-csa_ie_handling_fix.patch
# http://madwifi.org/ticket/858
Patch5:		%{name}-010-true_radiotap_parser.patch
# http://madwifi.org/ticket/946
Patch6:		%{name}-ieee80211_wireless.c.patch
URL:		http://www.madwifi.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sharutils
%endif
ExclusiveArch:	alpha arm %{ix86} %{x8664} mips powerpc ppc sparc sparcv9 sparc64 xscale
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Atheros WiFi card driver. Support Virtual APs and WDS Mode.

%description -l pl
Sterownik karty radiowej Atheros. Wspiera tryb wirtualnego AP oraz
tryb WDS.

%package devel
Summary:	Header files for madwifi
Summary(pl):	Pliki nag³ówkowe dla madwifi
Group:		Development/Libraries
Provides:	madwifi-devel
Obsoletes:	madwifi-devel

%description devel
Header files for madwifi.

%description devel -l pl
Pliki nag³ówkowe dla madwifi.

# kernel subpackages.

%package -n kernel-net-madwifi
Summary:	Linux driver for Atheros cards
Summary(pl):	Sterownik dla Linuksa do kart Atheros
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-net-madwifi
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel-net-madwifi -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-madwifi
Summary:	Linux SMP driver for %{name} cards
Summary(pl):	Sterownik dla Linuksa SMP do kart %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-net-madwifi
This is driver for Atheros cards for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-net-madwifi -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{name}-%{trunk}-%{snap}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
%if %{with userspace}
%{__make} -C tools \
	CC="%{__cc}" \
	CFLAGS="-include include/compat.h -\$(INCS) %{rpmcflags}" \
	KERNELCONF="%{_kernelsrcdir}/config-up"
%endif

%if %{with kernel}
# kernel module(s)

%ifarch alpha %{ix86} %{x8664}
target=%{_target_base_arch}-elf
%endif
%ifarch sparc sparcv9 sparc64
target=%{_target_base_arch}-be-elf
%endif
%ifarch powerpc ppc
target=powerpc-be-elf
%endif

for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf o/
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%ifarch ppc ppc64
	install -d include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-powerpc ] || ln -sf %{_kernelsrcdir}/include/asm-powerpc/* include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-%{_target_base_arch} ] || ln -snf %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
%else
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} o/include/asm
%endif

	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	ln -sf ../Makefile.inc o/Makefile.inc
	%{__make} -C %{_kernelsrcdir} clean \
		TARGET=$target \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o \
		KERNELPATH="%{_kernelsrcdir}" \
		%{?with_verbose:V=1}
	%{__make} \
		TARGET=$target \
		KERNELPATH="%{_kernelsrcdir}" \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		TOOLPREFIX= \
		O=$PWD/o \
		CC="%{__cc}" CPP="%{__cpp}" \
		%{?with_verbose:V=1}

	mv ath/ath_pci{,-$cfg}.ko
	mv ath_hal/ath_hal{,-$cfg}.ko
# default is ath_rate_sample now compiles, _onoe does not
	mv ath_rate/sample/ath_rate_sample{,-$cfg}.ko
#	mv ath_rate/onoe/ath_rate_onoe{,-$cfg}.ko

	for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan wlan_scan_ap wlan_scan_sta; do
		mv net80211/$i{,-$cfg}.ko
	done
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install-tools \
	KERNELCONF="%{_kernelsrcdir}/config-up" \
	KERNELPATH="%{_kernelsrcdir}" \
	DESTDIR=$RPM_BUILD_ROOT \
	BINDIR=%{_bindir} \
	MANDIR=%{_mandir}

install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
install net80211/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install include/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include
install include/sys/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/net
install ath/ath_pci-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_pci.ko
install ath_hal/ath_hal-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_hal.ko
install ath_rate/sample/ath_rate_sample-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_rate_sample.ko
#install ath_rate/onoe/ath_rate_onoe-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
#	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_rate_onoe.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan wlan_scan_ap wlan_scan_sta; do
	install net80211/$i-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/$i.ko
done
%if %{with smp} && %{with dist_kernel}
install ath/ath_pci-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_pci.ko
install ath_hal/ath_hal-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_hal.ko
install ath_rate/sample/ath_rate_sample-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_rate_sample.ko
#install ath_rate/onoe/ath_rate_onoe-smp.ko \
#	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_rate_onoe.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan wlan_scan_ap wlan_scan_sta; do
	install net80211/$i-smp.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/$i.ko
done
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-madwifi
%depmod %{_kernel_ver}

%postun	-n kernel-net-madwifi
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-madwifi
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-madwifi
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYRIGHT README docs/WEP-HOWTO.txt docs/users*
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man8/*

%files devel
%defattr(644,root,root,755)
%{_includedir}/madwifi
%endif

%if %{with kernel}
%files -n kernel-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/*.ko*
%endif
%endif
