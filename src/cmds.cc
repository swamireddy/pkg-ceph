// -*- mode:C++; tab-width:8; c-basic-offset:2; indent-tabs-mode:t -*- 
// vim: ts=8 sw=2 smarttab
/*
 * Ceph - scalable distributed file system
 *
 * Copyright (C) 2004-2006 Sage Weil <sage@newdream.net>
 *
 * This is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License version 2.1, as published by the Free Software 
 * Foundation.  See file COPYING.
 * 
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <sys/stat.h>
#include <iostream>
#include <string>
using namespace std;

#include "config.h"

#include "mon/MonMap.h"
#include "mds/MDS.h"
#include "mds/Dumper.h"

#include "msg/SimpleMessenger.h"

#include "common/Timer.h"
#include "common/common_init.h"

#include "mon/MonClient.h"

#include "auth/KeyRing.h"

void usage()
{
  derr << "usage: cmds -i name [flags] [[--journal_check]|[--hot-standby][rank]]\n"
       << "  -m monitorip:port\n"
       << "        connect to monitor at given address\n"
       << "  --debug_mds n\n"
       << "        debug MDS level (e.g. 10)\n"
       << "  --dump-journal rank [filename]"
       << "        dump the MDS journal for rank. Defaults to mds.journal.dump"
       << dendl;
  generic_server_usage();
}

int main(int argc, const char **argv) 
{
  vector<const char*> args;
  argv_to_vec(argc, argv, args);
  env_to_vec(args);
  bool dump_journal = false;
  const char *dump_file = NULL;
  int shadow = 0;

  common_set_defaults(true);
#ifdef HAVE_LIBTCMALLOC
  g_conf.profiler_start = HeapProfilerStart;
  g_conf.profiler_running = IsHeapProfilerRunning;
  g_conf.profiler_stop = HeapProfilerStop;
  g_conf.profiler_dump = HeapProfilerDump;
  g_conf.tcmalloc_have = true;
#endif //HAVE_LIBTCMALLOC
  common_init(args, "mds", true);

  // mds specific args
  for (unsigned i=0; i<args.size(); i++) {
    if (!strcmp(args[i], "--dump-journal")) {
      if (i + 1 < args.size() &&
          (args[i+1][0] != '-')) { // another argument?
        shadow = strtol(args[i+1], 0, 0);
        if (i + 2 < args.size() &&
            (args[i+2][0] != '-')) {
          dump_file = args[i+2];
          ++i;
        } else
          dump_file = "mds.journal.dump";
        ++i;
      } else {
        cout << "must specify rank of mds to dump!" << std::endl;
        return -1;
      }
      dump_journal = true;
      dout(0) << "dumping journal" << dendl;
    } else if (!strcmp(args[i], "--journal_check")) {
      dout(0) << "checking journal"  << dendl;
      if (shadow) {
        dout(0) << "Error: can only select one standby state" << dendl;
        return -1;
      }
      shadow = MDSMap::STATE_ONESHOT_REPLAY;
      char *endpoint = NULL;
      int check_rank = strtol(args[i+1], &endpoint, 0);
      if (*endpoint) {
        if(g_conf.mds_standby_for_rank == -1 &&
          !g_conf.mds_standby_for_name) {
          dout(0) << "Error: no rank specified for journal replay!" << dendl;
          return -1;
        }
      } else { // we got a rank from command line
        g_conf.mds_standby_for_rank = check_rank;
        ++i;
      }
    } else if (!strcmp(args[i], "--hot-standby")) {
      dout(0) << "going into standby_replay" << dendl;
      if (shadow) {
        dout(0) << "Error: can only select one standby state" << dendl;
        return -1;
      }
      shadow = MDSMap::STATE_STANDBY_REPLAY;
      char *endpoint = NULL;
      int check_rank = strtol(args[i+1], &endpoint, 0);
      if (*endpoint) {
        if(g_conf.mds_standby_for_rank == -1 &&
          !g_conf.mds_standby_for_name) {
          dout(0) << "no rank specified for standby, entering pool!" << dendl;
        }
      } else { // we got a rank from command line
        g_conf.mds_standby_for_rank = check_rank;
        ++i;
      }
    } else {
      derr << "unrecognized arg " << args[i] << dendl;
      usage();
    }
  }
  if (!g_conf.id && !dump_journal) {
    derr << "must specify '-i name' with the cmds instance name" << dendl;
    usage();
  }

  if (g_conf.clock_tare) g_clock.tare();

  // get monmap
  RotatingKeyRing rkeys(CEPH_ENTITY_TYPE_MDS, &g_keyring);
  MonClient mc(&rkeys);
  if (mc.build_initial_monmap() < 0)
    return -1;

  SimpleMessenger *messenger = new SimpleMessenger();
  messenger->bind();
  if (dump_journal) {
    Dumper *journal_dumper = new Dumper(messenger, &mc);
    journal_dumper->init(shadow);
    journal_dumper->dump(dump_file);
    mc.shutdown();
  } else {
    derr << "starting mds." << g_conf.id
        << " at " << messenger->get_ms_addr()
        << dendl;

    messenger->register_entity(entity_name_t::MDS(-1));
    assert_warn(messenger);
    if (!messenger)
      return 1;

    uint64_t supported =
      CEPH_FEATURE_UID |
      CEPH_FEATURE_NOSRCADDR |
      CEPH_FEATURE_DIRLAYOUTHASH;
    messenger->set_default_policy(SimpleMessenger::Policy::client(supported, 0));
    messenger->set_policy(entity_name_t::TYPE_MON,
                          SimpleMessenger::Policy::client(supported,
                                                          CEPH_FEATURE_UID));
    messenger->set_policy(entity_name_t::TYPE_MDS,
                          SimpleMessenger::Policy::lossless_peer(supported,
                                                                 CEPH_FEATURE_UID));
    messenger->set_policy(entity_name_t::TYPE_CLIENT,
                          SimpleMessenger::Policy::stateful_server(supported, 0));

    messenger->start();

    // start mds
    MDS *mds = new MDS(g_conf.id, messenger, &mc);

    // in case we have to respawn...
    mds->orig_argc = argc;
    mds->orig_argv = argv;

    if (shadow)
      mds->init(shadow);
    else
      mds->init();

    messenger->wait();

    // yuck: grab the mds lock, so we can be sure that whoever in *mds
    // called shutdown finishes what they were doing.
    mds->mds_lock.Lock();
    mds->mds_lock.Unlock();

    // only delete if it was a clean shutdown (to aid memory leak
    // detection, etc.).  don't bother if it was a suicide.
    if (mds->is_stopped())
      delete mds;

    // cd on exit, so that gmon.out (if any) goes into a separate directory for each node.
    char s[20];
    snprintf(s, sizeof(s), "gmon/%d", getpid());
    if (mkdir(s, 0755) == 0)
      chdir(s);

    generic_dout(0) << "stopped." << dendl;
  }
  return 0;
}

