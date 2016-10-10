#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname		sass
Summary:	PHP bindings to libsass - fast, native Sass parsing in PHP
Name:		%{php_name}-sassphp
Version:	0.2.1
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/sensational/sassphp/archive/v%{version}/sassphp-%{version}.tar.gz
# Source0-md5:	be9ad5c0c0780e64641729540dfee41c
Patch0:		libsass.patch
URL:		https://github.com/sensational/sassphp
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	libsass-devel >= 3.2.2
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%endif
%{?requires_php_extension}
Provides:	php(%{modname}) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The sass extension for PHP gives you an object-oriented system of
parsing Sass from within your PHP applications. Under the hood it uses
libsass to provide super speedy and compatible Sass parsing.

%prep
%setup -q -n sassphp-%{version}
%patch0 -p1

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="spl" \
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
