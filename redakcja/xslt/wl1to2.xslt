<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:wl="http://wolnelektury.pl/functions"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
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
            match="dc:title|dc:identifier.url|dc:publisher|dc:rights|dc:rights.license|dc:format|dc:date"
            mode="meta"/>

    <!-- TODO language-dependent: description, audience, requires (subject.competence?) -->
    <xsl:template
            match="dc:creator.expert|dc:creator.scenario|dc:creator.textbook|dc:description|dc:subject.curriculum|dc:creator.methodologist|dc:subject.competence|dc:audience|dc:type|dc:requires|dc:language"
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
            <xsl:apply-templates/>
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
            <xsl:if test="./text() = 'Pomysł na lekcję'">
                <metadata><dc:audience>teacher</dc:audience></metadata>
            </xsl:if>
            <header><xsl:apply-templates/></header>
            <xsl:apply-templates select="key('k_last_header', generate-id())" mode="rozdzial"/>
            <xsl:apply-templates select="key('k_rozdzial', generate-id())" mode="rozdzial"/>
        </section>
    </xsl:template>

    <xsl:template match="naglowek_podrozdzial" mode="rozdzial">
        <section>
            <header><xsl:apply-templates/></header>
            <xsl:apply-templates select="key('k_last_header', generate-id())" mode="rozdzial"/>
        </section>
    </xsl:template>

    <xsl:template match="akap" mode="rozdzial">
        <div class="p"><xsl:apply-templates mode="tekst"/></div>
    </xsl:template>

    <xsl:template match="akap" mode="opis">
        <header><xsl:apply-templates mode="tekst"/></header>
    </xsl:template>

    <xsl:template match="lista" mode="rozdzial">
        <div>
            <xsl:attribute name="class">
                <xsl:choose>
                    <xsl:when test="@typ = 'num'">list.enum</xsl:when>
                    <xsl:when test="@typ = 'punkt'">list</xsl:when>
                    <xsl:when test="@typ = 'slowniczek'">list.definitions</xsl:when>
                    <xsl:when test="@typ = 'czytelnia'">list.bibliography</xsl:when>
                </xsl:choose>
            </xsl:attribute>
            <xsl:if test="@src != ''">
                <xsl:attribute name="src"><xsl:value-of select="@src"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates mode="lista"/>
        </div>
    </xsl:template>

    <xsl:template match="lista" mode="tekst">
        <xsl:apply-templates select="." mode="rozdzial"/>
    </xsl:template>

    <xsl:template match="punkt" mode="lista">
        <div class="item">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

    <xsl:template match="definiendum" mode="tekst">
        <div class="defined">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

    <xsl:template match="aktywnosc" mode="rozdzial">
        <section>
            <xsl:apply-templates select="opis/akap[1]" mode="opis"/>
            <xsl:apply-templates select="opis/*[position() > 1]" mode="rozdzial"/>
            <xsl:apply-templates select="wskazowki" mode="rozdzial"/>
            <div class="list.definitions">
                <xsl:apply-templates mode="aktywnosc"/>
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

    <xsl:template match="link" mode="tekst">
        <div class="link">
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
        </div>
    </xsl:template>

    <xsl:template match="wyroznienie" mode="tekst">
        <div class="emp">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

    <xsl:template match="dlugi_cytat" mode="tekst">
        <div class="cite">
            <xsl:apply-templates mode="tekst"/>
        </div>
    </xsl:template>

    <!-- exercises -->

    <xsl:template match="cwiczenie" mode="rozdzial">

    </xsl:template>

</xsl:stylesheet>
