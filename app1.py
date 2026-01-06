from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)

x, y = sp.symbols('x y')

@app.route('/solve', methods=['POST'])
def solve_equation():
    data = request.json
    M_expr = data.get('M')
    N_expr = data.get('N')

    steps = []

    try:
        M = sp.sympify(M_expr)
        N = sp.sympify(N_expr)

        steps.append(f"M(x,y) = {M}")
        steps.append(f"N(x,y) = {N}")

        dM_dy = sp.diff(M, y)
        dN_dx = sp.diff(N, x)

        steps.append(f"∂M/∂y = {dM_dy}")
        steps.append(f"∂N/∂x = {dN_dx}")

        # ✅ EXACT CASE
        if sp.simplify(dM_dy - dN_dx) == 0:
            steps.append("Equation is EXACT.")

            phi = sp.integrate(M, x)
            g_y = sp.integrate(N - sp.diff(phi, y), y)
            solution = phi + g_y

            steps.append(f"General solution: {solution} = C")

            return jsonify({
                "steps": steps,
                "solution": f"{solution} = C"
            })

        # ❌ NON-EXACT CASE
        steps.append("Equation is NON-EXACT.")

        IF = None

        # Rule 1: IF as function of x only
        fx = sp.simplify((dM_dy - dN_dx) / N)
        if fx.has(x) and not fx.has(y):
            IF = sp.exp(sp.integrate(fx, x))
            steps.append("Using Rule 1: IF is function of x")
            steps.append(f"IF = {IF}")

        # Rule 2: IF as function of y only
        fy = sp.simplify((dN_dx - dM_dy) / M)
        if IF is None and fy.has(y) and not fy.has(x):
            IF = sp.exp(sp.integrate(fy, y))
            steps.append("Using Rule 2: IF is function of y")
            steps.append(f"IF = {IF}")

        # Rule 3: Homogeneous equation
        if IF is None:
            H = sp.simplify(x*M + y*N)
            if H != 0:
                IF = 1 / H
                steps.append("Using Rule 3: Homogeneous equation")
                steps.append("IF = 1 / (xM + yN)")

        # Rule 4: yf1 dx + xf2 dy
        if IF is None:
            H2 = sp.simplify(x*M - y*N)
            if H2 != 0:
                IF = 1 / H2
                steps.append("Using Rule 4: y f1 dx + x f2 dy")
                steps.append("IF = 1 / (xM - yN)")

        if IF is None:
            steps.append("Integrating factor not found.")
            return jsonify({"steps": steps, "solution": "Not solvable"})

        # Make exact
        M_new = sp.simplify(M * IF)
        N_new = sp.simplify(N * IF)

        steps.append(f"New M = {M_new}")
        steps.append(f"New N = {N_new}")
        steps.append("Equation is now EXACT.")

        phi = sp.integrate(M_new, x)
        g_y = sp.integrate(N_new - sp.diff(phi, y), y)
        solution = phi + g_y

        steps.append(f"General solution: {solution} = C")

        return jsonify({
            "steps": steps,
            "solution": f"{solution} = C"
        })

    except Exception as e:
        return jsonify({
            "steps": steps,
            "solution": str(e)
        })

if __name__ == "__main__":
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

