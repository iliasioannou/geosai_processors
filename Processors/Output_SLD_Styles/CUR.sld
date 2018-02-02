<?xml version="1.0" ?>
<sld:StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <sld:UserLayer>
        <sld:LayerFeatureConstraints>
            <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
            <sld:Name>CUR</sld:Name>
            <sld:Title/>
            <sld:FeatureTypeStyle>
                <sld:Name/>
                <Transformation>
                    <ogc:Function name="gs:RasterAsPointCollection">
                        <ogc:Function name="parameter">
                            <ogc:Literal>data</ogc:Literal>
                        </ogc:Function>
                    </ogc:Function>
                </Transformation>
                <sld:Rule>
                    <sld:RasterSymbolizer>
                        <sld:Geometry>
                            <ogc:PropertyName>grid</ogc:PropertyName>
                        </sld:Geometry>
                        <sld:Opacity>1</sld:Opacity>
                        <sld:ColorMap type="intervals">
                            <sld:ColorMapEntry color="#FDF8DD" label="0.00" opacity="1.0" quantity="0.00"/>
                            <sld:ColorMapEntry color="#F9E6C7" label="0.00" opacity="1.0" quantity="0.00"/>
                            <sld:ColorMapEntry color="#F5D5B1" label="0.10" opacity="1.0" quantity="0.10"/>
                            <sld:ColorMapEntry color="#F2C49B" label="0.15" opacity="1.0" quantity="0.15"/>
                            <sld:ColorMapEntry color="#EEB285" label="0.20" opacity="1.0" quantity="0.20"/>
                            <sld:ColorMapEntry color="#EAA16F" label="0.25" opacity="1.0" quantity="0.25"/>
                            <sld:ColorMapEntry color="#E79059" label="0.30" opacity="1.0" quantity="0.30"/>
                            <sld:ColorMapEntry color="#E37E43" label="0.35" opacity="1.0" quantity="0.35"/>
                            <sld:ColorMapEntry color="#E27B3F" label="0.40" opacity="1.0" quantity="0.40"/>
                            <sld:ColorMapEntry color="#DF6B2B" label="0.45" opacity="1.0" quantity="0.45"/>
                            <sld:ColorMapEntry color="#DC5C18" label="0.50" opacity="1.0" quantity="0.50"/>
                            <sld:ColorMapEntry color="#602b00" label="Land" opacity="0.0" quantity="998.1"/>
                            <sld:ColorMapEntry color="#000000" label="Nodata" opacity="1.0" quantity="998.9"/>
                            <sld:ColorMapEntry color="#000000" label="" opacity="1.0" quantity="999.1"/>
                        </sld:ColorMap>
                    </sld:RasterSymbolizer>
                </sld:Rule>
                <sld:Rule>
                    <sld:Filter>
                        <sld:And>
                            <sld:PropertyIsGreaterThanOrEqualTo>
                                <sld:PropertyName>GRAY_INDEX</sld:PropertyName>
                                <sld:Literal>0</sld:Literal>
                            </sld:PropertyIsGreaterThanOrEqualTo>
                            <sld:PropertyIsLessThanOrEqualTo>
                                <sld:PropertyName>GRAY_INDEX</sld:PropertyName>
                                <sld:Literal>0.5</sld:Literal>
                            </sld:PropertyIsLessThanOrEqualTo>
                        </sld:And>
                    </sld:Filter>
                    <sld:PointSymbolizer>
                        <sld:Graphic>
                            <sld:Mark>
                                <sld:WellKnownName>extshape://arrow</sld:WellKnownName>
                                <sld:Stroke>
                                    <sld:CssParameter name="stroke">#000000</sld:CssParameter>
                                    <sld:CssParameter name="stroke-width">0.8</sld:CssParameter>
                                </sld:Stroke>
                                <sld:Fill>
                                   <sld:CssParameter name="fill">#000000</sld:CssParameter>
                                </sld:Fill>
                            </sld:Mark>
                            <sld:Size>8</sld:Size>
                            <sld:Rotation>
                                <ogc:Function name="if_then_else">
                                    <ogc:Function name="greaterThan">
                                        <ogc:PropertyName>Band2</ogc:PropertyName>
                                        <ogc:Literal>180</ogc:Literal>
                                    </ogc:Function>
                                    <ogc:Sub>
                                        <ogc:PropertyName>Band2</ogc:PropertyName>
                                        <ogc:Literal>180</ogc:Literal>
                                    </ogc:Sub>
                                    <ogc:Add>
                                        <ogc:PropertyName>Band2</ogc:PropertyName>
                                        <ogc:Literal>180</ogc:Literal>
                                    </ogc:Add>
                                </ogc:Function>
                            </sld:Rotation>
                        </sld:Graphic>
                    </sld:PointSymbolizer>
                </sld:Rule>
            </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </sld:UserLayer>
</sld:StyledLayerDescriptor>