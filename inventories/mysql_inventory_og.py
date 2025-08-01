#!/usr/bin/env python3

import mysql.connector
import json
import sys

# Set up MySQL connection directly in the fetch_inventory function
def fetch_inventory():
    # Database connection settings
    conn = mysql.connector.connect(
        host='192.168.100.20',  # Update with your MySQL host
        user='root',            # Update with your username
        password='L3tm31n@23',  # Update with your password
        database='CMI'          # Update with your database
    )
    cursor = conn.cursor(dictionary=True)

    # Fetch data from the database
    cursor.execute("SELECT * FROM net")  # Adjust the query based on your schema
    rows = cursor.fetchall()

    # Start creating the inventory structure
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "children": ["ungrouped"]
        }
    }

    # Initialize groups
    groups = {}

    # Loop through each row in the database
    for row in rows:
        # Use the correct dictionary key for hostname (assuming "device" is the column name)
        hostname = row["device"]

        # Set host variables like ansible_host to use the IP address
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": row["ip"]
        } 
          
        # Generate group keys dynamically based on the columns
        group_keys = {
            f"site_{row['site']}",
            f"network_{row['network']}",
            f"vendor_{row['vendor']}",
            f"os_{row['os_type']}",
            f"platform_{row['platform']}",
            f"role_{row['role']}"
        }

        # Add groups to the inventory
        for key in group_keys:
            groups.setdefault(key, {"hosts": []})["hosts"].append(hostname)

    # Add all groups to inventory
    inventory.update(groups)

    # Close the connection
    cursor.close()
    conn.close()

    return inventory

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        print(json.dumps(fetch_inventory(), indent=4))
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        print(json.dumps({}, indent=4))  # Adjust this part as needed
    else:
        print(json.dumps({}, indent=4))
