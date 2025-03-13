import json
import time
import os
import sys
from datetime import datetime

import requests

from logger import logger
from database import get_db_connection, insert_into_api_results_multiple, check_db_connection_health

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
logger.info("Iniciando configurações de monitoramento do ViaIpe...")

logger.info("Conectando ao banco de dados...")
conn = get_db_connection(dbname, user, password, host, port)
if conn is None:
	sys.exit(1)

logger.info("Configurações finalizadas, inciando monitoramento")




'''
Laço principal
'''
def main(conn):
# Realiza requests continuamente, dormindo por X segundos entre iterações
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
				requests_timeout = config["requests_timeout"] # É importante ter um valor de timeout para evitar a possibilidade da requisição esperar eternamente
				requests_retry_wait = config["requests_retry_wait"] # É util que esse valor seja diferente do sleep_interval, pois se soubermos da natureza do problema com o servidor podemos estimar o tempo até normalizar
				api_host = config["api_host"]
		except Exception as e:
			logger.error(f"Erro ao abrir ou processar arquivo de configuração: {e}")
			sys.exit(1)

		logger.debug("Executando requests")
		requests_error = False
		try:
			api_response = requests.get(api_host, timeout=requests_timeout)
			if api_response.status_code < 200 or api_response.status_code > 299:
				logger.error(f"Requisição ao servidor não retornou código de sucesso. O servidor pode estar com problemas ou a API pode ter sofrido alguma atualização. Tentando novamente em {requests_retry_wait} segundos.")
				requests_error = True
			else:
				db_insert_data = []
				current_timestamp = datetime.now()
				for client in api_response.json():
					try:
						up = True
						if client["data"]["smoke"]["loss"] == 100:
							up = False
							quality = "Ruim"
						elif client["data"]["smoke"]["loss"] <= 0.01:
							quality = "Ótima"
						elif client["data"]["smoke"]["loss"] <= 1:
							quality = "Boa"
						elif client["data"]["smoke"]["loss"] <= 3:
							quality = "Regular"
						else:
							quality = "Ruim"

						bandwidth_use = 0
						for interface in client["data"]["interfaces"]:
							bandwidth_use += interface["traffic_in"] + interface["traffic_out"]

						avg_availability = 100 - client["data"]["smoke"]["avg_loss"]

						client_name = client["name"]

						db_insert_data.append((client_name, current_timestamp, up, bandwidth_use, quality, avg_availability))
					except KeyError as e:
						if "name" in client.keys():
							logger.warning(f"KeyError no cliente {client['name']}, há dados faltando no objeto: {e}")
						else:
							logger.warning(f"Objeto de cliente sem nome detectado")
						continue
				insert_success = insert_into_api_results_multiple(conn, db_insert_data)
		except requests.exceptions.Timeout:
			logger.error(f"Timeout ao tentar conectar com a API. O servidor pode estar indisponível. Tentando novamente em {requests_retry_wait} segundos.")
			requests_error = True
		except Exception as e:
			logger.error(f"Erro ao processar resposta do servidor: {e}. O servidor pode estar com problemas ou a API pode ter sofrido alguma atualização. Tentando novamente em {requests_retry_wait} segundos.")
			requests_error = True

		if requests_error:
			time.sleep(requests_retry_wait)
		if not requests_error:
			logger.debug(f"Dormindo por {sleep_interval} segundos")
			time.sleep(sleep_interval)

main(conn)
