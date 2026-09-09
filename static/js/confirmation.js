function copyBookingReference() {
    var refEl = document.getElementById('bookingRefCode');
    var btn = document.getElementById('copyRefBtn');
    var textEl = document.getElementById('copyText');
    var defaultIcon = document.getElementById('copyIconDefault');
    var checkIcon = document.getElementById('copyIconCheck');

    if (!refEl || !btn) return;

    var textToCopy = refEl.innerText.trim();

    function setCopiedState() {
        btn.classList.add('copied');

        if (textEl) textEl.textContent = 'Copied!';
        if (defaultIcon) defaultIcon.style.display = 'none';
        if (checkIcon) checkIcon.style.display = 'inline-block';

        btn.setAttribute('aria-label', 'Booking reference copied');

        setTimeout(function() {
            btn.classList.remove('copied');

            if (textEl) textEl.textContent = 'Copy';
            if (defaultIcon) defaultIcon.style.display = 'inline-block';
            if (checkIcon) checkIcon.style.display = 'none';

            btn.setAttribute(
                'aria-label',
                'Copy booking reference'
            );
        }, 2000);
    }

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy)
            .then(function() {
                setCopiedState();
            })
            .catch(function() {
                fallbackCopy(textToCopy);
            });
    } else {
        fallbackCopy(textToCopy);
    }

    function fallbackCopy(text) {
        try {
            var tempInput = document.createElement('textarea');

            tempInput.value = text;
            tempInput.setAttribute('readonly', '');

            tempInput.style.position = 'absolute';
            tempInput.style.left = '-9999px';

            document.body.appendChild(tempInput);
            tempInput.select();

            var success = document.execCommand('copy');

            document.body.removeChild(tempInput);

            if (success) {
                setCopiedState();
            }
        } catch (e) {
            // Graceful silent fallback
        }
    }
}