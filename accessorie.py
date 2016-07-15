import json

class Accessorie:
	def __init__(self):
		#common product attrs
		self.href = None
		self.title = None
		self.price = None
		self.img = None
		self.included = None
		#end common product attrs

		#product details
		self.product_details = None
		#end product details

		#tech data
		self.tehnical_data = None

	def to_json(self):
		return json.dumps(self.__dict__, sort_keys=True, indent=4)