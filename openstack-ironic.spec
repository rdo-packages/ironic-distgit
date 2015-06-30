%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global	release_name juno
%global	full_release ironic-%{version}

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:		openstack-ironic
Summary:	OpenStack Baremetal Hypervisor API (ironic)
Version:        XXX
Release:        XXX
License:	ASL 2.0
Group:		System Environment/Base
URL:		http://www.openstack.org
Source0:	https://launchpad.net/ironic/%{release_name}/%{version}/+download/ironic-%{version}.tar.gz
#Source0:	https://launchpad.net/ironic/juno/2014.2/+download/ironic-2014.2.tar.gz

Source1:	openstack-ironic-api.service
Source2:	openstack-ironic-conductor.service
Source3:	ironic-rootwrap-sudoers

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
rm requirements.txt test-requirements.txt

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}


# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}

# install sudoers file
mkdir -p %{buildroot}%{_sysconfdir}/sudoers.d
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/ironic

mkdir -p %{buildroot}%{_sharedstatedir}/ironic/
mkdir -p %{buildroot}%{_sysconfdir}/ironic/rootwrap.d

#Populate the conf dir
install -p -D -m 640 etc/ironic/ironic.conf.sample %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
install -p -D -m 640 etc/ironic/policy.json %{buildroot}/%{_sysconfdir}/ironic/policy.json
install -p -D -m 640 etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
install -p -D -m 640 etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/


%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common

Requires:	ipmitool
Requires:	python-eventlet
Requires:	python-greenlet
Requires:	python-iso8601
Requires:	python-posix_ipc
Requires:	python-jsonpatch
Requires:	python-keystonemiddleware
Requires:	python-kombu
Requires:	python-anyjson
Requires:	python-lockfile
Requires:	python-lxml
Requires:	python-migrate
Requires:	python-mock
Requires:	python-netaddr
Requires:	python-oslo-config
Requires:	python-oslo-db
Requires:	python-oslo-i18n
Requires:	python-oslo-rootwrap
Requires:	python-oslo-utils
Requires:	python-paramiko
Requires:	python-pecan
Requires:	python-retrying
Requires:	python-six
Requires:	python-stevedore
Requires:	python-webob
Requires:	python-websockify
Requires:	python-wsme
Requires:	pycrypto
Requires:	python-sqlalchemy
Requires:	python-neutronclient
Requires:	python-glanceclient
Requires:	python-keystoneclient
Requires:	python-swiftclient
Requires:	python-jinja2
Requires:	python-pyghmi
Requires:	python-alembic
Requires:	pysendfile
Requires:	python-pbr
Requires:	python-automaton
Requires:	python-oslo-context
Requires:	python-oslo-log
Requires:	python-oslo-concurrency
Requires:	python-oslo-policy
Requires:	python-oslo-serialization
Requires:	python-oslo-messaging
Requires:	python-oslo-service
Requires:	python-requests

Requires(pre):	shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{python2_sitelib}/ironic*
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API

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
