from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Pessoa, Diario
from django.db.models import Count 
from django.utils.safestring import mark_safe
import json

def home(request):
    textos = Diario.objects.order_by('create_at')[:3]
    pessoas_com_contagem = Pessoa.objects.annotate(qtd_diarios=Count('diario'))
    nomes = [pessoa.nome for pessoa in pessoas_com_contagem]
    qtds = [pessoa.qtd_diarios for pessoa in pessoas_com_contagem]

    # Prepare o dicionário como JSON para o template
    chart_data = json.dumps({'labels': nomes, 'data': qtds})

    return render(request, 'home.html', {
        'textos': textos,
        'chart_data': mark_safe(chart_data),  # Torna seguro para uso no template
    })





def escrever(request):
    if request.method == "GET":
        pessoas = Pessoa.objects.all()
        textos = Diario.objects.order_by('create_at')   
        return render(request, 'escrever.html', {'pessoas': pessoas, 'textos': textos})
    else:
        titulo = request.POST.get("titulo")
        tags = request.POST.getlist("tags")
        pessoas = request.POST.getlist("pessoas")
        texto = request.POST.get("texto")

        if len(titulo.strip()) == 0 or len(texto.strip()) == 0:
            return redirect('escrever')

        diario = Diario(
            titulo=titulo,
            texto=texto
        )
        diario.set_tags(tags)
        diario.save()
        
        pessoa_objs = Pessoa.objects.filter(id__in=pessoas)
        diario.pessoas.add(*pessoa_objs)
        diario.save()

        '''for i in pessoas:
            pessoa = Pessoa.objects.get(id=i)
            diario.pessoas.add(pessoa)'''

        #TODO: Mensagens e erro e sucesso
        
        return redirect('escrever')
def cadastrar_pessoa(request):
    if request.method == 'GET':
        return render(request, 'pessoa.html')
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')

        pessoa = Pessoa(
            nome=nome,
            foto=foto
        )
        pessoa.save()
        return redirect('escrever')

def dia(request):
    data = request.GET.get('data')
    if data:
        data_formatada = datetime.strptime(data, '%Y-%m-%d')
        diarios = Diario.objects.filter(
            create_at__gte=data_formatada,
            create_at__lt=data_formatada + timedelta(days=1)  # Use timedelta corretamente
        )
    else:
        diarios = Diario.objects.none()  # Retorna vazio se a data não for fornecida

    return render(request, 'dia.html', {
        'diarios': diarios,
        'total': diarios.count(),
        'data': data,
    })

def excluir_dia(request):
    dia = datetime.strptime(request.GET.get('data'), '%Y-%m-%d')
    diarios = Diario.objects.filter(create_at__gte=dia).filter(create_at__lte=dia + timedelta(days=1))
    diarios.delete()
    return redirect('escrever')
