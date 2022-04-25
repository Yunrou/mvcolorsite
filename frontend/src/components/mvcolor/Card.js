import React, { Component, Fragment, PureComponent } from 'react';

export default class Card extends PureComponent {

    render() {
        const spec = JSON.parse(this.props.spec);
        var opt = {
            actions: false,
            config : {
                "background": null,
                "style": {
                    "guide-label": {"fill": this.props.textcolor}, 
                    "guide-title": {"fill": this.props.textcolor}
                },
                "view": {"stroke": null},
                "axis": {
                  "grid": false,
                  "gridDash": [5,2],
                  "ticks": false,
                  "domain": false,
                  "labelPadding": 5,
                  "labelFontSize": 12,
                  "labelLimit": 80,
                  "titleFontWeight": "normal",
                  "titleFontSize": 12
                },
                "title": {
                  "FontWeight": "normal",
                  "subtitleFontWeight": "normal",
                  "color": this.props.textcolor
                },
                "legend": {
                  // "titleFontWeight": "normal",
                  "orient": "top",
                  "direction": "horizontal",
                  "symbolType": "circle",
                  "symbolStrokeWidth": 2,
                  "symbolSize": 60,
                  "offset": 10,
                  "labelLimit": 120,
                  "columnPadding": 5,
                  "columns": 5,
                  "gridAlign": "each",
                  "labelFontSize": 12,
                  "titlePadding": 2,
                  "titleFontSize": 12,
                  "titleFontWeight": "normal"
                },
                "header": {
                  "titleFontWeight": "normal"
                },
                "mark": {
                  "strokeWidth": 2.8
                }
                // "axisX": {"labelAngle": -30, "labelOverlap": false}
            },
                
            loader: { http: { credentials: 'same-origin' }}
        }
        vegaEmbed('#chart_'+this.props.pk, spec, opt);
        return (
            <Fragment>
            </Fragment>
        )
    }
}