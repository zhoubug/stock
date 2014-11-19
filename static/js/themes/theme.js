/**
 * Dark blue theme for Highcharts JS
 * @author Torstein Honsi
 */
var originalDrawPoints = Highcharts.seriesTypes.column.prototype.drawPoints;

Highcharts.seriesTypes.column.prototype.drawPoints = function () {
    if (this == this.chart.series[1]) {
        var merge  = Highcharts.merge,
            series = this,
            chart  = this.chart,
            points = series.points,
            i      = points.length;
        
        while (i--) {
            var candlePoint = chart.series[0].points[i];
            var color = (candlePoint.open < candlePoint.close) ? 'red' : 'green';
            var seriesPointAttr = merge(series.pointAttr);
            
            seriesPointAttr[''].fill = color;
            seriesPointAttr.hover.fill = Highcharts.Color(color).brighten(0.3).get();
            seriesPointAttr.select.fill = color;
            
            points[i].pointAttr = seriesPointAttr;
        }
    }

    originalDrawPoints.call(this);
}

Highcharts.theme = {
    plotOptions: {
	line: {
	    dataLabels: {
		color: '#CCC'
	    },
	    marker: {
		lineColor: '#333'
	    }
	},
	spline: {
	    marker: {
		lineColor: '#333'
	    }
	},
	scatter: {
	    marker: {
		lineColor: '#333'
	    }
	},
	candlestick: {
	    lineColor: 'green',
	    upLineColor: 'red',
	    color: 'green',
	    upColor: 'red'
	}
    }
};

// Apply the theme
var highchartsOptions = Highcharts.setOptions(Highcharts.theme);
