from rango.models import Category

x = 1
list = []
for categories in Category.objects.values():
    list.append([x, (categories['name'])])
    x+=1
CATEGORY_CHOICES = list
