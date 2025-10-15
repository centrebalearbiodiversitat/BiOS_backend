from django.contrib import admin

class ReadOnlyBatch(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		if not hasattr(self, "readonly_fields"):
			self.readonly_fields = ("batch",)
		else:
			self.readonly_fields = list(self.readonly_fields) + ["batch",]
