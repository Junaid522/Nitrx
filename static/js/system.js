function AhsanJs() {
    $(".drop-down1 .selected1 a").click(function () {
        $(".drop-down1 .options1 ul").toggle();
    });
    $(".drop-down1 .options1 ul li a").click(function () {
        var text = $(this).html();
        $(".drop-down1 .selected1 a span").html(text);
        $(".drop-down1 .options1 ul").hide();
    });
    $(document).bind('click', function (e) {
        var $clicked = $(e.target);
        if (!$clicked.parents().hasClass("drop-down1"))
            $(".drop-down1 .options1 ul").hide();
    });

    $(".drop-down2 .selected2 a").click(function () {
        $(".drop-down2 .options2 ul").toggle();
    });
    $(".drop-down2 .options2 ul li a").click(function () {
        var text = $(this).html();
        $(".drop-down2 .selected2 a span").html(text);
        $(".drop-down2 .options2 ul").hide();
    });
    $(document).bind('click', function (e) {
        var $clicked = $(e.target);
        if (!$clicked.parents().hasClass("drop-down2"))
            $(".drop-down2 .options2 ul").hide();
    });

    $(".drop-down3 .selected3 a").click(function () {
        $(".drop-down3 .options3 ul").toggle();
    });
    $(".drop-down3 .options3 ul li a").click(function () {
        var text = $(this).html();
        $(".drop-down3 .selected3 a span").html(text);
        $(".drop-down3 .options3 ul").hide();
    });
    $(document).bind('click', function (e) {
        var $clicked = $(e.target);
        if (!$clicked.parents().hasClass("drop-down3"))
            $(".drop-down3 .options3 ul").hide();
    });

}


jQuery(document).ready(function () {
    AhsanJs();

    Highcharts.chart('graph1', {
        chart: {
            type: 'spline',
        },

        title: {
            text: ''
        },

        subtitle: {
            text: ''
        },

        yAxis: {
            title: {
                text: ''
            }
        },

        xAxis: {
            accessibility: {
                rangeDescription: 'Range: 2010 to 2017'
            }
        },

        plotOptions: {
            series: {
                events: {
                    legendItemClick: function () {
                        var name = this.name.substring(this.name.length - 4, this.name.length);
                        var _i = this._i;
                        Highcharts.each(this.chart.series, function (p, i) {
                            if (name === p.name.substring(p.name.length - 4, p.name.length) && _i !== p._i) {
                                (!p.visible) ? p.show() : p.hide()
                            }
                        })
                    }
                }
            }
        },

        series: [
            {
                name: '1',
                data: [43934, 97031, 154175, 43934,]
            },
            {
                name: '2',
                data: [24916, 29851, 40434, 119931,]
            },
            {
                name: '3',
                data: [29742, 29851, 38121, 40434, 154175,]
            },
            {
                name: '4',
                data: [52503, 97031, 119931, 137133, 154175]
            }
        ],

        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        },
    })
    // function (chart) {
    //     debugger
    //     $legend = $('#id_legends');
    //
    //     $.each(chart.series[0].data, function (j, data) {
    //
    //         $legend.append('<div class="item"><div class="symbol" style="background-color:' + data.color + '"></div><div class="serieName" id="">' + data.name + '</div></div>');
    //
    //     });
    //
    //     $('#id_legends .item').click(function () {
    //         var inx = $(this).index(),
    //             point = chart.series[0].data[inx];
    //
    //         if (point.visible)
    //             point.setVisible(false);
    //         else
    //             point.setVisible(true);
    //     });
    // }
});