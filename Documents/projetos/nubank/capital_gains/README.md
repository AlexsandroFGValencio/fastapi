# Capital Gain Calculator

This project calculates **capital gain taxes** on stock buy/sell operations following simplified tax rules.  
It assumes that taxes are only due when there is a **taxable profit exceeding $20,000.00** in a given month (basic simulation).

The main script receives a list of operations through **stdin** in JSON format and returns the corresponding taxes for each operation, also in JSON format.

---

## 📂 Project Structure

```
.
├── src/
│   └── main.py                 # Entry point script for tax calculation
├── tests/
│   └── test_capital_gain.py    # Automated unit tests
├── README.md
└── requirements.txt            # Optional project dependencies
```

---

## ⚡ How to Run

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/capital-gain.git
cd capital-gain

2.	Run the script with JSON input via stdin:

```python
python3 src/main.py <<EOF
[{"operation":"buy","unit-cost":5000.00,"quantity":10},
 {"operation":"sell","unit-cost":4000.00,"quantity":5},
 {"operation":"buy","unit-cost":15000.00,"quantity":5},
 {"operation":"buy","unit-cost":4000.00,"quantity":2},
 {"operation":"buy","unit-cost":23000.00,"quantity":2},
 {"operation":"sell","unit-cost":20000.00,"quantity":1},
 {"operation":"sell","unit-cost":12000.00,"quantity":10},
 {"operation":"sell","unit-cost":15000.00,"quantity":3}]
EOF
```

💡 Expected output

```
[{"tax": 0.0},
 {"tax": 0.0},
 {"tax": 0.0},
 {"tax": 0.0},
 {"tax": 0.0},
 {"tax": 0.0},
 {"tax": 1000.0},
 {"tax": 2400.0}]
```

✅ Testing

This project includes a comprehensive unit test suite using unittest that validates multiple buy/sell scenarios.

Run all tests with:

```
python3 -m unittest discover tests
```

Or run the test file directly:

```
python3 tests/test_capital_gain.py
```

If everything is correct, all test cases will pass ✅

📌 Notes
	•	This implementation provides a simplified tax simulation and can be adapted to real-world tax regulations.
	•	Input and output are strictly JSON-based.
	•	The script does not read or write files; it only uses stdin/stdout, which makes it easy to integrate with pipelines.