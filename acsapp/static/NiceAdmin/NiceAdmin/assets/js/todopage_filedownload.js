function downloadCSV() {
    var table = document.getElementById("projectTable");
    if (!table) {
        alert("Table not found");
        return;
    }

    var rows = table.querySelectorAll("tr");

    if (rows.length === 0) {
        alert("No data available in the table");
        return;
    }

    var csvContent = "";

    rows.forEach(function(row, rowIndex) {
        var cols = row.querySelectorAll("td, th");
        var rowData = [];

        // Collect each cell's data, but skip the 'Action' column (last column)
        cols.forEach(function(cell, colIndex) {
            if (colIndex === cols.length - 1) {
                return; 
            }
            rowData.push(cell.innerText.trim());
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


function downloadPDF() {
    var table = document.getElementById("projectTable");
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
        if (colIndex !== headerRow.length - 1) { 
            headers.push(th.innerText.trim());
        }
    });

    table.querySelectorAll("tbody tr").forEach(function(row) {
        var rowData = [];
        row.querySelectorAll("td").forEach(function(cell, colIndex) {
            if (colIndex !== row.querySelectorAll("td").length - 1) {
                rowData.push(cell.innerText.trim());
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


