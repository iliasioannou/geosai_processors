<?xml version="1.0" ?>
<sld:StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <sld:UserLayer>
        <sld:LayerFeatureConstraints>
            <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
            <sld:Name>TEM</sld:Name>
            <sld:Title/>
            <sld:FeatureTypeStyle>
                <sld:Name/>
                <sld:Rule>
                    <sld:RasterSymbolizer>
                        <sld:Geometry>
                            <ogc:PropertyName>grid</ogc:PropertyName>
                        </sld:Geometry>
                        <sld:Opacity>1</sld:Opacity>
                        <sld:ColorMap>
                            <sld:ColorMapEntry color="#2b48ba" label="10" opacity="1.0" quantity="10"/>
                            <sld:ColorMapEntry color="#3666a5" label="11.2" opacity="1.0" quantity="11.2"/>
                            <sld:ColorMapEntry color="#418490" label="12.5" opacity="1.0" quantity="12.5"/>
                            <sld:ColorMapEntry color="#4ca27a" label="13.8" opacity="1.0" quantity="13.8"/>
                            <sld:ColorMapEntry color="#57bf65" label="15" opacity="1.0" quantity="15"/>
                            <sld:ColorMapEntry color="#62dd50" label="16.2" opacity="1.0" quantity="16.2"/>
                            <sld:ColorMapEntry color="#82e454" label="17.5" opacity="1.0" quantity="17.5"/>
                            <sld:ColorMapEntry color="#a1eb58" label="18.8" opacity="1.0" quantity="18.8"/>
                            <sld:ColorMapEntry color="#c1f25d" label="20" opacity="1.0" quantity="20"/>
                            <sld:ColorMapEntry color="#e0f961" label="21.2" opacity="1.0" quantity="21.2"/>
                            <sld:ColorMapEntry color="#ffff66" label="22.5" opacity="1.0" quantity="22.5"/>
                            <sld:ColorMapEntry color="#ffeb5e" label="23.8" opacity="1.0" quantity="23.8"/>
                            <sld:ColorMapEntry color="#ffd756" label="25" opacity="1.0" quantity="25"/>
                            <sld:ColorMapEntry color="#fec34e" label="26.2" opacity="1.0" quantity="26.2"/>
                            <sld:ColorMapEntry color="#feae45" label="27.5" opacity="1.0" quantity="27.5"/>
                            <sld:ColorMapEntry color="#fd9a3d" label="28.8" opacity="1.0" quantity="28.8"/>
                            <sld:ColorMapEntry color="#e97f35" label="30" opacity="1.0" quantity="30"/>
                            <sld:ColorMapEntry color="#d5632c" label="31.2" opacity="1.0" quantity="31.2"/>
                            <sld:ColorMapEntry color="#c04824" label="32.5" opacity="1.0" quantity="32.5"/>
                            <sld:ColorMapEntry color="#ac2c1b" label="33.8" opacity="1.0" quantity="33.8"/>
                            <sld:ColorMapEntry color="#971113" label="35" opacity="1.0" quantity="35"/>
                            <sld:ColorMapEntry color="#79211c" label="40" opacity="1.0" quantity="40"/>
                            <sld:ColorMapEntry color="#602b00" label="Land" opacity="1.0" quantity="998"/>
                            <sld:ColorMapEntry color="#000000" label="Nodata" opacity="1.0" quantity="999"/>
                        </sld:ColorMap>
                    </sld:RasterSymbolizer>
                </sld:Rule>
            </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </sld:UserLayer>
</sld:StyledLayerDescriptor>
