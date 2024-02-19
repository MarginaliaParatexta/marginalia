import django_filters
from .models import BoardGame, Comic, Country, Creation,  Genre, KeyWord, Movie, Musica, Novel, Product, TVSerie, Theatre, Videogame
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db import models
from functools import reduce
from operator import or_
from django.db.models import Q

YEAR_CHOICES = [(str(year), str(year)) for year in range(1930, 2025)]


def separate_creations_by_type(queryset):
    content_types = ContentType.objects.filter(model__in=['movie', 'tvserie', 'theatre', 'musica', 'boardgame', 'videogame', 'comic', 'novel'])
    queryset_by_type = {}

    for content_type in content_types:
        content_model = content_type.model
        filtered_queryset = queryset.filter(creation__polymorphic_ctype_id=content_type.id)

        queryset_by_type[content_model] = filtered_queryset
    
    return queryset_by_type

class YearRangeWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        year_range = [(year, str(year)) for year in range(1930, 2025)]
        widgets = (
            forms.Select(attrs=attrs, choices=year_range),
            forms.Select(attrs=attrs, choices=year_range),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        return [None, None]  


class YearRangeFilter(django_filters.RangeFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', YearRangeWidget())  # Usa nuestro widget personalizado
        super().__init__(*args, **kwargs)
        # Establece el valor predeterminado para el segundo campo del rango a 2024
        self.extra['widget'].widgets[1].choices = [(None, '---------')] + YEAR_CHOICES
        self.extra['widget'].widgets[1].initial = 2024
        self.extra['widget'].widgets[0].choices = [(None, '---------')] + YEAR_CHOICES
        self.extra['widget'].widgets[0].initial = 1930

class TextSearchFilter(django_filters.Filter):
    def filter(self, queryset, value):
        if value:
            #campos boardgame
            boardgames = BoardGame.objects.all()
            search_fields_boardgame = ['author',  'ilustrator', 'developer', 'design']
            queries_boardgame = [Q(**{field + '__icontains': value}) for field in search_fields_boardgame]
            search_query_boardgame = reduce(or_, queries_boardgame)
            queryset_boardgame = boardgames.filter(search_query_boardgame)
            boardgame_ids = queryset_boardgame.values_list('product__id', flat=True)
            copia_query_set_for_boardgame = queryset.filter(id__in=boardgame_ids)

            #campos novel
            novels = Novel.objects.all()
            search_fields_novels = ['autorship',]
            queries_novels = [Q(**{field + '__icontains': value}) for field in search_fields_novels]
            search_query_novels = reduce(or_, queries_novels)
            queryset_novels = novels.filter(search_query_novels)
            novels_ids = queryset_novels.values_list('product__id', flat=True)
            copia_query_set_for_novel = queryset.filter(id__in=novels_ids)

            #campos comic
            comics = Comic.objects.all()
            search_fields_comics = ['script', 'design']
            queries_comics = [Q(**{field + '__icontains': value}) for field in search_fields_comics]
            search_query_comics = reduce(or_, queries_comics)
            queryset_comics = comics.filter(search_query_comics)
            comics_ids = queryset_comics.values_list('product__id', flat=True)
            copia_query_set_for_comic = queryset.filter(id__in=comics_ids)

            #campos musica
            musics = Musica.objects.all()
            search_fields_musics = [ 'artist', 'album', 'discography', 'composer', 'mixing', 'remastering', 'cover_design']
            queries_musics = [Q(**{field + '__icontains': value}) for field in search_fields_musics]
            search_query_musics = reduce(or_, queries_musics)
            queryset_music = musics.filter(search_query_musics)
            musics_ids = queryset_music.values_list('product__id', flat=True)
            copia_query_set_for_music = queryset.filter(id__in=musics_ids)

            #campos theatre
            theatres = Theatre.objects.all()
            search_fields_theatres = ['stage_direction', 'producer', 'music', 'cast', 'lighting', 'sound', 'other_data', 'remake', 'repositions']
            queries_theatres = [Q(**{field + '__icontains': value}) for field in search_fields_theatres]
            search_query_theatres = reduce(or_, queries_theatres)
            queryset_theatres = theatres.filter(search_query_theatres)
            theatres_ids = queryset_theatres.values_list('product__id', flat=True)
            copia_query_set_for_theatre = queryset.filter(id__in=theatres_ids)

            #campos videogame
            videogames = Videogame.objects.all()
            search_fields_videogames = ['development', 'distribution', 'plataforms', 'official_website']
            queries_videogames = [Q(**{field + '__icontains': value}) for field in search_fields_videogames]
            search_query_videogames = reduce(or_, queries_videogames)
            queryset_videogames = videogames.filter(search_query_videogames)
            videogames_ids = queryset_videogames.values_list('product__id', flat=True)
            copia_query_set_for_videogame = queryset.filter(id__in=videogames_ids)

            #campos tvserie
            tvserie = TVSerie.objects.all()
            search_fields_tvserie = ['remastering', 'direction', 'producer', 'original_idea', 'cast', 'music', 'costume', 'sound', 'other_data', 'remake']
            queries_tvserie = [Q(**{field + '__icontains': value}) for field in search_fields_tvserie]
            search_query_tvserie = reduce(or_, queries_tvserie)
            queryset_tvseries = tvserie.filter(search_query_tvserie)
            tvserie_ids = queryset_tvseries.values_list('product__id', flat=True)
            copia_query_set_for_tvserie = queryset.filter(id__in=tvserie_ids)

            #campos movie
            movies = Movie.objects.all()
            search_fields_movies = ['remastering', 'direction', 'producer', 'script', 'cast', 'script', 'music', 'other_data', 'remake']
            queries_movies = [Q(**{field + '__icontains': value}) for field in search_fields_movies]
            search_query_movies = reduce(or_, queries_movies)
            queryset_movies = movies.filter(search_query_movies)
            movies_ids = queryset_movies.values_list('product__id', flat=True)
            copia_query_set_for_movie = queryset.filter(id__in=movies_ids)

            #Campos de creation
            search_fields = ['title', 'creation__subtitles', 'creation__original_title', 'creation__authorship', 'creation__synopsis']
            queries = [Q(**{field + '__icontains': value}) for field in search_fields]
            search_query = reduce(or_, queries)
            queryset = queryset.filter(search_query)

            #Combinar todas las creaciones
            queryset = queryset | copia_query_set_for_boardgame | copia_query_set_for_novel | copia_query_set_for_comic | copia_query_set_for_theatre | copia_query_set_for_music | copia_query_set_for_videogame | copia_query_set_for_tvserie | copia_query_set_for_movie
        return queryset

class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Título')
    text_search = TextSearchFilter(field_name='text_search', label='Buscar en todos los campos')
    palabras_clave = django_filters.ModelMultipleChoiceFilter(
        field_name='creation__palabras_clave',
        queryset=KeyWord.objects.all(),
        label='Palabras Clave',
        conjoined=True 
    )
    genero = django_filters.ModelMultipleChoiceFilter(
        field_name='creation__genero',  # Ajusta el campo para reflejar la relación con el género
        queryset=Genre.objects.all(),
        label='Género',
        conjoined=True 
    )

    paises = django_filters.ModelMultipleChoiceFilter(
        field_name='creation__paises', 
        queryset=Country.objects.all(),
        label='Paises Relacionados',
        conjoined=True 
    )
    
    creation_type = django_filters.ChoiceFilter(
        label='Tipo de Creación',
        method='filter_by_creation_type',
        choices=[
            ('movie', 'Movie'),
            ('tvserie', 'TV Serie'),
            ('theatre', 'Theatre'),
            ('musica', 'Musica'),
            ('boardgame', 'Boardgame'),
            ('videogame', 'VideoGame'),
            ('comic', 'Comic'),
            ('novel', 'Novel'),
        ]
    )


    publication_year_range = YearRangeFilter(
        field_name='creation__publication_year',
        label='Rango de años de publicación'
    )

    class Meta:
        model = Product
        fields = ['title', 'palabras_clave', 'genero', 'creation_type', 'publication_year_range', 'paises', 'text_search'  ]


    def filter_by_creation_type(self, queryset, name, value):
        content_type = ContentType.objects.get(model=value)
        return queryset.filter(creation__polymorphic_ctype_id=content_type.id)
