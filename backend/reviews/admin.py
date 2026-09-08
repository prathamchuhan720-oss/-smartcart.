from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        for review in queryset:
            review.update_product_rating()
        self.message_user(request, f"Selected reviews have been approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        for review in queryset:
            review.update_product_rating()
        self.message_user(request, f"Selected reviews have been marked unapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"
