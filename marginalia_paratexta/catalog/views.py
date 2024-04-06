from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.contenttypes.models import ContentType
from catalog.filters import ProductFilter
from .models import BoardGame, Comic, Country, Creation, Genre, KeyWord, Knot, Movie, Musica, Novel, Product, Theatre, Videogame
from django.contrib import messages
from .forms import SignUpForm
import plotly.graph_objs as go
from functools import reduce
from operator import or_
from django.db.models import Q
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Procesar el formulario y realizar el registro
            # Ejemplo: Guardar el usuario en la base de datos
            user = form.save()
            
            # Puedes agregar acciones adicionales aquí si es necesario, como enviar un correo de confirmación
            
            return redirect('login')  # Redirigir al inicio de sesión después del registro
        else:
            error_messages = form.errors.values()  # Obtener todos los mensajes de error
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'registration/signup.html', {'form': form})

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_products = Product.objects.all().count()

    context = {
        'num_products': num_products,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class ProductListView( generic.ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = 'catalog/product_list.html'
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        any_condition = super().get_queryset().none()
        devolverVacio = True
        if 'genero' in self.request.GET:
            generos = self.request.GET.getlist('genero')
            any_condition = queryset.filter(creation__genero__id__in=generos).distinct()
            devolverVacio = False
        if 'palabras_clave' in self.request.GET:
            keywords = self.request.GET.getlist('palabras_clave')
            any_condition = any_condition | queryset.filter(creation__palabras_clave__id__in=keywords).distinct()
            devolverVacio = False
        all_conditions = self.filterset.qs
        if devolverVacio:
            any_condition=[]
        else:
            any_condition = any_condition.exclude(id__in=all_conditions.values_list('id', flat=True))
            any_condition = any_condition.order_by('title')
        all_conditions = all_conditions.order_by('title')
                
        return all_conditions, any_condition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_conditions, any_condition = self.get_queryset()
        context['all_conditions'] = all_conditions
        context['any_condition'] = any_condition
        context['filter'] = self.filterset
        return context

class KnotListView(generic.ListView):
    model = Knot
    context_object_name = 'knot_list'

class ProductDetailView(generic.DetailView):
    model = Product

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user_belongs_to_group = request.user.groups.filter(name='Marginalia Member').exists()

    if isinstance(product.creation, Movie):    
        context = {
            'product': product,
            'type': "Película",
            'user_belongs_to_group': user_belongs_to_group
        }
    elif isinstance(product.creation, Videogame):    
        context = {
            'product': product,
            'type': "Videojuego",
            'user_belongs_to_group': user_belongs_to_group
        } 
    elif isinstance(product.creation, Musica):    
        context = {
            'product': product,
            'type': "Música",
            'user_belongs_to_group': user_belongs_to_group
        } 
    elif isinstance(product.creation, BoardGame):    
        context = {
            'product': product,
            'type': "Juego de mesa",
            'user_belongs_to_group': user_belongs_to_group
        } 
    elif isinstance(product.creation, Comic):    
        context = {
            'product': product,
            'type': "Comic",
            'user_belongs_to_group': user_belongs_to_group
        } 
    elif isinstance(product.creation, Novel):    
        context = {
            'product': product,
            'type': "Novela",
            'user_belongs_to_group': user_belongs_to_group
        }
    elif isinstance(product.creation, Theatre):    
        context = {
            'product': product,
            'type': "Teatro",
            'user_belongs_to_group': user_belongs_to_group
        }  
    else :
        context = {
            'product': product,
            'type': "Serie de television",
            'user_belongs_to_group': user_belongs_to_group
        }
    return render(request, 'catalog/product_detail.html', context=context)

def knot_detail_view(request, pk):
    knot = get_object_or_404(Knot, pk=pk)

    context = {
        'knot': knot,
    }

    return render(request, 'catalog/knot_detail.html', context=context)


def get_creaciones(request, query, generos=[], formatos=[], paises=[], keyWords=[]):
    year_range_str = request.GET.get('year_range', '10')
    year_range = int(year_range_str)
    paises_keywords = False
    keywords_paises_formato= False
    genero_keywords_paises_formato = False
    genero_keywords_formato = False
    if len(generos) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(genero__name=genero) for genero in generos]
        if query == 'OR':
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
        titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años'

        if len(keyWords) > 0:
            creaciones3 = Creation.objects.all()
            consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keyWords]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                for consulta_q in consultas_q:
                    creaciones = creaciones.filter(consulta_q)
            titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años y con palabras clave: {", ".join(keyWords)}'
            creaciones = creaciones.distinct()
            if len(formatos) > 0:
                genero_keywords_formato= True
            if len(paises) > 0:
                paises_keywords = True
                if len(formatos) > 0:
                    genero_keywords_paises_formato= True  

        if len(paises) > 0:
            creaciones3 = Creation.objects.all()
            consultas_q = [Q(paises__name=pais) for pais in paises]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                for consulta_q in consultas_q:
                    creaciones = creaciones.filter(consulta_q)
            titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años y con paises: {", ".join(paises)}'
            if paises_keywords:
                titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años, con palabras clave: {", ".join(keyWords)} y paises: {", ".join(paises)}'

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            
            if genero_keywords_paises_formato:
                titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con formato: {", ".join(formatos_nombres)}, género:  {", ".join(generos)} y palabras clave: {", ".join(keyWords)}'
            elif genero_keywords_formato:
                titulo = f'Número de Creaciones con formato {", ".join(formatos_nombres)} cada {year_range} años con género:  {", ".join(generos)} y palabras clave: {", ".join(keyWords)}'
            else:
                titulo = f'Número de Creaciones con formato: {", ".join(formatos_nombres)} cada {year_range} años con género: {", ".join(generos)}'

    elif len(keyWords) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keyWords]
        if query == 'OR':
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
        titulo = f'Número de Creaciones cada {year_range} años con palabras clave: {", ".join(keyWords)}'
        if len(paises) > 0:
            creaciones3 = Creation.objects.all()
            consultas_q = [Q(paises__name=pais) for pais in paises]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                for consulta_q in consultas_q:
                    creaciones = creaciones.filter(consulta_q)
            titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con palabras clave: {", ".join(keyWords)}'
            if len(formatos)>0:
                keywords_paises_formato=True

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            titulo = f'Número de Creaciones con formato: {", ".join(formatos_nombres)} cada {year_range} años con palabras clave: {", ".join(keyWords)}'
            if keywords_paises_formato:
                titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con formato: {", ".join(formatos_nombres)} y palabras clave: {", ".join(keyWords)}'
                
    elif len(paises) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(paises__name=pais) for pais in paises]
        if query == 'OR':
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
        titulo = f'Número de Creaciones cada {year_range} años con paises: {", ".join(paises)}'
        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
                creaciones = creaciones.distinct()
            else:
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con formato: {", ".join(formatos_nombres)}'
                
    elif len(formatos) > 0:
        creaciones = Creation.objects.all()
        content_types = ContentType.objects.filter(model__in=formatos)
        consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        formatos_nombres = [content_type.name for content_type in content_types]
        titulo = f'Número de Creaciones cada {year_range} años con formato: {", ".join(formatos_nombres)}'
    else:
        creaciones = Creation.objects.all()
        titulo = f'Número de Creaciones cada {year_range} años'
    return titulo, creaciones

def grafico_barras_view(request):
    generos = request.GET.getlist('genero') if 'genero' in request.GET else []
    formatos = request.GET.getlist('formato_ficha') if 'formato_ficha' in request.GET else []
    paises = request.GET.getlist('paises') if 'paises' in request.GET else []
    keyWords = request.GET.getlist('keywords') if 'keywords' in request.GET else []
    year_range_str = request.GET.get('year_range', '10')
    year_range = int(year_range_str)
    anio_inicio_str = request.GET.get('anio_inicio', '1930')
    anio_fin_str = request.GET.get('anio_fin', '2030')
    year_range_str = request.GET.get('year_range', '10')
    query = request.GET.get('query')
    anos = range(1930, 2031, 10)
    # Convertir los valores a enteros
    anio_inicio = int(anio_inicio_str)
    anio_fin = int(anio_fin_str)
    titulo, creaciones = get_creaciones(request, query, generos, formatos, paises, keyWords)
    # Lógica para generar el gráfico de barras
    # Por ejemplo, contar el número de creaciones por década
    decadas = range(anio_inicio, anio_fin, year_range)

    if (year_range == 5):
        num_creaciones_por_decada = [creaciones.filter(publication_year__range=(decada, decada + 4)).count() for decada in decadas]
    else:
        num_creaciones_por_decada = [creaciones.filter(publication_year__range=(decada, decada + 9)).count() for decada in decadas]
    
    # Crear el gráfico de barras
    data = {
        'labels': list(decadas),
        'values': num_creaciones_por_decada
    }
    rango_anos = [10, 5]
    # Lista de géneros para mostrar en el formulario de filtrado
    lista_paises = Creation.objects.values_list('paises__name', flat=True).distinct().exclude(paises__name=None).order_by('paises__name')
    lista_de_generos = Creation.objects.values_list('genero__name', flat=True).distinct().exclude(genero__name=None).order_by('genero__name')
    lista_de_palabras_clave = Creation.objects.values_list('palabras_clave__name', flat=True).distinct().exclude(palabras_clave__name=None).order_by('palabras_clave__name')
    # Retorna el contexto con los datos del gráfico y la lista de géneros
    return render(request, 'catalog/graph.html', { 'data':json.dumps(data), 'titulo': titulo, 'lista_de_generos': lista_de_generos, 'anos': anos, 
    'rango_anos': rango_anos, 'palabras_clave': lista_de_palabras_clave, 'paises': lista_paises, 'year_range': json.dumps(year_range),
    'formatos_seleccionados': json.dumps(formatos), 'paises_seleccionados': json.dumps(paises), 'keywords_seleccionados': json.dumps(keyWords), 
    'generos_seleccionados': json.dumps(generos),  'query_for': json.dumps(query)})

def year_creations_list(request, year, year_range,query_for, filter1=None, filter2=None, filter3=None, filter4=None):
    # Filtrar las creaciones por país
    filter1 = filter1.split(',') if filter1 else []
    filter2 = filter2.split(',') if filter2 else []
    filter3 = filter3.split(',') if filter3 else []
    filter4 = filter4.split(',') if filter4 else []
    creaciones = Creation.objects.all()
    titulo = f'Creaciones entre los años {year}, {year + year_range}'    
    creaciones = creaciones.filter(publication_year__range=(year, year + (year_range-1)))
    if len(filter1) == 0:
        return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})

    if len(filter4) > 0:
        content_types = ContentType.objects.filter(model__in=filter4)
        consultas_q = [Q(genero__name=genre) for genre in filter1]
        consultas_q.extend([Q(paises__name=pais) for pais in filter2])
        consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter3])
        if query_for == 'OR':
            consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
            consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        titulo = f'Creaciones con Países {", ".join(filter2)} entre {year} y {year + year_range} con formato: {", ".join(filter4)}, género:  {", ".join(filter1)} y palabras clave: {", ".join(filter3)}'
        return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})
    
    if len(filter3) > 0:
        if Genre.objects.filter(name=filter1[0]).exists():
            consultas_q = [Q(genero__name=genre) for genre in filter1]
            if Country.objects.filter(name=filter2[0]).exists():
                consultas_q.extend([Q(paises__name=pais) for pais in filter2])
                if KeyWord.objects.filter(name=filter3[0]).exists():
                    consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter3])
                    titulo = f'Creaciones con Países {", ".join(filter2)} entre {year} y {year + year_range} con género: {", ".join(filter1)} y palabras clave: {", ".join(filter3)}'
                    if query_for == 'OR':
                        consulta_final = reduce(or_, consultas_q)
                        creaciones = creaciones.filter(consulta_final).distinct()
                    else:
                        for consulta_q in consultas_q:
                            creaciones = creaciones.filter(consulta_q)
                else:
                    content_types = ContentType.objects.filter(model__in=filter3)
                    if query_for == 'OR':
                        consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                        consulta_final = reduce(or_, consultas_q)
                        creaciones = creaciones.filter(consulta_final).distinct()
                    else:
                        for consulta_q in consultas_q:
                            creaciones = creaciones.filter(consulta_q)
                        consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                        consulta_final = reduce(or_, consultas_q)
                        creaciones = creaciones.filter(consulta_final).distinct() 
                    titulo = f'Creaciones con Países {", ".join(filter2)} entre {year} y {year + year_range} con formato: {", ".join(filter3)} y género: {", ".join(filter1)}'
            else:
                content_types = ContentType.objects.filter(model__in=filter3)
                consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter2])
                if query_for == 'OR':
                    consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
                    consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()       
                titulo = f'Creaciones entre {year} y {year + year_range} con formato: {", ".join(filter3)}, género:  {", ".join(filter1)} y palabras clave: {", ".join(filter2)}'
        else:
            content_types = ContentType.objects.filter(model__in=filter3)
            consultas_q = ([Q(paises__name=pais) for pais in filter1])
            consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter2])
            if query_for == 'OR':
                consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            else:
                for consulta_q in consultas_q:
                    creaciones = creaciones.filter(consulta_q)
                consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct() 
            titulo = f'Número de Creaciones con Países {", ".join(filter1)} entre {year} y {year + year_range} con formato: {", ".join(filter3)} y palabras clave: {", ".join(filter2)}'
        return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})

    if len(filter2) > 0:
        if Genre.objects.filter(name=filter1[0]).exists():
            consultas_q = [Q(genero__name=genre) for genre in filter1]
            if Country.objects.filter(name=filter2[0]).exists():
                consultas_q.extend([Q(paises__name=pais) for pais in filter2])
                if query_for == 'OR':
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
                titulo = f'Creaciones con Países {", ".join(filter2)} entre {year} y {year + year_range} con género: {", ".join(filter1)}'
            elif KeyWord.objects.filter(name=filter2[0]).exists():
                consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter2])
                if query_for == 'OR':
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
                titulo = f'Creaciones entre {year} y {year + year_range} con género: {", ".join(filter1)} y  palabras clave: {", ".join(filter2)}'
            else:
                content_types = ContentType.objects.filter(model__in=filter2)
                if query_for == 'OR':
                    consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
                    consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct() 
                titulo = f'Creaciones entre {year} y {year + year_range} con formato: {", ".join(filter2)} y género: {", ".join(filter1)}'
        elif Country.objects.filter(name=filter1[0]).exists():
            consultas_q = ([Q(paises__name=pais) for pais in filter1])
            if KeyWord.objects.filter(name=filter2[0]).exists():
                consultas_q.extend([Q(palabras_clave__name=keyWord) for keyWord in filter2])
                titulo = f'Creaciones con Países {", ".join(filter2)} entre {year} y {year + year_range} con palabras clave: {", ".join(filter2)}'
                if query_for == 'OR':
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
            else:
                content_types = ContentType.objects.filter(model__in=filter2)
                if query_for == 'OR':
                    consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct()
                else:
                    for consulta_q in consultas_q:
                        creaciones = creaciones.filter(consulta_q)
                    consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                    consulta_final = reduce(or_, consultas_q)
                    creaciones = creaciones.filter(consulta_final).distinct() 
                titulo = f'Creaciones con Países {", ".join(filter1)} entre {year} y {year + year_range} con formato: {", ".join(filter2)}'
        else:
            content_types = ContentType.objects.filter(model__in=filter2)
            consultas_q = ([Q(palabras_clave__name=keyWord) for keyWord in filter1])
            if query_for == 'OR':
                consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            else:
                for consulta_q in consultas_q:
                    creaciones = creaciones.filter(consulta_q)
                consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct() 
            titulo = f'Creaciones entre {year} y {year + year_range} con formato: {", ".join(filter2)} y palabras clave: {", ".join(filter1)}'
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})

    if Genre.objects.filter(name=filter1[0]).exists():
        consultas_q = [Q(genero__name=genre) for genre in filter1]
        titulo = f'Creaciones entre {year} y {year + year_range} con género:  {", ".join(filter1)}'

    elif Country.objects.filter(name=filter1[0]).exists():
        consultas_q = [Q(paises__name=pais) for pais in filter1]
        titulo = f'Creaciones con Países {", ".join(filter1)} entre {year} y {year + year_range}'

    elif KeyWord.objects.filter(name=filter1[0]).exists():
        consultas_q = ([Q(palabras_clave__name=keyWord) for keyWord in filter1])
        titulo = f'Creaciones entre {year} y {year + year_range} con palabras clave: {", ".join(filter1)}'
    else:
        content_types = ContentType.objects.filter(model__in=filter1)
        titulo = f'Creaciones entre {year} y {year + year_range} con formato: {", ".join(filter1)}'
        consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})
    if query_for == 'OR':
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
    else:
        for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
    return render(request, 'catalog/country_creations_list.html', {'creations': creaciones, 'titulo': titulo})
    
def world_map_view(request):
    formatos = request.GET.getlist('formato_ficha') if 'formato_ficha' in request.GET else []
    keyWords = request.GET.getlist('keywords') if 'keywords' in request.GET else []
    query = request.GET.get('query') 
    titulo1 = f'Número de Creaciones por país'
    if len(keyWords) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keyWords]
        if query == 'OR':
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
        titulo1 = f'Número de Creaciones por país con palabras clave: {", ".join(keyWords)}'

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            if query == 'OR':
                consulta_final = reduce(or_, consultas_q)
                creaciones3 = creaciones3.filter(consulta_final).distinct()
                creaciones = creaciones | creaciones3
            else:
                consulta_final = reduce(or_, consultas_q)
                creaciones = creaciones.filter(consulta_final).distinct()
            creaciones = creaciones.distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            titulo1 = f'Número de Creaciones por país con formato: {", ".join(formatos_nombres)} y palabras clave: {", ".join(keyWords)}'

    elif len(formatos) > 0:
        creaciones = Creation.objects.all()
        content_types = ContentType.objects.filter(model__in=formatos)
        consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
        if query == 'OR':
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
        formatos_nombres = [content_type.name for content_type in content_types]
        titulo1 = f'Número de Creaciones por país con formato: {", ".join(formatos_nombres)}'

    else:
        creaciones = Creation.objects.all()

    # Contar el número de creaciones por país
    country_creations_count = {}
    for creation in creaciones:
        for country in creation.paises.all():
            country_iso = country.iso_code 
            if country_iso not in country_creations_count:
                country_creations_count[country_iso] = 1
            else:
                country_creations_count[country_iso] += 1

    # Crear los datos del mapa
    data = [go.Choropleth(
        locations=list(country_creations_count.keys()),
        z=list(country_creations_count.values()),
        locationmode='ISO-3',
        colorscale=[[0, 'rgb(200, 255, 200)'], [1, 'rgb(0, 100, 0)']],
        marker_line_color='black',
        marker_line_width=0.5,
    )]

    # Crear el diseño del mapa
    layout = go.Layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        width=600,  # Ancho del mapa en píxeles
        height=400,  # Alto del mapa en píxeles
    )

    # Crear la figura del mapa
    fig = go.Figure(data=data, layout=layout)
    formatos_seleccionados = json.dumps(formatos)
    keywords_seleccionadas = json.dumps(keyWords)
    query_for = json.dumps(query)
    # Convertir la figura a JSON para enviarla a la plantilla
    graph_json = fig.to_json()
    lista_de_palabras_clave = Creation.objects.values_list('palabras_clave__name', flat=True).distinct().exclude(palabras_clave__name=None).order_by('palabras_clave__name')
    return render(request, 'catalog/map.html', {'title': titulo1, 'graph_json': graph_json, 'palabras_clave': lista_de_palabras_clave, 'formatos_seleccionados': formatos_seleccionados, 'keywords_seleccionadas': keywords_seleccionadas, 'query_for': query_for})

def country_creations_list(request, country_iso, query_for=None, formatos=None, keywords=None):
    # Filtrar las creaciones por país
    formatos_list = formatos.split(',') if formatos else []
    keywords_list = keywords.split(',') if keywords else []
    creations = Creation.objects.filter(paises__iso_code=country_iso)
    country_name = Country.objects.get(iso_code=country_iso).name
    titulo = f'Creaciones del País {country_name}'    
    if len(keywords_list) > 0:
        content_types = ContentType.objects.filter(model__in=formatos_list)
        creaciones = Creation.objects.all()
        if query_for == 'OR':
            consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keywords_list]
            consultas_q.extend([Q(polymorphic_ctype=content_type) for content_type in content_types])
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()
        else:
            consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keywords_list]
            for consulta_q in consultas_q:
                creaciones = creaciones.filter(consulta_q)
            consultas_q = ([Q(polymorphic_ctype=content_type) for content_type in content_types])
            consulta_final = reduce(or_, consultas_q)
            creaciones = creaciones.filter(consulta_final).distinct()   
        
        titulo = f'Creaciones del País {country_name} con palabras clave {", ".join(keywords_list)} o formato {", ".join(formatos_list)}'
    else:
        creaciones = Creation.objects.all()
    creations = creaciones.filter(paises__iso_code=country_iso)
    # Aplicar los filtros
    return render(request, 'catalog/country_creations_list.html', {'creations': creations, 'titulo': titulo})

def country_creations_list_formato(request, country_iso, formatos=None):
    # Filtrar las creaciones por país
    formatos_list = formatos.split(',') if formatos else []
    creations = Creation.objects.filter(paises__iso_code=country_iso)
    country_name = Country.objects.get(iso_code=country_iso).name
    content_types = ContentType.objects.filter(model__in=formatos_list)
    creaciones = Creation.objects.all()
    consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
    consulta_final = reduce(or_, consultas_q)
    creaciones = creaciones.filter(consulta_final).distinct()
    titulo = f'Creaciones del País {country_name} con formato {", ".join(formatos_list)}'

    creations = creaciones.filter(paises__iso_code=country_iso)
    # Aplicar los filtros
    return render(request, 'catalog/country_creations_list.html', {'creations': creations, 'titulo': titulo})

def country_creations_list_keyWord(request, query_for, country_iso, keyWords=None):
    # Filtrar las creaciones por país
    keywords_list = keyWords.split(',') if keyWords else []
    creations = Creation.objects.filter(paises__iso_code=country_iso)
    country_name = Country.objects.get(iso_code=country_iso).name
    creaciones = Creation.objects.all()
    consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keywords_list]   
    if query_for == 'OR': 
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
    else:
        for consulta_q in consultas_q:
            creaciones = creaciones.filter(consulta_q)
    titulo = f'Creaciones del País {country_name} con palabras clave {", ".join(keywords_list)}'

    creations = creaciones.filter(paises__iso_code=country_iso)
    # Aplicar los filtros
    return render(request, 'catalog/country_creations_list.html', {'creations': creations, 'titulo': titulo})

def word_cloud(request):
    generos = request.GET.getlist('genero') if 'genero' in request.GET else []
    formatos = request.GET.getlist('formato_ficha') if 'formato_ficha' in request.GET else []
    paises = request.GET.getlist('paises') if 'paises' in request.GET else []
    anio_inicio_str = request.GET.get('anio_inicio', '1930')
    anio_fin_str = request.GET.get('anio_fin', '2030')
    anio_inicio = int(anio_inicio_str)
    anio_fin = int(anio_fin_str)
    query = request.GET.get('query')

    _, creaciones = get_creaciones(request, query, generos, formatos, paises)

    creaciones = creaciones.filter(publication_year__range=(anio_inicio, anio_fin)).distinct()
    palabras_clave = creaciones.values_list('palabras_clave__name', flat=True)
    
    word_counter = {}

    if len(palabras_clave) == 0:
        word_counter['Nothing'] = 1
    else:
        for palabra in palabras_clave:
            if palabra in word_counter:
                word_counter[palabra] += 1
            else:
                word_counter[palabra] = 1
    word_counter = {key: value for key, value in word_counter.items() if key is not None}    # Crear el objeto WordCloud con la fuente TTF especificada
    wordcloud1 = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counter)

    buffer = BytesIO()
    wordcloud1.to_image().save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    lista_paises = Creation.objects.values_list('paises__name', flat=True).distinct().exclude(paises__name=None).order_by('paises__name')
    lista_de_generos = Creation.objects.values_list('genero__name', flat=True).distinct().exclude(genero__name=None).order_by('genero__name')
    anos = range(1930, 2031, 10)
    # Pasar el wordcloud como una cadena base64 al contexto de renderización
    context = {'wordcloud_image': img_str, 'lista_de_generos': lista_de_generos, 'anos': anos, 'paises': lista_paises}

    return render(request, 'catalog/wordcloud.html', context)
    
def correo_invalido(request):
    return render(request, 'catalog/mail_invalid.html')

def contraseña_enviada(request):
    return render(request, 'catalog/password_sent.html')

def recuperar_contraseña_form(request):
    return render(request, 'catalog/reset_password_form.html')

from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
import string
def recuperar_contraseña(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user:
            # Generar una nueva contraseña aleatoria
            nueva_contraseña = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            # Actualizar la contraseña del usuario en la base de datos
            user.set_password(nueva_contraseña)
            user.save()
            # Enviar la nueva contraseña por correo electrónico
            send_mail(
                'Recuperación de Contraseña',
                f'Su nueva contraseña es: {nueva_contraseña}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return render(request, 'catalog/password_sent.html')
        else:
            return render(request, 'catalog/mail_invalid.html')
    return render(request, 'catalog/reset_password_form.html')
