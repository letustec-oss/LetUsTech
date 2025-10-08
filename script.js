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

// Contact form submission - NO EMAIL CLIENT
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
            
            // Show success message instead of opening email client
            const formContainer = this.parentElement;
            formContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                    <h3 style="color: white; margin-bottom: 1rem;">Thank You for Contacting LetUsTech!</h3>
                    <p style="color: rgba(255,255,255,0.9); margin-bottom: 1.5rem;">
                        We've received your message, ${name}! We'll get back to you at ${email} within 24 hours.
                    </p>
                    <button class="btn btn-secondary" onclick="location.reload()">Send Another Message</button>
                </div>
            `;
            
            // Log the form data (in production, you'd send this to a server)
            console.log('Form submission:', {
                name: name,
                email: email,
                subject: subject,
                message: message
            });
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