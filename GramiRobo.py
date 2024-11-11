from flask import Flask, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)


# Root route to return your student number in JSON format
@app.route('/')
def home():
    return jsonify({"student_number": "200568700"})

@app.route('/webhook', methods=['POST'])
def webhook():
    # Step 1: Get the JSON data sent by Dialogflow
    req = request.get_json(silent=True, force=True)

    # Step 2: Check if the JSON body is missing or malformed
    if req is None:
        return jsonify({'response': 'Invalid JSON format or empty body'}), 400

    try:
        # Step 3: Extract the intent name and parameters from the request
        intent = req.get('queryResult', {}).get('intent', {}).get('displayName', 'Unknown')
        parameters = req.get('queryResult', {}).get('parameters', {})

        # Print to inspect the request data and check if the parameter exists
        print(f"Received request: {req}")
        print(f"Intent: {intent}")
        print(f"Parameters: {parameters}")

        # Step 4: Check if the parameter 'crypto' is present
        crypto_name = parameters.get('crypto', None)

        # Print the value of crypto_name
        print(f"Crypto Name: {crypto_name}")

        # Set a default response if the intent is not recognized
        fulfillment_text = "I'm sorry, I couldn't find the price information."

        # Step 5: Process the intent if crypto_name is found
        if intent == 'GetCryptoPrice' and crypto_name:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_name}&vs_currencies=usd'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if crypto_name in data:
                    price = data[crypto_name]["usd"]
                    fulfillment_text = f"The current price of {crypto_name.capitalize()} is ${price} USD."
                else:
                    fulfillment_text = f"I couldn't find the price for {crypto_name}."
            else:
                fulfillment_text = "There was an error retrieving the cryptocurrency price. Please try again later."
        else:
            fulfillment_text = "Please specify a cryptocurrency, like Bitcoin or Ethereum."

        return jsonify({"fulfillmentText": fulfillment_text})

    except Exception as e:
        return jsonify({'response': f'Error processing the request: {str(e)}'}), 400
