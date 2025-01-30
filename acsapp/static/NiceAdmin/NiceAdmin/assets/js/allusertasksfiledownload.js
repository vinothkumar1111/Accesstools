// Fetch and display comments when modal is opened
document.getElementById('commentModal').addEventListener('show.bs.modal', function(event) {
    const button = event.relatedTarget;  // Button that triggered the modal
    const taskId = button.getAttribute('data-task-id');  // Extract the task ID from the data-task-id attribute

    // Store the taskId globally or in a hidden field inside the modal
    document.getElementById('commentModal').setAttribute('data-task-id', taskId);

    // Fetch comments for the selected task
    fetch(`/get-comments/${taskId}/`)
      .then(response => response.json())
      .then(data => {
        const commentsList = document.getElementById('commentsList');
        commentsList.innerHTML = '';  // Clear the list

        if (data.success && data.comments.length > 0) {
          data.comments.forEach(comment => {
            const commentElement = document.createElement('p');
            commentElement.innerHTML = `<strong>${comment.username}</strong>: ${comment.text} <small>(${comment.timestamp})</small>`;
            commentsList.appendChild(commentElement);
          });
        } else {
          commentsList.innerHTML = '<p>No comments yet.</p>';
        }
      })
      .catch(error => console.error('Error:', error));
});

// Submit a new comment via Ajax
function submitComment() {
    const taskId = document.getElementById('commentModal').getAttribute('data-task-id');  // Get the task ID from the modal
    const comment = document.getElementById('commentText').value;

    if (!comment) {
      alert("Comment cannot be empty.");
      return;
    }

    fetch(`/add-comment/${taskId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token }}',
      },
      body: JSON.stringify({ comment: comment })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Append the new comment to the previous comments section
        const commentSection = document.getElementById('commentsList');
        const newComment = document.createElement('p');
        newComment.innerHTML = `<strong>${data.username}</strong>: ${data.comment} <small>(${data.timestamp})</small>`;
        commentSection.appendChild(newComment);

        // Clear the comment input
        document.getElementById('commentText').value = '';
      } else {
        alert("Failed to add comment: " + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function downloadCSV() {
    var table = document.getElementById("userTable");
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
  var table = document.getElementById("userTable");
  if (!table) {
      alert("Table not found");
      return;
  }

  var { jsPDF } = window.jspdf;
  var doc = new jsPDF();

  var rows = [];
  var headers = [];

  // Capture the headers
  var headerRow = table.querySelectorAll("thead th");
  headerRow.forEach(function(th, colIndex) {
      if (colIndex !== 7) { // Exclude the Comment column
          headers.push(th.innerText.trim());
      }
  });

  // Get only the visible rows based on DataTable filtering
  var taskRows = table.querySelectorAll("tbody tr");
  taskRows.forEach(function(row) {
      // Check if the row is visible
      if (row.style.display !== "none") {
          var rowData = [];
          row.querySelectorAll("td").forEach(function(cell, colIndex) {
              if (colIndex !== 7) { // Exclude the Comment column
                  if (colIndex === 6) {
                      var statusSelect = cell.querySelector('select[name="status"]');
                      if (statusSelect) {
                          rowData.push(statusSelect.value.trim()); // Get the selected status value
                      } else {
                          rowData.push(cell.innerText.trim());
                      }
                  } else {
                      rowData.push(cell.innerText.trim());
                  }
              }
          });
          rows.push(rowData); // Add only visible rows
      }
  });

  // If there are no rows, alert the user
  if (rows.length === 0) {
      alert("No data available to download.");
      return;
  }

  // Export the PDF with the filtered data
  doc.autoTable({
      head: [headers],
      body: rows
  });

  doc.save("projects.pdf");
}
