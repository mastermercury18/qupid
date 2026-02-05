import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from qupid_time_dependent_floquet import run_simulation
from backend.message_analyzer import parse_messages_from_upload, infer_parameters

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "qupid-app", "dist")
)
app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app)


def to_unit(value):
    try:
        return float(value) / 100.0
    except (TypeError, ValueError):
        return 0.0


def build_simulation_args(payload):
    omega_A = to_unit(payload.get("personATemperarment"))
    omega_B = to_unit(payload.get("personBTemperarment"))
    J_empathy = to_unit(payload.get("mutualEmpathy"))
    J_compatability = to_unit(payload.get("mutualCompatability"))
    drive_amplitude = to_unit(payload.get("mutualStrength"))
    drive_freq = to_unit(payload.get("mutualFrequency"))

    rate_bit_flip_A = to_unit(payload.get("personAHotCold"))
    rate_dephase_A = to_unit(payload.get("personADistant"))
    rate_decay_A = to_unit(payload.get("personABurnedOut"))

    rate_bit_flip_B = to_unit(payload.get("personBHotCold"))
    rate_dephase_B = to_unit(payload.get("personBDistant"))
    rate_decay_B = to_unit(payload.get("personBBurnedOut"))

    mutual_sync = payload.get("mutualSync", 0)
    rate_anti_corr = to_unit(100 - float(mutual_sync or 0))
    rate_coll_decay = to_unit(payload.get("mutualCodependence"))

    return {
        "omega_A": omega_A,
        "omega_B": omega_B,
        "J_empathy": J_empathy,
        "J_compatability": J_compatability,
        "drive_amplitude": drive_amplitude,
        "drive_freq": drive_freq,
        "rate_bit_flip_A": rate_bit_flip_A,
        "rate_dephase_A": rate_dephase_A,
        "rate_decay_A": rate_decay_A,
        "rate_bit_flip_B": rate_bit_flip_B,
        "rate_dephase_B": rate_dephase_B,
        "rate_decay_B": rate_decay_B,
        "rate_anti_corr": rate_anti_corr,
        "rate_coll_decay": rate_coll_decay,
    }


@app.route("/run", methods=["POST"])
def run_qupid():
    payload = request.get_json(force=True) or {}
    results = run_simulation(build_simulation_args(payload))

    print(results["report_text"])
    return jsonify(results)


@app.route("/analyze-run", methods=["POST"])
def analyze_and_run():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "missing file upload. send multipart/form-data with a 'file' field."}), 400

    try:
        messages = parse_messages_from_upload(uploaded_file)
        inferred_params, analyzer_debug = infer_parameters(messages)
        sim_results = run_simulation(build_simulation_args(inferred_params))
        sim_results["inferred_params"] = inferred_params
        sim_results["analyzer_debug"] = analyzer_debug
        sim_results["messages_analyzed"] = len(messages)
        print(sim_results["report_text"])
        return jsonify(sim_results)
    except Exception as exc:
        return jsonify({"error": f"analyzer failed: {exc}"}), 400


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    target = os.path.join(FRONTEND_DIST, path)
    if path and os.path.exists(target):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
