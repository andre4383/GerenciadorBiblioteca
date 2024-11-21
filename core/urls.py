# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('livros/', views.lista_livros, name='lista_livros'),
    path('livros/cadastrar/', views.cadastrar_livro, name='cadastrar_livro'),
    path('livros/emprestar/<int:livro_id>/', views.emprestar_livro, name='emprestar_livro'),
    path('emprestimos/', views.meus_emprestimos, name='meus_emprestimos'),
    path('emprestimos/devolver/<int:emprestimo_id>/', views.devolver_livro, name='devolver_livro'),
    path('livros/<int:livro_id>/remover/', views.remover_livro, name='remover_livro'),
]