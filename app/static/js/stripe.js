const stripe = Stripe('pk_test_51MF6ugGPXD0B68moBMToCE8ebWoeVAnKFBCzPRM8XiTPcM31AZzsRUdDFZ7eEk21odkeZWKX0dGV4J5Jp3itR63J006NQ7f8BI');
const elements = stripe.elements();

const style = {
    base: {
        fontSize: '16px',
        color: '#32325d',
    },
};

const card = elements.create('card', { style: style });
card.mount('#card-element');
card.addEventListener('change', function (event) {
    const displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});

const form = document.getElementById('payment-form');
form.addEventListener('submit', function (event) {
    event.preventDefault();

    stripe.createToken(card).then(function (result) {
        if (result.error) {
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
        } else {
            stripeTokenHandler(result.token);
        }
    });
});

function stripeTokenHandler(token) {
    const form = document.getElementById('payment-form');
    const hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);
    form.submit();
}