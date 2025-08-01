#!/usr/bin/env python3

import yaml
import mysql.connector
import json
import sys

def fetch_inventory():
    # Connect to the database
    # Load credentials from your group_vars/all.yml
    # with open('/etc/ansible/inventories/group_vars/all.yml') as vf:
    with open('/etc/ansible/inventories/group_vars/all/main.yml') as vf:
        vars_all = yaml.safe_load(vf)

    mysql_host     = vars_all['mysql_host']
    mysql_port     = vars_all['mysql_port']
    mysql_user     = vars_all['mysql_user']
    mysql_password = vars_all['mysql_password']
    mysql_db       = vars_all['mysql_db']

    # Connect using those values
    conn = mysql.connector.connect(
        host     = mysql_host,
        port     = mysql_port,
        user     = mysql_user,
        password = mysql_password,
        database = mysql_db,
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM net")
    rows = cursor.fetchall()

    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "children": ["ungrouped"]
        }
    }

    groups = {}

    for row in rows:
        hostname = row["device"]

        # Set host-specific variables
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": row["ip"]
        }

        # Normalize and safely get group keys
        role = str(row.get('role', '')).strip().lower()
        network = str(row.get('network', '')).strip().lower()
        site = str(row.get('site', '')).strip().lower()
        platform = str(row.get('platform', '')).strip().lower()
        vendor = str(row.get('vendor', '')).strip().lower()
        os_type = str(row.get('os_type', '')).strip().lower()
        os_ver = str(row.get('os_ver', '')).strip().lower()
        origin = str(row.get('origin', '')).strip().lower()

        # Create group entries dynamically
        for key in [
            f"role_{role}" if role else '',
            f"network_{network}" if network else '',
            f"site_{site}" if site else '',
            f"platform_{platform}" if platform else '',
            f"vendor_{vendor}" if vendor else '',
            f"os_type_{os_type}" if os_type else '',
            f"os_ver_{os_ver}" if os_ver else '',
            f"origin_{origin}" if origin else '',
        ]:
            if key:
                groups.setdefault(key, {"hosts": []})["hosts"].append(hostname)

    # Add all the group data into the main inventory
    inventory.update(groups)

    cursor.close()
    conn.close()

    return inventory

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        print(json.dumps(fetch_inventory(), indent=4))
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        print(json.dumps({}, indent=4))  # Optional: customize per-host details if needed
    else:
        print(json.dumps({}, indent=4))
