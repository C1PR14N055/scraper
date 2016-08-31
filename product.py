import json

class Product:
	def __init__(self):
		#common product attrs
		self.parent_name = None
		self.parent_url = None
		self.href = None
		self.title = None
		self.subtitle = None
		self.price = None
		self.img = None
		self.variation = None
		self.included = None
		#end common product attrs

		#product details
		self.product_details_title = None
		self.product_details = None
		self.product_detail_common_attributes_title = None
		self.product_detail_common_attributes = None
		self.product_detail_primary_uses_title = None
		self.product_detail_primary_uses = None
		#end product details

		#performance imgs
		self.product_detail_performance_features_imgs = []
		#end performance imgs
		
		#table with pdfs/manuals
		self.product_pdfs_table = None

		#tech data
		self.tehnical_data = None
		
		#product accessories urls
		self.accessoriesLinks = []

		#product consumables urls
		self.consumablesLinks = []

	def to_json(self):
		return json.dumps(self.__dict__, sort_keys=True, indent=4)
