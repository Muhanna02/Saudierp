/** @odoo-module **/

/**
 * Chart utilities for Saudi ERP Dashboard
 * Uses Chart.js (loaded via CDN or bundled)
 */

/**
 * Initialize Revenue Chart (Line)
 */
export function initRevenueChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    // Destroy existing chart if any
    if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');

    // Gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, 'rgba(26, 122, 78, 0.3)');
    gradient.addColorStop(1, 'rgba(26, 122, 78, 0.0)');

    const chart = new window.Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue (SAR)',
                data: data,
                borderColor: '#1a7a4e',
                borderWidth: 2.5,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#1a7a4e',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f1923',
                    titleColor: '#a8b9c8',
                    bodyColor: '#fff',
                    borderColor: '#1a7a4e',
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        label: ctx => `SAR ${ctx.parsed.y.toLocaleString('en-SA', {
                            minimumFractionDigits: 2
                        })}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9aa8b8', font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(232, 236, 241, 0.6)', drawBorder: false },
                    ticks: {
                        color: '#9aa8b8',
                        font: { size: 11 },
                        callback: v => `${(v / 1000).toFixed(0)}K`
                    }
                }
            }
        }
    });

    canvas._chartInstance = chart;
    return chart;
}

/**
 * Initialize Saudization Donut Chart
 */
export function initSaudizationChart(canvasId, saudiCount, expatCount) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    const chart = new window.Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Saudi / سعودي', 'Expat / وافد'],
            datasets: [{
                data: [saudiCount, expatCount],
                backgroundColor: ['#1a7a4e', '#e8ecf1'],
                borderWidth: 0,
                hoverBackgroundColor: ['#22a362', '#d0d7e0'],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#6b7a8d',
                        font: { size: 11 },
                        padding: 12,
                        boxWidth: 10,
                        borderRadius: 3,
                    }
                },
                tooltip: {
                    backgroundColor: '#0f1923',
                    titleColor: '#a8b9c8',
                    bodyColor: '#fff',
                }
            }
        }
    });

    canvas._chartInstance = chart;
    return chart;
}

/**
 * Initialize VAT vs Revenue Bar Chart
 */
export function initVatRevenueChart(canvasId, labels, revenue, vat) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    const chart = new window.Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Revenue (SAR)',
                    data: revenue,
                    backgroundColor: 'rgba(26, 122, 78, 0.8)',
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'VAT Collected (SAR)',
                    data: vat,
                    backgroundColor: 'rgba(201, 168, 76, 0.8)',
                    borderRadius: 6,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#6b7a8d',
                        font: { size: 11 },
                        padding: 12,
                        boxWidth: 10,
                        borderRadius: 3,
                    }
                },
                tooltip: {
                    backgroundColor: '#0f1923',
                    titleColor: '#a8b9c8',
                    bodyColor: '#fff',
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9aa8b8', font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(232, 236, 241, 0.6)' },
                    ticks: {
                        color: '#9aa8b8',
                        font: { size: 11 },
                        callback: v => `${(v / 1000).toFixed(0)}K`
                    }
                }
            }
        }
    });

    canvas._chartInstance = chart;
    return chart;
}
