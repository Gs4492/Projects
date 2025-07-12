// window.addEventListener("DOMContentLoaded", () => {
//     const revenueChartEl = document.getElementById("revenueChart");
//     if (revenueChartEl) {
//         fetch('http://localhost:8000/invoices/revenue')
//             .then(res => res.json())
//             .then(data => {
//                 let chart = echarts.init(revenueChartEl);
//                 chart.setOption({
//                     title: { text: 'Total Revenue' },
//                     tooltip: {},
//                     xAxis: {
//                         type: 'category',
//                         data: ['Revenue']  // X label
//                     },
//                     yAxis: {
//                         type: 'value'
//                     },
//                     series: [{
//                         type: 'bar',
//                         data: [data.total_revenue]
//                     }]
//                 });

//             });
//     }

//     const stockChartEl = document.getElementById("plantStockChart");
//     if (stockChartEl) {
//         fetch('http://localhost:8000/plants')
//             .then(res => res.json())
//             .then(plants => {
//                 const categories = {};
//                 plants.forEach(p => {
//                     categories[p.category] = (categories[p.category] || 0) + p.stock;
//                 });
//                 let chart = echarts.init(stockChartEl);
//                 chart.setOption({
//                     title: { text: 'Plant Stock by Category' },
//                     tooltip: {},
//                     xAxis: { type: 'category', data: Object.keys(categories) },
//                     yAxis: { type: 'value' },
//                     series: [{
//                         data: Object.values(categories),
//                         type: 'bar'
//                     }]
//                 });
//             });
//     }
// });



window.addEventListener("DOMContentLoaded", () => {
  const revenueChartEl = document.getElementById("revenueChart");
  const stockChartEl = document.getElementById("plantStockChart");

  let revenueChart, stockChart;
  let revenueData = [], revenueLabels = [];

  // Initialize Revenue Chart (Live Line)
  if (revenueChartEl) {
    revenueChart = echarts.init(revenueChartEl);
    updateRevenueChart();
    setInterval(updateRevenueChart, 5000);
  }

  function updateRevenueChart() {
    const now = new Date().toLocaleTimeString();
    const fakeValue = Math.floor(Math.random() * 5000 + 1000); // ₹1k–₹6k

    if (revenueData.length >= 10) {
      revenueData.shift();
      revenueLabels.shift();
    }

    revenueData.push(fakeValue);
    revenueLabels.push(now);

    revenueChart.setOption({
      title: { text: 'Live Revenue Trend (₹)' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: revenueLabels },
      yAxis: { type: 'value' },
      series: [{
        data: revenueData,
        type: 'line',
        smooth: true,
        areaStyle: { color: '#d4f5e6' },
        lineStyle: { color: '#54b883' }
      }]
    });
  }

  // Plant Stock Chart (Fake Live Bar)
  if (stockChartEl) {
    stockChart = echarts.init(stockChartEl);
    updateStockChart();
    setInterval(updateStockChart, 5000);
  }

  function updateStockChart() {
    const categories = ['Indoor', 'Outdoor', 'Succulent', 'Herbs'];
    const stockCounts = categories.map(() => Math.floor(Math.random() * 100 + 10));
    stockChart.setOption({
      title: { text: 'Plant Stock by Category (Live)' },
      tooltip: {},
      xAxis: { type: 'category', data: categories },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: stockCounts
      }]
    });
  }

  // Scorecards
  function updateScorecards() {
    document.getElementById("totalRevenue").textContent = "₹ " + (Math.floor(Math.random() * 20000 + 10000));
    document.getElementById("totalPlants").textContent = Math.floor(Math.random() * 200 + 50) + " Plants";
    document.getElementById("totalOrders").textContent = Math.floor(Math.random() * 100 + 20) + " Orders";
    document.getElementById("totalCustomers").textContent = Math.floor(Math.random() * 300 + 80) + " Customers";
  }

  updateScorecards();
  setInterval(updateScorecards, 5000);
});
function animateValue(id, end, duration = 800) {
  const el = document.getElementById(id);
  let start = 0;
  const stepTime = Math.abs(Math.floor(duration / end));
  const timer = setInterval(() => {
    start += 1;
    el.textContent = '₹ ' + start;
    if (start >= end) clearInterval(timer);
  }, stepTime);
}
echarts.registerTheme('plantTheme', {
  color: ['#4CAF50', '#81C784', '#A5D6A7', '#C8E6C9'],
  backgroundColor: '#F0F8F4',
  textStyle: {
    fontFamily: 'Segoe UI',
    color: '#2E7D32'
  },
  title: {
    textStyle: {
      color: '#388E3C'
    }
  }
});
