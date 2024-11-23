from django.db import models
from django.contrib.auth.models import User

class Autor(models.Model):
    nome = models.CharField(max_length=200)
    biografia = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Autores"

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    data_publicacao = models.DateField()
    quantidade_total = models.IntegerField()
    quantidade_disponivel = models.IntegerField()
    
    def __str__(self):
        return self.titulo

class Emprestimo(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('E', 'Emprestado'),
        ('D', 'Devolvido'),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.livro.titulo} - {self.usuario.username}"
