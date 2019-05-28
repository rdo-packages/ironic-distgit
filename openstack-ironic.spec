# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global full_release ironic-%{version}

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-ironic
# Liberty semver reset
# https://review.openstack.org/#/q/I1a161b2c1d1e27268065b6b4be24c8f7a5315afb,n,z
Epoch:          1
Summary:        OpenStack Baremetal Hypervisor API (ironic)
Version:        XXX
Release:        XXX
License:        ASL 2.0
URL:            http://www.openstack.org
Source0:        https://tarballs.openstack.org/ironic/ironic-%{version}.tar.gz

Source1:        openstack-ironic-api.service
Source2:        openstack-ironic-conductor.service
Source3:        ironic-rootwrap-sudoers
Source4:        ironic-dist.conf
Source5:        ironic.logrotate

BuildArch:      noarch
BuildRequires:  openstack-macros
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  gmp-devel
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  systemd
# Required to compile translation files
BuildRequires:  python%{pyver}-babel
# Required to run unit tests
BuildRequires:  python%{pyver}-alembic
BuildRequires:  python%{pyver}-automaton
BuildRequires:  python%{pyver}-cinderclient
BuildRequires:  python%{pyver}-eventlet
BuildRequires:  python%{pyver}-futurist
BuildRequires:  python%{pyver}-glanceclient
BuildRequires:  python%{pyver}-jinja2
BuildRequires:  python%{pyver}-jsonpatch
BuildRequires:  python%{pyver}-jsonschema
BuildRequires:  python%{pyver}-keystoneauth1
BuildRequires:  python%{pyver}-keystonemiddleware
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-neutronclient
BuildRequires:  python%{pyver}-openstacksdk
BuildRequires:  python%{pyver}-oslo-concurrency
BuildRequires:  python%{pyver}-oslo-config
BuildRequires:  python%{pyver}-oslo-context
BuildRequires:  python%{pyver}-oslo-db
BuildRequires:  python%{pyver}-oslo-db-tests
BuildRequires:  python%{pyver}-oslo-i18n
BuildRequires:  python%{pyver}-oslo-log
BuildRequires:  python%{pyver}-oslo-messaging
BuildRequires:  python%{pyver}-oslo-middleware
BuildRequires:  python%{pyver}-oslo-policy
BuildRequires:  python%{pyver}-oslo-reports
BuildRequires:  python%{pyver}-oslo-rootwrap
BuildRequires:  python%{pyver}-oslo-serialization
BuildRequires:  python%{pyver}-oslo-service
BuildRequires:  python%{pyver}-oslo-upgradecheck
BuildRequires:  python%{pyver}-oslo-utils
BuildRequires:  python%{pyver}-oslo-versionedobjects
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-osprofiler
BuildRequires:  python%{pyver}-os-traits
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-pecan
BuildRequires:  python%{pyver}-psutil
BuildRequires:  python%{pyver}-pysnmp
BuildRequires:  python%{pyver}-pytz
BuildRequires:  python%{pyver}-requests
BuildRequires:  python%{pyver}-scciclient
BuildRequires:  python%{pyver}-six
BuildRequires:  python%{pyver}-sqlalchemy
BuildRequires:  python%{pyver}-stestr
BuildRequires:  python%{pyver}-stevedore
BuildRequires:  python%{pyver}-sushy
BuildRequires:  python%{pyver}-swiftclient
BuildRequires:  python%{pyver}-testresources
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-tooz
BuildRequires:  python%{pyver}-wsme

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:  pysendfile
BuildRequires:  python-dracclient
BuildRequires:  python-ironic-inspector-client
BuildRequires:  python-ironic-lib
BuildRequires:  python-proliantutils
BuildRequires:  python-retrying
BuildRequires:  python-UcsSdk
BuildRequires:  python-webob
%else
BuildRequires:  python%{pyver}-pysendfile
BuildRequires:  python%{pyver}-dracclient
BuildRequires:  python%{pyver}-ironic-inspector-client
BuildRequires:  python%{pyver}-ironic-lib
BuildRequires:  python%{pyver}-proliantutils
BuildRequires:  python%{pyver}-retrying
# FIXME(ykarel) Remove the optional dep until ironic fixes the dependency
# on python3 uncompatible UcsSdk https://storyboard.openstack.org/#!/story/2003925
#BuildRequires:  python%{pyver}-UcsSdk
BuildRequires:  python%{pyver}-webob
%endif

%prep
%setup -q -n ironic-%{upstream_version}
# Let RPM handle the requirements
%py_req_cleanup
# Remove tempest plugin entrypoint as a workaround
sed -i '/tempest/d' setup.cfg
rm -rf ironic_tempest_plugin
%build
%{pyver_build}

%install
%{pyver_install}

install -p -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-ironic

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}

# install sudoers file
mkdir -p %{buildroot}%{_sysconfdir}/sudoers.d
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/ironic

mkdir -p %{buildroot}%{_sharedstatedir}/ironic/
mkdir -p %{buildroot}%{_localstatedir}/log/ironic/
mkdir -p %{buildroot}%{_sysconfdir}/ironic/rootwrap.d

#Populate the conf dir
export PYTHONPATH=.
oslo-config-generator-%{pyver} --config-file tools/config/ironic-config-generator.conf --output-file %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
oslopolicy-sample-generator-%{pyver} --config-file tools/policy/ironic-policy-generator.conf --output-file %{buildroot}/%{_sysconfdir}/ironic/policy.json
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/
# Remove duplicate config files under /usr/etc/ironic
rmdir %{buildroot}%{_prefix}/etc/ironic/rootwrap.d
rmdir %{buildroot}%{_prefix}/etc/ironic

# Install distribution config
install -p -D -m 640 %{SOURCE4} %{buildroot}/%{_datadir}/ironic/ironic-dist.conf

%check
PYTHON=%{pyver_bin} stestr-%{pyver} run

%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common

Requires:   ipmitool
Requires:   python%{pyver}-alembic
Requires:   python%{pyver}-automaton >= 1.9.0
Requires:   python%{pyver}-cinderclient >= 3.3.0
Requires:   python%{pyver}-eventlet
Requires:   python%{pyver}-futurist >= 1.2.0
Requires:   python%{pyver}-glanceclient >= 2.8.0
Requires:   python%{pyver}-jinja2
Requires:   python%{pyver}-jsonpatch
Requires:   python%{pyver}-jsonschema
Requires:   python%{pyver}-keystoneauth1 >= 3.4.0
Requires:   python%{pyver}-keystonemiddleware >= 4.17.0
Requires:   python%{pyver}-neutronclient >= 6.7.0
Requires:   python%{pyver}-openstacksdk >= 0.25.0
Requires:   python%{pyver}-oslo-concurrency >= 3.26.0
Requires:   python%{pyver}-oslo-config >= 2:5.2.0
Requires:   python%{pyver}-oslo-context >= 2.19.2
Requires:   python%{pyver}-oslo-db >= 4.27.0
Requires:   python%{pyver}-oslo-i18n >= 3.15.3
Requires:   python%{pyver}-oslo-log >= 3.36.0
Requires:   python%{pyver}-oslo-messaging >= 5.29.0
Requires:   python%{pyver}-oslo-middleware >= 3.31.0
Requires:   python%{pyver}-oslo-policy >= 1.30.0
Requires:   python%{pyver}-oslo-reports >= 1.18.0
Requires:   python%{pyver}-oslo-rootwrap >= 5.8.0
Requires:   python%{pyver}-oslo-serialization >= 2.18.0
Requires:   python%{pyver}-oslo-service >= 1.24.0
Requires:   python%{pyver}-oslo-utils >= 3.33.0
Requires:   python%{pyver}-oslo-upgradecheck >= 0.1.0
Requires:   python%{pyver}-oslo-versionedobjects >= 1.31.2
Requires:   python%{pyver}-osprofiler >= 1.5.0
Requires:   python%{pyver}-os-traits >= 0.4.0
Requires:   python%{pyver}-pbr
Requires:   python%{pyver}-pecan
Requires:   python%{pyver}-psutil
Requires:   python%{pyver}-pysnmp
Requires:   python%{pyver}-pytz
Requires:   python%{pyver}-requests
Requires:   python%{pyver}-rfc3986 >= 0.3.1
Requires:   python%{pyver}-scciclient >= 0.5.0
Requires:   python%{pyver}-six
Requires:   python%{pyver}-sqlalchemy
Requires:   python%{pyver}-stevedore >= 1.20.0
Requires:   python%{pyver}-sushy
Requires:   python%{pyver}-swiftclient >= 3.2.0
Requires:   python%{pyver}-tooz >= 1.58.0
Requires:   python%{pyver}-wsme

# Handle python2 exception
%if %{pyver} == 2
Requires:   pysendfile
Requires:   python-dracclient >= 1.3.0
Requires:   python-ironic-inspector-client >= 1.5.0
Requires:   python-ironic-lib >= 2.15.0
Requires:   python-proliantutils >= 2.4.0
Requires:   python-retrying
Requires:   python-UcsSdk >= 0.8.2.2
Requires:   python-webob >= 1.7.1
%else
Requires:   python%{pyver}-pysendfile
Requires:   python%{pyver}-dracclient >= 1.3.0
Requires:   python%{pyver}-ironic-inspector-client >= 1.5.0
Requires:   python%{pyver}-ironic-lib >= 2.15.0
Requires:   python%{pyver}-proliantutils >= 2.4.0
Requires:   python%{pyver}-retrying
# FIXME(ykarel) Remove the optional dep until ironic fixes the dependency
# on python3 uncompatible UcsSdk https://storyboard.openstack.org/#!/story/2003925
#Requires:   python%{pyver}-UcsSdk >= 0.8.2.2
Requires:   python%{pyver}-webob >= 1.7.1
%endif

Requires(pre):  shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst
%license LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{_bindir}/ironic-status
%{pyver_sitelib}/ironic
%{pyver_sitelib}/ironic-*.egg-info
%exclude %{pyver_sitelib}/ironic/tests
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%attr(0750,ironic,ironic) %{_localstatedir}/log/ironic
%attr(-, root, ironic) %{_datadir}/ironic/ironic-dist.conf
%exclude %{pyver_sitelib}/ironic_tests.egg_info

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description api
Ironic API for management and provisioning of physical machines


%files api
%{_bindir}/ironic-api
%{_bindir}/ironic-api-wsgi
%{_unitdir}/openstack-ironic-api.service

%post api
%systemd_post openstack-ironic-api.service

%preun api
%systemd_preun openstack-ironic-api.service

%postun api
%systemd_postun_with_restart openstack-ironic-api.service

%package conductor
Summary: The Ironic Conductor

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description conductor
Ironic Conductor for management and provisioning of physical machines

%files conductor
%{_bindir}/ironic-conductor
%{_unitdir}/openstack-ironic-conductor.service

%post conductor
%systemd_post openstack-ironic-conductor.service

%preun conductor
%systemd_preun openstack-ironic-conductor.service

%postun conductor
%systemd_postun_with_restart openstack-ironic-conductor.service

%package -n python%{pyver}-ironic-tests
Summary:        Ironic unit tests
%{?python_provide:%python_provide python%{pyver}-ironic-tests}
Requires:       %{name}-common = %{epoch}:%{version}-%{release}
Requires:       python%{pyver}-mock
Requires:       python%{pyver}-oslotest
Requires:       python%{pyver}-stestr
Requires:       python%{pyver}-testresources
Requires:       python%{pyver}-testscenarios
Requires:       python%{pyver}-testtools


%description -n python%{pyver}-ironic-tests
This package contains the Ironic test files.

%files -n python%{pyver}-ironic-tests
%{pyver_sitelib}/ironic/tests

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/ironic/commit/?id=aae98fbedcd26a04e86c99096976a568ed292b22
