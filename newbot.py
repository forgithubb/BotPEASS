#!/usr/bin/env python

import os

import requests

from notifiers import generate_new_cve_message, send_slack_mesage, send_telegram_message
from providers import CVERetrieverNVD

DEBUG = False


def main():
    retriever = CVERetrieverNVD()
    data = retriever.get_new_cves()
    if data:
        if DEBUG: print("[DBG] data keys: {}".format(data[0].keys()))
        for item in data:
            public_exploits = ''
            cve_message = generate_new_cve_message(item)
            if item.get('ExploitDB_ID') is not None:
                print(f"[*] CVE *with Exploit-db ID* Message:\n{cve_message}")
            else:
                print(f"[*] CVE Message:\n{cve_message}")
            send_telegram_message(cve_message)
        
        print("[*] {} new CVE's to report this collection cycle".format(len(data)))
    else:
        print("[*] No new CVE's matching your search scope for this collection cycle")
    
    #if retriever.cve_new_dataset:
        #print("[*] Can also leverage this class attribute of the dataset. Pulled {} CVE's".format(len(retriever.cve_new_dataset)))
        #pass
    return


if __name__ == '__main__':
    main()
