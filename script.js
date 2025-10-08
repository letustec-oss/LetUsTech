// Modal Functions
function showDownloadModal(programName, fileName) {
    document.getElementById('modalProgramName').textContent = programName + ' - Download';
    
    // Set the download link
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = 'downloads/' + fileName; // Files should be in a 'downloads' folder
    downloadLink.download = fileName;
    
    document.getElementById('downloadModal').classList.add('active');
}

function showBankDetailsModal() {
    document.getElementById('bankDetailsModal').classList.add('active');
}

function showContactModal() {
    document.getElementById('contactModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Copy bank details to clipboard
function copyBankDetails() {
    const bankDetails = 'Sort Code: 04-00-04\nAccount Number: 49376025';
    
    // Try to copy to clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(bankDetails).then(function() {
            alert('✅ Bank details copied to clipboard!');
        }).catch(function() {
            alert('Bank Details:\nSort Code: 04-00-04\nAccount Number: 49376025');
        });
    } else {
        // Fallback for older browsers
        alert('Bank Details:\nSort Code: 04-00-04\nAccount Number: 49376025');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// Contact form submission
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const name = formData.get('name');
            const email = formData.get('email');
            const subject = formData.get('subject');
            const message = formData.get('message');
            
            // Create mailto link
            const mailtoLink = `mailto:letustec@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`)}`;
            
            // Open email client
            window.location.href = mailtoLink;
            
            // Show success message
            alert('Opening your email client... If it doesn\'t open automatically, please email us directly at letustec@gmail.com');
            
            // Reset form
            this.reset();
        });
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});