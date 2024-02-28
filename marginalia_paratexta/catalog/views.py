from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.contenttypes.models import ContentType
from catalog.filters import ProductFilter
from .models import BoardGame, Comic, Country, Creation, Genre, Knot, Movie, Musica, Novel, Product, Theatre, Videogame
from django.contrib import messages
from .forms import SignUpForm
import plotly.graph_objs as go
from functools import reduce
from operator import or_
from django.db.models import Q
from wordcloud import WordCloud
import matplotlib.pyplot as plt
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

def get_creaciones(request):
    generos = request.GET.getlist('genero') if 'genero' in request.GET else []
    formatos = request.GET.getlist('formato_ficha') if 'formato_ficha' in request.GET else []
    paises = request.GET.getlist('paises') if 'paises' in request.GET else []
    year_range_str = request.GET.get('year_range', '10')
    keyWords = request.GET.getlist('keywords') if 'keywords' in request.GET else []
    year_range = int(year_range_str)
    paises_keywords = False
    keywords_paises_formato= False
    genero_keywords_paises_formato = False
    genero_keywords_formato = False
    if len(generos) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(genero__name=genero) for genero in generos]
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años'

        if len(keyWords) > 0:
            creaciones2 = Creation.objects.all()
            consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keyWords]
            consulta_final = reduce(or_, consultas_q)
            creaciones2 = creaciones2.filter(consulta_final).distinct()
            titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años y con palabras clave: {", ".join(keyWords)}'
            creaciones = creaciones | creaciones2
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
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
            titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años y con paises: {", ".join(paises)}'
            if paises_keywords:
                titulo = f'Número de Creaciones con Género {", ".join(generos)} cada {year_range} años, con palabras clave: {", ".join(keyWords)} y paises: {", ".join(paises)}'

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
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
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        titulo = f'Número de Creaciones cada {year_range} años con palabras clave: {", ".join(keyWords)}'
        if len(paises) > 0:
            creaciones3 = Creation.objects.all()
            consultas_q = [Q(paises__name=pais) for pais in paises]
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
            titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con palabras clave: {", ".join(keyWords)}'
            if len(formatos)>0:
                keywords_paises_formato=True

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            titulo = f'Número de Creaciones con formato: {", ".join(formatos_nombres)} cada {year_range} años con palabras clave: {", ".join(keyWords)}'
            if keywords_paises_formato:
                titulo = f'Número de Creaciones con Países {", ".join(paises)} cada {year_range} años con formato: {", ".join(formatos_nombres)} y palabras clave: {", ".join(keyWords)}'
                
    elif len(paises) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(paises__name=pais) for pais in paises]
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        titulo = f'Número de Creaciones cada {year_range} años con paises: {", ".join(paises)}'
        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
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
    year_range_str = request.GET.get('year_range', '10')
    year_range = int(year_range_str)
    anio_inicio_str = request.GET.get('anio_inicio', '1930')
    anio_fin_str = request.GET.get('anio_fin', '2030')
    year_range_str = request.GET.get('year_range', '10')
    anos = range(1930, 2031, 10)
    # Convertir los valores a enteros
    anio_inicio = int(anio_inicio_str)
    anio_fin = int(anio_fin_str)
    titulo, creaciones = get_creaciones(request)
    # Lógica para generar el gráfico de barras
    # Por ejemplo, contar el número de creaciones por década
    decadas = range(anio_inicio, anio_fin, year_range)

    if (year_range == 5):
        num_creaciones_por_decada = [creaciones.filter(publication_year__range=(decada, decada + 4)).count() for decada in decadas]
    else:
        num_creaciones_por_decada = [creaciones.filter(publication_year__range=(decada, decada + 9)).count() for decada in decadas]
    
    # Crear el gráfico de barras
    plt.figure(figsize=(10, 6))  # Tamaño del gráfico
    plt.bar(decadas, num_creaciones_por_decada, width=5, align='center')  # Ancho de las barras y alineación
    plt.xticks(decadas) 
    plt.xlabel('Años')
    plt.ylabel('Número de Creaciones')
    plt.title(titulo, wrap=True)

    plt.yticks(range(max(num_creaciones_por_decada) + 1))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))

    # Convertir el gráfico a una imagen base64 para mostrar en el template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    rango_anos = [10, 5]
    # Lista de géneros para mostrar en el formulario de filtrado
    lista_paises = Creation.objects.values_list('paises__name', flat=True).distinct().exclude(paises__name=None).order_by('paises__name')
    lista_de_generos = Creation.objects.values_list('genero__name', flat=True).distinct().exclude(genero__name=None).order_by('genero__name')
    lista_de_palabras_clave = Creation.objects.values_list('palabras_clave__name', flat=True).distinct().exclude(palabras_clave__name=None).order_by('palabras_clave__name')
    # Retorna el contexto con los datos del gráfico y la lista de géneros
    return render(request, 'catalog/graph.html', {'imagen_base64': imagen_base64, 'lista_de_generos': lista_de_generos, 'anos': anos, 'rango_anos': rango_anos, 'palabras_clave': lista_de_palabras_clave, 'paises': lista_paises })

def world_map_view(request):
    formatos = request.GET.getlist('formato_ficha') if 'formato_ficha' in request.GET else []
    keyWords = request.GET.getlist('keywords') if 'keywords' in request.GET else []
    titulo1 = f'Número de Creaciones por país'

    if len(keyWords) > 0:
        creaciones = Creation.objects.all()
        consultas_q = [Q(palabras_clave__name=keyWord) for keyWord in keyWords]
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
        titulo1 = f'Número de Creaciones por país con palabras clave: {", ".join(keyWords)}'

        if len(formatos) > 0:
            creaciones3 = Creation.objects.all()
            content_types = ContentType.objects.filter(model__in=formatos)
            consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
            consulta_final = reduce(or_, consultas_q)
            creaciones3 = creaciones3.filter(consulta_final).distinct()
            creaciones = creaciones | creaciones3
            creaciones = creaciones.distinct()
            formatos_nombres = [content_type.name for content_type in content_types]
            titulo1 = f'Número de Creaciones por país con formato: {", ".join(formatos_nombres)}  años con palabras clave: {", ".join(keyWords)}'

    elif len(formatos) > 0:
        creaciones = Creation.objects.all()
        content_types = ContentType.objects.filter(model__in=formatos)
        consultas_q = [Q(polymorphic_ctype=content_type) for content_type in content_types]
        consulta_final = reduce(or_, consultas_q)
        creaciones = creaciones.filter(consulta_final).distinct()
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
        colorscale='Viridis',
        marker_line_color='black',
        marker_line_width=0.5,
    )]

    # Crear el diseño del mapa
    layout = go.Layout(
        title=titulo1,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        width=1000,  # Ancho del mapa en píxeles
        height=600,  # Alto del mapa en píxeles
    )

    # Crear la figura del mapa
    fig = go.Figure(data=data, layout=layout)

    # Convertir la figura a JSON para enviarla a la plantilla
    graph_json = fig.to_json()
    lista_de_palabras_clave = Creation.objects.values_list('palabras_clave__name', flat=True).distinct().exclude(palabras_clave__name=None).order_by('palabras_clave__name')
    return render(request, 'catalog/map.html', {'graph_json': graph_json, 'palabras_clave': lista_de_palabras_clave})

def word_cloud(request):
    _, creaciones = get_creaciones(request)
    palabras_clave = creaciones.values_list('palabras_clave__name', flat=True)

    # Crear un contador de palabras clave
    word_counter = {}
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
