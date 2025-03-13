import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import time
from datetime import datetime
from logger import logger

def get_db_connection(dbname, user, password, host, port):
# Conecta com o banco de dados
# Input: parâmetros de conexão; output: conexão
	retries = 0
	while retries < 10:
		try:
			conn = psycopg2.connect(
				dbname=dbname,
				user=user,
				password=password,
				host=host,
				port=port
			)
			return conn
		except Exception as e:
			logger.warning(f"Conexão ao banco de dados falhou: {e}. Tentando de novo")
			retries += 1
			time.sleep(5)

	logger.error("Erro ao conectar no banco de dados após múltiplas tentativas.")
	return None

def check_db_connection_health(conn, dbname, user, password, host, port):
# Checa que conexão com BD continua ativa
# Input: conexão e parâmetros de conexão; output: conexão
	try:
		if conn is None or conn.closed != 0:
			logger.warning(f"Conexão com banco de dados perdida. Reconectando...")
			conn = get_db_connection(dbname, user, password, host, port)
		return conn
	except Exception as e:
		logger.error("Não foi possível reestabelecer conexão com banco de dados.")
		return None

def insert_into_api_results_multiple(conn, all_results):
# Realiza insert na tabela api_results
# Input: parâmetros dos vários inserts na forma de uma lista de tuplas, com os valores dentro das tuplas na mesma ordem da query; output: True se insert tiver executado com sucesso, False caso contrário
	try:
		cur = conn.cursor()

		insert_query = sql.SQL("""
			INSERT INTO api_results (client, timestamp, up, bandwidth_use, quality, avg_availability)
			VALUES %s
			ON CONFLICT (client, timestamp) DO NOTHING;
		""")

		execute_values(cur, insert_query, all_results)
		conn.commit()
		cur.close()

		return True
	except Exception as e:
		conn.rollback()
		logger.error(f"Erro ao inserir dados na tabela de api_results: {e}")
		return False
