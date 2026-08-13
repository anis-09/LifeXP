/**
 * static/js/notifications.js
 * Handles fetching, displaying, and dismissing notifications via API.
 */

document.addEventListener('DOMContentLoaded', () => {
  const bellContainer = document.getElementById('notification-bell-container');
  if (!bellContainer) return; // Not logged in or bell not in DOM

  const dropdown = document.getElementById('notification-dropdown');
  const badge = document.getElementById('notification-badge');
  const listContainer = document.getElementById('notification-list');
  const markAllBtn = document.getElementById('notification-mark-read-all');

  // Toggle Dropdown
  bellContainer.addEventListener('click', (e) => {
    // Prevent closing immediately when clicking the bell
    e.stopPropagation();
    dropdown.classList.toggle('active');
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && !bellContainer.contains(e.target)) {
      dropdown.classList.remove('active');
    }
  });

  // Prevent dropdown from closing when clicking inside it
  dropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });

  // Fetch Unread Notifications
  async function fetchNotifications() {
    try {
      const response = await fetch('/api/notifications');
      if (!response.ok) return;
      const data = await response.json();
      renderNotifications(data);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    }
  }

  // Render HTML for Notifications
  function renderNotifications(notifications) {
    if (notifications.length > 0) {
      badge.textContent = notifications.length;
      badge.classList.remove('hidden');
      
      listContainer.innerHTML = '';
      notifications.forEach(notif => {
        const li = document.createElement('li');
        li.className = 'notification-item';
        
        let icon = '🔔';
        if (notif.type === 'Success') icon = '✅';
        else if (notif.type === 'Warning') icon = '⚠️';
        else if (notif.type === 'Error') icon = '❌';

        li.innerHTML = `
          <div class="notification-item-icon">${icon}</div>
          <div class="notification-item-content">
            <h4 class="notification-item-title">${escapeHTML(notif.title)}</h4>
            <p class="notification-item-message">${escapeHTML(notif.message)}</p>
            <span class="notification-item-time">${formatDate(notif.created_at)}</span>
          </div>
          <button class="notification-item-dismiss" data-id="${notif.id}" aria-label="Mark as read">&times;</button>
        `;
        listContainer.appendChild(li);
      });

      // Bind dismiss buttons
      document.querySelectorAll('.notification-item-dismiss').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          markAsRead(e.currentTarget.getAttribute('data-id'));
        });
      });
    } else {
      badge.classList.add('hidden');
      listContainer.innerHTML = `
        <div class="notification-empty">
          <div class="notification-empty-icon">📭</div>
          <p>You're all caught up!</p>
        </div>
      `;
    }
  }

  // Mark single or all as read
  async function markAsRead(id = null) {
    try {
      const payload = id ? { notification_id: parseInt(id) } : {};
      const response = await fetch('/api/notifications/read', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        // Re-fetch to update UI
        fetchNotifications();
      }
    } catch (error) {
      console.error("Failed to mark notification(s) as read:", error);
    }
  }

  // Bind mark all read
  if (markAllBtn) {
    markAllBtn.addEventListener('click', () => {
      markAsRead(null);
    });
  }

  // Utility to escape HTML
  function escapeHTML(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
  }

  // Utility to format date
  function formatDate(dateStr) {
    const date = new Date(dateStr + 'Z'); // SQLite timestamps are typically UTC if inserted nicely, adjust if needed
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  // Initial fetch
  fetchNotifications();
});
