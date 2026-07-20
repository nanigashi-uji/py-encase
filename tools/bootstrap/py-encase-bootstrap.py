#!/usr/bin/env python3
import errno
import os
import shutil
import signal
import subprocess
import sys
import argparse
import copy
import pathlib

class PyEncaseBootstrap():

    HANDLED_SIGNALS = (signal.SIGHUP,
                       signal.SIGINT,
                       signal.SIGQUIT,
                       signal.SIGPIPE,
                       signal.SIGTERM)

    @classmethod
    def env_variable(cls, name, fallback=None): 
        _v = os.environ.get(name)
        return _v if _v else fallback

    def __init__(self):
        self.python_cmd  = self.__class__.env_variable('PYTHON3', 
                                                       self.__class__.env_variable('PYTHON',
                                                                                   'python3'))
        self.pip_cmd     = self.__class__.env_variable('PIP3',
                                                       self.__class__.env_variable('PIP',
                                                                                   'pip3'))
        self.dest_top    = self.__class__.env_variable("TMPDIR" , "/tmp")

        user = self.__class__.env_variable("USER", "uuuuu").strip(os.sep)
        self.dest_subdir = os.path.join(user, ("sandbox-%09d" % (os.getpid(),)), "py-encase")
        self.dest        = os.path.join(self.dest_top, self.dest_subdir)

        self.prefix = ''
        self.py_encase_args = []
        self.verbose = False
        self.dryrun  = False
        self.keep    = False
        self.top_created = self.__class__.top_tobecreated(self.dest)
        self.top_created_done = False
        self.current_process = None
        self.pending_signal = None

    @classmethod
    def top_tobecreated(cls, path:str):
        _p = os.path.normpath(os.path.expanduser(path))
        if _p.startswith(os.sep):
            upper = os.sep
            subdirs = _p[len(os.sep):]
        else:
            upper = "."
            subdirs = _p

        for component in subdirs.split(os.sep):
            if not component:
                continue
            if upper == os.sep:
                upper = os.path.join(os.sep, component)
            else:
                upper = os.path.join(upper, component)

            if not os.path.lexists(upper):
                if upper.startswith("."+os.sep):
                    return upper[1+len(os.sep):]
                return upper
        return None

    @classmethod
    def cmd_status(cls, returncode:int):
        if returncode < 0:
            return 128 - returncode
        return returncode

    def echo_cmd(self, cmds):
        if self.verbose or self.dryrun:
            if isinstance(cmds, (list, tuple)):
                sys.stderr.write(" ".join(cmds)+"\n")
            else:
                sys.stderr.write(str(cmds)+"\n")

    def invoke_cmd(self, cmds, env=None):
        self.echo_cmd(cmds)
        if self.dryrun:
            return 0
        try:
            self.current_process = subprocess.Popen(cmds, env=env,
                                                    start_new_session=True)
            returncode = self.current_process.wait()

        except FileNotFoundError:
            sys.stderr.write("[Error] : command not found : %s\n" % (cmds[0], ))
            returncode = 127
        except PermissionError:
            sys.stderr.write("[Error] : Can not execute : %s\n" % (cmds[0], ))
            returncode = 126
        except OSError as exc:
            sys.stderr.write("[Error] : Can not execute : %s: %s\n" % (cmds[0], str(exc)))
            if exc.errno in (errno.EACCES, errno.ENOEXEC):
                returncode = 126
            else:
                returncode = 1
        finally:
            self.current_process = None

        if self.pending_signal is not None:
            sigid = self.pending_signal
            self.pending_signal = None
            self.clean_up(sigid)

        return self.cmd_status(returncode)

    def set_sig_handlers(self):
        for sigid in self.__class__.HANDLED_SIGNALS:
            signal.signal(sigid, self.handle_signal)

    def set_sig_handlers_ignore(self):
        for sigid in self.__class__.HANDLED_SIGNALS:
            signal.signal(sigid, signal.SIG_IGN)

    def handle_signal(self, sigid, _frame):
        proc = self.current_process
        if proc is None or proc.poll() is not None:
            self.clean_up(sigid)
            return

        self.pending_signal = sigid

        try:
            os.killpg(proc.pid, sigid)
        except ProcessLookupError:
            pass
        #self.clean_up(sigid)

    def mk_directories(self) -> int:

        if self.top_created is None:
            return 0

        self.echo_cmd(["umask", "077"])
        if not self.dryrun:
            os.umask(0o077)

        self.echo_cmd(["mkdir", self.top_created])
        if not self.dryrun:
            try:
                os.mkdir(self.top_created)
            except OSError as exc:
                sys.stderr.write("[ERROR] Cannot create directory: %s (%s)\n"
                                 % (self.top_created, str(exc)))
                return 1

        self.top_created_done = True
        self.echo_cmd(["mkdir", "-p", self.dest])
        if not self.dryrun:
            try:
                os.makedirs(self.dest, exist_ok=True)
            except OSError as exc:
                sys.stderr.write("[ERROR] Cannot create directory: %s (%s)\n" % (self.dest, str(exc)))
                return 1
        return 0

    def rm_created_directories(self):
        if (self.top_created is None or
            not self.top_created_done or self.keep):
            return 0

        cleanup_status = 0

        if self.dryrun:
            return 0

        try:
            if os.path.lexists(self.dest):
                if (os.path.isdir(self.dest)
                    and not os.path.islink(self.dest)):
                    self.echo_cmd(["rm", "-rf", self.dest])
                    shutil.rmtree(self.dest)
                else:
                    os.unlink(self.dest)
        except OSError as exc:
            sys.stderr.write("[ERROR] Cannot remove path: %s (%s)\n" % (self.dest, str(exc)))
            cleanup_status = 1

        top_created = os.path.normpath(self.top_created)
        current     = os.path.dirname(os.path.normpath(self.dest))

        if top_created == os.path.normpath(self.dest):
            return cleanup_status

        while True:
            try:
                self.echo_cmd(["rmdir", current])
                os.rmdir(current)
            except FileNotFoundError:
                pass
            except OSError as exc:
                if exc.errno in (errno.ENOTEMPTY, errno.EEXIST):
                    break
                sys.stderr.write("[ERROR] Cannot remove directory: %s (%s)\n" % (current, str(exc)))
                cleanup_status = 1
                break
            if current == top_created:
                break
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return cleanup_status

    def clean_up(self, signum=None):
        self.set_sig_handlers_ignore()
        status = self.rm_created_directories()
        if signum is not None:
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)
            os._exit(128 + signum) # Normally unreachable, but retain a deterministic fallback.
        return status

    def run(self):

        self.set_sig_handlers()

        if self.verbose:
            sys.stderr.write("dest        = '%s'\n" % (self.dest, ))
            sys.stderr.write("top_created = '%s'\n" % (self.top_created or "", ))

        status = self.mk_directories()

        if status == 0:
            status = self.invoke_cmd([self.pip_cmd, "install",
                                      "--target", self.dest, "py-encase",])

        py_encase_opts = copy.deepcopy(self.py_encase_args)
        if ( self.verbose and 
             (not any( arg in ("-v", "--verbose") for arg in py_encase_opts))):
            py_encase_opts.insert(0, "--verbose")

        if status == 0:
            chldprcss_env = os.environ.copy()
            chldprcss_env["PYTHONPATH"] = self.dest
            chldprcss_env["PIP"]        = self.pip_cmd
            chldprcss_env["PIP3"]       = self.pip_cmd

            chldprcss_cmd = [ self.python_cmd,
                              os.path.join(self.dest, "bin", "py_encase"),
                              "--manage", "init",
                              ("--prefix=%s" % (self.prefix, )), ] + py_encase_opts
            status = self.invoke_cmd(chldprcss_cmd, env=chldprcss_env)

        if self.keep:
            if self.dryrun:
                sys.stderr.write("Dry-run: working directory would be kept under '%s'\n" % (self.dest, ))
            elif status == 0:
                sys.stderr.write("Installed py-encase is kept under '%s'\n" % (self.dest, ))
            else:
                sys.stderr.write("Incomplete working directory is kept under '%s'\n" % (self.dest, ))
            cleanup_status = 0
        else:
            cleanup_status = self.clean_up()

        if status == 0:
            status = cleanup_status

        return status

    def main(self):
        
        argpsr = argparse.ArgumentParser(description='py-encase bootstrap utility')
        argpsr.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        argpsr.add_argument('-n', '--dryrun',  action='store_true', help='dry-run mode')
        argpsr.add_argument('-f', '--force',  action='store_true',  help='force overwrite mode')
        argpsr.add_argument('-k', '--keep',    action='store_true', help='Keep py-encase (Do not clean directory)')
        argpsr.add_argument('-D', '--dest', type=str, metavar='path', default=self.dest, help='directory where py-encase is installed')
        argpsr.add_argument('prefix', type=str, metavar='prefix', help='Prefix of py-encase argument')
        argpsr.add_argument('py_encase_args', nargs=argparse.REMAINDER, metavar='py_encase_args', help='optional py-encase arguments')

        opts=argpsr.parse_args()
        self.verbose = opts.verbose
        self.dryrun  = opts.dryrun
        self.keep    = opts.keep

        if not opts.dest:
            sys.stderr.write("[ERROR] Invalid (empty) destination\n")
            return 1

        _raw_dest = os.path.expanduser(opts.dest)
        if ".." in pathlib.PurePath(_raw_dest).parts:
            sys.stderr.write("[ERROR] Specify destination without '..': %s\n" % (opts.dest, ))
            return 1
        
        self.dest = os.path.normpath(_raw_dest)
        self.top_created = self.__class__.top_tobecreated(self.dest)
        
        if not opts.prefix:
            sys.stderr.write("[ERROR] Invalid (empty) prefix\n")
            sys.exit(1)
        elif os.path.lexists(opts.prefix):
            if not opts.force:
                sys.stderr.write("[ERROR] prefix directory exists: %s\n" % (opts.prefix, ))
                sys.exit(1)
            else:
                sys.stderr.write("[WARNING] prefix directory exists  (force overwrite mode): %s\n" % (opts.prefix, ))
        self.prefix = opts.prefix
        self.py_encase_args = opts.py_encase_args

        return self.run()


if __name__ == "__main__":
    sys.exit(PyEncaseBootstrap().main())
