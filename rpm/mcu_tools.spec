Name:           mcu_tools
Version:        %{?pkg_version}%{!?pkg_version:0.0}
Release:        1%{?dist}
Summary:        Apollo CM MCU tools: sflash firmware loader and clock EEPROM scripts
License:        MIT
URL:            https://github.com/apollo-lhc/mcu_tools
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
Requires:       python3
Requires:       python3-pyserial

# sflash is linked with -s (stripped), so there is nothing for debuginfo
%global debug_package %{nil}
# scripts live in /usr/bin, not site-packages; skip bytecompiling them
%global __brp_python_bytecompile %{nil}

%global py_scripts LoadClkEeprom.py LoadClkConfig_tripletEEPROM.py LoadClock.py LoadClock_rev2.py ReadEEPROM.py SwitchClock.py

%description
Host-side tools for the Apollo Command Module MCU: sflash (UART firmware
loader) and standalone pyserial scripts for loading clock synthesizer
configurations into the clock EEPROM.

%prep
%setup -q

%build
make -C sflash

%install
install -D -m 0755 sflash/sflash %{buildroot}%{_bindir}/sflash
for f in %{py_scripts}; do
    install -D -m 0755 python/$f %{buildroot}%{_bindir}/$f
    sed -i '1s|^#!.*python.*$|#!/usr/bin/python3|' %{buildroot}%{_bindir}/$f
done
# LoadClock*.py fall back to /usr/share/mcu_tools/data when ../data is absent
install -d %{buildroot}%{_datadir}/%{name}/data
install -m 0644 data/*.txt %{buildroot}%{_datadir}/%{name}/data/

%files
%license LICENSE
%doc README.md sflash/README.md
%{_bindir}/sflash
%{_bindir}/LoadClkEeprom.py
%{_bindir}/LoadClkConfig_tripletEEPROM.py
%{_bindir}/LoadClock.py
%{_bindir}/LoadClock_rev2.py
%{_bindir}/ReadEEPROM.py
%{_bindir}/SwitchClock.py
%{_datadir}/%{name}
