from flask import Flask, request, jsonify
app = Flask(__name__)

leads = []

@app.route('/leads', methods=['GET'])
def get_leads():
    return jsonify(leads)

@app.route('/leads', methods=['POST'])
def add_lead():
    data = request.get_json()
    leads.append(data)
    return jsonify({"message": "Lead added"}), 201

if __name__ == '__main__':
    app.run(port=5010, debug=True)
