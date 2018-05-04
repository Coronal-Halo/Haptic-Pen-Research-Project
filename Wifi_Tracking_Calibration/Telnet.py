import telnetlib

# Telnet functions to fetch data from the ESP8266 TCP Server
class TelnetWorkers(object):
	"""
	Creates our connection, holds and handles data.
	"""

	def __init__(self, IP, PORT):
		# IP and PORT are strings
		self.connection = telnetlib.Telnet(IP, PORT)

	def getMoreData(self):
		"""
		Reads STDOUT, splits on and strips '\r\n'.

		Returns list.
		"""
		# 10 means that we're going to timeout after 10 seconds if
		# we don't get any input that satisfies our regex.
		cursor = self.connection.read_until('\r\n', 10)

		return cursor