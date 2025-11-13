// Blood Pressure Tracker JavaScript - Mobile Enhanced

let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();

// Mobile-specific variables
let touchStartX = 0;
let touchStartY = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();
    
    // Initialize calendar
    displayCalendar(currentMonth, currentYear);
    updateStats();
    
    // Initialize mobile features
    initializeMobileFeatures();
    
    // Handle URL parameters (for shortcuts)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'add') {
        // Scroll to input form or highlight it
        document.querySelector('.input-form').scrollIntoView({ behavior: 'smooth' });
    }
});

// Mobile-specific initialization
function initializeMobileFeatures() {
    // Add touch gestures for calendar navigation
    const calendarSection = document.querySelector('.calendar-section');
    
    calendarSection.addEventListener('touchstart', handleTouchStart, { passive: false });
    calendarSection.addEventListener('touchmove', handleTouchMove, { passive: false });
    calendarSection.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    // Prevent double-tap zoom
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Add haptic feedback support
    if ('vibrate' in navigator) {
        // Add subtle vibration on button clicks
        document.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', () => {
                navigator.vibrate(10); // 10ms vibration
            });
        });
    }
}

// Touch gesture handlers
function handleTouchStart(e) {
    const firstTouch = e.touches[0];
    touchStartX = firstTouch.clientX;
    touchStartY = firstTouch.clientY;
}

function handleTouchMove(e) {
    if (!touchStartX || !touchStartY) return;
    
    const xUp = e.touches[0].clientX;
    const yUp = e.touches[0].clientY;
    
    const xDiff = touchStartX - xUp;
    const yDiff = touchStartY - yUp;
    
    // Prevent default scrolling during swipe
    if (Math.abs(xDiff) > Math.abs(yDiff)) {
        e.preventDefault();
    }
}

function handleTouchEnd(e) {
    if (!touchStartX || !touchStartY) return;
    
    const xUp = e.changedTouches[0].clientX;
    const yUp = e.changedTouches[0].clientY;
    
    const xDiff = touchStartX - xUp;
    const yDiff = touchStartY - yUp;
    
    // Minimum swipe distance
    const minSwipeDistance = 50;
    
    if (Math.abs(xDiff) > Math.abs(yDiff) && Math.abs(xDiff) > minSwipeDistance) {
        if (xDiff > 0) {
            // Left swipe - next month
            changeMonth(1);
        } else {
            // Right swipe - previous month
            changeMonth(-1);
        }
    }
    
    // Reset values
    touchStartX = 0;
    touchStartY = 0;
}

// Storage functions
function saveReading(reading) {
    let readings = getReadings();
    const dateKey = reading.date;
    readings[dateKey] = reading;
    localStorage.setItem('bpReadings', JSON.stringify(readings));
}

function getReadings() {
    const stored = localStorage.getItem('bpReadings');
    return stored ? JSON.parse(stored) : {};
}

function getReadingByDate(date) {
    const readings = getReadings();
    return readings[date] || null;
}

// Add new reading
function addReading() {
    const date = document.getElementById('date').value;
    const systolic = parseInt(document.getElementById('systolic').value);
    const diastolic = parseInt(document.getElementById('diastolic').value);
    const time = document.getElementById('time').value;
    const notes = document.getElementById('notes').value;

    if (!date || !systolic || !diastolic) {
        alert('Please fill in the date and blood pressure values.');
        return;
    }

    if (systolic < 70 || systolic > 250 || diastolic < 40 || diastolic > 150) {
        alert('Please enter valid blood pressure values.');
        return;
    }

    const reading = {
        date: date,
        systolic: systolic,
        diastolic: diastolic,
        time: time,
        notes: notes,
        timestamp: new Date().toISOString()
    };

    saveReading(reading);
    
    // Clear form
    document.getElementById('systolic').value = '';
    document.getElementById('diastolic').value = '';
    document.getElementById('time').value = '';
    document.getElementById('notes').value = '';
    
    // Refresh calendar and stats
    displayCalendar(currentMonth, currentYear);
    updateStats();
    
    alert('Reading saved successfully!');
}

// Blood pressure classification
function classifyBP(systolic, diastolic) {
    if (systolic < 120 && diastolic < 80) {
        return { category: 'normal', class: 'bp-normal' };
    } else if ((systolic >= 120 && systolic < 130) && diastolic < 80) {
        return { category: 'elevated', class: 'bp-elevated' };
    } else if ((systolic >= 130 && systolic < 140) || (diastolic >= 80 && diastolic < 90)) {
        return { category: 'high-stage1', class: 'bp-high' };
    } else if (systolic >= 140 || diastolic >= 90) {
        return { category: 'high-stage2', class: 'bp-high' };
    } else {
        return { category: 'unknown', class: 'bp-normal' };
    }
}

// Calendar functions
function displayCalendar(month, year) {
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    
    document.getElementById('monthYear').textContent = `${monthNames[month]} ${year}`;
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    
    const calendarBody = document.getElementById('calendarBody');
    calendarBody.innerHTML = '';
    
    let date = 1;
    const readings = getReadings();
    
    // Create calendar rows
    for (let i = 0; i < 6; i++) {
        const row = document.createElement('tr');
        
        // Create calendar cells
        for (let j = 0; j < 7; j++) {
            const cell = document.createElement('td');
            
            if (i === 0 && j < firstDay) {
                // Previous month's dates
                const prevMonth = month === 0 ? 11 : month - 1;
                const prevYear = month === 0 ? year - 1 : year;
                const prevMonthDays = new Date(prevYear, prevMonth + 1, 0).getDate();
                const prevDate = prevMonthDays - firstDay + j + 1;
                
                cell.textContent = prevDate;
                cell.classList.add('other-month');
            } else if (date > daysInMonth) {
                // Next month's dates
                const nextDate = date - daysInMonth;
                cell.textContent = nextDate;
                cell.classList.add('other-month');
                date++;
            } else {
                // Current month's dates
                cell.textContent = date;
                
                // Check if it's today
                if (date === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                    cell.classList.add('today');
                }
                
                // Check for BP reading
                const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
                const reading = readings[dateString];
                
                if (reading) {
                    cell.classList.add('has-reading');
                    const classification = classifyBP(reading.systolic, reading.diastolic);
                    
                    // Add BP reading display
                    const bpDiv = document.createElement('div');
                    bpDiv.className = `bp-reading ${classification.class}`;
                    bpDiv.textContent = `${reading.systolic}/${reading.diastolic}`;
                    cell.appendChild(bpDiv);
                    
                    // Add indicator dot
                    const indicator = document.createElement('div');
                    indicator.className = `bp-indicator indicator-${classification.category.split('-')[0]}`;
                    cell.appendChild(indicator);
                    
                    // Add click event to show details
                    cell.addEventListener('click', () => showReadingDetails(reading));
                }
                
                date++;
            }
            
            row.appendChild(cell);
        }
        
        calendarBody.appendChild(row);
        
        // Stop creating rows if we've displayed all days
        if (date > daysInMonth) {
            break;
        }
    }
}

// Show reading details
function showReadingDetails(reading) {
    const classification = classifyBP(reading.systolic, reading.diastolic);
    let categoryText = '';
    
    switch(classification.category) {
        case 'normal':
            categoryText = 'Normal';
            break;
        case 'elevated':
            categoryText = 'Elevated';
            break;
        case 'high-stage1':
            categoryText = 'High Blood Pressure Stage 1';
            break;
        case 'high-stage2':
            categoryText = 'High Blood Pressure Stage 2';
            break;
        default:
            categoryText = 'Unknown';
    }
    
    let message = `Date: ${reading.date}\n`;
    message += `Blood Pressure: ${reading.systolic}/${reading.diastolic} mmHg\n`;
    message += `Category: ${categoryText}\n`;
    
    if (reading.time) {
        message += `Time: ${reading.time}\n`;
    }
    
    if (reading.notes) {
        message += `Notes: ${reading.notes}\n`;
    }
    
    alert(message);
}

// Navigate months
function changeMonth(direction) {
    currentMonth += direction;
    
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    } else if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    
    displayCalendar(currentMonth, currentYear);
    updateStats();
}

// Update statistics
function updateStats() {
    const readings = getReadings();
    const currentDate = new Date();
    const currentMonthReadings = [];
    
    // Filter readings for current month
    Object.values(readings).forEach(reading => {
        const readingDate = new Date(reading.date);
        if (readingDate.getMonth() === currentMonth && readingDate.getFullYear() === currentYear) {
            currentMonthReadings.push(reading);
        }
    });
    
    // Update reading count
    document.getElementById('readingCount').textContent = currentMonthReadings.length;
    
    // Calculate average BP
    if (currentMonthReadings.length > 0) {
        const avgSystolic = Math.round(
            currentMonthReadings.reduce((sum, reading) => sum + reading.systolic, 0) / currentMonthReadings.length
        );
        const avgDiastolic = Math.round(
            currentMonthReadings.reduce((sum, reading) => sum + reading.diastolic, 0) / currentMonthReadings.length
        );
        
        document.getElementById('avgBP').textContent = `${avgSystolic}/${avgDiastolic}`;
        
        // Find most recent reading
        const sortedReadings = currentMonthReadings.sort((a, b) => new Date(b.date) - new Date(a.date));
        const lastReading = sortedReadings[0];
        document.getElementById('lastReading').textContent = `${lastReading.systolic}/${lastReading.diastolic} (${lastReading.date})`;
    } else {
        document.getElementById('avgBP').textContent = '--/--';
        document.getElementById('lastReading').textContent = 'None';
    }
}

// Export data (bonus feature)
function exportData() {
    const readings = getReadings();
    const csvContent = "Date,Systolic,Diastolic,Time,Notes\n" + 
        Object.values(readings).map(reading => 
            `${reading.date},${reading.systolic},${reading.diastolic},${reading.time || ''},${reading.notes || ''}`
        ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'blood-pressure-data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Clear all data (bonus feature)
function clearAllData() {
    if (confirm('Are you sure you want to delete all blood pressure readings? This action cannot be undone.')) {
        localStorage.removeItem('bpReadings');
        displayCalendar(currentMonth, currentYear);
        updateStats();
        alert('All data has been cleared.');
    }
}

// Mobile-specific helper functions
function showMobileNotification(message, type = 'info') {
    // Create a mobile-friendly notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        font-size: 14px;
        max-width: 90%;
        text-align: center;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Enhanced mobile-friendly add reading function
const originalAddReading = addReading;
addReading = function() {
    const result = originalAddReading.call(this);
    
    // Replace alert with mobile-friendly notification
    if (result !== false) {
        showMobileNotification('Reading saved successfully!', 'success');
    }
    
    return result;
}

// Request notification permission (for reminders)
function requestNotificationPermission() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('Notification permission granted');
                // You can set up daily reminders here
            }
        });
    }
}

// Set daily reminder (optional feature)
function setDailyReminder(hour = 9, minute = 0) {
    if ('serviceWorker' in navigator && 'Notification' in window) {
        navigator.serviceWorker.ready.then(registration => {
            // Calculate time until next reminder
            const now = new Date();
            const scheduledTime = new Date();
            scheduledTime.setHours(hour, minute, 0, 0);
            
            if (scheduledTime < now) {
                scheduledTime.setDate(scheduledTime.getDate() + 1);
            }
            
            const timeUntilReminder = scheduledTime.getTime() - now.getTime();
            
            setTimeout(() => {
                registration.showNotification('BP Tracker Reminder', {
                    body: 'Time to record your blood pressure!',
                    icon: 'icon-192.png',
                    badge: 'icon-192.png',
                    tag: 'daily-reminder'
                });
            }, timeUntilReminder);
        });
    }
}
