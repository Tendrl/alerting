Name: tendrl-notifier
Version: 1.6.3
Release: 4%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Notifier
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/Notifier

BuildRequires: pytest
BuildRequires: systemd
BuildRequires: python-mock

Requires: python2-pyasn1 
Requires: python2-crypto >= 2.6.1
Requires: pysnmp
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
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier
install -m  0755  --directory $RPM_BUILD_ROOT%{_datadir}/tendrl/notifier
install -Dm 0644 tendrl-notifier.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-notifier.service
install -Dm 0640 etc/tendrl/notifier.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/notifier.conf.yaml
install -Dm 0640 etc/tendrl/email.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/email.conf.yaml
install -Dm 0640 etc/tendrl/email_auth.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/email_auth.conf.yaml.sample
install -Dm 0640 etc/tendrl/snmp.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/notifier/snmp.conf.yaml
install -Dm 644 etc/tendrl/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/notifier/.

%post
systemctl enable tendrl-notifier >/dev/null 2>&1 || :
%systemd_post tendrl-notifier.service

%preun
%systemd_preun tendrl-notifier.service

%postun
%systemd_postun_with_restart tendrl-notifier.service

%check
py.test -v tendrl/notifier/tests || :

%files -f INSTALLED_FILES
%dir %{_sysconfdir}/tendrl/notifier
%dir %{_datadir}/tendrl/notifier
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/notifier/
%{_unitdir}/tendrl-notifier.service
%config(noreplace) %{_sysconfdir}/tendrl/notifier/email.conf.yaml
%config(noreplace) %{_sysconfdir}/tendrl/notifier/email_auth.conf.yaml.sample
%config(noreplace) %{_sysconfdir}/tendrl/notifier/notifier.conf.yaml
%config(noreplace) %{_sysconfdir}/tendrl/notifier/snmp.conf.yaml

%changelog
* Mon Jun 18 2018 Shubhendu Tripathi <shtripat@redhat.com> - 1.6.3-4
- Bugfixe (https://github.com/Tendrl/notifier/milestone/6)

* Wed May 16 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-3
- Bugfixe https://github.com/Tendrl/notifier/issues/173

* Fri Apr 20 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-2
- Bugfixes (https://github.com/Tendrl/notifier/milestone/4)

* Wed Apr 18 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-1
- Bugfixes

* Sat Feb 17 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.0-1
- Bugfixes

* Fri Feb 02 2018 Rohan Kanade <rkanade@redhat.com> - 1.5.5-1
- Add unit tests

* Thu Nov 30 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-6
- Bugfixes

* Mon Nov 27 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-5
- Supress service enable message during package update

* Fri Nov 24 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-4
- Bugfixes

* Tue Nov 21 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-3
- Bugfixes-2 tendrl-notifier v1.5.4

* Fri Nov 10 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-2
- Bugfixes tendrl-notifier v1.5.4

* Thu Nov 02 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-1
- Release tendrl-notifier v1.5.4

* Thu Oct 12 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.3-1
- Release tendrl-notifier v1.5.3

* Fri Sep 15 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.2-1
- Release tendrl-notifier v1.5.2

* Fri Sep 08 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.1-1
- Release tendrl-notifier v1.5.1
