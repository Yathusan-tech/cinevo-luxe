const seats = document.querySelectorAll(".seat:not(.booked)");

const selectedSeatsInput = document.getElementById("selectedSeats");
const selectedList = document.getElementById("selectedList");
const seatCount = document.getElementById("seatCount");
const totalPrice = document.getElementById("totalPrice");
const continueButton = document.getElementById("continueButton");

const ticketPrice = Number(
    document.getElementById("ticketPriceData")?.dataset.price || 0
);

let selectedSeats = [];


/* =================================================
   SELECT / DESELECT SEAT
================================================== */

seats.forEach(function (seat) {

    seat.addEventListener("click", function () {

        const seatName = this.dataset.seat;

        if (selectedSeats.includes(seatName)) {

            selectedSeats = selectedSeats.filter(function (item) {
                return item !== seatName;
            });

            this.classList.remove("selected");

        } else {

            selectedSeats.push(seatName);

            this.classList.add("selected");
        }

        updateSummary();
    });
});


/* =================================================
   UPDATE SUMMARY
================================================== */

function updateSummary() {

    /* Sort seats naturally */

    selectedSeats.sort(function (a, b) {

        const rowA = a.charAt(0);
        const rowB = b.charAt(0);

        if (rowA !== rowB) {
            return rowA.localeCompare(rowB);
        }

        return (
            parseInt(a.substring(1))
            -
            parseInt(b.substring(1))
        );
    });


    const count = selectedSeats.length;

    const total = count * ticketPrice;


    /* Hidden input */

    selectedSeatsInput.value =
        selectedSeats.join(",");


    /* Count */

    seatCount.textContent =
        count
        +
        (
            count === 1
                ? " Seat Selected"
                : " Seats Selected"
        );


    /* Selected seats */

    if (count === 0) {

        selectedList.textContent =
            "No seats selected";

        selectedList.classList.remove(
            "has-seats"
        );

    } else {

        selectedList.textContent =
            "Selected seats: "
            +
            selectedSeats.join(", ");

        selectedList.classList.add(
            "has-seats"
        );
    }


    /* Price */

    totalPrice.textContent =
        "₹"
        +
        total.toLocaleString("en-IN");


    /* Continue button */

    if (count === 0) {

        continueButton.disabled = true;

        continueButton.textContent =
            "Select at least one seat";

    } else {

        continueButton.disabled = false;

        continueButton.textContent =
            "Continue to Customer Details →";
    }
}


/* =================================================
   PREVENT EMPTY FORM
================================================== */

document
    .getElementById("seatForm")
    .addEventListener(
        "submit",
        function (event) {

            if (selectedSeats.length === 0) {

                event.preventDefault();

                alert(
                    "Please select at least one seat."
                );
            }
        }
    );


/* =================================================
   INITIAL STATE
================================================== */

updateSummary();