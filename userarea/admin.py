from django.contrib import admin

# Register your models here.

from .models import Category, Product, ProductImage, Brand, Size, Color


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "grandparent")

    def grandparent(self, obj):
        if obj.parent and obj.parent.parent:
            return obj.parent.parent.name
        return None

    grandparent.short_description = "Grandparent Category"


admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage)
admin.site.register(Product)


class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "parent_category", "grandparent_category")
    list_filter = ("category",)
    search_fields = (
        "name",
        "category__name",
        "category__parent__name",
        "category__parent__parent__name",
    )

    def parent_category(self, obj):
        if obj.category and obj.category.parent:
            return obj.category.parent.name
        return None

    parent_category.short_description = "Parent Category"

    def grandparent_category(self, obj):
        if obj.category and obj.category.parent and obj.category.parent.parent:
            return obj.category.parent.parent.name
        return None

    grandparent_category.short_description = "Grandparent Category"


admin.site.register(Brand, BrandAdmin)
from .models import Size


class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "parent_category", "grandparent_category")
    list_filter = ("category",)
    search_fields = (
        "name",
        "category__name",
        "category__parent__name",
        "category__parent__parent__name",
    )

    def parent_category(self, obj):
        if obj.category and obj.category.parent:
            return obj.category.parent.name
        return None

    parent_category.short_description = "Parent Category"

    def grandparent_category(self, obj):
        if obj.category and obj.category.parent and obj.category.parent.parent:
            return obj.category.parent.parent.name
        return None

    grandparent_category.short_description = "Grandparent Category"


admin.site.register(Size, SizeAdmin)
admin.site.register(Color)
