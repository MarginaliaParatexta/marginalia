from tabnanny import verbose
from django.db import models
import uuid
from django import forms
import datetime
from django.urls import reverse
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from treenode.models import TreeNodeModel
BLANK_CHOICE = [('', '---------')]  # Opción en blanco para el formulario

year_choices = BLANK_CHOICE + [(i, i) for i in range(1930, 2024)]
class Genre(models.Model):

    name = models.CharField('Nombre', max_length=200, null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Generos"
        verbose_name = "Genero"

class Fandom(models.Model):
    class FandomTypes(models.TextChoices):
        Foro = "Foro"
        FanFiction = "FanFiction"
        Fanart = "Fanart"
        Mod = "Mod"
        Wiki = "Wiki"
        Meme = "Meme"
        Parodia = "Parodia"

    name = models.CharField('Nombre', max_length=200, null=True, blank=True)
    link = models.CharField('Link', max_length=200, null=True, blank=True)
    type = models.CharField(
        max_length=10000,
        choices=FandomTypes.choices
    )
    metatext = models.ForeignKey("Metatext", on_delete=models.CASCADE, related_name="metatext_fandoms") 

    def __str__(self):
        if self.name:
            return self.name
        return ""
    class Meta:
        verbose_name_plural = "Tipos de fandom"
        verbose_name = "Tipo de fandom"

class Country(models.Model):
    name = models.CharField('Nombre del país', max_length=200)
    iso_code = models.CharField('Código ISO del país', max_length=3, null=True, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Países"
        verbose_name = "País"

class Language(models.Model):
    """Model representing a Language."""
    name = models.CharField('Idioma', max_length=200)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Idiomas"
        verbose_name = "Idioma"

class KeyWord(TreeNodeModel):

    # the field used to display the model instance
    # default value 'pk'
    treenode_display_field = "name"

    name = models.CharField("Palabra", max_length=200)

    class Meta(TreeNodeModel.Meta):
        verbose_name = "Árbol de jerarquía"
        verbose_name_plural = "Palabras clave"

class Creation(PolymorphicModel):
    """Model representing a creation."""
    original_title = models.CharField('Título original', max_length=10000, null=True,)
    subtitles = models.TextField('Subtítulos, capítulos y entregas', null=True, blank=True,)
    authorship = models.TextField('Autoría', null=True, blank=True,)
    publication_year =  models.IntegerField("Año de publicación",default=2023, choices=((i,i) for i in range(1930, 2024)))
    end_year = models.IntegerField("Año Finalización", default=None, choices=year_choices, null=True, blank=True)
    synopsis = models.TextField('Sinopsis', null=True, blank=True,)
    paises = models.ManyToManyField(Country, blank=True)
    palabras_clave = models.ManyToManyField(KeyWord, blank=True)
    genero = models.ManyToManyField(Genre, blank=True)

    #Dudoso
    #product = models.OneToOneField("Product", on_delete=models.CASCADE, related_name="product_creation")
    def __str__(self):
        return self.original_title
    class Meta:
        verbose_name = "Creación"
        verbose_name_plural = "Creaciones"

class OtherLanguageTitle(models.Model):
    idioma = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, related_name="language")
    title = models.CharField('Título', max_length=10000)
    creation = models.ForeignKey(Creation, on_delete=models.CASCADE, related_name="creation_other_language")
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Título en otros idiomas"
        verbose_name_plural = "Título en otros idiomas"

class MediaCreation(Creation):
    idioma_original = models.ForeignKey(Language, on_delete=models.SET_NULL,blank=True, null=True)
    IMDb = models.CharField(max_length=10000,blank=True, null=True)
    commertial_editions = models.CharField('Ediciones comerciales', max_length=10000,blank=True, null=True)

class OtherCountriesDebut(models.Model):
    creation = models.ForeignKey(MediaCreation,verbose_name="Creación", on_delete=models.CASCADE,related_name="mediacreation_other_countries_debut")
    pais = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    description = models.CharField("Descripción", max_length=10000,blank=True, null=True)
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    def __str__(self):
        return self.pais.name
    class Meta:
        verbose_name = "Debut en otros países"
        verbose_name_plural = "Debut en otros países"
        
class Movie(MediaCreation):
    """Model representing a Movie."""
    remastering = models.TextField('Reedición',  null=True, blank=True)
    direction = models.TextField('Dirección',  null=True, blank=True)
    producer = models.TextField('Producción', null=True, blank=True)
    script = models.TextField('Guión',  null=True, blank=True)
    cast = models.TextField('Reparto',  null=True, blank=True)
    music = models.TextField('Música',  null=True, blank=True)
    costume = models.TextField('Vestuario',  null=True, blank=True)
    sound = models.TextField('Sonido',  null=True, blank=True)
    other_data = models.TextField('Otros datos',  null=True, blank=True)
    earnings = models.IntegerField("Taquilla", null=True, blank=True)
    remake = models.TextField('Remake info', null=True, blank=True)
    remake_link =  models.OneToOneField('Product', on_delete=models.SET_NULL, blank=True, null=True, name='remake_link', related_name="remake_movie")
    class Meta:
        verbose_name = "Película"

class TVSerie(MediaCreation):
    """Model representing a TVSerie."""
    debut = models.IntegerField("Año de debut", null=True, blank=True)
    number_seasons = models.IntegerField("Número de temporadas", null=True, blank=True)
    number_chapters = models.IntegerField("Número de capítulos", null=True, blank=True)
    remastering = models.TextField('Reedición',  null=True, blank=True)
    direction = models.TextField('Dirección',  null=True, blank=True)
    producer = models.TextField('Productora',  null=True, blank=True)
    original_idea = models.TextField('Idea original',  null=True, blank=True)
    cast = models.TextField('Reparto',  null=True, blank=True)
    music = models.TextField('Música',  null=True, blank=True)
    costume = models.TextField('Vestuario', null=True, blank=True)
    sound = models.TextField('Sonido',  null=True, blank=True)
    other_data = models.TextField('Otros datos', null=True, blank=True)
    remake = models.TextField('Remake info',  null=True, blank=True)
    remake_link =  models.OneToOneField('Product', on_delete=models.SET_NULL, null=True, blank=True, name='remake_link', related_name="remake_tvserie")
    
    class Meta:
        verbose_name = "Serie TV"

class Videogame(MediaCreation):
    """Model representing a Videogame."""
    batch_number = models.IntegerField("Número de entregas", null=True, blank=True)
    development = models.TextField('Desarrollo',  null=True, blank=True)
    distribution = models.TextField('Distribución',  null=True, blank=True)
    design = models.TextField('Diseño',  null=True, blank=True)
    plataforms = models.TextField('Plataformas',  null=True, blank=True)
    official_website = models.CharField('Web oficial', max_length=10000, null=True, blank=True)
    
    class Meta:
        verbose_name = "Videojuego"

class Award(models.Model):
    """Model representing an award."""
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    institution_name = models.CharField('Nombre de la institucion', max_length=10000,blank=True, null=True)
    text = models.CharField('Información del premio', max_length=10000, null=True, blank=True)
    creation = models.ForeignKey(Creation, on_delete=models.CASCADE, related_name="creation_award")

    def __str__(self):
        if self.text:
            return self.text
        return " "
    class Meta:
        verbose_name_plural = "Premios"
        verbose_name = "Premio"


class Musica(Creation):
    """Model representing a Music Creation."""
    idioma_original = models.ForeignKey(Language, on_delete=models.SET_NULL,blank=True, null=True)
    artist = models.CharField('Artista', max_length=10000, null=True, blank=True)
    album = models.CharField('Álbum', max_length=10000, null=True, blank=True)
    discography = models.CharField('Discográfica', max_length=10000, null=True, blank=True)
    composer = models.CharField('Compositor', max_length=10000, null=True, blank=True)
    lyricist = models.CharField('Letrista', max_length=10000, null=True, blank=True)
    mixing = models.CharField('Mezcla', max_length=10000, null=True, blank=True)
    remastering = models.CharField('Reedición', max_length=10000, null=True, blank=True)
    cover_design = models.CharField('Diseño de carátula', max_length=10000, null=True, blank=True)
    
    class Meta:
        verbose_name = "Música"


class TheaterDebut(models.Model):
    location = models.CharField('Lugar', max_length=10000, null=True, blank=True)
    date = models.DateField('Fecha', null=True, blank=True)
    def __str__(self):
        if self.location:
            return self.location
        return ""

class Theatre(Creation):
    """Model representing a Movie."""
    idioma_original = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    estreno = models.OneToOneField(TheaterDebut, on_delete=models.SET_NULL, null=True, blank=True)
    stage_direction = models.TextField('Dirección escénica', null=True, blank=True)
    producer = models.TextField('Producción', null=True, blank=True)
    cast = models.TextField('Reparto', null=True, blank=True)
    music = models.TextField('Música',  null=True, blank=True)
    lighting = models.TextField('Iluminación',  null=True, blank=True)
    sound = models.TextField('Sonido',  null=True, blank=True)
    other_data = models.TextField('Otros datos',  null=True, blank=True)
    dramatic_text = models.TextField("Texto dramático", null=True, blank=True)
    remake = models.TextField('Remake info',  null=True, blank=True)
    remake_link =  models.OneToOneField('Product', on_delete=models.SET_NULL, null=True, blank=True, name='remake_link', related_name="remake_theatre")
    repositions = models.TextField('Reposiciones',  null=True, blank=True)
    links = models.TextField('Links',  null=True, blank=True)
    

    class Meta:
        verbose_name = "Teatro"

class Image(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True)
    theatre = models.ForeignKey(Theatre,verbose_name='Obra de teatro asociada', on_delete=models.CASCADE, related_name="theatre_images") 
    class Meta:
        verbose_name_plural = "Carteles y fotografías"
        verbose_name = "Cartel o fotografía"

class Staging(models.Model):
    artistic_direction = models.TextField('Dirección artística',null=True, blank=True)
    producer = models.TextField('Producción', null=True, blank=True)
    cast = models.TextField('Reparto', null=True, blank=True)    
    location = models.CharField('Lugar', max_length=10000, null=True, blank=True)
    date = models.CharField('Fecha', max_length=10000, null=True, blank=True)
    link = models.CharField('Enlace', max_length=10000, null=True, blank=True)
    theatre = models.ForeignKey(Theatre,verbose_name='Obra de teatro asociada', on_delete=models.CASCADE, related_name="theatre_staging")
    def __str__(self):
        if self.producer:
            return self.producer 
        return ""
    class Meta:
        verbose_name_plural = "Puestas en escena"
        verbose_name = "Puesta en escena"

class Editorial(models.Model):
    name = models.CharField('Nombre', max_length=10000)
    city = models.CharField('Ciudad',null=True, blank=True,  max_length=10000)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Editoriales"

class Collection(models.Model):
    collection_name = models.CharField('Nombre de la colección', max_length=10000, null=True, blank=True)
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, related_name="editorial_collection", null=True) 
    def  __str__(self):
        if self.collection_name:
            return self.collection_name
        return ""
    class Meta:
        verbose_name_plural = "Colecciones"
        verbose_name = "Colección"

class OriginalEdition(models.Model):
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    isbn = models.CharField('ISBN', max_length=10000,null=True, blank=True)
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, related_name="editorial_original_edition") 
    def __str__(self):
        return "Year: " + str(self.year) + " " + self.editorial.name
    class Meta:
        verbose_name_plural = "Ediciones originales"
        verbose_name = "Edición original"

class LibraryCreation(Creation):
    original_edition = models.OneToOneField(OriginalEdition, on_delete=models.SET_NULL, null=True, blank=True, related_name="creation_original_edition")

class Comic(LibraryCreation):
    script = models.TextField('Guión', null=True, blank=True)
    design = models.TextField('Diseño',  null=True, blank=True)
    colecciones = models.ManyToManyField(Collection, related_name='collection_comic', blank=True)
    class Meta:
        verbose_name = "Comic"
class Novel(LibraryCreation):
    autorship = models.CharField('Autoría', max_length=10000, null=True, blank=True)
    class Meta:
        verbose_name = "Novela"

class BoardGame(LibraryCreation):
    number_players =  models.IntegerField("Número de jugadores",default=2, choices=((i,i) for i in range(1, 16)))
    age = models.IntegerField("Edad minima",default=1, choices=((i,i) for i in range(1, 101)))
    author = models.CharField('Creador', max_length=10000, null=True, blank=True)
    ilustrator = models.TextField('Ilustrador',  null=True, blank=True)
    developer = models.TextField('Desarrollador',  null=True, blank=True)
    design = models.TextField('Diseño',  null=True, blank=True)
    
    class Meta:
        verbose_name = "Juego de mesa"

class OtherLanguageEdition(models.Model):
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    isbn = models.CharField('ISBN', max_length=10000, null=True, blank=True)
    location = models.CharField('Lugar', max_length=10000, null=True, blank=True)
    traductor = models.CharField('Traductor', max_length=10000,  null=True, blank=True)
    idioma = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="language_other_language_edition") 
    libraryCreation = models.ForeignKey(LibraryCreation, on_delete=models.CASCADE, related_name="library_creation_other_language_edition") 
    editorial = models.ForeignKey(Editorial, on_delete=models.SET_NULL, related_name="editorial", null=True) 
    class Meta:
        verbose_name_plural = "Ediciones en otros idiomas"
        verbose_name = "Edición en otro idioma"

class Reissue(models.Model):
    year = models.IntegerField("Año",default=2023, choices=((i,i) for i in range(1930, 2024)))
    isbn = models.CharField('ISBN', max_length=10000, null=True, blank=True)
    location = models.CharField('Lugar', max_length=10000,  null=True, blank=True)
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, related_name="editorial_reissue") 
    traductor = models.CharField('Traductor', max_length=10000,  null=True, blank=True)
    libraryCreation = models.ForeignKey(LibraryCreation, on_delete=models.CASCADE, related_name="library_creation_reissue") 
    class Meta:
        verbose_name_plural = "Reediciones"
        verbose_name = "Reedición"

class Hipotext(models.Model):
    #fuentes_clasicas = models.ForeignKey(Reference, on_delete=models.CASCADE, related_name="hipotext_classic_sources") 
    #otras_fuentes = models.ManyToManyField(Reference, related_name="hipotext_other_sources")  # Cambiado a ManyToManyField
    #fuentes_documentales = models.ForeignKey(Reference, on_delete=models.CASCADE, related_name="hipotext_documentary_sources") 
    unnecesary_field = models.CharField('Campo innecesario para funcionamiento', max_length=10000)     
    product = models.OneToOneField("Product", on_delete=models.CASCADE,related_name="product_hipotext")
    def __str__(self):
        return self.product.title
    class Meta:
        verbose_name_plural = "Hipotextos"
        verbose_name = "Hipotexto"

class ClassicSource(models.Model):
    name = models.CharField('Nombre', max_length=10000, null=True, blank=True)
    title = models.CharField('Título', max_length=10000, null=True, blank=True)
    reference = models.CharField('Referencia bibliográfica', max_length=10000,  null=True, blank=True)
    others = models.CharField('Otros', max_length=10000,  null=True, blank=True)
    hipotext = models.ForeignKey(Hipotext, on_delete=models.CASCADE, related_name="hipotext_classic_sources") 
    class Meta:
        verbose_name_plural = "Fuentes clásicas"
        verbose_name = "Fuente clásica"
    def __str__(self):
        return ""

class OtherSource(models.Model):
    name = models.CharField('Nombre', max_length=10000,null=True, blank=True)
    title = models.CharField('Título', max_length=10000, null=True, blank=True)
    reference = models.CharField('Referencia bibliográfica', max_length=10000,  null=True, blank=True)
    others = models.CharField('Otros', max_length=10000,  null=True, blank=True)
    hipotext = models.ForeignKey(Hipotext, on_delete=models.CASCADE, related_name="hipotext_other_sources") 
    class Meta:
        verbose_name_plural = "Otras fuentes"
        verbose_name = "Otra fuente"
    def __str__(self):
        return ""

class DocumentarySource(models.Model):
    name = models.CharField('Nombre', max_length=10000,null=True, blank=True)
    title = models.CharField('Título', max_length=10000,null=True, blank=True)
    reference = models.CharField('Referencia bibliográfica', max_length=10000,  null=True, blank=True)
    others = models.CharField('Otros', max_length=10000,  null=True, blank=True)
    hipotext = models.ForeignKey(Hipotext, on_delete=models.CASCADE, related_name="hipotext_documentary_sources") 
    class Meta:
        verbose_name_plural = "Fuentes documentales"
        verbose_name = "Fuente documental"
    def __str__(self):
        return ""

class Paratext(models.Model):
    introduction = models.TextField('Introducción',null=True, blank=True)
    prologue = models.TextField('Prólogo',null=True, blank=True)
    epilogue = models.TextField('Epílogo',null=True, blank=True)
    notes = models.TextField('Notas',null=True, blank=True)
    product = models.OneToOneField("Product", on_delete=models.CASCADE, related_name="product_paratext")
    def __str__(self):
        return self.product.title
    class Meta:
        verbose_name_plural = "Paratextos"
        verbose_name = "Paratexto"

class Rulebook(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True, blank=True)
    paratext = models.ForeignKey(Paratext, on_delete=models.CASCADE, related_name="paratext_rulebook") 
    description = models.TextField('Descripción',null=True, blank=True)
    class Meta:
        verbose_name_plural = "Libros de reglas"
        verbose_name = "Libro de reglas"

class Cover(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True, blank=True)
    paratext = models.ForeignKey(Paratext, on_delete=models.CASCADE, related_name="paratext_cover") 
    description = models.TextField('Descripción',null=True, blank=True)
    class Meta:
        verbose_name_plural = "Portadas"
        verbose_name = "Portada"

class Videoclips(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True, blank=True)
    videoclip = models.CharField('Enlace al videoclip', max_length=10000,null=True, blank=True)
    paratext = models.ForeignKey(Paratext, on_delete=models.CASCADE, related_name="paratext_videoclip") 
    description = models.TextField('Descripción',null=True, blank=True)
    class Meta:
        verbose_name = "VideoClip"
        verbose_name_plural = "VideoClips"

class AdsTrailers(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True, blank=True)
    videoclip = models.CharField('Video del trailer', max_length=10000, null=True, blank=True)
    paratext = models.ForeignKey(Paratext, on_delete=models.CASCADE, related_name="paratext_adstrailer") 
    description = models.TextField('Descripción', null=True, blank=True)
    class Meta:
        verbose_name = "Anuncio o tráiler"
        verbose_name_plural = "Anuncios y tráileres"

class Extras(models.Model):
    image = models.CharField('Link de la imagen', max_length=10000, null=True, blank=True)
    videoclip = models.CharField('Video del trailer', max_length=10000,null=True, blank=True)
    paratext = models.ForeignKey(Paratext, on_delete=models.CASCADE, related_name="paratext_extras") 
    description = models.TextField('Descripción', null=True, blank=True)
    class Meta:
        verbose_name = "Extra"
        verbose_name_plural = "Extras"


class Metatext(models.Model):
    unnecesary_field = models.CharField('Campo innecesario para funcionamiento', max_length=10000)    
    #declarations = models.TextField('Declaraciones autorizadas',  null=True, blank=True)
    #criticism = models.TextField('Críticas',  null=True, blank=True)
    #press_articles = models.TextField('Artículos de prensa',  null=True, blank=True)
    #social_networks = models.TextField('Social networks', null=True, blank=True)
    #blogs = models.TextField('Blogs',  null=True, blank=True)
    #fandoms = models.TextField('Fandoms',  null=True, blank=True)
    product = models.OneToOneField("Product", on_delete=models.CASCADE,related_name='product_metatext')
    def __str__(self):
        return self.product.title
    class Meta:
        verbose_name = "Metatexto"
        verbose_name_plural = "Metatextos"

class Declaration(models.Model):
    description = models.CharField('Descripción', max_length=10000, null=True, blank=True)
    link = models.CharField('Link', max_length=10000, null=True, blank=True)
    metatext = models.ForeignKey(Metatext, on_delete=models.CASCADE, related_name="metatext_declarations") 
    class Meta:
        verbose_name_plural = "Declaraciones autorizadas"
        verbose_name = "Declaración autorizada"
    def __str__(self):
        if self.description:
            return self.description
        return ""

class Criticism(models.Model):
    description = models.CharField('Descripción', max_length=10000, null=True, blank=True)
    link = models.CharField('Link', max_length=10000, null=True, blank=True)
    metatext = models.ForeignKey(Metatext, on_delete=models.CASCADE, related_name="metatext_criticism") 
    class Meta:
        verbose_name_plural = "Críticas"
        verbose_name = "Crítica"
    def __str__(self):
        if self.description:
            return self.description
        return ""

class PressArticle(models.Model):
    description = models.CharField('Descripción', max_length=10000, null=True, blank=True)
    link = models.CharField('Link', max_length=10000, null=True, blank=True)
    metatext = models.ForeignKey(Metatext, on_delete=models.CASCADE, related_name="metatext_press_article") 
    class Meta:
        verbose_name_plural = "Artículos de prensa"
        verbose_name = "Artículo de prensa"
    def __str__(self):
        if self.description:
            return self.description
        return ""

class SocialNetwork(models.Model):
    description = models.CharField('Descripción', max_length=10000, null=True, blank=True)
    link = models.CharField('Link', max_length=10000, null=True, blank=True)
    metatext = models.ForeignKey(Metatext, on_delete=models.CASCADE, related_name="metatext_social_networks") 
    class Meta:
        verbose_name_plural = "Social Networks"
        verbose_name = "Social Network"
    def __str__(self):
        if self.description:
            return self.description
        return ""

class Blog(models.Model):
    description = models.CharField('Descripción', max_length=10000, null=True, blank=True)
    link = models.CharField('Link', max_length=10000, null=True, blank=True)
    metatext = models.ForeignKey(Metatext, on_delete=models.CASCADE, related_name="metatext_blogs") 
    class Meta:
        verbose_name_plural = "Blogs"
        verbose_name = "Blog"
    def __str__(self):
        if self.description:
            return self.description
        return ""

class MedialTransfers(models.Model):
    transmediality = models.OneToOneField('Product', name='Transmedialidad',on_delete=models.SET_NULL, null=True, blank=True,  related_name="product_transmediality")
    hypertext = models.TextField('Hipertexto',  null=True, blank=True)
    product = models.OneToOneField("Product" ,on_delete=models.CASCADE,related_name='product_medialTransfer',name="product_owner")
    def __str__(self):
        return self.product_owner.title
    class Meta:
        verbose_name = "Trasvase medial"
        verbose_name_plural = "Trasvases mediales"


class Bibliography(models.Model):
    studies_tradition_classical_reception = models.TextField('Estudios de Tradición y Recepción Clásica',null=True, blank=True)
    other_studies = models.TextField('Otros estudios',null=True, blank=True)
    product = models.OneToOneField("Product", on_delete=models.CASCADE, related_name='product_bibliography')
    def __str__(self):
        return self.product.title
    class Meta:
        verbose_name = "Bibliografía"
        verbose_name_plural = "Bibliografías"

class Product(models.Model):
    """Model representing a product."""
    id = models.UUIDField(primary_key = True, default=uuid.uuid4, unique=True, db_index=True, editable=False)
    title = models.CharField('Titulo', max_length=10000, null=True)
    build_id = models.CharField('Autor/a de la ficha', max_length= 100, editable=False) #Esto tiene que hacerse con el id del que lo ha creado
    last_modified = models.DateField('Última modificación', editable=False, default=datetime.date.today)
    creation = models.OneToOneField(Creation, on_delete=models.CASCADE)
    related_products = models.ManyToManyField('self', blank=True, verbose_name='Fichas relacionadas', related_name='related_to')
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class Knot(models.Model):
    info = models.CharField('Información del nudo', max_length=10000, null=True, blank=True)
    productos = models.ManyToManyField(Product, blank=True, related_name='related_knots')
    def __str__(self):
        if self.info:
            return self.info
        return ""
    class Meta:
        verbose_name = "Nodo"
        verbose_name_plural = "Nodos"
