

$(document).ready(function () {
    // Fetch existing orders on page load
    fetchOrders();

    // Handle form submission to add a new order
    $('#orderForm').submit(function (event) {
        event.preventDefault();

        // Get form data
        const orderData = {
            order_number: $('#order_number').val(),
            customer_name: $('#customer_name').val(),
            order_date: $('#order_date').val(),
            status: $('#status').val()
        };



        // Send POST request to add the order
        $.ajax({
            url: 'http://127.0.0.1:5001/orders',  // Add port 5001 here
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(orderData),
            success: function (response) {
                // Clear form fields
                $('#order_number').val('');
                $('#customer_name').val('');
                $('#order_date').val('');
                $('#status').val('');

                // Reload the order list
                fetchOrders();

                // Optionally, show a success message
                alert('Order added successfully');
            },
            error: function () {
                alert('Failed to add order');
            }
        });
    });


    // Function to fetch and display orders
    function fetchOrders() {
        $.ajax({
            url: 'http://127.0.0.1:5001/orders',  // Add port 5001 here
            type: 'GET',
            success: function (data) {
                // Clear the existing rows in the table
                $('#orderList').empty();

                // Append each order as a new row in the table
                data.forEach(order => {
                    const row = `<tr>
                                <td>${order.id}</td>
                                <td>${order.order_number}</td>
                                <td>${order.customer_name}</td>
                                <td>${order.order_date}</td>
                                <td>${order.status}</td>
                                <td>
                                    <button class="btn btn-warning btn-sm edit-btn" data-id="${order.id}">Edit</button>
                                    <button class="btn btn-danger btn-sm delete-btn" data-id="${order.id}">Delete</button>
                                </td>
                            </tr>`;
                    $('#orderList').append(row);
                });

                // Update the ECharts chart with live data
                updateChart(data);
            },
            error: function () {
                alert('Failed to load orders');
            }
        });
    }



    // Real-time search for orders

    $('#searchOrderInput').on('keyup', function () {
        const searchTerm = $(this).val().toLowerCase();

        $('#orderList tr').each(function () {
            const id = $(this).find('td:nth-child(1)').text().toLowerCase();
            const orderNumber = $(this).find('td:nth-child(2)').text().toLowerCase();
            const customerName = $(this).find('td:nth-child(3)').text().toLowerCase();
            const orderDate = $(this).find('td:nth-child(4)').text();

            const Status = $(this).find('td:nth-child(4)').text().toLowerCase();

            // Check if any field contains the search term
            if (id.includes(searchTerm) || orderNumber.includes(searchTerm) || customerName.includes(searchTerm) || orderDate.includes(searchTerm) || Status.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });



    // Update Order
    $(document).on('click', '.edit-btn', function () {
        const id = $(this).data('id');
        const orderNumber = prompt("Enter new Order Number:");
        const customerName = prompt("Enter new Customer Name:");
        const orderDate = prompt("Enter new Order Date (YYYY-MM-DD):");
        const status = prompt("Enter new Status:");

        const updatedOrder = {
            order_number: orderNumber,
            customer_name: customerName,
            order_date: orderDate,
            status: status
        };

        $.ajax({
            url: `http://127.0.0.1:5001/orders/${id}`,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(updatedOrder),
            success: function () {
                alert("Order updated successfully");
                fetchOrders();
            },
            error: function () {
                alert("Failed to update order");
            }
        });
    });

    // Delete Order
    $(document).on('click', '.delete-btn', function () {
        const id = $(this).data('id');
        if (confirm("Are you sure you want to delete this order?")) {
            $.ajax({
                url: `http://127.0.0.1:5001/orders/${id}`,
                type: 'DELETE',
                success: function () {
                    alert("Order deleted successfully");
                    fetchOrders();
                },
                error: function () {
                    alert("Failed to delete order");
                }
            });
        }
    });


    // Function to update the ECharts chart with live data
    function updateChart(data) {
        // Prepare the chart data
        const orderNumbers = data.map(order => order.order_number);
        const orderStatuses = data.map(order => order.status);
        const orderDates = data.map(order => new Date(order.order_date).toLocaleDateString());

        // Prepare the data for the chart (e.g., for a bar chart)
        const chartData = {
            xAxisData: orderNumbers,
            seriesData: orderStatuses.map(status => {
                // Assign a number based on status for visualization purposes (e.g., 1 for "Processed", 2 for "Pending", etc.)
                return status === 'Processed' ? 1 : status === 'Pending' ? 2 : 0;
            })
        };

        // Initialize the chart (make sure the element exists in the HTML)
        const chart = echarts.init(document.getElementById('performanceChart'));

        // Configure the chart
        const chartOptions = {
            title: {
                text: 'Order Status Overview',
            },
            tooltip: {
                trigger: 'item'
            },
            xAxis: {
                type: 'category',
                data: chartData.xAxisData
            },
            yAxis: {
                type: 'value',
                name: 'Status'
            },
            series: [{
                data: chartData.seriesData,
                type: 'bar',
            }]
        };

        // Set the chart options
        chart.setOption(chartOptions);
    }
});


fetchCredits();

$('#creditForm').submit(function (event) {
    event.preventDefault();

    const creditData = {
        customer_name: $('#customer_name').val(),
        credit_amount: parseFloat($('#credit_amount').val()),
        credit_status: $('#credit_status').val()
    };

    $.ajax({
        url: 'http://127.0.0.1:5002/credits',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(creditData),
        success: function () {
            fetchCredits();
            alert('Credit added successfully');
        }
    });
});

// Real-time search for credits
$('#searchCreditInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#creditList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text().toLowerCase();
        const customerName = $(this).find('td:nth-child(2)').text().toLowerCase();
        const creditStatus = $(this).find('td:nth-child(4)').text().toLowerCase();

        // Check if either field contains the search term
        if (id.includes(searchTerm) || customerName.includes(searchTerm) || creditStatus.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});


function fetchCredits() {
    $.ajax({
        url: 'http://127.0.0.1:5002/credits',
        type: 'GET',
        success: function (data) {
            $('#creditList').empty();
            data.forEach(credit => {
                const row = `
                        <tr>
                            <td>${credit.id}</td>
                            <td>${credit.customer_name}</td>
                            <td>${credit.credit_amount}</td>
                            <td>${credit.credit_status}</td>
                            <td>
                                <button onclick="deleteCredit(${credit.id})" class="btn btn-danger btn-sm">Delete</button>
                                <button onclick="updateCredit(${credit.id})" class="btn btn-warning btn-sm">Edit</button>
                            </td>
                        </tr>`;
                $('#creditList').append(row);
            });
        }
    });
}

window.deleteCredit = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5002/credits/${id}`,
        type: 'DELETE',
        success: function () {
            fetchCredits();
            alert('Credit deleted');
        }
    });
};

window.updateCredit = function (id) {
    const updatedData = {
        customer_name: prompt("Enter new customer name:"),
        credit_amount: parseFloat(prompt("Enter new credit amount:")),
        credit_status: prompt("Enter new credit status:")
    };

    $.ajax({
        url: `http://127.0.0.1:5002/credits/${id}`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(updatedData),
        success: function () {
            fetchCredits();
            alert('Credit updated');
        }
    });
};



fetchPayments();

$('#paymentForm').submit(function (event) {
    event.preventDefault();

    const paymentData = {
        customer_name: $('#customer_name').val(),
        amount: parseFloat($('#amount').val()),
        payment_date: $('#payment_date').val(),
        payment_status: $('#payment_status').val()
    };

    $.ajax({
        url: 'http://127.0.0.1:5003/payments',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(paymentData),
        success: function () {
            fetchPayments();
            alert('Payment added successfully');
        }
    });
});

// Real-time search for credits
$('#searchPaymentInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#paymentList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text().toLowerCase();
        const customerName = $(this).find('td:nth-child(2)').text().toLowerCase();
        const PaymentStatus = $(this).find('td:nth-child(5)').text().toLowerCase();

        // Check if either field contains the search term
        if (id.includes(searchTerm) || customerName.includes(searchTerm) || PaymentStatus.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});

function fetchPayments() {
    $.ajax({
        url: 'http://127.0.0.1:5003/payments',
        type: 'GET',
        success: function (data) {
            $('#paymentList').empty();
            data.forEach(payment => {
                const row = `
                        <tr>
                            <td>${payment.id}</td>
                            <td>${payment.customer_name}</td>
                            <td>${payment.amount}</td>
                            <td>${payment.payment_date}</td>
                            <td>${payment.payment_status}</td>
                            <td>
                                <button onclick="deletePayment(${payment.id})" class="btn btn-danger btn-sm">Delete</button>
                                <button onclick="updatePayment(${payment.id})" class="btn btn-warning btn-sm">Edit</button>
                            </td>
                        </tr>`;
                $('#paymentList').append(row);
            });
        }
    });
}

window.deletePayment = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5003/payments/${id}`,
        type: 'DELETE',
        success: function () {
            fetchPayments();
            alert('Payment deleted');
        }
    });
};

window.updatePayment = function (id) {
    const updatedData = {
        customer_name: prompt("Enter new customer name:"),
        amount: parseFloat(prompt("Enter new payment amount:")),
        payment_date: prompt("Enter new payment date:"),
        payment_status: prompt("Enter new payment status:")
    };

    $.ajax({
        url: `http://127.0.0.1:5003/payments/${id}`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(updatedData),
        success: function () {
            fetchPayments();
            alert('Payment updated');
        }
    });
};



fetchFulfillments();

// Handle form submission to add a new fulfillment
$('#fulfillmentForm').submit(function (event) {
    event.preventDefault();

    const fulfillmentData = {
        order_number: $('#order_number').val(),
        fulfillment_date: $('#fulfillment_date').val(),
        status: $('#status').val()
    };

    $.ajax({
        url: 'http://127.0.0.1:5004/fulfillment',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(fulfillmentData),
        success: function () {
            $('#order_number').val('');
            $('#fulfillment_date').val('');
            $('#status').val('');
            fetchFulfillments();
            alert('Fulfillment added successfully');
        },
        error: function () {
            alert('Failed to add fulfillment');
        }
    });
});

// Fetch fulfillments from the backend
function fetchFulfillments() {
    $.ajax({
        url: 'http://127.0.0.1:5004/fulfillment',
        type: 'GET',
        success: function (data) {
            $('#fulfillmentList').empty();
            data.forEach(fulfillment => {
                const row = `
                        <tr>
                            <td>${fulfillment.id}</td>
                            <td>${fulfillment.order_number}</td>
                            <td>${fulfillment.fulfillment_date}</td>
                            <td>${fulfillment.status}</td>
                            <td>
                                <button class="btn btn-warning btn-sm" onclick="updateFulfillment(${fulfillment.id})">Edit</button>
                                <button class="btn btn-danger btn-sm" onclick="deleteFulfillment(${fulfillment.id})">Delete</button>
                            </td>
                        </tr>`;
                $('#fulfillmentList').append(row);
            });
        },
        error: function () {
            alert('Failed to fetch fulfillments');
        }
    });
}

// Real-time search for orders

$('#searchFulfillmentInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#fulfillmentList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text();
        const orderNumber = $(this).find('td:nth-child(2)').text().toLowerCase();
        const orderDate = $(this).find('td:nth-child(3)').text();
        const Status = $(this).find('td:nth-child(4)').text().toLowerCase();

        // Check if any field contains the search term
        if (id.includes(searchTerm) || orderNumber.includes(searchTerm) || orderDate.includes(searchTerm) || Status.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});


// Function to delete a fulfillment
function deleteFulfillment(id) {
    $.ajax({
        url: `http://127.0.0.1:5004/fulfillment/${id}`,
        type: 'DELETE',
        success: function () {
            // Reload the fulfillment list
            fetchFulfillments();
            alert('Fulfillment deleted successfully');
        },
        error: function () {
            alert('Failed to delete fulfillment');
        }
    });
};

// Update fulfillment
window.updateFulfillment = function (id) {
    const order_number = prompt('Enter new Order Number:');
    const fulfillment_date = prompt('Enter new Fulfillment Date (YYYY-MM-DD):');
    const status = prompt('Enter new Status:');

    if (order_number && fulfillment_date && status) {
        $.ajax({
            url: `http://127.0.0.1:5004/fulfillment/${id}`,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ order_number, fulfillment_date, status }),
            success: function () {
                fetchFulfillments();
                alert('Fulfillment updated successfully');
            },
            error: function () {
                alert('Failed to update fulfillment');
            }
        });
    }
};


// invoice
// Fetch invoices on page load
fetchInvoices();

// Add new invoice on form submission
$('#invoiceForm').submit(function (event) {
    event.preventDefault();

    const invoiceData = {
        invoice_number: $('#invoice_number').val(),
        customer_name: $('#customer_name').val(),
        amount: parseFloat($('#amount').val()),
        status: $('#status').val(),
        issue_date: $('#issue_date').val()
    };

    $.ajax({
        url: 'http://127.0.0.1:5005/invoices',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(invoiceData),
        success: function () {
            $('#invoiceForm')[0].reset();
            fetchInvoices();
            alert('Invoice added successfully');
        },
        error: function () {
            alert('Failed to add invoice');
        }
    });
});

// Fetch and display invoices
function fetchInvoices() {
    $.ajax({
        url: 'http://127.0.0.1:5005/invoices',
        type: 'GET',
        success: function (data) {
            $('#invoiceList').empty();

            // Display the total number of invoices
            $('#invoiceCount').text(`Total Invoices Issued: ${data.length}`);

            data.forEach(invoice => {
                const row = `
                    <tr>
                        <td>${invoice.id}</td>
                        <td>${invoice.invoice_number}</td>
                        <td>${invoice.customer_name}</td>
                        <td>${invoice.amount}</td>
                        <td>${invoice.status}</td>
                        <td>${invoice.issue_date}</td>
                        <td>
                            <button onclick="deleteInvoice(${invoice.id})" class="btn btn-danger btn-sm">Delete</button>
                            <button onclick="updateInvoice(${invoice.id})" class="btn btn-warning btn-sm">Edit</button>
                        </td>
                    </tr>`;
                $('#invoiceList').append(row);
            });
        },
        error: function () {
            alert('Failed to load invoices');
        }
    });
}

// Real-time search for invoices
$('#searchInvoiceInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#invoiceList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text(); // Numeric, no .toLowerCase()
        const invoiceNumber = $(this).find('td:nth-child(2)').text().toLowerCase();
        const customerName = $(this).find('td:nth-child(3)').text().toLowerCase();
        const amount = $(this).find('td:nth-child(4)').text(); // Numeric, no .toLowerCase()
        const status = $(this).find('td:nth-child(5)').text().toLowerCase();
        const issueDate = $(this).find('td:nth-child(6)').text().toLowerCase();

        // Check if any field contains the search term
        if (
            id.includes(searchTerm) ||
            invoiceNumber.includes(searchTerm) ||
            customerName.includes(searchTerm) ||
            amount.includes(searchTerm) ||
            status.includes(searchTerm) ||
            issueDate.includes(searchTerm)
        ) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});

// Delete invoice
window.deleteInvoice = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5005/invoices/${id}`,
        type: 'DELETE',
        success: function () {
            fetchInvoices();
            alert('Invoice deleted successfully');
        },
        error: function () {
            alert('Failed to delete invoice');
        }
    });
};

// Update invoice
window.updateInvoice = function (id) {
    const invoice_number = prompt('Enter new Invoice Number:');
    const customer_name = prompt('Enter new Customer Name:');
    const amount = prompt('Enter new Amount:');
    const status = prompt('Enter new Status:');
    const issue_date = prompt('Enter new Issue Date (YYYY-MM-DD):');

    const updatedInvoice = {
        invoice_number,
        customer_name,
        amount: parseFloat(amount),
        status,
        issue_date
    };

    $.ajax({
        url: `http://127.0.0.1:5005/invoices/${id}`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(updatedInvoice),
        success: function () {
            fetchInvoices();
            alert('Invoice updated successfully');
        },
        error: function () {
            alert('Failed to update invoice');
        }
    });
};



// dispute



fetchDisputes();

// Handle form submission to add or update a dispute
$('#disputeForm').submit(function (event) {
    event.preventDefault();

    const disputeData = {
        dispute_number: $('#dispute_number').val(),
        order_number: $('#order_number').val(),
        description: $('#description').val(),
        resolution_status: $('#resolution_status').val()
    };

    const disputeId = $('#dispute_id').val();
    const url = disputeId ? `http://127.0.0.1:5006/disputes/${disputeId}` : 'http://127.0.0.1:5006/disputes';
    const method = disputeId ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        type: method,
        contentType: 'application/json',
        data: JSON.stringify(disputeData),
        success: function () {
            alert(disputeId ? 'Dispute updated successfully' : 'Dispute added successfully');
            $('#disputeForm')[0].reset();
            $('#dispute_id').val('');
            fetchDisputes();
        },
        error: function () {
            alert('Failed to add/update dispute');
        }
    });
});

function fetchDisputes() {
    $.ajax({
        url: 'http://127.0.0.1:5006/disputes',
        type: 'GET',
        success: function (data) {
            $('#disputeList').empty();
            data.forEach(dispute => {
                $('#disputeList').append(`
                        <tr>
                            <td>${dispute.id}</td>
                            <td>${dispute.dispute_number}</td>
                            <td>${dispute.order_number}</td>
                            <td>${dispute.description}</td>
                            <td>${dispute.resolution_status}</td>
                            <td>
                                <button class="btn btn-danger btn-sm" onclick="deleteDispute(${dispute.id})">Delete</button>
                                <button class="btn btn-warning btn-sm" onclick="editDispute(${dispute.id}, '${dispute.dispute_number}', '${dispute.order_number}', '${dispute.description}', '${dispute.resolution_status}')">Edit</button>
                            </td>
                        </tr>
                    `);
            });
        }
    });
}


// Real-time search for Dispute

$('#searchDisputetInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#disputeList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text();
        const disputeNumber = $(this).find('td:nth-child(2)').text().toLowerCase();
        const orderNumber = $(this).find('td:nth-child(3)').text().toLowerCase();
        const resolutionStatus = $(this).find('td:nth-child(5)').text().toLowerCase();


        // Check if any field contains the search term
        if (id.includes(searchTerm) || disputeNumber.includes(searchTerm) || orderNumber.includes(searchTerm) || resolutionStatus.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});


// Delete dispute
window.deleteDispute = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5006/disputes/${id}`,
        type: 'DELETE',
        success: function () {
            alert('Dispute deleted');
            fetchDisputes();
        }
    });
};

// Edit dispute - fill form with existing data
window.editDispute = function (id, dispute_number, order_number, description, resolution_status) {
    $('#dispute_id').val(id);
    $('#dispute_number').val(dispute_number);
    $('#order_number').val(order_number);
    $('#description').val(description);
    $('#resolution_status').val(resolution_status);
};


// reporting

fetchReports();

$('#reportForm').submit(function (event) {
    event.preventDefault();

    const reportData = {
        report_name: $('#report_name').val(),
        report_type: $('#report_type').val(),
        created_at: $('#created_at').val()
    };

    const reportId = $('#report_id').val();
    const url = reportId ? `http://127.0.0.1:5007/reports/${reportId}` : 'http://127.0.0.1:5007/reports';
    const method = reportId ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        type: method,
        contentType: 'application/json',
        data: JSON.stringify(reportData),
        success: function () {
            alert(reportId ? 'Report updated successfully' : 'Report added successfully');
            $('#reportForm')[0].reset();
            $('#report_id').val('');
            fetchReports();
        },
        error: function () {
            alert('Failed to add/update report');
        }
    });
});

function fetchReports() {
    $.ajax({
        url: 'http://127.0.0.1:5007/reports',
        type: 'GET',
        success: function (data) {
            $('#reportList').empty();
            data.forEach(report => {
                $('#reportList').append(`
                        <tr>
                            <td>${report.id}</td>
                            <td>${report.report_name}</td>
                            <td>${report.report_type}</td>
                            <td>${report.created_at}</td>
                            <td>
                                <button class="btn btn-danger btn-sm" onclick="deleteReport(${report.id})">Delete</button>
                                <button class="btn btn-warning btn-sm" onclick="editReport(${report.id}, '${report.report_name}', '${report.report_type}', '${report.created_at}')">Edit</button>
                            </td>
                        </tr>
                    `);
            });
        }
    });
}


// Real-time search for reports
$('#searchreportingInput').on('input', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#reportList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text().toLowerCase();
        const reportName = $(this).find('td:nth-child(2)').text().toLowerCase();
        const reportType = $(this).find('td:nth-child(3)').text().toLowerCase();
        const createdat = $(this).find('td:nth-child(4)').text().toLowerCase();


        // Check if any field contains the search term
        if (id.includes(searchTerm) || reportName.includes(searchTerm) || reportType.includes(searchTerm) || createdat.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});



window.deleteReport = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5007/reports/${id}`,
        type: 'DELETE',
        success: function () {
            alert('Report deleted');
            fetchReports();
        }
    });
};

window.editReport = function (id, report_name, report_type, created_at) {
    $('#report_id').val(id);
    $('#report_name').val(report_name);
    $('#report_type').val(report_type);
    $('#created_at').val(created_at);
};


// cash application

fetchCashApplications();

$('#cashApplicationForm').submit(function (event) {
    event.preventDefault();

    const applicationData = {
        payment_number: $('#payment_number').val(),
        customer_name: $('#customer_name').val(),
        amount: parseFloat($('#amount').val()),
        application_date: $('#application_date').val(),
        status: $('#status').val()
    };

    $.ajax({
        url: 'http://127.0.0.1:5008/cash_applications',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(applicationData),
        success: function () {
            alert('Cash application added successfully');
            fetchCashApplications();
        },
        error: function () {
            alert('Failed to add cash application');
        }
    });
});

function fetchCashApplications() {
    $.ajax({
        url: 'http://127.0.0.1:5008/cash_applications',
        type: 'GET',
        success: function (data) {
            $('#cashApplicationList').empty();
            data.forEach(app => {
                $('#cashApplicationList').append(`
                        <tr>
                            <td>${app.id}</td>
                            <td>${app.payment_number}</td>
                            <td>${app.customer_name}</td>
                            <td>${app.amount}</td>
                            <td>${app.application_date}</td>
                            <td>${app.status}</td>
                            <td>
                                <button class="btn btn-danger btn-sm" onclick="deleteCashApplication(${app.id})">Delete</button>
                                <button class="btn btn-warning btn-sm onclick="updateCashApplication(${app.id})">Edit</button>
                            </td>
                        </tr>
                    `);
            });
        }
    });
}

// search for Cash

$('#searchcashInput').on('keyup', function () {
    const searchTerm = $(this).val().toLowerCase();

    $('#cashApplicationList tr').each(function () {
        const id = $(this).find('td:nth-child(1)').text();
        const paymenteNumber = $(this).find('td:nth-child(2)').text().toLowerCase();
        const customerName = $(this).find('td:nth-child(3)').text().toLowerCase();
        const applicationrDate = $(this).find('td:nth-child(5)').text();
        const Status = $(this).find('td:nth-child(6)').text().toLowerCase();



        // Check if any field contains the search term
        if (id.includes(searchTerm) || paymenteNumber.includes(searchTerm) || customerName.includes(searchTerm) || applicationrDate.includes(searchTerm) || Status.includes(searchTerm)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});

window.deleteCashApplication = function (id) {
    $.ajax({
        url: `http://127.0.0.1:5008/cash_applications/${id}`,
        type: 'DELETE',
        success: function () {
            alert('Cash application deleted');
            fetchCashApplications();
        }
    });
};






// const microservices = [
//     { name: "Order Management", url: "http://127.0.0.1:5001/orders", chartId: "orderChart", chartType: "donut" },
//     { name: "Credit Management", url: "http://127.0.0.1:5002/credits", chartId: "creditChart", chartType: "bar" },
//     { name: "Payment Collection", url: "http://127.0.0.1:5003/payments", chartId: "paymentChart", chartType: "efficiency" },
//     { name: "Fulfillment", url: "http://127.0.0.1:5004/fulfillment", chartId: "fulfillmentChart", chartType: "efficiency" },
//     { name: "Invoicing", url: "http://127.0.0.1:5005/invoices", chartId: "invoiceChart", chartType: "donut" },
//     { name: "Dispute Resolution", url: "http://127.0.0.1:5006/disputes", chartId: "disputeChart", chartType: "donut" },
//     { name: "Reporting", url: "http://127.0.0.1:5007/reports", chartId: "reportingChart", chartType: "pie" },
//     { name: "Cash Application", url: "http://127.0.0.1:5008/cash_applications", chartId: "cashAppChart", chartType: "pie" },
// ];

// microservices.forEach(ms => {
//     fetchDataAndRenderChart(ms.url, ms.chartId, ms.chartType, ms.name);
// });

// function fetchDataAndRenderChart(url, chartId, chartType, name) {
//     $.ajax({
//         url: url,
//         type: 'GET',
//         success: function (data) {
//             // Update metric value in scorecards based on microservice name
//             switch (name) {
//                 case "Order Management":
//                     $('#orderMetric').text(data.length);
//                     // Count approved and pending
//                     const approvedCount = data.filter(d => d.status === "Approved").length;
//                     const pendingCount = data.filter(d => d.status === "Pending").length;
//                     const total = approvedCount + pendingCount;

//                     // Avoid division by zero
//                     const approvedPercentage = total === 0 ? 0 : Math.round((approvedCount / total) * 100);
//                     const pendingPercentage = total === 0 ? 0 : 100 - approvedPercentage;

//                     // Update the DOM
//                     $('#approvedPercentage').text(approvedPercentage + "%");
//                     $('#pendingPercentage').text(pendingPercentage + "%");
//                     break;
//                 case "Payment Collection":
//                     const completedPayments = data.filter(d => d.payment_status === "Completed").length;
//                     $('#paymentMetric').text(`${completedPayments} Completed`);
//                     break;
//                 case "Fulfillment":
//                     const deliveredOrders = data.filter(d => d.status === "Delivered").length;
//                     $('#fulfillmentMetric').text(`${deliveredOrders} Delivered`);
//                     break;
//                 case "Invoicing":
//                     $('#invoiceMetric').text(data.length);
//                     break;
//                 // You can add more cases here for other scorecards if needed
//             }

//             // Update invoice count if microservice is Invoicing (optional)
//             if (name === "Invoicing") {
//                 $('#invoiceCount').text(`Total Invoices Issued: ${data.length}`);
//             }

//             // Render chart
//             const chart = echarts.init(document.getElementById(chartId));
//             const chartOptions = generateChartOptions(data, chartType, chartId, name);
//             chart.setOption(chartOptions);
//         },
//         error: function () {
//             console.error('Failed to load data from', url);
//         }
//     });
// }

// // Your existing generateChartOptions function remains unchanged
// function generateChartOptions(data, chartType, chartId, name) {
//     const categories = data.map(item => item.credit_status || item.payment_status || item.resolution_status || item.status);

//     let approvedCount = 0, pendingCount = 0, deliveredCount = 0, completedCount = 0;
//     let efficiency = 0, efficiencyDelivered = 0, efficiencyCompleted = 0;

//     if (chartId === "paymentChart") {
//         completedCount = categories.filter(status => status === "Completed").length;
//         pendingCount = categories.filter(status => status === "Pending").length;
//         const totalCompleted = completedCount + pendingCount;
//         efficiencyCompleted = totalCompleted === 0 ? 0 : Math.round((completedCount / totalCompleted) * 100);
//     }
//     else if (chartId === "fulfillmentChart") {
//         deliveredCount = categories.filter(status => status === "Delivered").length;
//         pendingCount = categories.filter(status => status === "Pending").length;
//         const totalDelivered = deliveredCount + pendingCount;
//         efficiencyDelivered = totalDelivered === 0 ? 0 : Math.round((deliveredCount / totalDelivered) * 100);
//     }
//     else {
//         approvedCount = categories.filter(status => status === "Approved").length;
//         pendingCount = categories.filter(status => status === "Pending").length;
//         const total = approvedCount + pendingCount;
//         efficiency = total === 0 ? 0 : Math.round((approvedCount / total) * 100);
//     }

//     const values = chartId === "fulfillmentChart" ? [deliveredCount, pendingCount] :
//         chartId === "paymentChart" ? [completedCount, pendingCount] :
//             [approvedCount, pendingCount];

//     switch (chartType) {
//         case "bar":
//             return {
//                 tooltip: {},
//                 xAxis: {
//                     type: 'category',
//                     data: ['Approved', 'Pending'],
//                     axisTick: { alignWithLabel: true },
//                     axisLabel: { fontSize: 12, rotate: 30 }
//                 },
//                 yAxis: {
//                     type: 'value',
//                     axisLabel: { fontSize: 12 }
//                 },
//                 series: [{
//                     type: 'bar',
//                     data: values,
//                     itemStyle: {
//                         borderRadius: [5, 5, 0, 0],
//                         color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
//                             { offset: 0, color: '#3b8bba' },
//                             { offset: 1, color: '#61a0a8' }
//                         ])
//                     },
//                     label: {
//                         show: true,
//                         position: 'top',
//                         fontWeight: 'bold'
//                     }
//                 }]
//             };

//         case "line":
//             return {
//                 tooltip: {
//                     trigger: 'axis'
//                 },
//                 xAxis: {
//                     type: 'category',
//                     data: ['Approved', 'Pending']
//                 },
//                 yAxis: {
//                     type: 'value'
//                 },
//                 series: [{
//                     name: 'Credit Status',
//                     type: 'line',
//                     data: [approvedCount, pendingCount],
//                     label: {
//                         show: true,
//                         position: 'top'
//                     },
//                     lineStyle: {
//                         width: 2
//                     },
//                     itemStyle: {
//                         color: '#5470C6'
//                     }
//                 }]
//             };
//         case "pie":
//             return {
//                 tooltip: {
//                     trigger: 'item',
//                     formatter: '{a} <br/>{b} : {c} ({d}%)'
//                 },
//                 series: [{
//                     name: chartId === "fulfillmentChart" ? 'Delivery Status' : chartId === "paymentChart" ? 'Completed Status' : 'Approval Status',
//                     type: 'pie',
//                     radius: chartType === "donut" ? ['40%', '70%'] : '50%',
//                     center: ['50%', '60%'],
//                     data: chartId === "fulfillmentChart" ? [
//                         { value: deliveredCount, name: 'Delivered' },
//                         { value: pendingCount, name: 'Pending' }
//                     ] : chartId === "paymentChart" ? [
//                         { value: completedCount, name: 'Completed' },
//                         { value: pendingCount, name: 'Pending' }
//                     ] : [
//                         { value: approvedCount, name: 'Approved' },
//                         { value: pendingCount, name: 'Pending' }
//                     ],
//                     label: {
//                         fontSize: 12,
//                         color: '#333'
//                     },
//                     itemStyle: {
//                         borderRadius: 10,
//                         borderColor: '#fff',
//                         borderWidth: 2
//                     }
//                 }],
//                 color: ['#5470C6', '#91CC75', '#EE6666', '#FAC858'],
//                 legend: {
//                     orient: 'horizontal',
//                     bottom: 10,
//                     textStyle: {
//                         fontSize: 12
//                     }
//                 }
//             };
//         case "donut":
//             return {
//                 tooltip: {
//                     trigger: 'item',
//                     formatter: '{a} <br/>{b} : {c} ({d}%)'
//                 },
//                 series: [{
//                     name: chartId === "fulfillmentChart" ? 'Delivery Status' : chartId === "paymentChart" ? 'Completed Status' : 'Approval Status',
//                     type: 'pie',
//                     radius: ['40%', '70%'],
//                     center: ['50%', '60%'],
//                     data: chartId === "fulfillmentChart" ? [
//                         { value: deliveredCount, name: 'Delivered' },
//                         { value: pendingCount, name: 'Pending' }
//                     ] : chartId === "paymentChart" ? [
//                         { value: completedCount, name: 'Completed' },
//                         { value: pendingCount, name: 'Pending' }
//                     ] : [
//                         { value: approvedCount, name: 'Approved' },
//                         { value: pendingCount, name: 'Pending' }
//                     ],
//                     emphasis: {
//                         itemStyle: {
//                             shadowBlur: 10,
//                             shadowOffsetX: 0,
//                             shadowColor: 'rgba(0, 0, 0, 0.5)'
//                         }
//                     }
//                 }]
//             };
//         case "efficiency":
//             return {
//                 series: [{
//                     type: 'gauge',
//                     progress: {
//                         show: true,
//                         width: 18
//                     },
//                     axisLine: {
//                         lineStyle: {
//                             width: 18
//                         }
//                     },
//                     axisTick: { show: false },
//                     splitLine: { show: false },
//                     axisLabel: { show: false },
//                     pointer: { show: false },
//                     title: {
//                         show: true,
//                         offsetCenter: [0, '-30%'],
//                         fontSize: 14
//                     },
//                     detail: {
//                         valueAnimation: true,
//                         fontSize: 20,
//                         fontWeight: 'bold',
//                         formatter: '{value}%',
//                         offsetCenter: [0, '0%']
//                     },
//                     data: [{
//                         value: chartId === "fulfillmentChart" ? efficiencyDelivered :
//                             chartId === "paymentChart" ? efficiencyCompleted :
//                                 efficiency,
//                         name: name
//                     }]
//                 }]
//             };

//         case "halfDonut":
//             return {
//                 title: { text: 'Approval Status', left: 'center' },
//                 tooltip: { trigger: 'item', formatter: '{a} <br/>{b} : {c} ({d}%)' },
//                 series: [{
//                     name: 'Status',
//                     type: 'pie',
//                     radius: ['50%', '70%'],
//                     center: ['50%', '75%'],
//                     startAngle: 180,
//                     data: [
//                         { value: approvedCount, name: 'Approved' },
//                         { value: pendingCount, name: 'Pending' }
//                     ],
//                     label: { show: true, position: 'outside' },
//                     labelLine: { length: 30, length2: 50 },
//                     itemStyle: {
//                         borderRadius: 8,
//                         borderColor: '#fff',
//                         borderWidth: 2
//                     }
//                 }]
//             };
//         default:
//             return {};
//     }
// }




// function updateLiveData() {
//     document.getElementById('liveVisitors').innerText = Math.floor(Math.random() * 150 + 20);
//     document.getElementById('liveSales').innerText = Math.floor(Math.random() * 50 + 10);
//     document.getElementById('liveRevenue').innerText = '$' + (Math.random() * 5000).toFixed(2);
//     document.getElementById('livePayments').innerText = Math.floor(Math.random() * 40 + 5);

//     // Simulate live orders queue update
//     const liveOrderQueue = document.getElementById('liveOrderQueue');
//     liveOrderQueue.innerHTML = '';
//     for(let i=0; i<5; i++) {
//       const orderNum = 100000 + Math.floor(Math.random()*999);
//       const amount = (Math.random()*300).toFixed(2);
//       liveOrderQueue.innerHTML += `<div class="live-ticker-item">Order #${orderNum} - $${amount}</div>`;
//     }
//   }

//   // Update every 5 seconds
//   updateLiveData();
//   setInterval(updateLiveData, 5000)



// // fake live data for scorecards and charts
//   function updateLiveData() {
//     // Top scorecards
//     document.getElementById('orderMetric').innerText = Math.floor(Math.random() * 1000 + 200);
//     document.getElementById('paymentMetric').innerText = Math.floor(Math.random() * 500 + 100);
//     document.getElementById('fulfillmentMetric').innerText = Math.floor(Math.random() * 800 + 100);
//     document.getElementById('invoiceMetric').innerText = Math.floor(Math.random() * 400 + 50);

//     // Bottom small boxes
//     document.getElementById('liveVisitors').innerText = Math.floor(Math.random() * 150 + 20);
//     document.getElementById('liveSales').innerText = Math.floor(Math.random() * 50 + 10);
//     document.getElementById('liveRevenue').innerText = '$' + (Math.random() * 5000).toFixed(2);
//     document.getElementById('livePayments').innerText = Math.floor(Math.random() * 40 + 5);

//     // Order chart percentages
//     const approved = Math.floor(Math.random() * 60 + 30);
//     const pending = 100 - approved;
//     document.getElementById('approvedPercentage').innerText = approved + '%';
//     document.getElementById('pendingPercentage').innerText = pending + '%';

//     // Recent transactions
//     const recentTbody = document.getElementById('recentTransactions');
//     recentTbody.innerHTML = '';
//     for (let i = 0; i < 5; i++) {
//       const orderNum = 'ORD' + (100 + i + Math.floor(Math.random() * 100));
//       const date = new Date().toISOString().split('T')[0];
//       const status = ['Completed', 'Pending', 'Refunded'][Math.floor(Math.random() * 3)];
//       const badge = {
//         'Completed': 'bg-success',
//         'Pending': 'bg-warning text-dark',
//         'Refunded': 'bg-danger'
//       }[status];
//       const amount = (Math.random() * 300).toFixed(2);
//       recentTbody.innerHTML += `
//         <tr>
//           <td>${orderNum}</td>
//           <td>${date}</td>
//           <td><span class="badge ${badge}">${status}</span></td>
//           <td>$${amount}</td>
//         </tr>`;
//     }

//     // Live Order Queue
//     const liveOrderQueue = document.getElementById('liveOrderQueue');
//     liveOrderQueue.innerHTML = '';
//     for (let i = 0; i < 5; i++) {
//       const orderNum = 100000 + Math.floor(Math.random() * 999);
//       const amount = (Math.random() * 300).toFixed(2);
//       liveOrderQueue.innerHTML += `<div class="live-ticker-item">Order #${orderNum} - $${amount}</div>`;
//     }
//   }

//   updateLiveData();
//   setInterval(updateLiveData, 20000);




// function updateLiveData() {
//   // Top Scorecards
//   document.getElementById('orderMetric').innerText = Math.floor(Math.random() * 1000 + 200);
//   document.getElementById('paymentMetric').innerText = Math.floor(Math.random() * 500 + 100);
//   document.getElementById('fulfillmentMetric').innerText = Math.floor(Math.random() * 800 + 100);
//   document.getElementById('invoiceMetric').innerText = Math.floor(Math.random() * 400 + 50);

//   // Bottom Small Boxes
//   document.getElementById('liveVisitors').innerText = Math.floor(Math.random() * 150 + 20);
//   document.getElementById('liveSales').innerText = Math.floor(Math.random() * 50 + 10);
//   document.getElementById('liveRevenue').innerText = '$' + (Math.random() * 5000).toFixed(2);
//   document.getElementById('livePayments').innerText = Math.floor(Math.random() * 40 + 5);

//   // Order Chart Percentages
//   const approved = Math.floor(Math.random() * 60 + 30);
//   const pending = 100 - approved;
//   document.getElementById('approvedPercentage').innerText = approved + '%';
//   document.getElementById('pendingPercentage').innerText = pending + '%';

//   // Recent Transactions Table
//   const recentTbody = document.getElementById('recentTransactions');
//   if (recentTbody) {
//     recentTbody.innerHTML = '';
//     for (let i = 0; i < 5; i++) {
//       const orderNum = 'ORD' + (100 + i + Math.floor(Math.random() * 100));
//       const date = new Date().toISOString().split('T')[0];
//       const status = ['Completed', 'Pending', 'Refunded'][Math.floor(Math.random() * 3)];
//       const badge = {
//         'Completed': 'bg-success',
//         'Pending': 'bg-warning text-dark',
//         'Refunded': 'bg-danger'
//       }[status];
//       const amount = (Math.random() * 300).toFixed(2);
//       recentTbody.innerHTML += `
//         <tr>
//           <td>${orderNum}</td>
//           <td>${date}</td>
//           <td><span class="badge ${badge}">${status}</span></td>
//           <td>$${amount}</td>
//         </tr>`;
//     }
//   }

//   // Live Order Queue
//   const liveOrderQueue = document.getElementById('liveOrderQueue');
//   if (liveOrderQueue) {
//     liveOrderQueue.innerHTML = '';
//     for (let i = 0; i < 5; i++) {
//       const orderNum = 100000 + Math.floor(Math.random() * 999);
//       const amount = (Math.random() * 300).toFixed(2);
//       liveOrderQueue.innerHTML += `<div class="live-ticker-item">Order #${orderNum} - $${amount}</div>`;
//     }
//   }

//   // Product Performance Table
//   const productTable = document.getElementById('productPerformance');
//   if (productTable) {
//     productTable.innerHTML = '';
//     const products = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'];
//     products.forEach(product => {
//       const sales = Math.floor(Math.random() * 1000);
//       const stock = Math.floor(Math.random() * 100);
//       productTable.innerHTML += `
//         <tr>
//           <td>${product}</td>
//           <td>${sales}</td>
//           <td>${stock}</td>
//         </tr>`;
//     });
//   }
// }

// // Initial call + every 5 seconds
// updateLiveData();
// setInterval(updateLiveData, 5000);


// const inventoryChart = echarts.init(document.getElementById('inventoryChart'));
// inventoryChart.setOption({
//   title: { text: 'Inventory', left: 'center' },
//   tooltip: {},
//   series: [{
//     type: 'pie',
//     radius: '60%',
//     data: [
//       { value: 120, name: 'Electronics' },
//       { value: 80, name: 'Clothing' },
//       { value: 50, name: 'Home Goods' }
//     ]
//   }]
// });

// const trafficChart = echarts.init(document.getElementById('trafficChart'));
// trafficChart.setOption({
//   title: { text: 'Traffic Sources', left: 'center' },
//   tooltip: {},
//   xAxis: { type: 'category', data: ['Direct', 'Referral', 'Social', 'Search'] },
//   yAxis: { type: 'value' },
//   series: [{
//     data: [300, 200, 150, 400],
//     type: 'bar',
//     color: '#4facfe'
//   }]
// });

// const orderChart = echarts.init(document.getElementById('orderChart'));
// orderChart.setOption({
//   title: { text: 'Order Status' },
//   tooltip: {},
//   legend: { data: ['Orders'] },
//   xAxis: { data: ['Approved', 'Pending'] },
//   yAxis: {},
//   series: [{
//     name: 'Orders',
//     type: 'bar',
//     data: [
//       Math.floor(Math.random() * 100),
//       Math.floor(Math.random() * 50)
//     ]
//   }]
// });

// const paymentChart = echarts.init(document.getElementById('paymentChart'));
// paymentChart.setOption({
//   title: { text: 'Payment Status' },
//   tooltip: {},
//   series: [{
//     name: 'Payments',
//     type: 'pie',
//     radius: '50%',
//     data: [
//       { value: Math.floor(Math.random() * 100), name: 'Completed' },
//       { value: Math.floor(Math.random() * 30), name: 'Failed' },
//       { value: Math.floor(Math.random() * 20), name: 'Pending' }
//     ]
//   }]
// });

// Ensure jQuery is loaded
$(document).ready(function () {
    // Fake metric generators
    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1) + min);
    }

    function randomFloat(min, max, decimals = 2) {
        return (Math.random() * (max - min) + min).toFixed(decimals);
    }

    // Update scorecards and metrics
    function updateMetrics() {
        $("#orderMetric").text(randomInt(100, 500));
        $("#paymentMetric").text(randomInt(200, 700));
        $("#fulfillmentMetric").text(randomInt(150, 600));
        $("#invoiceMetric").text(randomInt(80, 400));
    }

    // Update live stats
    function updateLiveStats() {
        $("#liveVisitors").text(randomInt(10, 100));
        $("#liveSales").text(randomInt(5, 50));
        $("#liveRevenue").text("$" + randomFloat(1000, 10000));
    }

    // Update product performance table
    function updateProductPerformance() {
        const products = ["Widget A", "Widget B", "Gadget C", "Thing D"];
        const tbody = $("#productPerformance");
        tbody.empty();

        products.forEach(product => {
            const sales = randomInt(50, 500);
            const stock = randomInt(0, 100);
            const row = `
        <tr>
          <td>${product}</td>
          <td>${sales}</td>
          <td>${stock}</td>
        </tr>`;
            tbody.append(row);
        });
    }

    // Update recent transactions
    function updateTransactions() {
        const statuses = ["Completed", "Pending", "Failed"];
        const tbody = $("#recentTransactions");
        tbody.empty();

        for (let i = 0; i < 5; i++) {
            const orderId = "ORD" + randomInt(1000, 9999);
            const date = new Date().toLocaleDateString();
            const status = statuses[randomInt(0, 2)];
            const amount = "$" + randomFloat(50, 500);
            const row = `
        <tr>
          <td>${orderId}</td>
          <td>${date}</td>
          <td>${status}</td>
          <td>${amount}</td>
        </tr>`;
            tbody.append(row);
        }
    }

    // Update live order queue
  function updateLiveQueue() {
    const start = 1234;
    const end = 2244; // or 2234 for a larger set
    const statuses = ["Packing", "Shipping", "Delivered", "Received"];
    const orders = [];

    for (let i = start; i <= end; i++) {
        const status = statuses[Math.floor(Math.random() * statuses.length)];
        orders.push(`#${i} ${status}`);
    }

    const container = $("#liveOrderQueue");
    container.empty();

    orders.sort(() => 0.5 - Math.random()).slice(0, 10).forEach(order => {
        const div = `<div class="mb-1">${order}</div>`;
        container.append(div);
    });
}

    // Call update functions initially and at intervals
    function refreshAll() {
        updateMetrics();
        updateLiveStats();
        updateProductPerformance();
        updateTransactions();
        updateLiveQueue();
    }

    refreshAll(); // Initial
    setInterval(refreshAll, 5000); // Update every 5 seconds
});
document.addEventListener("DOMContentLoaded", function () {
    const orderChart = echarts.init(document.getElementById("orderChart"));

    const option = {
        title: {
            text: "Order Status",
            left: "center"
        },
        tooltip: {
            trigger: "item"
        },
        legend: {
            orient: "vertical",
            left: "left"
        },
        series: [
            {
                name: "Orders",
                type: "pie",
                radius: "60%",
                data: [
                    { value: 1048, name: "Pending" },
                    { value: 735, name: "Processing" },
                    { value: 580, name: "Shipped" },
                    { value: 484, name: "Delivered" }
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    };

    orderChart.setOption(option);

    // Optional: Auto update every few seconds with fake data
    setInterval(() => {
        option.series[0].data = [
            { value: Math.floor(Math.random() * 500), name: "Pending" },
            { value: Math.floor(Math.random() * 500), name: "Processing" },
            { value: Math.floor(Math.random() * 500), name: "Shipped" },
            { value: Math.floor(Math.random() * 500), name: "Delivered" }
        ];
        orderChart.setOption(option);
    }, 5000);
});
document.addEventListener("DOMContentLoaded", function () {
    const map = new jsVectorMap({
        selector: "#world-map",
        map: "world",
        zoomButtons: true,
        backgroundColor: "#0077f7",
        markers: [
            { name: "New York", coords: [40.7128, -74.0060] },
            { name: "London", coords: [51.5074, -0.1278] },
            { name: "Tokyo", coords: [35.6895, 139.6917] },
            { name: "Sydney", coords: [-33.8688, 151.2093] },
            { name: "Cairo", coords: [30.0444, 31.2357] },
            { name: "New Delhi", coords: [28.6139, 77.2090] }
        ],
        markerStyle: {
            initial: { fill: "#FF5722", stroke: "#fff", r: 6 }
        },
        regionStyle: {
            initial: { fill: "#e4e4e4" },
            hover: { fill: "#ccc" }
        }
    });
});


// Chatbot functionality

// document.addEventListener('DOMContentLoaded', function () {
//     const toggleButton = document.getElementById('chatbot-toggle');
//     const chatbotPopup = document.getElementById('chatbot-popup');
//     const closeBtn = document.getElementById('close-chatbot');

//     toggleButton.addEventListener('click', function (e) {
//         e.preventDefault();
//         chatbotPopup.style.display = 'block';
//     });

//     closeBtn.addEventListener('click', function () {
//         chatbotPopup.style.display = 'none';
//     });

//     const chatForm = document.getElementById('chat-form');
//     const chatInput = document.getElementById('chat-input');
//     const chatMessages = document.getElementById('chat-messages');

//     // Typewriter effect for bot messages
//     function typeWriter(element, text, speed = 40, callback) {
//         let i = 0;
//         element.textContent = ''; // Clear previous text
//         function typing() {
//             if (i < text.length) {
//                 element.textContent += text.charAt(i);
//                 i++;
//                 setTimeout(typing, speed);
//             } else if (callback) {
//                 callback();
//             }
//         }
//         typing();
//     }

//     function addMessage(sender, text) {
//         const messageDiv = document.createElement('div');
//         messageDiv.classList.add('message');

//         // Create sender name span
//         const senderSpan = document.createElement('span');
//         senderSpan.classList.add('sender-name');

//         if (sender === 'You') {
//             messageDiv.classList.add('user');
//             senderSpan.classList.add('user');      // Add user class here
//             senderSpan.textContent = 'You: ';
//             messageDiv.appendChild(senderSpan);
//             messageDiv.appendChild(document.createTextNode(text));
//         } else {
//             messageDiv.classList.add('bot');
//             senderSpan.classList.add('bot');       // Add bot class here
//             senderSpan.textContent = 'Bot: ';
//             messageDiv.appendChild(senderSpan);

//             // Typewriter effect on bot message text
//             const messageTextSpan = document.createElement('span');
//             messageDiv.appendChild(messageTextSpan);
//             typeWriter(messageTextSpan, text);
//         }

//         chatMessages.appendChild(messageDiv);
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//     }



//     chatForm.addEventListener('submit', function (e) {
//         e.preventDefault();
//         const message = chatInput.value.trim();
//         if (!message) return;

//         addMessage('You', message); // Show user message
//         chatInput.value = ''; // Clear input

//         // Show dummy response
//         fetch('/api/chatbot', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ message })
//         })
//             .then(response => response.json())
//             .then(data => {
//                 setTimeout(() => {
//                     addMessage('Bot', data.response);
//                 }, 1000); // Delay before bot reply
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//                 setTimeout(() => {
//                     addMessage('Bot', 'Sorry, something went wrong.');
//                 }, 1000);
//             });
//     });
// });


// function addMessage(sender, text) {
//     const msg = document.createElement('div');
//     msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
//     msg.classList.add('mb-2');
//     chatMessages.appendChild(msg);
//     chatMessages.scrollTop = chatMessages.scrollHeight;
// }



// 2
function typeWriter(element, text, speed = 40, callback) {
    let i = 0;
    element.textContent = '';
    function typing() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(typing, speed);
        } else if (callback) {
            callback();
        }
    }
    typing();
}

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message'); // ✔️ Common class

    if (sender === 'Bot') {
        messageDiv.classList.add('bot-message'); // ✔️ Bot class (left)
    } else {
        messageDiv.classList.add('user-message'); // ✔️ User class (right)
    }

    const bubble = document.createElement('div');
    bubble.classList.add('message-content'); // ✔️ For the bubble appearance

    if (sender === 'Bot') {
        typeWriter(bubble, text);
    } else {
        bubble.textContent = text;
    }

    messageDiv.appendChild(bubble);

    const chatBox = document.getElementById('chatMessages');
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage('You', message);
    input.value = '';

    fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
        .then(res => res.json())
        .then(data => {
            setTimeout(() => {
                addMessage('Bot', data.response);
            }, 600);
        })
        .catch(() => {
            addMessage('Bot', 'Sorry, something went wrong.');
        });

    return false;
}




// Stakeholder KPIs rendering function
function renderStakeholderKpis() {
    const kpis = [
        {
            stakeholder: "Sales",
            metrics: [
                { name: "Order-to-Cash Cycle", value: "45 days" },
                { name: "Sales Order Accuracy", value: "98%" },
                { name: "Customer Satisfaction", value: "90%" }
            ]
        },
        {
            stakeholder: "Finance",
            metrics: [
                { name: "DSO", value: "38 days" },
                { name: "Cash Flow Forecast Accuracy", value: "95%" },
                { name: "Bad Debt Ratio", value: "1.2%" }
            ]
        },
        {
            stakeholder: "Operations",
            metrics: [
                { name: "Fulfillment Rate", value: "96%" },
                { name: "Cycle Time", value: "5 days" },
                { name: "Inventory Accuracy", value: "99%" }
            ]
        }
    ];

    const container = document.getElementById("stakeholderKpiCards");
    if (!container) return;

    container.innerHTML = '';

    kpis.forEach(group => {
        const col = document.createElement("div");
        col.className = "col-md-4 mb-3";

        const card = document.createElement("div");
        card.className = "card h-100 border-primary";
        card.innerHTML = `
      <div class="card-header bg-primary text-white">${group.stakeholder}</div>
      <div class="card-body">
        ${group.metrics.map(m => `<p class="mb-2"><strong>${m.name}:</strong> ${m.value}</p>`).join('')}
      </div>
    `;
        col.appendChild(card);
        container.appendChild(col);
    });
}


// adminlte dashboard 
// Initialize OverlayScrollbars for the sidebar
document.addEventListener('DOMContentLoaded', function () {
    const SELECTOR_SIDEBAR_WRAPPER = '.sidebar-wrapper';
    const Default = {
        scrollbarTheme: 'os-theme-light',
        scrollbarAutoHide: 'leave',
        scrollbarClickScroll: true,
    };

    const sidebarWrapper = document.querySelector(SELECTOR_SIDEBAR_WRAPPER);
    if (sidebarWrapper && typeof OverlayScrollbarsGlobal?.OverlayScrollbars !== 'undefined') {
        OverlayScrollbarsGlobal.OverlayScrollbars(sidebarWrapper, {
            scrollbars: {
                theme: Default.scrollbarTheme,
                autoHide: Default.scrollbarAutoHide,
                clickScroll: Default.scrollbarClickScroll,
            },
        });
    }
});

// Initialize SortableJS for draggable cards
const connectedSortables = document.querySelectorAll('.connectedSortable');
connectedSortables.forEach((connectedSortable) => {
    new Sortable(connectedSortable, {
        group: 'shared',
        handle: '.card-header',
    });
});

// Set the cursor to "move" for draggable card headers
const cardHeaders = document.querySelectorAll('.connectedSortable .card-header');
cardHeaders.forEach((cardHeader) => {
    cardHeader.style.cursor = 'move';
});

// Toggle filter bar visibility
function toggleFilterBar() {
    const filterBar = document.getElementById('filterBar');
    filterBar.style.display = filterBar.style.display === 'none' ? 'block' : 'none';
}
function applyFilters() {
    const status = document.getElementById('statusFilter').value;
    const date = document.getElementById('dateRange').value;

    // Send filters to your backend API or filter on client
    fetch(`/api/filter-data?status=${status}&date=${date}`)
        .then(res => res.json())
        .then(data => {
            updateOrderChart(data.orders);
            updateTable(data.transactions);
            updateQueue(data.queue);
        })
        .catch(() => {
            alert('Failed to filter data');
        });
}


// Update the order chart with filtered data
// Initialize the chart
var chart = echarts.init(document.getElementById('profitLossChart'));

var dataCount = 30;
var data = [];
var base = +new Date();
var oneDay = 24 * 3600 * 1000;
var value = 0;

for (var i = 0; i < dataCount; i++) {
  var now = new Date(base += oneDay);
  value += (Math.random() * 20 - 10);
  data.push({
    name: now.toISOString().slice(0, 10),
    value: [
      now.toISOString().slice(0, 10),
      Math.round(value * 100) / 100
    ]
  });
}

var option = {
  title: {
    text: 'Profit/Loss Trend',
    left: 'center',
  },
  tooltip: {
    trigger: 'axis',
    formatter: function (params) {
      var date = params[0].name;
      var val = params[0].value[1];
      return `${date}<br/>Profit/Loss: ${val}k`;
    },
  },
  xAxis: {
    type: 'time',
    boundaryGap: false,
    axisLine: { lineStyle: { color: '#888' } },
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#888' } },
    splitLine: { show: false },
  },
  series: [{
    type: 'line',
    smooth: true,
    data: data.map(item => item.value),
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(0, 176, 155, 0.8)' },
        { offset: 1, color: 'rgba(0, 176, 155, 0.1)' }
      ])
    },
    lineStyle: {
      color: '#00b09b',
      width: 3
    },
    showSymbol: false,
  }]
};

chart.setOption(option);

// Optional: update data every 5 seconds with new random values
setInterval(() => {
  var lastDate = new Date(data[data.length - 1].value[0]);
  var newDate = new Date(lastDate.getTime() + oneDay);
  value += (Math.random() * 20 - 10);
  data.shift();
  data.push({
    name: newDate.toISOString().slice(0, 10),
    value: [newDate.toISOString().slice(0, 10), Math.round(value * 100) / 100]
  });
  chart.setOption({
    series: [{ data: data.map(item => item.value) }]
  });
}, 5000);



