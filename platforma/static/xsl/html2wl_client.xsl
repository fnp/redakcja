<xsl:stylesheet 
    version="1.0"

    xmlns:html="http://www.w3.org/1999/xhtml"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
>

    <xsl:output method="xml" encoding="utf-8" indent="yes" omit-xml-declaration="yes" />
    <!--
        Ten dokument definiuję przekształcenie odwrotne do wl2html
    -->

    <xsl:template match="comment()"><xsl:copy /></xsl:template>

    <!-- libxslt has fuck-ed prorities -->
    <!-- <xsl:template match="@*[not(starts-with(name(), 'x-')) and name() != 'class']">
        <xsl:message>Boom!: <xsl:value-of select="name()" /></xsl:message>
    </xsl:template> -->

    <xsl:template match="@*" priority="0" />

    <!-- Specjalne reguły dla przypisów -->
    <xsl:template match="*[@x-annotation-box]|*[@class='theme-text-list']">
        <xsl:apply-templates select="node()" />
    </xsl:template>

    <xsl:template match="*[@x-node]">
        <xsl:element name="{@x-node}" namespace="{@x-ns}">
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="node()" />
        </xsl:element>
    </xsl:template>   

    <xsl:template match="*[@x-node = 'out-of-flow-text']"><xsl:value-of select="@x-content" /></xsl:template>

    <!-- Specjalne reguły dla wersów -->
    <xsl:template match="*[@x-node = 'wers']">
        <xsl:apply-templates select="node()" />
        <xsl:if test="count(following-sibling::*[starts-with(@x-node, 'wers')]) > 0"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>

    <xsl:template match="*[starts-with(@x-node, 'wers_')]">
        <xsl:element name="{@x-node}" namespace="{@x-ns}"><xsl:apply-templates select="@*|node()" /></xsl:element>
        <xsl:if test="count(following-sibling::*[starts-with(@x-node, 'wers')]) > 0"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>
    
    <xsl:template match="@*[starts-with(name(), 'x-attr-qname-')]">
        <xsl:variable name="attr-id" select="substring-after(name(), 'x-attr-qname-')" />
        <xsl:attribute name="{.}" namespace="{parent::*/@*[name() = concat('x-attr-ns-', $attr-id)]}">
            <xsl:value-of select="parent::*/@*[name() = concat('x-attr-value-', $attr-id)]" />
        </xsl:attribute>
    </xsl:template>

    <!-- upper case duplicates for the brain-dead Firefox -->

    <xsl:template match="@*[starts-with(name(), 'X-ATTR-QNAME-')]">
        <xsl:variable name="attr-id" select="substring-after(name(), 'X-ATTR-QNAME-')" />
        <xsl:attribute name="{.}" namespace="{parent::*/@*[name() = concat('X-ATTR-NS-', $attr-id)]}">
            <xsl:value-of select="parent::*/@*[name() = concat('X-ATTR-VALUE-', $attr-id)]" />
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="*[@X-ANNOTATION-BOX]">
        <xsl:apply-templates select="node()" />
    </xsl:template>

    <xsl:template match="*[@X-NODE]">
        <xsl:element name="{@X-NODE}" namespace="{@X-NS}">
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="node()" />
        </xsl:element>
    </xsl:template>

    <xsl:template match="*[@X-NODE = 'out-of-flow-text']"><xsl:value-of select="@X-CONTENT" /></xsl:template>

    <!-- Specjalne reguły dla wersów -->
    <xsl:template match="*[@X-NODE = 'wers']">
        <xsl:apply-templates select="node()" />
        <xsl:if test="count(following-sibling::*[starts-with(@X-NODE, 'wers')]) > 0"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>

    <xsl:template match="*[starts-with(@X-NODE, 'wers_')]">
        <xsl:element name="{@X-NODE}" namespace="{@X-NS}"><xsl:apply-templates select="@*|node()" /></xsl:element>
        <xsl:if test="count(following-sibling::*[starts-with(@X-NODE, 'wers')]) > 0"><xsl:text>/&#x000a;</xsl:text></xsl:if>
    </xsl:template>
        
    <xsl:template match="*" />
        
    
</xsl:stylesheet>