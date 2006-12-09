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
%define		snap_month	12
%define		snap_day	08
%define		snap	%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		_rel	0.%{snap}.1
%define		trunk	r1844
Summary:	Atheros WiFi card driver
Summary(pl):	Sterownik karty radiowej Atheros
Name:		madwifi-ng
Version:	0
Release:	%{_rel}
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Provides:	madwifi
Obsoletes:	madwifi
# http://snapshots.madwifi.org/madwifi-ng/madwifi-ng-r1844-20061208.tar.gz
Source0:	http://snapshots.madwifi.org/madwifi-ng/%{name}-%{trunk}-%{snap}.tar.gz
# Source0-md5:	9ab58ff1c9b3803f76b064eba3555679
# http://patches.aircrack-ng.org/madwifi-ng-r1816.patch
Patch0:		%{name}-r1816.patch
Patch1:		%{name}-gcc4.patch
# http://madwifi.org/ticket/617
Patch2:		%{name}-ticket-617.patch
# http://madwifi.org/ticket/946
Patch3:		%{name}-ieee80211_wireless.c.patch
URL:		http://www.madwifi.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.333
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

%package -n kernel%{_alt_kernel}-net-madwifi-ng
Summary:	Linux driver for Atheros cards
Summary(pl):	Sterownik dla Linuksa do kart Atheros
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-net-madwifi-ng
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-madwifi-ng -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel%{_alt_kernel}-smp-net-madwifi-ng
Summary:	Linux SMP driver for %{name} cards
Summary(pl):	Sterownik dla Linuksa SMP do kart %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-net-madwifi-ng
This is driver for Atheros cards for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-net-madwifi-ng -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{name}-%{trunk}-%{snap}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

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
%define target %{_target_base_arch}-elf
%endif
%ifarch sparc sparcv9 sparc64
%define target %{_target_base_arch}-be-elf
%endif
%ifarch powerpc ppc
%define target powerpc-be-elf
%endif

# default is ath_rate_sample now compiles, _onoe does not
%define modules_ath ath/ath_pci,ath_hal/ath_hal,ath_rate/sample/ath_rate_sample
%define modules_wlan net80211/wlan,net80211/wlan_{wep,xauth,acl,ccmp,tkip,scan_{ap,sta}}
%define modules %{modules_ath},%{modules_wlan}

%define opts TARGET=%{target} KERNELPATH="%{_kernelsrcdir}" KERNELCONF="$PWD/o/.config" TOOLPREFIX=

make svnversion.h
%build_kernel_modules -c -m %{modules} %{opts} <<'EOF'
find -name "*.o" | xargs -r rm
ln -sf ../Makefile.inc o/Makefile.inc
EOF

%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install-tools \
	TARGET=%{target} \
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
%install_kernel_modules -m %{modules} -d kernel/net
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-madwifi-ng
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-madwifi-ng
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-net-madwifi-ng
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-net-madwifi-ng
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
%files -n kernel%{_alt_kernel}-net-madwifi-ng
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-madwifi-ng
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/*.ko*
%endif
%endif
