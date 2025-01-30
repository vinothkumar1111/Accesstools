let previousUnreadCount = 0;  
function loadNotifications() {
    const profileImgUrl = document.getElementById('profile-img-url').value; 
    
    fetch('/fetch-notifications/')
        .then(response => response.json())
        .then(data => {
            const notificationsList = document.getElementById('notifications-list');
            const taskCountSpan = document.getElementById('task-count');

            notificationsList.innerHTML = ''; 

            const currentUnreadCount = data.unread_count;
            taskCountSpan.textContent = currentUnreadCount > 0 ? currentUnreadCount : '';

            previousUnreadCount = currentUnreadCount;

            data.notifications.forEach(notification => {
                const notificationItem = `
                    <li class="notification-item" style="list-style: none; display: flex; align-items: center;">
                        <i class="ri-user-3-fill" style="font-size: 25px;"></i>  <!-- Add the icon here -->
                        <div class="notification-content" style="flex-grow: 1;">
                            <h4 style="margin: 0;">${notification.assigned_by}</h4> <!-- Username -->
                            <p style="margin: 0;">${notification.task_name}</p> <!-- Task name -->
                            <p style="margin: 0; font-size: 12px;" class="text-primary">${notification.created_at}</p>
                            <hr>
                        </div>
                    </li>
                `;
                notificationsList.innerHTML += notificationItem;
            });
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

function resetNotificationCount() {
    fetch('/mark-notifications-read/', {
        method: 'POST',  
        headers: {
            'X-CSRFToken': getCookie('csrftoken') 
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
           
            loadNotifications();  
        }
    })
    .catch(error => console.error('Error resetting notifications:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('task-icon').addEventListener('click', function(event) {
    event.preventDefault(); 
    resetNotificationCount();
});

setInterval(loadNotifications, 30000);

loadNotifications();
