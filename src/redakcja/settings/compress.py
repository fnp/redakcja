STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'pipeline.finders.PipelineFinder',
)


STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None
PIPELINE_STORAGE = 'pipeline.storage.PipelineFinderStorage'


# CSS and JS files to compress
PIPELINE_CSS = {
    'detail': {
         'source_filenames': (
            'css/master.css',
            'css/toolbar.css',
            'css/gallery.css',
            'css/history.css',
            'css/summary.css',
            'css/html.css',
            'css/jquery.autocomplete.css',
            'css/imgareaselect-default.css', #img!
            'css/dialogs.css',
        ),
        'output_filename': 'compressed/detail_styles.css',
    },
    'catalogue': {
        'source_filenames': (
            'css/filelist.css',
        ),
        'output_filename': 'compressed/catalogue_styles.css',
     },
     'book': {
        'source_filenames': (
            'css/book.css',
        ),
        'output_filename': 'compressed/book.css',
    },
    'book_list': {
        'source_filenames': (
            'contextmenu/jquery.contextMenu.css',
            'css/book_list.css',
        ),
        'output_filename': 'compressed/book_list.css',
    },
}

PIPELINE_JS = {
    # everything except codemirror
    'detail': {
        'source_filenames': (
                # libraries
                'js/lib/jquery/jquery.autocomplete.js',
                'js/lib/jquery/jquery.blockui.js',
                'js/lib/jquery/jquery.elastic.js',
                'js/lib/jquery/jquery.xmlns.js',
                'js/button_scripts.js',
                'js/slugify.js',

                # wiki scripts
                'js/wiki/wikiapi.js',
                'js/wiki/xslt.js',

                # base UI
                'js/wiki/base.js',
                'js/wiki/toolbar.js',

                # dialogs
                'js/wiki/dialog_save.js',
                'js/wiki/dialog_revert.js',
                'js/wiki/dialog_pubmark.js',

                # views
                'js/wiki/view_history.js',
                'js/wiki/view_summary.js',
                'js/wiki/view_editor_source.js',
                'js/wiki/view_editor_wysiwyg.js',
                'js/wiki/view_gallery.js',
                'js/wiki/view_annotations.js',
                'js/wiki/view_search.js',
                'js/wiki/view_column_diff.js',
        ),
        'output_filename': 'compressed/detail_scripts.js',
     },
    'wiki_img': {
        'source_filenames': (
                # libraries
                'js/lib/jquery-1.4.2.min.js',
                'js/lib/jquery/jquery.autocomplete.js',
                'js/lib/jquery/jquery.blockui.js',
                'js/lib/jquery/jquery.elastic.js',
                'js/lib/jquery/jquery.imgareaselect.js',
                'js/button_scripts.js',
                'js/slugify.js',

                # wiki scripts
                'js/wiki_img/wikiapi.js',

                # base UI
                'js/wiki_img/base.js',
                'js/wiki/toolbar.js',

                # dialogs
                'js/wiki/dialog_save.js',
                'js/wiki/dialog_revert.js',
                'js/wiki/dialog_pubmark.js',

                # views
                'js/wiki_img/view_editor_objects.js',
                'js/wiki_img/view_editor_motifs.js',
                'js/wiki/view_editor_source.js',
                'js/wiki/view_history.js',
                'js/wiki/view_column_diff.js',
        ),
        'output_filename': 'compressed/detail_img_scripts.js',
     },
    'catalogue': {
        'source_filenames': (
                'js/catalogue/catalogue.js',
                'js/slugify.js',
                'email_mangler/email_mangler.js',
        ),
        'output_filename': 'compressed/catalogue_scripts.js',
     },
     'book': {
        'source_filenames': (
            'js/book_text/jquery.eventdelegation.js',
            'js/book_text/jquery.scrollto.js',
            'js/book_text/jquery.highlightfade.js',
            'js/book_text/book.js',
        ),
        'output_filename': 'compressed/book.js',
         },
    'book_list': {
        'source_filenames': (
            'contextmenu/jquery.ui.position.js',
            'contextmenu/jquery.contextMenu.js',
            'js/catalogue/book_list.js',
        ),
        'output_filename': 'compressed/book_list.js',
    }
}
