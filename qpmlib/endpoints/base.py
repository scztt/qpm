class EndpointBase:

	@classmethod
	def validate(cls, target):
		return False

	def __init__(self, validated_target):
		self.target = validated_target

	def verify(self):
		return False

	def get_to(self, local_dir):
		pass