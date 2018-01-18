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
                <sld:Rule>
                    <sld:RasterSymbolizer>
                        <sld:Geometry>
                            <ogc:PropertyName>grid</ogc:PropertyName>
                        </sld:Geometry>
                        <sld:Opacity>1</sld:Opacity>
                        <sld:ColorMap>
                            <sld:ColorMapEntry color="#ca0020" label="1.018" opacity="1.0" quantity="1.018"/>
                            <sld:ColorMapEntry color="#d01128" label="1.25" opacity="1.0" quantity="1.25"/>
                            <sld:ColorMapEntry color="#d52330" label="1.50" opacity="1.0" quantity="1.50"/>
                            <sld:ColorMapEntry color="#da3438" label="2.50" opacity="1.0" quantity="2.50"/>
                            <sld:ColorMapEntry color="#df4640" label="3.00" opacity="1.0" quantity="3.00"/>
                            <sld:ColorMapEntry color="#e45849" label="3.16" opacity="1.0" quantity="3.16"/>
                            <sld:ColorMapEntry color="#602b00" label="Land" opacity="1.0" quantity="998"/>
                            <sld:ColorMapEntry color="#000000" label="Nodata" opacity="1.0" quantity="999"/>
                        </sld:ColorMap>
                    </sld:RasterSymbolizer>
                </sld:Rule>
            </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </sld:UserLayer>
</sld:StyledLayerDescriptor>
