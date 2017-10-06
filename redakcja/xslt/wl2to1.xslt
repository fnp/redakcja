<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:wl="http://wolnelektury.pl/functions"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    exclude-result-prefixes="wl dc"><!-- nie jestem pewien czy tak ma być -->
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

            <xsl:if test="not(/section/metadata/dc:publisher)">
                <dc:publisher xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">Fundacja Nowoczesna Polska</dc:publisher>
            </xsl:if>
            <dc:rights xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">Creative Commons Uznanie autorstwa - Na tych samych warunkach 3.0</dc:rights>
            <dc:rights.license xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">http://creativecommons.org/licenses/by-sa/3.0/</dc:rights.license>
            <dc:format xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">xml</dc:format>
            <!--dc:type xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">added-var</dc:type-->
            <xsl:if test="not(/section/metadata/dc:date)">
                <dc:date xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">2015-01-12</dc:date>
            </xsl:if>
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
        <xsl:otherwise><xsl:apply-templates /></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- TODO language-dependent: description, audience, requires (subject.competence?) -->
<xsl:template match="dc:creator.expert|dc:creator.scenario|dc:creator.textbook|dc:description|dc:subject.curriculum|dc:subject.curriculum.new|dc:creator.methodologist|dc:subject.competence|dc:audience|dc:type|dc:requires|dc:relation|dc:subject|dc:date|dc:publisher" mode="meta">
    <xsl:copy><xsl:apply-templates /></xsl:copy>
</xsl:template>

<xsl:template match="metadata"/>
<xsl:template match="aside">
    <xsl:if test="@class = 'gap'">
        <luka><xsl:apply-templates/></luka>
    </xsl:if>
</xsl:template>


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
            <lista typ="punkt">
                <xsl:if test="@name">
                    <xsl:attribute name="nazwa"><xsl:value-of select="@name"/></xsl:attribute>
                </xsl:if>
                <xsl:if test="@dest">
                    <xsl:attribute name="cel"><xsl:value-of select="@dest"/></xsl:attribute>
                </xsl:if>
                <xsl:if test="@handles">
                    <xsl:attribute name="uchwyty"><xsl:value-of select="@handles"/></xsl:attribute>
                </xsl:if>
                <xsl:if test="@short">
                    <xsl:attribute name="krotkie"><xsl:value-of select="@short"/></xsl:attribute>
                </xsl:if>
                <xsl:apply-templates />
            </lista>
        </xsl:when>
        <xsl:when test="@class = 'list.itemized'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.orderable'">
            <lista typ="punkt"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.enum'">
            <lista typ="num"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'list.definitions'">
            <lista typ="slowniczek">
                <xsl:if test="@src">
                    <xsl:attribute name="src"><xsl:value-of select="@src"/></xsl:attribute>
                </xsl:if>
                <xsl:apply-templates />
            </lista>
        </xsl:when>
        <xsl:when test="@class = 'list.bibliography'">
            <lista typ="czytelnia"><xsl:apply-templates /></lista>
        </xsl:when>
        <xsl:when test="@class = 'item'">
            <punkt><xsl:apply-templates /></punkt>
        </xsl:when>
        <xsl:when test="@class = 'item.category'">
            <punkt nazwa="{@name}"><xsl:apply-templates /></punkt>
        </xsl:when>
        <xsl:when test="@class = 'item.answer'">
            <punkt>
                <xsl:attribute name="rozw">
                    <xsl:choose>
                        <xsl:when test="@answer = 'true'">prawda</xsl:when>
                        <xsl:when test="@answer = 'false'">falsz</xsl:when>
                        <xsl:otherwise><xsl:value-of select="@answer" /></xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
                <xsl:apply-templates />
            </punkt>
        </xsl:when>
        <xsl:when test="@class = 'question'">
            <pytanie>
                <xsl:for-each select="div">
                    <xsl:choose>
                        <xsl:when test="@class = 'p'">
                            <xsl:apply-templates />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:apply-templates select="."/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </pytanie>
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
        <xsl:when test="@class = 'img'">
            <obraz nazwa="{@name}" alt="{@alt}"/>
        </xsl:when>
        <xsl:when test="@class = 'video'">
            <video url="{@src}"/>
        </xsl:when>
        <xsl:when test="@class = 'label'">
            <podpis>
                <xsl:apply-templates/>
            </podpis>
        </xsl:when>
        <xsl:when test="@class = 'solution.comment'">
            <rozw_kom>
                <xsl:apply-templates/>
            </rozw_kom>
        </xsl:when>
        <xsl:when test="@class = 'important'">
            <dlugi_cytat>
                <xsl:apply-templates/>
            </dlugi_cytat>
        </xsl:when>
        <xsl:when test="@class = 'exercise.order'">
            <cwiczenie typ="uporzadkuj">
                <xsl:call-template name="cwiczenie"/>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'exercise.choice.true-or-false'">
            <cwiczenie typ="prawdafalsz">
                <xsl:call-template name="cwiczenie"/>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'exercise.choice' or @class = 'exercise.choice.single'">
            <cwiczenie typ="wybor">
                <xsl:call-template name="cwiczenie"/>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'exercise.match'">
            <cwiczenie typ="przyporzadkuj">
                <xsl:call-template name="cwiczenie"/>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'exercise.gap'">
            <cwiczenie typ="luki">
                <xsl:choose>
                    <xsl:when test="div[1]/aside[@class = 'gap']">
                        <opis><akap>Uzupełnij luki:</akap></opis>
                        <xsl:apply-templates/>
                    </xsl:when>
                    <xsl:otherwise>
                        <opis><xsl:apply-templates select="*[1]"/></opis>
                        <xsl:apply-templates select="*[position() > 1]"/>
                    </xsl:otherwise>
                </xsl:choose>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'exercise.replace'">
            <cwiczenie typ="zastap">
                <xsl:choose>
                    <xsl:when test="div[1]/aside[@class = 'gap']">
                        <opis><akap>Znajdź i zamień niepasujące słowa w zdaniach na następujące:</akap></opis>
                        <xsl:apply-templates/>
                    </xsl:when>
                    <xsl:otherwise>
                        <opis><xsl:apply-templates select="*[1]"/></opis>
                        <xsl:apply-templates select="*[position() > 1]"/>
                    </xsl:otherwise>
                </xsl:choose>
            </cwiczenie>
        </xsl:when>
        <xsl:when test="@class = 'table'">
            <tabela ramki="0">
                <xsl:apply-templates/>
            </tabela>
        </xsl:when>
        <xsl:when test="@class = 'table.row'">
            <wiersz><xsl:apply-templates/></wiersz>
        </xsl:when>
        <xsl:when test="@class = 'table.cell'">
            <kol><xsl:apply-templates/></kol>
        </xsl:when>
        <xsl:when test="@class = 'verse'">
            <strofa><xsl:apply-templates/></strofa>
        </xsl:when>
        <xsl:otherwise>
            <NIEZNANY_DIV><xsl:value-of select="@class" /></NIEZNANY_DIV>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="div" mode="opis">
    <xsl:choose>
        <xsl:when test="@class != 'list.definitions'">
            <xsl:apply-templates select="." />
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
                    <xsl:when test="starts-with(@href, 'http') or starts-with(@href, '#')">
                        <xsl:attribute name="url">
                            <xsl:value-of select="@href" />
                        </xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="url">
                            <xsl:value-of select="." />
                        </xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:apply-templates />
            </link>
        </xsl:when>
        <xsl:when test="@class = 'emp'">
            <wyroznienie><xsl:apply-templates /></wyroznienie>
        </xsl:when>
        <xsl:when test="@class = 'cite'">
            <tytul_dziela><xsl:apply-templates /></tytul_dziela>
        </xsl:when>
        <xsl:when test="@class = 'answer'">
            <zastap rozw="{@answer}"><xsl:apply-templates/></zastap>
        </xsl:when>
        <xsl:otherwise>
            <NIEZNANY_SPAN><xsl:value-of select="@class" /></NIEZNANY_SPAN>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="section" mode="error">
    NIEZNANA_SEKCJA
</xsl:template>

<xsl:template name="cwiczenie">
    <xsl:for-each select="div">
        <xsl:choose>
            <xsl:when test="@class = 'p'">
                <opis><xsl:apply-templates select="."/></opis>
                <!-- https://stackoverflow.com/questions/27374493/grouping-the-consecutive-elements-in-xslt -->
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
