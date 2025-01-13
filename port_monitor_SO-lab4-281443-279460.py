#!/usr/bin python3

import os
import sys
import time
import subprocess
import logging
from signal import signal, SIGTERM

LOG_FILE = '/var/log/port_monitor.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Daemon:
    def __init__(self, pid_file, interval=60):
        self.pid_file = pid_file
        self.interval = interval

    def daemonize(self):
        if os.fork() > 0:
            sys.exit(0)
        os.setsid()
        if os.fork() > 0:
            sys.exit(0)

        sys.stdout.flush()
        sys.stderr.flush()
        stdin = open('/dev/null', 'r')
        stdout = open('/dev/null', 'a+')
        stderr = open('/dev/null', 'a+')
        os.dup2(stdin.fileno(), sys.stdin.fileno())
        os.dup2(stdout.fileno(), sys.stdout.fileno())
        os.dup2(stderr.fileno(), sys.stderr.fileno())

        file = open(self.pid_file, 'w')
        file.write(str(os.getpid()))

    def delpid(self):
        os.remove(self.pid_file)

    def start(self):
        if os.path.exists(self.pid_file):
            print(f"Daemon już działa. PID znajduje się w {self.pid_file}.")
            sys.exit(1)

        logging.info("Uruchamianie demona...")
        self.daemonize()
        self.run()

    def stop(self, *args):
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = int(f.read())
            os.kill(pid, SIGTERM)
            os.remove(self.pid_file)
            logging.info("Demon został zatrzymany.")
            sys.exit(0)
        else:
            print("Demon nie działa.")
            sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        while True:
            logging.info("Sprawdzanie otwartych portów...")
            ports_info = self.check_open_ports()
            if ports_info:
                logging.info("Otwarte porty:\n" + ports_info)
            time.sleep(self.interval)

    def check_open_ports(self):
        try:
            result = subprocess.check_output(['ss', '-tuln']).decode('utf-8')
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Błąd podczas sprawdzania portów: {e}")
            return None


if __name__ == "__main__":
    PID_FILE = '/var/run/port_monitor.pid'

    daemon = Daemon(pid_file=PID_FILE, interval=60)

    if len(sys.argv) != 2:
        print(f"Użycie: {sys.argv[0]} start|stop|restart")
        sys.exit(1)

    if sys.argv[1] == 'start':
        daemon.start()
    elif sys.argv[1] == 'stop':
        daemon.stop()
    elif sys.argv[1] == 'restart':
        daemon.restart()
    else:
        print(f"Nieprawidłowa opcja: {sys.argv[1]}")
        sys.exit(1)
