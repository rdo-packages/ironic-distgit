%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
Source3:        ironic-sudoers
Source4:        ironic-dist.conf
Source5:        ironic.logrotate
Source6:        openstack-ironic-dnsmasq-tftp-server.service
Source7:        dnsmasq-tftp-server.conf
Source8:        openstack-ironic.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/ironic/ironic-%{version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:  openstack-macros
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  gmp-devel
BuildRequires:  python3-sphinx
BuildRequires:  systemd
# Required to run unit tests
BuildRequires:  python3-alembic
BuildRequires:  python3-automaton
BuildRequires:  python3-cinderclient
BuildRequires:  python3-ddt
BuildRequires:  python3-eventlet
BuildRequires:  python3-futurist
BuildRequires:  python3-glanceclient
BuildRequires:  python3-jinja2
BuildRequires:  python3-jsonpatch
BuildRequires:  python3-jsonschema
BuildRequires:  python3-keystoneauth1
BuildRequires:  python3-keystonemiddleware
BuildRequires:  python3-mock
BuildRequires:  python3-neutronclient
BuildRequires:  python3-openstacksdk
BuildRequires:  python3-oslo-concurrency
BuildRequires:  python3-oslo-config
BuildRequires:  python3-oslo-context
BuildRequires:  python3-oslo-db
BuildRequires:  python3-oslo-db-tests
BuildRequires:  python3-oslo-i18n
BuildRequires:  python3-oslo-log
BuildRequires:  python3-oslo-messaging
BuildRequires:  python3-oslo-middleware
BuildRequires:  python3-oslo-policy
BuildRequires:  python3-oslo-reports
BuildRequires:  python3-oslo-rootwrap
BuildRequires:  python3-oslo-serialization
BuildRequires:  python3-oslo-service
BuildRequires:  python3-oslo-upgradecheck
BuildRequires:  python3-oslo-utils
BuildRequires:  python3-oslo-versionedobjects
BuildRequires:  python3-oslotest
BuildRequires:  python3-osprofiler
BuildRequires:  python3-os-traits
BuildRequires:  python3-pbr
BuildRequires:  python3-pecan
BuildRequires:  python3-psutil
BuildRequires:  python3-pycdlib
BuildRequires:  python3-pysnmp
BuildRequires:  python3-pytz
BuildRequires:  python3-requests
BuildRequires:  python3-scciclient
BuildRequires:  python3-sqlalchemy
BuildRequires:  python3-stestr
BuildRequires:  python3-stevedore
BuildRequires:  python3-sushy
BuildRequires:  python3-swiftclient
BuildRequires:  python3-testresources
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools
BuildRequires:  python3-tooz
BuildRequires:  python3-webtest

BuildRequires:  python3-dracclient
BuildRequires:  python3-ironic-lib
BuildRequires:  python3-proliantutils
BuildRequires:  python3-tenacity
BuildRequires:  python3-webob

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: udev

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%setup -q -n ironic-%{upstream_version}
# Let RPM handle the requirements
%py_req_cleanup
# Remove tempest plugin entrypoint as a workaround
sed -i '/tempest/d' setup.cfg
rm -rf ironic_tempest_plugin
%build
%{py3_build}

%install
%{py3_install}

install -p -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-ironic

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE8} %{buildroot}%{_unitdir}

# install sudoers file
mkdir -p %{buildroot}%{_sysconfdir}/sudoers.d
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/ironic

mkdir -p %{buildroot}%{_sharedstatedir}/ironic/
mkdir -p %{buildroot}%{_localstatedir}/log/ironic/
mkdir -p %{buildroot}%{_sysconfdir}/ironic/rootwrap.d

#Populate the conf dir
export PYTHONPATH=.
oslo-config-generator --config-file tools/config/ironic-config-generator.conf --output-file %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
oslopolicy-sample-generator --config-file tools/policy/ironic-policy-generator.conf
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
mv %{buildroot}%{_prefix}/etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/
# Remove duplicate config files under /usr/etc/ironic
rmdir %{buildroot}%{_prefix}/etc/ironic/rootwrap.d
rmdir %{buildroot}%{_prefix}/etc/ironic

# Install distribution config
install -p -D -m 640 %{SOURCE4} %{buildroot}/%{_datadir}/ironic/ironic-dist.conf
install -p -D -m 644 %{SOURCE7} %{buildroot}/%{_sysconfdir}/ironic/dnsmasq-tftp-server.conf


%check
PYTHON=%{__python3} stestr run

%description
Ironic provides an API for management and provisioning of physical machines

%files
%{_bindir}/ironic
%{_unitdir}/openstack-ironic.service

%post
%systemd_post openstack-ironic.service

%preun
%systemd_preun openstack-ironic.service

%postun
%systemd_postun_with_restart openstack-ironic.service

%package common
Summary: Ironic common

Requires:   python3-alembic >= 1.4.2
Requires:   python3-automaton >= 1.9.0
Requires:   python3-cinderclient >= 3.3.0
Requires:   python3-eventlet >= 0.18.2
Requires:   python3-futurist >= 1.2.0
Requires:   python3-glanceclient >= 2.8.0
Requires:   python3-ironic-lib >= 5.4.0
Requires:   python3-jinja2 >= 3.0.0
Requires:   python3-jsonpatch >= 1.16
Requires:   python3-jsonschema >= 3.2.0
Requires:   python3-keystoneauth1 >= 4.2.0
Requires:   python3-keystonemiddleware >= 9.5.0
Requires:   python3-openstacksdk >= 0.48.0
Requires:   python3-oslo-concurrency >= 4.2.0
Requires:   python3-oslo-config >= 6.8.0
Requires:   python3-oslo-context >= 2.22.0
Requires:   python3-oslo-db >= 9.1.0
Requires:   python3-oslo-log >= 4.3.0
Requires:   python3-oslo-messaging >= 14.1.0
Requires:   python3-oslo-middleware >= 3.31.0
Requires:   python3-oslo-policy >= 3.7.0
Requires:   python3-oslo-rootwrap >= 5.8.0
Requires:   python3-oslo-serialization >= 2.25.0
Requires:   python3-oslo-service >= 1.24.0
Requires:   python3-oslo-upgradecheck >= 1.3.0
Requires:   python3-oslo-utils >= 4.5.0
Requires:   python3-oslo-versionedobjects >= 1.31.2
Requires:   python3-osprofiler >= 1.5.0
Requires:   python3-os-traits >= 0.4.0
Requires:   python3-pbr >= 3.1.1
Requires:   python3-pecan >= 1.0.0
Requires:   python3-oslo-privsep >= 2.4.0
Requires:   python3-psutil >= 3.2.2
Requires:   python3-pycdlib >= 1.11.0
Requires:   python3-pytz >= 2013.6
Requires:   python3-requests >= 2.18.0
Requires:   python3-rfc3986 >= 1.2.0
Requires:   python3-sqlalchemy >= 1.4.0
Requires:   python3-stevedore >= 1.29.0
Requires:   python3-sushy >= 4.3.0
Requires:   python3-swiftclient >= 3.2.0
Requires:   python3-tenacity >= 6.2.0
Requires:   python3-tooz >= 2.7.0
Requires:   python3-webob >= 1.7.1

%if 0%{?fedora} || 0%{?rhel} > 7
Recommends: ipmitool
Recommends: python3-dracclient >= 5.1.0
Recommends: python3-proliantutils >= 2.10.0
Recommends: python3-pysnmp >= 4.3.0
Recommends: python3-scciclient >= 0.8.0

# Optional features
Suggests: python3-oslo-i18n >= 3.15.3
Suggests: python3-oslo-reports >= 1.18.0
%endif

Requires(pre):  shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst
%doc etc/ironic/policy.yaml.sample
%license LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{_bindir}/ironic-status
%{python3_sitelib}/ironic
%{python3_sitelib}/ironic-*.egg-info
%exclude %{python3_sitelib}/ironic/tests
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%attr(0750,ironic,ironic) %{_localstatedir}/log/ironic
%attr(-, root, ironic) %{_datadir}/ironic/ironic-dist.conf
%exclude %{python3_sitelib}/ironic_tests.egg_info

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
Requires: udev
Requires: dosfstools
Requires: mtools
Requires: xorriso
Requires: pykickstart
Requires: syslinux-nonlinux

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

%package dnsmasq-tftp-server
Summary:    tftp-server service for Ironic using dnsmasq
Requires:   dnsmasq

%description dnsmasq-tftp-server
Ironic is service for the management and provisioning of physical machines

This package contains a dnsmasq service pre-configured for using with
ironic to support TFTP to enable initial PXE boot operations using TFTP.

%files dnsmasq-tftp-server
%license LICENSE
%{_unitdir}/openstack-ironic-dnsmasq-tftp-server.service
%config(noreplace) %attr(-, root, ironic) %{_sysconfdir}/ironic/dnsmasq-tftp-server.conf

%post dnsmasq-tftp-server
%systemd_post openstack-ironic-dnsmasq-tftp-server.service

%preun dnsmasq-tftp-server
%systemd_preun openstack-ironic-dnsmasq-tftp-server.service

%postun dnsmasq-tftp-server
%systemd_postun_with_restart openstack-ironic-dnsmasq-tftp-server.service

%package -n python3-ironic-tests
Summary:        Ironic unit tests
%{?python_provide:%python_provide python3-ironic-tests}
Requires:       %{name}-common = %{epoch}:%{version}-%{release}
Requires:       python3-mock
Requires:       python3-oslotest
Requires:       python3-stestr
Requires:       python3-testresources
Requires:       python3-testscenarios
Requires:       python3-testtools


%description -n python3-ironic-tests
This package contains the Ironic test files.

%files -n python3-ironic-tests
%{python3_sitelib}/ironic/tests

%changelog
