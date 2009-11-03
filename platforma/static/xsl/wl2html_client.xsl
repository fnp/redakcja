<xsl:stylesheet version="1.0"    
    xmlns="http://www.w3.org/1999/xhtml"    
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!--
        Dokument ten opisuje jednoznaczne przekształcenie WLML 0.1 -> XHTML.
    -->        
    <xsl:output method="html" encoding="utf-8" indent="yes" />

    <xsl:template match="/">
        <xsl:apply-templates select="chunk|utwor" />
    </xsl:template>

    <!--
        Base tag for rendering a fragment of text
    -->
    <xsl:template match="chunk">        
        <xsl:apply-templates select="child::node()">            
            <xsl:with-param name="mixed" select="true()" />
        </xsl:apply-templates>        
    </xsl:template>
    
    <!--
        Base tag for rendering the whole text 
    -->

    <xsl:template match="utwor">
        <xsl:apply-templates select="child::*[name() = local-name()]">
            <xsl:with-param name="mixed" select="false()" />
        </xsl:apply-templates>
    </xsl:template>    
    
    <!-- 
        Przekształcenia poszczególnych elementów zgodnie z:            
        http://wiki.wolnepodreczniki.pl/Lektury:Sk%C5%82ad/Tagi_sk%C5%82adu
    -->

    <!-- TAGI MASTERÓW STYLÓW
    
        Tagi rozpoczynające i kończące tekst utworu lirycznego o standardowej szerokości łamu:
    -->

    <xsl:template match="opowiadanie|powiesc">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="liryka_l|liryka_lp">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="dramat_wierszowany_l|dramat_wierszowany_lp|dramat_wspolczesny">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="wywiad">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <!-- 
        *****************************
        ELEMENTY POZA TEKSTEM GŁÓWNYM
        *****************************
    -->

    <!--
        Autor składanego utworu

        Element strony tytułowej - lub odpowiadającej jej przestrzeni,
        np. na stronie internetowej) :

        <autor_utworu> imiona-itd.-autora-składanego-utworu </autor_utworu>
    -->
    <xsl:template match="autor_utworu">
        <xsl:param name="mixed" />
        <h2 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h2>
    </xsl:template>

    <!-- 
        Nazwa składanego utworu

        Element strony tytułowej - lub odpowiadającej jej przestrzeni,
        np. na stronie internetowej

        <nazwa_utworu> tytuł-składanego-utworu </nazwa_utworu>
    -->
    <xsl:template match="nazwa_utworu">
        <xsl:param name="mixed" />
        <h1 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h1>
    </xsl:template>

    <!--
        Nazwa utworu nadrzędnego, w którego skład wchodzi dany utwór
        <dzielo_nadrzedne> tytuł-dzieła-nadrzędnego </dzielo_nadrzedne>

         Przykład:

         <utwor>
         <liryka_l>
            <autor_utworu>Bruno Jasieński</autor_utworu>
            <dzielo_nadrzedne>But w butonierce</dzielo_nadrzedne>
            <nazwa_utworu>Deszcz</nazwa_utworu>
            ....
    -->
    <xsl:template match="dzielo_nadrzedne">
        <xsl:param name="mixed" />
        <h2 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h2>
    </xsl:template>

    <!--
        Podtytuł, czyli wszystkie dopiski do tytułu

        Element strony tytułowej - lub odpowiadającej jej przestrzeni.
        <podtytul> podtytuł-składanego-utworu </podtytul>

        Przykład:
        <utwor>
            <powiesc>
            <autor_utworu>Daniel Defoe</autor_utworu>
            <nazwa_utworu>Robinson Crusoe</nazwa_utworu>
            <podtytul>Jego życia losy, doświadczenia i przypadki</podtytul>
            ...
    -->
    <xsl:template match="podtytul">
        <xsl:param name="mixed" />
        <h3 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h3>
    </xsl:template>

    <!--
       Tagi obejmujące tekst noty poprzedzającej tekst główny (styl wieloakapitowy):

        <nota><akap> tekst-noty </akap></nota> (styl wieloakapitowy)
    -->

    <xsl:template match="nota">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <!--
        Tagi obejmujące tekst dedykacji (styl wieloakapitowy bądź wielostrofowy):
        <dedykacja> tekst-dedykacji </dedykacja>
    -->
    <xsl:template match="dedykacja">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <!--
        Tagi obejmujące tekst motta (styl wieloakapitowy bądź wielostrofowy):
        <motto> tekst-motta </motto>
    -->
    <xsl:template match="motto">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="motto_podpis">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>

    <!--
        Tagi obejmujące listę osób poprzedzającą tekst dramatu
          (zwykle składaną na osobnej stronie; to odmiana stylu listy):

        <lista_osob> osoby </lista_osob>
    -->
    <xsl:template match="lista_osob">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="naglowek_listy">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>

    <xsl:template match="lista_osoba">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>


    <!--
        ***************************
        TAGI STYLÓW TEKSTU GŁÓWNEGO
        ***************************
    -->

    <!--
      Tagi nagłówka części/księgi:
      <naglowek_czesc> nagłówek-części-lub-księgi </naglowek_czesc>
    -->
    <xsl:template match="naglowek_czesc">
        <xsl:param name="mixed" />
        <h2 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h2>
    </xsl:template>

    <!--
      Tagi tytułu rozdziału:
      <naglowek_rozdzial> nr-i/lub-tytuł </naglowek_rozdzial>
    -->
    <xsl:template match="naglowek_rozdzial">
        <xsl:param name="mixed" />
        <h3 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h3>
    </xsl:template>

    <!--
      Tagi tytułu podrozdziału:
      <naglowek_podrozdzial> nr-i/lub-podtytuł </naglowek_podrozdzial>
    -->
    <xsl:template match="naglowek_podrozdzial">
        <xsl:param name="mixed" />
        <h4 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h4>
    </xsl:template>

    <!--
       Tagi sródtytułu:
       <srodtytul> śródtytuł </srodtytul>

       Tagi nagłówków aktów:
       <naglowek_akt> nagłówek-aktu </naglowek_akt>
    -->

    <xsl:template match="srodtytul">
        <xsl:param name="mixed" />
        <h2 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h2>
    </xsl:template>

    <xsl:template match="naglowek_akt">
        <xsl:param name="mixed" />
        <h2 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h2>
    </xsl:template>

    <!--
      Tagi nagłówków scen:
      <naglowek_scena> nagłówek-sceny </naglowek_scena>
    -->

    <xsl:template match="naglowek_scena">
        <xsl:param name="mixed" />
        <h3 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h3>
    </xsl:template>
    
    <xsl:template match="naglowek_osoba">
        <xsl:param name="mixed" />
        <h4 class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </h4>
    </xsl:template>

    <!--
       ************************
       Bloki w tekście głównym
       ************************
    -->
    
    <xsl:template match="dlugi_cytat">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>
    
    <xsl:template match="poezja_cyt">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="kwestia">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="didaskalia">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="wywiad_pyt">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <xsl:template match="wywiad_odp">
        <xsl:param name="mixed" />
        <div class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <!--
        ***********************************
        Style akapitowe oraz strofy i wersy
        ***********************************
    -->

    <xsl:template match="akap">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>

    <xsl:template match="akap_cd">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>

    <xsl:template match="akap_dialog">
        <xsl:param name="mixed" />
        <p class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </p>
    </xsl:template>

    <!--
        ********
        STROFA
        ********
    -->
    <xsl:template match="strofa">
        <div class="{name()}" x-editable="true" x-node="{name()}">
            <xsl:call-template name="context-menu" />
            <xsl:choose>
                <xsl:when test="count(br) > 0">
                    <xsl:variable name="first-verse" select="br[1]/preceding-sibling::node()" />                    
                    <xsl:call-template name="verse">
                        <xsl:with-param name="verse-content" select="$first-verse" />                        
                    </xsl:call-template>
                    <xsl:for-each select="br">
                        <xsl:variable name="lnum" select="count(preceding-sibling::br)" />
                        <!-- select all nodes up to the next br or end of stanza -->
                        <xsl:variable name="current-verse"
                            select="following-sibling::node()[count(preceding-sibling::br) = $lnum+1]" />                        
                        <xsl:call-template name="verse">
                            <xsl:with-param name="verse-content" select="$current-verse" />                            
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="verse">
                        <xsl:with-param name="verse-content" select="child::node()" />                        
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>

    <xsl:template name="verse">
        <!-- the verse contents including the last br (if any) -->
        <xsl:param name="verse-content" />
        
        <xsl:variable name="first-tag-name" select="name($verse-content/self::*)" />
        <!-- name of text nodes is '' == false -->

        <xsl:choose>
            <xsl:when test="starts-with($first-tag-name, 'wers')">
                <p class="{$first-tag-name}" x-node="{$first-tag-name}">
                <xsl:for-each select="$verse-content[name(.) != 'br']">
                <xsl:apply-templates select=".">
                    <xsl:with-param name="mixed" select="true()" />
                </xsl:apply-templates>
                </xsl:for-each>
                </p>
            </xsl:when>

            <xsl:otherwise>
                <p class="wers" x-node="wers">
                <xsl:for-each select="$verse-content[name(.) != 'br']">
                    <xsl:apply-templates select=".">
                    <xsl:with-param name="mixed" select="true()" />
                    </xsl:apply-templates>
                </xsl:for-each>
                </p>                
            </xsl:otherwise>          
            
        </xsl:choose>       
    </xsl:template>

    <xsl:template match="wers_cd|wers_akap|wers_wciety">
        <xsl:param name="mixed" />
        <xsl:call-template name="copy-attributes" />
        <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
    </xsl:template>
    

    <!--
        *************
        STYLE ZNAKOWE
        *************
    -->

    <!--
        Tagi obejmujące tytuł dzieła, np. książki, filmu, piosenki,
        modlitwy, przedstawienia teatr. itd.:

        <tytul_dziela> tytuł-dzieła </tytul_dziela>
    -->
    <xsl:template match="tytul_dziela">
        <xsl:param name="mixed" />
        <em class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </em>
    </xsl:template>

    <xsl:template match="wyroznienie|slowo_obce|mat|didask_tekst|osoba|wyp_osoba|www">
        <xsl:param name="mixed" />
        <em class="{name()}" x-node="{name()}">
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </em>
    </xsl:template>

    <!--
        **********
        SEPARATORY
        **********
    -->
    <xsl:template match="sekcja_swiatlo">
        <xsl:param name="mixed" />
        <br class="{name()}" x-node="{name()}" />
    </xsl:template>

    <xsl:template match="sekcja_asterysk">
        <xsl:param name="mixed" />
        <hr class="{name()}" x-node="{name()}" />
    </xsl:template>

    <xsl:template match="separator_linia">
        <xsl:param name="mixed" />
        <hr class="{name()}" x-node="{name()}" />
    </xsl:template>

    <xsl:template match="zastepnik_wersu">
        <xsl:param name="mixed" />
        <hr class="{name()}" x-node="{name()}" />
    </xsl:template>

    <!--
        *************
           PRZYPISY
        *************
    -->

    <!--
        Przypisy i motywy
    -->
    <xsl:template match="pr|pa|pe|pt">       
        <span class="annotation-inline-box" x-node="{name()}" x-editable="true">
            <a name="anchor-{generate-id(.)}" />
            <!-- the link to the non-inline version -->
            <a href="#annotation-{generate-id(.)}" class="annotation"></a>
            <!-- inline contents -->
            <span x-annotation-box="true">
                <xsl:call-template name="context-menu" />
                <xsl:apply-templates select="node()">
                    <xsl:with-param name="mixed" select="true()" />
                </xsl:apply-templates>
            </span>
        </span>
    </xsl:template>

    <xsl:template match="begin">        
        <span class="theme-begin" x-node="begin">
            <xsl:call-template name="copy-attributes" />
        </span>
    </xsl:template>

    <xsl:template match="motyw">
        <span class="theme-ref" x-node="motyw">
            <xsl:call-template name="copy-attributes" />
            <xsl:value-of select="." />
        </span>
    </xsl:template>

    <xsl:template match="end">
        <span class="theme-end" x-node="end">
            <xsl:call-template name="copy-attributes" />
        </span>
    </xsl:template>


    <!--
        ****************
         TEKST WŁAŚCIWY
        ****************
    -->

    <xsl:template match="text()">
        <xsl:param name="mixed" />
        <xsl:choose>
            <xsl:when test="normalize-space(.) = ''" />
            <xsl:when test="not($mixed)">
                <span x-node="text" class="out-of-flow-text"
                    x-content="{normalize-space(.)}"></span>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="." />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="*">
        <div x-node="error" x-content="{name()}" />
    </xsl:template>

    <xsl:template name="context-menu">
        <span class="default-menu context-menu">
            <span class="edit-button">Edit</span>
        </span>
        <span class="edit-menu context-menu">
            <span class="accept-button">OK</span>
            <span class="reject-button">Cancel</span>
        </span>
    </xsl:template>

    <xsl:template name="copy-attributes">
        <xsl:for-each select="@*">
            <xsl:attribute name="x-attrib-{name(.)}"><xsl:value-of select="."/></xsl:attribute>
        </xsl:for-each>
    </xsl:template>
    
</xsl:stylesheet>