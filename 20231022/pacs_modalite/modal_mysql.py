import sys
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
import psycopg2
from psycopg2 import connect    # Does NOT need TextBroker to re-write
from psycopg2 import OperationalError, errorcodes, errors
import time

#------------------------------------------------------------------------------
# RECUPERATION DE LA BDD MYSQL  DANS LA LISTE l_mysql
#------------------------------------------------------------------------------

try:
    cnx_mysql = mysql.connector.connect(user='kligliro', password='%LokO80%',
                                 host='shor',
                                 database='modalite')
                                 
    print("Connexion à la base de données MYSQL reussie")
    cursor_mysql = cnx_mysql.cursor()


    # query = ("SELECT * FROM liste_new WHERE marque = 'DELTAMED'")
    # cursor.execute(query)
    # select_stmt = "SELECT * FROM liste_new WHERE marque = %(marque)s"
    # cursor.execute(select_stmt, { 'marque': 'SIEMENS' })
    select_stmt = "SELECT * FROM liste_new"
    cursor_mysql.execute(select_stmt)
    # cursor_postgres.execute(select_stmt)

    c1 = []
    c2 = []
    # c3 = []
    
    for i in range(len(cursor_mysql.description)):
        # print("Column {}:".format(i+1))
        c1.append(i+1)
        desc = cursor_mysql.description[i]
        # print("  column_name = {}".format(desc[0]))
        c2.append(desc[0])
        # print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))
        # c3.append(FieldType.get_info(desc[1]))
        # print("  null_ok = {}".format(desc[6]))
        # print("  column_flags = {}".format(desc[7]))
    print(c1)
    print(c2)
    # print(c3)

    l_mysql = []
    n = 0
    for (line) in cursor_mysql:
        l_mysql.append(line)
        n = n + 1
    print("nombre de lignes dans BDD MYSQL : ", n)
    print(l_mysql)
    cursor_mysql.close()


except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx_mysql.close()

#------------------------------------------------------------------------------
# RECUPERATION DE LA BDD POSTGRESQL  DANS LA LISTE l_postgres
#------------------------------------------------------------------------------
# time.sleep(4)

def print_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print ("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

try:
    cnx_postgres = psycopg2.connect(
              user = "kligliro",
              password = "atc3213",
              host = "shor",
              port = "5432",
              database = "modalite"
        )
    print("Connexion à la base de données POSTGRESQL reussie")
    cursor_postgres = cnx_postgres.cursor()

    select_stmt = "SELECT * FROM liste_new"
    cursor_postgres.execute(select_stmt)

    c3 = []
    c4 = []
    # c3 = []
    
    for i in range(len(cursor_postgres.description)):
        # print("Column {}:".format(i+1))
        c3.append(i+1)
        desc = cursor_postgres.description[i]
        # print("  column_name = {}".format(desc[0]))
        c4.append(desc[0])
        # print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))
        # c3.append(FieldType.get_info(desc[1]))
        # print("  null_ok = {}".format(desc[6]))
        # print("  column_flags = {}".format(desc[7]))
    print(c3)
    print(c4)
    # print(c3)

    l_postgres = []
    n = 0
    for (line) in cursor_postgres:
        l_postgres.append(line)
        n = n + 1
    print("nombre de lignes dans BDD POSTGRESQL : ", n)
    # print(l_postgres)
    cnx_postgres.close()

except (Exception, psycopg2.Error) as error :
    print_psycopg2_exception(error)
    print ("Erreur lors de la connexion à PostgreSQL", error)
    # logger.error("Erreur lors de la connexion à PostgreSQL ")
    cnx_postgres = None


#------------------------------------------------------------------------------
# ANALYSE DES 2 LISTES : l_postgres et l_mysql
#------------------------------------------------------------------------------


# 'Divers', 'Fini', 'Par', 'date_modification', 'dateping'   #  BDD POSTGRESQL

# 'Index', 'Adresse Ip', 'Type Machine', 'Aet', 'Port',      # commun aux 2 BDD
# 'Masque', 'Hostname''Modalite''Libelle Hote', 'Pacs',      # commun aux 2 BDD
# 'Remarque', 'Localisation', 'Systeme''Marque', 'Appareil'  # commun aux 2 BDD
# 'Store', 'MacAdresse', 'Vlan', 'Dicom', 'Inventaire'       # commun aux 2 BDD
# 'DHCP', 'Worklist', 'PingHost'                             # commun aux 2 BDD

