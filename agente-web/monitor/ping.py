import asyncio
import asyncio.subprocess as subprocess
import re
from logger import logger

async def ping_site(hostname, count, timeout, semaphore):
# Executa <count> pings concorrentes pro host <hostname>
# Input: parâmetros do ping + semáforo para controlar concorrência; output: estatísticas do ping
	async with semaphore:
		results = {
			"hostname" : hostname,
			"packet_loss" : None,
			"rtt_min" : None,
			"rtt_avg" : None,
			"rtt_max" : None,
			"rtt_mdev" : None
		}

		# Execução do ping
		try:
			result = await asyncio.create_subprocess_shell(f"ping -c {count} -W {timeout} {hostname}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = await result.communicate()
			output = stdout.decode('utf-8')
			error = stderr.decode('utf-8')
		except Exception as e:
			logger.error(f"Comando de ping falhou para o host {hostname}: {e}")
			return None
		if result.returncode != 0:
			logger.error(f"Comando de ping falhou para o host {hostname}: {error}")
			return None

		# Busca estatísticas de perda de pacote no output do ping
		try:
			packet_loss_expression = re.search(r"(\d+(\.\d+)?)% packet loss", output)
			packet_loss_raw = float(packet_loss_expression.group(1)) if packet_loss_expression else None
		except Exception as e:
			logger.error(f"Erro ao processar saída do comando de ping para o host {hostname}: {e}")
			return None
		#packet_loss_decimal = packet_loss_raw/100

		# Busca estatísticas de latência no output do ping
		try:
			rtt_expression = re.search(r"rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms", output)
			rtt_min = float(rtt_expression.group(1))
			rtt_avg = float(rtt_expression.group(2))
			rtt_max = float(rtt_expression.group(3))
			rtt_mdev = float(rtt_expression.group(4))
		except Exception as e:
			logger.error(f"Erro ao processar saída do comando de ping para o host {hostname}: {e}")
			return None

		#results["packet_loss"] = packet_loss_decimal
		results["packet_loss"] = packet_loss_raw
		results["rtt_min"] = rtt_min
		results["rtt_avg"] = rtt_avg
		results["rtt_max"] = rtt_max
		results["rtt_mdev"] = rtt_mdev
		return results
