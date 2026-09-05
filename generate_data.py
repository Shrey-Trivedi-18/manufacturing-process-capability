"""Generate the synthetic manufacturing-quality study data.

The simulation keeps the process's true dimensions separate from the observed
measurements. That distinction is necessary for a meaningful Gage R&R study.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TARGET_DIAMETER = 20.00
LSL_DIAMETER = 19.70
USL_DIAMETER = 20.30
TARGET_LENGTH = 50.00
LSL_LENGTH = 49.50
USL_LENGTH = 50.50


def _measurement(true_value: np.ndarray, operators: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Apply operator bias and repeatability noise to a true dimension."""

    operator_bias = {"O1": -0.004, "O2": 0.006, "O3": 0.001}
    bias = np.array([operator_bias[operator] for operator in operators])
    repeatability_noise = rng.normal(0.0, 0.008, size=len(true_value))
    return true_value + bias + repeatability_noise


def _defect_type(
    diameter: np.ndarray,
    shift: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Assign one primary defect category to each inspected part."""

    defect = np.full(len(diameter), "None", dtype=object)
    oversize = diameter > USL_DIAMETER
    undersize = diameter < LSL_DIAMETER
    defect[oversize] = "Oversize"
    defect[undersize] = "Undersize"

    available = defect == "None"
    surface_probability = np.where(shift == "C", 0.040, 0.015)
    surface_finish = available & (rng.random(len(diameter)) < surface_probability)
    defect[surface_finish] = "Surface finish"

    available = defect == "None"
    burr = available & (rng.random(len(diameter)) < 0.012)
    defect[burr] = "Burr"

    available = defect == "None"
    taper = available & (rng.random(len(diameter)) < 0.009)
    defect[taper] = "Taper"

    available = defect == "None"
    tool_mark = available & (rng.random(len(diameter)) < 0.008)
    defect[tool_mark] = "Tool mark"
    return defect


def generate_production_data(
    n_parts: int = 20_000,
    seed: int = 42,
    process_centered: bool = False,
) -> pd.DataFrame:
    """Generate one row per manufactured and inspected part."""

    rng = np.random.default_rng(seed)
    machines = rng.choice(["M1", "M2", "M3", "M4"], size=n_parts)
    shifts = rng.choice(["A", "B", "C"], size=n_parts, p=[0.35, 0.35, 0.30])
    suppliers = rng.choice(["Supplier A", "Supplier B", "Supplier C"], size=n_parts)
    operators = rng.choice(["O1", "O2", "O3"], size=n_parts)

    dates = pd.date_range("2026-01-05", periods=60, freq="D")
    date_index = rng.integers(0, len(dates), size=n_parts)
    production_dates = dates[date_index]
    day_number = date_index.astype(float)
    temperature = (
        22.0
        + 1.8 * np.sin(2 * np.pi * day_number / 30)
        + rng.normal(0.0, 1.0, size=n_parts)
    )

    machine_offset = {"M1": -0.015, "M2": 0.000, "M3": 0.220, "M4": 0.010}
    if process_centered:
        machine_offset["M3"] = 0.000

    # M3 is intentionally more temperature-sensitive than the other machines.
    temperature_slope = {"M1": 0.0015, "M2": 0.0020, "M3": 0.0080, "M4": 0.0018}
    supplier_std = {"Supplier A": 0.012, "Supplier B": 0.025, "Supplier C": 0.015}
    shift_offset = {"A": 0.000, "B": 0.002, "C": 0.004}

    stock_variation = np.array([supplier_std[supplier] for supplier in suppliers])
    machine_effect = np.array([machine_offset[machine] for machine in machines])
    thermal_effect = np.array(
        [temperature_slope[machine] for machine in machines]
    ) * (temperature - 22.0)
    shift_effect = np.array([shift_offset[shift] for shift in shifts])

    true_diameter = (
        TARGET_DIAMETER
        + machine_effect
        + thermal_effect
        + shift_effect
        + rng.normal(0.0, 0.025, size=n_parts)
        + rng.normal(0.0, stock_variation)
    )
    true_length = TARGET_LENGTH + rng.normal(0.0, 0.12, size=n_parts)

    diameter = _measurement(true_diameter, operators, rng)
    length = _measurement(true_length, operators, rng)
    defect_type = _defect_type(diameter, shifts, rng)

    cycle_time = (
        42.0
        + np.select(
            [machines == "M1", machines == "M2", machines == "M3"],
            [0.0, 1.5, 3.0],
            default=2.0,
        )
        + 0.25 * (temperature - 22.0)
        + rng.normal(0.0, 1.2, size=n_parts)
    )

    return pd.DataFrame(
        {
            "Part_ID": [f"P{part_id:05d}" for part_id in range(1, n_parts + 1)],
            "Date": production_dates,
            "Shift": shifts,
            "Machine": machines,
            "Operator": operators,
            "Supplier": suppliers,
            "True_Diameter_mm": true_diameter,
            "Diameter_mm": diameter,
            "True_Length_mm": true_length,
            "Length_mm": length,
            "Temperature_C": temperature,
            "Cycle_Time_sec": cycle_time,
            "Defect_Type": defect_type,
            "Inspection_Result": np.where(defect_type == "None", "Pass", "Fail"),
        }
    )


def generate_gage_rr_data(
    production_data: pd.DataFrame,
    seed: int = 43,
) -> pd.DataFrame:
    """Create a crossed 10-part x 3-operator x 3-trial Gage R&R study."""

    rng = np.random.default_rng(seed)
    true_values = np.quantile(production_data["True_Diameter_mm"], np.linspace(0.05, 0.95, 10))

    rows: list[dict[str, object]] = []
    for part_number, true_value in enumerate(true_values, start=1):
        for operator in ["O1", "O2", "O3"]:
            for trial in range(1, 4):
                measured_value = _measurement(
                    np.array([true_value]), np.array([operator]), rng
                )[0]
                rows.append(
                    {
                        "Part_ID": f"GRR_P{part_number:02d}",
                        "Operator": operator,
                        "Trial": trial,
                        "True_Diameter_mm": true_value,
                        "Diameter_mm": measured_value,
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    production = generate_production_data()
    gage_rr = generate_gage_rr_data(production)

    production.to_csv(data_dir / "manufacturing.csv", index=False)
    gage_rr.to_csv(data_dir / "gage_rr.csv", index=False)

    print(f"Generated {len(production):,} production records")
    print(f"Generated {len(gage_rr):,} Gage R&R measurements")
    print("Overall inspection yield:", f"{(production['Inspection_Result'] == 'Pass').mean():.1%}")
    print("Diameter means by machine:")
    print(production.groupby("Machine")["Diameter_mm"].mean().round(4).to_string())


if __name__ == "__main__":
    main()
