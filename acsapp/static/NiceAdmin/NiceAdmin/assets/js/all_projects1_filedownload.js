// csvDownload.js
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

    // Loop through each row and extract data
    rows.forEach(function(row, rowIndex) {
        var cols = row.querySelectorAll("td, th");
        var rowData = [];

        cols.forEach(function(cell, colIndex) {
            // Skip the last column (Action column) if present
            if (colIndex === cols.length - 1) {
                return;
            }

            // Handle the "Assigned To" column (index 5 in your case)
            if (colIndex === 5) {
                var userNames = [];

                // Collect visible user names from the icons (tooltip titles)
                var userIcons = cell.querySelectorAll('.user-icon');
                userIcons.forEach(function(icon) {
                    userNames.push(icon.getAttribute('title')); // Extract username from tooltip
                });

                // Collect user names from the "Show More" modal (if it exists)
                var modal = document.querySelector('#showMoreModal' + rowIndex);
                if (modal) {
                    modal.querySelectorAll('.list-group-item').forEach(function(item) {
                        userNames.push(item.innerText.trim());
                    });
                }

                // Add all collected usernames to the CSV row
                rowData.push(userNames.join(", "));
            } else {
                rowData.push(cell.innerText.trim()); // Collect other cell data as-is
            }
        });

        csvContent += rowData.join(",") + "\n"; // Join row data and add a newline
    });

    // Trigger download of the CSV file
    var downloadLink = document.createElement("a");
    var blob = new Blob([csvContent], { type: "text/csv" });
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "projects.csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink); // Clean up
}


// pdfDownload.js
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

    // Get table headers
    var headerRow = table.querySelectorAll("thead th");
    headerRow.forEach(function(th, colIndex) {
        if (colIndex !== headerRow.length - 1) { // Skip Action column
            headers.push(th.innerText.trim());
        }
    });

    // Get table rows
    table.querySelectorAll("tbody tr").forEach(function(row, rowIndex) {
        var rowData = [];
        row.querySelectorAll("td").forEach(function(cell, colIndex) {
            if (colIndex !== row.querySelectorAll("td").length - 1) { // Skip Action column
                if (colIndex === 5) { // "Assigned To" column (index 5)
                    var userNames = [];

                    // Collect visible user names from icons
                    var userIcons = cell.querySelectorAll('.user-icon');
                    userIcons.forEach(function(icon) {
                        userNames.push(icon.getAttribute('title')); // Extract from tooltips
                    });

                    // Collect users from the "Show More" modal
                    var modal = document.querySelector('#showMoreModal' + rowIndex);
                    if (modal) {
                        modal.querySelectorAll('.list-group-item').forEach(function(item) {
                            userNames.push(item.innerText.trim());
                        });
                    }

                    // Add all user names to the row data
                    rowData.push(userNames.join(", "));
                } else {
                    rowData.push(cell.innerText.trim());
                }
            }
        });
        rows.push(rowData);
    });

    // Add the table headers and rows to the PDF
    doc.autoTable({
        head: [headers],
        body: rows
    });

    // Download the PDF
    doc.save("projects.pdf");
}
