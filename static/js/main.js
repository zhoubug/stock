var HOST = document.location.origin;

function updateChart(sym){
    $.getJSON(HOST+"/_stock/"+sym, function(data){
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
                text: sym
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
                name: sym,
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

function compare(data){
    var seriesOptions = [],
        // create the chart when all data is loaded
        createChart = function () {
            $('#chart').highcharts('StockChart', {

                rangeSelector: {
                    selected: 4
                },

                yAxis: {
                    labels: {
                        formatter: function () {
                            return (this.value > 0 ? ' + ' : '') + this.value + '%';
                        }
                    },
                    plotLines: [{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }]
                },

                plotOptions: {
                    series: {
                        compare: 'percent'
                    }
                },

                tooltip: {
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
                    valueDecimals: 2
                },

                series: seriesOptions
            });
        };

    var i = 0;

    for(var key in data){
	var rawdata = JSON.parse(data[key]);
	var closes = [];
	var index = rawdata.index,
	    close = rawdata.data;
	for(var j=0; j<rawdata.index.length; j++){
	    closes.push([index[j], close[j]]);
	}

	seriesOptions[i] = {
            name: key,
            data: closes
	};
	i++;
    }
    createChart();
}
