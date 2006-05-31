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
%define		snap_month	05
%define		snap_day	28
%define		snap	%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		_rel	0.%{snap}.1
%define		trunk	r1611
Summary:	Atheros WiFi card driver
Summary(pl):	Sterownik karty radiowej Atheros
Name:		madwifi-ng
Version:	0
Release:	%{_rel}
Epoch:		0
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Provides:	madwifi
Obsoletes:	madwifi
Source0:	http://snapshots.madwifi.org/madwifi-ng/%{name}-%{trunk}-%{snap}.tar.gz
# Source0-md5:	41e3c103a61e2cc3009ef3f3c6d4c94d
#Patch0:		%{name}-bashizm.patch
URL:		http://www.madwifi.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sharutils
%endif
ExclusiveArch:	%{x8664} arm %{ix86} mips ppc xscale
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
#%patch0 -p1

%build
%if %{with userspace}
%{__make} -C tools \
	CC="%{__cc}" \
	CFLAGS="-include include/compat.h -\$(INCS) %{rpmcflags}" \
	KERNELCONF="%{_kernelsrcdir}/config-up"
%endif

%if %{with kernel}
# kernel module(s)
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

#
#	patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	ln -sf ../Makefile.inc o/Makefile.inc
	%{__make} -C %{_kernelsrcdir} clean \
		TARGET="%{_target_base_arch}-elf" \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o \
		KERNELPATH="%{_kernelsrcdir}" \
		%{?with_verbose:V=1}
	%{__make} \
		TARGET="%{_target_base_arch}-elf" \
		KERNELPATH="%{_kernelsrcdir}" \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		TOOLPREFIX= \
		O=$PWD/o \
		CC="%{__cc}" CPP="%{__cpp}" \
		%{?with_verbose:V=1}

	mv ath/ath_pci{,-$cfg}.ko
	mv ath/ath_hal{,-$cfg}.ko
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
install ath/ath_hal-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
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
install ath/ath_hal-smp.ko \
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
