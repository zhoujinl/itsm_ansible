%define name ansible
%define ansible_version $VERSION

Name:      %{name}
Version:   %{ansible_version}
Release:   1%{?dist}
Url:       http://www.ansible.com
Summary:   SSH-based application deployment, configuration management, and IT orchestration platform
License:   GPLv3
Group:     Development/Libraries
Source:    http://releases.ansible.com/ansible/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

BuildArch: noarch


%description

Ansible for ITSM

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --prefix=%{_prefix} --root=%{buildroot}


#mkdir -p %{buildroot}/etc/ansible/
#cp examples/hosts %{buildroot}/etc/ansible/
#cp examples/ansible.cfg %{buildroot}/etc/ansible/
#mkdir -p %{buildroot}/%{_mandir}/man1/
#cp -v docs/man/man1/*.1 %{buildroot}/%{_mandir}/man1/
#mkdir -p %{buildroot}/%{_datadir}/ansible

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{python_sitelib}/ansible*
%{_bindir}/ansible*
%dir %{_datadir}/ansible
%config(noreplace) %{_sysconfdir}/ansible
%doc README.md PKG-INFO COPYING
%doc %{_mandir}/man1/ansible*

%changelog



* 2016-04-28  <ganjl@ffcs.cn> - 0.0.1
- Release of 0.0.1