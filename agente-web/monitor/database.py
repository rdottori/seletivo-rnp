import psycopg2
from psycopg2 import sql
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

def insert_into_ping_results(conn, host, packet_loss, rtt_min, rtt_avg, rtt_max, rtt_mdev):
# Realiza insert na tabela ping_results
# Input: parâmetros do insert; output: True se insert tiver executado com sucesso, False caso contrário
	try:
		cur = conn.cursor()
		current_timestamp = datetime.now()

		insert_query = sql.SQL("""
			INSERT INTO ping_results (host, timestamp, rtt_min, rtt_avg, rtt_max, rtt_mdev, packet_loss)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (host, timestamp) DO NOTHING;
		""")

		cur.execute(insert_query, (host, current_timestamp, rtt_min, rtt_avg, rtt_max, rtt_mdev, packet_loss))
		conn.commit()
		cur.close()

		return True
	except Exception as e:
		conn.rollback()
		logger.error(f"Erro ao inserir dados na tabela de ping_results: {e}")
		return False

def insert_into_track_results(conn, host, loading_time, status_code):
# Realiza insert na tabela track_results
# Input: parâmetros do insert; output: True se insert tiver executado com sucesso, False caso contrário
	try:
		cur = conn.cursor()
		current_timestamp = datetime.now()

		insert_query = sql.SQL("""
			INSERT INTO track_results (host, timestamp, loading_time, status_code)
			VALUES (%s, %s, %s, %s)
			ON CONFLICT (host, timestamp) DO NOTHING;
		""")

		cur.execute(insert_query, (host, current_timestamp, loading_time, status_code))
		conn.commit()
		cur.close()

		return True
	except Exception as e:
		conn.rollback()
		logger.error(f"Erro ao inserir dados na tabela de ping_results: {e}")
		return False
