import requests


# Define the URL and endpoint of your Flask API
url = 'http://localhost:5000/translate'
data = {
    'input_text': '동물'
}

# Send a POST request to the Flask API
response = requests.post(url, json=data)

# Parse the response
if response.status_code == 200:
    translated_text = response.json()['translation']
    print('Translated text:', translated_text)
else:
    print('Error:', response.text)