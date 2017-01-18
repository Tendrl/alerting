Name: tendrl-alerting
Version: 1.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Alerting
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/alerting

BuildRequires: python-gevent
BuildRequires: pytest
BuildRequires: systemd
BuildRequires: python-mock

Requires: python-etcd
Requires: python-dateutil
Requires: gevent
Requires: python-greenlet
Requires: msgpack-python
Requires: pytz
Requires: flask
Requires: Flask-API

%description
Python module for Tendrl alerting

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m  0755  --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/alerting
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/alerting
install -m  0755  --directory $RPM_BUILD_ROOT%{_datadir}/tendrl/alerting
install -Dm 0644 tendrl-alerting.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-alerting.service
install -Dm 0644 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/tendrl.conf
install -Dm 0644 etc/logging.yaml.timedrotation.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/alerting_logging.yaml
install -Dm 644 etc/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/alerting/.

%post
%systemd_post tendrl-alerting.service

%preun
%systemd_preun tendrl-alerting.service

%postun
%systemd_postun_with_restart tendrl-alerting.service

%check
py.test -v tendrl/alerting/tests || :

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/alerting
%dir %{_sysconfdir}/tendrl/alerting
%dir %{_datadir}/tendrl/alerting
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/alerting/
%{_sysconfdir}/tendrl/tendrl.conf
%{_sysconfdir}/tendrl/alerting_logging.yaml
%{_unitdir}/tendrl-alerting.service

%changelog
* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
