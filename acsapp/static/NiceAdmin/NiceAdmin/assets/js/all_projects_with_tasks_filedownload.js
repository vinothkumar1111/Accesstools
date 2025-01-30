// Read More Modal functionality
document.addEventListener('DOMContentLoaded', function () {
    const readMoreLinks = document.querySelectorAll('.read-more');

    readMoreLinks.forEach(link => {
        link.addEventListener('click', function () {
            const description = this.getAttribute('data-description');  // Get the full description from data attribute
            const descriptionModal = document.getElementById('fullDescription');
            descriptionModal.textContent = description;  // Set the modal content
        });
    });
});

// CSV Download functionality
function downloadCSV() {
    var table = document.getElementById("userTable");
    if (!table) {
        alert("Table not found");
        return;
    }

    var rows = table.querySelectorAll("tbody tr");
    var headers = table.querySelectorAll("thead th");

    if (rows.length === 0) {
        alert("No data available in the table");
        return;
    }

    var csvContent = "";
    var headerData = [];
    headers.forEach(function(header, index) {
        if (index !== 5) {
            headerData.push(header.innerText.trim());
        }
    });
    csvContent += headerData.join(",") + "\n";

    rows.forEach(function(row) {
        var rowData = [];
        var cells = row.querySelectorAll("td");

        cells.forEach(function(cell, colIndex) {
            if (colIndex === 5) {
                return;
            }

            if (colIndex === 3 || colIndex === 4) {
                var dateText = cell.innerText.trim();
                rowData.push(dateText);
            } else if (colIndex === 6) {
                var statusSelect = cell.querySelector('select[name="status"]');
                if (statusSelect) {
                    rowData.push(statusSelect.value.trim());
                }
            } else {
                rowData.push(cell.innerText.trim());
            }
        });

        csvContent += rowData.join(",") + "\n";
    });

    var downloadLink = document.createElement("a");
    var blob = new Blob([csvContent], { type: "text/csv" });
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "projects.csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// PDF Download functionality
function downloadPDF() {
    var table = document.getElementById("userTable");
    if (!table) {
        alert("Table not found");
        return;
    }

    var { jsPDF } = window.jspdf;
    var doc = new jsPDF();

    var rows = [];
    var headers = [];

    var headerRow = table.querySelectorAll("thead th");
    headerRow.forEach(function(th, colIndex) {
        if (colIndex !== 5) {
            headers.push(th.innerText.trim());
        }
    });

    table.querySelectorAll("tbody tr").forEach(function(row) {
        var rowData = [];
        row.querySelectorAll("td").forEach(function(cell, colIndex) {
            if (colIndex !== 5) {
                if (colIndex === 6) {
                    var statusSelect = cell.querySelector('select[name="status"]');
                    if (statusSelect) {
                        rowData.push(statusSelect.value.trim());
                    } else {
                        rowData.push(cell.innerText.trim());
                    }
                } else {
                    rowData.push(cell.innerText.trim());
                }
            }
        });
        rows.push(rowData);
    });

    doc.autoTable({
        head: [headers],
        body: rows
    });

    doc.save("projects.pdf");
}
