from django.contrib import admin
from .models import *


admin.site.register(CustomUser)
admin.site.register(additional_data)

admin.site.register(classes)
admin.site.register(standard)
admin.site.register(subject)
admin.site.register(daily_schedule)
admin.site.register(income_details)


