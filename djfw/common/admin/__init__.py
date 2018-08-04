from django.contrib import admin


class CustomModelAdmin(admin.ModelAdmin):

    # class Media:
        # js = [
        #     '/media/tinymce/jscripts/tiny_mce/tiny_mce.js',
        #     '/media/tinymce_setup/tinymce_setup.js',
        # ]
    save_on_top = True

    list_display = (
        'id',
        '__unicode__',
        'created_at',
        'updated_at',
    )

    list_display_links = (
        'id',
        '__unicode__',
    )

    search_fields = (
        'pk',
    )

    list_per_page = 100

    date_hierarchy = 'created_at'


class StatusAdmin(CustomModelAdmin):

    list_display = (
        'id',
        '__unicode__',
        'name',
        'created_at',
        'updated_at',
    )

    list_editable = (
        'name',
    )

    list_filter = (
    )

    search_fields = (
        'id',
        'name',
    )


class DescribedStatusAdmin(CustomModelAdmin):

    list_display = (
        'id',
        '__unicode__',
        'name',
        'description',
        'created_at',
        'updated_at',
    )

    list_editable = (
        'name',
        'description',
    )

    list_filter = (
    )

    search_fields = (
        'id',
        'name',
        'description',
    )
