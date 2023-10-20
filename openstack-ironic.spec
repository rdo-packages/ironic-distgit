%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global full_release ironic-%{version}

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order sphinx openstackdocstheme pyasn1-lextudio pyasn1-modules-lextudio pysnmp-lextudio

Name:           openstack-ironic
# Liberty semver reset
# https://review.openstack.org/#/q/I1a161b2c1d1e27268065b6b4be24c8f7a5315afb,n,z
Epoch:          1
Summary:        OpenStack Baremetal Hypervisor API (ironic)
Version:        XXX
Release:        XXX
License:        Apache-2.0
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
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  openssl-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  gmp-devel
BuildRequires:  systemd
BuildRequires:  python3-oslo-db-tests
BuildRequires:  python3-pysnmp

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: udev

%{?systemd_ordering}

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n ironic-%{upstream_version} -S git
# Remove tempest plugin entrypoint as a workaround
sed -i '/tempest/d' setup.cfg
rm -rf ironic_tempest_plugin
sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

%generate_buildrequires
%pyproject_buildrequires -t -e %{default_toxenv}

%build
%pyproject_wheel

%install
%pyproject_install

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
export PYTHONPATH="%{buildroot}/%{python3_sitelib}"
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
%tox -e %{default_toxenv}

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

Recommends: ipmitool
Recommends: python3-dracclient >= 5.1.0
Recommends: python3-proliantutils >= 2.10.0
Recommends: python3-pysnmp >= 4.3.0
Recommends: python3-scciclient >= 0.8.0

# Optional features
Suggests: python3-oslo-i18n >= 3.15.3
Suggests: python3-oslo-reports >= 1.18.0

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
%{python3_sitelib}/ironic-*.dist-info
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

%{?systemd_ordering}

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

%{?systemd_ordering}

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
# REMOVEME: error caused by commit https://opendev.org/openstack/ironic/commit/341f80e24dc06a2149aa3ad9730309a57c98283a
