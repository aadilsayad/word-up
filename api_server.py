from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


model = AutoModelForSeq2SeqLM.from_pretrained('test_model')
tokenizer = AutoTokenizer.from_pretrained('test_tokenizer')
output_language = "en"
LANG_TOKEN_MAPPING = {
    'en': '<en>',
    'ko': '<ko>'
}


def encode_input_string(text, target_lang, tokenizer_used, seq_len, lang_token_map=None):
  if lang_token_map is None:
      lang_token_map = LANG_TOKEN_MAPPING
  target_lang_token = lang_token_map[target_lang]
  # Tokenize and add special tokens
  input_ids = tokenizer_used.encode(
      text=target_lang_token + text,
      return_tensors='pt',
      padding='max_length',
      truncation=True,
      max_length=seq_len
  )

  return input_ids[0]


app = Flask(__name__)
@app.route('/translate', methods=['POST'])
def translate():
    # Extract input data from the request
    input_word = request.json['input_text']

    input_ids = encode_input_string(
        text=input_word,
        target_lang=output_language,
        tokenizer_used=tokenizer,
        seq_len=model.config.max_length,
        lang_token_map=LANG_TOKEN_MAPPING
    )

    input_ids = input_ids.unsqueeze(0)

    output_tokens = model.generate(input_ids, num_beams=20, length_penalty=0.2)
    output_word = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    print(output_word)

    response = {
        'translation': output_word
    }

    # Return the JSON response
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)