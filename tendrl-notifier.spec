Name: tendrl-notifier
Version: 1.4.2
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Notifier
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/Notifier

BuildRequires: python-gevent
BuildRequires: pytest
BuildRequires: systemd
BuildRequires: python-mock

Requires: tendrl-commons

%description
Python module for Tendrl Notifier

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
install -m  0755  --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/notifier
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier
install -m  0755  --directory $RPM_BUILD_ROOT%{_datadir}/tendrl/notifier
install -Dm 0644 tendrl-notifier.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-notifier.service
install -Dm 0644 etc/tendrl/notifier.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/notifier.conf.yaml
install -Dm 0644 etc/tendrl/notifier_logging.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/notifier_logging.yaml
install -Dm 0644 etc/tendrl/email.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/email.conf.yaml
install -Dm 0644 etc/tendrl/email_auth.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/email_auth.conf.yaml.sample
install -Dm 644 etc/tendrl/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/notifier/.

%post
systemctl enable tendrl-notifier
%systemd_post tendrl-notifier.service

%preun
%systemd_preun tendrl-notifier.service

%postun
%systemd_postun_with_restart tendrl-notifier.service

%check
py.test -v tendrl/notifier/tests || :

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/notifier
%dir %{_sysconfdir}/tendrl/notifier
%dir %{_datadir}/tendrl/notifier
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/notifier/
%{_sysconfdir}/tendrl/notifier/notifier.conf.yaml
%{_sysconfdir}/tendrl/notifier/notifier_logging.yaml
%{_sysconfdir}/tendrl/notifier/email.conf.yaml
%{_sysconfdir}/tendrl/notifier/email_auth.conf.yaml.sample
%{_unitdir}/tendrl-notifier.service
