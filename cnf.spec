Name     : cnf
Version  : 1
Release  : 1051
Source0  : 10-command-not-found.sh
Source1  : commandlist.csv
Source2  : alternatives.csv
Summary  : Bash command not found handler
Group    : Development/Tools
License  : GPL-3.0
Requires : gawk-bin

%description
Shell based command not found handler


%prep

%build

%install
mkdir -p %{buildroot}/usr/share/clear
mkdir -p %{buildroot}/usr/share/defaults/etc/profile.d/

cp %{SOURCE0} %{buildroot}/usr/share/defaults/etc/profile.d/
cp %{SOURCE1} %{buildroot}/usr/share/clear
cp %{SOURCE2} %{buildroot}/usr/share/clear

%check
grep "^m4[[:space:]]" %{SOURCE1}

%files
%defattr(-,root,root,-)
/usr/share/defaults/etc/profile.d/10-command-not-found.sh
/usr/share/clear/commandlist.csv
/usr/share/clear/alternatives.csv

