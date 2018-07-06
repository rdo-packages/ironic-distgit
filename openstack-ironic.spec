%global full_release ironic-%{version}

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-ironic
# Liberty semver reset
# https://review.openstack.org/#/q/I1a161b2c1d1e27268065b6b4be24c8f7a5315afb,n,z
Epoch:          1
Summary:        OpenStack Baremetal Hypervisor API (ironic)
Version:        10.1.3
Release:        1%{?dist}
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
BuildRequires:  python2-setuptools
BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  gmp-devel
BuildRequires:  python2-sphinx
BuildRequires:  systemd
# Required to compile translation files
BuildRequires:  python2-babel
# Required to run unit tests
BuildRequires:  pysendfile
BuildRequires:  python2-alembic
BuildRequires:  python2-automaton
BuildRequires:  python2-cinderclient
BuildRequires:  python-dracclient
BuildRequires:  python2-eventlet
BuildRequires:  python2-futurist
BuildRequires:  python2-glanceclient
BuildRequires:  python-ironic-inspector-client
BuildRequires:  python-ironic-lib
BuildRequires:  python2-jinja2
BuildRequires:  python2-jsonpatch
BuildRequires:  python2-jsonschema
BuildRequires:  python2-keystoneauth1
BuildRequires:  python2-keystonemiddleware
BuildRequires:  python2-mock
BuildRequires:  python2-neutronclient
BuildRequires:  python2-oslo-concurrency
BuildRequires:  python2-oslo-config
BuildRequires:  python2-oslo-context
BuildRequires:  python2-oslo-db
BuildRequires:  python2-oslo-db-tests
BuildRequires:  python2-oslo-i18n
BuildRequires:  python2-oslo-log
BuildRequires:  python2-oslo-messaging
BuildRequires:  python2-oslo-middleware
BuildRequires:  python2-oslo-policy
BuildRequires:  python2-oslo-reports
BuildRequires:  python2-oslo-rootwrap
BuildRequires:  python2-oslo-serialization
BuildRequires:  python2-oslo-service
BuildRequires:  python2-oslo-utils
BuildRequires:  python2-oslo-versionedobjects
BuildRequires:  python2-oslotest
BuildRequires:  python2-osprofiler
BuildRequires:  /usr/bin/ostestr
BuildRequires:  python2-os-traits
BuildRequires:  python2-pbr
BuildRequires:  python2-pecan
BuildRequires:  python-proliantutils
BuildRequires:  python2-psutil
BuildRequires:  python2-requests
BuildRequires:  python-retrying
BuildRequires:  python2-scciclient
BuildRequires:  python2-six
BuildRequires:  python2-sqlalchemy
BuildRequires:  python2-stevedore
BuildRequires:  python2-sushy
BuildRequires:  python2-swiftclient
BuildRequires:  python2-testresources
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools
BuildRequires:  python2-tooz
BuildRequires:  python-UcsSdk
BuildRequires:  python-webob
BuildRequires:  python2-wsme
BuildRequires:  python2-pysnmp
BuildRequires:  python2-pytz

%prep
%setup -q -n ironic-%{upstream_version}
# Let RPM handle the requirements
%py_req_cleanup
# Remove tempest plugin entrypoint as a workaround
sed -i '/tempest/d' setup.cfg
rm -rf ironic_tempest_plugin
%build
%{__python2} setup.py build
# Generate i18n files
%{__python2} setup.py compile_catalog -d build/lib/ironic/locale

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}

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
oslo-config-generator --config-file tools/config/ironic-config-generator.conf --output-file %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
oslopolicy-sample-generator --config-file tools/policy/ironic-policy-generator.conf --output-file %{buildroot}/%{_sysconfdir}/ironic/policy.json
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/
# Remove duplicate config files under /usr/etc/ironic
rmdir %{buildroot}%{_prefix}/etc/ironic/rootwrap.d
rmdir %{buildroot}%{_prefix}/etc/ironic

# Install distribution config
install -p -D -m 640 %{SOURCE4} %{buildroot}/%{_datadir}/ironic/ironic-dist.conf

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python2_sitelib}/ironic/locale/*/LC_*/ironic*po
rm -f %{buildroot}%{python2_sitelib}/ironic/locale/*pot
mv %{buildroot}%{python2_sitelib}/ironic/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang ironic --all-name

%check
ostestr --path ironic/tests/unit

%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common

Requires:   ipmitool
Requires:   pysendfile
Requires:   python2-alembic
Requires:   python2-automaton >= 1.9.0
Requires:   python2-cinderclient >= 3.3.0
Requires:   python-dracclient >= 1.3.0
Requires:   python2-eventlet
Requires:   python2-futurist >= 1.2.0
Requires:   python2-glanceclient >= 2.8.0
Requires:   python-ironic-inspector-client >= 1.5.0
Requires:   python-ironic-lib >= 2.5.0
Requires:   python2-jinja2
Requires:   python2-jsonpatch
Requires:   python2-jsonschema
Requires:   python2-keystoneauth1 >= 3.3.0
Requires:   python2-keystonemiddleware >= 4.17.0
Requires:   python2-neutronclient >= 6.3.0
Requires:   python2-oslo-concurrency >= 3.25.0
Requires:   python2-oslo-config >= 2:5.1.0
Requires:   python2-oslo-context >= 2.19.2
Requires:   python2-oslo-db >= 4.27.0
Requires:   python2-oslo-i18n >= 3.15.3
Requires:   python2-oslo-log >= 3.36.0
Requires:   python2-oslo-messaging >= 5.29.0
Requires:   python2-oslo-middleware >= 3.31.0
Requires:   python2-oslo-policy >= 1.30.0
Requires:   python2-oslo-reports >= 1.18.0
Requires:   python2-oslo-rootwrap >= 5.8.0
Requires:   python2-oslo-serialization >= 2.18.0
Requires:   python2-oslo-service >= 1.24.0
Requires:   python2-oslo-utils >= 3.33.0
Requires:   python2-oslo-versionedobjects >= 1.31.2
Requires:   python2-osprofiler >= 1.5.0
Requires:   python2-os-traits
Requires:   python2-pbr
Requires:   python2-pecan
Requires:   python-proliantutils >= 2.4.0
Requires:   python2-psutil
Requires:   python2-requests
Requires:   python-retrying
Requires:   python2-rfc3986 >= 0.3.1
Requires:   python2-scciclient >= 0.5.0
Requires:   python2-six
Requires:   python2-sqlalchemy
Requires:   python2-stevedore >= 1.20.0
Requires:   python2-sushy
Requires:   python2-swiftclient >= 3.2.0
Requires:   python2-tooz >= 1.58.0
Requires:   python-UcsSdk >= 0.8.2.2
Requires:   python-webob >= 1.7.1
Requires:   python2-wsme
Requires:   python2-pysnmp
Requires:   python2-pytz


Requires(pre):  shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common -f ironic.lang
%doc README.rst
%license LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{python2_sitelib}/ironic
%{python2_sitelib}/ironic-*.egg-info
%exclude %{python2_sitelib}/ironic/tests
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%attr(0750,ironic,ironic) %{_localstatedir}/log/ironic
%attr(-, root, ironic) %{_datadir}/ironic/ironic-dist.conf
%exclude %{python2_sitelib}/ironic_tests.egg_info

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

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

%{?systemd_requires}

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

%package -n python-ironic-tests
Summary:        Ironic unit tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}
Requires:       python2-mock
Requires:       python2-oslotest
Requires:       /usr/bin/ostestr
Requires:       python2-testresources
Requires:       python2-testscenarios
Requires:       python2-testtools


%description -n python-ironic-tests
This package contains the Ironic test files.

%files -n python-ironic-tests
%{python2_sitelib}/ironic/tests

%changelog
* Mon Jun 18 2018 RDO <dev@lists.rdoproject.org> 1:10.1.3-1
- Update to 10.1.3

* Mon Apr 09 2018 RDO <dev@lists.rdoproject.org> 1:10.1.2-1
- Update to 10.1.2

* Thu Feb 22 2018 RDO <dev@lists.rdoproject.org> 1:10.1.1-1
- Update to 10.1.1

* Thu Feb 15 2018 RDO <dev@lists.rdoproject.org> 1:10.1.0-1
- Update to 10.1.0

