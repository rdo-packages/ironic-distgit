%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

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
Group:          System Environment/Base
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

%prep
%setup -q -n ironic-%{upstream_version}
rm requirements.txt test-requirements.txt

%build
%{__python2} setup.py build

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

# Create httpboot and tftpboot dirs for iPXE
mkdir -p %{buildroot}/httpboot
mkdir -p %{buildroot}/tftpboot/pxelinux.cfg

%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common

Requires:   ipmitool
Requires:   python-dracclient
Requires:   python-eventlet
Requires:   python-futurist
Requires:   python-greenlet
Requires:   python-ironic-lib
Requires:   python-iso8601
Requires:   python-posix_ipc
Requires:   python-jsonpatch
Requires:   python-keystonemiddleware
Requires:   python-kombu
Requires:   python-anyjson
Requires:   python-lockfile
Requires:   python-lxml
Requires:   python-migrate
Requires:   python-mock
Requires:   python-netaddr
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
Requires:   python-pecan
Requires:   python-proliantutils
Requires:   python-psutil
Requires:   python-retrying
Requires:   python-six
Requires:   python-stevedore
Requires:   python-webob
Requires:   python-websockify
Requires:   python-wsme
Requires:   pycrypto
Requires:   python-sqlalchemy
Requires:   python-neutronclient
Requires:   python-glanceclient
Requires:   python-keystoneclient
Requires:   python-swiftclient
Requires:   python-jinja2
Requires:   python-pyghmi
Requires:   python-alembic
Requires:   pysendfile
Requires:   python-pbr
Requires:   python-automaton
Requires:   python-requests
Requires:   python-jsonschema
Requires:   pytz


Requires(pre):  shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{python2_sitelib}/ironic*
%exclude %{python2_sitelib}/ironic/tests
%exclude %{python2_sitelib}/ironic_tempest_plugin
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic
%attr(-,ironic,ironic) %{_localstatedir}/log/ironic
%attr(-, root, ironic) %{_datadir}/ironic/ironic-dist.conf
%attr(-,ironic,ironic) /httpboot
%attr(-,ironic,ironic) /tftpboot

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%post common
install -o ironic -g ironic -m 744 /usr/share/ipxe/undionly.kpxe /tftpboot/undionly.kpxe
install -o ironic -g ironic -m 744 /usr/share/syslinux/pxelinux.0 /tftpboot/pxelinux.0
# for newer syslinux versions we may need to copy in the library
# modules as well (Fedora 21 for example)
if [ -f /usr/share/syslinux/ldlinux.* ]; then
    # Fedora/RHEL
    cp /usr/share/syslinux/ldlinux.* /tftpboot
fi
# Copy in the chain loader for full disk image booting.
syslinux='/usr/share/syslinux'
for f in chain.c32 libcom32.c32 libutil.c32; do
    if [ -f $syslinux/$f ]; then
        cp $syslinux/$f /tftpboot
    fi
done
cat > /etc/xinetd.d/tftp << EOF
service tftp
{
    protocol        = udp
    port            = 69
    socket_type     = dgram
    wait            = yes
    user            = root
    server          = /usr/sbin/in.tftpd
    server_args     = --map-file /tftpboot/map-file /tftpboot
    disable         = no
    flags           = IPv4
}
EOF
# Adds support for tftp requests that don't include the directory name.
echo 'r ^([^/]) /tftpboot/\1' > /tftpboot/map-file

%package api
Summary: The Ironic API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

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

Requires: %{name}-common = %{epoch}:%{version}-%{release}

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

%package -n python-ironic-tests
Summary:        Ironic tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

%description -n python-ironic-tests
This package contains the Ironic test files.

%files -n python-ironic-tests
%license LICENSE
%{python2_sitelib}/ironic/tests
%{python2_sitelib}/ironic_tempest_plugin

%changelog
