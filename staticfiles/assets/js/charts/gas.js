var ctxGas = document.getElementById('gasChart').getContext('2d');
var gasChart = new Chart(ctxGas, {
    type: 'line',
    data: {
    labels: ['0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h', '20h', '21h', '22h', '23h'],
    datasets: [{
        label: 'Gas Concentration (ppm)',
        data: [5, 10, 15, 10, 12, 15, 17, 20, 22, 24, 25, 27, 29, 30, 28, 26, 24, 22, 20, 18, 15, 12, 10, 8],
        backgroundColor: 'rgba(255, 159, 64, 0.2)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
        fill: true,  // Enable fill
        tension: 0.1
    }]
    },
    options: {
    scales: {
        x: {
        title: {
            display: true,
            text: 'Hours'
        }
        },
        y: {
        title: {
            display: true,
            text: 'Gas Concentration (ppm)'
        },
        suggestedMin: 0,
        suggestedMax: 35
        }
    },
    plugins: {
        legend: {
        display: true,
        position: 'top',
        },
        title: {
        display: true,
        text: 'Daily Gas Concentration'
        },
        tooltip: {
        callbacks: {
            label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            if (context.parsed.y !== null) {
                label += context.parsed.y + ' ppm';
            }
            return label;
            }
        }
        }
    }
    }
});