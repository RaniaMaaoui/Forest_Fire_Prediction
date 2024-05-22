var ctxTemp = document.getElementById('temperatureChart').getContext('2d');
var temperatureChart = new Chart(ctxTemp, {
    type: 'line',
    data: {
    labels: ['0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h', '20h', '21h', '22h', '23h'],
    datasets: [{
        label: 'Daily Temperatures',
        data: [25, 25, 27, 27, 28, 30, 28, 28, 27, 29, 30, 27, 28, 30, 28, 26, 24, 22, 20, 18, 18, 18, 17, 18],
        backgroundColor: 'rgba(0, 123, 255, 0.2)',
        borderColor: 'rgba(0, 123, 255, 1)',
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
            text: 'Temperature (°C)'
        },
        suggestedMin: 5,
        suggestedMax: 45
        }
    },
    plugins: {
        legend: {
        display: true,
        position: 'top',
        },
        title: {
        display: true,
        text: 'Daily Temperatures'
        },
        tooltip: {
        callbacks: {
            label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            if (context.parsed.y !== null) {
                label += context.parsed.y + '°C';
            }
            return label;
            }
        }
        }
    }
    }
});
