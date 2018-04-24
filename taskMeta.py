class TaskMeta(object):
	productId=-1
	state=-1
	error=""
	session=None
	compressUrl=""
	fileUrl=""
	def  __init__(self,productId, state,session):
		self.productId = productId
		self.state = state
		self.session = session
