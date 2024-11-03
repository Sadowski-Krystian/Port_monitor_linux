#!/usr/bin/env python3

import os
import time
import subprocess
import logging

logging.basicConfig(filename='/var/log/port_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_open_ports():
    try:
        result = subprocess.check_output(['ss', '-tuln']).decode('utf-8')
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Błąd podczas sprawdzania portów: {e}")
        return None

def monitor_ports(interval):
    while True:
        logging.info("Sprawdzanie otwartych portów...")
        ports_info = check_open_ports()
        if ports_info:
            logging.info("Otwarte porty:\n" + ports_info)
        time.sleep(interval)

if __name__ == "__main__":
    try:
        monitoring_interval = 60
        logging.info("Demon monitorujący porty uruchomiony.")
        monitor_ports(monitoring_interval)
    except KeyboardInterrupt:
        logging.info("Demon monitorujący porty zatrzymany.")
