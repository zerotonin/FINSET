import sqlite3

def remove_column(fileposition):
    """
    This function is specifically designed to remove the 'Result_1_nan' column from the 
    'ethovision_data' table in the 'habituation.db' SQLite database. This is done in order to make 
    the 'ethovision_data' combinable with other tables in the database.

    The process involves creating a new table without the 'Result_1_nan' column, copying the 
    data from the 'ethovision_data' to the new table, deleting the 'ethovision_data', and finally renaming 
    the new table to 'ethovision_data'. 

    Remember to backup your database before running this function, as the changes made by this 
    function are irreversible.

    Returns:
        None
    """
    
    # Connect to your database
    conn = sqlite3.connect(fileposition)
    c = conn.cursor()

    # Get all columns from the table
    c.execute('PRAGMA table_info(ethovision_data);')
    info = c.fetchall()
    columns = [row[1] for row in info]

    # Remove 'Result_1_nan' from the list of columns
    if 'Result_1_nan' in columns:
        columns.remove('Result_1_nan')

    # Create a string with the column names for the SQL query
    columns_str = ', '.join([f'"{col}"' for col in columns])

    # 1. Create new table without 'Result_1_nan'
    c.execute(f'''
        CREATE TABLE new_table AS 
        SELECT {columns_str}
        FROM ethovision_data;
    ''')

    # 2. The data is automatically copied as part of the CREATE TABLE command

    # 3. Delete old table
    c.execute('DROP TABLE ethovision_data;')

    # 4. Rename new table
    c.execute('ALTER TABLE new_table RENAME TO ethovision_data;')

    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()

remove_column('/home/bgeurten/ethoVision_database/habituation2023_ethovision_data.db')
