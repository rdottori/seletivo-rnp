import json
import time
import os
import sys

import asyncio
import aiohttp

from logger import logger
from database import get_db_connection, insert_into_ping_results, insert_into_track_results, check_db_connection_health
from ping import ping_site
from track import track_site

'''
Definição de constantes e variáveis globais importantes
'''

dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")



'''
Início da execução: setup inicial
'''
logger.info("Iniciando configurações de monitoramento...")

logger.info("Conectando ao banco de dados...")
conn = get_db_connection(dbname, user, password, host, port)
if conn is None:
	sys.exit(1)

logger.info("Configurações finalizadas, inciando monitoramento")




'''
Laço principal
'''
async def main(conn):
# Realiza pings e requests continuamente, dormindo por X segundos entre iterações
# Input: conexão com BD; output (nenhum; função perpétua)
	while True:
		# Checamos saúde da conexão com o BD; como o programa deve rodar continuamente, é importante levar em conta a possibilidade de quedas
		logger.debug("Testando conexão com BD")
		conn = check_db_connection_health(conn, dbname, user, password, host, port)
		if conn is None:
			sys.exit(1)

		logger.debug("Carregando configurações")
		try:
			with open("config.json", 'r') as f:
				config = json.load(f)
				sleep_interval = config["sleep_interval"]
				ping_count = config["ping_count"]
				ping_timeout = config["ping_timeout"]
				ping_hosts = config["ping_hosts"]
				track_hosts = config["track_hosts"]
				concurrent_connections = config["concurrent_connections"]
			# Usamos um semáforo para que as estatísticas de latência/tempo de resposta não sejam afetadas por congestionamento na rede
			semaphore = asyncio.Semaphore(concurrent_connections)
		except Exception as e:
			logger.error(f"Erro ao abrir ou processar arquivo de configuração: {e}")
			sys.exit(1)

		logger.debug("Executando trackings")
		track_results = await asyncio.gather(*(track_site(host, semaphore) for host in track_hosts))
		for result in track_results:
			insert_success = insert_into_track_results(conn, result["hostname"], result["loading_time"], result["status_code"])

		logger.debug("Executando pings")
		ping_results = await asyncio.gather(*(ping_site(host, ping_count, ping_timeout, semaphore) for host in ping_hosts))
		for result in ping_results:
			insert_success = insert_into_ping_results(conn, result["hostname"], result["packet_loss"], result["rtt_min"], result["rtt_avg"], result["rtt_max"], result["rtt_mdev"])

		logger.debug(f"Dormindo por {sleep_interval} segundos")
		time.sleep(sleep_interval)

asyncio.run(main(conn))
