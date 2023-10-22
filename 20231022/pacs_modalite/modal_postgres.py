import psycopg2
from datetime import datetime
import time
import ping3
import logging
import sys
from psycopg2 import connect    # Does NOT need TextBroker to re-write
from psycopg2 import OperationalError, errorcodes, errors
from psycopg2 import __version__ as psycopg2_version

# print ("psycopg2 version:", psycopg2_version, "\n")

# Create a custom logger
logger = logging.getLogger(__name__)
# Create handlers
d_handler = logging.FileHandler('modalite_debug.log')
# c_handler = logging.FileHandler('modalite_warning.log')
# f_handler = logging.FileHandler('modalite_error.log')
# i_handler = logging.FileHandler('modalite_info.log')
d_handler.setLevel(logging.DEBUG)
# c_handler.setLevel(logging.WARNING)
# f_handler.setLevel(logging.ERROR)
# i_handler.setLevel(logging.INFO)
# Create formatters and add it to handlers
d_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# i_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
d_handler.setFormatter(d_format)
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
# i_handler.setFormatter(i_format)
# Add handlers to the logger
logger.addHandler(d_handler)
#logger.addHandler(c_handler)
#logger.addHandler(f_handler)
#logger.addHandler(i_handler)

logging.basicConfig(level=logging.DEBUG)

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
    conn = psycopg2.connect(
          user = "kligliro",
          password = "atc3213",
          host = "shor",
          port = "5432",
          database = "modalite"
    )
    cur = conn.cursor()
    # print("cur : ", cur)
    # print("cur : ", cur.__dir__() )

    modal_dic = {
        0 : "Index",
        1 : "Adresse Ip",
        2 : "PingHost",
        3 : "date_modification",
        4 : "dateping",
    }

    modal_col = ["Index", "Port", "Adresse Ip", "Aet", "Type Machine", "Masque", "Pacs", "Worklist", "Hostname", "Modalite", \
                 "Libelle Hote", "Remarque", "Localisation", "Systeme", "Marque", "Appareil", "Store", "MacAdresse", "Vlan", \
                 "Dicom", "Inventaire", "DHCP", "Divers", "Fini", "Par", "PingHost", "date_modification", "dateping"]
    
    modal_liste = []
    cur.execute("select 'ping OK : ', count(*)  from liste_new where {} = 'OK' ;".format("\"PingHost\"" ))
    nb_OK = cur.fetchall()
    cur.execute("select 'ping KO : ', count(*)  from liste_new where {} = 'KO' ;".format("\"PingHost\""))
    nb_KO = cur.fetchall()

    logger.debug("-----------------------------------------------------------------")
    logger.info("  {}  /  {}".format(nb_OK, nb_KO))

    cur.execute("SELECT %s, %s, %s, %s FROM liste_new ;" % ("\"Index\"", "\"Adresse Ip\"", "\"PingHost\"", "\"dateping\"") )

    res = cur.fetchall()
    ojd = datetime.today().strftime('%Y-%m-%d')
    for r in res:
        ip = r[1]
        print(r[0]);
        if ip == "0.0.0.0":
            logger.error(" à l' index {}, adresse <0.0.0.0> affectée à la modalié : {}".format(id, ip))
            continue
        elif ip == "":
            logger.error(" à l' index {}, pas d'adresse IP affectée à la modalié : {}".format(id, ip))
            continue
        else:
            ph = r[2]
            if ph == "OK":
                # logger.debug(" à l' index {}, la modalité a déjà répondu positivement au 'ping' : {}".format(id, ip))
                continue
            id = r[0]                       
            resping = ping3.ping(ip, timeout=1.5)            
            if resping :
                ping = "OK"
                logger.debug(" à l' index {}, -----> une nouvelle modalité répond au 'ping' : {}".format(id, ip))
                chaine = "UPDATE {} SET ({}, {} ) = ('{}', '{}' ) WHERE {} = {} ;".format("liste_new", "\"PingHost\"", "\"dateping\"", ping, ojd, "\"Index\"", id)
            else:
                if ph == "KO":
                    continue
                else:
                    ping = "KO"
                    logger.debug(" à l' index {}, la modalité ne répond pas au 'ping' : {}".format(id, ip))
                    # chaine = "UPDATE {} SET ({}, {} ) = ('{}', '{}' ) WHERE {} = {} ;".format("liste_new", "\"PingHost\"", "\"dateping\"", ping, ojd, "\"Index\"", id)
                    chaine = "UPDATE {} SET {} = '{}' WHERE {} = {} ;".format("liste_new", "\"PingHost\"", ping, "\"Index\"", id)
            cur.execute(chaine)
            conn.commit()
            # pour le formatage des chaines SQL, 
            # pour les tables, pas besoin de "\"....\"", c 'est seulement pour les colonnes !
            # entourer les valeurs de '..' quand c' est du string !
    cur.execute("select 'ping OK : ', count(*)  from liste_new where {} = 'OK' ;".format("\"PingHost\"" ))
    nb_OK = cur.fetchall()
    cur.execute("select 'ping KO : ', count(*)  from liste_new where {} = 'KO' ;".format("\"PingHost\""))
    nb_KO = cur.fetchall()
    logger.info("  {}  /  {}".format(nb_OK, nb_KO))       

    cur.close()
    conn.close()
    print("La connexion PostgreSQL est fermée")

except (Exception, psycopg2.Error) as error :
    print_psycopg2_exception(error)
    print ("Erreur lors de la connexion à PostgreSQL", error)
    logger.error("Erreur lors de la connexion à PostgreSQL ")
    conn = None


"""
for i in range(len(cur.description)):
    print("Column {}:".format(i+1))
    desc = cur.description[i]
    print("  column_name = {}".format(desc[0]))
    print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))
    print("  null_ok = {}".format(desc[6]))
    print("  column_flags = {}".format(desc[7]))"""