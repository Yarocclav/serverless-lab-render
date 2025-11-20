from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello, Serverless! 🚀"


@app.route('/echo', methods=['POST'])
def echo():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        return jsonify({
            "status": "received",
            "you_sent": data,
            "length": len(str(data))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)