from django.contrib import admin
from .models import *
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django import forms
from polymorphic.admin import PolymorphicParentModelAdmin,  PolymorphicChildModelFilter
from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm
from django.utils.html import format_html
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


admin.site.site_header = 'Marginalia Paratexta'
admin.site.index_title = 'Panel de control Marginalia Paratexta'
admin.site.site_title = 'Marginalia Paratexta'

class RulebookInline(NestedStackedInline):
    model=Rulebook
    extra=1

class CoverInline(NestedStackedInline):
    model=Cover
    extra=1

class VideoclipsInline(NestedStackedInline):
    model=Videoclips
    extra=1

class AdsTrailersInline(NestedStackedInline):
    model=AdsTrailers
    extra=1

class ExtrasInline(NestedStackedInline):
    model=Extras
    extra = 1

#Dudoso
#class CreationInline(NestedStackedInline):
#    model=Creation

class ParatextInline(NestedStackedInline):
    model=Paratext
    inlines = [RulebookInline, CoverInline, VideoclipsInline, AdsTrailersInline, ExtrasInline]

class AwardInline(NestedStackedInline):
    model=Award
    extra = 1

class ClassicSourceInline(NestedStackedInline):
    model = ClassicSource
    extra = 1 

class DeclarationInline(NestedStackedInline):
    model = Declaration
    extra = 1 

class SocialNetworkInline(NestedStackedInline):
    model = SocialNetwork
    extra = 1 

class CriticismInline(NestedStackedInline):
    model = Criticism
    extra = 1 

class PressArticleInline(NestedStackedInline):
    model = PressArticle
    extra = 1 

class BlogInline(NestedStackedInline):
    model = Blog
    extra = 1 

class FandomInline(NestedStackedInline):
    model = Fandom
    extra = 1 

class MetatextInline(NestedStackedInline):
    model=Metatext
    inlines = [DeclarationInline,CriticismInline,  PressArticleInline,  SocialNetworkInline, BlogInline, FandomInline]

class OtherSourceInline(NestedStackedInline):
    model = OtherSource
    extra = 1 

class DocumentarySourceInline(NestedStackedInline):
    model = DocumentarySource
    extra = 1 

class HipotextInline(NestedStackedInline):
    model=Hipotext
    inlines = [ClassicSourceInline, DocumentarySourceInline, OtherSourceInline]

class BibliographyInline(NestedStackedInline):
    model=Bibliography

class MedialTransferInline(NestedStackedInline):
    model=MedialTransfers
    fk_name = "product_owner"

class OtherLanguageTitleInline(NestedStackedInline):
    model=OtherLanguageTitle
    extra = 1

class StagingInline(NestedStackedInline):
    model=Staging
    extra = 1

class ImageInline(admin.TabularInline):
    model=Image
    extra = 1

class OtherCountriesDebutInline(NestedStackedInline):
    model=OtherCountriesDebut
    extra = 1

class OtherLanguageEditionInline(NestedStackedInline):
    model=OtherLanguageEdition
    extra=1
class ReissueInline(NestedStackedInline):
    model=Reissue
    extra = 1

class CreationParentAdmin(PolymorphicParentModelAdmin):
    """Parent admin class for Creation model."""
    base_model = Creation
    child_models = (Movie, Musica, TVSerie, Videogame, Theatre)

class HiddenModelAdmin(admin.ModelAdmin):
    """Admin class to hide models from list view."""
    def get_model_perms(self, request):
        # Excluir los modelos ocultos de la lista de objetos
        excluded_models = (Videogame, TVSerie, Movie, Musica)
        model_perms = super().get_model_perms(request)
        perms = {}
        for model in excluded_models:
            perms[model] = model_perms.get(model, {'add': False, 'change': False, 'delete': False, 'view': False})
        return perms

class DisableAddButtonModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        model_perms = super().get_model_perms(request)
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        add_url = reverse('admin:%s_%s_add' % (app_label, model_name), current_app=self.admin_site.name)
        change_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[0], current_app=self.admin_site.name)

        perms = model_perms.copy()
        perms.update({'add': False})

        if request.path == add_url or request.path == change_url:
            perms.update({'add': True})

        return perms

    def has_add_permission(self, request):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        if request.path == reverse('admin:%s_%s_changelist' % (app_label, model_name)):
            return False

        return super().has_add_permission(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

@admin.register(Creation)
class CreationAdmin(CreationParentAdmin, DisableAddButtonModelAdmin):
    """Admin class for Creation model."""
    base_model = Creation
    child_models = (Movie, Musica, TVSerie, Videogame, Theatre, Novel, Comic, BoardGame)
    list_filter = (PolymorphicChildModelFilter, )
    list_display = ('get_product_title', 'original_title', 'authorship', 'publication_year')
    def get_product_title(self, obj):
        return obj.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(MediaCreation)
class MediaCreationAdmin(admin.ModelAdmin):
    """Admin class for MediaCreation model."""
    pass
admin.site.unregister(MediaCreation)

@admin.register(LibraryCreation)
class LibraryCreationAdmin(admin.ModelAdmin):
    """Admin class for LibraryCreation model."""
    pass
admin.site.unregister(LibraryCreation)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields=('title',)

@admin.register(Movie)
class MovieAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(MovieAdmin, self).get_form(request, obj, **kwargs)
        return form
    list_display = ('original_title', 'authorship')
    inlines = [AwardInline, OtherLanguageTitleInline, OtherCountriesDebutInline]

@admin.register(Musica)
class MusicAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(MusicAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline]

@admin.register(TVSerie)
class TVSerieAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(TVSerieAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, OtherCountriesDebutInline]

@admin.register(Videogame)
class VideogameAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(VideogameAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, OtherCountriesDebutInline]

@admin.register(Theatre)
class TheatreAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(TheatreAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, StagingInline, ImageInline]


@admin.register(Novel)
class NovelAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(NovelAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, OtherLanguageEditionInline, ReissueInline]

@admin.register(Comic)
class ComicAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(ComicAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, OtherLanguageEditionInline, ReissueInline]

@admin.register(BoardGame)
class BoardGameAdmin(HiddenModelAdmin, DisableAddButtonModelAdmin):
    def get_form(self, request, obj=None, **kwargs):    # Just added this override
        form = super(BoardGameAdmin, self).get_form(request, obj, **kwargs)
        return form
    inlines = [AwardInline, OtherLanguageTitleInline, OtherLanguageEditionInline, ReissueInline]

@admin.register(Paratext)
class ParatextAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title',)
    readonly_fields = ('product',)
    inlines = [RulebookInline, CoverInline, VideoclipsInline, AdsTrailersInline, ExtrasInline]
    def get_product_title(self, obj):
        return obj.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(Hipotext)
class HipotextAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title',)
    readonly_fields = ('product',)
    def get_product_title(self, obj):
        return obj.product.title  # Obtiene el título del producto asociado a la creación
    inlines = [ClassicSourceInline, DocumentarySourceInline, OtherSourceInline]
    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(Metatext)
class MetatextAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title',)
    readonly_fields = ('product',)
    def get_product_title(self, obj):
        return obj.product.title  # Obtiene el título del producto asociado a la creación
    inlines = [DeclarationInline,CriticismInline,  PressArticleInline,  SocialNetworkInline, BlogInline, FandomInline]
    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(MedialTransfers)
class MedialTransfersAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title',)
    readonly_fields = ('product_owner',)
    def get_product_title(self, obj):
        return obj.product_owner.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(Bibliography)
class BibliographyAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title',)
    def get_product_title(self, obj):
        return obj.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display
    readonly_fields = ('product','zotero_link', 'refworks_link')

    def zotero_link(self, obj):
        zotero_url = "https://www.zotero.org/"  # Reemplaza con la URL de Zotero que desees
        return format_html('<a href="{}" target="_blank">Zotero</a>', zotero_url)

    def refworks_link(self, obj):
        refworks_url = "https://refworks.proquest.com/"  # Reemplaza con la URL de RefWorks que desees
        return format_html('<a href="{}" target="_blank">RefWorks</a>', refworks_url)

@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    list_display = ('title', 'last_modified', 'build_id')
    search_fields=('title',)
    inlines = [ HipotextInline, ParatextInline, MetatextInline, MedialTransferInline, BibliographyInline ]
    def save_model(self, request, obj, form, change):
        obj.last_modified = datetime.date.today()
        obj.build_id = str(request.user.username) + "-" + str(request.user.id)
        obj.save()

@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(OtherLanguageTitle)
class OtherLanguageTitleAdmin(admin.ModelAdmin):
    list_display = ('idioma','title', 'get_product_title')

    def get_product_title(self, obj):
        return obj.creation.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('get_product_title',)

    def get_product_title(self, obj):
        return obj.theatre.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(OriginalEdition)
class OriginalEditionAdmin(DisableAddButtonModelAdmin):
    list_display = ('get_product_title', 'year', 'isbn', 'get_editorial_name')

    def get_product_title(self, obj):
        return obj.creation_original_edition.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

    def get_editorial_name(self, obj):
        return obj.editorial.name  # Obtiene el título del producto asociado a la creación

    get_editorial_name.short_description = 'Editorial'  # Establece el nombre de la columna en el list_display

@admin.register(OtherCountriesDebut)
class OtherCountriesDebutAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'pais', 'year')

    def get_product_title(self, obj):
        return obj.creation.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(OtherLanguageEdition)
class OtherLanguageEditionAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'get_language_name', 'year', 'get_editorial_name')

    def get_product_title(self, obj):
        return obj.libraryCreation.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

    def get_editorial_name(self, obj):
        return obj.editorial.name  # Obtiene el título del producto asociado a la creación

    get_editorial_name.short_description = 'Editorial'  # Establece el nombre de la columna en el list_display

    def get_language_name(self, obj):
        return obj.idioma.name  # Obtiene el título del producto asociado a la creación

    get_language_name.short_description = 'Idioma'  # Establece el nombre de la columna en el list_display

@admin.register(Reissue)
class ReissueAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'year', 'get_editorial_name')

    def get_product_title(self, obj):
        return obj.libraryCreation.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

    def get_editorial_name(self, obj):
        return obj.editorial.name  # Obtiene el título del producto asociado a la creación

    get_editorial_name.short_description = 'Editorial'  # Establece el nombre de la columna en el list_display

@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'location', 'producer')

    def get_product_title(self, obj):
        return obj.theatre.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

class AwardYearFilter(admin.SimpleListFilter):
    title = 'Year Range'
    parameter_name = 'year_range'

    def lookups(self, request, model_admin):
        # Define los rangos de años
        year_ranges = [
            ('1930-1940', '1930-1940'),
            ('1940-1950', '1940-1950'),
            ('1950-1960', '1950-1960'),
            ('1960-1970', '1960-1970'),
            ('1970-1980', '1970-1980',),
            ('1980-1990', '1980-1990'),
            ('1990-2000', '1990-2000'),
            ('2000-2010', '2000-2010'),
            ('2010-2020', '2010-2020'),
            ('2020-2030', '2020-2030'),
            # Agrega más rangos según sea necesario
        ]
        return year_ranges

    def queryset(self, request, queryset):
        if self.value():
            # Divide el valor del filtro en el rango de años
            start_year, end_year = self.value().split('-')
            return queryset.filter(year__range=[start_year, end_year])
        return queryset

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'year', 'institution_name', "text")
    list_filter = (AwardYearFilter,) 
    def get_product_title(self, obj):
        return obj.creation.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(TheaterDebut)
class TheaterDebutAdmin(HiddenModelAdmin):
    list_display = ('get_product_title', 'location', 'date')

    def get_product_title(self, obj):
        return obj.theatre.product.title  # Obtiene el título del producto asociado a la creación

    get_product_title.short_description = 'Título del producto'  # Establece el nombre de la columna en el list_display

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection_name','year', 'get_editorial_name')

    def get_editorial_name(self, obj):
        return obj.editorial.name  # Obtiene el título del producto asociado a la creación

    get_editorial_name.short_description = 'Editorial'  # Establece el nombre de la columna en el list_display

@admin.register(KeyWord)
class KeyWordAdmin(TreeNodeModelAdmin):
    readonly_fields = ('tn_priority', )
    # set the changelist display mode: 'accordion', 'breadcrumbs' or 'indentation' (default)
    # when changelist results are filtered by a querystring,
    # 'breadcrumbs' mode will be used (to preserve data display integrity)
    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_BREADCRUMBS
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_INDENTATION

    # use TreeNodeForm to automatically exclude invalid parent choices
    form = TreeNodeForm

admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Knot)
