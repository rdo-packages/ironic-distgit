%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global	release_name icehouse
%global	release_letter rc
%global	milestone 1
%global	full_release ironic-%{upstream_version}


Name:		openstack-ironic
Summary:	OpenStack Baremetal Hypervisor API (ironic)
Version:	2014.1
Release:	%{release_letter}%{milestone}.2%{?dist}.1
License:	ASL 2.0
Group:		System Environment/Base
URL:		http://www.openstack.org
#Source0:	https://launchpad.net/ironic/%{release_name}/%{release_name}-%{milestone}/+download/%{full_release}.tar.gz
Source0:	https://launchpad.net/ironic/icehouse/icehouse-rc1/+download/ironic-2014.1.rc1.tar.gz


Source1:	openstack-ironic-api.service
Source2:	openstack-ironic-conductor.service
Source3:	ironic-sudoers

Patch0001: 0001-Remove-runtime-dep-on-python-pbr.patch

BuildArch:	noarch
BuildRequires:	python-setuptools
BuildRequires:	python2-devel
BuildRequires:	python-pbr
BuildRequires:	openssl-devel
BuildRequires:	libxml2-devel
BuildRequires:	libxslt-devel
BuildRequires:	gmp-devel
BuildRequires:	python-sphinx
BuildRequires:	systemd


%prep
%setup -q -n ironic-%{upstream_version}

%patch0001 -p1

# Remove the requirements file so that PBR hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

# We add REDHATIRONICVERSION/RELEASE with the pbr removal patch
sed -i s/REDHATIRONICVERSION/%{version}/ ironic/version.py
sed -i s/REDHATIRONICRELEASE/%{release}/ ironic/version.py

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}


# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}

mkdir -p %{buildroot}%{_sharedstatedir}/ironic/
mkdir -p %{buildroot}%{_sysconfdir}/ironic/rootwrap.d

#Populate the conf dir
install -p -D -m 640 %{_builddir}/%{full_release}/etc/ironic/ironic.conf.sample %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
install -p -D -m 640 %{_builddir}/%{full_release}/etc/ironic/policy.json %{buildroot}/%{_sysconfdir}/ironic/policy.json
install -p -D -m 640 %{_builddir}/%{full_release}/etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
install -p -D -m 640 %{_builddir}/%{full_release}/etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/

# Install sudoers
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/ironic


%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common
Group: System Environment/Base

Requires:	python-eventlet
Requires:	python-fixtures
Requires:	python-iso8601
Requires:	python-jsonpatch
Requires:	python-kombu
Requires:	python-anyjson
Requires:	python-migrate
Requires:	python-mock
Requires:	python-netaddr
Requires:	python-paramiko
Requires:	python-pecan
Requires:	python-stevedore
Requires:	python-wsme
Requires:	pycrypto
Requires:	python-sqlalchemy
Requires:	python-neutronclient
Requires:	python-glanceclient
Requires:	python-keystoneclient
Requires:	python-keystonemiddleware
Requires:	python-jinja2
Requires:	python-pyghmi
Requires:	python-alembic
Requires:	python-posix_ipc
Requires:	python-oslo-concurrency

Requires(pre):	shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{_bindir}/ironic-nova-bm-migrate
%{python_sitelib}/ironic*
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%config(noreplace) %{_sysconfdir}/sudoers.d/ironic

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
Ironic API for management and provisioning of physical machines


%files api
%doc LICENSE
%{_bindir}/ironic-api
%{_unitdir}/openstack-ironic-api.service

%post api
%systemd_post openstack-ironic-api.service

%preun api
%systemd_preun openstack-ironic-api.service

%postun api
%systemd_postun_with_restart openstack-ironic-api.service

%package conductor
Summary: The Ironic Conductor
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description conductor
Ironic Conductor for management and provisioning of physical machines


%files conductor
%doc LICENSE
%{_bindir}/ironic-conductor
%{_unitdir}/openstack-ironic-conductor.service

%post conductor
%systemd_post openstack-ironic-conductor.service

%preun conductor
%systemd_preun openstack-ironic-conductor.service

%postun conductor
%systemd_postun_with_restart openstack-ironic-conductor.service



%changelog
* Wed Oct 29 2014 Dan Prince <dprince@redhat.com> - XXX
- Add dependency on oslo.concurrency.

* Thu Oct 09 2014 Dan Prince <dprince@redhat.com> - XXX
- Patch out PBR runtime dependency.

* Wed Oct 01 2014 Dan Prince <dprince@redhat.com> - XXX
- Remove requirements.txt and test-requirements.txt in prep rather
  than via a patch.

* Thu Sep 04 2014 James Slagle <jslagle@redhat.com> - XXX
- Add ironic-sudoers

* Fri Aug 15 2014 Derek Higgins <derekh@redhat.com> - XXX
- Add dependency on python-keystonemiddleware

* Mon Aug 11 2014 Derek Higgins <derekh@redhat.com> - XXX
- Update requirements

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2014.1-rc1.2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild


* Wed Apr 9 2014 Angus Thomas <athomas@redhat.com> - 2014.1-rc1.2
- License file in each package

* Mon Apr 7 2014 Angus Thomas <athomas@redhat.com> - 2014.1-rc1.1
- Rebuilt with -rc1 tarball
- Rebased patches
- Added dependency on python-alembic

* Thu Mar 27 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.5
- Split into multiple packages

* Fri Feb 28 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.4
- Restored BuildRequires: python-pbr 

* Thu Feb 27 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.3
- Added dependency on python-pyghmi
- Patch to remove pbr build dependency
- Fixed python2-devel build dependency
- Added noreplace to config files
- Added  unitdir macro for systemd service file installation
- Added scripts to manage systemd services
- Removed unnecessary Requires & BuildRequires


* Mon Feb 24 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.2
- Removed /var/log/ironic from package
- Replaced hardcoded file paths with macros
- Added LICENSE and README.rst docs

* Fri Feb 21 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.1
- Initial package build

