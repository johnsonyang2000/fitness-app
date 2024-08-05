document.addEventListener('DOMContentLoaded', function () {
    const chartData = document.getElementById('chartData');
    const dates = chartData.dataset.dates.split(', ');
    const weights = chartData.dataset.weights.split(', ').map(Number);
    const bmis = chartData.dataset.bmis.split(', ').map(Number);
    const bmrs = chartData.dataset.bmrs.split(', ').map(Number);

    const weightCtx = document.getElementById('weightChart').getContext('2d');
    const bmiCtx = document.getElementById('bmiChart').getContext('2d');
    const bmrCtx = document.getElementById('bmrChart').getContext('2d');

    new Chart(weightCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Weight (kg)',
                data: weights,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Weight (kg)'
                    }
                }
            }
        }
    });

    new Chart(bmiCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'BMI',
                data: bmis,
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'BMI'
                    }
                }
            }
        }
    });

    new Chart(bmrCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'BMR',
                data: bmrs,
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'BMR'
                    }
                }
            }
        }
    });
});
