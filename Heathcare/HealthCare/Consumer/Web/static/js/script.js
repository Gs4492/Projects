// // static/js/script.js

// // Reset forms after successful submission
// document.addEventListener('submit', function (e) {
//     const form = e.target;
//     setTimeout(() => {
//         form.reset();
//     }, 100);
// });

// // Confirm deletion
// document.querySelectorAll('a[href*="delete"]').forEach(link => {
//     link.addEventListener('click', function (e) {
//         if (!confirm('Are you sure you want to delete this item?')) {
//             e.preventDefault();
//         }
//     });
// });

// // ✅ Declare charts globally so both DOMContentLoaded and fetch can access them
// let appointmentChart, invoiceChart, appointmentsTrendChart, invoicesTrendChart;


// // DOM Ready
// document.addEventListener("DOMContentLoaded", function () {
//     // Initialize ECharts
//     appointmentChart = echarts.init(document.getElementById('appointmentsChart'));
//     invoiceChart = echarts.init(document.getElementById('invoicesChart'));
//     appointmentsTrendChart = echarts.init(document.getElementById('appointmentsTrendChart'));
//     invoicesTrendChart = echarts.init(document.getElementById('invoicesTrendChart'));


//     // Set initial options (empty)
//     appointmentChart.setOption({
//         title: { text: 'Appointments by Status' },
//         tooltip: {},
//         xAxis: { type: 'category', data: [] },
//         yAxis: { type: 'value' },
//         series: [{ data: [], type: 'bar' }]
//     });

//     invoiceChart.setOption({
//         title: { text: 'Invoices (Paid vs Unpaid)' },
//         tooltip: { trigger: 'item' },
//         series: [{ type: 'pie', data: [] }]
//     });

//     // Initial fetch
//     fetchDashboardData();

//     // Poll every 5 seconds
//     setInterval(fetchDashboardData, 5000);
// });

// // ✅ Fetch and update dashboard data
// function fetchDashboardData() {
//     fetch('/api/dashboard-data')
//         .then(res => res.json())
//         .then(data => {
//             // Update cards
//             document.getElementById('totalPatients').textContent = data.total_patients;
//             document.getElementById('totalDoctors').textContent = data.total_doctors;
//             document.getElementById('availableDoctors').textContent = data.available_doctors;
//             document.getElementById('totalAppointments').textContent = data.total_appointments;
//             document.getElementById('totalInvoices').textContent = data.total_invoices;
//             document.getElementById('totalStaff').textContent = data.total_staff;
//             document.getElementById('activeStaff').textContent = data.active_staff;

//             // Update appointment chart
//             const statusLabels = Object.keys(data.appointment_statuses);
//             const statusCounts = Object.values(data.appointment_statuses);

//             appointmentChart.setOption({
//                 xAxis: { data: statusLabels },
//                 series: [{ data: statusCounts }]
//             });

//             // Update invoice chart
//             invoiceChart.setOption({
//                 series: [{
//                     data: [
//                         { value: data.invoice_statuses.Paid, name: 'Paid' },
//                         { value: data.invoice_statuses.Unpaid, name: 'Unpaid' }
//                     ]
//                 }]
//             });
//         })
//         .catch(err => {
//             console.error('Failed to fetch dashboard data:', err);
//         });
// }

// //fake live data
// // Simulated Fake Data for Trend Charts
// const fakeDays = ['2025-06-18','2025-06-19','2025-06-20','2025-06-21','2025-06-22','2025-06-23','2025-06-24'];
// const appointmentsPerDay = [4, 9, 7, 3, 8, 9, 4];
// const invoicesPaidPerDay = [2, 3, 1, 2, 1, 2, 5];
// const invoicesUnpaidPerDay = [0, 1, 2, 0, 3, 0, 3];

// // Appointments Trend Line Chart
// appointmentsTrendChart.setOption({
//   title: { text: 'Appointments Trend (7 Days)' },
//   tooltip: { trigger: 'axis' },
//   xAxis: { type: 'category', data: fakeDays },
//   yAxis: { type: 'value' },
//   series: [{
//     name: 'Appointments',
//     type: 'line',
//     data: appointmentsPerDay,
//     smooth: true,
//     lineStyle: { color: '#3b82f6' },
//     itemStyle: { color: '#3b82f6' }
//   }]
// });

// // Invoices Trend Stacked Bar Chart
// invoicesTrendChart.setOption({
//   title: { text: 'Invoices Trend (Paid vs Unpaid)' },
//   tooltip: { trigger: 'axis' },
//   legend: { data: ['Paid', 'Unpaid'] },
//   xAxis: { type: 'category', data: fakeDays },
//   yAxis: { type: 'value' },
//   series: [
//     {
//       name: 'Paid',
//       type: 'bar',
//       stack: 'invoice',
//       data: invoicesPaidPerDay,
//       itemStyle: { color: '#10b981' }
//     },
//     {
//       name: 'Unpaid',
//       type: 'bar',
//       stack: 'invoice',
//       data: invoicesUnpaidPerDay,
//       itemStyle: { color: '#ef4444' }
//     }
//   ]
// });


// ✅ Toggle: use fake data for now
const useFakeData = true;

// ✅ Fake Dashboard Data
const fakeDashboardData = {
    total_patients: 42,
    total_doctors: 12,
    available_doctors: 8,
    total_appointments: 25,
    total_invoices: 17,
    total_staff: 10,
    active_staff: 6,
    appointment_statuses: {
        Scheduled: 12,
        Completed: 9,
        Cancelled: 4
    },
    invoice_statuses: {
        Paid: 11,
        Unpaid: 6
    },
    trend_days: ['2025-06-18','2025-06-19','2025-06-20','2025-06-21','2025-06-22','2025-06-23','2025-06-24'],
    appointments_per_day: [4, 9, 7, 3, 8, 9, 4],
    invoices_paid: [2, 3, 1, 2, 1, 2, 5],
    invoices_unpaid: [0, 1, 2, 0, 3, 0, 3]
};

// ✅ Declare charts globally
let appointmentChart, invoiceChart, appointmentsTrendChart, invoicesTrendChart;

// ✅ DOM Ready
document.addEventListener("DOMContentLoaded", function () {
    // Form reset
    document.addEventListener('submit', function (e) {
        const form = e.target;
        setTimeout(() => form.reset(), 100);
    });

    // Confirm delete
    document.querySelectorAll('a[href*="delete"]').forEach(link => {
        link.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // ECharts setup
    appointmentChart = echarts.init(document.getElementById('appointmentsChart'));
    invoiceChart = echarts.init(document.getElementById('invoicesChart'));
    appointmentsTrendChart = echarts.init(document.getElementById('appointmentsTrendChart'));
    invoicesTrendChart = echarts.init(document.getElementById('invoicesTrendChart'));

    // Initial placeholder options
    appointmentChart.setOption({
        title: { text: 'Appointments by Status' },
        tooltip: {},
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: [{ data: [], type: 'bar' }]
    });

    invoiceChart.setOption({
        title: { text: 'Invoices (Paid vs Unpaid)' },
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', data: [] }]
    });

    // Initial load
    fetchDashboardData();

    // Update every 7 seconds
    setInterval(() => {
        if (useFakeData) simulateFakeData();
        fetchDashboardData();
    }, 7000);
});

// ✅ Render to dashboard
function renderDashboard(data) {
    // Scorecards
    document.getElementById('totalPatients').textContent = data.total_patients;
    document.getElementById('totalDoctors').textContent = data.total_doctors;
    document.getElementById('availableDoctors').textContent = data.available_doctors;
    document.getElementById('totalAppointments').textContent = data.total_appointments;
    document.getElementById('totalInvoices').textContent = data.total_invoices;
    document.getElementById('totalStaff').textContent = data.total_staff;
    document.getElementById('activeStaff').textContent = data.active_staff;

    // Appointment Chart
    appointmentChart.setOption({
        xAxis: { data: Object.keys(data.appointment_statuses) },
        series: [{ data: Object.values(data.appointment_statuses) }]
    });

    // Invoice Pie Chart
    invoiceChart.setOption({
        series: [{
            data: [
                { value: data.invoice_statuses.Paid, name: 'Paid' },
                { value: data.invoice_statuses.Unpaid, name: 'Unpaid' }
            ]
        }]
    });

    // Appointments Trend Chart
    appointmentsTrendChart.setOption({
        title: { text: 'Appointments Trend (7 Days)' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.trend_days },
        yAxis: { type: 'value' },
        series: [{
            name: 'Appointments',
            type: 'line',
            data: data.appointments_per_day,
            smooth: true,
            lineStyle: { color: '#3b82f6' },
            itemStyle: { color: '#3b82f6' }
        }]
    });

    // Invoices Trend Chart
    invoicesTrendChart.setOption({
        title: {
        text: 'Invoices Trend (Paid vs Unpaid)',
        left: 'center',
        top: 10
    },
        tooltip: { trigger: 'axis' },
        legend: {
        data: ['Paid', 'Unpaid'],
        top: 40,
        left: 'center'
    },
        xAxis: { type: 'category', data: data.trend_days },
        yAxis: { type: 'value' },
        series: [
            {
                name: 'Paid',
                type: 'bar',
                stack: 'invoice',
                data: data.invoices_paid,
                itemStyle: { color: '#10b981' }
            },
            {
                name: 'Unpaid',
                type: 'bar',
                stack: 'invoice',
                data: data.invoices_unpaid,
                itemStyle: { color: '#ef4444' }
            }
        ]
    });
}

// ✅ Switch between real and fake data
function fetchDashboardData() {
    if (useFakeData) {
        renderDashboard(fakeDashboardData); // Use fake data
    } else {
        // Real data fetch (currently disabled)
        /*
        fetch('/api/dashboard-data')
            .then(res => res.json())
            .then(data => renderDashboard(data))
            .catch(err => console.error('Failed to fetch dashboard data:', err));
        */
    }
}

// ✅ Simulate changing fake data
function simulateFakeData() {
    fakeDashboardData.total_patients += Math.floor(Math.random() * 2);
    fakeDashboardData.total_appointments += Math.floor(Math.random() * 3);
    fakeDashboardData.total_invoices += Math.floor(Math.random() * 2);
    fakeDashboardData.invoice_statuses.Paid += Math.floor(Math.random() * 2);
    fakeDashboardData.invoice_statuses.Unpaid += Math.floor(Math.random() * 1);
    fakeDashboardData.total_staff += Math.random() < 0.2 ? 1 : 0;
}




// edit doctor form
// Show and populate edit form for doctors
function editDoctor(doctor) {
    const form = document.getElementById('editForm');
    const container = document.getElementById('editFormContainer');
    container.style.display = 'block';

    form.action = `/doctors/edit/${doctor.id}`;
    document.getElementById('editId').value = doctor.id;
    document.getElementById('editName').value = doctor.name;
    document.getElementById('editSpecialty').value = doctor.specialty;
    document.getElementById('editContact').value = doctor.contact;
    document.getElementById('editAvailable').value = doctor.available ? "1" : "0";
}


// Show and populate patient edit form
function editPatient(patient) {
    const form = document.getElementById('editPatientForm');
    const container = document.getElementById('editPatientFormContainer');
    container.style.display = 'block';

    form.action = `/patients/edit/${patient.id}`;
    document.getElementById('editPatientId').value = patient.id;
    document.getElementById('editPatientName').value = patient.name;
    document.getElementById('editPatientAge').value = patient.age;
    document.getElementById('editPatientGender').value = patient.gender;
    document.getElementById('editPatientContact').value = patient.contact;
}

// Edit staff
function editStaff(member) {
    const container = document.getElementById('editStaffFormContainer');
    const form = document.getElementById('editStaffForm');

    container.style.display = 'block';
    form.action = `/staff/edit/${member.id}`;
    document.getElementById('editStaffId').value = member.id;
    document.getElementById('editStaffName').value = member.name;
    document.getElementById('editStaffRole').value = member.role;
    document.getElementById('editStaffContact').value = member.contact;
    document.getElementById('editStaffActive').checked = member.active;
}
