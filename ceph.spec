# vim: set noexpandtab ts=8 sw=8 :
#
# spec file for package ceph
#
# Copyright (C) 2004-2016 The Ceph Project Developers. See COPYING file
# at the top-level directory of this distribution and at
# https://github.com/ceph/ceph/blob/master/COPYING
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon.
#
# This file is under the GNU Lesser General Public License, version 2.1
#
# Please submit bugfixes or comments via http://tracker.ceph.com/
# 
%bcond_with ocf
%bcond_without cephfs_java
%bcond_with tests
%bcond_with xio
%ifnarch s390 s390x
%bcond_without tcmalloc
%else
# no gperftools/tcmalloc on s390(x)
%bcond_with tcmalloc
%endif
%bcond_without libs_compat
%bcond_with lowmem_builder
%if 0%{?fedora} || 0%{?rhel}
%bcond_without selinux
%endif
%if 0%{?suse_version}
%bcond_with selinux
%endif

# LTTng-UST enabled on Fedora, RHEL 6+, and SLE (not openSUSE)
%if 0%{?fedora} || 0%{?rhel} >= 6 || 0%{?suse_version}
%if ! 0%{?is_opensuse}
%bcond_without lttng
%endif
%endif

%if %{with selinux}
# get selinux policy version
%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp 2>/dev/null || echo 0.0.0)}
%endif

%{!?_udevrulesdir: %global _udevrulesdir /lib/udev/rules.d}
%{!?tmpfiles_create: %global tmpfiles_create systemd-tmpfiles --create}

# unify libexec for all targets
%global _libexecdir %{_exec_prefix}/lib


#################################################################################
# common
#################################################################################
Name:		ceph
Version:	10.2.3
Release:	359.gaa7f17f%{?dist}
Epoch:		1
Summary:	User space components of the Ceph file system
License:	LGPL-2.1 and CC-BY-SA-1.0 and GPL-2.0 and BSL-1.0 and GPL-2.0-with-autoconf-exception and BSD-3-Clause and MIT
%if 0%{?suse_version}
Group:         System/Filesystems
%endif
URL:		http://ceph.com/
Source0:	http://ceph.com/download/%{name}-%{version}.tar.bz2
%if 0%{?suse_version}
%if 0%{?is_opensuse}
ExclusiveArch:  x86_64 aarch64 ppc64 ppc64le
%else
ExclusiveArch:  x86_64 aarch64
%endif
%endif
#################################################################################
# dependencies that apply across all distro families
#################################################################################
Requires:       ceph-osd = %{epoch}:%{version}-%{release}
Requires:       ceph-mds = %{epoch}:%{version}-%{release}
Requires:       ceph-mon = %{epoch}:%{version}-%{release}
Requires(post):	binutils
%if 0%{with cephfs_java}
BuildRequires:	java-devel
BuildRequires:	sharutils
%endif
%if 0%{with selinux}
BuildRequires:	checkpolicy
BuildRequires:	selinux-policy-devel
BuildRequires:	/usr/share/selinux/devel/policyhelp
%endif
BuildRequires:	boost-devel
BuildRequires:  cmake
BuildRequires:	cryptsetup
BuildRequires:	fuse-devel
BuildRequires:	gcc-c++
BuildRequires:	gdbm
%if 0%{with tcmalloc}
BuildRequires:	gperftools-devel
%endif
BuildRequires:	hdparm
BuildRequires:	leveldb-devel > 1.2
BuildRequires:	libaio-devel
BuildRequires:	libatomic_ops-devel
BuildRequires:	libblkid-devel >= 2.17
BuildRequires:	libcurl-devel
BuildRequires:	libudev-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	make
BuildRequires:	parted
BuildRequires:	perl
BuildRequires:	pkgconfig
BuildRequires:	python
BuildRequires:	python-devel
BuildRequires:	python-nose
BuildRequires:	python-requests
BuildRequires:	python-sphinx
BuildRequires:	python-virtualenv
BuildRequires:	snappy-devel
BuildRequires:	udev
BuildRequires:	util-linux
BuildRequires:	valgrind-devel
BuildRequires:	xfsprogs
BuildRequires:	xfsprogs-devel
BuildRequires:	xmlstarlet
BuildRequires:	yasm

#################################################################################
# distro-conditional dependencies
#################################################################################
%if 0%{?suse_version}
BuildRequires:  pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
BuildRequires:	systemd
%{?systemd_requires}
PreReq:		%fillup_prereq
BuildRequires:	net-tools
BuildRequires:	libbz2-devel
BuildRequires:  btrfsprogs
BuildRequires:	mozilla-nss-devel
BuildRequires:	keyutils-devel
BuildRequires:  libopenssl-devel
BuildRequires:  lsb-release
BuildRequires:  openldap2-devel
BuildRequires:	python-Cython
%endif
%if 0%{?fedora} || 0%{?rhel} 
Requires:	systemd
BuildRequires:  boost-random
BuildRequires:	btrfs-progs
BuildRequires:	nss-devel
BuildRequires:	keyutils-libs-devel
BuildRequires:  openldap-devel
BuildRequires:  openssl-devel
BuildRequires:  redhat-lsb-core
BuildRequires:	Cython
%endif
# lttng and babeltrace for rbd-replay-prep
%if %{with lttng}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	lttng-ust-devel
BuildRequires:	libbabeltrace-devel
%endif
%if 0%{?suse_version}
BuildRequires:	lttng-ust-devel
BuildRequires:  babeltrace-devel
%endif
%endif
# expat and fastcgi for RGW
%if 0%{?suse_version}
BuildRequires:	libexpat-devel
BuildRequires:	FastCGI-devel
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	expat-devel
BuildRequires:	fcgi-devel
%endif
#hardened-cc1
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:  redhat-rpm-config
%endif
# Accelio IB/RDMA
%if 0%{with xio}
BuildRequires:  libxio-devel
%endif

%description
Ceph is a massively scalable, open-source, distributed storage system that runs
on commodity hardware and delivers object, block and file system storage.


#################################################################################
# packages
#################################################################################
%package base
Summary:       Ceph Base Package
Group:         System Environment/Base
Requires:      ceph-common = %{epoch}:%{version}-%{release}
Requires:      librbd1 = %{epoch}:%{version}-%{release}
Requires:      librados2 = %{epoch}:%{version}-%{release}
Requires:      libcephfs1 = %{epoch}:%{version}-%{release}
Requires:      librgw2 = %{epoch}:%{version}-%{release}
%if 0%{with selinux}
Requires:      ceph-selinux = %{epoch}:%{version}-%{release}
%endif
Requires:      python
Requires:      python-requests
Requires:      python-setuptools
Requires:      grep
Requires:      xfsprogs
Requires:      logrotate
Requires:      util-linux
Requires:      hdparm
Requires:      cryptsetup
Requires:      findutils
Requires:      which
%if 0%{?suse_version}
Requires:      lsb-release
Recommends:    ntp-daemon
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:      redhat-lsb-core
%endif
%if 0%{with xio}
Requires:      libxio
%endif
%description base
Base is the package that includes all the files shared amongst ceph servers

%package -n ceph-common
Summary:	Ceph Common
Group:		System Environment/Base
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Requires:	python-rbd = %{epoch}:%{version}-%{release}
Requires:	python-cephfs = %{epoch}:%{version}-%{release}
Requires:	python-requests
%{?systemd_requires}
%if 0%{?suse_version}
Requires(pre):	pwdutils
%endif
%if 0%{with xio}
Requires:       libxio
%endif
%description -n ceph-common
Common utilities to mount and interact with a ceph storage cluster.
Comprised of files that are common to Ceph clients and servers.

%package mds
Summary:	Ceph Metadata Server Daemon
Group:		System Environment/Base
Requires:	ceph-base = %{epoch}:%{version}-%{release}
%description mds
ceph-mds is the metadata server daemon for the Ceph distributed file system.
One or more instances of ceph-mds collectively manage the file system
namespace, coordinating access to the shared OSD cluster.

%package mon
Summary:	Ceph Monitor Daemon
Group:		System Environment/Base
Requires:	ceph-base = %{epoch}:%{version}-%{release}
# For ceph-rest-api
%if 0%{?fedora} || 0%{?rhel}
Requires:      python-flask
%endif
%if 0%{?suse_version}
Requires:      python-Flask
%endif
%description mon
ceph-mon is the cluster monitor daemon for the Ceph distributed file
system. One or more instances of ceph-mon form a Paxos part-time
parliament cluster that provides extremely reliable and durable storage
of cluster membership, configuration, and state.

%package fuse
Summary:	Ceph fuse-based client
Group:		System Environment/Base
%description fuse
FUSE based client for Ceph distributed network file system

%package -n rbd-fuse
Summary:	Ceph fuse-based client
Group:		System Environment/Base
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librbd1 = %{epoch}:%{version}-%{release}
%description -n rbd-fuse
FUSE based client to map Ceph rbd images to files

%package -n rbd-mirror
Summary:	Ceph daemon for mirroring RBD images
Group:		System Environment/Base
Requires:	ceph-common = %{epoch}:%{version}-%{release}
Requires:	librados2 = %{epoch}:%{version}-%{release}
%description -n rbd-mirror
Daemon for mirroring RBD images between Ceph clusters, streaming
changes asynchronously.

%package -n rbd-nbd
Summary:	Ceph RBD client base on NBD
Group:		System Environment/Base
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librbd1 = %{epoch}:%{version}-%{release}
%description -n rbd-nbd
NBD based client to map Ceph rbd images to local device

%package radosgw
Summary:	Rados REST gateway
Group:		Development/Libraries
Requires:	ceph-common = %{epoch}:%{version}-%{release}
%if 0%{with selinux}
Requires:	ceph-selinux = %{epoch}:%{version}-%{release}
%endif
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librgw2 = %{epoch}:%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Requires:	mailcap
# python-flask for powerdns
Requires:	python-flask
%endif
%if 0%{?suse_version}
# python-Flask for powerdns
Requires:      python-Flask
%endif
%description radosgw
RADOS is a distributed object store used by the Ceph distributed
storage system.  This package provides a REST gateway to the
object store that aims to implement a superset of Amazon's S3
service as well as the OpenStack Object Storage ("Swift") API.

%if %{with ocf}
%package resource-agents
Summary:	OCF-compliant resource agents for Ceph daemons
Group:		System Environment/Base
License:	LGPL-2.0
Requires:	ceph-base = %{epoch}:%{version}
Requires:	resource-agents
%description resource-agents
Resource agents for monitoring and managing Ceph daemons
under Open Cluster Framework (OCF) compliant resource
managers such as Pacemaker.
%endif

%package osd
Summary:	Ceph Object Storage Daemon
Group:		System Environment/Base
Requires:	ceph-base = %{epoch}:%{version}-%{release}
# for sgdisk, used by ceph-disk
%if 0%{?fedora} || 0%{?rhel}
Requires:	gdisk
%endif
%if 0%{?suse_version}
Requires:	gptfdisk
%endif
Requires:       parted
%description osd
ceph-osd is the object storage daemon for the Ceph distributed file
system.  It is responsible for storing objects on a local file system
and providing access to them over the network.

%package -n librados2
Summary:	RADOS distributed object store client library
Group:		System Environment/Libraries
License:	LGPL-2.0
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
%endif
%description -n librados2
RADOS is a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to access the distributed object
store using a simple file-like interface.

%package -n librados2-devel
Summary:	RADOS headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n librados2-devel
This package contains libraries and headers needed to develop programs
that use RADOS object store.

%package -n librgw2
Summary:	RADOS gateway client library
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%description -n librgw2
This package provides a library implementation of the RADOS gateway
(distributed object store with S3 and Swift personalities).

%package -n librgw2-devel
Summary:	RADOS gateway client library
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%description -n librgw2-devel
This package contains libraries and headers needed to develop programs
that use RADOS gateway client library.

%package -n python-rados
Summary:	Python libraries for the RADOS object store
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-rados
This package contains Python libraries for interacting with Cephs RADOS
object store.

%package -n libradosstriper1
Summary:	RADOS striping interface
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%description -n libradosstriper1
Striping interface built on top of the rados library, allowing
to stripe bigger objects onto several standard rados objects using
an interface very similar to the rados one.

%package -n libradosstriper1-devel
Summary:	RADOS striping interface headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	libradosstriper1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libradosstriper1-devel
This package contains libraries and headers needed to develop programs
that use RADOS striping interface.

%package -n librbd1
Summary:	RADOS block device client library
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
%endif
%description -n librbd1
RBD is a block device striped across multiple distributed objects in
RADOS, a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to manage these block devices.

%package -n librbd1-devel
Summary:	RADOS block device headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n librbd1-devel
This package contains libraries and headers needed to develop programs
that use RADOS block device.

%package -n python-rbd
Summary:	Python libraries for the RADOS block device
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-rbd
This package contains Python libraries for interacting with Cephs RADOS
block device.

%package -n libcephfs1
Summary:	Ceph distributed file system client library
Group:		System Environment/Libraries
License:	LGPL-2.0
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
Obsoletes:	ceph-libcephfs
%endif
%description -n libcephfs1
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability. This is a shared library
allowing applications to access a Ceph distributed file system via a
POSIX-like interface.

%package -n libcephfs1-devel
Summary:	Ceph distributed file system headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libcephfs1-devel
This package contains libraries and headers needed to develop programs
that use Cephs distributed file system.

%package -n python-cephfs
Summary:	Python libraries for Ceph distributed file system
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-cephfs
This package contains Python libraries for interacting with Cephs distributed
file system.

%package -n ceph-test
Summary:	Ceph benchmarks and test tools
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	ceph-common
Requires:	xmlstarlet
%description -n ceph-test
This package contains Ceph benchmarks and test tools.

%if 0%{with cephfs_java}

%package -n libcephfs_jni1
Summary:	Java Native Interface library for CephFS Java bindings
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
%description -n libcephfs_jni1
This package contains the Java Native Interface library for CephFS Java
bindings.

%package -n libcephfs_jni1-devel
Summary:	Development files for CephFS Java Native Interface library
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs_jni1 = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libcephfs_jni1-devel
This package contains the development files for CephFS Java Native Interface
library.

%package -n cephfs-java
Summary:	Java libraries for the Ceph File System
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs_jni1 = %{epoch}:%{version}-%{release}
Requires:       junit
BuildRequires:  junit
%description -n cephfs-java
This package contains the Java libraries for the Ceph File System.

%endif

%if 0%{with selinux}

%package selinux
Summary:	SELinux support for Ceph MON, OSD and MDS
Group:		System Environment/Base
Requires:	ceph-base = %{epoch}:%{version}-%{release}
Requires:	policycoreutils, libselinux-utils
Requires(post): selinux-policy-base >= %{_selinux_policy_version}, policycoreutils, gawk
Requires(postun): policycoreutils
%description selinux
This package contains SELinux support for Ceph MON, OSD and MDS. The package
also performs file-system relabelling which can take a long time on heavily
populated file-systems.

%endif

%if 0%{with libs_compat}

%package libs-compat
Summary:	Meta package to include ceph libraries
Group:		System Environment/Libraries
License:	LGPL-2.0
Obsoletes:	ceph-libs
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Provides:	ceph-libs

%description libs-compat
This is a meta package, that pulls in librados2, librbd1 and libcephfs1. It
is included for backwards compatibility with distributions that depend on the
former ceph-libs package, which is now split up into these three subpackages.
Packages still depending on ceph-libs should be fixed to depend on librados2,
librbd1 or libcephfs1 instead.

%endif

%package devel-compat
Summary:	Compatibility package for Ceph headers
Group:		Development/Libraries
License:	LGPL-2.0
Obsoletes:	ceph-devel
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Requires:	libradosstriper1-devel = %{epoch}:%{version}-%{release}
Requires:	librbd1-devel = %{epoch}:%{version}-%{release}
Requires:	libcephfs1-devel = %{epoch}:%{version}-%{release}
%if 0%{with cephfs_java}
Requires:	libcephfs_jni1-devel = %{epoch}:%{version}-%{release}
%endif
Provides:	ceph-devel
%description devel-compat
This is a compatibility package to accommodate ceph-devel split into
librados2-devel, librbd1-devel and libcephfs1-devel. Packages still depending
on ceph-devel should be fixed to depend on librados2-devel, librbd1-devel,
libcephfs1-devel or libradosstriper1-devel instead.

%package -n python-ceph-compat
Summary:	Compatibility package for Cephs python libraries
Group:		System Environment/Libraries
License:	LGPL-2.0
Obsoletes:	python-ceph
Requires:	python-rados = %{epoch}:%{version}-%{release}
Requires:	python-rbd = %{epoch}:%{version}-%{release}
Requires:	python-cephfs = %{epoch}:%{version}-%{release}
Provides:	python-ceph
%description -n python-ceph-compat
This is a compatibility package to accommodate python-ceph split into
python-rados, python-rbd and python-cephfs. Packages still depending on
python-ceph should be fixed to depend on python-rados, python-rbd or
python-cephfs instead.

#################################################################################
# common
#################################################################################
%prep
%setup -q

%build
%if 0%{with cephfs_java}
# Find jni.h
for i in /usr/{lib64,lib}/jvm/java/include{,/linux}; do
    [ -d $i ] && java_inc="$java_inc -I$i"
done
%endif

./autogen.sh

%if %{with lowmem_builder}
RPM_OPT_FLAGS="$RPM_OPT_FLAGS --param ggc-min-expand=20 --param ggc-min-heapsize=32768"
%endif
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/i386/i486/'`

%{configure}	CPPFLAGS="$java_inc" \
		--prefix=/usr \
                --libexecdir=%{_libexecdir} \
		--localstatedir=%{_localstatedir} \
		--sysconfdir=%{_sysconfdir} \
%if 0%{?rhel} && ! 0%{?centos}
                --enable-subman \
%endif
		--with-systemdsystemunitdir=%_unitdir \
		--docdir=%{_docdir}/ceph \
		--with-man-pages \
		--mandir="%_mandir" \
		--with-nss \
		--without-cryptopp \
		--with-debug \
%if 0%{with cephfs_java}
		--enable-cephfs-java \
%endif
%if 0%{with xio}
		--enable-xio \
%endif
%if 0%{with selinux}
		--with-selinux \
%endif
		--with-librocksdb-static=check \
		--with-radosgw \
%if %{without lttng}
		--without-lttng \
		--without-babeltrace \
%endif
		$CEPH_EXTRA_CONFIGURE_ARGS \
		%{?_with_ocf} \
%if %{without tcmalloc}
		--without-tcmalloc \
%endif
		CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS"

%if %{with lowmem_builder}
%if 0%{?jobs} > 8
%define _smp_mflags -j8
%endif
%endif

make %{?_smp_mflags}


%if 0%{with tests}
%check
# run in-tree unittests
make %{?_smp_mflags} check

%endif



%install
make DESTDIR=%{buildroot} install
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'
find %{buildroot} -type f -name "*.a" -exec rm -f {} ';'
install -D src/etc-rbdmap %{buildroot}%{_sysconfdir}/ceph/rbdmap
%if 0%{?fedora} || 0%{?rhel}
install -m 0644 -D etc/sysconfig/ceph %{buildroot}%{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
install -m 0644 -D etc/sysconfig/ceph %{buildroot}%{_localstatedir}/adm/fillup-templates/sysconfig.%{name}
%endif
install -m 0644 -D systemd/ceph.tmpfiles.d %{buildroot}%{_tmpfilesdir}/ceph-common.conf
install -m 0755 -D systemd/ceph %{buildroot}%{_sbindir}/rcceph
install -m 0644 -D systemd/50-ceph.preset %{buildroot}%{_libexecdir}/systemd/system-preset/50-ceph.preset
mkdir -p %{buildroot}%{_sbindir}
install -m 0644 -D src/logrotate.conf %{buildroot}%{_sysconfdir}/logrotate.d/ceph
chmod 0644 %{buildroot}%{_docdir}/ceph/sample.ceph.conf
chmod 0644 %{buildroot}%{_docdir}/ceph/sample.fetch_config

# firewall templates and /sbin/mount.ceph symlink
%if 0%{?suse_version}
install -m 0644 -D etc/sysconfig/SuSEfirewall2.d/services/ceph-mon %{buildroot}%{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-mon
install -m 0644 -D etc/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds %{buildroot}%{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds
mkdir -p %{buildroot}/sbin
ln -sf %{_sbindir}/mount.ceph %{buildroot}/sbin/mount.ceph
%endif

# udev rules
install -m 0644 -D udev/50-rbd.rules %{buildroot}%{_udevrulesdir}/50-rbd.rules
install -m 0644 -D udev/60-ceph-by-parttypeuuid.rules %{buildroot}%{_udevrulesdir}/60-ceph-by-parttypeuuid.rules
install -m 0644 -D udev/95-ceph-osd.rules %{buildroot}%{_udevrulesdir}/95-ceph-osd.rules

#set up placeholder directories
mkdir -p %{buildroot}%{_sysconfdir}/ceph
mkdir -p %{buildroot}%{_localstatedir}/run/ceph
mkdir -p %{buildroot}%{_localstatedir}/log/ceph
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/tmp
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/mon
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/osd
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/mds
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/radosgw
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-osd
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-mds
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-rgw

%clean
rm -rf %{buildroot}

#################################################################################
# files and systemd scriptlets
#################################################################################
%files

%files base
%defattr(-,root,root,-)
%docdir %{_docdir}
%dir %{_docdir}/ceph
%{_docdir}/ceph/sample.ceph.conf
%{_docdir}/ceph/sample.fetch_config
%{_bindir}/crushtool
%{_bindir}/monmaptool
%{_bindir}/osdmaptool
%{_bindir}/ceph-run
%{_bindir}/ceph-detect-init
%{_bindir}/ceph-client-debug
%{_bindir}/cephfs
%{_unitdir}/ceph-create-keys@.service
%{_libexecdir}/systemd/system-preset/50-ceph.preset
%{_sbindir}/ceph-create-keys
%{_sbindir}/rcceph
%dir %{_libexecdir}/ceph
%{_libexecdir}/ceph/ceph_common.sh
%dir %{_libdir}/rados-classes
%{_libdir}/rados-classes/*
%dir %{_libdir}/ceph
%dir %{_libdir}/ceph/erasure-code
%{_libdir}/ceph/erasure-code/libec_*.so*
%dir %{_libdir}/ceph/compressor
%{_libdir}/ceph/compressor/libceph_*.so*
%if %{with lttng}
%{_libdir}/libos_tp.so*
%{_libdir}/libosd_tp.so*
%endif
%config %{_sysconfdir}/bash_completion.d/ceph
%config(noreplace) %{_sysconfdir}/logrotate.d/ceph
%if 0%{?fedora} || 0%{?rhel}
%config(noreplace) %{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
%{_localstatedir}/adm/fillup-templates/sysconfig.*
%config %{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-mon
%config %{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds
%endif
%{_unitdir}/ceph.target
%{python_sitelib}/ceph_detect_init*
%{python_sitelib}/ceph_disk*
%{_mandir}/man8/ceph-deploy.8*
%{_mandir}/man8/ceph-detect-init.8*
%{_mandir}/man8/ceph-create-keys.8*
%{_mandir}/man8/ceph-run.8*
%{_mandir}/man8/crushtool.8*
%{_mandir}/man8/osdmaptool.8*
%{_mandir}/man8/monmaptool.8*
%{_mandir}/man8/cephfs.8*
#set up placeholder directories
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/tmp
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-osd
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-mds
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-rgw

%post base
/sbin/ldconfig
%if 0%{?suse_version}
%fillup_only
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph.target
%endif
/usr/bin/systemctl start ceph.target >/dev/null 2>&1 || :

%preun base
%if 0%{?suse_version}
%service_del_preun ceph.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph.target
%endif

%postun base
/sbin/ldconfig
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph.target
%endif

#################################################################################
%files common
%defattr(-,root,root,-)
%{_bindir}/ceph
%{_bindir}/ceph-authtool
%{_bindir}/ceph-conf
%{_bindir}/ceph-dencoder
%{_bindir}/ceph-rbdnamer
%{_bindir}/ceph-syn
%{_bindir}/ceph-crush-location
%{_bindir}/cephfs-data-scan
%{_bindir}/cephfs-journal-tool
%{_bindir}/cephfs-table-tool
%{_bindir}/rados
%{_bindir}/rbd
%{_bindir}/rbd-replay
%{_bindir}/rbd-replay-many
%{_bindir}/rbdmap
%{_sbindir}/mount.ceph
%if 0%{?suse_version}
/sbin/mount.ceph
%endif
%if %{with lttng}
%{_bindir}/rbd-replay-prep
%endif
%{_bindir}/ceph-post-file
%{_bindir}/ceph-brag
%{_tmpfilesdir}/ceph-common.conf
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/ceph-post-file.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/rbdmap.8*
%{_mandir}/man8/rbd-replay.8*
%{_mandir}/man8/rbd-replay-many.8*
%{_mandir}/man8/rbd-replay-prep.8*
%dir %{_datadir}/ceph/
%{_datadir}/ceph/known_hosts_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com.pub
%dir %{_sysconfdir}/ceph/
%config %{_sysconfdir}/bash_completion.d/rados
%config %{_sysconfdir}/bash_completion.d/rbd
%config(noreplace) %{_sysconfdir}/ceph/rbdmap
%{_unitdir}/rbdmap.service
%{python_sitelib}/ceph_argparse.py*
%{python_sitelib}/ceph_daemon.py*
%dir %{_udevrulesdir}
%{_udevrulesdir}/50-rbd.rules
%attr(3770,ceph,ceph) %dir %{_localstatedir}/log/ceph/
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/

%pre common
CEPH_GROUP_ID=167
CEPH_USER_ID=167
%if 0%{?rhel} || 0%{?fedora}
/usr/sbin/groupadd ceph -g $CEPH_GROUP_ID -o -r 2>/dev/null || :
/usr/sbin/useradd ceph -u $CEPH_USER_ID -o -r -g ceph -s /sbin/nologin -c "Ceph daemons" -d %{_localstatedir}/lib/ceph 2>/dev/null || :
%endif
%if 0%{?suse_version}
if ! getent group ceph >/dev/null ; then
    CEPH_GROUP_ID_OPTION=""
    getent group $CEPH_GROUP_ID >/dev/null || CEPH_GROUP_ID_OPTION="-g $CEPH_GROUP_ID"
    groupadd ceph $CEPH_GROUP_ID_OPTION -r 2>/dev/null || :
fi
if ! getent passwd ceph >/dev/null ; then
    CEPH_USER_ID_OPTION=""
    getent passwd $CEPH_USER_ID >/dev/null || CEPH_USER_ID_OPTION="-u $CEPH_USER_ID"
    useradd ceph $CEPH_USER_ID_OPTION -r -g ceph -s /sbin/nologin 2>/dev/null || :
fi
usermod -c "Ceph storage service" \
        -d %{_localstatedir}/lib/ceph \   
        -g ceph \
        -s /sbin/nologin \
        ceph
%endif
exit 0

%post common
%tmpfiles_create %{_tmpfilesdir}/ceph-common.conf

%postun common
# Package removal cleanup
if [ "$1" -eq "0" ] ; then
    rm -rf %{_localstatedir}/log/ceph
    rm -rf %{_sysconfdir}/ceph
fi

#################################################################################
%files mds
%{_bindir}/ceph-mds
%{_mandir}/man8/ceph-mds.8*
%{_unitdir}/ceph-mds@.service
%{_unitdir}/ceph-mds.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mds

%post mds
%if 0%{?suse_version}
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph-mds@\*.service ceph-mds.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-mds@\*.service ceph-mds.target
%endif
/usr/bin/systemctl start ceph-mds.target >/dev/null 2>&1 || :

%preun mds
%if 0%{?suse_version}
%service_del_preun ceph-mds@\*.service ceph-mds.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-mds@\*.service ceph-mds.target
%endif

%postun mds
test -n "$FIRST_ARG" || FIRST_ARG=$1
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph-mds@\*.service ceph-mds.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph-mds@\*.service ceph-mds.target
%endif
if [ $FIRST_ARG -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-mds@\*.service > /dev/null 2>&1 || :
  fi
fi

#################################################################################
%files mon
%{_bindir}/ceph-mon
%{_bindir}/ceph-rest-api
%{_mandir}/man8/ceph-mon.8*
%{_mandir}/man8/ceph-rest-api.8*
%{python_sitelib}/ceph_rest_api.py*
%{_unitdir}/ceph-mon@.service
%{_unitdir}/ceph-mon.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mon

%post mon
%if 0%{?suse_version}
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target
%endif
/usr/bin/systemctl start ceph-mon.target >/dev/null 2>&1 || :

%preun mon
%if 0%{?suse_version}
%service_del_preun ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target
%endif

%postun mon
test -n "$FIRST_ARG" || FIRST_ARG=$1
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph-create-keys@\*.service ceph-mon@\*.service ceph-mon.target
%endif
if [ $FIRST_ARG -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-create-keys@\*.service ceph-mon@\*.service > /dev/null 2>&1 || :
  fi
fi

#################################################################################
%files fuse
%defattr(-,root,root,-)
%{_bindir}/ceph-fuse
%{_mandir}/man8/ceph-fuse.8*
%{_sbindir}/mount.fuse.ceph

#################################################################################
%files -n rbd-fuse
%defattr(-,root,root,-)
%{_bindir}/rbd-fuse
%{_mandir}/man8/rbd-fuse.8*

#################################################################################
%files -n rbd-mirror
%defattr(-,root,root,-)
%{_bindir}/rbd-mirror
%{_mandir}/man8/rbd-mirror.8*
%{_unitdir}/ceph-rbd-mirror@.service
%{_unitdir}/ceph-rbd-mirror.target

%post -n rbd-mirror
%if 0%{?suse_version}
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph-rbd-mirror@\*.service ceph-rbd-mirror.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
/usr/bin/systemctl start ceph-rbd-mirror.target >/dev/null 2>&1 || :

%preun -n rbd-mirror
%if 0%{?suse_version}
%service_del_preun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif

%postun -n rbd-mirror
test -n "$FIRST_ARG" || FIRST_ARG=$1
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
if [ $FIRST_ARG -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-rbd-mirror@\*.service > /dev/null 2>&1 || :
  fi
fi

#################################################################################
%files -n rbd-nbd
%defattr(-,root,root,-)
%{_bindir}/rbd-nbd
%{_mandir}/man8/rbd-nbd.8*

#################################################################################
%files radosgw
%defattr(-,root,root,-)
%{_bindir}/radosgw
%{_bindir}/radosgw-admin
%{_bindir}/radosgw-token
%{_bindir}/radosgw-object-expirer
%{_mandir}/man8/radosgw.8*
%{_mandir}/man8/radosgw-admin.8*
%config %{_sysconfdir}/bash_completion.d/radosgw-admin
%dir %{_localstatedir}/lib/ceph/radosgw
%{_unitdir}/ceph-radosgw@.service
%{_unitdir}/ceph-radosgw.target

%post radosgw
%if 0%{?suse_version}
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph-radosgw@\*.service ceph-radosgw.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-radosgw@\*.service ceph-radosgw.target
%endif
/usr/bin/systemctl start ceph-radosgw.target >/dev/null 2>&1 || :

%preun radosgw
%if 0%{?suse_version}
%service_del_preun ceph-radosgw@\*.service ceph-radosgw.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-radosgw@\*.service ceph-radosgw.target
%endif

%postun radosgw
test -n "$FIRST_ARG" || FIRST_ARG=$1
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph-radosgw@\*.service ceph-radosgw.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph-radosgw@\*.service ceph-radosgw.target
%endif
if [ $FIRST_ARG -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-radosgw@\*.service > /dev/null 2>&1 || :
  fi
fi

#################################################################################
%files osd
%{_bindir}/ceph-clsinfo
%{_bindir}/ceph-bluefs-tool
%{_bindir}/ceph-objectstore-tool
%{_bindir}/ceph-osd
%{_sbindir}/ceph-disk
%{_sbindir}/ceph-disk-udev
%{_libexecdir}/ceph/ceph-osd-prestart.sh
%dir %{_udevrulesdir}
%{_udevrulesdir}/60-ceph-by-parttypeuuid.rules
%{_udevrulesdir}/95-ceph-osd.rules
%{_mandir}/man8/ceph-clsinfo.8*
%{_mandir}/man8/ceph-disk.8*
%{_mandir}/man8/ceph-osd.8*
%if 0%{?rhel} && ! 0%{?centos}
%{_sysconfdir}/cron.hourly/subman
%endif
%{_unitdir}/ceph-osd@.service
%{_unitdir}/ceph-osd.target
%{_unitdir}/ceph-disk@.service
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/osd

%post osd
%if 0%{?suse_version}
if [ $1 -ge 1 ] ; then
  /usr/bin/systemctl preset ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target
%endif
/usr/bin/systemctl start ceph-osd.target >/dev/null 2>&1 || :

%preun osd
%if 0%{?suse_version}
%service_del_preun ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target
%endif

%postun osd
test -n "$FIRST_ARG" || FIRST_ARG=$1
%if 0%{?suse_version}
DISABLE_RESTART_ON_UPDATE="yes"
%service_del_postun ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_postun ceph-disk@\*.service ceph-osd@\*.service ceph-osd.target
%endif
if [ $FIRST_ARG -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-disk@\*.service ceph-osd@\*.service > /dev/null 2>&1 || :
  fi
fi

#################################################################################
%if %{with ocf}

%files resource-agents
%defattr(0755,root,root,-)
# N.B. src/ocf/Makefile.am uses $(prefix)/lib
%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/resource.d
%dir %{_prefix}/lib/ocf/resource.d/ceph
%{_prefix}/lib/ocf/resource.d/ceph/rbd

%endif

#################################################################################
%files -n librados2
%defattr(-,root,root,-)
%{_libdir}/librados.so.*
%if %{with lttng}
%{_libdir}/librados_tp.so.*
%endif

%post -n librados2
/sbin/ldconfig

%postun -n librados2
/sbin/ldconfig

#################################################################################
%files -n librados2-devel
%defattr(-,root,root,-)
%dir %{_includedir}/rados
%{_includedir}/rados/librados.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/buffer.h
%{_includedir}/rados/buffer_fwd.h
%{_includedir}/rados/page.h
%{_includedir}/rados/crc32c.h
%{_includedir}/rados/rados_types.h
%{_includedir}/rados/rados_types.hpp
%{_includedir}/rados/memory.h
%{_libdir}/librados.so
%if %{with lttng}
%{_libdir}/librados_tp.so
%endif
%{_bindir}/librados-config
%{_mandir}/man8/librados-config.8*

#################################################################################
%files -n python-rados
%defattr(-,root,root,-)
%{python_sitearch}/rados.so
%{python_sitearch}/rados-*.egg-info

#################################################################################
%files -n libradosstriper1
%defattr(-,root,root,-)
%{_libdir}/libradosstriper.so.*

%post -n libradosstriper1
/sbin/ldconfig

%postun -n libradosstriper1
/sbin/ldconfig

#################################################################################
%files -n libradosstriper1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/radosstriper
%{_includedir}/radosstriper/libradosstriper.h
%{_includedir}/radosstriper/libradosstriper.hpp
%{_libdir}/libradosstriper.so

#################################################################################
%files -n librbd1
%defattr(-,root,root,-)
%{_libdir}/librbd.so.*
%if %{with lttng}
%{_libdir}/librbd_tp.so.*
%endif

%post -n librbd1
/sbin/ldconfig
mkdir -p /usr/lib64/qemu/
ln -sf %{_libdir}/librbd.so.1 /usr/lib64/qemu/librbd.so.1

%postun -n librbd1
/sbin/ldconfig

#################################################################################
%files -n librbd1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/rbd
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/librbd.so
%if %{with lttng}
%{_libdir}/librbd_tp.so
%endif

#################################################################################
%files -n librgw2
%defattr(-,root,root,-)
%{_libdir}/librgw.so.*

%post -n librgw2
/sbin/ldconfig

%postun -n librgw2
/sbin/ldconfig

#################################################################################
%files -n librgw2-devel
%defattr(-,root,root,-)
%dir %{_includedir}/rados
%{_includedir}/rados/librgw.h
%{_includedir}/rados/rgw_file.h
%{_libdir}/librgw.so

#################################################################################
%files -n python-rbd
%defattr(-,root,root,-)
%{python_sitearch}/rbd.so
%{python_sitearch}/rbd-*.egg-info

#################################################################################
%files -n libcephfs1
%defattr(-,root,root,-)
%{_libdir}/libcephfs.so.*

%post -n libcephfs1
/sbin/ldconfig

%postun -n libcephfs1
/sbin/ldconfig

#################################################################################
%files -n libcephfs1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/cephfs
%{_includedir}/cephfs/libcephfs.h
%{_libdir}/libcephfs.so

#################################################################################
%files -n python-cephfs
%defattr(-,root,root,-)
%{python_sitearch}/cephfs.so
%{python_sitearch}/cephfs-*.egg-info
%{python_sitelib}/ceph_volume_client.py*

#################################################################################
%files -n ceph-test
%defattr(-,root,root,-)
%{_bindir}/ceph_bench_log
%{_bindir}/ceph_kvstorebench
%{_bindir}/ceph_multi_stress_watch
%{_bindir}/ceph_erasure_code
%{_bindir}/ceph_erasure_code_benchmark
%{_bindir}/ceph_omapbench
%{_bindir}/ceph_objectstore_bench
%{_bindir}/ceph_perf_objectstore
%{_bindir}/ceph_perf_local
%{_bindir}/ceph_perf_msgr_client
%{_bindir}/ceph_perf_msgr_server
%{_bindir}/ceph_psim
%{_bindir}/ceph_radosacl
%{_bindir}/ceph_rgw_jsonparser
%{_bindir}/ceph_rgw_multiparser
%{_bindir}/ceph_scratchtool
%{_bindir}/ceph_scratchtoolpp
%{_bindir}/ceph_smalliobench
%{_bindir}/ceph_smalliobenchdumb
%{_bindir}/ceph_smalliobenchfs
%{_bindir}/ceph_smalliobenchrbd
%{_bindir}/ceph_test_*
%{_bindir}/librgw_file*
%{_bindir}/ceph_tpbench
%{_bindir}/ceph_xattr_bench
%{_bindir}/ceph-coverage
%{_bindir}/ceph-monstore-tool
%{_bindir}/ceph-osdomap-tool
%{_bindir}/ceph-kvstore-tool
%{_bindir}/ceph-debugpack
%{_mandir}/man8/ceph-debugpack.8*
%dir %{_libdir}/ceph
%{_libdir}/ceph/ceph-monstore-update-crush.sh

#################################################################################
%if 0%{with cephfs_java}
%files -n libcephfs_jni1
%defattr(-,root,root,-)
%{_libdir}/libcephfs_jni.so.*

%post -n libcephfs_jni1
/sbin/ldconfig

%postun -n libcephfs_jni1
/sbin/ldconfig

#################################################################################
%files -n libcephfs_jni1-devel
%defattr(-,root,root,-)
%{_libdir}/libcephfs_jni.so

#################################################################################
%files -n cephfs-java
%defattr(-,root,root,-)
%{_javadir}/libcephfs.jar
%{_javadir}/libcephfs-test.jar
%endif

#################################################################################
%if 0%{with selinux}
%files selinux
%defattr(-,root,root,-)
%attr(0600,root,root) %{_datadir}/selinux/packages/ceph.pp
%{_datadir}/selinux/devel/include/contrib/ceph.if
%{_mandir}/man8/ceph_selinux.8*

%post selinux
# backup file_contexts before update
. /etc/selinux/config
FILE_CONTEXT=/etc/selinux/${SELINUXTYPE}/contexts/files/file_contexts
cp ${FILE_CONTEXT} ${FILE_CONTEXT}.pre

# Install the policy
/usr/sbin/semodule -i %{_datadir}/selinux/packages/ceph.pp

# Load the policy if SELinux is enabled
if ! /usr/sbin/selinuxenabled; then
    # Do not relabel if selinux is not enabled
    exit 0
fi

if diff ${FILE_CONTEXT} ${FILE_CONTEXT}.pre > /dev/null 2>&1; then
   # Do not relabel if file contexts did not change
   exit 0
fi

# Check whether the daemons are running
/usr/bin/systemctl status ceph.target > /dev/null 2>&1
STATUS=$?

# Stop the daemons if they were running
if test $STATUS -eq 0; then
    /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
fi

# Now, relabel the files
/usr/sbin/fixfiles -C ${FILE_CONTEXT}.pre restore 2> /dev/null
rm -f ${FILE_CONTEXT}.pre
# The fixfiles command won't fix label for /var/run/ceph
/usr/sbin/restorecon -R /var/run/ceph > /dev/null 2>&1

# Start the daemons iff they were running before
if test $STATUS -eq 0; then
    /usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
fi
exit 0

%postun selinux
if [ $1 -eq 0 ]; then
    # backup file_contexts before update
    . /etc/selinux/config
    FILE_CONTEXT=/etc/selinux/${SELINUXTYPE}/contexts/files/file_contexts
    cp ${FILE_CONTEXT} ${FILE_CONTEXT}.pre

    # Remove the module
    /usr/sbin/semodule -n -r ceph > /dev/null 2>&1

    # Reload the policy if SELinux is enabled
    if ! /usr/sbin/selinuxenabled ; then
        # Do not relabel if SELinux is not enabled
        exit 0
    fi

    # Check whether the daemons are running
    /usr/bin/systemctl status ceph.target > /dev/null 2>&1
    STATUS=$?

    # Stop the daemons if they were running
    if test $STATUS -eq 0; then
        /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
    fi

    /usr/sbin/fixfiles -C ${FILE_CONTEXT}.pre restore 2> /dev/null
    rm -f ${FILE_CONTEXT}.pre
    # The fixfiles command won't fix label for /var/run/ceph
    /usr/sbin/restorecon -R /var/run/ceph > /dev/null 2>&1

    # Start the daemons if they were running before
    if test $STATUS -eq 0; then
	/usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
    fi
fi
exit 0

%endif # with selinux

#################################################################################
%if 0%{with libs_compat}
%files libs-compat
# We need an empty %%files list for ceph-libs-compat, to tell rpmbuild to actually
# build this meta package.
%endif

#################################################################################
%files devel-compat
# We need an empty %%files list for ceph-devel-compat, to tell rpmbuild to
# actually build this meta package.

#################################################################################
%files -n python-ceph-compat
# We need an empty %%files list for python-ceph-compat, to tell rpmbuild to
# actually build this meta package.


%changelog
