class Constants:

	#### STATUSES ####

	STATUS_OK = 0

	# File statuses
	STATUS_FAIL_ENOENT = 1
	STATUS_FAIL_ENOPERM = 2

	STATUS_FAIL_INSUFARGS = 3

	STATUS_FAIL_TOOMANYITERS = 4

	STATUS_FAIL_INCOMPMETA = 5

	########

	MAX_SOCKET_QUEUE = 5
	BUFFER_SIZE = 10 * 1024 * 1024

	def __init__(self):
		pass


CONSTANTS = Constants()
