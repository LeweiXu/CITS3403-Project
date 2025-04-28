document.addEventListener('DOMContentLoaded', function () {
    const rankingSelect = document.getElementById('ranking-select');
    const graphSelect = document.getElementById('graph-select');
    const graphCanvas = document.getElementById('graph-canvas');

    // Handle ranking selection
    rankingSelect.addEventListener('change', function () {
        const selectedRanking = rankingSelect.value;
        console.log(`Selected ranking: ${selectedRanking}`);
        // Add logic to update ranking view dynamically
    });

    // Handle graph selection
    graphSelect.addEventListener('change', function () {
        const selectedGraph = graphSelect.value;
        console.log(`Selected graph: ${selectedGraph}`);
        // Add logic to update graph dynamically
    });

    // Example: Initialize a chart (if using Chart.js)
    if (graphCanvas) {
        const ctx = graphCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                datasets: [{
                    label: 'Hours Spent',
                    data: [2, 3, 4, 5, 6, 7, 8],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});