# Generated by Django 3.1.13 on 2021-08-13 15:44

from django.db import migrations


initial_tags = {
    "section": {
        "opowiadanie": {},
        "powiesc": {},
        "liryka_l": {},
        "liryka_lp": {},
        "dramat_wierszowany_l": {},
        "dramat_wierszowany_lp": {},
        "dramat_wspolczesny": {},
        "wywiad": {},
        "nota": {},
        "nota_red": {
            "editor_css": """
            background-color: #eee;
            border: 1px solid #888;
            border-radius: 10px;
            display: block;
            padding: 0 1em 1em 1em;
            """
        },
        "dedykacja": {},
        "ramka": {},
        "lista_osob": {},
        "dlugi_cytat": {},
        "poezja_cyt": {
            "editor_css": """margin: 1.5em 2em 0;
font-size: 0.875em;"""
        },
        "kwestia": {
            "editor_css": """
                margin: 5em 0 0;
            """
        },
        "wywiad_pyt": {},
        "wywiad_odp": {},
        "motto": {
            "editor_css": """
                text-align: justify;
                font-style: italic;
            """
        },
    },
    "div": {
        "didaskalia": {
            "editor_css": """font-style: italic;
margin: 0.5em 0 0 1.5em;"""
        },
        "naglowek_podrozdzial": {
            "editor_css": """
                font-size: 1em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        },
        "naglowek_osoba": {
            "editor_css": """
                font-size: 1em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "podtytul": {
            "editor_css": """
                font-size: 1.5em;
                margin: 1.5em 0 0;
                font-weight: normal;
                line-height: 1.5em;
            """
        }, 
        "naglowek_scena": {
            "editor_css": """
                font-size: 1.5em;
                margin: 1.5em 0 0;
                font-weight: normal;
                line-height: 1.5em;
            """
        }, 
        "naglowek_rozdzial": {
            "editor_css": """
                font-size: 1.5em;
                margin: 1.5em 0 0;
                font-weight: normal;
                line-height: 1.5em;
            """
        }, 
        "autor_utworu": {
            "editor_css": """
                font-size: 2em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "dzielo_nadrzedne": {
            "editor_css": """
                font-size: 2em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "naglowek_czesc": {
            "editor_css": """
                font-size: 2em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "srodtytul": {
            "editor_css": """
                font-size: 2em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "naglowek_akt": {
            "editor_css": """
                font-size: 2em;
                margin: 1.5em 0 0;
                font-weight: bold;
                line-height: 1.5em;
            """
        }, 
        "nazwa_utworu": {
            "editor_css": """
                font-size: 3em;
                margin: 1.5em 0;
                text-align: center;
                line-height: 1.5em;
                font-weight: bold;
            """,
        }, 
        "naglowek_listy": {}, 
        "lista_osoba": {}, 
        "miejsce_czas": {
            "editor_css": """font-style: italic;""",
        }, 
        "akap": {
            "editor_css": """
                text-align: justify;
                margin: 1.5em 0 0;
            """
        }, 
        "akap_cd": {
            "editor_css": """
                text-align: justify;
                margin: 1.5em 0 0;
            """
        }, 
        "akap_dialog": {
            "editor_css": """
                text-align: justify;
                margin: 1.5em 0 0;
            """
        }, 
        "motto_podpis": {
            "editor_css": """
                position: relative;
                right: -3em;
                text-align: right;
            """
        }, 
        "uwaga": {}, 
        "extra": {},
    },
    "verse": {
        "wers_cd": {}, 
        "wers_akap": {
            "editor_css": """padding-left: 1em;"""
        }, 
        "wers_wciety": {}, 
        "wers_do_prawej": {
            "editor_css": """
                text-align: right;
            """
        }, 
        "wers": {},
    },
    "span": {
        "tytul_dziela": {
            "editor_css": """font-style: italic;"""
        }, 
        "wyroznienie": {
            "editor_css": """font-style: italic;
letter-spacing: 0.1em;"""
        }, 
        "slowo_obce": {
            "editor_css": """font-style: italic;"""
        }, 
        "mat": {
            "editor_css": """font-style: italic;"""
        }, 
        "didask_tekst": {}, 
        "osoba": {
            "editor_css": """font-style: normal;
font-variant: small-caps;"""
        }, 
        "wyp_osoba": {}, 
        "www": {}, 
        "wieksze_odstepy": {
            "editor_css": """font-style: normal;
word-spacing: 1em;"""
        }, 
        "indeks_dolny": {
            "editor_css": """font-style: normal;
vertical-align: sub;
font-size: .9em;"""
        }, 
        "zastepnik_wersu": {},
    },
    "sep": {
        "sekcja_swiatlo": {
            "editor_css": """
            margin: 2em 0;
            visibility: hidden;
            """
        }, 
        "sekcja_asterysk": {
            "editor_css": """
            border: none;
            text-align: center;
            """,
            "editor_css_after": """
            content: "*";
            """
        }, 
        "separator_linia": {
            "editor_css": """
            margin: 1.5em 0;
            border: none;
            border-bottom: 0.1em solid #000;
            """
        },
    },
    "aside": {
        "pr": {}, 
        "pa": {}, 
        "pe": {}, 
        "pt": {},
    }

    # To nie są wszystkie tagi.
    # Brakuje:
    # strofa?
    # motyw,begin,end?
    # ref?
}


def create_tags(apps, schema_editor):
    Tag = apps.get_model('wlxml', 'Tag')
    for tag_type, tags in initial_tags.items():
        for name, props in tags.items():
            Tag.objects.create(
                type=tag_type,
                name=name,
                **props
            )


class Migration(migrations.Migration):

    dependencies = [
        ('wlxml', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_tags,
            migrations.RunPython.noop
        )
    ]