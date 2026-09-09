// ============================================================
// CINEVO LUXE - SEAT SELECTION
// ============================================================


// ============================================================
// FOOD CART
// ============================================================

let myFoodCart = {};

function openFoodModal() {
    document.getElementById('foodModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeFoodModal() {
    document.getElementById('foodModal').style.display = 'none';
    document.body.style.overflow = '';
}

function addFoodItem(name, price) {

    if (myFoodCart[name]) {
        myFoodCart[name].quantity += 1;
    } else {
        myFoodCart[name] = {
            price: price,
            quantity: 1
        };
    }

    updateFoodUI();
}


function updateFoodUI() {

    const summary =
        document.getElementById('bookingFoodSummary');

    const items =
        document.getElementById('bookingFoodItems');

    const totalEl =
        document.getElementById('bookingFoodTotal');

    let total = 0;
    let html = '';

    for (let key in myFoodCart) {

        let itemTotal =
            myFoodCart[key].price *
            myFoodCart[key].quantity;

        total += itemTotal;

        html +=
            '<div style="display: flex; justify-content: space-between; margin-bottom: 6px;">' +
            '<span>' + key + ' × ' + myFoodCart[key].quantity + '</span>' +
            '<span>₹' + itemTotal + '</span>' +
            '</div>';
    }


    if (total > 0) {

        summary.style.display = 'block';

        items.innerHTML = html;

        totalEl.innerText = '₹' + total;

    } else {

        summary.style.display = 'none';

    }
}


function submitWithFood() {

    document.getElementById('input-food').value =
        JSON.stringify(myFoodCart);

    document.getElementById('checkoutForm').submit();
}


function skipFood() {

    document.getElementById('input-food').value =
        JSON.stringify({});

    document.getElementById('checkoutForm').submit();
}


// ============================================================
// SEAT SELECTION
// ============================================================

const TICKET_PRICE = Number(window.CINEVO_TICKET_PRICE || 0);

let selectedSeats = [];


const displaySeats =
    document.getElementById('display-seats');

const displayCount =
    document.getElementById('display-count');

const displayTotal =
    document.getElementById('display-total');

const inputSeats =
    document.getElementById('input-seats');

const proceedBtn =
    document.getElementById('proceed-btn');


// ============================================================
// SEAT ALERT
// ============================================================

let seatAlertTimeout = null;


function showSeatAlert(msg) {

    const alertBox =
        document.getElementById('seat-alert-msg');

    if (alertBox) {

        alertBox.textContent = msg;

        alertBox.style.display = 'block';

        clearTimeout(seatAlertTimeout);

        seatAlertTimeout = setTimeout(() => {

            alertBox.style.display = 'none';

        }, 4000);
    }
}


function hideSeatAlert() {

    const alertBox =
        document.getElementById('seat-alert-msg');

    if (alertBox) {

        alertBox.style.display = 'none';

    }
}


// ============================================================
// HANDLE SEAT CLICK
// ============================================================

function handleSeatClick(
    seatCode,
    elem,
    isOccupied
) {

    if (
        isOccupied ||
        elem.classList.contains('occupied')
    ) {

        showSeatAlert(
            'This seat is already booked. Please select another seat.'
        );

        return;
    }


    hideSeatAlert();

    toggleSeat(
        seatCode,
        elem
    );
}


// ============================================================
// TOGGLE SEAT
// ============================================================

function toggleSeat(
    seatCode,
    elem
) {

    if (
        elem.classList.contains('occupied')
    ) {
        return;
    }


    if (
        elem.classList.contains('selected')
    ) {

        elem.classList.remove('selected');

        selectedSeats =
            selectedSeats.filter(
                seat => seat !== seatCode
            );

    } else {

        elem.classList.add('selected');

        selectedSeats.push(seatCode);

    }


    updateSummary();
}


// ============================================================
// UPDATE BOOKING SUMMARY
// ============================================================

function updateSummary() {

    if (selectedSeats.length > 0) {

        displaySeats.textContent =
            selectedSeats.join(', ');

        displayCount.textContent =
            selectedSeats.length;

        displayTotal.textContent =
            '₹' +
            (
                selectedSeats.length *
                TICKET_PRICE
            ).toLocaleString('en-IN');

        inputSeats.value =
            selectedSeats.join(',');

        proceedBtn.disabled = false;

    } else {

        displaySeats.textContent =
            'None';

        displayCount.textContent =
            '0';

        displayTotal.textContent =
            '₹0';

        inputSeats.value =
            '';

        proceedBtn.disabled = true;
    }
}