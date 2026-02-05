import base64
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import qutip as qt
from qutip import *

def calculate_health_score(final_rho):
    """
    Calculates a 0-100 score based on Purity and 'Ideal State' overlap.
    Assumes |00> (Both Happy) is the ideal target state.
    """
    # 1. Purity: How 'clear' is the relationship status? 
    # (High purity = You know where you stand. Low purity = Confusion/Entropy)
    purity = final_rho.purity()
    
    # 2. Fidelity: How close are we to the 'Ideal' state (|00>)?
    # We define ideal as tensor(basis(2,0), basis(2,0))
    ideal_state = tensor(basis(2,0), basis(2,0))
    fidelity_score = fidelity(final_rho, ideal_state)**2 # Probability of finding them in ideal state
    
    # Weighted Score: 70% based on being Happy (Fidelity), 30% on Clarity (Purity)
    health_score = (0.7 * fidelity_score + 0.3 * purity) * 100
    return health_score

def calculate_hybrid_score(times, data_A, data_B, final_rho):
    """
    Hybrid score that blends trajectory metrics with final-state purity/fidelity.
    """
    final_score = calculate_health_score(final_rho)

    avg_happiness = np.mean((data_A + data_B) / 2.0)  # [-1, 1]
    avg_happiness_score = (avg_happiness + 1.0) * 50.0  # [0, 100]

    correlation = np.corrcoef(data_A, data_B)[0, 1]  # [-1, 1]
    if np.isnan(correlation):
        correlation = 0.0
    correlation_score = (correlation + 1.0) * 50.0  # [0, 100]

    slope_A = np.polyfit(times, data_A, 1)[0]
    slope_B = np.polyfit(times, data_B, 1)[0]
    avg_slope = (slope_A + slope_B) / 2.0
    trend_score = (np.tanh(avg_slope * 6) + 1.0) * 50.0  # [0, 100]

    volatility = (np.std(data_A) + np.std(data_B)) / 2.0  # ~[0, 1]
    stability_score = np.exp(-1.6 * np.clip(volatility, 0.0, 1.5)) * 100.0

    trajectory_score = (
        0.45 * avg_happiness_score
        + 0.2 * correlation_score
        + 0.2 * stability_score
        + 0.15 * trend_score
    )

    hybrid = 0.7 * trajectory_score + 0.3 * final_score
    hybrid = 100.0 * np.power(np.clip(hybrid / 100.0, 0.0, 1.0), 0.85)
    return float(np.clip(hybrid, 0.0, 100.0))
def generate_horoscope(times, data_A, data_B, score):
    """
    Analyzes the trajectory to generate text advice.
    data_A/B are arrays of Happiness (-1 to 1).
    """
    narrative = []
    
    # --- ANALYSIS ---
    
    # 1. Sync Check (Correlation)
    # Are they moving together or opposite?
    correlation = np.corrcoef(data_A, data_B)[0,1]
    
    # 2. Trend Check (Slope)
    # Fit a simple line to seeing if happiness is going up or down
    slope_A = np.polyfit(times, data_A, 1)[0]
    slope_B = np.polyfit(times, data_B, 1)[0]
    avg_slope = (slope_A + slope_B) / 2
    
    # 3. Volatility (Standard Deviation)
    volatility = (np.std(data_A) + np.std(data_B)) / 2
    
    # --- WRITING THE HOROSCOPE ---
    
    # HEADLINE
    if score > 80:
        narrative.append("status: quantum entanglement")
    elif score > 50:
        narrative.append("status: it's complicated")
    else:
        narrative.append("status: decoherence detected")
        
    # SYNC ANALYSIS
    if correlation > 0.8:
        narrative.append("• your phases are so perfectly in sync that the relationship risks becoming an echo chamber. without friction or divergence, growth is stalled, and love trades depth for comfort.")
    elif correlation < 0:
        narrative.append("• your phases are anticorrelated, meaning there is a fundamental misalignment in your relationship. every attempt to resync costs more energy than it returns, causing you to drift further apart.")
    else:
        narrative.append("• there is noise/interference in your communication. external factors may consume your relationship and affect the quality of your interactions.")

    # TRAJECTORY ADVICE
    if avg_slope < -0.01:
        narrative.append("• your relationship is decaying and will keep slowly losing energy.")
        narrative.append("• advice: engage in more energetic conversation and spend more time with each other to counteract entropy.")
    elif volatility > 0.4:
        narrative.append("• your relationship is highly volatile like a rollercoaster.")
        narrative.append("• advice: your hamiltonian needs damping. introduce stabilizing routines, like daily check-ins, to reduce fluctuations.")
    else:
        narrative.append("• your relationship has reached a local minimum steady state.")
        if score < 60:
             narrative.append("• advice: your quantum state is stable but stagnant. introduce a perturbation to reignite the spark in your relationship.")

    return "\n".join(narrative)

def run_simulation(params=None, render_plot=True):
    params = params or {}

    # --- 1. Define The Operators ---
    I = qeye(2)

    # Acts on A, leaves B alone
    sx_A = tensor(sigmax(), I)  # Hot/Cold Partner, Bit flip A
    sz_A = tensor(sigmaz(), I)  # Cold shoulder partner, Dephase A
    sm_A = tensor(sigmam(), I)  # Burnt out partner, Decay A

    # Leaves A alone, acts on B
    sx_B = tensor(I, sigmax())
    sz_B = tensor(I, sigmaz())
    sm_B = tensor(I, sigmam())

    # Things that affect BOTH simultaneously
    sz_A_B = tensor(sigmaz(), sigmaz())  # Growing apart partners, Anti-correlated Dephase A/B
    sm_A_B = tensor(sigmam(), sigmam()) # Codepedent downward spiral partners, Collective Decay A/B

    # Creates the "Swap" interaction
    sy_A = tensor(sigmay(), I)
    sy_B = tensor(I, sigmay())

    # --- 2. Define Parameters ---
    omega_A = float(params.get("omega_A", 1.0))
    omega_B = float(params.get("omega_B", 1.4))
    J_empathy = float(params.get("J_empathy", 0.1))
    J_compatibility = float(
        params.get("J_compatibility", params.get("J_compatability", 0.05))
    )
    drive_amplitude = float(params.get("drive_amplitude", 1.5))
    drive_freq = float(params.get("drive_freq", 1.0))
    T = (2 * np.pi) / drive_freq

    args = {"w": drive_freq}

    # --- 3. Construct the Time-Dependent Hamiltonian ---
    H_static = (omega_A * sz_A) + (omega_B * sz_B) + \
               J_empathy * (sx_A * sx_B + sy_A * sy_B) + \
               J_compatibility * (sz_A * sz_B)

    H_driving_op = drive_amplitude * (sx_A + sx_B)
    H = [H_static, [H_driving_op, lambda t, args: np.sin(args["w"] * t)]]

    # --- 4. Define Noise Spectra ---
    def make_spectrum(rate):
        def spectrum(w):
            return rate / (2 * np.pi)
        return spectrum

    rate_bit_flip_A = float(params.get("rate_bit_flip_A", 0.05))
    rate_dephase_A = float(params.get("rate_dephase_A", 0.2))
    rate_decay_A = float(params.get("rate_decay_A", 0.01))

    rate_bit_flip_B = float(params.get("rate_bit_flip_B", 0.01))
    rate_dephase_B = float(params.get("rate_dephase_B", 0.05))
    rate_decay_B = float(params.get("rate_decay_B", 0.1))

    rate_anti_corr = float(params.get("rate_anti_corr", 0.9))
    rate_coll_decay = float(params.get("rate_coll_decay", 0.02))

    c_ops_list = []
    spectra_list = []

    c_ops_list.append(sx_A); spectra_list.append(make_spectrum(rate_bit_flip_A))
    c_ops_list.append(sz_A); spectra_list.append(make_spectrum(rate_dephase_A))
    c_ops_list.append(sm_A); spectra_list.append(make_spectrum(rate_decay_A))

    c_ops_list.append(sx_B); spectra_list.append(make_spectrum(rate_bit_flip_B))
    c_ops_list.append(sz_B); spectra_list.append(make_spectrum(rate_dephase_B))
    c_ops_list.append(sm_B); spectra_list.append(make_spectrum(rate_decay_B))

    c_ops_list.append(sz_A_B); spectra_list.append(make_spectrum(rate_anti_corr))
    c_ops_list.append(sm_A_B); spectra_list.append(make_spectrum(rate_coll_decay))

    # --- 5. Setup Simulation ---
    tlist = np.linspace(0.0, 10 * T, 200)
    psi0 = tensor(basis(2, 0), basis(2, 0))

    # --- 6. The Floquet-Markov Solver Flow ---
    f_modes_0, f_energies = floquet_modes(H, T, args)
    f_modes_table_t = floquet_modes_table(
        f_modes_0, f_energies, np.linspace(0, T, 500 + 1), H, T, args
    )

    output = fmmesolve(
        H, psi0, tlist,
        c_ops_list,
        [],
        spectra_list,
        T=T,
        args=args
    )

    # --- 7. Transform & Extract Data ---
    happiness_A = np.zeros(len(tlist))
    happiness_B = np.zeros(len(tlist))

    for idx, t in enumerate(tlist):
        f_modes_t = floquet_modes_t_lookup(f_modes_table_t, t, T)
        rho_lab = output.states[idx].transform(f_modes_t, True)
        happiness_A[idx] = expect(sz_A, rho_lab)
        happiness_B[idx] = expect(sz_B, rho_lab)

    # --- EXECUTE ANALYSIS ---
    final_rho_floquet = output.states[-1]
    final_modes = floquet_modes_t_lookup(f_modes_table_t, tlist[-1], T)
    final_rho_lab = final_rho_floquet.transform(final_modes, True)

    health_score = calculate_hybrid_score(tlist, happiness_A, happiness_B, final_rho_lab)
    horoscope_text = generate_horoscope(tlist, happiness_A, happiness_B, health_score)

    report_lines = [
        "\n" + "=" * 40,
        "  QUPID RELATIONSHIP REPORT",
        "=" * 40,
        f"HEALTH SCORE: {health_score:.1f}%",
        "-" * 40,
        horoscope_text,
        "=" * 40 + "\n",
    ]
    report_text = "\n".join(report_lines)

    plot_b64 = None
    if render_plot:
        matplotlib.use("Agg")
        fig = plt.figure(figsize=(10, 6))
        plt.style.use("dark_background")
        plt.plot(tlist, happiness_A, label="Person A", color="#00FFFF", linewidth=2)
        plt.plot(tlist, happiness_B, label="Person B", color="#FF00FF", linewidth=2, linestyle="--")
        plt.axhline(0, color="white", linestyle=":", alpha=0.5)
        plt.title("Relationship Dynamics with Periodic Effort (Floquet-Markov)")
        plt.legend(loc="upper right")
        plt.ylim(-1.1, 1.1)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=160, bbox_inches="tight")
        buffer.seek(0)
        plot_b64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)

    return {
        "health_score": float(health_score),
        "report_text": report_text,
        "plot_base64": plot_b64,
    }


if __name__ == "__main__":
    results = run_simulation()
    print(results["report_text"])
    if results["plot_base64"]:
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            img_data = base64.b64decode(results["plot_base64"])
            img_buf = io.BytesIO(img_data)
            img = plt.imread(img_buf, format="png")
            plt.figure(figsize=(10, 6))
            plt.imshow(img)
            plt.axis("off")
            plt.show()
        except Exception:
            pass
