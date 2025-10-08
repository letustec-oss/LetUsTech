// Modal Functions
function showDownloadModal(programName, fileUrl) {
    document.getElementById('modalProgramName').textContent = programName;
    const downloadLink = document.getElementById('downloadLink');
    
    // If it's an external URL (starts with http), open in new tab
    if (fileUrl.startsWith('http://') || fileUrl.startsWith('https://')) {
        downloadLink.href = fileUrl;
        downloadLink.setAttribute('target', '_blank');
        downloadLink.removeAttribute('download');
    } else {
        // For local files
        downloadLink.href = fileUrl;
        downloadLink.setAttribute('download', '');
        downloadLink.removeAttribute('target');
    }
    
    document.getElementById('downloadModal').style.display = 'flex';
}

function showBankDetailsModal() {
    document.getElementById('bankDetailsModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Copy bank details to clipboard
function copyBankDetails() {
    const bankDetails = `Sort Code: 04-00-04\nAccount Number: 49376025`;
    
    navigator.clipboard.writeText(bankDetails).then(() => {
        alert('Bank details copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy. Please copy manually.');
    });
}

// Contact Form Submission
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const name = formData.get('name');
            const email = formData.get('email');
            const subject = formData.get('subject');
            const message = formData.get('message');
            
            // Create mailto link
            const mailtoLink = `mailto:letustec@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`)}`;
            
            window.location.href = mailtoLink;
            
            // Reset form
            contactForm.reset();
        });
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '#donate' && href !== '#contact' && href !== '#programs' && href !== '#about') {
            return;
        }
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});