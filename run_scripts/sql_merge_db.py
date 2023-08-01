import sqlite3

def combine_databases(filepath):
    """
    This function combines the 'ethovision_data' tables from three SQLite databases into one in a new database.

    The databases are 'habituation2023_ethovision_data.db', 'rehabituation_2023.db', and 'meth_administration_2023.db'. The data from the tables in these
    databases is copied into a new 'ethovision_data' table in a new database 'combined_database.db'.

    Note: Make sure that the 'ethovision_data' tables in all three databases have the same structure.

    Returns:
        None
    """
    # Connect to the first database
    conn1 = sqlite3.connect(f'{filepath}habituation2023_ethovision_data.db')
    c1 = conn1.cursor()

    # Create a new database and a cursor for it
    conn_new = sqlite3.connect(f'{filepath}combined_ethovision_data.db')
    c_new = conn_new.cursor()

    # Create a new table in the new database with the same structure as the 'ethovision_data' table
    c1.execute("SELECT sql FROM sqlite_master WHERE name = 'ethovision_data'")
    create_table_query = c1.fetchone()[0]
    c_new.execute(create_table_query)

    # Attach the databases
    c_new.execute(f"ATTACH DATABASE '{filepath}habituation2023_ethovision_data.db' AS db1")
    c_new.execute(f"ATTACH DATABASE '{filepath}rehabituation2023_ethovision_data.db' AS db2")
    c_new.execute(f"ATTACH DATABASE '{filepath}meth2023_ethovision_data.db' AS db3")

    # Copy the data from the tables in the other databases into the table in the new database
    c_new.execute("INSERT INTO ethovision_data SELECT * FROM db1.ethovision_data")
    c_new.execute("INSERT INTO ethovision_data SELECT * FROM db2.ethovision_data")
    c_new.execute("INSERT INTO ethovision_data SELECT * FROM db3.ethovision_data")

    # Save (commit) the changes and close the connections
    conn_new.commit()
    conn1.close()
    conn_new.close()

combine_databases('/home/bgeurten/ethoVision_database/')
