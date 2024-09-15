# core/context_processors.py

from userarea.models import Category


def category_context(request):
    main_categories = Category.objects.filter(parent__isnull=True)
    return {
        "main_categories": main_categories,
    }
