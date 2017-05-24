<?xml version="1.0" ?>
<sld:StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <sld:UserLayer>
        <sld:LayerFeatureConstraints>
            <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
            <sld:Name>WT</sld:Name>
            <sld:Title/>
            <sld:FeatureTypeStyle>
                <sld:Name/>
                <sld:Rule>
                    <sld:RasterSymbolizer>
                        <sld:Opacity>1</sld:Opacity>
                        <sld:ColorMap type="intervals">
                            <sld:ColorMapEntry color="#000000" label="" opacity="0.0" quantity="-11.1"/>
                            <sld:ColorMapEntry color="#000000" label="NODATA" opacity="1.0" quantity="-10.1"/>
                          	<sld:ColorMapEntry color="#aa3300" label="Land" opacity="0.0" quantity="-9.9"/>
                            <sld:ColorMapEntry color="#000096" label="-" opacity="1.0" quantity="0.01"/>
                            <sld:ColorMapEntry color="#000096" label="-" opacity="1.0" quantity="8"/>
                            <sld:ColorMapEntry color="#0000c8" label="-" opacity="1.0" quantity="16"/>
                            <sld:ColorMapEntry color="#0064ff" label="-" opacity="1.0" quantity="24"/>
                            <sld:ColorMapEntry color="#0096ff" label="-" opacity="1.0" quantity="32"/>
                            <sld:ColorMapEntry color="#32c8ff" label="-" opacity="1.0" quantity="40"/>
                            <sld:ColorMapEntry color="#82faff" label="-" opacity="1.0" quantity="48"/>
                            <sld:ColorMapEntry color="#96faff" label="-" opacity="1.0" quantity="56"/>
                            <sld:ColorMapEntry color="#befeff" label="-" opacity="1.0" quantity="64"/>
                            <sld:ColorMapEntry color="#d2fffe" label="-" opacity="1.0" quantity="72"/>
                            <sld:ColorMapEntry color="#ebfffe" label="-" opacity="1.0" quantity="100"/>
                        </sld:ColorMap>
                    </sld:RasterSymbolizer>
                </sld:Rule>
            </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </sld:UserLayer>
</sld:StyledLayerDescriptor>
