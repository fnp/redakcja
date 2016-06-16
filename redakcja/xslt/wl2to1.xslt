<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:wl="http://wolnelektury.pl/functions"
    xmlns:dc="http://purl.org/dc/elements/1.1/" >
<xsl:output encoding="utf-8" indent="yes" omit-xml-declaration = "yes" version="2.0" />

<xsl:template match="section">
    <xsl:choose>
        <xsl:when test="not(ancestor::*)">
        <utwor xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:wl="http://wolnelektury.pl/functions">
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <xsl:attribute name="rdf:about">
                <xsl:text>http://redakcja.edukacjamedialna.edu.pl/documents/book/</xsl:text>
                <xsl:value-of select="@redslug" />
                <xsl:text>/</xsl:text>
            </xsl:attribute>
        <dc:title xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/"><xsl:apply-templates select="header/text()" /></dc:title>
        <dc:identifier.url xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <xsl:text>http://edukacjamedialna.edu.pl/lekcje/</xsl:text>
            <xsl:value-of select="@wlslug" />
            <xsl:text>/</xsl:text>
        </dc:identifier.url>

        <!--dc:creator.expert xml:lang="pl" ></dc:creator.expert>
        <dc:creator.methodologist xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/"></dc:creator.methodologist>
        <dc:creator.scenario xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/"></dc:creator.scenario>
        <dc:creator.textbook xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/"></dc:creator.textbook-->

        <xsl:apply-templates select="metadata" mode="meta" />

        <dc:publisher xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">Fundacja Nowoczesna Polska</dc:publisher>
        <dc:rights xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">Creative Commons Uznanie autorstwa - Na tych samych warunkach 3.0</dc:rights>
        <dc:rights.license xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">http://creativecommons.org/licenses/by-sa/3.0/</dc:rights.license>
        <dc:format xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">xml</dc:format>
        <!--dc:type xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">added-var</dc:type-->
        <dc:date xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">2015-01-12</dc:date>
	<!--dc:audience xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/"><!- -liceum - -><xsl:value-of select="//dc:audience/text()" /></dc:audience-->
        <dc:language xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">pol</dc:language>
        </rdf:Description>
        </rdf:RDF>
        <powiesc>
            <xsl:apply-templates />
        </powiesc>
        </utwor>
    </xsl:when>
    <xsl:when test="count(ancestor::*) = 3">
        <aktywnosc>
            <opis><xsl:apply-templates select="header" /><xsl:apply-templates select="div" mode="opis" /></opis>
            <xsl:apply-templates select="div" mode="aktywnosc" />
            <xsl:apply-templates select="section" mode="error" />
        </aktywnosc>
</xsl:when>
<xsl:when test='header/text() = "Zadanie dla ucznia..."'>

</xsl:when>
    <xsl:otherwise><xsl:apply-templates /></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- TODO language-dependent: description, audience, requires (subject.competence?) -->
<xsl:template match="dc:creator.expert|dc:creator.scenario|dc:creator.textbook|dc:description|dc:subject.curriculum|dc:creator.methodologist|dc:subject.competence|dc:audience|dc:type|dc:requires" mode="meta">
    <xsl:copy><xsl:apply-templates /></xsl:copy>
</xsl:template>

<xsl:template match="metadata"></xsl:template>
<xsl:template match="aside"></xsl:template>


<xsl:template match="header">
    <xsl:choose>
        <xsl:when test="count(ancestor::*) = 1">
            <nazwa_utworu><xsl:apply-templates /></nazwa_utworu>
        </xsl:when>
        <xsl:when test="count(ancestor::*) = 2">
            <naglowek_rozdzial><xsl:apply-templates /></naglowek_rozdzial>
        </xsl:when>
        <xsl:when test="count(ancestor::*) = 3">
            <naglowek_podrozdzial><xsl:apply-templates /></naglowek_podrozdzial>
        </xsl:when>
        <xsl:when test="count(ancestor::*) = 4">
            <akap><xsl:apply-templates /></akap>
        </xsl:when>
    </xsl:choose>
</xsl:template>


<xsl:template match="div">
    <xsl:choose>
        <xsl:when test="@class = 'p'">
            <akap><xsl:apply-templates /></akap>
        </xsl:when>
        <xsl:when test="@class = 'list'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.itemized'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
	<xsl:when test="@class = 'list.enum'">
	    <lista typ="num"><xsl:apply-templates /></lista>
	</xsl:when>
        <xsl:when test="@class = 'list.definitions'">
            <lista typ="slowniczek"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.bibliography'">
            <lista typ="czytelnia"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'item'">
            <punkt><xsl:apply-templates /></punkt>
        </xsl:when>
        <xsl:when test="@class = 'defined'">
            <xsl:choose>
                <xsl:when test="count(ancestor::*) = 4 ">
                    <definiendum><xsl:apply-templates /></definiendum>
                </xsl:when>
                <xsl:otherwise>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
            <NIEZNANY_DIV><xsl:value-of select="@class" /></NIEZNANY_DIV>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="div" mode="opis">
    <xsl:choose>
        <xsl:when test="@class = 'p'">
            <akap><xsl:apply-templates /></akap>
        </xsl:when>
        <xsl:when test="@class = 'list'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.itemized'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'item'">
            <punkt><xsl:apply-templates /></punkt>
        </xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="div" mode="aktywnosc">
    <xsl:choose>
        <xsl:when test="@class = 'list.definitions'">
            <xsl:apply-templates mode="defs" />
        </xsl:when>
    </xsl:choose>
</xsl:template>


<xsl:template match="div" mode="defs">
    <xsl:choose>
        <xsl:when test="div/text() = 'Czas'"><czas><xsl:apply-templates /></czas></xsl:when>
        <xsl:when test="div/text() = 'Metoda'"><forma><xsl:apply-templates /></forma></xsl:when>
        <xsl:when test="div/text() = 'Pomoce'"><pomoce><xsl:apply-templates /></pomoce></xsl:when>
    </xsl:choose>
</xsl:template>

<xsl:template match="span">
    <xsl:choose>
        <xsl:when test="@class = 'link'">
            <link>
                <xsl:choose>
                    <xsl:when test="starts-with(@href, 'file://')">
                        <xsl:attribute name="material">
                            <xsl:value-of select="wl:rmext(substring(@href, 8))" />
                        </xsl:attribute>
		    </xsl:when>
		    <xsl:when test="starts-with(@href, 'http')">
				    <xsl:attribute name="url">
					    <xsl:value-of select="@href" />
				    </xsl:attribute>
		    </xsl:when>
		    <xsl:otherwise>
				    <xsl:attribute name="url">
					    <xsl:value-of select="text()" />
				    </xsl:attribute>
                    </xsl:otherwise>
	    </xsl:choose>
				<xsl:apply-templates />
            </link>
        </xsl:when>
        <xsl:when test="@class = 'emp'">
            <wyroznienie><xsl:apply-templates /></wyroznienie>
    </xsl:when>
    <xsl:when test="@class='cite'">
	    <dlugi_cytat><xsl:apply-templates /></dlugi_cytat>
    </xsl:when>
        <xsl:otherwise>
            <NIEZNANY_SPAN><xsl:value-of select="@class" /></NIEZNANY_SPAN>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>


<xsl:template match="section" mode="error">
    NIEZNANA_SEKCJA
</xsl:template>

</xsl:stylesheet>
