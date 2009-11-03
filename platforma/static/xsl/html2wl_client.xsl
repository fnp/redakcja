<xsl:stylesheet 
    version="1.0"
    xmlns:html="http://www.w3.org/1999/xhtml"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="xml" encoding="utf-8" omit-xml-declaration = "yes" />
    <!--
        Ten dokument definiuję przekształcenie odwrotne do wl2html
    -->   

    <!-- Specjalne reguły dla przypisów -->
    <xsl:template match="*[@x-annotation-box]|*[@X-ANNOTATION-BOX]">
        <xsl:apply-templates select="node()" />
    </xsl:template>
   
    <xsl:template match="*[@x-node]">
        <xsl:element name="{@x-node}">            
            <xsl:apply-templates select="@*|node()" />
        </xsl:element>
    </xsl:template>

    <xsl:template match="*[@X-NODE]">
        <xsl:element name="{@X-NODE}">
            <xsl:apply-templates select="@*|node()" />
        </xsl:element>
    </xsl:template>

    <!-- Specjalne reguły dla wersów -->
    <xsl:template match="*[@x-node = 'wers' or @X-NODE = 'wers']">
        <xsl:apply-templates select="node()" />
        <xsl:if test="position() != last()"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>

    <xsl:template match="*[starts-with(@x-node, 'wers_')]">
        <xsl:element name="{@x-node}">            
            <xsl:apply-templates select="@*|node()" />
        </xsl:element>
        <xsl:if test="position() != last()"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>

    <xsl:template match="*[starts-with(@X-NODE, 'wers_')]">
        <xsl:element name="{@X-NODE}">
            <xsl:apply-templates select="@*|node()" />
        </xsl:element>
        <xsl:if test="position() != last()"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>

    <!-- Użycie zmiennych jako argumenty dla translate, psuję Chrome/Safari :( -->
    <xsl:template match="@*[starts-with(translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'x-attrib-')]">
        <xsl:attribute name="{substring-after(translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'x-attrib-')}"><xsl:value-of select="." /></xsl:attribute>
    </xsl:template>

    <xsl:template match="@*" /><!--[A:<xsl:value-of select="name()" />]</xsl:template> -->
    
    <xsl:template match="*" />
</xsl:stylesheet>