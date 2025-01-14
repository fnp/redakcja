<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"    
    xmlns="http://www.w3.org/1999/xhtml"    
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" omit-xml-declaration="yes" encoding="utf-8" indent="no" />

    <!--
        Base tag for rendering a fragment of text
    -->
    <xsl:template match="chunk">        
        <xsl:apply-templates select="child::node()">            
            <xsl:with-param name="mixed" select="true()" />
        </xsl:apply-templates>        
    </xsl:template>
    
    <xsl:template match="utwor">
        <div>
            <xsl:call-template name="standard-attributes" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>    


    <!-- nieedytowany - zawiera bloki   section-->
    <xsl:template match="{{ tags.section|join:"|" }}">
        <xsl:param name="mixed" />
        <div>
            <xsl:call-template name="standard-attributes" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>

    <!-- edytowalny - zawiera tekst      div -->
    <xsl:template match="{{ tags.div|join:"|" }}">
        <xsl:param name="mixed" />
        <div x-editable="true">
            <xsl:call-template name="standard-attributes" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </div>
    </xsl:template>
    
    <xsl:template match="ilustr">
      <div>
        <xsl:call-template name="standard-attributes" />
        <img>
          <xsl:attribute name="src">
            <xsl:value-of select="@src" />
          </xsl:attribute>
        </img>
        <p class="alt"><xsl:value-of select="@alt"/></p>
      </div>
    </xsl:template>

    <xsl:template match="numeracja">
      <div>
        <xsl:call-template name="standard-attributes" />
        <div>
          <xsl:attribute name="data-start">
            <xsl:value-of select="@start" />
          </xsl:attribute>
          <xsl:attribute name="data-link">
            <xsl:value-of select="@link" />
          </xsl:attribute>
        </div>
      </div>
    </xsl:template>

    <!--
        ********
        STROFA
        ********
    -->
    <xsl:template match="strofa">
        <div x-editable="true">
            <xsl:call-template name="standard-attributes" />
         
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

        <!-- THIS IS A HORROR!!! -->
        <!-- Possible variants: -->
        <xsl:choose>
            <!-- Simple verse == not wers_ tags anywhere until the ending br -->
            <xsl:when test="not($verse-content[starts-with(name(), 'wers')])">
                <div class="wers" x-node="wers" x-verse="true" x-auto-node="true">
                <xsl:apply-templates select="$verse-content[local-name(.) != 'br']">
                    <xsl:with-param name="mixed" select="true()" />
                </xsl:apply-templates>
                </div>
            </xsl:when>

            <xsl:otherwise>
            <xsl:apply-templates select="$verse-content[local-name(.) != 'br']">
                <xsl:with-param name="mixed" select="false()" />
            </xsl:apply-templates>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    {% if tags.verse %}
    <xsl:template match="{{ tags.verse|join:"|" }}">
        <xsl:param name="mixed" />
        	<div x-verse="true">
            	<xsl:call-template name="standard-attributes" />
            	<xsl:apply-templates select="child::node()">
                	<xsl:with-param name="mixed" select="true()" />
            	</xsl:apply-templates>
	        </div>
    </xsl:template>
    {% endif %}

    <xsl:template match="br"><xsl:text>/</xsl:text></xsl:template>

    {% if tags.span %}
    <!-- Style znakowe         span -->
    <xsl:template match="{{ tags.span|join:"|" }}">
        <xsl:param name="mixed" />
        <em>
            <xsl:call-template name="standard-attributes" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </em>
    </xsl:template>
    {% endif %}

    {% if tags.sep %}
    <!-- Separatory            sep -->
    <xsl:template match="{{ tags.sep|join:"|" }}">
        <xsl:param name="mixed" />
        <hr><xsl:call-template name="standard-attributes" /></hr>
    </xsl:template>
    {% endif %}

    {% if tags.aside %}
    <!-- Przypisy i motywy     aside -->
    <xsl:template match="{{ tags.aside|join:"|" }}">
        <span x-editable="true">
            <xsl:call-template name="standard-attributes">
                <xsl:with-param name="extra-class" select="'annotation-inline-box'" />
            </xsl:call-template>
            <a name="anchor-{generate-id(.)}" />
            <!-- the link to the non-inline version -->
            <a href="#annotation-{generate-id(.)}" class="annotation"></a>
            <!-- inline contents -->
            <span x-annotation-box="true" x-pass-thru="true">
                <xsl:apply-templates select="node()">
                    <xsl:with-param name="mixed" select="true()" />
                </xsl:apply-templates>
            </span>
        </span>
    </xsl:template>
    {% endif %}

    <xsl:template match="ref">
      <span x-editable="true" x-edit-no-format="true" x-edit-attribute="href">
        <xsl:call-template name="standard-attributes">
          <xsl:with-param name="extra-class" select="'reference-inline-box'" />
        </xsl:call-template>
        <a class="reference">📌</a>
        <span x-preview="true" x-pass-thru="true">
	  <a target="wiki" title="?">
	    <xsl:attribute name="href">
	      <xsl:value-of select="@href" />
	    </xsl:attribute>
	    <xsl:value-of select="@href" />
	  </a>
        </span>
      </span>
    </xsl:template>
    
    <xsl:template match="begin">        
        <span>
            <xsl:call-template name="standard-attributes" />
            <xsl:attribute name="theme-class">
                <xsl:value-of select="substring-after(@id, 'b')" />
            </xsl:attribute>
        </span>
    </xsl:template>

    <xsl:template match="motyw">
        <span x-editable="true" x-edit-no-format="true">
            <xsl:call-template name="standard-attributes" />
            <xsl:attribute name="theme-class">
                <xsl:value-of select="substring-after(@id, 'm')" />
            </xsl:attribute>
            <span x-pass-thru="true" class="theme-text-list"><xsl:value-of select=".|node()" /></span>
        </span>
    </xsl:template>

    <xsl:template match="end">
        <span>
            <xsl:call-template name="standard-attributes" />
            <xsl:attribute name="theme-class">
                <xsl:value-of select="substring-after(@id, 'e')" />
            </xsl:attribute>
        </span>
    </xsl:template>


    <!-- Tekst -->
    <xsl:template match="text()">
      <!-- <xsl:value-of select="." /> -->
      <xsl:param name="mixed" />
      <xsl:choose>
        <xsl:when test="normalize-space(.) = ''">
          <xsl:value-of select="." />
        </xsl:when>
        <xsl:when test="not($mixed)">
          <span x-node="out-of-flow-text" class="out-of-flow-text" x-editable="true">
            <xsl:value-of select="." />
	  </span>
	</xsl:when>
        <xsl:otherwise><xsl:value-of select="." /></xsl:otherwise>
      </xsl:choose>
    </xsl:template>

    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="." /></xsl:comment>
    </xsl:template>

    <xsl:template match="*[name() != local-name()]">
        <span>
            <xsl:call-template name="standard-attributes" />
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>
        </span>
    </xsl:template>
	
    <xsl:template match="*">
        <span>
            <xsl:call-template name="standard-attributes">
                <xsl:with-param name="extra-class">unknown-tag</xsl:with-param>
            </xsl:call-template>
            <xsl:apply-templates select="child::node()">
                <xsl:with-param name="mixed" select="true()" />
            </xsl:apply-templates>        
        </span>
    </xsl:template>

    <xsl:template name="standard-attributes">
        <xsl:param name="extra-class" />
        <xsl:attribute name="class"><xsl:value-of select="$extra-class" /></xsl:attribute>

        <xsl:attribute name="x-node"><xsl:value-of select="local-name()" /></xsl:attribute>

        <xsl:if test="local-name() != name()">
            <xsl:attribute name="x-ns"><xsl:value-of select="namespace-uri()" /></xsl:attribute>
        </xsl:if>

        <xsl:for-each select="@*">

          <xsl:choose>
            {% for namespace, prefix in namespaces.items %}
            <xsl:when test="namespace-uri() =  '{{ namespace }}'">
              <xsl:attribute name="x-a-{{ prefix }}-{local-name()}">
                <xsl:value-of select="."/>
              </xsl:attribute>
            </xsl:when>
            {% endfor %}

            <xsl:otherwise>
              <xsl:variable name="id" select="generate-id()" />
              <xsl:attribute name="x-attr-value-{$id}"><xsl:value-of select="."/></xsl:attribute>
              <xsl:attribute name="x-attr-name-{$id}"><xsl:value-of select="local-name()"/></xsl:attribute>
              <xsl:attribute name="x-attr-ns-{$id}"><xsl:value-of select="namespace-uri()"/></xsl:attribute>
	    </xsl:otherwise>
	  </xsl:choose>               

        </xsl:for-each>
    </xsl:template>

    <xsl:template match="alien">
            <span class="alien" x-pass-thru="true">
                <xsl:apply-templates select="node()">
                    <xsl:with-param name="mixed" select="true()" />
                </xsl:apply-templates>
            </span>
    </xsl:template>

    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>
</xsl:stylesheet>
