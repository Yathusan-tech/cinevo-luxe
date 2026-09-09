const searchInput = document.getElementById("bookingSearch");

const bookingCards = Array.from(
    document.querySelectorAll(".booking-card")
);

const noSearch = document.getElementById("noSearch");

const resultText = document.getElementById("resultText");


if (searchInput) {

    searchInput.addEventListener(
        "input",
        function () {

            const query = searchInput.value
                .trim()
                .toLowerCase();

            let visible = 0;


            bookingCards.forEach(function(card) {

                const text = card.dataset.search
                    .toLowerCase();

                if (
                    !query ||
                    text.includes(query)
                ) {

                    card.style.display = "";

                    visible++;

                } else {

                    card.style.display = "none";

                }

            });


            if (resultText) {

                resultText.innerHTML =
                    "Showing <strong>"
                    +
                    visible
                    +
                    "</strong> booking(s)";

            }


            if (noSearch) {

                if (
                    visible === 0 &&
                    query
                ) {

                    noSearch.style.display = "block";

                } else {

                    noSearch.style.display = "none";

                }

            }

        }
    );

}