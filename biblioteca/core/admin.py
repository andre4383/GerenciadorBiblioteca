from django.contrib import admin
from .models import Autor, Categoria, Livro, Emprestimo

admin.site.register(Autor)
admin.site.register(Categoria)
admin.site.register(Livro)
admin.site.register(Emprestimo)