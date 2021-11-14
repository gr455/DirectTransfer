import time

class Progress:
	def __init__(self, totalBytes, transferName):
		self.transferName = transferName
		self.totalBytes = totalBytes
		self.completedBytes = 0
		self.currentTransferRate = 0
		self.lastUpdated = time.time()

	def percentCompletion(self):
		return (self.completedBytes / self.totalBytes) * 100

	def update(self, newBytesRecvd):
		timeDelta = time.time() - self.lastUpdated
		self.lastUpdated = time.time()
		self.completedBytes += newBytesRecvd
		self.currentTransferRate = ( newBytesRecvd / timeDelta ) 
