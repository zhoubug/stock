function updateChart(sym){
    var host = document.location.origin;
    $.getJSON(host+"/_stock/"+sym, function(data){
	var ohlc = [],
            volumes = [],
            dataLength = data.data.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]],

            i = 0;

	var iopen = data.columns.indexOf("open"),
	    iclose = data.columns.indexOf("close"),
	    ihigh = data.columns.indexOf("high"),
	    ilow = data.columns.indexOf("low"),
	    ivolume = data.columns.indexOf("volume");
	
        for (i; i < dataLength; i += 1) {
	    var date = data.index[i],
		open = data.data[i][iopen],
		close = data.data[i][iclose],
		high = data.data[i][ihigh],
		low = data.data[i][ilow],
		volume = data.data[i][ivolume];
            ohlc.push([
                date, // the date
                open, // open
                high,
                low,
                close,
            ]);

            volumes.push([
		date,
		volume
            ]);
        }


        // create the chart
        $('#chart').highcharts('StockChart', {

            rangeSelector: {
                selected: 1
            },

            title: {
                text: 'AAPL Historical'
            },

            yAxis: [{
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'OHLC'
                },
                height: '60%',
                lineWidth: 2
            }, {
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'Volume'
                },
                top: '65%',
                height: '35%',
                offset: 0,
                lineWidth: 2
            }],

            series: [{
                type: 'candlestick',
                name: 'AAPL',
                data: ohlc,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                type: 'column',
                name: 'Volume',
                data: volumes,
		turboThreshold: Number.MAX_VALUE,
                yAxis: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }]
	});
    });
}
