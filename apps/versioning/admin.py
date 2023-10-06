from django.contrib import admin

from apps.versioning.models import Batch, Source

admin.site.register(Batch)
admin.site.register(Source)
