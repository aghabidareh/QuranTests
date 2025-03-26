from flask import Flask, request, jsonify
from creator import create_question

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'response': 'App is running!'})


@app.route('/generate_questions', methods=['GET'])
def generate_question():
    try:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
        count = int(request.args.get('count'))

    except:
        return jsonify({'error': 'Invalid Input parameters.'})

    question = create_question(start, end, count)

    return jsonify({'question': question})


if __name__ == '__main__':
    app.run(debug=True)
