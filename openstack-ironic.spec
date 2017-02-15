%global full_release ironic-%{version}

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-ironic
# Liberty semver reset
# https://review.openstack.org/#/q/I1a161b2c1d1e27268065b6b4be24c8f7a5315afb,n,z
Epoch:          1
Summary:        OpenStack Baremetal Hypervisor API (ironic)
Version:        6.2.4
Release:        1%{?dist}
License:        ASL 2.0
URL:            http://www.openstack.org
Source0:        http://tarballs.openstack.org/ironic/ironic-%{version}.tar.gz

Source1:        openstack-ironic-api.service
Source2:        openstack-ironic-conductor.service
Source3:        ironic-rootwrap-sudoers
Source4:        ironic-dist.conf
Source5:        ironic.logrotate

BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  gmp-devel
BuildRequires:  python-sphinx
BuildRequires:  systemd
# Required to compile translation files
BuildRequires:  python-babel
# Required to run unit tests
BuildRequires:  pysendfile
BuildRequires:  python-alembic
BuildRequires:  python-automaton
BuildRequires:  python-dracclient
BuildRequires:  python-eventlet
BuildRequires:  python-futurist
BuildRequires:  python-glanceclient
BuildRequires:  python-greenlet
BuildRequires:  python-ironic-inspector-client
BuildRequires:  python-ironic-lib
BuildRequires:  python-jinja2
BuildRequires:  python-jsonpatch
BuildRequires:  python-jsonschema
BuildRequires:  python-keystoneauth1
BuildRequires:  python-keystonemiddleware
BuildRequires:  python-mock
BuildRequires:  python-netaddr
BuildRequires:  python-neutronclient
BuildRequires:  python-oslo-concurrency
BuildRequires:  python-oslo-config
BuildRequires:  python-oslo-context
BuildRequires:  python-oslo-db
BuildRequires:  python-oslo-i18n
BuildRequires:  python-oslo-log
BuildRequires:  python-oslo-messaging
BuildRequires:  python-oslo-middleware
BuildRequires:  python-oslo-policy
BuildRequires:  python-oslo-rootwrap
BuildRequires:  python-oslo-serialization
BuildRequires:  python-oslo-service
BuildRequires:  python-oslo-utils
BuildRequires:  python-oslo-versionedobjects
BuildRequires:  python-oslotest
BuildRequires:  python-os-testr
BuildRequires:  python-paramiko
BuildRequires:  python-pbr
BuildRequires:  python-pecan
BuildRequires:  python-proliantutils
BuildRequires:  python-psutil
BuildRequires:  python-pyghmi
BuildRequires:  python-requests
BuildRequires:  python-retrying
BuildRequires:  python-six
BuildRequires:  python-sqlalchemy
BuildRequires:  python-stevedore
BuildRequires:  python-swiftclient
BuildRequires:  python-testresources
BuildRequires:  python-webob
BuildRequires:  python-wsme
BuildRequires:  pytz

%prep
%setup -q -n ironic-%{upstream_version}
rm requirements.txt test-requirements.txt

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
install -p -D -m 640 etc/ironic/ironic.conf.sample %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
install -p -D -m 640 etc/ironic/policy.json %{buildroot}/%{_sysconfdir}/ironic/policy.json
install -p -D -m 640 etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
install -p -D -m 640 etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/

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
%{__python2} setup.py test

%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common

Requires:   ipmitool
Requires:   pysendfile
Requires:   python-alembic
Requires:   python-automaton
Requires:   python-dracclient
Requires:   python-eventlet
Requires:   python-futurist
Requires:   python-glanceclient
Requires:   python-greenlet
Requires:   python-ironic-inspector-client
Requires:   python-ironic-lib
Requires:   python-jinja2
Requires:   python-jsonpatch
Requires:   python-jsonschema
Requires:   python-keystoneauth1
Requires:   python-keystonemiddleware
Requires:   python-netaddr
Requires:   python-neutronclient
Requires:   python-oslo-concurrency
Requires:   python-oslo-config
Requires:   python-oslo-context
Requires:   python-oslo-db
Requires:   python-oslo-i18n
Requires:   python-oslo-log
Requires:   python-oslo-messaging
Requires:   python-oslo-middleware
Requires:   python-oslo-policy
Requires:   python-oslo-rootwrap
Requires:   python-oslo-serialization
Requires:   python-oslo-service
Requires:   python-oslo-utils
Requires:   python-oslo-versionedobjects
Requires:   python-paramiko
Requires:   python-pbr
Requires:   python-pecan
Requires:   python-proliantutils
Requires:   python-psutil
Requires:   python-pyghmi
Requires:   python-requests
Requires:   python-retrying
Requires:   python-six
Requires:   python-sqlalchemy
Requires:   python-stevedore
Requires:   python-swiftclient
Requires:   python-webob
Requires:   python-wsme
Requires:   pytz


Requires(pre):  shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common -f ironic.lang
%doc README.rst
%license LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{python2_sitelib}/ironic*
%exclude %{python2_sitelib}/ironic/tests
%exclude %{python2_sitelib}/ironic_tempest_plugin
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%attr(0750,ironic,ironic) %{_localstatedir}/log/ironic
%attr(-, root, ironic) %{_datadir}/ironic/ironic-dist.conf

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
Ironic API for management and provisioning of physical machines


%files api
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

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

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
Summary:        Ironic tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}
Requires:       python-mock
Requires:       python-oslotest
Requires:       python-os-testr
Requires:       python-testresources

%description -n python-ironic-tests
This package contains the Ironic test files.

%files -n python-ironic-tests
%{python2_sitelib}/ironic/tests
%{python2_sitelib}/ironic_tempest_plugin

%changelog
* Wed May 31 2017 rdo-trunk <javier.pena@redhat.com> 1:6.2.4-1
- Update to 6.2.4

* Tue Apr 11 2017 Alfredo Moralejo <amoralej@redhat.com> 1:6.2.3-1
- Update to 6.2.3

* Mon Nov 28 2016 Jon Schlueter <jschluet@redhat.com> 1:6.2.2-1
- Update to 6.2.2

* Mon Oct 10 2016 Haikel Guemar <hguemar@fedoraproject.org> 1:6.2.1-1
- Update to 6.2.1

* Thu Sep 29 2016 Alfredo Moralejo <amoralej@redhat.com> 1:6.2.0-1
- Update to 6.2.0

* Wed Sep 14 2016 Haikel Guemar <hguemar@fedoraproject.org> 1:6.1.0-1
- Update to 6.1.0

