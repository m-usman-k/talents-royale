from django.contrib import admin
from .models import CustomUser, EmailConfirmationToken, Arena, Contestant, Vote, TokenTransaction, Payment

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(EmailConfirmationToken)
admin.site.register(Arena)
admin.site.register(Contestant)
admin.site.register(Vote)
admin.site.register(TokenTransaction)
admin.site.register(Payment)
