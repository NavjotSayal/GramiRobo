from flask import Flask, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)


# Root route to return your student number in JSON format
@app.route('/')
def home():
    return jsonify({"student_number": "200568700"})


# Webhook route that handles requests from Dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    # Step 1: Get the JSON data sent by Dialogflow
    req = request.get_json(silent=True, force=True)

    # Step 2: Extract the intent name and parameters from the request
    intent = req.get('queryResult').get('intent').get('displayName')
    parameters = req.get('queryResult').get('parameters')

    # Step 3: Set a default response if the intent is not recognized
    fulfillment_text = "I'm sorry, I couldn't find the price information."

    # Step 4: Check if the intent is "GetCryptoPrice" (the one we created in Dialogflow)
    if intent == 'GetCryptoPrice':
        crypto_name = parameters.get('crypto')  # Get the cryptocurrency name

        if crypto_name:
            # Step 5: Call CoinGecko API to get the price of the cryptocurrency
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_name}&vs_currencies=usd'
            response = requests.get(url)

            if response.status_code == 200:
                # Step 6: Parse the response from CoinGecko
                data = response.json()
                if crypto_name in data:
                    price = data[crypto_name]["usd"]
                    # Step 7: Respond with the cryptocurrency price
                    fulfillment_text = f"The current price of {crypto_name.capitalize()} is ${price} USD."
                else:
                    fulfillment_text = f"I couldn't find the price for {crypto_name}."
            else:
                fulfillment_text = "There was an error retrieving the cryptocurrency price. Please try again later."
        else:
            fulfillment_text = "Please specify a cryptocurrency, like Bitcoin or Ethereum."

    # Step 8: Return the response as JSON that Dialogflow can use
    return jsonify({"fulfillmentText": fulfillment_text})


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
