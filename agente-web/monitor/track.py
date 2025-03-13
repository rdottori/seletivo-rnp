import asyncio
import aiohttp
import time
from logger import logger

async def track_site(hostname, semaphore):
# Faz requisição GET pro host <hostname> de forma concorrente
# Input: hostname + semáforo para controlar concorrência; output: estatísticas da requisição
	async with semaphore:
		results = {
			"hostname" : hostname,
			"loading_time" : None,
			"status_code" : None,
		}

		try:
			async with aiohttp.ClientSession() as session:
				start_time = asyncio.get_event_loop().time()
				async with session.get(f"https://{hostname}") as response:
					end_time = asyncio.get_event_loop().time()
					loading_time = end_time - start_time

					results["loading_time"] = loading_time
					results["status_code"] = response.status
					return results
		except Exception as e:
			logger.error(f"Requisição à página {hostname} para tracking falhou: {e}")
			return None
