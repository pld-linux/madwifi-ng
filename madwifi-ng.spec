#
# TODO:
# - kernel header is additional BR  (whatever it means???)
# - broken build without kernel
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	force_userspace	# force userspace build (useful if alt_kernel is set)
%bcond_with	verbose		# verbose build (V=1)
#
%define		snap_year	2012
%define		snap_month	01
%define		snap_day	31
%define		snap		%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		prel	0.%{snap}.%{rel}
%define		trunk	r4177

%define		rel		69

%if "%{_alt_kernel}" != "%{nil}"
%if %{with kernel}
%undefine	with_userspace
%endif
%endif
%if %{with force_userspace}
%define		with_userspace 1
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		pname	madwifi-ng
%define		tname	madwifi-trunk

Summary:	Atheros WiFi card driver
Summary(pl.UTF-8):	Sterownik karty radiowej Atheros
Name:		%{pname}%{_alt_kernel}
Version:	0
Release:	%{prel}
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Provides:	madwifi
Obsoletes:	madwifi
Source0:	http://snapshots.madwifi-project.org/madwifi-trunk/%{tname}-%{trunk}-%{snap}.tar.gz
# Source0-md5:	10da9c87bce17879ee660a32cbf9cc83
# http://patches.aircrack-ng.org/madwifi-ng-r4073.patch
Patch0:		%{pname}-r4073.patch
# needed when build against (more noisy) pax enabled kernel
Patch1:		%{pname}-makefile-werror.patch
# http://madwifi-project.org/ticket/617
Patch2:		%{pname}-ticket-617.patch
Patch3:		%{pname}-ieee80211-skb-update.patch
Patch4:		format-security.patch
URL:		http://madwifi-project.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:3.0.21}
BuildRequires:	rpmbuild(macros) >= 1.642
%endif
ExclusiveArch:	alpha arm %{ix86} %{x8664} mips powerpc ppc sparc sparcv9 sparc64 xscale
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Atheros WiFi card driver. Supports Virtual APs and WDS Mode. It uses
binary HAL and supports AR5210, AR5211, AR5212, RF5111, RF5112, RF2413
and RF5413 cards.

%description -l pl.UTF-8
Sterownik karty radiowej Atheros. Wspiera tryb wirtualnego AP oraz
tryb WDS. Używa binarnej wersji HAL i obsługuje karty z układami
AR5210, AR5211, AR5212, RF5111, RF5112, RF2413 i RF5413.

%package devel
Summary:	Header files for madwifi
Summary(pl.UTF-8):	Pliki nagłówkowe dla madwifi
Group:		Development/Libraries
Provides:	madwifi-devel
Obsoletes:	madwifi-devel

%description devel
Header files for madwifi.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla madwifi.

%package -n kernel%{_alt_kernel}-net-madwifi-ng
Summary:	Linux driver for Atheros cards
Summary(pl.UTF-8):	Sterownik dla Linuksa do kart Atheros
Release:	%{prel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
Obsoletes:	kernel-smp-net-madwifi-ng
%endif

%description -n kernel%{_alt_kernel}-net-madwifi-ng
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-madwifi-ng -l pl.UTF-8
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -q -n %{tname}-%{trunk}-%{snap}
# aircrack-ng
%patch0 -p1
# werror
%patch1 -p1
# fix - ticket 617
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%if %{with userspace}
%{__make} -C tools \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}" \
	KERNELPATH="%{_kernelsrcdir}"
%endif

%ifarch alpha %{ix86} %{x8664}
%define target %{_target_base_arch}-elf
%endif
%ifarch sparc sparcv9 sparc64
%define target %{_target_base_arch}-be-elf
%endif
%ifarch powerpc ppc
%define target powerpc-be-elf
%endif

%if %{with kernel}
# kernel module(s)

# default is ath_rate_sample now compiles, _onoe does not
%define modules_ath ath/ath_pci,ath_hal/ath_hal,ath_rate/sample/ath_rate_sample
%define modules_wlan net80211/wlan,net80211/wlan_{wep,xauth,acl,ccmp,tkip,scan_{ap,sta}}
%define modules %{modules_ath},%{modules_wlan}

%define opts TARGET=%{target} KERNELPATH="%{_kernelsrcdir}" TOOLPREFIX= LDFLAGS_MODULE=

%{__make} %{opts}  svnversion.h
%build_kernel_modules -c -m %{modules} %{opts}

%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install-tools \
	TARGET=%{target} \
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

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYRIGHT README
%attr(755,root,root) %{_bindir}/80211debug
%attr(755,root,root) %{_bindir}/80211stats
%attr(755,root,root) %{_bindir}/ath_info
%attr(755,root,root) %{_bindir}/athchans
%attr(755,root,root) %{_bindir}/athctrl
%attr(755,root,root) %{_bindir}/athdebug
%attr(755,root,root) %{_bindir}/athkey
%attr(755,root,root) %{_bindir}/athstats
%attr(755,root,root) %{_bindir}/madwifi-unload
%attr(755,root,root) %{_bindir}/wlanconfig
%attr(755,root,root) %{_bindir}/wpakey
%{_mandir}/man8/80211debug.8*
%{_mandir}/man8/80211stats.8*
%{_mandir}/man8/ath_info.8*
%{_mandir}/man8/athchans.8*
%{_mandir}/man8/athctrl.8*
%{_mandir}/man8/athdebug.8*
%{_mandir}/man8/athkey.8*
%{_mandir}/man8/athstats.8*
%{_mandir}/man8/wlanconfig.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/madwifi
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-madwifi-ng
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*
%endif
