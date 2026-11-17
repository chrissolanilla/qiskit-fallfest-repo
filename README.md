# IBM Qiskit Fallfest

This is a hackathon hosted at UCF sponsored by IBM for qiskit fallfest 2026.

The goal is to take 3 different QPUs and test out 3 different noise scenarios.

[Three processor models](assets/threeQPUs.png)

[Challenge Table](assets/table.png)

## How to run

### Clone the repo

```sh
git clone https://github.com/chrissolanilla/qiskit-fallfest-repo.git
cd qiskit-fallfest-repo
```

### Running the CLI

```sh
git clone https://github.com/chrissolanilla/qiskit-fallfest-repo.git
cd qiskit-fallfest-repo

python -m venv venv
source venv/bin/activate #source venv/bin/activate.fish if using fish

pip install -r requirements.txt
python src/main.py # use the cli or use the flags
```

### Running the notebook

```sh
#install the requirements if not already
python -m venv venv
source venv/bin/activate #source venv/bin/activate.fish if using fish
pip install -r requirements.txt

#start a jupyter lab server locally and open in your browser
jupyter lab
```
