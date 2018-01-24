<?xml version="1.0" ?>
<sld:StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <sld:UserLayer>
        <sld:LayerFeatureConstraints>
            <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
            <sld:Name>SWH</sld:Name>
            <sld:Title/>
            <sld:FeatureTypeStyle>
                <sld:Name/>
                <sld:Rule>
                    <sld:RasterSymbolizer>
                        <sld:Geometry>
                            <ogc:PropertyName>grid</ogc:PropertyName>
                        </sld:Geometry>
                        <sld:Opacity>1</sld:Opacity>
                        <sld:ColorMap type="intervals">
                            <sld:ColorMapEntry color="#2b2bba" label="0" opacity="1.0" quantity="0"/>
                            <sld:ColorMapEntry color="#3b4eaa" label="0.375" opacity="1.0" quantity="0.375"/>
                            <sld:ColorMapEntry color="#4a729a" label="0.75" opacity="1.0" quantity="0.75"/>
                            <sld:ColorMapEntry color="#5a968a" label="1.12" opacity="1.0" quantity="1.12"/>
                            <sld:ColorMapEntry color="#6aba7a" label="1.5" opacity="1.0" quantity="1.5"/>
                            <sld:ColorMapEntry color="#7add6b" label="1.88" opacity="1.0" quantity="1.88"/>
                            <sld:ColorMapEntry color="#95e461" label="2.25" opacity="1.0" quantity="2.25"/>
                            <sld:ColorMapEntry color="#afeb57" label="2.62" opacity="1.0" quantity="2.62"/>
                            <sld:ColorMapEntry color="#caf24d" label="3" opacity="1.0" quantity="3"/>
                            <sld:ColorMapEntry color="#e5f943" label="3.38" opacity="1.0" quantity="3.38"/>
                            <sld:ColorMapEntry color="#ffff39" label="3.75" opacity="1.0" quantity="3.75"/>
                            <sld:ColorMapEntry color="#ffef39" label="4.12" opacity="1.0" quantity="4.12"/>
                            <sld:ColorMapEntry color="#ffdf38" label="4.5" opacity="1.0" quantity="4.5"/>
                            <sld:ColorMapEntry color="#fecf38" label="4.88" opacity="1.0" quantity="4.88"/>
                            <sld:ColorMapEntry color="#febe38" label="5.25" opacity="1.0" quantity="5.25"/>
                            <sld:ColorMapEntry color="#fdae38" label="5.62" opacity="1.0" quantity="5.62"/>
                            <sld:ColorMapEntry color="#e28e30" label="6" opacity="1.0" quantity="6"/>
                            <sld:ColorMapEntry color="#c76e27" label="6.38" opacity="1.0" quantity="6.38"/>
                            <sld:ColorMapEntry color="#ac4d1f" label="6.75" opacity="1.0" quantity="6.75"/>
                            <sld:ColorMapEntry color="#912d17" label="7.12" opacity="1.0" quantity="7.12"/>
                            <sld:ColorMapEntry color="#760d0f" label="7.5" opacity="1.0" quantity="7.5"/>
                            <sld:ColorMapEntry color="#3c0d10" label="10" opacity="1.0" quantity="10"/>
                            <sld:ColorMapEntry color="#602b00" label="Land" opacity="1.0" quantity="998"/>
                            <sld:ColorMapEntry color="#000000" label="Nodata" opacity="1.0" quantity="999"/>
                        </sld:ColorMap>
                    </sld:RasterSymbolizer>
                </sld:Rule>
            </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </sld:UserLayer>
</sld:StyledLayerDescriptor>
