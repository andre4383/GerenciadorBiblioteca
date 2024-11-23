from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Livro, Emprestimo, Autor
from django import forms
from datetime import datetime, timedelta


def home(request):
    return render(request, 'core/home.html')


class LivroForm(forms.ModelForm):
    autor_nome = forms.CharField(max_length=100, widget=forms.TextInput(), label='Autor')
    
    class Meta:
        model = Livro
        fields = ['titulo', 'isbn', 'data_publicacao', 
                 'quantidade_total', 'quantidade_disponivel']
        widgets = {
            'data_publicacao': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def save(self, commit=True):
        livro = super().save(commit=False)
        autor_nome = self.cleaned_data['autor_nome']
        autor, created = Autor.objects.get_or_create(nome=autor_nome)
        livro.autor = autor
        if commit:
            livro.save()
        return livro


def cadastrar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livro cadastrado com sucesso!')
            return redirect('core:lista_livros')
    else:
        form = LivroForm()
    
    return render(request, 'core/cadastrar_livro.html', {'form': form})


def lista_livros(request):
    livros = Livro.objects.all()
    return render(request, 'core/lista_livros.html', {'livros': livros})


def remover_livro(request, livro_id):
    livro = get_object_or_404(Livro, pk=livro_id)
    
    # Verificar se existem empréstimos ativos
    emprestimos_ativos = Emprestimo.objects.filter(
        livro=livro,
        data_devolucao_real__isnull=True  # Alterado aqui
    ).exists()
    
    if emprestimos_ativos:
        messages.error(request, 'Não é possível remover este livro pois existem empréstimos ativos.')
        return redirect('core:home')
    
    titulo = livro.titulo
    livro.delete()
    messages.success(request, f'Livro "{titulo}" removido com sucesso!')
    return redirect('core:home')
@login_required
def emprestar_livro(request, livro_id):
    livro = get_object_or_404(Livro, pk=livro_id)
    
    # Verificar se o usuário já tem este livro emprestado
    emprestimo_existente = Emprestimo.objects.filter(
        usuario=request.user,
        livro=livro,
        data_devolucao__isnull=True
    ).exists()
    
    if emprestimo_existente:
        messages.error(request, 'Você já possui um empréstimo ativo deste livro.')
        return redirect('core:lista_livros')
    
    # Verificar se o livro está disponível
    if livro.quantidade_disponivel <= 0:
        messages.error(request, 'Este livro não está disponível para empréstimo no momento.')
        return redirect('core:lista_livros')
    
    try:
        # Criar registro de empréstimo
        data_emprestimo = datetime.now()
        data_prevista_devolucao = data_emprestimo + timedelta(days=14)  # 14 dias de prazo
        
        emprestimo = Emprestimo.objects.create(
            usuario=request.user,
            livro=livro,
            data_emprestimo=data_emprestimo,
            data_prevista_devolucao=data_prevista_devolucao
        )
        
        # Atualizar quantidade disponível
        livro.quantidade_disponivel -= 1
        livro.save()
        
        messages.success(request, f'Livro "{livro.titulo}" emprestado com sucesso! '
                                f'Data prevista para devolução: {data_prevista_devolucao.strftime("%d/%m/%Y")}')
        
    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao processar o empréstimo. Tente novamente.')
    
    return redirect('core:lista_livros')


@login_required
def devolver_livro(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, pk=emprestimo_id, usuario=request.user)
    
    if emprestimo.data_devolucao:
        messages.error(request, 'Este livro já foi devolvido.')
        return redirect('core:meus_emprestimos')
    
    try:
        # Atualizar registro de empréstimo
        emprestimo.data_devolucao = datetime.now()
        emprestimo.save()
        
        # Atualizar quantidade disponível do livro
        livro = emprestimo.livro
        livro.quantidade_disponivel += 1
        livro.save()
        
        messages.success(request, f'Livro "{livro.titulo}" devolvido com sucesso!')
        
    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao processar a devolução. Tente novamente.')
    
    return redirect('core:meus_emprestimos')


@login_required
def meus_emprestimos(request):
    emprestimos_ativos = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao__isnull=True
    ).order_by('-data_emprestimo')
    
    emprestimos_anteriores = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao__isnull=False
    ).order_by('-data_devolucao')
    
    context = {
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_anteriores': emprestimos_anteriores,
    }
    
    return render(request, 'core/meus_emprestimos.html', context)