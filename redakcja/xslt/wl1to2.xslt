<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                exclude-result-prefixes="rdf">
    <xsl:output encoding="utf-8" indent="yes" omit-xml-declaration="yes" version="2.0"/>

    <xsl:template match="utwor">
        <section xmlns:dc="http://purl.org/dc/elements/1.1/">
            <xsl:apply-templates/>
        </section>
    </xsl:template>

    <xsl:template match="rdf:RDF">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="rdf:Description">
        <metadata>
            <xsl:apply-templates mode="meta"/>
        </metadata>
    </xsl:template>

    <xsl:template
            match="dc:title|dc:identifier.url|dc:publisher|dc:rights|dc:rights.license|dc:format|dc:date|dc:language|dc:description.material|dc:relation.isPartOf"
            mode="meta"/>

    <!-- TODO language-dependent: description, audience, requires (subject.competence?) -->
    <xsl:template
            match="dc:creator.expert|dc:creator.scenario|dc:creator.textbook|dc:description|dc:subject.curriculum|dc:creator.methodologist|dc:subject.competence|dc:audience|dc:type|dc:requires|dc:relation|dc:subject|dc:publisher|dc:date"
            mode="meta">
        <xsl:copy>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="powiesc">
        <xsl:apply-templates select="nazwa_utworu"/>
        <xsl:apply-templates select="naglowek_rozdzial"/>
    </xsl:template>

    <xsl:template match="nazwa_utworu">
        <header>
            <xsl:apply-templates mode="tekst"/>
        </header>
    </xsl:template>

    <xsl:key name="k_rozdzial"
           match="naglowek_podrozdzial"
           use="generate-id(preceding-sibling::naglowek_rozdzial[1])"/>

    <xsl:key name="k_last_header"
             match="*[not(starts-with(name(),'naglowek_'))]"
             use="generate-id(preceding-sibling::*[starts-with(name(),'naglowek_')][1])"/>

    <xsl:template match="naglowek_rozdzial">
        <section>
            <xsl:if test="contains(./text(), 'Pomysł na lekcję')">
                <metadata><dc:audience>teacher</dc:audience></metadata>
            </xsl:if>
            <header><xsl:apply-templates mode="tekst"/></header>
            <xsl:apply-templates select="key('k_last_header', generate-id())" mode="rozdzial"/>
            <xsl:apply-templates select="key('k_rozdzial', generate-id())" mode="rozdzial"/>
        </section>
    </xsl:template>

    <xsl:template match="naglowek_podrozdzial" mode="rozdzial">
        <section>
            <header><xsl:apply-templates mode="tekst"/></header>
            <xsl:apply-templates select="key('k_last_header', generate-id())" mode="rozdzial"/>
        </section>
    </xsl:template>

    <xsl:template match="akap" mode="rozdzial">
        <div class="p"><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <xsl:template match="akap" mode="opis">
        <header><xsl:number format="1. " count="aktywnosc"/><xsl:apply-templates mode="tekst"/></header>
    </xsl:template>

    <xsl:template match="opis" mode="rozdzial">
        <xsl:apply-templates mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="akap" mode="tekst"><!-- for akap inside punkt -->
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="uwaga" mode="rozdzial">
        <aside class="comment"><xsl:apply-templates mode="tekst"/></aside>
    </xsl:template>
    <xsl:template match="uwaga" mode="tekst">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>
    <xsl:template match="uwaga" mode="lista">
        <div class="item"><xsl:apply-templates select="." mode="rozdzial"/></div>
    </xsl:template>

    <xsl:template match="text()[normalize-space()]" mode="rozdzial">
        <div class="p"><xsl:value-of select="normalize-space()"/></div>
    </xsl:template>

    <xsl:template match="lista" mode="rozdzial">
        <div>
            <xsl:attribute name="class">
                <xsl:choose>
                    <xsl:when test="@typ = 'punkt' or @nazwa or @cel">list</xsl:when>
                    <xsl:when test="@typ = 'num'">list.enum</xsl:when>
                    <xsl:when test="@typ = 'alfa'">list</xsl:when>
                    <xsl:when test="@typ = 'slowniczek'">list.definitions</xsl:when>
                    <xsl:when test="@typ = 'czytelnia'">list.bibliography</xsl:when>
                </xsl:choose>
            </xsl:attribute>
            <xsl:if test="@nazwa">
                <xsl:attribute name="name"><xsl:value-of select="@nazwa"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@cel">
                <xsl:attribute name="dest"><xsl:value-of select="@cel"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@uchwyty">
                <xsl:attribute name="handles"><xsl:value-of select="@uchwyty"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@krotkie">
                <xsl:attribute name="short"><xsl:value-of select="@krotkie"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@src">
                <xsl:attribute name="src"><xsl:value-of select="@src"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates mode="lista"/>
        </div>
    </xsl:template>

    <xsl:template match="lista" mode="lista">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="lista" mode="tekst">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="punkt" mode="lista">
        <xsl:choose>
            <xsl:when test="@rozw">
                <div class="item.answer">
                    <xsl:attribute name="answer">
                        <xsl:choose>
                            <xsl:when test="@rozw = 'prawda'">true</xsl:when>
                            <xsl:when test="@rozw = 'falsz'">false</xsl:when>
                            <xsl:otherwise><xsl:value-of select="@rozw"/></xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                    <xsl:apply-templates mode="tekst"/>
                </div>
            </xsl:when>
            <xsl:when test="@nazwa">
                <div class="item.category" name="{@nazwa}">
                    <xsl:apply-templates mode="tekst"/>
                </div>
            </xsl:when>
            <xsl:otherwise>
                <div class="item">
                    <xsl:apply-templates mode="tekst"/>
                </div>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="definiendum" mode="tekst">
        <div class="defined">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

    <xsl:template match="dlugi_cytat" mode="rozdzial">
        <div class="important">
            <xsl:apply-templates mode="rozdzial"/>
        </div>
    </xsl:template>

    <xsl:template match="obraz" mode="rozdzial">
        <div class="img" name="{@nazwa}" alt="{@alt}"/>
    </xsl:template>

    <xsl:template match="obraz" mode="tekst"><!-- inside punkt -->
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="video" mode="rozdzial">
        <div class="video" src="{@url}"/>
    </xsl:template>

    <xsl:template match="podpis" mode="rozdzial">
        <div class="label">
            <xsl:apply-templates mode="rozdzial"/>
        </div>
    </xsl:template>

    <xsl:template match="strofa" mode="tekst">
        <div class="verse"><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <!-- aktywnosc -->

    <xsl:template match="aktywnosc" mode="rozdzial">
        <section>
            <xsl:apply-templates select="opis/akap[1]" mode="opis"/>
            <xsl:apply-templates select="opis/*[position() > 1]" mode="rozdzial"/>
            <xsl:apply-templates select="akap|lista" mode="rozdzial"/>
            <xsl:apply-templates select="wskazowki" mode="rozdzial"/>
            <div class="list.definitions">
                <xsl:apply-templates select="czas|forma|pomoce" mode="aktywnosc"/>
            </div>
        </section>
    </xsl:template>

    <xsl:template match="czas" mode="aktywnosc">
        <div class="item"><div class="defined">Czas</div><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <xsl:template match="forma" mode="aktywnosc">
        <div class="item"><div class="defined">Metoda</div><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <xsl:template match="pomoce" mode="aktywnosc">
        <div class="item"><div class="defined">Pomoce</div><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <!-- inline elements -->

    <xsl:template match="link" mode="tekst">
        <span class="link">
            <xsl:attribute name="href">
                <xsl:choose>
                    <xsl:when test="@material">
                        <xsl:value-of select="concat('file://', @material)"/>
                    </xsl:when>
                    <xsl:when test="@url">
                        <xsl:value-of select="@url"/>
                    </xsl:when>
                </xsl:choose>
            </xsl:attribute>
            <xsl:apply-templates mode="tekst"/>
        </span>
    </xsl:template>

    <xsl:template match="wyroznienie" mode="tekst">
        <span class="emp">
            <xsl:apply-templates mode="tekst"/>
        </span>
    </xsl:template>

    <xsl:template match="tytul_dziela|slowo_obce" mode="tekst">
        <span class="cite"><xsl:apply-templates mode="tekst"/></span>
    </xsl:template>

    <!-- exercises -->

    <xsl:template match="cwiczenie" mode="rozdzial">
        <xsl:choose>
            <xsl:when test="@typ = 'uporzadkuj'">
                <div class="exercise.order">
                    <xsl:apply-templates select="opis/*" mode="rozdzial"/>
                    <div class="list.orderable">
                        <xsl:apply-templates select="lista/punkt" mode="lista"/>
                    </div>
                </div>
            </xsl:when>
            <xsl:when test="@typ = 'prawdafalsz'">
                <div class="exercise.choice.true-or-false">
                    <xsl:apply-templates mode="rozdzial"/>
                </div>
            </xsl:when>
            <xsl:when test="@typ = 'luki'">
                <div class="exercise.gap">
                    <xsl:apply-templates mode="rozdzial"/>
                </div>
            </xsl:when>
            <xsl:when test="@typ = 'zastap'">
                <div class="exercise.replace">
                    <xsl:apply-templates mode="rozdzial"/>
                </div>
            </xsl:when>
            <xsl:when test="@typ = 'przyporzadkuj'">
                <div class="exercise.match">
                    <xsl:apply-templates mode="rozdzial"/>
                </div>
            </xsl:when>
            <xsl:when test="@typ = 'wybor'">
                <div>
                    <xsl:attribute name="class">
                        <xsl:choose>
                            <xsl:when
                                    test="count(.//pytanie) = count(.//punkt[@rozw='prawda']) or (count(.//pytanie) = 0 and count(.//punkt[@rozw='prawda']) = 1)">exercise.choice.single</xsl:when>
                            <xsl:otherwise>exercise.choice</xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                    <xsl:apply-templates mode="rozdzial"/>
                </div>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="luka" mode="tekst">
        <aside class="gap"><xsl:apply-templates mode="tekst"/></aside>
    </xsl:template>

    <xsl:template match="zastap" mode="tekst">
        <span class="answer" answer="{@rozw}"><xsl:apply-templates mode="tekst"/></span>
    </xsl:template>

    <xsl:template match="pytanie" mode="rozdzial">
        <div class="question">
            <xsl:apply-templates mode="rozdzial"/>
        </div>
    </xsl:template>

    <xsl:template match="pytanie" mode="tekst">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="rozw_kom" mode="rozdzial">
        <div class="solution.comment">
            <xsl:apply-templates mode="rozdzial"/>
        </div>
    </xsl:template>
    <xsl:template match="rozw_kom" mode="tekst">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <!-- table -->

    <xsl:template match="tabela" mode="rozdzial">
        <div class="table">
            <xsl:apply-templates mode="tabela"/>
        </div>
    </xsl:template>

    <xsl:template match="wiersz" mode="tabela">
        <div class="table.row">
            <xsl:apply-templates mode="wiersz"/>
        </div>
    </xsl:template>

    <xsl:template match="kol" mode="wiersz">
        <div class="table.cell">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

</xsl:stylesheet>
