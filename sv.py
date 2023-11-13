import csv
import socket
from main import connection
d = []



with open('arp.csv', 'r') as csvfile:
    # Create a CSV reader
    csv_reader = csv.reader(csvfile)

    # Read and print each row
    for row in csv_reader:
        if row[1].count(':') != 0:
            try:
                hostname, _, _ = socket.gethostbyaddr(row[0].strip())
            except Exception as E:
                print(E)
            else:
                if hostname.split('.')[0][0] == 'U' or hostname.split('.')[0][0] == 'u':
                    d.append((row[0].strip(), row[1].strip()[:17], hostname.split('.')[0]))
                    SQLRequest = """insert into computerlist (node, mac) values (%s, %s)"""
                    try:
                        connection.connect()
                    except Exception as E:
                        print(E)
                    else:
                        with connection.cursor() as cursor:
                            cursor.execute(SQLRequest, (hostname.split('.')[0].upper(), row[1].strip()[:17]))
                            connection.commit()
                        cursor.close()
                        connection.close()










