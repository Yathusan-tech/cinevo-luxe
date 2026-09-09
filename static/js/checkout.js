function validateCheckoutForm() {
    const nameInput = document.getElementById('customer_name');

    if (!nameInput || !nameInput.value.trim()) {
        alert('Please enter your full name.');

        if (nameInput) {
            nameInput.focus();
        }

        return false;
    }

    const emailInput = document.getElementById('email');
    const emailVal = emailInput ? emailInput.value.trim() : '';

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailVal || !emailRegex.test(emailVal) || emailVal.includes('..')) {
        alert('Please enter a valid email address.');

        if (emailInput) {
            emailInput.focus();
        }

        return false;
    }

    const phoneInput = document.getElementById('phone');

    let phoneVal = phoneInput
        ? phoneInput.value.trim().replace(/\D/g, '')
        : '';

    if (phoneVal.length === 11 && phoneVal.startsWith('0')) {
        phoneVal = phoneVal.substring(1);
    } else if (phoneVal.length === 12 && phoneVal.startsWith('91')) {
        phoneVal = phoneVal.substring(2);
    }

    if (
        phoneVal.length !== 10 ||
        !/^[6-9]\d{9}$/.test(phoneVal)
    ) {
        alert('Please enter a valid 10-digit mobile number.');

        if (phoneInput) {
            phoneInput.focus();
        }

        return false;
    }

    return true;
}